from .schemas import ChoiceQuestion, NoulQuestion, Question, ScoreQuestion

QUESTIONS: dict[str, Question] = {
    "complexity": ScoreQuestion(
        instructions="Rate how difficult this task is for a language model to do well.",
        criteria=["trivial", "simple", "moderate", "complex", "expert"],
    ),
    "task_type": ChoiceQuestion(
        instructions="Classify the primary type of this task.",
        criteria={
            "factual": "Looking up or stating a fact",
            "conversation": "Casual chat or a short interactive exchange",
            "summarization": "Condensing or extracting from a longer text",
            "code": "Writing, explaining, or debugging code",
            "creative": "Creative writing: stories, poems, marketing copy",
            "reasoning": "Multi-step logical, mathematical, or analytical reasoning",
        },
    ),
    "reasoning_required": NoulQuestion(
        instructions="Does answering this well require multi-step reasoning or chain-of-thought, rather than a direct lookup or generation?",
        criteria={"true": "Needs multi-step reasoning", "false": "Direct answer suffices"},
    ),
    "latency_sensitive": NoulQuestion(
        instructions="Does this look like an interactive, real-time exchange where a slow response would be noticed (e.g. a chat turn), as opposed to a batch/background job?",
        criteria={"true": "Interactive, latency matters", "false": "Batch-tolerant"},
    ),
}
