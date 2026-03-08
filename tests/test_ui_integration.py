"""Integration and end-to-end tests."""

import pytest
from datetime import date, timedelta

from src.models.student import Student
from src.models.sign_catalog import get_all_signs, get_signs_by_category, get_sign_by_id
from src.services.student_service import (
    create_student, save_student, load_student, get_dashboard_stats,
)
from src.services.learning_service import (
    create_learning_session, mark_sign_known, mark_sign_unknown,
    advance_to_retry, get_unlearned_signs,
)
from src.services.repetition_service import (
    create_review_session, record_review_result, get_signs_due_for_review,
)
from src.services.test_service import (
    create_test_session, record_answer, save_test_result, create_retry_session,
)


class TestEndToEndFlow:
    """Full flow: create student -> learn -> review -> test."""

    def test_full_learning_flow(self, tmp_path):
        # 1. Create student
        student = create_student("Anna Nowak", data_dir=tmp_path)
        assert student.student_id == "anna_nowak"

        # 2. Learn 4 signs from Szlaki_rowerowe (small category)
        session = create_learning_session(student, "Szlaki_rowerowe", batch_size=4)
        assert session.total == 4

        # Mark 2 as known, 2 as unknown
        mark_sign_known(student, session.signs[0].sign_id, session)
        mark_sign_known(student, session.signs[1].sign_id, session)
        mark_sign_unknown(student, session.signs[2].sign_id, session)
        mark_sign_unknown(student, session.signs[3].sign_id, session)

        # Retry unknown
        advance_to_retry(session)
        assert len(session.signs) == 2
        mark_sign_known(student, session.signs[0].sign_id, session)
        mark_sign_known(student, session.signs[1].sign_id, session)
        advance_to_retry(session)
        assert session.is_complete

        save_student(student, data_dir=tmp_path)

        # 3. Check stats
        stats = get_dashboard_stats(student)
        assert stats.learned == 4

        # 4. Review - signs should be due (set next_review to today)
        for sign_id in student.signs:
            student.signs[sign_id]["next_review"] = date.today().isoformat()
        review_session = create_review_session(student)
        assert review_session.total == 4

        for i in range(4):
            sign = review_session.current_sign
            record_review_result(student, sign.sign_id, correct=True)
            review_session.current_index += 1

        save_student(student, data_dir=tmp_path)

        # 5. Test
        test_session = create_test_session(mode="random", count=10)
        for _ in range(10):
            q = test_session.current_question
            record_answer(test_session, q.correct_index)
        assert test_session.is_complete

        save_test_result(student, test_session, "random")
        save_student(student, data_dir=tmp_path)

        # 6. Verify persistence
        loaded = load_student("anna_nowak", data_dir=tmp_path)
        assert loaded is not None
        assert len(loaded.test_history) == 1
        assert loaded.test_history[0]["correct_answers"] == 10


class TestEdgeCases:
    def test_empty_category_learning(self):
        student = Student(student_id="test", display_name="Test")
        # Learn all signs in Szlaki_rowerowe first
        for sign in get_signs_by_category("Szlaki_rowerowe"):
            student.signs[sign.sign_id] = {"status": "learned"}
        unlearned = get_unlearned_signs(student, "Szlaki_rowerowe")
        assert unlearned == []

    def test_all_signs_learned_stats(self):
        student = Student(student_id="test", display_name="Test")
        for sign in get_all_signs():
            student.signs[sign.sign_id] = {
                "status": "learned",
                "next_review": "2099-12-31",
            }
        stats = get_dashboard_stats(student)
        assert stats.learned == 176
        assert stats.remaining == 0

    def test_student_no_history(self):
        student = Student(student_id="test", display_name="Test")
        stats = get_dashboard_stats(student)
        assert stats.learned == 0
        assert stats.due_for_review == 0

    def test_review_with_no_learned_signs(self):
        student = Student(student_id="test", display_name="Test")
        session = create_review_session(student)
        assert session.total == 0

    def test_test_wrong_answers_retry(self):
        session = create_test_session(mode="random", count=5)
        # Answer all wrong
        for _ in range(5):
            q = session.current_question
            wrong_idx = (q.correct_index + 1) % 4
            record_answer(session, wrong_idx)

        assert len(session.wrong_answers) == 5
        retry = create_retry_session(session.wrong_answers)
        assert retry is not None
        assert retry.total == 5

    def test_all_176_images_accessible(self):
        from src.models.sign_catalog import get_image_path
        for sign in get_all_signs():
            path = get_image_path(sign)
            assert path.exists(), f"Missing: {path}"
