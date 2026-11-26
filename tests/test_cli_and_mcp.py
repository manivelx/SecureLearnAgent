import os

import main as cli
import mcp_server


def run_cli(monkeypatch, inputs):
    answers = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _="": next(answers))
    return cli.main()


def test_cli_learning_path_is_written_inside_learning_paths(monkeypatch, tmp_path):
    assert run_cli(monkeypatch, ["1", "../../outside topic", "5"]) == 0
    files = os.listdir(tmp_path / "learning_paths")
    assert files == ["outside_topic_path.md"]
    assert not (tmp_path.parent / "outside_topic_path.md").exists()


def test_cli_quiz_records_score(monkeypatch, tmp_path):
    # Demo quiz answers: first question is B.
    assert run_cli(monkeypatch, ["3", "linux", "B", "X", "X", "5"]) == 0
    profile = (tmp_path / "data" / "student_profile.json").read_text()
    assert "linux" in profile


def test_cli_handles_empty_topic_without_crashing(monkeypatch):
    assert run_cli(monkeypatch, ["1", "   ", "5"]) == 0


def test_cli_without_key_exits_cleanly(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "false")
    assert cli.main() == 1


def test_mcp_validation_errors_are_returned():
    assert "error" in mcp_server.quiz("", 3)
    assert "error" in mcp_server.quiz("xss", 99)
    assert "error" in mcp_server.topic_resources("xss", "expert")
    assert "error" in mcp_server.topic_resources("x" * 101, "beginner")


def test_mcp_demo_responses():
    assert len(mcp_server.quiz("xss", 2)["questions"]) == 2
    assert "key_concepts" in mcp_server.topic_resources("xss", "beginner")


def test_mcp_live_path_reports_bad_model_output(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "false")

    class Bad:
        def generate(self, prompt):
            return "nope"

    assert mcp_server.quiz("xss", 2, llm=Bad()) == {"error": "Model did not return valid JSON"}
