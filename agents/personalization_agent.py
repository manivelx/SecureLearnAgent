from agents.common import GeminiClient, demo_mode, load_demo


class PersonalizationAgent:
    def __init__(self, llm=None):
        self.demo_mode = demo_mode()
        self.llm = llm if llm is not None else (None if self.demo_mode else GeminiClient())

    def recommend_next_topic(self, profile_data: str, session_topics: list) -> str:
        """Recommend one topic to study next from the student's profile and session."""
        if self.demo_mode:
            return load_demo("personalization")

        prompt = f"""
        You are a Cybersecurity Mentorship AI. Your goal is to recommend ONE specific cybersecurity topic for the student to study next.

        Here is the student's current profile (JSON format):
        {profile_data}

        Here are the topics they have ALREADY discussed in the current study session:
        {session_topics}

        Rules for recommendation:
        1. Look at "weak_areas". If there are weak areas, prioritize reviewing them.
        2. Look at "topics_studied". Recommend something that builds logically upon what they already know (Difficulty progression).
        3. DO NOT recommend any topic that is in the "session_topics" list (they just did it).
        4. Do not jump to advanced topics if they haven't covered basics.

        Respond in Markdown format.
        Provide the recommended topic clearly at the top, and explain why you chose it based on their profile. Include a brief summary of what they will learn.
        """
        return self.llm.generate(prompt)
