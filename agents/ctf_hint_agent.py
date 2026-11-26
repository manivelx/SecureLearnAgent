from agents.common import GeminiClient, clean_topic, demo_mode, load_demo


class CTFHintAgent:
    def __init__(self, llm=None):
        self.demo_mode = demo_mode()
        self.llm = llm if llm is not None else (None if self.demo_mode else GeminiClient())

    def generate_hints(self, description: str, category: str) -> str:
        """Give three progressive hints for a CTF challenge without revealing the flag."""
        category = clean_topic(category)
        description = description.strip()
        if not description:
            raise ValueError("challenge description must not be empty")
        if self.demo_mode:
            return load_demo("ctf_hints")

        prompt = f"""
        You are a CTF (Capture The Flag) mentor and coach.
        A student is stuck on a challenge.

        Category: {category}
        Challenge Description: {description}

        Provide 3 progressive hints to help the student solve the challenge.
        Important Rules:
        - Do NOT give the flag or the complete solution.
        - Hint 1 should be a gentle nudge regarding what to look at first.
        - Hint 2 should introduce the required tool or technique.
        - Hint 3 should be a strong push towards the vulnerability or method of exploitation, but still require the student to execute it.

        Format the response with clear headings for each Hint.
        """
        return self.llm.generate(prompt)
