import hashlib

from ..schemas import Answer, ChoiceAnswer, ChoiceQuestion, NoulAnswer, NoulQuestion, Question, ScoreAnswer, ScoreQuestion
from .base import Provider

CODE_KW = ["def ", "function", "class ", "algorithm", "python", "javascript", "write a function", "debug", "code"]
REASONING_KW = ["step by step", "explain your reasoning", "how many", "calculate", "solve", "prove", "if x", "logic"]
CREATIVE_KW = ["poem", "story", "once upon a time", "write a short", "creative", "haiku"]
CASUAL_KW = ["hey", "how's it going", "what's up", "lol", "thanks", "how are you"]
SUMMARY_KW = ["summarize", "summarise", "tl;dr", "condense", "in short"]
FACTUAL_KW = ["what is", "when did", "who is", "define", "capital of", "boiling point"]


def _blob(state: str | dict) -> str:
    text = state if isinstance(state, str) else str(state)
    return text.lower()


def _jitter(seed_text: str, low: float, high: float) -> float:
    digest = int(hashlib.sha256(seed_text.encode()).hexdigest(), 16)
    frac = (digest % 1000) / 1000
    return round(low + frac * (high - low), 3)


class MockProvider(Provider):
    """Local, zero-cost stand-in for Jev. Keyword heuristics tuned for
    JevRouter's task-classification questions."""

    name = "mock"

    def evaluate(self, state: str | dict, questions: dict[str, Question]) -> dict[str, Answer]:
        blob = _blob(state)
        hits = {
            "code": any(kw in blob for kw in CODE_KW),
            "reasoning": any(kw in blob for kw in REASONING_KW),
            "creative": any(kw in blob for kw in CREATIVE_KW),
            "casual": any(kw in blob for kw in CASUAL_KW),
            "summary": any(kw in blob for kw in SUMMARY_KW),
            "factual": any(kw in blob for kw in FACTUAL_KW),
        }
        answers: dict[str, Answer] = {}
        for qid, q in questions.items():
            if isinstance(q, ChoiceQuestion):
                answers[qid] = self._task_type(blob, hits, q)
            elif isinstance(q, ScoreQuestion):
                answers[qid] = self._complexity(blob, hits, q)
            elif isinstance(q, NoulQuestion):
                answers[qid] = self._noul(qid, q, blob, hits)
        return answers

    def _task_type(self, blob: str, hits: dict, q: ChoiceQuestion) -> ChoiceAnswer:
        order = ["code", "reasoning", "creative", "summary", "factual", "casual"]
        label_map = {"code": "code", "reasoning": "reasoning", "creative": "creative",
                     "summary": "summarization", "factual": "factual", "casual": "conversation"}
        top_key = next((k for k in order if hits[k]), "casual")
        top = label_map[top_key]
        top_p = _jitter(blob + "task_type", 0.55, 0.9)
        options = list(q.criteria.keys())
        remaining = round(1 - top_p, 3)
        others = [o for o in options if o != top]
        probabilities = {top: top_p}
        for o in others:
            probabilities[o] = round(remaining / len(others), 3) if others else 0.0
        return ChoiceAnswer(choice=top, probabilities=probabilities, confidence=top_p)

    def _complexity(self, blob: str, hits: dict, q: ScoreQuestion) -> ScoreAnswer:
        # reasoning and code both raise complexity, but only true multi-step
        # reasoning keywords should also force reasoning_required high below --
        # plain code generation is complex enough for a mid tier without
        # necessarily needing the top tier.
        levels = len(q.criteria)
        score = 0
        if hits["reasoning"]:
            score += 2
        elif hits["code"]:
            score += 2
        if len(blob) > 150:
            score += 1
        if len(blob) > 350:
            score += 1
        if hits["casual"] or hits["factual"]:
            score = max(0, score - 1)
        score = min(levels - 1, score)
        return ScoreAnswer(score=score, legend={str(i): c for i, c in enumerate(q.criteria)},
                            confidence=_jitter(blob + "complexity", 0.65, 0.92))

    def _noul(self, qid: str, q: NoulQuestion, blob: str, hits: dict) -> NoulAnswer:
        if qid == "reasoning_required" or "reasoning" in q.instructions.lower():
            if hits["reasoning"]:
                return NoulAnswer(noul=_jitter(blob + qid, 0.72, 0.95))
            if hits["code"]:
                # code needs some rigor but isn't automatically "multi-step reasoning"
                return NoulAnswer(noul=_jitter(blob + qid, 0.35, 0.58))
            return NoulAnswer(noul=_jitter(blob + qid, 0.04, 0.2))
        if qid == "latency_sensitive" or "interactive" in q.instructions.lower():
            interactive = hits["casual"] or (len(blob) < 80 and not hits["summary"])
            return NoulAnswer(noul=_jitter(blob + qid, 0.7, 0.93) if interactive else _jitter(blob + qid, 0.1, 0.35))
        return NoulAnswer(noul=_jitter(blob + qid, 0.3, 0.5))
