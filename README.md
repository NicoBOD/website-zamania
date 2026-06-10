# ZamanIA — [zamania.fr](https://zamania.fr)

[![CI](https://github.com/NicoBOD/website-zamania/actions/workflows/ci.yml/badge.svg)](https://github.com/NicoBOD/website-zamania/actions/workflows/ci.yml)

Site vitrine de **ZamanIA**, solutions d'intelligence artificielle sur mesure pour TPE et PME : audit, automatisation, intégration et formation IA.

Le site est **100 % statique** (HTML/CSS/JS, sans framework ni étape de build), hébergé sur **GitHub Pages**, et disponible en **trois langues** :

| Langue | URL | Particularités |
|---|---|---|
| 🇫🇷 Français | [zamania.fr](https://zamania.fr/) | Version de référence, à la racine |
| 🇬🇧 Anglais | [zamania.fr/en/](https://zamania.fr/en/) | |
| 🇸🇦 Arabe | [zamania.fr/ar/](https://zamania.fr/ar/) | Sens de lecture RTL (`dir="rtl"` + `css/rtl.css`) |

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
├── en/                         # Miroir anglais (index.html + blog/)
├── ar/                         # Miroir arabe RTL (index.html + blog/)
├── css/
│   ├── styles.css              # Styles principaux (thème sombre par défaut)
│   ├── dark-mode.css           # Bascule clair/sombre
│   └── rtl.css                 # Surcharges RTL pour la version arabe
├── js/                         # Navigation, thème, carrousel, cookies, FAQ…
├── images/
│   └── blog/img-<slug>.jpg     # Une illustration par article (1600×900)
├── 404.html, cgu.html, cgv.html, mentions-legales.html,
│   politique-de-confidentialite.html, charte-ia-ethique.html
├── CNAME, robots.txt, sitemap.xml, manifest.json, browserconfig.xml
├── .automation/                # Outillage de l'agent Hermes (non publié)
│   ├── publish_zamania_article.py   # Publication trilingue d'un article
│   ├── update_home_articles.py      # Synchro du carrousel d'accueil
│   ├── zamania_topic_guard.py       # Garde-fou anti-doublons de sujets
│   ├── run_record.py                # Enregistre une publication dans la mémoire
│   ├── zamania-topic-memory.json    # Historique des sujets traités
│   ├── zamania-proposals-latest.json / zamania-selection.json
│   └── checks/check_site.py         # Contrôles d'intégrité (CI)
└── .github/workflows/ci.yml    # Intégration continue
```

> GitHub Pages (build Jekyll par défaut) **ne publie pas** les dossiers commençant par un point : `.automation/` et `.github/` restent privés au dépôt.

---

## 🤖 Pipeline de publication automatique (Hermes)

Un agent IA publie un article de blog **tous les 2 jours**, selon ce cycle :

1. **Proposition** — L'agent génère 3 sujets d'articles (`zamania-proposals-latest.json`) orientés B2B/ROI pour les décideurs de PME.
2. **Garde-fou** — `zamania_topic_guard.py` compare les propositions à la mémoire des sujets déjà traités (`zamania-topic-memory.json`) : similarité lexicale, thèmes récurrents, fenêtres récentes. Objectif : ne jamais republier deux fois le même angle.
3. **Validation humaine** — Les 3 sujets sont envoyés sur Telegram (message « 🗂️ Propositions ZamanIA du jour ») ; la réponse `1`, `2` ou `3` est consignée dans `zamania-selection.json`.
4. **Publication trilingue** — Le contenu est rédigé en FR/EN/AR, rendu via les gabarits `blog/template.html` (et équivalents `en/`, `ar/`), avec une illustration dédiée.
5. **Propagation** — Cartes ajoutées aux 3 index de blog, carrousel des pages d'accueil resynchronisé, publication enregistrée dans la mémoire des sujets.
6. **Déploiement** — Commit + push sur `main` → GitHub Pages met le site en ligne.

### Contrat de publication (invariants vérifiés par la CI)

Toute publication doit respecter ces règles — c'est exactement ce que `check_site.py` vérifie :

- **Parité trilingue** : chaque article existe dans `blog/`, `en/blog/` **et** `ar/blog/` (même nom de fichier).
- **Placeholders** : aucun `{{TITLE}}`, `{{DATE}}`, `{{DESCRIPTION}}`, `{{SOMMAIRE}}`, `{{CONTENT}}`, `{{IMAGE_URL}}` ne subsiste dans une page publiée (seuls les `template.html` en contiennent).
- **Marqueurs intacts** : les index de blog conservent exactement un couple
  `<!-- ARTICLES_LIST_START -->` / `<!-- ARTICLES_LIST_END -->` (la carte du nouvel article s'insère juste après le marqueur de début, donc les articles sont triés du plus récent au plus ancien) ; les pages d'accueil conservent `<!-- HOME_ARTICLES_START -->` / `<!-- HOME_ARTICLES_END -->`.
- **Illustration** : `images/blog/img-<slug>.jpg` existe et est référencée par l'article et sa carte.
- **Carrousel synchronisé** : après publication, exécuter

  ```bash
  python3 .automation/update_home_articles.py
  ```

  pour répercuter les 5 derniers articles sur les 3 pages d'accueil (script idempotent).
- **Liens valides** : tout `href`/`src` local (y compris les URL absolues `https://zamania.fr/...` et les ancres `#section`) pointe vers un fichier/id existant.
- **HTML minimal** : `lang` correct (`fr`/`en`/`ar`), `dir="rtl"` sur les pages arabes, `<title>`, meta description, un seul `<h1>` par article.

Avant tout commit, l'agent (ou un humain) lance :

```bash
python3 .automation/checks/check_site.py
```

et ne pousse que si tous les contrôles sont au vert.

---

## 🧪 Intégration continue

Le workflow [`ci.yml`](.github/workflows/ci.yml) s'exécute à chaque push sur `main`, sur chaque pull request, et manuellement (`workflow_dispatch`). Il lance `check_site.py`, qui couvre :

| Contrôle | Ce qui casserait sans lui |
|---|---|
| Fichiers requis & encodage UTF-8 | Page ou ressource supprimée par erreur |
| Parité trilingue FR/EN/AR | Article publié dans une seule langue |
| Placeholders `{{...}}` | Gabarit mal rempli visible en production |
| Marqueurs du pipeline | Prochaine publication automatique impossible |
| Liens, ancres, images, CSS `url()` | Liens morts, images cassées |
| Cartes des index de blog | Article publié mais absent de la liste |
| Synchro du carrousel d'accueil | Accueil en retard sur le blog (bug déjà rencontré) |
| Attributs HTML (lang, RTL, title, description, h1) | Régressions SEO/accessibilité |
| `sitemap.xml`, `robots.txt`, `CNAME` | Désindexation, domaine cassé |
| Icônes PWA (`manifest.json`, `browserconfig.xml`) | Manifest invalide |
| Compilation des scripts Python | Pipeline de publication cassé |

Aucune dépendance : la bibliothèque standard Python ≥ 3.10 suffit.

```bash
# En local, depuis la racine du dépôt :
python3 .automation/checks/check_site.py

# Tester une copie de travail :
python3 .automation/checks/check_site.py --base /chemin/vers/copie
```

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

Il n'y a **aucune étape de build** : ce qui est commité est ce qui est servi.

### Scripts historiques

`generate_post.py` et `build.py` (à la racine) sont des scripts de publication ponctuels d'anciens articles, conservés pour mémoire ; ils contiennent des chemins absolus propres à l'environnement de l'agent et ne doivent pas être réexécutés tels quels. L'outillage actif vit dans `.automation/`.

---

## 📬 Contact

ZamanIA — [contact@zamania.fr](mailto:contact@zamania.fr) · © 2026 ZamanIA. Tous droits réservés.
