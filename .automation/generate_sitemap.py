#!/usr/bin/env python3
"""Génère sitemap.xml à partir des pages publiées.

Couvre les pages d'accueil, les index de blog et tous les articles dans les
trois langues (avec leurs alternates hreflang), ainsi que les pages légales.
La sortie est déterministe : relancer le script sans nouveau contenu ne
change rien.

Usage :
    python3 .automation/generate_sitemap.py [--base /chemin/vers/le/site]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from article_index import LANGS, SITE_URL, all_articles  # noqa: E402

LEGAL_PAGES = ['cgu.html', 'cgv.html', 'mentions-legales.html',
               'politique-de-confidentialite.html', 'charte-ia-ethique.html']

HEADER = f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- Généré par .automation/generate_sitemap.py : ne pas éditer à la main. -->
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
'''


def url_entry(loc: str, lastmod: str | None = None, changefreq: str | None = None,
              priority: str | None = None, alternates: dict[str, str] | None = None) -> str:
    lines = ['    <url>', f'        <loc>{escape(loc)}</loc>']
    if lastmod:
        lines.append(f'        <lastmod>{lastmod}</lastmod>')
    if changefreq:
        lines.append(f'        <changefreq>{changefreq}</changefreq>')
    if priority:
        lines.append(f'        <priority>{priority}</priority>')
    for hreflang, href in (alternates or {}).items():
        lines.append(f'        <xhtml:link rel="alternate" hreflang="{hreflang}" '
                     f'href="{escape(href)}"/>')
    lines.append('    </url>')
    return '\n'.join(lines)


def build_sitemap(base: Path) -> str:
    articles = all_articles(base)
    newest = articles[0]['date'].isoformat() if articles else None

    home_alts = {lang: conf['home_url'] for lang, conf in LANGS.items()}
    home_alts['x-default'] = LANGS['fr']['home_url']
    blog_alts = {lang: f'{SITE_URL}/{conf["blog"]}/index.html'
                 for lang, conf in LANGS.items()}
    blog_alts['x-default'] = blog_alts['fr']

    entries = []
    for lang, conf in LANGS.items():
        entries.append(url_entry(conf['home_url'], lastmod=newest, changefreq='weekly',
                                 priority='1.0' if lang == 'fr' else '0.9',
                                 alternates=home_alts))
    for lang in LANGS:
        entries.append(url_entry(blog_alts[lang], lastmod=newest, changefreq='weekly',
                                 priority='0.8', alternates=blog_alts))
    for article in articles:
        alts = {lang: article[lang]['url'] for lang in LANGS}
        alts['x-default'] = article['fr']['url']
        for lang in LANGS:
            entries.append(url_entry(article[lang]['url'],
                                     lastmod=article['date'].isoformat(),
                                     changefreq='monthly', priority='0.7',
                                     alternates=alts))
    for page in LEGAL_PAGES:
        entries.append(url_entry(f'{SITE_URL}/{page}', changefreq='yearly',
                                 priority='0.3'))

    return HEADER + '\n'.join(entries) + '\n</urlset>\n'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path,
                        default=Path(__file__).resolve().parent.parent,
                        help='racine du site (défaut : dossier parent de .automation/)')
    args = parser.parse_args()
    base = args.base.resolve()

    target = base / 'sitemap.xml'
    content = build_sitemap(base)
    changed = not target.exists() or target.read_text(encoding='utf-8') != content
    target.write_text(content, encoding='utf-8')
    print(f'sitemap.xml : {content.count("<loc>")} URL, '
          f'{"mis à jour" if changed else "déjà à jour"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
