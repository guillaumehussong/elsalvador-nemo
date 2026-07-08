from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table

from salvador_personas.config.env import load_project_env
from salvador_personas.dataset.cache import runs_dir
from salvador_personas.models.persona import PersonaFilter
from salvador_personas.stage0.generator import PersonaGenerator
from salvador_personas.stage1.cost import estimate_run_cost_usd
from salvador_personas.stage1.focus_group import run_focus_group
from salvador_personas.stage1.llm.factory import create_llm_client

MAX_N = 25
CONFIRM_ABOVE_N = 15
DEFAULT_N = 8

console = Console()


def main() -> None:
    load_project_env()

    parser = argparse.ArgumentParser(
        description="Virtual B2C focus group — Salvadoran persona reactions (Stage 1)."
    )
    parser.add_argument(
        "--stimulus",
        "-s",
        required=True,
        help="Ad copy / hook / price to test",
    )
    parser.add_argument("-n", type=int, default=DEFAULT_N, help=f"Number of personas (default: {DEFAULT_N})")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--department", action="append", dest="departments")
    parser.add_argument("--municipality", action="append", dest="municipalities")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt when N>15")
    parser.add_argument(
        "--estimate-only",
        action="store_true",
        help="Show cost estimate without calling the LLM",
    )
    args = parser.parse_args()

    if args.n < 1:
        console.print("[red]N must be ≥ 1[/red]")
        sys.exit(1)
    if args.n > MAX_N:
        console.print(f"[red]Hard cap: N≤{MAX_N}[/red]")
        sys.exit(1)

    try:
        gen = PersonaGenerator()
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        sys.exit(1)

    filt = PersonaFilter(
        departments=tuple(args.departments) if args.departments else None,
        municipalities=tuple(args.municipalities) if args.municipalities else None,
    )
    gen = gen.filter(filt)
    available = gen.count_filtered()
    if args.n > available:
        console.print(f"[red]Only {available} personas match filters[/red]")
        sys.exit(1)

    personas = gen.sample(args.n, seed=args.seed)
    est = estimate_run_cost_usd(personas, args.stimulus)

    table = Table(title="Cost estimate (before run)")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Personas", str(args.n))
    table.add_row("Input tokens (est.)", str(est["estimated_input_tokens"]))
    table.add_row("Output tokens (est.)", str(est["estimated_output_tokens"]))
    table.add_row("Estimated cost (USD)", f"${est['estimated_cost_usd']:.4f}")
    console.print(table)

    if args.estimate_only:
        return

    if args.n > CONFIRM_ABOVE_N and not args.yes:
        answer = input(f"N={args.n} > {CONFIRM_ABOVE_N}. Continue? [y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            console.print("Cancelled.")
            sys.exit(0)

    client = create_llm_client()
    console.print(f"[cyan]Model: {client.model} — {args.n} LLM calls…[/cyan]")

    run = run_focus_group(client=client, personas=personas, stimulus=args.stimulus, seed=args.seed)

    out_dir = runs_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"focus_{ts}.json"
    out_path.write_text(
        json.dumps(run.model_dump(mode="json"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    console.print(f"\n[green]Result → {out_path}[/green]")
    console.print(f"Mean score: {run.aggregate.mean_interest_score}/10")
    console.print(f"Sentiments: {run.aggregate.sentiment_counts}")
    if run.aggregate.top_objections:
        console.print("Top objections:")
        for obj in run.aggregate.top_objections:
            console.print(f"  • {obj}")
    if run.cost_actual_usd is not None:
        console.print(f"Actual cost (est.): ${run.cost_actual_usd:.4f} ({run.total_tokens} tokens)")


if __name__ == "__main__":
    main()
