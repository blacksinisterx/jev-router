from app.providers.mock import MockProvider
from app.questions import QUESTIONS
from app.schemas import ChoiceAnswer, NoulAnswer, ScoreAnswer

provider = MockProvider()


def test_code_prompt_classified_as_code():
    answers = provider.evaluate("Write a Python function that reverses a linked list.", QUESTIONS)
    task_type = answers["task_type"]
    assert isinstance(task_type, ChoiceAnswer)
    assert task_type.choice == "code"


def test_casual_prompt_classified_as_conversation_and_latency_sensitive():
    answers = provider.evaluate("hey how's it going, what's up?", QUESTIONS)
    assert isinstance(answers["task_type"], ChoiceAnswer)
    assert answers["task_type"].choice == "conversation"
    latency = answers["latency_sensitive"]
    assert isinstance(latency, NoulAnswer)
    assert latency.noul > 0.5


def test_reasoning_prompt_flags_reasoning_required():
    answers = provider.evaluate(
        "A farmer has 17 sheep, all but 9 die. How many are left? Explain your reasoning step by step.",
        QUESTIONS,
    )
    reasoning = answers["reasoning_required"]
    assert isinstance(reasoning, NoulAnswer)
    assert reasoning.noul > 0.5


def test_answers_are_schema_valid_for_every_question():
    answers = provider.evaluate("What is the capital of France?", QUESTIONS)
    assert set(answers.keys()) == set(QUESTIONS.keys())
    assert isinstance(answers["complexity"], ScoreAnswer)
