import json

import pytest

from agents import CTFHintAgent, CurriculumAgent, PersonalizationAgent, QuizAgent
from tests.conftest import FakeLLM


def test_demo_agents_need_no_key():
    assert CurriculumAgent().generate_curriculum("sql injection").startswith("# Learning Path")
    assert "Hint 1" in CTFHintAgent().generate_hints("login form", "web")
    assert PersonalizationAgent().recommend_next_topic("{}", [])
    assert len(QuizAgent().generate_quiz("linux", 2)) == 2


def test_live_mode_without_key_gives_clear_error(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "false")
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        CurriculumAgent()


def test_live_mode_uses_injected_client(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "false")
    llm = FakeLLM("# Path")
    assert CurriculumAgent(llm=llm).generate_curriculum("xss") == "# Path"
    assert "xss" in llm.prompts[0]


def test_quiz_parses_fenced_json_and_drops_invalid_questions(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "false")
    good = {"question": "Q?", "options": {"A": "1", "B": "2"}, "correct_answer": "b", "explanation": "e"}
    bad = {"question": "Q?", "options": {"A": "1"}, "correct_answer": "Z"}
    reply = "```json\n" + json.dumps({"questions": [good, bad]}) + "\n```"
    assert QuizAgent(llm=FakeLLM(reply)).generate_quiz("xss", 2) == [good]


def test_quiz_returns_empty_list_on_unparseable_reply(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "false")
    assert QuizAgent(llm=FakeLLM("sorry")).generate_quiz("xss", 2) == []


def test_quiz_rejects_bad_counts():
    for n in (0, 11):
        with pytest.raises(ValueError):
            QuizAgent().generate_quiz("xss", n)


def test_ctf_hint_prompt_forbids_giving_the_flag(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "false")
    llm = FakeLLM("hints")
    CTFHintAgent(llm=llm).generate_hints("find the bug", "web")
    assert "Do NOT give the flag" in llm.prompts[0]
