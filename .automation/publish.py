#!/usr/bin/env python3
"""Publie un article de blog ZamanIA dans les trois langues.

Point d'entrée unique du pipeline de publication : à partir d'un fichier
JSON décrivant l'article (voir examples/article.example.json), le script

  1. valide le contenu (slug, date, champs requis, ancres du sommaire) ;
  2. vérifie que l'illustration images/blog/img-<slug>.jpg existe et génère
     ses variantes WebP (480/800/1200 px) ;
  3. rend les trois pages depuis les templates blog/template.html ;
  4. met à jour les blocs dérivés de tous les articles (temps de lecture,
     partage, « À lire aussi », précédent/suivant) ;
  5. régénère les index du blog avec leur pagination ;
  6. resynchronise le carrousel des pages d'accueil ;
  7. régénère sitemap.xml et les flux RSS ;
  8. exécute les contrôles d'intégrité (checks/check_site.py).

Le script est idempotent : republier un slug déjà publié est refusé sauf
avec --force (qui réécrit les pages sans dupliquer les cartes).

Usage :
    python3 .automation/publish.py article.json [--base RACINE] [--image FICHIER] [--force]

Format du JSON attendu :
    {
      "slug": "mon-article",            # kebab-case, sans accents
      "date": "2026-06-12",             # date de publication (ISO)
      "fr": {"title": "...", "description": "...", "content_html": "..."},
      "en": {...}, "ar": {...}
    }

Le sommaire est dérivé automatiquement des <h2 id="..."> du content_html.
Les titres et descriptions ne doivent pas contenir de guillemets doubles
(ils sont insérés dans des attributs HTML et du JSON-LD).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from article_index import LANGS, date_label  # noqa: E402

SLUG_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
H2_RE = re.compile(r'<h2\s+id="([^"]+)"\s*>\s*(.*?)\s*</h2>', re.DOTALL)
H2_ANY_RE = re.compile(r'<h2[\s>]')

# Variantes WebP générées pour chaque illustration (srcset responsive).
WEBP_WIDTHS = [480, 800, 1200]


def webp_srcset(prefix: str, slug: str) -> str:
    return ', '.join(f'{prefix}images/blog/img-{slug}-{w}.webp {w}w' for w in WEBP_WIDTHS)


def generate_image_variants(image_path: Path) -> list[Path]:
    """Décline l'illustration JPEG en WebP 480/800/1200 px de large.

    Nécessite Pillow (uniquement à la publication, jamais en CI).
    Les images plus étroites que la cible ne sont pas agrandies.
    """
    try:
        from PIL import Image
    except ImportError:
        raise PublicationError(
            'Pillow est requis pour générer les variantes WebP : pip install Pillow')
    written = []
    with Image.open(image_path) as img:
        img = img.convert('RGB')
        for width in WEBP_WIDTHS:
            target = image_path.with_name(f'{image_path.stem}-{width}.webp')
            scale = min(width, img.width) / img.width
            resized = img.resize((round(img.width * scale), round(img.height * scale)),
                                 Image.LANCZOS)
            resized.save(target, 'WEBP', quality=80, method=6)
            written.append(target)
    return written


class PublicationError(SystemExit):
    def __init__(self, message: str):
        super().__init__(f'ERREUR : {message}')


def load_and_validate(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        raise PublicationError(f'lecture de {path} impossible : {exc}')

    slug = data.get('slug', '')
    if not SLUG_RE.match(slug):
        raise PublicationError(f'slug invalide "{slug}" (attendu : kebab-case ascii)')
    try:
        data['date_obj'] = date.fromisoformat(data.get('date', ''))
    except ValueError:
        raise PublicationError(f'date invalide "{data.get("date")}" (attendu : AAAA-MM-JJ)')

    for lang in LANGS:
        block = data.get(lang)
        if not isinstance(block, dict):
            raise PublicationError(f'section "{lang}" manquante')
        for field in ('title', 'description', 'content_html'):
            value = block.get(field, '')
            if not isinstance(value, str) or not value.strip():
                raise PublicationError(f'{lang}.{field} manquant ou vide')
        for field in ('title', 'description'):
            if '"' in block[field]:
                raise PublicationError(
                    f'{lang}.{field} contient un guillemet double (interdit : '
                    f'la valeur est insérée dans des attributs HTML et du JSON-LD)')
        if '{{' in block['content_html']:
            raise PublicationError(f'{lang}.content_html contient "{{{{" (placeholder ?)')
        content = block['content_html']
        h2_with_id = H2_RE.findall(content)
        if len(H2_ANY_RE.findall(content)) != len(h2_with_id):
            raise PublicationError(f'{lang}.content_html : chaque <h2> doit porter un id '
                                   f'(utilisé pour le sommaire)')
        if len(h2_with_id) < 2:
            raise PublicationError(f'{lang}.content_html : au moins 2 sections <h2 id=...> '
                                   f'attendues (sommaire)')
        block['sommaire'] = '\n'.join(
            f'<li><a href="#{anchor}">{re.sub(r"<[^>]+>", "", label)}</a></li>'
            for anchor, label in h2_with_id)
    return data


def render_pages(base: Path, data: dict) -> list[Path]:
    slug = data['slug']
    written = []
    for lang, conf in LANGS.items():
        blog_dir = base / conf['blog']
        template = (blog_dir / 'template.html').read_text(encoding='utf-8')
        depth = '../' * (1 + conf['blog'].count('/'))
        page = (template
                .replace('{{TITLE}}', data[lang]['title'])
                .replace('{{DATE}}', date_label(data['date_obj'], lang))
                .replace('{{DATE_ISO}}', data['date_obj'].isoformat())
                .replace('{{DESCRIPTION}}', data[lang]['description'])
                .replace('{{SOMMAIRE}}', data[lang]['sommaire'])
                .replace('{{CONTENT}}', data[lang]['content_html'])
                .replace('{{IMAGE_URL}}', f'{depth}images/blog/img-{slug}.jpg')
                .replace('{{IMAGE_SRCSET}}', webp_srcset(depth, slug))
                .replace('{{SLUG}}', slug))
        target = blog_dir / f'{slug}.html'
        target.write_text(page, encoding='utf-8')
        written.append(target)
    return written


def run_step(label: str, command: list[str]) -> None:
    proc = subprocess.run(command, capture_output=True, text=True)
    output = (proc.stdout + proc.stderr).strip()
    if proc.returncode != 0:
        raise PublicationError(f'{label} a échoué :\n{output}')
    print(f'--- {label}\n{output}')


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('article', type=Path, help="fichier JSON de l'article")
    parser.add_argument('--base', type=Path,
                        default=Path(__file__).resolve().parent.parent,
                        help='racine du site (défaut : dossier parent de .automation/)')
    parser.add_argument('--image', type=Path, default=None,
                        help="illustration à copier vers images/blog/img-<slug>.jpg")
    parser.add_argument('--force', action='store_true',
                        help='réécrit un article déjà publié')
    args = parser.parse_args()
    base = args.base.resolve()
    automation = base / '.automation'

    data = load_and_validate(args.article)
    slug = data['slug']

    image_path = base / 'images' / 'blog' / f'img-{slug}.jpg'
    if args.image is not None:
        if not args.image.is_file():
            raise PublicationError(f'illustration introuvable : {args.image}')
        image_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.image, image_path)
    if not image_path.is_file():
        raise PublicationError(
            f"l'illustration {image_path.relative_to(base)} n'existe pas. "
            f"Générer l'image d'abord (1600x900 JPEG), ou la passer via --image.")
    variants = generate_image_variants(image_path)
    print('--- variantes WebP\n' + '\n'.join(str(v.relative_to(base)) for v in variants))

    already = [p for conf in LANGS.values()
               if (p := base / conf['blog'] / f'{slug}.html').exists()]
    if already and not args.force:
        raise PublicationError(
            f'l\'article "{slug}" existe déjà ({len(already)} page(s)). '
            f'Utiliser --force pour le réécrire.')

    pages = render_pages(base, data)
    print(f'--- pages écrites\n' + '\n'.join(str(p.relative_to(base)) for p in pages))

    python = sys.executable
    run_step("blocs d'articles (lecture, partage, à lire aussi, précédent/suivant)",
             [python, str(automation / 'update_article_blocks.py'), '--base', str(base)])
    run_step('génération des index du blog (pagination)',
             [python, str(automation / 'generate_blog_indexes.py'), '--base', str(base)])
    run_step('synchronisation du carrousel',
             [python, str(automation / 'update_home_articles.py'), '--base', str(base)])
    run_step('génération du sitemap',
             [python, str(automation / 'generate_sitemap.py'), '--base', str(base)])
    run_step('génération des flux RSS',
             [python, str(automation / 'generate_feeds.py'), '--base', str(base)])
    run_step("contrôles d'intégrité",
             [python, str(automation / 'checks' / 'check_site.py'), '--base', str(base)])

    print(json.dumps({
        'slug': slug,
        'date': data['date_obj'].isoformat(),
        'links': {lang: data_url for lang, data_url in
                  ((lang, f'https://zamania.fr/{conf["blog"]}/{slug}.html')
                   for lang, conf in LANGS.items())},
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
