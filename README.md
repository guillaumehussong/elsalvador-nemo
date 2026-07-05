# El Salvador Nemotron: 148k personas on a map

[Live map](https://elsalvador-nemo.guillaumehussong.workers.dev) | [Source](https://github.com/guillaumehussong/elsalvador-nemo)

148,000 personas from the [NVIDIA Nemotron-Personas-El-Salvador](https://huggingface.co/datasets/nvidia/Nemotron-Personas-El-Salvador) dataset, geolocated on an interactive map of El Salvador (deck.gl + MapLibre). Filter by color (occupation, age, income), department, sex, and urban/rural area. Click a point to see a synthetic profile.

![demo](docs/demo.gif)

Local Python toolkit: Polars sampling and optional LLM focus groups.

## Licenses and attribution

- **Code:** [MIT](LICENSE)
- **Nemotron personas:** [CC BY 4.0](https://huggingface.co/datasets/nvidia/Nemotron-Personas-El-Salvador) (NVIDIA / WideLabs)
- **Admin boundaries:** [CC BY 4.0](https://www.geoboundaries.org) (geoBoundaries / William & Mary)

## Quickstart (local dev)

Requirements: [uv](https://docs.astral.sh/uv/), Node 20+.

```bash
git clone git@github.com:guillaumehussong/elsalvador-nemo.git
cd elsalvador-nemo

cp .env.example .env   # see LLM configuration below for focus groups

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

## LLM configuration

The focus group uses an OpenAI-compatible chat endpoint. Any provider works by setting three variables in `.env`:

```
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=<provider endpoint>
LLM_MODEL=<model name>
```

Put the provider's API key in `OPENAI_API_KEY` (even when the provider uses a different env var name in their own docs).

| Provider | OPENAI_BASE_URL | Env key (set its value in OPENAI_API_KEY) | Example model |
|----------|-----------------|-------------------------------------------|---------------|
| OpenAI | https://api.openai.com/v1 | OPENAI_API_KEY | gpt-4.1-mini |
| Groq | https://api.groq.com/openai/v1 | GROQ_API_KEY | llama-3.3-70b-versatile |
| DeepSeek | https://api.deepseek.com | DEEPSEEK_API_KEY | deepseek-chat |
| xAI (Grok) | https://api.x.ai/v1 | XAI_API_KEY | grok-3-mini |
| OpenRouter | https://openrouter.ai/api/v1 | OPENROUTER_API_KEY | (any routed model) |

Personas reply in Salvadoran Spanish. Models with strong Spanish output (GPT, Claude via a compatible gateway) produce more natural verbatims than small English-first models. Groq only serves open-weight models (Llama, etc.), not GPT, Claude, or Gemini.

## Map deployment (Cloudflare Workers)

Fully static site, no API keys.

- **Build command:** `cd apps/map && npm ci && npm run build`
- **Deploy command:** `npx wrangler deploy`
- **Root directory:** empty (repo root)

Root `wrangler.toml` points to `apps/map/dist`. Recommended env var: `NODE_VERSION=20`.

Optional LLM focus group (local dev only): see [PLAN.md](PLAN.md).
