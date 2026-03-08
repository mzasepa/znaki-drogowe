"""Tests for test service - Module 3 logic."""

import pytest
from src.models.student import Student
from src.services.test_service import (
    create_test_session,
    generate_question,
    record_answer,
    create_retry_session,
    save_test_result,
    _get_distractors,
)
from src.models.sign_catalog import get_sign_by_id, get_all_signs, get_signs_by_category


class TestCreateTestSession:
    def test_random_mode_10(self):
        session = create_test_session(mode="random", count=10)
        assert session.total == 10

    def test_random_mode_20(self):
        session = create_test_session(mode="random", count=20)
        assert session.total == 20

    def test_random_mode_30(self):
        session = create_test_session(mode="random", count=30)
        assert session.total == 30

    def test_all_mode(self):
        session = create_test_session(mode="all")
        assert session.total == 176


class TestGenerateQuestion:
    def test_type_1_has_4_text_options(self):
        sign = get_sign_by_id("INFOR-01")
        q = generate_question(sign, question_type=1)
        assert q.question_type == 1
        assert len(q.options) == 4
        assert sign.name in q.options
        assert q.options[q.correct_index] == sign.name

    def test_type_2_has_4_image_options(self):
        sign = get_sign_by_id("INFOR-01")
        q = generate_question(sign, question_type=2)
        assert q.question_type == 2
        assert len(q.options) == 4
        assert sign.sign_id in q.options
        assert q.options[q.correct_index] == sign.sign_id

    def test_correct_answer_at_random_position(self):
        sign = get_sign_by_id("ZAKAZ-01")
        positions = set()
        for _ in range(50):
            q = generate_question(sign, question_type=1)
            positions.add(q.correct_index)
        # With 50 tries, should hit at least 2 different positions
        assert len(positions) >= 2

    def test_auto_question_type(self):
        sign = get_sign_by_id("INFOR-01")
        types = set()
        for _ in range(50):
            q = generate_question(sign)
            types.add(q.question_type)
        assert types == {1, 2}


class TestDistractors:
    def test_distractors_from_same_category(self):
        sign = get_sign_by_id("INFOR-01")
        distractors = _get_distractors(sign, 3)
        assert len(distractors) == 3
        assert all(d.sign_id != sign.sign_id for d in distractors)
        # Most should be from same category (Informacyjne has 35 signs)
        assert all(d.category == sign.category for d in distractors)

    def test_fallback_for_small_category(self):
        # Szlaki_rowerowe has only 4 signs
        sign = get_signs_by_category("Szlaki_rowerowe")[0]
        distractors = _get_distractors(sign, 3)
        assert len(distractors) == 3


class TestRecordAnswer:
    def test_correct_answer(self):
        session = create_test_session(mode="random", count=5)
        q = session.current_question
        result = record_answer(session, q.correct_index)
        assert result is True
        assert session.current_index == 1
        assert session.correct_count == 1

    def test_wrong_answer(self):
        session = create_test_session(mode="random", count=5)
        q = session.current_question
        wrong_idx = (q.correct_index + 1) % 4
        result = record_answer(session, wrong_idx)
        assert result is False
        assert len(session.wrong_answers) == 1
        assert session.wrong_answers[0]["sign_id"] == q.sign.sign_id

    def test_session_completes(self):
        session = create_test_session(mode="random", count=3)
        for _ in range(3):
            q = session.current_question
            record_answer(session, q.correct_index)
        assert session.is_complete


class TestRetrySession:
    def test_creates_from_wrong_answers(self):
        wrong = [
            {"sign_id": "INFOR-01", "question_type": 1,
             "chosen_answer": "x", "correct_answer": "y"},
            {"sign_id": "INFOR-02", "question_type": 2,
             "chosen_answer": "x", "correct_answer": "y"},
        ]
        retry = create_retry_session(wrong)
        assert retry is not None
        assert retry.total == 2

    def test_returns_none_for_empty(self):
        assert create_retry_session([]) is None


class TestSaveTestResult:
    def test_saves_to_history(self):
        student = Student(student_id="test", display_name="Test")
        session = create_test_session(mode="random", count=5)
        # Answer all correctly
        for _ in range(5):
            q = session.current_question
            record_answer(session, q.correct_index)

        save_test_result(student, session, mode="random")
        assert len(student.test_history) == 1
        assert student.test_history[0]["total_questions"] == 5
        assert student.test_history[0]["correct_answers"] == 5
        assert student.test_history[0]["mode"] == "random"
