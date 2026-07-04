from __future__ import annotations

from collections import Counter

from salvador_personas.stage1.models import FocusGroupAggregate, FocusGroupPersonaResult


def aggregate_results(results: list[FocusGroupPersonaResult]) -> FocusGroupAggregate:
    if not results:
        return FocusGroupAggregate(
            mean_interest_score=0.0,
            sentiment_counts={},
            top_objections=[],
            sample_verbatims=[],
        )

    scores = [r.reaction.interest_score for r in results]
    sentiment_counts = dict(Counter(r.reaction.sentiment for r in results))

    objection_counter: Counter[str] = Counter()
    for r in results:
        for obj in r.reaction.objections:
            text = obj.strip()
            if text:
                objection_counter[text.lower()] += 1

    top_objections = [text for text, _ in objection_counter.most_common(5)]

    verbatims = [r.reaction.verbatim.strip() for r in results if r.reaction.verbatim.strip()]
    sample_verbatims = verbatims[:5]

    return FocusGroupAggregate(
        mean_interest_score=round(sum(scores) / len(scores), 2),
        sentiment_counts=sentiment_counts,
        top_objections=top_objections,
        sample_verbatims=sample_verbatims,
    )
