#!/usr/bin/env python3
"""Contrôles d'intégrité du site ZamanIA.

Vérifie les invariants que le pipeline de publication automatique (Hermes)
doit respecter à chaque commit. Conçu pour tourner en CI (GitHub Actions)
comme en local, sans aucune dépendance hors bibliothèque standard.

Usage :
    python3 .automation/checks/check_site.py [--base /chemin/vers/le/site]

Code de sortie : 0 si tous les contrôles passent, 1 sinon.
"""

from __future__ import annotations

import argparse
import json
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit

DEFAULT_BASE = Path(__file__).resolve().parents[2]

SITE_DOMAIN = 'zamania.fr'
BLOG_DIRS = ['blog', 'en/blog', 'ar/blog']
HOME_PAGES = ['index.html', 'en/index.html', 'ar/index.html']
BLOG_INDEXES = ['blog/index.html', 'en/blog/index.html', 'ar/blog/index.html']
REQUIRED_FILES = [
    'index.html', '404.html', 'CNAME', 'robots.txt', 'sitemap.xml',
    'manifest.json', 'browserconfig.xml',
    'feed.xml', 'en/feed.xml', 'ar/feed.xml',
    'css/styles.css', 'css/dark-mode.css', 'css/rtl.css', 'css/blog.css',
    'css/fonts.css',
    'js/navigation.js', 'js/theme.js', 'js/home-articles.js',
    'js/share.js', 'js/reading-progress.js', 'js/contact-form.js', 'js/analytics.js',
    'contact.html', 'en/contact.html', 'ar/contact.html',
    'blog/index.html', 'blog/template.html', 'blog/index-template.html',
    'en/index.html', 'en/blog/index.html', 'en/blog/template.html',
    'en/blog/index-template.html',
    'ar/index.html', 'ar/blog/index.html', 'ar/blog/template.html',
    'ar/blog/index-template.html',
]
ARTICLES_START = '<!-- ARTICLES_LIST_START -->'
ARTICLES_END = '<!-- ARTICLES_LIST_END -->'
HOME_START = '<!-- HOME_ARTICLES_START -->'
HOME_END = '<!-- HOME_ARTICLES_END -->'

