"""Local MCP server exposing SecureLearn tools over HTTP on localhost."""

from __future__ import annotations

import logging
from typing import Literal

from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer

from agents.common import GeminiClient, clean_topic, demo_mode, extract_json, load_demo

load_dotenv()
logging.basicConfig(level=logging.INFO)

mcp = MCPServer("SecureLearn MCP Server")

Difficulty = Literal["beginner", "intermediate", "advanced"]


def topic_resources(topic: str, difficulty_level: str, llm=None) -> dict:
    """Return learning resources for a topic. Errors are returned, not raised."""
    try:
        topic = clean_topic(topic)
        if difficulty_level not in {"beginner", "intermediate", "advanced"}:
            raise ValueError("difficulty_level must be beginner, intermediate or advanced")
    except ValueError as exc:
        return {"error": f"Input validation error: {exc}"}

    if demo_mode():
        return load_demo("topic_resources")

    prompt = f"""
    You are an expert Cybersecurity Education AI.
    Generate learning resources for the cybersecurity topic: "{topic}" at the "{difficulty_level}" level.
    Return ONLY a raw JSON object (without markdown wrappers like ```json) with this exact structure:
    {{
        "description": "Brief description of the topic",
        "key_concepts": ["concept1", "concept2"],
        "practice_platforms": ["platform1", "platform2"],
        "recommended_order": ["step1", "step2"]
    }}
    """
    return _ask_for_json(prompt, llm)


def quiz(topic: str, num_questions: int, llm=None) -> dict:
    """Return a multiple-choice quiz. Errors are returned, not raised."""
    try:
        topic = clean_topic(topic)
        if not isinstance(num_questions, int) or not 1 <= num_questions <= 10:
            raise ValueError("num_questions must be an integer between 1 and 10")
    except ValueError as exc:
        return {"error": f"Input validation error: {exc}"}

    if demo_mode():
        return {"questions": load_demo("quiz")["questions"][:num_questions]}

    prompt = f"""
    You are a Cybersecurity Instructor.
    Generate a multiple choice quiz about "{topic}" with exactly {num_questions} questions.
    Return ONLY a raw JSON object (without markdown wrappers like ```json) with this exact structure:
    {{
        "questions": [
            {{
                "question": "Question text",
                "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
                "correct_answer": "A",
                "explanation": "Why this option is correct"
            }}
        ]
    }}
    """
    return _ask_for_json(prompt, llm)


def _ask_for_json(prompt: str, llm) -> dict:
    try:
        client = llm if llm is not None else GeminiClient()
        text = client.generate(prompt)
    except RuntimeError as exc:
        return {"error": str(exc)}
    try:
        parsed = extract_json(text)
    except ValueError:
        return {"error": "Model did not return valid JSON"}
    return parsed if isinstance(parsed, dict) else {"error": "Model returned unexpected JSON"}


@mcp.tool()
def get_topic_resources(topic: str, difficulty_level: Difficulty) -> dict:
    """Return curated learning resources for a cybersecurity topic."""
    return topic_resources(topic, difficulty_level)


@mcp.tool()
def generate_quiz(topic: str, num_questions: int) -> dict:
    """Generate multiple-choice quiz questions (1 to 10) on a topic."""
    return quiz(topic, num_questions)


def main() -> int:
    """Run the MCP server on localhost only."""
    print("Starting SecureLearn MCP Server on http://127.0.0.1:8080")
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8080,
        json_response=True,
        stateless_http=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
