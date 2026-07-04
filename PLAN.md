# PLAN — Salvador Personas Toolkit

> Mono-repo Python local-first. Dataset : `nvidia/Nemotron-Personas-El-Salvador` (CC BY 4.0).  
> Ordre de construction imposé : **Stage 0 → Stage 1 → Stage 2**.

---

## Décisions validées (Q1–Q10 — ne pas rediscuter)

| # | Décision |
|---|----------|
| Q1 | Repo : **`salvador-personas`** |
| Q2 | LLM : agrégateur **APIYI** — smoke test curl avant d'écrire le client ; `LLMClient` Protocol absorbe OpenAI-compat ou Anthropic-compat selon résultat |
| Q3 | Stage 1 : hooks publicitaires **B2C locaux** (marketplace auto, services). Prompts : réaction d'achat, sensibilité prix, objections. Métriques : `interest_score` 1–10 + top objections. Modèle **cheap** obligatoire |
| Q4 | Stage 2 : **carte publique** 148k personas géolocalisées (Artefact A) ; sim économique abandonnée |
| Q5 | Focus group : **N=8** défaut, confirmation coût si **N>15**, plafond dur **N=25** |
| Q6 | Langues : prompts + réponses personas en **espagnol** ; UI / CLI / docs en **français** |
| Q7 | Backstory **compacte** : `persona` + `professional_persona` + `cultural_background` uniquement. Exclure `sports/arts/travel_persona`. `*_list` dans `narratives`, jamais dans backstory |
| Q8 | Revenu : **USD/mois**, fiction réglable YAML. **Aucune mention EHPM** dans code ou UI. Sanity-check : salaire minimum commerce/services (~**$365/mois**) dans la plage plausible des profils formels urbains |
| Q9 | Géo Stage 2 : **national** (148k) si bundle data < 5 Mo ; frontières **geoBoundaries** CC BY 4.0 |
| Q10 | Persistance : **JSON/Parquet par run**. Pas de SQLite |

### Hypothèses techniques restantes

| # | Hypothèse |
|---|-----------|
| H1 | `row_count` lu au runtime via `len(ds)` / `build_meta.json` — jamais hardcodé |
| H2 | Colonnes HF incluent `sports_persona`, `arts_persona`, `travel_persona`, `country` (exclus de backstory) |
| H3 | Pas de noms dans le dataset ; labels synthétiques en Stage 1 (« Persona A »…) |
| H5 | Gestion env via **uv** |
| H6 | **Polars** + Parquet enrichi |
| H10 | CPU only |
| H12 | Attribution CC BY 4.0 dans README + footer Streamlit |

### Exclusions explicites

- **Kie.ai** : provider média (image/vidéo async), pas LLM. Aucun stage. Pas dans `.env` ni le code.
- **SQLite**, auth, microservices, EHPM comme source de defaults.

---

## Ajustements plan (A–F)

| ID | Ajustement |
|----|------------|
| **A** | Supprimer toute estimation de taille disque contradictoire. `preload_dataset.py` mesure `row_count`, tailles réelles (HF cache, parquet brut/enrichi) au runtime → `build_meta.json`. Aucun garde-fou basé sur une taille supposée |
| **B** | Courbes d'âge (revenu **et** adoption) : gaussienne normalisée `factor(age) = floor + (1 - floor) × exp(-((age - peak)² / (2 × width²)))`. Defaults : `floor=0.6` (revenu), `floor=0.3` (adoption). Pas d'autre forme sans décision explicite |
| **C** | Review **119 occupations** → `occupation_roles.yaml` : **1 h budgetée, AVANT Stage 2** (pas pendant le weekend sim) |
| **D** | **Stage 0 = scope réduit d'office** : backstory compacte, tags digital = liste mots-clés simple, **3 tests pytest** (loader, filtre, seed). CLI `sv-personas` **conservé** |
| **E** | Stage 2 : **Mesa OU Polars vectorisé** — deux chemins **équivalents**. Décision au moment T selon le temps restant ; pas de dette anticipée |
| **F** | Kie.ai exclu (cf. ci-dessus) |

---

## 1. Arborescence mono-repo

