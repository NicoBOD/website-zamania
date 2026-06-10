#!/usr/bin/env python3
"""Génère les flux RSS du blog : feed.xml (FR), en/feed.xml, ar/feed.xml.

Les articles proviennent des index de blog (voir article_index.py). La sortie
est déterministe : le pubDate est fixé à 08:00 heure de Paris le jour de
publication, et lastBuildDate reprend la date du dernier article.

Usage :
    python3 .automation/generate_feeds.py [--base /chemin/vers/le/site]
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from article_index import LANGS, SITE_URL, all_articles  # noqa: E402

PARIS_TZ = timezone(timedelta(hours=2))

CHANNELS = {
    'fr': {
        'path': 'feed.xml',
        'title': 'Blog ZamanIA',
        'description': "Automatisation IA pour TPE et PME : analyses, cas d'usage "
                       'et bonnes pratiques pour gagner du temps et de la marge.',
    },
    'en': {
        'path': 'en/feed.xml',
        'title': 'ZamanIA Blog',
        'description': 'AI automation for SMBs: insights, use cases and best '
                       'practices to save time and protect your margins.',
    },
    'ar': {
        'path': 'ar/feed.xml',
        'title': 'مدونة زمانيا',
        'description': 'أتمتة الذكاء الاصطناعي للشركات الصغيرة والمتوسطة: '
                       'تحليلات وحالات استخدام وممارسات عملية.',
    },
}


def rfc822(d) -> str:
    return format_datetime(datetime(d.year, d.month, d.day, 8, 0, 0, tzinfo=PARIS_TZ))


def build_feed(lang: str, articles: list[dict]) -> str:
    conf = CHANNELS[lang]
    blog_url = f'{SITE_URL}/{LANGS[lang]["blog"]}/index.html'
    feed_url = f'{SITE_URL}/{conf["path"]}'
    last_build = rfc822(articles[0]['date']) if articles else rfc822_now()

    items = []
    for article in articles:
        data = article[lang]
        image_url = f'{SITE_URL}/images/blog/{article["image"]}'
        items.append(f'''        <item>
            <title>{escape(data['title'])}</title>
            <link>{escape(data['url'])}</link>
            <guid isPermaLink="true">{escape(data['url'])}</guid>
            <description>{escape(data['description'])}</description>
            <enclosure url="{escape(image_url)}" type="image/jpeg" length="0"/>
            <pubDate>{rfc822(article['date'])}</pubDate>
        </item>''')

    items_xml = '\n'.join(items)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- Généré par .automation/generate_feeds.py : ne pas éditer à la main. -->
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <title>{escape(conf['title'])}</title>
        <link>{escape(blog_url)}</link>
        <atom:link href="{escape(feed_url)}" rel="self" type="application/rss+xml"/>
        <description>{escape(conf['description'])}</description>
        <language>{lang}</language>
        <lastBuildDate>{last_build}</lastBuildDate>
{items_xml}
    </channel>
</rss>
'''


def rfc822_now() -> str:
    return format_datetime(datetime.now(tz=PARIS_TZ))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path,
                        default=Path(__file__).resolve().parent.parent,
                        help='racine du site (défaut : dossier parent de .automation/)')
    args = parser.parse_args()
    base = args.base.resolve()

    articles = all_articles(base)
    for lang, conf in CHANNELS.items():
        target = base / conf['path']
        content = build_feed(lang, articles)
        changed = not target.exists() or target.read_text(encoding='utf-8') != content
        target.write_text(content, encoding='utf-8')
        print(f'{conf["path"]} : {len(articles)} articles, '
              f'{"mis à jour" if changed else "déjà à jour"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
