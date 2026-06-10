#!/usr/bin/env python3
"""Génère les index du blog (avec pagination) dans les trois langues.

À partir des pages d'articles publiées (voir article_index.py), reconstruit
blog/index.html puis blog/page-2.html, page-3.html... par tranches de
PAGE_SIZE articles, du plus récent au plus ancien. Les pages excédentaires
d'une exécution précédente sont supprimées.

Chaque page porte son canonical, ses alternates hreflang et une navigation
de pagination. La première illustration de chaque page est chargée en
priorité (LCP), les suivantes en lazy loading.

La sortie est déterministe : relancer le script sans nouveau contenu ne
change rien.

Usage :
    python3 .automation/generate_blog_indexes.py [--base /chemin/vers/le/site]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from article_index import LANGS, SITE_URL, all_articles  # noqa: E402

PAGE_SIZE = 9
WEBP_WIDTHS = [480, 800, 1200]
CARD_SIZES = '(max-width: 968px) 94vw, 370px'

LABELS = {
    'fr': {'nav': 'Pagination du blog', 'prev': 'Page précédente',
           'next': 'Page suivante', 'page': 'Page', 'suffix': ' – Page {n}'},
    'en': {'nav': 'Blog pagination', 'prev': 'Previous page',
           'next': 'Next page', 'page': 'Page', 'suffix': ' – Page {n}'},
    'ar': {'nav': 'تصفح صفحات المدونة', 'prev': 'الصفحة السابقة',
           'next': 'الصفحة التالية', 'page': 'صفحة', 'suffix': ' – الصفحة {n}'},
}

CARD_TEMPLATE = '''
            <article class="blog-card">
                <picture>
                    <source type="image/webp" srcset="{srcset}" sizes="{sizes}">
                    <img src="{image}" alt="{title}" {img_attrs}>
                </picture>
                <div class="blog-card-content">
                    <span class="blog-card-date">{date}</span>
                    <h3>{title}</h3>
                    <p>{description}</p>
                    <a href="{slug}.html">{cta}</a>
                </div>
            </article>
'''.strip('\n')


def page_filename(number: int) -> str:
    return 'index.html' if number == 1 else f'page-{number}.html'


def page_url(lang: str, number: int) -> str:
    return f'{SITE_URL}/{LANGS[lang]["blog"]}/{page_filename(number)}'


def render_head_links(lang: str, number: int) -> str:
    lines = [f'    <link rel="canonical" href="{page_url(lang, number)}">']
    for alt_lang in LANGS:
        lines.append(f'    <link rel="alternate" hreflang="{alt_lang}" '
                     f'href="{page_url(alt_lang, number)}">')
    lines.append(f'    <link rel="alternate" hreflang="x-default" '
                 f'href="{page_url("fr", number)}">')
    return '\n'.join(lines)


def render_cards(chunk: list[dict], lang: str, depth: str) -> str:
    cards = []
    for position, article in enumerate(chunk):
        slug = article['slug']
        srcset = ', '.join(f'{depth}images/blog/img-{slug}-{w}.webp {w}w'
                           for w in WEBP_WIDTHS)
        cards.append(CARD_TEMPLATE.format(
            image=f'{depth}images/blog/img-{slug}.jpg',
            srcset=srcset,
            sizes=CARD_SIZES,
            img_attrs=('fetchpriority="high" decoding="async"' if position == 0
                       else 'loading="lazy" decoding="async"'),
            title=article[lang]['title'],
            description=article[lang]['description'],
            date=article[lang]['date_label'],
            slug=slug,
            cta=LANGS[lang]['cta'],
        ))
    return '\n\n'.join(cards)


def render_pagination(lang: str, number: int, total: int) -> str:
    if total <= 1:
        return ''
    t = LABELS[lang]
    items = []
    if number > 1:
        items.append(f'            <a class="page-step page-step-prev" '
                     f'href="{page_filename(number - 1)}">{t["prev"]}</a>')
    for n in range(1, total + 1):
        if n == number:
            items.append(f'            <span class="page-num current" '
                         f'aria-current="page">{n}</span>')
        else:
            items.append(f'            <a class="page-num" href="{page_filename(n)}" '
                         f'aria-label="{t["page"]} {n}">{n}</a>')
    if number < total:
        items.append(f'            <a class="page-step page-step-next" '
                     f'href="{page_filename(number + 1)}">{t["next"]}</a>')
    body = '\n'.join(items)
    return (f'\n        <nav class="blog-pagination" aria-label="{t["nav"]}">\n'
            f'{body}\n        </nav>\n')


def build_indexes(base: Path) -> tuple[int, int]:
    articles = all_articles(base)
    chunks = [articles[i:i + PAGE_SIZE]
              for i in range(0, len(articles), PAGE_SIZE)] or [[]]
    total = len(chunks)
    written = changed = 0
    for lang, conf in LANGS.items():
        blog_dir = base / conf['blog']
        template = (blog_dir / 'index-template.html').read_text(encoding='utf-8')
        depth = '../' * (1 + conf['blog'].count('/'))
        suffix_fmt = LABELS[lang]['suffix']
        for number, chunk in enumerate(chunks, start=1):
            cards = render_cards(chunk, lang, depth)
            page = (template
                    .replace('{{TITLE_SUFFIX}}',
                             '' if number == 1 else suffix_fmt.format(n=number))
                    .replace('{{HEAD_LINKS}}', render_head_links(lang, number))
                    .replace('{{CARDS}}', cards)
                    .replace('{{PAGINATION}}', render_pagination(lang, number, total)))
            target = blog_dir / page_filename(number)
            previous = target.read_text(encoding='utf-8') if target.exists() else None
            if previous != page:
                target.write_text(page, encoding='utf-8')
                changed += 1
            written += 1
        # pages au-delà du nombre actuel (anciennes exécutions) : supprimées
        for stale in blog_dir.glob('page-*.html'):
            if (m := re.match(r'page-(\d+)\.html$', stale.name)) and int(m.group(1)) > total:
                stale.unlink()
                changed += 1
    return written, changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path,
                        default=Path(__file__).resolve().parent.parent,
                        help='racine du site (défaut : dossier parent de .automation/)')
    args = parser.parse_args()
    written, changed = build_indexes(args.base.resolve())
    print(f'index du blog : {written} page(s) générée(s), '
          f'{changed} modifiée(s)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