```
salvador-personas/
├── PLAN.md
├── pyproject.toml
├── .env.example
├── .gitignore
│
├── config/
│   ├── derived_fields.yaml
│   ├── occupation_roles.yaml      # ★ review 1 h avant Stage 2
│   ├── narrative_tags.yaml
│   └── sim_product.yaml           # défaut : service digital $10/mois
│
├── data/                          # gitignored
│   ├── hf/                        # HF_HOME
│   ├── processed/
│   │   ├── personas_enriched.parquet
│   │   └── build_meta.json        # row_count, tailles mesurées, hashes config
│   └── runs/                      # JSON/Parquet par focus group / sim
│
├── scripts/
│   ├── preload_dataset.py
│   ├── build_enriched_cache.py
│   ├── smoke_test_llm.sh          # curl APIYI → choix client
│   └── export_occupations.py      # liste 119 occ. pour review YAML
│
├── src/salvador_personas/
│   ├── __init__.py
│   ├── models/
│   │   └── persona.py
│   ├── dataset/
│   │   ├── loader.py
│   │   ├── cache.py
│   │   ├── enrich.py
│   │   └── filters.py
│   ├── stage0/
│   │   └── generator.py
│   ├── stage1/
│   │   ├── llm/
│   │   │   ├── base.py            # Protocol LLMClient
│   │   │   ├── factory.py         # sélection client depuis .env + smoke result
│   │   │   ├── openai_compat.py
│   │   │   └── anthropic_compat.py
│   │   ├── prompts.py             # system prompt B2C, espagnol
│   │   ├── focus_group.py
│   │   ├── aggregate.py
│   │   └── cli.py                 # UI messages en français
│   └── stage2/
│       ├── derived.py
│       ├── economy.py
│       ├── sim_polars.py          # chemin A : vectorisé
│       ├── sim_mesa/              # chemin B : optionnel
│       │   ├── agents.py
│       │   └── model.py
│       └── metrics.py
│
├── apps/
│   ├── focus_group_app.py         # UI français
│   └── city_sim_app.py
│
└── tests/
    ├── test_loader.py
    ├── test_stage0_filter.py
    └── test_stage0_seed.py
```

**Entrypoints**

| Commande | Stage | Rôle |
|----------|-------|------|
| `sv-preload` | 0 | Télécharge dataset, mesure meta, build cache enrichi |
| `sv-personas` | 0 | CLI sample/filter (français) |
| `sv-smoke-llm` | 1 | Smoke test APIYI → écrit `LLM_CLIENT=openai\|anthropic` dans meta local |
| `sv-focus-group` | 1 | CLI focus group B2C |
| `sv-focus-app` | 1 | Streamlit focus group |
| `sv-city-sim` | 2 | Sim headless (Polars ou Mesa) |
| `sv-city-app` | 2 | Dashboard San Salvador |

---

## 2. Dépendances par stage

### Core

| Package | Usage |
|---------|-------|
| `datasets` | Chargement HF |
| `polars` | Filtres, sample, sim vectorisée Stage 2 |
| `pyarrow` | Parquet |
| `pydantic` | Modèles + validation réponses LLM |
| `pyyaml` | Config tunables |
| `python-dotenv` | `.env` |

### Stage 1 (`stage1`)

| Package | Usage |
|---------|-------|
| `openai` | Client OpenAI-compat (APIYI path A) |
| `httpx` | Client Anthropic-compat (APIYI path B) |
| `streamlit` | UI |
| `rich` | CLI français, estimateur coût |
| `tenacity` | Retry API |

### Stage 2 (`stage2`)

| Package | Usage |
|---------|-------|
| `mesa` | **Optionnel** — chemin B agent-based |
| `streamlit` | Dashboard |
| `plotly` ou `altair` | Graphiques |

Polars (core) suffit pour le chemin A ; Mesa installé seulement si chemin B choisi.

### Dev

| Package | Usage |
|---------|-------|
| `pytest` | 3 tests Stage 0 + tests dérivés Stage 2 |
| `ruff` | Lint |

---

## 3. Stratégie chargement + cache dataset

### Flux

```
HF load_dataset ──► build_meta.json (mesures runtime)
        │
        └──► build_enriched_cache ──► personas_enriched.parquet
                                              │
                         Stage 0 / 1 / 2 ◄────┘
```

### `preload_dataset.py`

