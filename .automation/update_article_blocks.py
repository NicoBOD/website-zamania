#!/usr/bin/env python3
"""Met à jour les blocs dérivés de chaque page d'article (les trois langues).

Blocs maintenus, recalculés à chaque publication pour TOUS les articles :

  - temps de lecture (span dans l'en-tête, à côté de la date) ;
  - boutons de partage (LinkedIn, X, WhatsApp, copie du lien) ;
  - « À lire aussi » : les 3 articles les plus récents (hors article courant) ;
  - navigation article précédent / article suivant (ordre chronologique).

Idempotent et déterministe : le contenu ne dépend que des pages publiées.
Conçu pour tourner depuis publish.py comme en CI (aucune dépendance externe).

Usage :
    python3 .automation/update_article_blocks.py [--base /chemin/vers/le/site]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from article_index import LANGS, all_articles  # noqa: E402

SHARE_START = '<!-- SHARE_START -->'
SHARE_END = '<!-- SHARE_END -->'
RELATED_START = '<!-- RELATED_START -->'
RELATED_END = '<!-- RELATED_END -->'
PREVNEXT_START = '<!-- PREVNEXT_START -->'
PREVNEXT_END = '<!-- PREVNEXT_END -->'

RELATED_COUNT = 3
WEBP_WIDTHS = [480, 800, 1200]
RELATED_SIZES = '(max-width: 640px) 94vw, 240px'

# Vitesse de lecture (mots/minute) : latin ~220, arabe un peu plus lent.
WPM = {'fr': 220, 'en': 220, 'ar': 180}

LABELS = {
    'fr': {'share': 'Partager cet article', 'copy': 'Copier le lien',
           'copied': 'Lien copié !', 'related': 'À lire aussi',
           'prev': 'Article précédent', 'next': 'Article suivant'},
    'en': {'share': 'Share this article', 'copy': 'Copy link',
           'copied': 'Link copied!', 'related': 'Further reading',
           'prev': 'Previous article', 'next': 'Next article'},
    'ar': {'share': 'شارك هذا المقال', 'copy': 'نسخ الرابط',
           'copied': 'تم نسخ الرابط!', 'related': 'اقرأ أيضاً',
           'prev': 'المقال السابق', 'next': 'المقال التالي'},
}

ICONS = {
    'linkedin': '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>',
    'x': '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>',
    'whatsapp': '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>',
    'copy': '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>',
}


def webp_srcset(slug: str) -> str:
    # Les cartes « À lire aussi » pointent dans le même dossier (../images vu
    # depuis blog/, ../../ depuis en|ar/blog/) ; le préfixe est passé à part.
    return ', '.join(f'img-{slug}-{w}.webp {w}w' for w in WEBP_WIDTHS)


def reading_minutes(html: str, lang: str) -> int:
    """Compte les mots du corps de l'article (entre sommaire et signature)."""
    sommaire = re.search(r'<div class="post-sommaire">.*?</div>', html, re.DOTALL)
    author = re.search(r'<div class="post-author">', html)
    span = html[sommaire.end() if sommaire else 0:author.start() if author else len(html)]
    span = re.sub(r'<!--.*?-->', ' ', span, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', span)
    words = len(text.split())
    return max(1, round(words / WPM[lang]))


def reading_label(minutes: int, lang: str) -> str:
    if lang == 'fr':
        return f'{minutes} min de lecture'
    if lang == 'en':
        return f'{minutes} min read'
    if minutes == 1:
        return 'دقيقة قراءة واحدة'
    if minutes == 2:
        return 'دقيقتا قراءة'
    if minutes <= 10:
        return f'{minutes} دقائق قراءة'
    return f'{minutes} دقيقة قراءة'


def upsert_reading_time(html: str, label: str) -> str:
    span = f'<span class="post-reading-time">{label}</span>'
    if 'class="post-reading-time"' in html:
        return re.sub(r'<span class="post-reading-time">[^<]*</span>', span, html)
    return re.sub(r'(<span class="post-date">.*?</span>)',
                  r'\1\n                ' + span, html, count=1)


def upsert_block(html: str, start: str, end: str, content: str,
                 anchor_re: str, page: Path, before: bool = False) -> str:
    """Remplace le bloc [start..end] s'il existe, sinon l'insère à l'ancre
    (juste après le motif, ou juste avant si before=True)."""
    block = f'{start}\n{content}\n                {end}'
    if start in html and end in html:
        i, j = html.find(start), html.find(end) + len(end)
        return html[:i] + block + html[j:]
    match = re.search(anchor_re, html, re.DOTALL)
    if not match:
        raise ValueError(f"{page} : point d'insertion introuvable pour {start}")
    if before:
        return html[:match.start()] + block + '\n\n                ' + html[match.start():]
    return html[:match.end()] + '\n\n                ' + block + html[match.end():]


def share_block(url: str, title: str, lang: str) -> str:
    t = LABELS[lang]
    u, txt = quote(url, safe=''), quote(title, safe='')
    return f'''                <div class="post-share">
                    <span class="post-share-label">{t['share']}</span>
                    <div class="post-share-buttons">
                        <a href="https://www.linkedin.com/sharing/share-offsite/?url={u}" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">{ICONS['linkedin']}</a>
                        <a href="https://twitter.com/intent/tweet?url={u}&amp;text={txt}" target="_blank" rel="noopener noreferrer" aria-label="X (Twitter)">{ICONS['x']}</a>
                        <a href="https://wa.me/?text={txt}%20{u}" target="_blank" rel="noopener noreferrer" aria-label="WhatsApp">{ICONS['whatsapp']}</a>
                        <button type="button" class="share-copy" data-copied="{t['copied']}" aria-label="{t['copy']}">{ICONS['copy']}</button>
                    </div>
                </div>'''


def related_block(article: dict, others: list[dict], lang: str, depth: str) -> str:
    t = LABELS[lang]
    cards = []
    for other in others:
        slug = other['slug']
        srcset = ', '.join(f'{depth}images/blog/img-{slug}-{w}.webp {w}w'
                           for w in WEBP_WIDTHS)
        cards.append(f'''                    <a class="related-card" href="{slug}.html">
                        <picture>
                            <source type="image/webp" srcset="{srcset}" sizes="{RELATED_SIZES}">
                            <img src="{depth}images/blog/img-{slug}.jpg" alt="" loading="lazy" decoding="async">
                        </picture>
                        <span class="related-card-date">{other[lang]['date_label']}</span>
                        <span class="related-card-title">{other[lang]['title']}</span>
                    </a>''')
    cards_html = '\n'.join(cards)
    return f'''                <section class="post-related" aria-label="{t['related']}">
                    <h2 class="related-heading">{t['related']}</h2>
                    <div class="related-grid">
{cards_html}
                    </div>
                </section>'''


def prevnext_block(newer: dict | None, older: dict | None, lang: str) -> str:
    t = LABELS[lang]
    tiles = []
    if older:
        tiles.append(f'''                    <a class="prevnext-card prevnext-prev" href="{older['slug']}.html">
                        <span class="prevnext-label">{t['prev']}</span>
                        <span class="prevnext-title">{older[lang]['title']}</span>
                    </a>''')
    if newer:
        tiles.append(f'''                    <a class="prevnext-card prevnext-next" href="{newer['slug']}.html">
                        <span class="prevnext-label">{t['next']}</span>
                        <span class="prevnext-title">{newer[lang]['title']}</span>
                    </a>''')
    tiles_html = '\n'.join(tiles)
    return f'''                <nav class="post-prevnext" aria-label="{t['prev']} / {t['next']}">
{tiles_html}
                </nav>'''


def update_article(base: Path, articles: list[dict], position: int) -> int:
    article = articles[position]
    others = [a for i, a in enumerate(articles) if i != position][:RELATED_COUNT]
    newer = articles[position - 1] if position > 0 else None
    older = articles[position + 1] if position + 1 < len(articles) else None
    changed = 0
    for lang, conf in LANGS.items():
        depth = '../' * (1 + conf['blog'].count('/'))
        page = base / conf['blog'] / f"{article['slug']}.html"
        html = original = page.read_text(encoding='utf-8')

        minutes = reading_minutes(html, lang)
        html = upsert_reading_time(html, reading_label(minutes, lang))
        html = upsert_block(html, SHARE_START, SHARE_END,
                            share_block(article[lang]['url'], article[lang]['title'], lang),
                            r'<div class="post-author">', page, before=True)
        html = upsert_block(html, RELATED_START, RELATED_END,
                            related_block(article, others, lang, depth),
                            r'<div class="post-cta">.*?</div>', page)
        html = upsert_block(html, PREVNEXT_START, PREVNEXT_END,
                            prevnext_block(newer, older, lang),
                            re.escape(RELATED_END), page)
        if html != original:
            page.write_text(html, encoding='utf-8')
            changed += 1
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path,
                        default=Path(__file__).resolve().parent.parent,
                        help='racine du site (défaut : dossier parent de .automation/)')
    args = parser.parse_args()
    base = args.base.resolve()

    articles = all_articles(base)
    changed = sum(update_article(base, articles, i) for i in range(len(articles)))
    print(f'blocs d\'articles : {len(articles)} article(s), '
          f'{changed} page(s) mise(s) à jour')
    return 0


if __name__ == '__main__':
    sys.exit(main())
