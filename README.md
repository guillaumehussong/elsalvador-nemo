# El Salvador Nemotron — 148k personas on a map

**[→ Carte live](https://elsalvador-nemo.guillaumehussong.workers.dev)** · [Code](https://github.com/guillaumehussong/elsalvador-nemo)

148 000 personas du dataset [NVIDIA Nemotron-Personas-El-Salvador](https://huggingface.co/datasets/nvidia/Nemotron-Personas-El-Salvador), géolocalisées sur une carte interactive d'El Salvador (deck.gl + MapLibre). Filtres par couleur (métier, âge, revenu), département, sexe, zone urbaine/rurale. Clic sur un point → profil synthétique.

![demo](docs/demo.gif)

Toolkit Python en local : échantillonnage Polars, focus group LLM (APIYI, optionnel).

## Licences & attributions

| Élément | Licence |
|---------|---------|
| Code | [MIT](LICENSE) |
| Personas Nemotron | [CC BY 4.0](https://huggingface.co/datasets/nvidia/Nemotron-Personas-El-Salvador) — NVIDIA / WideLabs |
| Frontières admin. | [CC BY 4.0](https://www.geoboundaries.org) — geoBoundaries / William & Mary |

## Quickstart (dev local)

Prérequis : [uv](https://docs.astral.sh/uv/), Node 20+.

```bash
git clone git@github.com:guillaumehussong/elsalvador-nemo.git
cd elsalvador-nemo

cp .env.example .env   # APIYI_API_KEY uniquement pour le focus group LLM

uv sync --extra stage2
uv run sv-preload
uv run python scripts/build_enriched_cache.py

# Carte
uv run sv-build-map
cd apps/map && npm ci && npm run build && npm run preview:host
# → http://localhost:4173

# Explorer des personas (CLI)
uv run sv-personas --department "San Salvador" --sample 3

# Focus group LLM (local, clé requise)
uv sync --extra stage1
uv run sv-focus-group -s "Votre stimulus" -n 8 --seed 42
```

Les fichiers `apps/map/public/data/*.bin` sont versionnés (~2,3 Mo) — pas besoin de regénérer la carte pour un clone simple.

## Déploiement carte (Cloudflare Workers)

Site 100 % statique, sans clé API.

| Champ | Valeur |
|-------|--------|
| Build command | `cd apps/map && npm ci && npm run build` |
| Deploy command | `npx wrangler deploy` |
| Root directory | *(vide — racine du repo)* |

`wrangler.toml` à la racine pointe vers `apps/map/dist`. Variable d'environnement recommandée : `NODE_VERSION=20`.

## Focus group web

**LOCAL ONLY** — ne pas exposer sans auth + rate-limit.

```bash
uv sync --extra focus-api --extra stage1
./scripts/serve_focus.sh   # http://127.0.0.1:8080
```