- `load_dataset("nvidia/Nemotron-Personas-El-Salvador", split="train")`
- Mesure et écrit dans `build_meta.json` :
  - `row_count` (runtime)
  - `columns`
  - `hf_cache_bytes` (taille réelle du cache HF sous `data/hf/`)
  - `dataset_id`, `built_at`
- **Aucune estimation hardcodée** ; pas de garde-fou disque basé sur une taille supposée

### `build_enriched_cache.py`

- Parse narratifs **1×** : tags digital (liste mots-clés), champs dérivés Stage 2
- Écrit `personas_enriched.parquet`
- Met à jour `build_meta.json` : `enriched_bytes`, `schema_version`, hashes des YAML config

### Runtime

- `PersonaGenerator` lit uniquement le parquet enrichi
- Filtres Polars lazy scan
- Invalidation : changement dataset HF ou hash YAML (`derived_fields`, `occupation_roles`, `narrative_tags`)

### Cache HF

- `HF_HOME=data/hf` (`.env.example`)

---

## 4. Stages — scope, done, scope réduit

### Stage 0 — Générateur (½ journée) — **scope réduit d'office (D)**

**Scope**

- `PersonaGenerator` : filtres + `sample(n)` + `get(uuid)`
- Backstory compacte (Q7) — **sans** `family_persona`
- Tags digital : matching mots-clés simple dans `narrative_tags.yaml` (extensible plus tard)
- Champs dérivés pré-calculés dans parquet (pour Stage 2)
- CLI `sv-personas` (messages français)
- **3 tests pytest** : loader (`row_count > 0`), filtre department, reproductibilité seed

**Assemblage backstory (validé)**

```
{persona}

Contexto profesional: {professional_persona}
Antecedentes culturales: {cultural_background}
```

**Done =**

- [ ] `sv-preload` + enrich passent ; `build_meta.json` contient `row_count` + tailles mesurées
- [ ] `PersonaGenerator.sample(10)` fonctionnel
- [ ] Filtres department / municipality / occupation / age OK
- [ ] Aucun appel LLM
- [ ] 3 tests pytest verts

**Scope réduit si dépassement**

- Drop enrich pré-calculé Stage 2 du cache Stage 0 (dériver seulement au build Stage 2)
- Tags digital = 5 mots-clés inline sans YAML

---

### Stage 1 — Focus group B2C (1 soirée)

**Prérequis** : `scripts/smoke_test_llm.sh` exécuté → choix client documenté dans `.env`

**Smoke test APIYI (avant tout client Python)**

```bash
curl https://api.apiyi.com/v1/chat/completions \
  -H "Authorization: Bearer $APIYI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-haiku-4-5-20251001","messages":[{"role":"user","content":"ping"}],"max_tokens":10}'
```

| Résultat | Client | Variables `.env` |
|----------|--------|----------------|
| HTTP 200 | `OpenAICompatClient` | `OPENAI_API_KEY`, `OPENAI_BASE_URL=https://api.apiyi.com/v1`, `LLM_MODEL=claude-haiku-4-5-20251001` |
| Échec | `AnthropicCompatClient` | `ANTHROPIC_API_KEY`, `ANTHROPIC_BASE_URL=https://api.apiyi.com`, endpoint `/v1/messages`, `LLM_MODEL=claude-haiku-4-5-20251001` |

Le Protocol `LLMClient` masque l'implémentation. **Aucun provider hardcodé.**

**Scope**

- Entrée : `PersonaGenerator.sample(N)` + stimulus (hook pub / prix / landing)
- System prompt espagnol : réaction d'achat B2C locale, sensibilité prix, objections
- 1 appel LLM/persona → JSON : `sentiment`, `objections[]`, `verbatim`, `interest_score` 1–10
- Agrégation : moyenne score, top objections, verbatims
- Garde-fous : N défaut 8 ; confirmation si **N>15** ; refus si **N>25**
- Estimateur coût avant run (modèle cheap Haiku)
- Sortie : `data/runs/focus_<timestamp>.json`
- CLI français + Streamlit français

**Done =**

- [ ] Smoke test passé ; client sélectionné via factory
- [ ] 8 personas, réponses JSON parseables (1 retry si malformed)
- [ ] Coût estimé affiché ; confirmation N>15
- [ ] Streamlit affiche agrégat + verbatims

**Scope réduit si dépassement**

- CLI seulement (pas Streamlit)
- Réponse texte libre + extraction regex (pas JSON mode)

