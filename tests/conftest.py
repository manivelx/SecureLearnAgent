import pytest


@pytest.fixture(autouse=True)
def demo_env(monkeypatch, tmp_path):
    """Run every test in demo mode inside an empty temp directory."""
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)


class FakeLLM:
    """Stands in for GeminiClient so no network call is made."""

    def __init__(self, reply):
        self.reply = reply
        self.prompts = []

    def generate(self, prompt):
        self.prompts.append(prompt)
        return self.reply
