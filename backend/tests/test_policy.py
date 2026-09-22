from app.policy import route
from app.schemas import ChoiceAnswer, NoulAnswer, ScoreAnswer


def _answers(complexity: int, task_type: str = "conversation", reasoning: float = 0.1, latency: float = 0.1) -> dict:
    return {
        "complexity": ScoreAnswer(score=complexity, legend={}, confidence=0.8),
        "task_type": ChoiceAnswer(choice=task_type, probabilities={task_type: 0.8}, confidence=0.8),
        "reasoning_required": NoulAnswer(noul=reasoning),
        "latency_sensitive": NoulAnswer(noul=latency),
    }


def test_trivial_latency_sensitive_task_routes_to_fast_tier():
    model, _ = route(_answers(complexity=0, task_type="conversation", latency=0.9))
    assert model.tier == "fast"


def test_complex_reasoning_task_routes_to_frontier_tier():
    model, _ = route(_answers(complexity=4, task_type="reasoning", reasoning=0.9))
    assert model.tier == "frontier"
    assert model.supports_reasoning


def test_moderate_task_routes_to_balanced_tier():
    model, _ = route(_answers(complexity=2, task_type="factual"))
    assert model.tier == "balanced"


def test_fast_tier_model_never_picked_for_unsupported_reasoning():
    model, _ = route(_answers(complexity=1, task_type="code", reasoning=0.95))
    assert model.supports_reasoning


def test_cheapest_eligible_model_is_chosen():
    model, _ = route(_answers(complexity=2, task_type="factual"))
    # sonnet-balanced is the only balanced-tier model in the default catalog
    assert model.id == "sonnet-balanced"