---

### Stage 2 — Carte publique 148k personas (1 weekend)

**Pivot** : abandon sim Mesa/Polars. Livrables :

| Priorité | Artefact | Description |
|----------|----------|-------------|
| **A** | `apps/map/` | Carte deck.gl + MapLibre, build statique Vite, partageable |
| **B** (optionnel) | FastAPI + front minimal | Wrap `sv-focus-group` ; clé LLM côté serveur uniquement |

**Prérequis** : `config/occupation_groups.yaml` (8 catégories couleur carte)

**Pipeline géo**

- Frontières : **geoBoundaries** (William & Mary, CC BY 4.0) — ADM2 El Salvador
- Cache : `data/geo/geoboundaries_slv_adm2.geojson`
- Script : `scripts/build_geoboundaries_map.py` ; entrypoint `sv-build-map`
- Correspondance `municipality` (dataset, 44 zones post-censales) → polygones geoBoundaries (nom + fuzzy accents/casse) ; log `unmatched` au build
- Placement : seed déterministe `md5(uuid) % 2**32` ; triangulation Shapely (pas de rejection sampling)
- Export : `apps/map/public/data/points.bin`, `attrs.bin`, `manifest.json`
- **Défaut vue** : benchmark bundle — si `< 5 Mo` → national (148k) ; sinon San Salvador + toggle national  
  *(mesuré : ~2,3 Mo → défaut « Todo El Salvador »)*

**Front carte (esthétique = livrable)**

