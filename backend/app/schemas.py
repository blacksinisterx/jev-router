"""Pydantic models mirroring the real Jev HTTP API (docs.typesafe.ai/api.md) exactly,
so any Provider implementation is interchangeable without touching call sites."""

from typing import Literal, Union
from pydantic import BaseModel

# ---- Questions (request side) ----


class NoulQuestion(BaseModel):
    type: Literal["noul"] = "noul"
    instructions: str
    criteria: dict[str, str] | None = None  # {"true": ..., "false": ...}


class ChoiceQuestion(BaseModel):
    type: Literal["choice"] = "choice"
    instructions: str
    criteria: dict[str, str]  # option_key -> description, max 255 options


class ScoreQuestion(BaseModel):
    type: Literal["score"] = "score"
    instructions: str
    criteria: list[str]  # ordered level descriptions, 2-10 levels


Question = Union[NoulQuestion, ChoiceQuestion, ScoreQuestion]


class JevRequest(BaseModel):
    state: str | dict | list
    model: str = "jev-latest"
    questions: dict[str, Question]


# ---- Answers (response side) ----


class NoulAnswer(BaseModel):
    type: Literal["noul"] = "noul"
    noul: float  # 0-1


class ChoiceAnswer(BaseModel):
    type: Literal["choice"] = "choice"
    choice: str
    probabilities: dict[str, float]
    confidence: float


class ScoreAnswer(BaseModel):
    type: Literal["score"] = "score"
    score: float
    legend: dict[str, str] = {}
    probabilities: dict[str, float] = {}
    confidence: float


Answer = Union[NoulAnswer, ChoiceAnswer, ScoreAnswer]


class Usage(BaseModel):
    input_tokens: int
    output_tokens: int


class JevResponse(BaseModel):
    model: str
    answers: dict[str, Answer]
    usage: Usage


# ---- JevRouter's own API surface ----


class TaskRequest(BaseModel):
    prompt: str
    estimated_output_tokens: int = 500


class ModelOption(BaseModel):
    id: str
    name: str
    tier: str
    estimated_cost_usd: float
    estimated_latency_ms: float


class RoutingResult(BaseModel):
    selected_model: ModelOption
    reason: str
    latency_ms: float
    provider: str
    raw_answers: dict[str, Answer] = {}
    prompt: str
    alternatives: list[ModelOption] = []
