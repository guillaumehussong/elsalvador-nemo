from __future__ import annotations

import argparse
import sys

from salvador_personas.models.persona import PersonaFilter
from salvador_personas.stage0.generator import PersonaGenerator


def main() -> None:
    parser = argparse.ArgumentParser(description="Échantillonne des personas Salvador (Stage 0).")
    parser.add_argument("-n", type=int, default=3, help="Nombre de personas (défaut: 3)")
    parser.add_argument("--seed", type=int, default=None, help="Graine aléatoire")
    parser.add_argument("--department", action="append", dest="departments", help="Filtrer par département")
    parser.add_argument("--municipality", action="append", dest="municipalities")
    parser.add_argument("--occupation", action="append", dest="occupations")
    parser.add_argument("--age-min", type=int, default=None)
    parser.add_argument("--age-max", type=int, default=None)
    parser.add_argument("--area", choices=["urbano", "rural"], default=None)
    parser.add_argument("--sex", choices=["Femenino", "Masculino"], default=None)
    parser.add_argument("--count-only", action="store_true", help="Afficher le décompte filtré seulement")
    args = parser.parse_args()

    try:
        gen = PersonaGenerator()
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    print(f"Dataset : {gen.row_count} personas")

    filt = PersonaFilter(
        departments=tuple(args.departments) if args.departments else None,
        municipalities=tuple(args.municipalities) if args.municipalities else None,
        occupations=tuple(args.occupations) if args.occupations else None,
        age_min=args.age_min,
        age_max=args.age_max,
        area=args.area,
        sex=args.sex,
    )
    gen = gen.filter(filt)
    print(f"Après filtres : {gen.count_filtered()} personas")

    if args.count_only:
        return

    personas = gen.sample(args.n, seed=args.seed)
    for i, p in enumerate(personas, 1):
        print(f"\n--- Persona {i} ({p.uuid[:8]}…) ---")
        print(f"{p.age} ans · {p.sex} · {p.occupation}")
        print(f"{p.municipality}, {p.department} ({p.area})")
        print(f"Revenu proxy : ${p.derived.income_usd_monthly:.0f}/mois · adoption {p.derived.adoption_propensity:.2f}")
        print(p.backstory[:400] + ("…" if len(p.backstory) > 400 else ""))


if __name__ == "__main__":
    main()
