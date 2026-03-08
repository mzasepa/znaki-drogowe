"""Tests for learning service - Module 1 logic."""

import pytest
from src.models.student import Student
from src.services.learning_service import (
    get_unlearned_signs,
    create_learning_session,
    mark_sign_known,
    mark_sign_unknown,
    advance_to_retry,
)


@pytest.fixture
def student():
    return Student(student_id="test", display_name="Test")


class TestGetUnlearnedSigns:
    def test_all_unlearned_initially(self, student):
        signs = get_unlearned_signs(student, "Informacyjne")
        assert len(signs) == 35

    def test_excludes_learned(self, student):
        student.signs["INFOR-01"] = {"status": "learned"}
        signs = get_unlearned_signs(student, "Informacyjne")
        assert len(signs) == 34
        assert all(s.sign_id != "INFOR-01" for s in signs)


class TestCreateSession:
    def test_default_batch_size(self, student):
        session = create_learning_session(student, "Informacyjne")
        assert len(session.signs) == 10

    def test_custom_batch_size(self, student):
        session = create_learning_session(student, "Informacyjne", batch_size=5)
        assert len(session.signs) == 5

    def test_respects_settings(self, student):
        student.settings["signs_per_session"] = 7
        session = create_learning_session(student, "Informacyjne")
        assert len(session.signs) == 7

    def test_fewer_than_batch_available(self, student):
        # Szlaki_rowerowe has only 4 signs
        session = create_learning_session(student, "Szlaki_rowerowe", batch_size=10)
        assert len(session.signs) == 4


class TestMarkKnown:
    def test_mark_known_updates_student(self, student):
        session = create_learning_session(student, "Informacyjne", batch_size=3)
        sign_id = session.signs[0].sign_id
        mark_sign_known(student, sign_id, session)

        assert student.signs[sign_id]["status"] == "learned"
        assert student.signs[sign_id]["next_review"] is not None
        assert sign_id in session.learned_in_session
        assert session.current_index == 1

    def test_mark_known_advances_session(self, student):
        session = create_learning_session(student, "Informacyjne", batch_size=2)
        mark_sign_known(student, session.signs[0].sign_id, session)
        assert session.progress == 1


class TestMarkUnknown:
    def test_mark_unknown_adds_to_retry(self, student):
        session = create_learning_session(student, "Informacyjne", batch_size=3)
        sign = session.signs[0]
        mark_sign_unknown(student, sign.sign_id, session)

        assert sign in session.not_learned
        assert session.current_index == 1

    def test_mark_unknown_sets_learning_status(self, student):
        session = create_learning_session(student, "Informacyjne", batch_size=3)
        sign_id = session.signs[0].sign_id
        mark_sign_unknown(student, sign_id, session)
        assert student.signs[sign_id]["status"] == "learning"


class TestAdvanceToRetry:
    def test_retry_moves_not_learned_back(self, student):
        session = create_learning_session(student, "Informacyjne", batch_size=3)
        # Mark first two unknown, last one known
        mark_sign_unknown(student, session.signs[0].sign_id, session)
        mark_sign_unknown(student, session.signs[1].sign_id, session)
        mark_sign_known(student, session.signs[2].sign_id, session)

        assert session.current_index == 3
        advance_to_retry(session)
        assert session.current_index == 0
        assert len(session.signs) == 2

    def test_no_retry_when_all_learned(self, student):
        session = create_learning_session(student, "Szlaki_rowerowe", batch_size=2)
        mark_sign_known(student, session.signs[0].sign_id, session)
        mark_sign_known(student, session.signs[1].sign_id, session)

        advance_to_retry(session)
        assert session.is_complete

    def test_session_complete_after_all_learned(self, student):
        session = create_learning_session(student, "Szlaki_rowerowe", batch_size=2)
        # First pass: mark all unknown
        mark_sign_unknown(student, session.signs[0].sign_id, session)
        mark_sign_unknown(student, session.signs[1].sign_id, session)
        advance_to_retry(session)

        # Second pass: mark all known
        mark_sign_known(student, session.signs[0].sign_id, session)
        mark_sign_known(student, session.signs[1].sign_id, session)
        advance_to_retry(session)

        assert session.is_complete
