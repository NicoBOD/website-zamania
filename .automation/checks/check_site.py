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
    'css/styles.css', 'css/dark-mode.css', 'css/rtl.css',
    'js/navigation.js', 'js/theme.js', 'js/home-articles.js',
    'blog/index.html', 'blog/template.html',
    'en/index.html', 'en/blog/index.html', 'en/blog/template.html',
    'ar/index.html', 'ar/blog/index.html', 'ar/blog/template.html',
]
ARTICLES_START = '<!-- ARTICLES_LIST_START -->'
ARTICLES_END = '<!-- ARTICLES_LIST_END -->'
HOME_START = '<!-- HOME_ARTICLES_START -->'
HOME_END = '<!-- HOME_ARTICLES_END -->'

PLACEHOLDER_RE = re.compile(r'\{\{\s*[A-Z_]+\s*\}\}')
LINK_RE = re.compile(r'(?:href|src)\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
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
    return path.name == 'template.html'


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
    for raw in LINK_RE.findall(text) + SOCIAL_IMG_RE.findall(text):
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


def check_home_carousel_sync(base: Path) -> list[str]:
    """Le carrousel des pages d'accueil doit refléter les 5 derniers articles.

    On rejoue update_home_articles.py sur une copie temporaire du site : s'il
    modifie une page d'accueil, c'est que le carrousel n'était pas synchronisé.
    """
    script = base / '.automation' / 'update_home_articles.py'
    if not script.is_file():
        return ['.automation/update_home_articles.py introuvable']
    errors = []
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / 'site'
        shutil.copytree(base, work, ignore=shutil.ignore_patterns('.git'))
        proc = subprocess.run(
            [sys.executable, str(work / '.automation' / 'update_home_articles.py'),
             '--base', str(work)],
            capture_output=True, text=True)
        if proc.returncode != 0:
            return [f'update_home_articles.py a échoué : {proc.stderr.strip()}']
        for rel in HOME_PAGES:
            if read(base / rel) != read(work / rel):
                errors.append(f'{rel} : carrousel désynchronisé du blog '
                              f'(relancer .automation/update_home_articles.py)')
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


def check_blog_indexes(base: Path) -> list[str]:
    """Chaque carte du blog doit pointer vers un article et une image existants."""
    errors = []
    card_re = re.compile(r'<article class="blog-card[^"]*">.*?</article>', re.DOTALL)
    for rel in BLOG_INDEXES:
        index = base / rel
        text = read(index)
        start, end = text.find(ARTICLES_START), text.find(ARTICLES_END)
        section = text[start:end] if start != -1 and end != -1 else ''
        cards = card_re.findall(section)
        if not cards:
            errors.append(f'{rel} : aucune carte d\'article entre les marqueurs')
        articles = {p.name for p in (index.parent).glob('*.html')} - {'index.html', 'template.html'}
        linked = set()
        for card in cards:
            for href in re.findall(r'href="([^"]+)"', card):
                linked.add(unquote(urlsplit(href).path))
        missing = articles - linked
        if missing:
            errors.append(f'{rel} : articles publiés absents de l\'index : {sorted(missing)}')
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
    ('Cartes des index de blog', check_blog_indexes),
    ('Synchronisation du carrousel d\'accueil', check_home_carousel_sync),
    ('Attributs HTML essentiels', check_html_basics),
    ('Sitemap, robots.txt et CNAME', check_sitemap_and_seo_files),
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
