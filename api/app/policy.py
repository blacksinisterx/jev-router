from .catalog import CATALOG, TIER_ORDER, ModelSpec
from .schemas import Answer, ChoiceAnswer, NoulAnswer, ScoreAnswer

REASONING_THRESHOLD = 0.6
LATENCY_THRESHOLD = 0.6


def _target_tier(complexity_idx: int, reasoning: float) -> str:
    if complexity_idx >= 3 or reasoning >= REASONING_THRESHOLD:
        return "frontier"
    if complexity_idx <= 1:
        return "fast"
    return "balanced"


def _eligible(models: list[ModelSpec], complexity_idx: int, needs_reasoning: bool) -> list[ModelSpec]:
    return [m for m in models if m.max_complexity >= complexity_idx and (not needs_reasoning or m.supports_reasoning)]


def route(answers: dict[str, Answer], catalog: list[ModelSpec] = CATALOG) -> tuple[ModelSpec, str]:
    """Returns (chosen model, reason). Picks the cheapest model at the target
    tier that can actually handle the task's complexity/reasoning needs,
    escalating tiers upward until one qualifies."""
    complexity = answers.get("complexity")
    task_type = answers.get("task_type")
    reasoning = answers.get("reasoning_required")
    latency = answers.get("latency_sensitive")

    complexity_idx = round(complexity.score) if isinstance(complexity, ScoreAnswer) else 2
    needs_reasoning = isinstance(reasoning, NoulAnswer) and reasoning.noul >= REASONING_THRESHOLD
    is_latency_sensitive = isinstance(latency, NoulAnswer) and latency.noul >= LATENCY_THRESHOLD
    task = task_type.choice if isinstance(task_type, ChoiceAnswer) else None

    target = _target_tier(complexity_idx, reasoning.noul if isinstance(reasoning, NoulAnswer) else 0.0)
    if is_latency_sensitive and complexity_idx <= 1 and target != "frontier":
        target = "fast"

    start = TIER_ORDER.index(target)
    for tier in TIER_ORDER[start:]:
        candidates = _eligible([m for m in catalog if m.tier == tier], complexity_idx, needs_reasoning)
        if task:
            preferred = [m for m in candidates if task in m.good_for]
            candidates = preferred or candidates
        if candidates:
            chosen = min(candidates, key=lambda m: m.input_price_per_m)
            reason = (
                f"complexity={complexity_idx}/4, task_type={task}, "
                f"reasoning_required={needs_reasoning}, latency_sensitive={is_latency_sensitive} "
                f"-> {tier} tier"
            )
            return chosen, reason

    # Nothing qualified anywhere (shouldn't happen with this catalog) -- fall back to the most capable model.
    chosen = max(catalog, key=lambda m: m.max_complexity)
    return chosen, "no catalog model matched constraints, fell back to most capable model"
