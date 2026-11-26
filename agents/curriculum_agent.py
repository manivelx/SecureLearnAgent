from agents.common import GeminiClient, clean_topic, demo_mode, load_demo


class CurriculumAgent:
    def __init__(self, llm=None):
        self.demo_mode = demo_mode()
        self.llm = llm if llm is not None else (None if self.demo_mode else GeminiClient())

    def generate_curriculum(self, topic: str) -> str:
        """Generate a beginner-to-advanced learning path for a cybersecurity topic."""
        topic = clean_topic(topic)
        if self.demo_mode:
            return load_demo("curriculum")

        prompt = f"""
        You are an expert Cybersecurity Education AI.
        Create a structured, beginner-to-advanced learning path for the following topic: "{topic}".

        The curriculum must include:
        1. A brief introduction to the topic.
        2. Beginner concepts and foundational knowledge required.
        3. Intermediate concepts with practical applications or lab ideas.
        4. Advanced concepts, including real-world scenarios or complex attacks/defenses.
        5. A list of high-quality resources to study (e.g., specific CVEs, standard tools, documentation).

        Format the response in clear Markdown.
        """
        return self.llm.generate(prompt)
