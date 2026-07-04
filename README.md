# Salvador Personas

148 000 personas Nemotron géolocalisées sur une carte interactive d'El Salvador — focus group LLM en local.

![demo](docs/demo.gif)

## Licences & attributions

- **Code** : [MIT](LICENSE)
- **Données personas** : [NVIDIA Nemotron-Personas-El-Salvador](https://huggingface.co/datasets/nvidia/Nemotron-Personas-El-Salvador) (CC BY 4.0) — NVIDIA / WideLabs
- **Frontières administratives** : [geoBoundaries](https://www.geoboundaries.org) (CC BY 4.0) — William & Mary

## Quickstart

Prérequis : [uv](https://docs.astral.sh/uv/), Node 20+ (carte).

```bash
# 1. Config
cp .env.example .env   # puis APIYI_API_KEY dans .env (local uniquement)

# 2. Dataset + cache
uv sync --extra stage2
uv run sv-preload
uv run python scripts/build_enriched_cache.py

# 3. Explorer personas (CLI)
uv run sv-personas --department "San Salvador" --sample 3

# 4. Focus group (CLI, clé locale)
uv sync --extra stage1
uv run sv-focus-group -s "Votre stimulus" -n 8 --seed 42

# 5. Carte interactive
uv run sv-build-map
cd apps/map && npm install && npm run build
npm run preview:host   # → http://localhost:4173
```

## Déploiement carte (statique uniquement)

La carte (`apps/map/dist/`) est **100 % statique** — pas de clé API, pas de backend.

### Cloudflare Pages

| Champ | Valeur |
|-------|--------|
| Build command | `cd apps/map && npm ci && npm run build` |
| Build output directory | `apps/map/dist` |
| Root directory | `/` (repo root) |

Prérequis CI : lancer `uv run sv-build-map` avant le build npm (ou committer `apps/map/public/data/*.bin`).

```bash
# Build local complet avant upload manuel
uv run sv-build-map && cd apps/map && npm ci && npm run build
npx wrangler pages deploy dist --project-name salvador-personas-map
```

### GitHub Pages (project site)

Si l'URL est `https://<user>.github.io/salvador-personas/` :

1. Dans `apps/map/vite.config.ts`, ajouter `base: '/salvador-personas/'`
2. Rebuild : `npm run build`
3. GitHub Actions (`.github/workflows/pages.yml`) :

```yaml
name: Deploy map
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: uv sync --extra stage2 && uv run sv-build-map
      - run: cd apps/map && npm ci && npm run build
        env:
          # décommenter si base GitHub Pages :
          # VITE_BASE: /salvador-personas/
      - uses: actions/upload-pages-artifact@v3
        with:
          path: apps/map/dist
      - uses: actions/deploy-pages@v4
```

## Focus group web (LOCAL ONLY)

```bash
uv sync --extra focus-api --extra stage2
./scripts/serve_focus.sh   # http://127.0.0.1:8080
```

Ne pas exposer publiquement sans auth + rate-limit — la clé APIYI reste côté serveur.
