from agents.common import GeminiClient, clean_topic, demo_mode, extract_json, load_demo


class QuizAgent:
    def __init__(self, llm=None):
        self.demo_mode = demo_mode()
        self.llm = llm if llm is not None else (None if self.demo_mode else GeminiClient())

    def generate_quiz(self, topic: str, num_questions: int = 3) -> list:
        """Return a list of multiple-choice questions, or [] if the reply cannot be parsed."""
        topic = clean_topic(topic)
        if not 1 <= num_questions <= 10:
            raise ValueError("num_questions must be between 1 and 10")
        if self.demo_mode:
            return load_demo("quiz")["questions"][:num_questions]

        prompt = f"""
        You are a Cybersecurity Instructor.
        Generate a multiple choice quiz about "{topic}" with exactly {num_questions} questions.
        Return ONLY a raw JSON object (no markdown, no ```json wrapper) with this structure:
        {{
            "questions": [
                {{
                    "question": "Question text",
                    "options": {{ "A": "...", "B": "...", "C": "...", "D": "..." }},
                    "correct_answer": "A",
                    "explanation": "Why this option is correct"
                }}
            ]
        }}
        """
        try:
            parsed = extract_json(self.llm.generate(prompt))
        except ValueError:
            return []
        questions = parsed.get("questions", []) if isinstance(parsed, dict) else []
        return [q for q in questions if _valid_question(q)]


def _valid_question(question) -> bool:
    return (
        isinstance(question, dict)
        and isinstance(question.get("options"), dict)
        and str(question.get("correct_answer", "")).upper() in question["options"]
        and "question" in question
    )
