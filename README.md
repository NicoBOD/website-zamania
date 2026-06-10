# ZamanIA — [zamania.fr](https://zamania.fr)

[![CI](https://github.com/NicoBOD/website-zamania/actions/workflows/ci.yml/badge.svg)](https://github.com/NicoBOD/website-zamania/actions/workflows/ci.yml)
[![Audit hebdomadaire](https://github.com/NicoBOD/website-zamania/actions/workflows/weekly-audit.yml/badge.svg)](https://github.com/NicoBOD/website-zamania/actions/workflows/weekly-audit.yml)

Site vitrine de **ZamanIA**, solutions d'intelligence artificielle sur mesure pour TPE et PME : audit, automatisation, intégration et formation IA.

Le site est **100 % statique** (HTML/CSS/JS, sans framework ni étape de build), hébergé sur **GitHub Pages**, et disponible en **trois langues** :

| Langue | URL | Flux RSS | Particularités |
|---|---|---|---|
| 🇫🇷 Français | [zamania.fr](https://zamania.fr/) | [feed.xml](https://zamania.fr/feed.xml) | Version de référence, à la racine |
| 🇬🇧 Anglais | [zamania.fr/en/](https://zamania.fr/en/) | [en/feed.xml](https://zamania.fr/en/feed.xml) | |
| 🇸🇦 Arabe | [zamania.fr/ar/](https://zamania.fr/ar/) | [ar/feed.xml](https://zamania.fr/ar/feed.xml) | Sens de lecture RTL (`dir="rtl"` + `css/rtl.css`) |

Le blog est alimenté **automatiquement tous les 2 jours** par un agent IA (« Hermes ») qui propose des sujets, attend une validation humaine via Telegram, puis publie l'article dans les trois langues. Voir [Pipeline de publication](#-pipeline-de-publication-automatique-hermes).

---

## 📁 Structure du dépôt

```
.
├── index.html                  # Accueil FR (référence)
├── blog/
│   ├── index.html              # Liste des articles FR
│   ├── template.html           # Gabarit d'article FR (placeholders {{...}})
│   └── <slug>.html             # Articles publiés
├── en/                         # Miroir anglais (index.html + blog/ + feed.xml)
├── ar/                         # Miroir arabe RTL (index.html + blog/ + feed.xml)
├── css/
│   ├── styles.css              # Styles principaux (thème sombre par défaut)
│   ├── dark-mode.css           # Bascule clair/sombre
│   └── rtl.css                 # Surcharges RTL pour la version arabe
├── js/                         # Navigation, thème, carrousel, cookies, FAQ…
├── images/
│   └── blog/img-<slug>.jpg     # Une illustration par article (1600×900)
├── feed.xml                    # Flux RSS FR (généré — ne pas éditer)
├── sitemap.xml                 # Sitemap complet (généré — ne pas éditer)
├── 404.html, cgu.html, cgv.html, mentions-legales.html,
│   politique-de-confidentialite.html, charte-ia-ethique.html
├── CNAME, robots.txt, manifest.json, browserconfig.xml
├── .automation/                # Outillage du pipeline (non publié)
│   ├── publish.py                   # ⭐ Point d'entrée : publie un article (3 langues)
│   ├── article_index.py             # Bibliothèque : inventaire des articles publiés
│   ├── update_home_articles.py      # Synchro du carrousel d'accueil
│   ├── generate_sitemap.py          # Régénère sitemap.xml
│   ├── generate_feeds.py            # Régénère les 3 flux RSS
│   ├── zamania_topic_guard.py       # Garde-fou anti-doublons de sujets
│   ├── zamania-topic-memory.json    # Historique des sujets traités
│   ├── zamania-proposals-latest.json / zamania-selection.json
│   ├── examples/article.example.json # Format attendu par publish.py
│   └── checks/check_site.py         # Contrôles d'intégrité (CI)
└── .github/
    ├── workflows/ci.yml             # CI : intégrité du site
    ├── workflows/weekly-audit.yml   # Hebdo : liens externes + Lighthouse
    └── lighthouse/lighthouserc.json
```

> GitHub Pages (build Jekyll par défaut) **ne publie pas** les dossiers commençant par un point : `.automation/` et `.github/` restent privés au dépôt.

---

## 🤖 Pipeline de publication automatique (Hermes)

Un agent IA publie un article de blog **tous les 2 jours**, selon ce cycle :

1. **Proposition** — L'agent génère 3 sujets d'articles (`zamania-proposals-latest.json`) orientés B2B/ROI pour les décideurs de PME.
2. **Garde-fou** — `zamania_topic_guard.py` compare les propositions à la mémoire des sujets déjà traités (`zamania-topic-memory.json`) : similarité lexicale, thèmes récurrents, fenêtres récentes. Objectif : ne jamais republier deux fois le même angle.
3. **Validation humaine** — Les 3 sujets sont envoyés sur Telegram (message « 🗂️ Propositions ZamanIA du jour ») ; la réponse `1`, `2` ou `3` est consignée dans `zamania-selection.json`.
4. **Rédaction** — L'agent rédige l'article en FR/EN/AR dans **un fichier JSON** (format : [`examples/article.example.json`](.automation/examples/article.example.json)) et génère l'illustration `images/blog/img-<slug>.jpg` (1600×900).
5. **Publication** — Une seule commande fait tout le reste :

   ```bash
   python3 .automation/publish.py article.json
   ```

   Elle valide le contenu, rend les 3 pages depuis les templates, insère les cartes dans les 3 index, resynchronise le carrousel d'accueil, régénère `sitemap.xml` et les flux RSS, puis exécute les contrôles d'intégrité. Si quelque chose ne va pas, elle échoue **avant** tout commit.
6. **Déploiement** — Commit + push sur `main` → GitHub Pages met le site en ligne, et l'agent enregistre la publication dans la mémoire des sujets (`zamania_topic_guard.py record-publication`).

### Contrat de l'article (`article.json`)

```jsonc
{
  "slug": "mon-article",            // kebab-case ascii, sans accents
  "date": "2026-06-12",             // date de publication (ISO)
  "fr": {
    "title": "...",                 // sans guillemets doubles
    "description": "...",           // 150-160 caractères idéalement, sans guillemets doubles
    "content_html": "<h2 id=\"a\">…</h2><p>…</p>…"
  },
  "en": { ... }, "ar": { ... }      // mêmes champs, obligatoires
}
```

Règles appliquées par `publish.py` :

- chaque `<h2>` du contenu doit porter un `id` : le **sommaire est dérivé automatiquement** des `<h2 id="...">` (minimum 2 sections) ;
- l'illustration `images/blog/img-<slug>.jpg` doit exister avant la publication (ou être passée via `--image chemin.jpg`) ;
- republier un slug existant est refusé sans `--force` ;
- titres et descriptions sans guillemets doubles (ils alimentent des attributs HTML et le JSON-LD).

### Invariants du site (vérifiés par la CI)

- **Parité trilingue** : chaque article existe dans `blog/`, `en/blog/` **et** `ar/blog/` (même nom de fichier).
- **Placeholders** : aucun `{{TITLE}}`, `{{DATE}}`, `{{DATE_ISO}}`, `{{DESCRIPTION}}`, `{{SOMMAIRE}}`, `{{CONTENT}}`, `{{IMAGE_URL}}`, `{{SLUG}}` ne subsiste dans une page publiée (seuls les `template.html` en contiennent).
- **Marqueurs intacts** : les index de blog conservent exactement un couple `<!-- ARTICLES_LIST_START -->` / `<!-- ARTICLES_LIST_END -->` (articles triés du plus récent au plus ancien) ; les pages d'accueil conservent `<!-- HOME_ARTICLES_START -->` / `<!-- HOME_ARTICLES_END -->`.
- **Artefacts générés à jour** : carrousel d'accueil (5 derniers articles), `sitemap.xml` et flux RSS reflètent exactement l'état du blog — ils sont régénérés par `publish.py`, jamais édités à la main.
- **SEO des articles** : chaque article porte canonical, hreflang FR/EN/AR, Open Graph, Twitter Card et un JSON-LD `Article` valide (le tout rempli par les templates).
- **Liens valides** : tout `href`/`src` local (y compris les URL absolues `https://zamania.fr/...` et les ancres `#section`) pointe vers un fichier/id existant.

---

## 🧪 Intégration continue

**[`ci.yml`](.github/workflows/ci.yml)** s'exécute à chaque push sur `main`, sur chaque pull request, et manuellement. Il lance les contrôles d'intégrité :

```bash
# La même commande, en local (Python ≥ 3.10, aucune dépendance) :
python3 .automation/checks/check_site.py
```

| Contrôle | Ce qui casserait sans lui |
|---|---|
| Fichiers requis & encodage UTF-8 | Page ou ressource supprimée par erreur |
| Parité trilingue FR/EN/AR | Article publié dans une seule langue |
| Placeholders `{{...}}` | Gabarit mal rempli visible en production |
| Marqueurs du pipeline | Prochaine publication automatique impossible |
| Liens, ancres, images, CSS `url()` | Liens morts, images cassées |
| Cartes des index de blog | Article publié mais absent de la liste |
| Artefacts générés (carrousel, sitemap, RSS) | Accueil/SEO/flux en retard sur le blog |
| Attributs HTML (lang, RTL, title, description, h1) | Régressions SEO/accessibilité |
| SEO des articles (canonical, OG, JSON-LD) | Partages sociaux et indexation dégradés |
| `sitemap.xml`, flux RSS, `robots.txt`, `CNAME` | Désindexation, domaine cassé |
| Icônes PWA (`manifest.json`, `browserconfig.xml`) | Manifest invalide |
| Compilation des scripts Python | Pipeline de publication cassé |

**[`weekly-audit.yml`](.github/workflows/weekly-audit.yml)** tourne tous les lundis (et à la demande), sans bloquer quoi que ce soit :

- **lychee** vérifie que les liens externes répondent encore ;
- **Lighthouse** audite performance, SEO et accessibilité des pages principales (rapports en artefacts du workflow).

---

## 🛠️ Développement local

Aucune installation requise — un serveur statique suffit (nécessaire car certaines pages utilisent des chemins absolus `/css/...`, `/images/...`) :

```bash
python3 -m http.server 8000
# puis ouvrir http://localhost:8000
```

À vérifier avant de pousser une modification visuelle :

- les 3 langues (`/`, `/en/`, `/ar/` — y compris le rendu RTL) ;
- les deux thèmes (bouton 🌙 dans la barre de navigation) ;
- l'affichage mobile (menu hamburger).

---

## 🚀 Déploiement

- **Hébergement** : GitHub Pages, branche `main` (racine).
- **Domaine** : `zamania.fr` via le fichier [`CNAME`](CNAME).
- **Mise en ligne** : automatique à chaque push sur `main` (une à deux minutes de délai).

Il n'y a **aucune étape de build** : ce qui est commité est ce qui est servi. Les fichiers générés (`sitemap.xml`, `feed.xml`, carrousel des accueils) sont commités avec le reste — la CI vérifie qu'ils sont à jour.

---

## 📬 Contact

ZamanIA — [contact@zamania.fr](mailto:contact@zamania.fr) · © 2026 ZamanIA. Tous droits réservés.
