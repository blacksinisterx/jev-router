"""Static model catalog. Prices/latency are illustrative placeholders for
demo purposes -- not live-fetched from any provider. Edit to match real
pricing if you wire this up to actually dispatch calls."""

from pydantic import BaseModel

TIER_ORDER = ["fast", "balanced", "frontier"]


class ModelSpec(BaseModel):
    id: str
    name: str
    tier: str  # fast | balanced | frontier
    input_price_per_m: float  # USD per million input tokens
    output_price_per_m: float
    avg_latency_ms: float
    max_complexity: int  # highest complexity index (0-4) this model is suited for
    supports_reasoning: bool
    good_for: list[str]


CATALOG: list[ModelSpec] = [
    ModelSpec(
        id="haiku-fast", name="Claude Haiku 4.5", tier="fast",
        input_price_per_m=1.00, output_price_per_m=5.00, avg_latency_ms=600,
        max_complexity=2, supports_reasoning=False,
        good_for=["factual", "conversation", "summarization"],
    ),
    ModelSpec(
        id="sonnet-balanced", name="Claude Sonnet 5", tier="balanced",
        input_price_per_m=3.00, output_price_per_m=15.00, avg_latency_ms=1500,
        max_complexity=4, supports_reasoning=True,
        good_for=["factual", "conversation", "summarization", "code", "creative", "reasoning"],
    ),
    ModelSpec(
        id="opus-frontier", name="Claude Opus 5", tier="frontier",
        input_price_per_m=15.00, output_price_per_m=75.00, avg_latency_ms=3500,
        max_complexity=4, supports_reasoning=True,
        good_for=["code", "reasoning"],
    ),
]


def by_tier(tier: str) -> list[ModelSpec]:
    return [m for m in CATALOG if m.tier == tier]


def estimate_cost_usd(model: ModelSpec, input_tokens: int, output_tokens: int) -> float:
    return round(
        input_tokens / 1_000_000 * model.input_price_per_m
        + output_tokens / 1_000_000 * model.output_price_per_m,
        6,
    )