- Basemap sombre (Carto dark-matter)
- Palette contrastée occupation / âge / revenu
- Animation reveal ~2,8 s ; filtres département, sexe, área
- Toggle zoom San Salvador ↔ national
- Footer **double attribution CC BY 4.0** :
  - Personas : [NVIDIA / WideLabs — HF dataset](https://huggingface.co/datasets/nvidia/Nemotron-Personas-El-Salvador)
  - Frontières : [geoBoundaries](https://www.geoboundaries.org) (William & Mary)

**Done =**

- [x] `sv-build-map` → 148k points, bundle < 5 Mo
- [x] App Vite build OK (`npm run build`)
- [ ] Démo fluide 148k (reveal + filtres)
- [ ] Artefact B si temps restant

**Scope réduit si dépassement**

- Drop Artefact B
- Filtres réduits (département + couleur occupation seulement)

---

## 5. Contrat Stage 0

```python
# src/salvador_personas/models/persona.py

from dataclasses import dataclass
from typing import Literal

EconomicRole = Literal["merchant", "consumer", "both", "inactive"]

@dataclass(frozen=True)
class ParsedTags:
    digital_score: float
    consumption_tags: tuple[str, ...]

@dataclass(frozen=True)
class DerivedFields:
    income_usd_monthly: float
    economic_role: EconomicRole
    adoption_propensity: float

@dataclass(frozen=True)
class PersonaFilter:
    departments: tuple[str, ...] | None = None
    municipalities: tuple[str, ...] | None = None
    occupations: tuple[str, ...] | None = None
    age_min: int | None = None
    age_max: int | None = None
    area: Literal["urbano", "rural"] | None = None
    sex: Literal["Female", "Male"] | None = None

@dataclass(frozen=True)
class Persona:
    uuid: str
    sex: str
    age: int
    marital_status: str
    household_type: str
    education_level: str
    occupation: str
    area: str
    municipality: str
    department: str
    languages_spoken: str
    narratives: dict[str, str]
    backstory: str                  # compacte Q7
    tags: ParsedTags
    derived: DerivedFields

class PersonaGenerator:
    def __init__(self, data_dir: str | None = None) -> None: ...

    @property
    def row_count(self) -> int: ...  # depuis build_meta.json

    def filter(self, f: PersonaFilter) -> "PersonaGenerator": ...
    def sample(self, n: int, *, seed: int | None = None) -> list[Persona]: ...
    def get(self, uuid: str) -> Persona | None: ...
    def count_filtered(self) -> int: ...
```

---

## 6. Trois champs dérivés Stage 2

> Calculés 1× dans `build_enriched_cache.py`. Recalcul = rebuild cache. Jamais en runtime sim.

### Courbe d'âge commune (B)

```
age_factor(age) = floor + (1 - floor) × exp(-((age - peak)² / (2 × width²)))
```

| Usage | floor | peak | width |
|-------|-------|------|-------|
| Revenu | 0.6 | 45 | 15 |
| Adoption (composante âge) | 0.3 | 32 | 12 |

### (a) Revenu — `income_usd_monthly`

**Fichier** : `config/derived_fields.yaml`

```yaml
income:
  base_by_education:
    ninguno: 180
    primaria: 250
    secundaria: 320
    bachillerato: 420
    tecnico: 550
    universitario: 780
    posgrado: 1100
  occupation_multipliers:
    default: 1.0
    overrides: {}
  area_multiplier:
    urbano: 1.12
    rural: 0.88
  age_curve:
    peak: 45
    width: 15
    floor: 0.6
  noise_std: 0.08
```

```
income = base[education] × occ_mult × area_mult × age_factor(age) × (1 + noise)
```

**Sanity-check (Q8)** : après tuning defaults, un profil `bachillerato` + `urbano` + occupation formelle standard doit pouvoir atteindre **~$365/mois** (salaire minimum commerce/services). Fiction réglable — **aucune référence EHPM** dans code/UI.

### (b) Rôle — `economic_role`

**Fichier** : `config/occupation_roles.yaml` — review **1 h avant Stage 2**

```yaml
patterns:
  merchant: ["Comercio*", "Venta*", "Restaurantes*"]
  inactive: ["*doméstico*", "*familiar no remunerado*"]
defaults:
  unmatched: consumer
overrides: {}
```

Workflow : `export_occupations.py` → liste 119 → review manuelle → overrides.

### (c) Adoption — `adoption_propensity`

```yaml
adoption:
  weights:
    digital_score: 0.35
    education: 0.25
    age: 0.20
    area: 0.20
  education_score:
    ninguno: 0.15
    primaria: 0.25
    secundaria: 0.35
    bachillerato: 0.45
    tecnico: 0.60
    universitario: 0.75
    posgrado: 0.90
  age_curve:
    peak: 32
    width: 12
    floor: 0.3
  area_score:
    urbano: 0.65
    rural: 0.40
  clamp: [0.05, 0.95]
```

```
adoption = clamp(w_d × digital + w_e × edu + w_a × age_factor(age) + w_r × area)
```

`digital_score` : mots-clés simples dans hobbies (narrative + `_list`), score = matches / max(3, len(keywords)).

### Produit simulé — `config/sim_product.yaml`

```yaml
name: "Servicio digital"
description: "Suscripción mensual genérica"
price_usd_monthly: 10
price_elasticity: 0.5        # sensibilité dans f(prix)
channel: digital
```

---

## 7. Risques

| Risque | Mitigation |
|--------|------------|
| APIYI format inconnu jusqu'au smoke test | `smoke_test_llm.sh` + factory avant Stage 1 |
| 119 occupations mal classées | Review 1 h dédiée avant Stage 2 ; YAML overrides |
| Revenu fiction déconnectée du réel | Documenté tunable ; sanity $365 ; pas de claim statistique |
| Coût LLM N appels | Haiku cheap ; N≤25 ; confirm N>15 |
| JSON LLM malformed | Retry + pydantic ; fallback regex en scope réduit |
| Mesa vs temps weekend | Scope réduit : Artefact B abandonné |
| Noms municipio ≠ geoBoundaries | Mapping fuzzy + log unmatched au build |
| Bundle data > 5 Mo | Défaut San Salvador + toggle national |
| Prompt injection stimulus | System prompt strict ; pas d'outils |
| Licence CC BY 4.0 | README + footer Streamlit |

---

## Ordre d'exécution

| Étape | Livrable |
|-------|----------|
| J0 AM | Scaffold, preload (meta mesurée), enrich, Stage 0 + 3 tests |
| J0 PM | Smoke test APIYI, Stage 1 CLI |
| J1 soir | Stage 1 Streamlit |
| **Avant Stage 2** | `occupation_groups.yaml` pour couleurs carte |
| J2–J3 | Stage 2 Artefact A (carte deck.gl) ; B optionnel |

---

## Prochaine action

1. Scaffold `pyproject.toml` + arborescence Stage 0
2. `sv-preload` → mesurer `row_count` et tailles réelles
3. Implémenter `PersonaGenerator` + 3 tests
4. Smoke test APIYI avant Stage 1
