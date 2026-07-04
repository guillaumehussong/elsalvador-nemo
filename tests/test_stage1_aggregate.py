from salvador_personas.stage1.aggregate import aggregate_results
from salvador_personas.stage1.models import FocusGroupPersonaResult, PersonaReaction


def _result(score: int, sentiment: str, objections: list[str], verbatim: str) -> FocusGroupPersonaResult:
    return FocusGroupPersonaResult(
        persona_label="A",
        uuid="u1",
        age=30,
        sex="Femenino",
        municipality="San Salvador",
        department="San Salvador",
        occupation="Comercio",
        reaction=PersonaReaction(
            sentiment=sentiment,  # type: ignore[arg-type]
            interest_score=score,
            objections=objections,
            verbatim=verbatim,
        ),
    )


def test_aggregate_mean_and_objections():
    results = [
        _result(8, "positivo", ["Precio alto"], "Me gusta la idea."),
        _result(4, "negativo", ["Precio alto", "No confío"], "No me convence."),
    ]
    agg = aggregate_results(results)
    assert agg.mean_interest_score == 6.0
    assert agg.sentiment_counts["positivo"] == 1
    assert "precio alto" in agg.top_objections[0]
    assert len(agg.sample_verbatims) == 2
