"""Tests for spaced repetition engine."""

import pytest
from datetime import date, timedelta

from src.models.student import Student
from src.services.repetition_service import (
    calculate_next_review,
    get_signs_due_for_review,
    create_review_session,
    record_review_result,
    MAX_DAILY_REVIEWS,
)


@pytest.fixture
def student():
    return Student(student_id="test", display_name="Test")


def _make_sign_data(consecutive=0, ease=2.5, interval=1, next_review=None):
    if next_review is None:
        next_review = date.today().isoformat()
    return {
        "status": "learned",
        "first_seen": "2026-03-01T10:00:00",
        "learned_at": "2026-03-01T10:00:00",
        "review_history": [],
        "next_review": next_review,
        "interval_days": interval,
        "ease_factor": ease,
        "consecutive_correct": consecutive,
    }


class TestCalculateNextReview:
    def test_first_correct_interval_1_day(self):
        data = _make_sign_data(consecutive=0)
        result = calculate_next_review(data, correct=True)
        assert result["interval_days"] == 1
        assert result["consecutive_correct"] == 1

    def test_second_correct_interval_3_days(self):
        data = _make_sign_data(consecutive=1)
        result = calculate_next_review(data, correct=True)
        assert result["interval_days"] == 3
        assert result["consecutive_correct"] == 2

    def test_third_correct_interval_7_days(self):
        data = _make_sign_data(consecutive=2)
        result = calculate_next_review(data, correct=True)
        assert result["interval_days"] == 7

    def test_fourth_correct_interval_14_days(self):
        data = _make_sign_data(consecutive=3)
        result = calculate_next_review(data, correct=True)
        assert result["interval_days"] == 14

    def test_fifth_correct_uses_ease_factor(self):
        data = _make_sign_data(consecutive=4, interval=14, ease=2.5)
        result = calculate_next_review(data, correct=True)
        assert result["interval_days"] == 30  # capped at max

    def test_wrong_answer_resets_interval(self):
        data = _make_sign_data(consecutive=3, interval=7)
        result = calculate_next_review(data, correct=False)
        assert result["interval_days"] == 1
        assert result["consecutive_correct"] == 0

    def test_ease_increases_on_correct(self):
        data = _make_sign_data(ease=2.5)
        result = calculate_next_review(data, correct=True)
        assert result["ease_factor"] == pytest.approx(2.6)

    def test_ease_decreases_on_wrong(self):
        data = _make_sign_data(ease=2.5)
        result = calculate_next_review(data, correct=False)
        assert result["ease_factor"] == pytest.approx(2.3)

    def test_ease_floor(self):
        data = _make_sign_data(ease=1.3)
        result = calculate_next_review(data, correct=False)
        assert result["ease_factor"] == 1.3

    def test_ease_ceiling(self):
        data = _make_sign_data(ease=3.0)
        result = calculate_next_review(data, correct=True)
        assert result["ease_factor"] == 3.0

    def test_next_review_date_set(self):
        data = _make_sign_data(consecutive=1)
        result = calculate_next_review(data, correct=True)
        expected = (date.today() + timedelta(days=3)).isoformat()
        assert result["next_review"] == expected


class TestGetSignsDueForReview:
    def test_due_signs_returned(self, student):
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        student.signs["INFOR-01"] = _make_sign_data(next_review=yesterday)
        due = get_signs_due_for_review(student)
        assert "INFOR-01" in due

    def test_future_signs_not_returned(self, student):
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        student.signs["INFOR-01"] = _make_sign_data(next_review=tomorrow)
        due = get_signs_due_for_review(student)
        assert due == []

    def test_today_is_due(self, student):
        today = date.today().isoformat()
        student.signs["INFOR-01"] = _make_sign_data(next_review=today)
        due = get_signs_due_for_review(student)
        assert "INFOR-01" in due


class TestCreateReviewSession:
    def test_session_with_due_signs(self, student):
        student.signs["INFOR-01"] = _make_sign_data()
        student.signs["INFOR-02"] = _make_sign_data()
        session = create_review_session(student)
        assert session.total == 2

    def test_empty_when_nothing_due(self, student):
        session = create_review_session(student)
        assert session.total == 0

    def test_limited_to_max(self, student):
        for i in range(1, 40):
            sid = f"INFOR-{i:02d}" if i <= 35 else f"ZAKAZ-{i-35:02d}"
            student.signs[sid] = _make_sign_data()
        session = create_review_session(student)
        assert session.total <= MAX_DAILY_REVIEWS


class TestRecordReviewResult:
    def test_correct_updates_history(self, student):
        student.signs["INFOR-01"] = _make_sign_data()
        record_review_result(student, "INFOR-01", correct=True)
        data = student.signs["INFOR-01"]
        assert len(data["review_history"]) == 1
        assert data["review_history"][0]["correct"] is True
        assert data["consecutive_correct"] == 1

    def test_incorrect_resets(self, student):
        student.signs["INFOR-01"] = _make_sign_data(consecutive=3)
        record_review_result(student, "INFOR-01", correct=False)
        assert student.signs["INFOR-01"]["consecutive_correct"] == 0
        assert student.signs["INFOR-01"]["interval_days"] == 1
