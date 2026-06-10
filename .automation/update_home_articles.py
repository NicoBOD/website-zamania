"""Synchronise la section "Nos derniers Articles" des pages d'accueil.

Extrait les 5 dernières cartes d'articles de chaque blog (FR/EN/AR) et
régénère le carrousel de la page d'accueil correspondante, entre les
marqueurs <!-- HOME_ARTICLES_START --> et <!-- HOME_ARTICLES_END -->.

À exécuter après chaque publication d'article (le pipeline
publish_zamania_article.py l'appelle automatiquement après la mise à
jour des index de blog). Le script est idempotent : le relancer sans
nouvel article ne change rien.

Usage :
    python3 update_home_articles.py [--base /chemin/vers/website-zamania]

Sans argument, la racine du site est le dossier parent de .automation/.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MAX_ARTICLES = 5
BLOG_START = '<!-- ARTICLES_LIST_START -->'
BLOG_END = '<!-- ARTICLES_LIST_END -->'
HOME_START = '<!-- HOME_ARTICLES_START -->'
HOME_END = '<!-- HOME_ARTICLES_END -->'

# Pour chaque langue : chemin de l'index du blog et de la page d'accueil,
# relatifs à la racine du site. Les chemins des cartes du blog sont relatifs
# au dossier blog/ ; vus depuis l'accueil (un niveau au-dessus), les images
# perdent un "../" et les liens d'articles gagnent un préfixe "blog/".
LANGS = {
    'fr': {'blog_index': 'blog/index.html', 'home': 'index.html'},
    'en': {'blog_index': 'en/blog/index.html', 'home': 'en/index.html'},
    'ar': {'blog_index': 'ar/blog/index.html', 'home': 'ar/index.html'},
}

CARD_RE = re.compile(r'<article class="blog-card">.*?</article>', re.DOTALL)
IMG_RE = re.compile(r'<img\s+src="([^"]+)"\s+alt="([^"]*)"')
DATE_RE = re.compile(r'<span class="blog-card-date">(.*?)</span>', re.DOTALL)
TITLE_RE = re.compile(r'<h3>(.*?)</h3>', re.DOTALL)
LINK_RE = re.compile(r'<a href="([^"]+)">(.*?)</a>', re.DOTALL)


def extract_cards(blog_index: Path) -> list[dict]:
    html = blog_index.read_text(encoding='utf-8')
    start = html.find(BLOG_START)
    end = html.find(BLOG_END)
    if start == -1:
        raise ValueError(f'marqueur {BLOG_START} introuvable dans {blog_index}')
    section = html[start:end] if end != -1 else html[start:]

    cards = []
    for block in CARD_RE.findall(section)[:MAX_ARTICLES]:
        img = IMG_RE.search(block)
        date = DATE_RE.search(block)
        title = TITLE_RE.search(block)
        link = LINK_RE.search(block)
        if not (img and date and title and link):
            raise ValueError(f'carte illisible dans {blog_index} :\n{block}')
        cards.append({
            'image': re.sub(r'^\.\./', '', img.group(1), count=1),
            'alt': img.group(2),
            'date': date.group(1).strip(),
            'title': title.group(1).strip(),
            'href': 'blog/' + link.group(1),
            'cta': link.group(2).strip(),
        })
    return cards


def render_card(card: dict) -> str:
    return f'''                <article class="blog-card carousel-card">
                    <img src="{card['image']}" alt="{card['alt']}" loading="lazy">
                    <div class="blog-card-content">
                        <span class="blog-card-date">{card['date']}</span>
                        <h3>{card['title']}</h3>
                        <a href="{card['href']}" class="blog-card-link">{card['cta']}</a>
                    </div>
                </article>'''


def update_home(home: Path, cards: list[dict]) -> bool:
    html = home.read_text(encoding='utf-8')
    start = html.find(HOME_START)
    end = html.find(HOME_END)
    if start == -1 or end == -1 or end < start:
        raise ValueError(f'marqueurs {HOME_START}/{HOME_END} introuvables dans {home}')

    block = HOME_START + '\n' + '\n'.join(render_card(c) for c in cards) + '\n                '
    updated = html[:start] + block + html[end:]
    if updated == html:
        return False
    home.write_text(updated, encoding='utf-8')
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, default=Path(__file__).resolve().parent.parent,
                        help='racine du site (défaut : dossier parent de .automation/)')
    args = parser.parse_args()

    result = {}
    for lang, paths in LANGS.items():
        cards = extract_cards(args.base / paths['blog_index'])
        changed = update_home(args.base / paths['home'], cards)
        result[lang] = {
            'articles': [c['href'] for c in cards],
            'updated': changed,
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
