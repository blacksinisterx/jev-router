import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .catalog import CATALOG, estimate_cost_usd
from .fixtures import DEMO_TASKS
from .policy import route
from .providers import get_provider
from .questions import QUESTIONS
from .schemas import ModelOption, RoutingResult, TaskRequest

app = FastAPI(title="JevRouter", description="An intelligent LLM model router, backed by Jev.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_decisions: list[RoutingResult] = []
_MAX_LOG = 50


def _to_option(model, input_tokens: int, output_tokens: int) -> ModelOption:
    return ModelOption(
        id=model.id, name=model.name, tier=model.tier,
        estimated_cost_usd=estimate_cost_usd(model, input_tokens, output_tokens),
        estimated_latency_ms=model.avg_latency_ms,
    )


@app.post("/route", response_model=RoutingResult)
def route_task(task: TaskRequest) -> RoutingResult:
    start = time.perf_counter()
    provider = get_provider(config.JEV_PROVIDER)
    answers = provider.evaluate(task.prompt, QUESTIONS)
    chosen, reason = route(answers)

    input_tokens = max(len(task.prompt) // 4, 1)
    alternatives = [_to_option(m, input_tokens, task.estimated_output_tokens) for m in CATALOG]

    result = RoutingResult(
        selected_model=_to_option(chosen, input_tokens, task.estimated_output_tokens),
        reason=reason,
        latency_ms=round((time.perf_counter() - start) * 1000, 2),
        provider=config.JEV_PROVIDER,
        raw_answers=answers,
        prompt=task.prompt,
        alternatives=alternatives,
    )

    _decisions.insert(0, result)
    del _decisions[_MAX_LOG:]
    return result


@app.get("/decisions", response_model=list[RoutingResult])
def decisions() -> list[RoutingResult]:
    return _decisions


@app.get("/examples")
def examples() -> list[dict]:
    return DEMO_TASKS


@app.get("/catalog")
def catalog() -> list[dict]:
    return [m.model_dump() for m in CATALOG]


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "provider": config.JEV_PROVIDER}
