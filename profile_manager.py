import json
import os
from datetime import datetime, timedelta

WEAK_AREA_THRESHOLD = 70.0


class ProfileManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.profile_path = os.path.join(self.data_dir, "student_profile.json")
        self.profile = self.load_profile()
        self.update_streak()

    def _default_profile(self):
        return {
            "topics_studied": [],
            "quiz_scores": {},  # "topic": score percentage, e.g. 75.0
            "weak_areas": [],
            "study_streak": 1,
            "last_active_date": datetime.now().strftime("%Y-%m-%d"),
        }

    def load_profile(self):
        os.makedirs(self.data_dir, exist_ok=True)
        defaults = self._default_profile()
        if not os.path.exists(self.profile_path):
            return defaults

        try:
            with open(self.profile_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
        except (json.JSONDecodeError, OSError):
            return defaults
        if not isinstance(loaded, dict):
            return defaults

        # Fill any missing keys so older or hand-edited files do not crash.
        defaults.update(loaded)
        return defaults

    def save_profile(self):
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.profile_path, "w", encoding="utf-8") as f:
            json.dump(self.profile, f, indent=4)

    def update_streak(self):
        today = datetime.now().date()
        today_str = today.strftime("%Y-%m-%d")
        last_active_str = self.profile.get("last_active_date", today_str)
        if last_active_str == today_str:
            return

        try:
            last_active = datetime.strptime(last_active_str, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            last_active = None

        if last_active is not None and today - last_active == timedelta(days=1):
            self.profile["study_streak"] = self.profile.get("study_streak", 0) + 1
        else:
            self.profile["study_streak"] = 1

        self.profile["last_active_date"] = today_str
        self.save_profile()

    def mark_topic_studied(self, topic):
        known = [t.lower() for t in self.profile["topics_studied"]]
        if topic.lower() not in known:
            self.profile["topics_studied"].append(topic)
            self.save_profile()

    def record_quiz_score(self, topic, score_percentage):
        self.profile["quiz_scores"][topic.lower()] = score_percentage
        self.profile["weak_areas"] = [
            t for t, score in self.profile["quiz_scores"].items() if score < WEAK_AREA_THRESHOLD
        ]
        self.save_profile()

    def get_profile_summary(self):
        return json.dumps(self.profile, indent=2)
