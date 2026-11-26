import os
import sys

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.common import clean_topic, demo_mode, slugify
from agents.ctf_hint_agent import CTFHintAgent
from agents.curriculum_agent import CurriculumAgent
from agents.personalization_agent import PersonalizationAgent
from agents.quiz_agent import QuizAgent
from profile_manager import ProfileManager


def save_learning_path(topic: str, content: str, directory: str = "learning_paths") -> str:
    """Write a learning path inside `directory` using a sanitized file name."""
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{slugify(topic)}_path.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def run_quiz(agent: QuizAgent, topic: str, profile_mgr: ProfileManager) -> None:
    print(f"\nGenerating 3 questions on {topic}...\n")
    questions = agent.generate_quiz(topic, num_questions=3)
    if not questions:
        print("Failed to generate quiz. Please try again.")
        return

    correct_count = 0
    for i, q in enumerate(questions, 1):
        print(f"\nQuestion {i}: {q['question']}")
        for key, val in q["options"].items():
            print(f"  {key}) {val}")

        answer = input("Your answer (A/B/C/D): ").strip().upper()
        if answer == q["correct_answer"].upper():
            print("Correct!")
            correct_count += 1
        else:
            print(f"Incorrect. The correct answer was {q['correct_answer']}.")
        print(f"Explanation: {q.get('explanation', '')}")

    score = (correct_count / len(questions)) * 100
    print(f"\nQuiz complete. Score: {correct_count}/{len(questions)} ({score:.1f}%)")
    profile_mgr.record_quiz_score(topic, score)
    print(f"[+] Quiz score for '{topic}' recorded in your profile.")


def main():
    load_dotenv()

    if demo_mode():
        print("\n=== DEMO MODE === Using sample responses. Set DEMO_MODE=false to use live AI.\n")
    elif not os.getenv("GEMINI_API_KEY"):
        print("GEMINI_API_KEY is not set.")
        print("Copy .env.example to .env and add your key, or set DEMO_MODE=true.")
        return 1

    print("Loading student profile...")
    profile_mgr = ProfileManager()
    session_topics = set()

    print("\nWelcome back to SecureLearnAgent!")
    print(f"Current study streak: {profile_mgr.profile['study_streak']} day(s)")

    while True:
        print("\n=== Main Menu ===")
        print("1. Start Learning Path")
        print("2. Get CTF Hint")
        print("3. Take Quiz")
        print("4. Get My Recommendation")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        try:
            if choice == "1":
                topic = clean_topic(input("Enter a cybersecurity topic: "))
                print("\nGenerating curriculum...\n")
                result = CurriculumAgent().generate_curriculum(topic)
                print(result)
                path = save_learning_path(topic, result)
                session_topics.add(topic)
                profile_mgr.mark_topic_studied(topic)
                print(f"\n[+] '{topic}' saved to {path} and added to your studied topics.")

            elif choice == "2":
                category = input("Enter CTF category (e.g., web, crypto): ")
                description = input("Enter the CTF challenge description: ")
                print("\nGenerating hints...\n")
                print(CTFHintAgent().generate_hints(description, category))

            elif choice == "3":
                topic = clean_topic(input("Enter a topic for the quiz: "))
                run_quiz(QuizAgent(), topic, profile_mgr)
                session_topics.add(topic)

            elif choice == "4":
                print("\nAnalyzing your profile and session history...\n")
                recommendation = PersonalizationAgent().recommend_next_topic(
                    profile_mgr.get_profile_summary(), sorted(session_topics)
                )
                print("=== Personalized Recommendation ===")
                print(recommendation)

            elif choice == "5":
                print("Saving profile and exiting. Happy hacking!")
                profile_mgr.save_profile()
                return 0
            else:
                print("Invalid choice. Please try again.")
        except ValueError as exc:
            print(f"Input problem: {exc}")
        except RuntimeError as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    sys.exit(main())
