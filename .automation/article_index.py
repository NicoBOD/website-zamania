"""Inventaire des articles du blog ZamanIA (bibliothèque commune).

Source de vérité : les pages HTML publiées. L'ordre des articles est celui
des cartes de l'index FR (du plus récent au plus ancien), tel que maintenu
par le pipeline de publication.

Utilisée par generate_sitemap.py, generate_feeds.py et publish.py.
Aucune dépendance hors bibliothèque standard.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import date
from pathlib import Path

SITE_URL = 'https://zamania.fr'

LANGS = {
    'fr': {'blog': 'blog', 'home': 'index.html', 'home_url': f'{SITE_URL}/',
           'locale': 'fr_FR', 'cta': "Lire l'article"},
    'en': {'blog': 'en/blog', 'home': 'en/index.html', 'home_url': f'{SITE_URL}/en/',
           'locale': 'en_US', 'cta': 'Read article'},
    'ar': {'blog': 'ar/blog', 'home': 'ar/index.html', 'home_url': f'{SITE_URL}/ar/',
           'locale': 'ar_AR', 'cta': 'اقرأ المقال'},
}

MONTHS_FR = ['janvier', 'fevrier', 'mars', 'avril', 'mai', 'juin', 'juillet',
             'aout', 'septembre', 'octobre', 'novembre', 'decembre']
MONTHS_EN = ['january', 'february', 'march', 'april', 'may', 'june', 'july',
             'august', 'september', 'october', 'november', 'december']
MONTHS_AR = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو',
             'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']

ARTICLES_START = '<!-- ARTICLES_LIST_START -->'
ARTICLES_END = '<!-- ARTICLES_LIST_END -->'

CARD_HREF_RE = re.compile(r'<article class="blog-card[^"]*">.*?href="([^"#]+)\.html"',
                          re.DOTALL)
H1_RE = re.compile(r'<h1 class="post-title">\s*(.*?)\s*</h1>', re.DOTALL)
DATE_SPAN_RE = re.compile(r'<span class="post-date">\s*(.*?)\s*</span>', re.DOTALL)
DESC_RE = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"', re.IGNORECASE)
IMAGE_RE = re.compile(r'<img\s+src="([^"]+)"[^>]*class="post-image"')


def _strip_accents(text: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                   if unicodedata.category(c) != 'Mn')


# Tout nom de mois connu (FR/EN/AR, sans accents, minuscules) -> numéro de mois.
_MONTH_LOOKUP = {}
for names in (MONTHS_FR, MONTHS_EN, MONTHS_AR):
    for i, name in enumerate(names, start=1):
        _MONTH_LOOKUP[_strip_accents(name).lower()] = i


def parse_date_label(label: str) -> date:
    """Interprète un libellé de date d'article : "10 Juin 2026", "June 3, 2026",
    "10 يونيو 2026"… Lève ValueError si le libellé est inintelligible."""
    day = month = year = None
    for token in re.split(r'[\s,]+', label.strip()):
        if not token:
            continue
        if token.isdigit():
            value = int(token)
            if value > 1900:
                year = value
            elif day is None:
                day = value
        else:
            key = _strip_accents(token).lower()
            if key in _MONTH_LOOKUP:
                month = _MONTH_LOOKUP[key]
    if not (day and month and year):
        raise ValueError(f'libellé de date illisible : "{label}"')
    return date(year, month, day)


def date_label(d: date, lang: str) -> str:
    """Formate une date dans le style des libellés existants du site."""
    if lang == 'fr':
        return f'{d.day} {MONTHS_FR[d.month - 1].capitalize()} {d.year}'
    if lang == 'en':
        return f'{MONTHS_EN[d.month - 1].capitalize()} {d.day}, {d.year}'
    if lang == 'ar':
        return f'{d.day} {MONTHS_AR[d.month - 1]} {d.year}'
    raise ValueError(f'langue inconnue : {lang}')


def article_url(slug: str, lang: str) -> str:
    return f'{SITE_URL}/{LANGS[lang]["blog"]}/{slug}.html'


def ordered_slugs(base: Path) -> list[str]:
    """Slugs des articles, du plus récent au plus ancien (ordre de l'index FR)."""
    html = (base / 'blog' / 'index.html').read_text(encoding='utf-8')
    start, end = html.find(ARTICLES_START), html.find(ARTICLES_END)
    if start == -1:
        raise ValueError(f'marqueur {ARTICLES_START} introuvable dans blog/index.html')
    section = html[start:end] if end != -1 else html[start:]
    return CARD_HREF_RE.findall(section)


def load_article(base: Path, slug: str) -> dict:
    """Charge les métadonnées d'un article depuis ses trois pages HTML.

    Renvoie {'slug', 'date' (datetime.date), 'image' (nom de fichier),
    et par langue : {'title', 'description', 'date_label', 'url'}}.
    """
    info: dict = {'slug': slug}
    for lang, conf in LANGS.items():
        page = base / conf['blog'] / f'{slug}.html'
        html = page.read_text(encoding='utf-8')
        title = H1_RE.search(html)
        desc = DESC_RE.search(html)
        date_span = DATE_SPAN_RE.search(html)
        image = IMAGE_RE.search(html)
        if not (title and desc and date_span and image):
            raise ValueError(f'métadonnées incomplètes dans {page}')
        info[lang] = {
            'title': title.group(1),
            'description': desc.group(1),
            'date_label': date_span.group(1),
            'url': article_url(slug, lang),
        }
        if lang == 'fr':
            info['date'] = parse_date_label(date_span.group(1))
            info['image'] = image.group(1).rsplit('/', 1)[-1]
    return info


def all_articles(base: Path) -> list[dict]:
    """Tous les articles publiés, du plus récent au plus ancien."""
    return [load_article(base, slug) for slug in ordered_slugs(base)]
