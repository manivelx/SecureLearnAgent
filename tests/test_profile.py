import json
from datetime import datetime, timedelta

from profile_manager import ProfileManager


def test_new_profile_starts_with_streak_one(tmp_path):
    assert ProfileManager(str(tmp_path)).profile["study_streak"] == 1


def test_weak_areas_follow_the_70_percent_rule(tmp_path):
    manager = ProfileManager(str(tmp_path))
    manager.record_quiz_score("XSS", 50.0)
    manager.record_quiz_score("sqli", 90.0)
    assert manager.profile["weak_areas"] == ["xss"]
    manager.record_quiz_score("xss", 80.0)
    assert manager.profile["weak_areas"] == []


def test_topics_are_not_duplicated_case_insensitively(tmp_path):
    manager = ProfileManager(str(tmp_path))
    manager.mark_topic_studied("SQL Injection")
    manager.mark_topic_studied("sql injection")
    assert manager.profile["topics_studied"] == ["SQL Injection"]


def test_streak_grows_on_consecutive_days_and_resets_after_gap(tmp_path):
    path = tmp_path / "student_profile.json"
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    path.write_text(json.dumps({"study_streak": 4, "last_active_date": yesterday}))
    assert ProfileManager(str(tmp_path)).profile["study_streak"] == 5

    last_week = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    path.write_text(json.dumps({"study_streak": 4, "last_active_date": last_week}))
    assert ProfileManager(str(tmp_path)).profile["study_streak"] == 1


def test_partial_or_corrupt_files_do_not_crash(tmp_path):
    path = tmp_path / "student_profile.json"
    path.write_text(json.dumps({"study_streak": 3}))
    manager = ProfileManager(str(tmp_path))
    manager.mark_topic_studied("crypto")  # key was missing in the file
    assert manager.profile["topics_studied"] == ["crypto"]

    path.write_text("not json")
    assert ProfileManager(str(tmp_path)).profile["topics_studied"] == []

    path.write_text(json.dumps({"last_active_date": "garbage"}))
    assert ProfileManager(str(tmp_path)).profile["study_streak"] == 1