PLACEHOLDER_RE = re.compile(r'\{\{\s*[A-Z_]+\s*\}\}')
LINK_RE = re.compile(r'(?:href|src)\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
SRCSET_RE = re.compile(r'srcset\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
SOCIAL_IMG_RE = re.compile(
    r'<meta\s+(?:property|name)=["\'](?:og:image|twitter:image)["\']\s+content=["\']([^"\']+)["\']',
    re.IGNORECASE)
CSS_URL_RE = re.compile(r'url\(\s*["\']?([^"\')]+)["\']?\s*\)')
COMMENT_RE = re.compile(r'<!--.*?-->', re.DOTALL)
ID_RE = re.compile(r'\bid\s*=\s*["\']([^"\']+)["\']')
H1_RE = re.compile(r'<h1[\s>]')
LANG_RE = re.compile(r'<html\b[^>]*\blang\s*=\s*["\']([^"\']+)["\']')
DIR_RE = re.compile(r'<html\b[^>]*\bdir\s*=\s*["\']rtl["\']')
TITLE_RE = re.compile(r'<title>\s*([^<]+?)\s*</title>', re.DOTALL)
META_DESC_RE = re.compile(
    r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']', re.IGNORECASE)
NOINDEX_RE = re.compile(r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*noindex',
                        re.IGNORECASE)
EXTERNAL_PREFIXES = ('http://', 'https://', '//', 'mailto:', 'tel:', 'data:', 'javascript:')
# Les URL absolues du site lui-même sont vérifiées comme des fichiers locaux.
SITE_PREFIXES = tuple(f'{scheme}://{host}' for scheme in ('https', 'http')
                      for host in (SITE_DOMAIN, f'www.{SITE_DOMAIN}'))


def is_template(path: Path) -> bool:
    return path.name in ('template.html', 'index-template.html')


def site_url_to_local(base: Path, url: str) -> Path | None:
    """Convertit une URL absolue https://zamania.fr/... en chemin local."""
    for prefix in SITE_PREFIXES:
        if url == prefix or url.startswith(prefix + '/'):
            path = unquote(urlsplit(url).path).lstrip('/')
            resolved = (base / path) if path else base
            if resolved.is_dir():
                resolved = resolved / 'index.html'
            return resolved
    return None


def html_pages(base: Path) -> list[Path]:
    """Toutes les pages HTML publiées (templates exclus)."""
    return sorted(p for p in base.rglob('*.html')
                  if '.git' not in p.parts and not is_template(p))


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


# --------------------------------------------------------------------------
# Contrôles. Chaque fonction reçoit la racine du site et renvoie une liste
# de messages d'erreur (vide si tout va bien).
# --------------------------------------------------------------------------

def check_required_files(base: Path) -> list[str]:
    """Fichiers indispensables au site (pages, CSS, JS, SEO, PWA)."""
    return [f'fichier manquant : {name}'
            for name in REQUIRED_FILES if not (base / name).is_file()]


def check_trilingual_parity(base: Path) -> list[str]:
    """Chaque article doit exister dans les trois langues (FR, EN, AR)."""
    errors = []
    names = {d: {p.name for p in (base / d).glob('*.html')} for d in BLOG_DIRS}
    all_names = set().union(*names.values())
    for name in sorted(all_names):
        missing = [d for d in BLOG_DIRS if name not in names[d]]
        if missing:
            errors.append(f'article {name} absent de : {", ".join(missing)}')
    return errors


def check_no_placeholders(base: Path) -> list[str]:
    """Aucun placeholder {{...}} ne doit rester dans une page publiée."""
    errors = []
    for page in html_pages(base):
        leftovers = sorted(set(PLACEHOLDER_RE.findall(read(page))))
        if leftovers:
            rel = page.relative_to(base)
            errors.append(f'{rel} : placeholders non remplacés {leftovers}')
    return errors


def check_markers(base: Path) -> list[str]:
    """Les marqueurs d'insertion utilisés par le pipeline doivent rester en place."""
    errors = []
    for rel, start, end in (
        [(p, ARTICLES_START, ARTICLES_END) for p in BLOG_INDEXES]
        + [(p, HOME_START, HOME_END) for p in HOME_PAGES]
    ):
        text = read(base / rel)
        if text.count(start) != 1 or text.count(end) != 1:
            errors.append(f'{rel} : il faut exactement un marqueur {start} et un {end}')
        elif text.find(end) < text.find(start):
            errors.append(f'{rel} : marqueur {end} placé avant {start}')
    return errors


def iter_local_targets(page: Path, base: Path):
    """Liens internes (href/src, og:image) d'une page : (cible brute, fichier résolu, fragment).

    Les liens dans les commentaires HTML sont ignorés. Les URL absolues du
    domaine du site sont rapportées à leur fichier local.
    """
    text = COMMENT_RE.sub('', read(page))
    srcset_urls = [part.strip().split()[0]
                   for srcset in SRCSET_RE.findall(text)
                   for part in srcset.split(',') if part.strip()]
    for raw in LINK_RE.findall(text) + SOCIAL_IMG_RE.findall(text) + srcset_urls:
        raw = raw.strip()
        if not raw:
            continue
        local = site_url_to_local(base, raw)
        if local is not None:
            yield raw, local, urlsplit(raw).fragment
            continue
        if raw.startswith(EXTERNAL_PREFIXES):
            continue
        parts = urlsplit(raw)
        target_path = unquote(parts.path)
        if not target_path:           # ancre pure "#xxx" : même fichier
            yield raw, page, parts.fragment
            continue
        if target_path.startswith('/'):
            resolved = (base / target_path.lstrip('/')).resolve()
        else:
            resolved = (page.parent / target_path).resolve()
        if resolved.is_dir():
            resolved = resolved / 'index.html'
        yield raw, resolved, parts.fragment


def check_internal_links(base: Path) -> list[str]:
    """Tout lien ou ressource local (href/src) doit pointer vers un fichier existant."""
    errors = []
    for page in html_pages(base):
        rel = page.relative_to(base)
        for raw, resolved, _ in iter_local_targets(page, base):
            if not resolved.is_file():
                errors.append(f'{rel} : lien cassé "{raw}"')
    return errors


def check_anchors(base: Path) -> list[str]:
    """Toute ancre #fragment doit correspondre à un id dans la page cible."""
    errors = []
    ids_cache: dict[Path, set[str]] = {}
    for page in html_pages(base):
        rel = page.relative_to(base)
        for raw, resolved, fragment in iter_local_targets(page, base):
            if not fragment or not resolved.is_file() or resolved.suffix != '.html':
                continue
            if resolved not in ids_cache:
                ids_cache[resolved] = set(ID_RE.findall(COMMENT_RE.sub('', read(resolved))))
            if fragment not in ids_cache[resolved]:
                errors.append(f'{rel} : ancre introuvable "{raw}" '
                              f'(pas de id="{fragment}" dans {resolved.relative_to(base)})')
    return errors


def check_css_assets(base: Path) -> list[str]:
    """Les url(...) des feuilles de style doivent pointer vers des fichiers existants."""
    errors = []
    for css in sorted((base / 'css').glob('*.css')):
        for raw in CSS_URL_RE.findall(read(css)):
            raw = raw.strip()
            if not raw or raw.startswith(EXTERNAL_PREFIXES) or raw.startswith('#'):
                continue
            resolved = (css.parent / unquote(urlsplit(raw).path)).resolve()
            if not resolved.is_file():
                errors.append(f'css/{css.name} : ressource introuvable "{raw}"')
    return errors


def check_generated_artifacts(base: Path) -> list[str]:
    """Tous les artefacts générés doivent être à jour : blocs d'articles,
    index paginés du blog, carrousel d'accueil, sitemap.xml et flux RSS.

    On rejoue les générateurs sur une copie temporaire du site : si un
    fichier diffère (ou apparaît/disparaît), l'artefact commité n'était pas
    synchronisé. Les sorties sont décrites par motifs glob.
    """
    generators = [
        ('update_article_blocks.py',
         ['blog/*.html', 'en/blog/*.html', 'ar/blog/*.html'],
         "blocs d'articles désynchronisés (relancer .automation/update_article_blocks.py)"),
        ('generate_blog_indexes.py',
         ['blog/index.html', 'blog/page-*.html',
          'en/blog/index.html', 'en/blog/page-*.html',
          'ar/blog/index.html', 'ar/blog/page-*.html'],
         'index du blog obsolète (relancer .automation/generate_blog_indexes.py)'),
        ('update_home_articles.py', HOME_PAGES,
         'carrousel désynchronisé du blog (relancer .automation/update_home_articles.py)'),
        ('generate_sitemap.py', ['sitemap.xml'],
         'sitemap obsolète (relancer .automation/generate_sitemap.py)'),
        ('generate_feeds.py', ['feed.xml', 'en/feed.xml', 'ar/feed.xml'],
         'flux RSS obsolète (relancer .automation/generate_feeds.py)'),
    ]
    errors = []
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / 'site'
        shutil.copytree(base, work, ignore=shutil.ignore_patterns('.git'))
        for script, patterns, message in generators:
            script_path = work / '.automation' / script
            if not script_path.is_file():
                errors.append(f'.automation/{script} introuvable')
                continue
            proc = subprocess.run(
                [sys.executable, str(script_path), '--base', str(work)],
                capture_output=True, text=True)
            if proc.returncode != 0:
                errors.append(f'{script} a échoué : {proc.stderr.strip()}')
                continue
            outputs = set()
            for pattern in patterns:
                outputs |= {str(p.relative_to(base)) for p in base.glob(pattern)}
                outputs |= {str(p.relative_to(work)) for p in work.glob(pattern)}
            for rel in sorted(outputs):
                committed, regenerated = base / rel, work / rel
                if not regenerated.is_file():
                    errors.append(f'{rel} : fichier en trop ({message})')
                elif not committed.is_file():
                    errors.append(f'{rel} : fichier manquant ({message})')
                elif read(committed) != read(regenerated):
                    errors.append(f'{rel} : {message}')
    return errors


def check_html_basics(base: Path) -> list[str]:
    """Attributs minimaux de chaque page : lang, dir RTL, <title>, meta description, h1 unique."""
    errors = []
    for page in html_pages(base):
        rel = page.relative_to(base)
        text = read(page)
        relstr = str(rel)

        lang = LANG_RE.search(text)
        expected = 'en' if relstr.startswith('en/') else 'ar' if relstr.startswith('ar/') else 'fr'
        if not lang:
            errors.append(f'{rel} : attribut lang manquant sur <html>')
        elif lang.group(1) != expected:
            errors.append(f'{rel} : lang="{lang.group(1)}" au lieu de "{expected}"')
        if relstr.startswith('ar/') and not DIR_RE.search(text):
            errors.append(f'{rel} : dir="rtl" manquant sur <html>')

        title = TITLE_RE.search(text)
        if not title or not title.group(1).strip():
            errors.append(f'{rel} : balise <title> absente ou vide')
        if not NOINDEX_RE.search(text):   # les pages noindex (404...) en sont dispensées
            desc = META_DESC_RE.search(text)
            if not desc or not desc.group(1).strip():
                errors.append(f'{rel} : meta description absente ou vide')

        if page.parent.name == 'blog' and page.name != 'index.html':
            h1_count = len(H1_RE.findall(text))
            if h1_count != 1:
                errors.append(f'{rel} : {h1_count} balises <h1> (attendu : 1)')
    return errors


NON_ARTICLE_RE = re.compile(r'^(index|page-\d+|template|index-template)\.html$')


def check_blog_indexes(base: Path) -> list[str]:
    """Index paginés : chaque article publié doit apparaître sur exactement une
    page de l'index de sa langue, et les attributs de chargement des
    illustrations doivent suivre la règle « première en priorité, suite en lazy »."""
    errors = []
    card_re = re.compile(r'<article class="blog-card[^"]*">.*?</article>', re.DOTALL)
    img_re = re.compile(r'<img\s[^>]*>')
    for blog_dir in BLOG_DIRS:
        index_pages = [base / blog_dir / 'index.html']
        index_pages += sorted((base / blog_dir).glob('page-*.html'))
        articles = {p.name for p in (base / blog_dir).glob('*.html')
                    if not NON_ARTICLE_RE.match(p.name)}
        linked: list[str] = []
        for index in index_pages:
            rel = index.relative_to(base)
            text = read(index)
            start, end = text.find(ARTICLES_START), text.find(ARTICLES_END)
            section = text[start:end] if start != -1 and end != -1 else ''
            cards = card_re.findall(section)
            if not cards:
                errors.append(f'{rel} : aucune carte d\'article entre les marqueurs')
            for position, card in enumerate(cards):
                for href in re.findall(r'<a href="([^"]+)"', card):
                    linked.append(unquote(urlsplit(href).path))
                img = img_re.search(card)
                if not img:
                    errors.append(f'{rel} : carte sans illustration ({card[:60]}...)')
                    continue
                expected = 'fetchpriority="high"' if position == 0 else 'loading="lazy"'
                if expected not in img.group(0):
                    errors.append(f'{rel} : carte {position + 1}, attribut {expected} '
                                  f'attendu sur l\'illustration')
        missing = articles - set(linked)
        if missing:
            errors.append(f'{blog_dir} : articles publiés absents des index : '
                          f'{sorted(missing)}')
        duplicates = sorted({name for name in linked if linked.count(name) > 1})
        if duplicates:
            errors.append(f'{blog_dir} : articles présents sur plusieurs pages '
                          f'd\'index : {duplicates}')
    return errors


JSONLD_RE = re.compile(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
                       re.DOTALL)


def check_article_seo(base: Path) -> list[str]:
    """Chaque article doit porter canonical, hreflang, Open Graph, Twitter Card
    et un JSON-LD Article valide."""
    errors = []
    required_snippets = [
        'rel="canonical"', 'hreflang="fr"', 'hreflang="en"', 'hreflang="ar"',
        'property="og:title"', 'property="og:image"', 'property="og:url"',
        'name="twitter:card"', 'property="article:published_time"',
        '"speakable"',
    ]
    for page in html_pages(base):
        if page.parent.name != 'blog' or NON_ARTICLE_RE.match(page.name):
            continue
        rel = page.relative_to(base)
        text = read(page)
        for snippet in required_snippets:
            if snippet not in text:
                errors.append(f'{rel} : balise SEO manquante ({snippet})')
        articles_ld = []
        for blob in JSONLD_RE.findall(text):
            try:
                parsed = json.loads(blob)
            except json.JSONDecodeError as exc:
                errors.append(f'{rel} : JSON-LD invalide ({exc})')
                continue
            if parsed.get('@type') == 'Article':
                articles_ld.append(parsed)
        if len(articles_ld) != 1:
            errors.append(f'{rel} : {len(articles_ld)} bloc(s) JSON-LD Article (attendu : 1)')
            continue
        for field in ('headline', 'description', 'image', 'datePublished',
                      'mainEntityOfPage', 'inLanguage'):
            if not articles_ld[0].get(field):
                errors.append(f'{rel} : champ JSON-LD manquant ou vide ({field})')
    return errors


def check_sitemap_and_seo_files(base: Path) -> list[str]:
    """sitemap.xml bien formé, robots.txt déclarant le sitemap, CNAME correct."""
    errors = []
    try:
        tree = ET.parse(base / 'sitemap.xml')
        ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
        locs = [loc.text or '' for loc in tree.getroot().iter(f'{ns}loc')]
        if not locs:
            errors.append('sitemap.xml : aucune balise <loc>')
        for loc in locs:
            if not loc.startswith(f'https://{SITE_DOMAIN}/') and loc != f'https://{SITE_DOMAIN}':
                errors.append(f'sitemap.xml : URL hors domaine "{loc}"')
            else:
                local = site_url_to_local(base, loc)
                if local is not None and not local.is_file():
                    errors.append(f'sitemap.xml : page inexistante "{loc}"')
    except ET.ParseError as exc:
        errors.append(f'sitemap.xml : XML invalide ({exc})')

    for feed in ('feed.xml', 'en/feed.xml', 'ar/feed.xml'):
        try:
            ET.parse(base / feed)
        except ET.ParseError as exc:
            errors.append(f'{feed} : XML invalide ({exc})')

    robots = read(base / 'robots.txt')
    if f'Sitemap: https://{SITE_DOMAIN}/sitemap.xml' not in robots:
        errors.append('robots.txt : déclaration du sitemap manquante')

    cname = read(base / 'CNAME').strip()
    if cname != SITE_DOMAIN:
        errors.append(f'CNAME : "{cname}" au lieu de "{SITE_DOMAIN}"')
    return errors


def check_manifest_icons(base: Path) -> list[str]:
    """Les icônes du manifest PWA et de browserconfig.xml doivent exister."""
    errors = []
    manifest = json.loads(read(base / 'manifest.json'))
    for icon in manifest.get('icons', []):
        src = icon.get('src', '')
        target = base / src.lstrip('/') if src.startswith('/') else base / src
        if not target.is_file():
            errors.append(f'manifest.json : icône introuvable "{src}"')
    for src in re.findall(r'src="([^"]+)"', read(base / 'browserconfig.xml')):
        target = base / src.lstrip('/') if src.startswith('/') else base / src
        if not target.is_file():
            errors.append(f'browserconfig.xml : icône introuvable "{src}"')
    return errors


CSS_VAR_DEF_RE = re.compile(r'--([a-zA-Z0-9_-]+)\s*:')
CSS_VAR_USE_RE = re.compile(r'var\(\s*--([a-zA-Z0-9_-]+)')


def check_css_variables(base: Path) -> list[str]:
    """Toute variable var(--x) utilisée (CSS ou HTML) doit être définie dans css/*.css.

    Une variable inconnue rend la déclaration invalide sans aucun message
    d'erreur dans le navigateur (ex. : fond de carte transparent).
    """
    defined = set()
    for css in (base / 'css').glob('*.css'):
        defined |= set(CSS_VAR_DEF_RE.findall(read(css)))
    errors = []
    for css in sorted((base / 'css').glob('*.css')):
        for name in sorted(set(CSS_VAR_USE_RE.findall(read(css))) - defined):
            errors.append(f'css/{css.name} : variable inconnue var(--{name})')
    for page in html_pages(base):
        for name in sorted(set(CSS_VAR_USE_RE.findall(read(page))) - defined):
            errors.append(f'{page.relative_to(base)} : variable inconnue var(--{name})')
    return errors


def check_blog_styles(base: Path) -> list[str]:
    """Pages et templates du blog : css/blog.css requise (plus de <style> dupliqué),
    css/rtl.css requise sur toutes les pages arabes."""
    errors = []
    pages = [p for p in base.rglob('*.html') if '.git' not in p.parts]
    for page in sorted(pages):
        rel = str(page.relative_to(base))
        text = read(page)
        if page.parent.name == 'blog':
            if 'css/blog.css' not in text:
                errors.append(f'{rel} : css/blog.css non référencée')
            if re.search(r'\.(?:post-content|blog-grid)\s*\{', text):
                errors.append(f'{rel} : styles du blog dupliqués en inline '
                              f'(à maintenir dans css/blog.css)')
        if rel.startswith('ar/') and 'css/rtl.css' not in text:
            errors.append(f'{rel} : css/rtl.css non référencée (page RTL)')
    return errors


def check_fonts(base: Path) -> list[str]:
    """Polices auto-hébergées : chaque page charge css/fonts.css et plus
    aucune ressource ne pointe vers Google Fonts (RGPD, performance)."""
    errors = []
    pages = [p for p in base.rglob('*.html') if '.git' not in p.parts]
    for page in sorted(pages):
        rel = page.relative_to(base)
        text = read(page)
        if 'css/fonts.css' not in text:
            errors.append(f'{rel} : css/fonts.css non référencée')
        if 'fonts.googleapis.com' in text or 'fonts.gstatic.com' in text:
            errors.append(f'{rel} : référence à Google Fonts (polices auto-hébergées '
                          f'dans /fonts)')
    for css in sorted((base / 'css').glob('*.css')):
        if 'fonts.googleapis.com' in read(css):
            errors.append(f'css/{css.name} : @import Google Fonts '
                          f'(polices auto-hébergées dans /fonts)')
    return errors


FAQ_QUESTION_RE = re.compile(r'<span class="faq-question-text">(.*?)</span>', re.DOTALL)


def check_faq_schema(base: Path) -> list[str]:
    """Le JSON-LD FAQPage de chaque accueil doit refléter exactement les
    questions visibles sur la page (exigence Google sur ce balisage)."""
    errors = []
    for rel in HOME_PAGES:
        text = read(base / rel)
        visible = {re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', q)).strip()
                   for q in FAQ_QUESTION_RE.findall(text)}
        schema_questions: set[str] = set()
        faq_blocks = 0
        for blob in JSONLD_RE.findall(text):
            try:
                parsed = json.loads(blob)
            except json.JSONDecodeError:
                continue        # les JSON-LD invalides sont signalés ailleurs
            if parsed.get('@type') == 'FAQPage':
                faq_blocks += 1
                schema_questions = {item.get('name', '').strip()
                                    for item in parsed.get('mainEntity', [])}
        if not visible:
            continue            # pas de FAQ sur cette page : rien à exiger
        if faq_blocks != 1:
            errors.append(f'{rel} : {faq_blocks} bloc(s) JSON-LD FAQPage '
                          f'(attendu : 1)')
            continue
        for q in sorted(visible - schema_questions):
            errors.append(f'{rel} : question absente du JSON-LD FAQPage « {q} »')
        for q in sorted(schema_questions - visible):
            errors.append(f'{rel} : question du JSON-LD absente de la page « {q} »')
    return errors


def check_python_scripts(base: Path) -> list[str]:
    """Tous les scripts Python du dépôt doivent au moins compiler."""
    errors = []
    for script in sorted(base.rglob('*.py')):
        if '.git' in script.parts:
            continue
        try:
            py_compile.compile(str(script), cfile=None, doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f'{script.relative_to(base)} : erreur de compilation\n{exc.msg}')
    return errors


def check_utf8(base: Path) -> list[str]:
    """Tous les fichiers texte doivent être de l'UTF-8 valide."""
    errors = []
    for pattern in ('*.html', '*.css', '*.js', '*.json', '*.xml', '*.txt', '*.py'):
        for path in base.rglob(pattern):
            if '.git' in path.parts:
                continue
            try:
                path.read_text(encoding='utf-8')
            except UnicodeDecodeError as exc:
                errors.append(f'{path.relative_to(base)} : UTF-8 invalide ({exc})')
    return errors


CHECKS = [
    ('Fichiers requis', check_required_files),
    ('Encodage UTF-8', check_utf8),
    ('Parité trilingue du blog (FR/EN/AR)', check_trilingual_parity),
    ('Placeholders de template', check_no_placeholders),
    ('Marqueurs du pipeline', check_markers),
    ('Liens et ressources internes', check_internal_links),
    ('Ancres (#fragments)', check_anchors),
    ('Ressources des feuilles de style', check_css_assets),
    ('Variables CSS définies', check_css_variables),
    ('Feuilles de style du blog et RTL', check_blog_styles),
    ('Polices auto-hébergées', check_fonts),
    ('Cartes des index de blog (pagination)', check_blog_indexes),
    ('Artefacts générés (blocs, index, carrousel, sitemap, flux RSS)',
     check_generated_artifacts),
    ('Attributs HTML essentiels', check_html_basics),
    ('SEO des articles (canonical, Open Graph, JSON-LD)', check_article_seo),
    ('JSON-LD FAQPage synchronisé', check_faq_schema),
    ('Sitemap, flux RSS, robots.txt et CNAME', check_sitemap_and_seo_files),
    ('Icônes PWA (manifest, browserconfig)', check_manifest_icons),
    ('Compilation des scripts Python', check_python_scripts),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, default=DEFAULT_BASE,
                        help='racine du site (défaut : racine du dépôt)')
    args = parser.parse_args()
    base = args.base.resolve()

    failures = 0
    for label, check in CHECKS:
        errors = check(base)
        status = 'OK  ' if not errors else 'FAIL'
        print(f'[{status}] {label}')
        for error in errors:
            print(f'       - {error}')
        failures += len(errors)

    print()
    if failures:
        print(f'{failures} erreur(s) détectée(s).')
        return 1
    print('Tous les contrôles sont passés.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
