# LOCAL ONLY — clé APIYI exposée, ne jamais déployer en public ouvert sans rate-limit + auth.
from __future__ import annotations

import json
from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from salvador_personas.config.env import load_project_env
from salvador_personas.dataset.cache import project_root, runs_dir
from salvador_personas.models.persona import PersonaFilter
from salvador_personas.stage0.generator import PersonaGenerator
from salvador_personas.stage1.cost import estimate_run_cost_usd
from salvador_personas.stage1.focus_group import run_focus_group
from salvador_personas.stage1.llm.factory import create_llm_client

MAX_N = 25
CONFIRM_ABOVE_N = 15
DEFAULT_N = 8

load_project_env()

app = FastAPI(title="Salvador Personas Focus API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class FocusRequest(BaseModel):
    stimulus: str = Field(min_length=1, max_length=4000)
    n: int = Field(default=DEFAULT_N, ge=1, le=MAX_N)
    seed: int | None = None
    departments: list[str] | None = None
    municipalities: list[str] | None = None
    confirm: bool = False


def _sample_personas(body: FocusRequest):
    try:
        gen = PersonaGenerator()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    filt = PersonaFilter(
        departments=tuple(body.departments) if body.departments else None,
        municipalities=tuple(body.municipalities) if body.municipalities else None,
    )
    gen = gen.filter(filt)
    available = gen.count_filtered()
    if body.n > available:
        raise HTTPException(
            status_code=400,
            detail=f"Seulement {available} personas après filtres (demandé: {body.n})",
        )
    return gen.sample(body.n, seed=body.seed)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/focus/estimate")
def estimate_focus(body: FocusRequest) -> dict:
    personas = _sample_personas(body)
    est = estimate_run_cost_usd(personas, body.stimulus)
    return {
        "n": body.n,
        "stimulus": body.stimulus,
        "seed": body.seed,
        "departments": body.departments,
        "municipalities": body.municipalities,
        **est,
        "confirm_required": body.n > CONFIRM_ABOVE_N,
    }


@app.post("/api/focus/run")
def run_focus(body: FocusRequest) -> dict:
    if body.n > CONFIRM_ABOVE_N and not body.confirm:
        raise HTTPException(
            status_code=400,
            detail=f"N={body.n} > {CONFIRM_ABOVE_N} : envoyer confirm=true",
        )

    personas = _sample_personas(body)
    try:
        client = create_llm_client()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"LLM non configuré : {exc}") from exc

    run = run_focus_group(client=client, personas=personas, stimulus=body.stimulus, seed=body.seed)

    out_dir = runs_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"focus_{ts}.json"
    payload = run.model_dump(mode="json")
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    return {"run": payload, "saved_to": str(out_path)}


def mount_focus_frontend() -> None:
    focus_dir = project_root() / "apps" / "focus"
    if focus_dir.is_dir():
        app.mount("/", StaticFiles(directory=focus_dir, html=True), name="focus")


mount_focus_frontend()
