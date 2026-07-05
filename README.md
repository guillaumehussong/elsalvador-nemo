# El Salvador Nemotron: 148k personas on a map

[Live map](https://elsalvador-nemo.guillaumehussong.workers.dev) | [Source](https://github.com/guillaumehussong/elsalvador-nemo)

148,000 personas from the [NVIDIA Nemotron-Personas-El-Salvador](https://huggingface.co/datasets/nvidia/Nemotron-Personas-El-Salvador) dataset, geolocated on an interactive map of El Salvador (deck.gl + MapLibre). Filter by color (occupation, age, income), department, sex, and urban/rural area. Click a point to see a synthetic profile.

![demo](docs/demo.gif)

Local Python toolkit: Polars sampling and optional LLM focus groups (APIYI).

## Licenses and attribution

- **Code:** [MIT](LICENSE)
- **Nemotron personas:** [CC BY 4.0](https://huggingface.co/datasets/nvidia/Nemotron-Personas-El-Salvador) (NVIDIA / WideLabs)
- **Admin boundaries:** [CC BY 4.0](https://www.geoboundaries.org) (geoBoundaries / William & Mary)

## Quickstart (local dev)

Requirements: [uv](https://docs.astral.sh/uv/), Node 20+.

```bash
git clone git@github.com:guillaumehussong/elsalvador-nemo.git
cd elsalvador-nemo

cp .env.example .env   # APIYI_API_KEY only needed for LLM focus groups

uv sync --extra stage2
uv run sv-preload
uv run python scripts/build_enriched_cache.py

# Map
uv run sv-build-map
cd apps/map && npm ci && npm run build && npm run preview:host
# http://localhost:4173

# Explore personas (CLI)
uv run sv-personas --department "San Salvador" --sample 3

# LLM focus group (local, API key required)
uv sync --extra stage1
uv run sv-focus-group -s "Your stimulus" -n 8 --seed 42
```

Map bundle files `apps/map/public/data/*.bin` are committed (~2.3 MB). A simple clone does not require regenerating the map.

## Map deployment (Cloudflare Workers)

Fully static site, no API keys.

- **Build command:** `cd apps/map && npm ci && npm run build`
- **Deploy command:** `npx wrangler deploy`
- **Root directory:** empty (repo root)

Root `wrangler.toml` points to `apps/map/dist`. Recommended env var: `NODE_VERSION=20`.

Optional LLM focus group (local dev only): see [PLAN.md](PLAN.md).
