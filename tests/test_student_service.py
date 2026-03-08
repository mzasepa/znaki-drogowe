"""Tests for student service."""

import pytest
from pathlib import Path

from src.services.student_service import (
    create_student,
    save_student,
    load_student,
    list_students,
    delete_student,
    rename_student,
    get_dashboard_stats,
    _sanitize_id,
)
from src.models.student import Student


class TestSanitizeId:
    def test_simple_name(self):
        assert _sanitize_id("Jan Kowalski") == "jan_kowalski"

    def test_polish_characters(self):
        assert _sanitize_id("Łukasz") == "lukasz"

    def test_diacritics(self):
        assert _sanitize_id("Żółć") == "zolc"

    def test_complex_polish_name(self):
        assert _sanitize_id("Grzegorz Brzęczyszczykiewicz") == "grzegorz_brzeczyszczykiewicz"

    def test_extra_spaces(self):
        assert _sanitize_id("  Jan   Kowalski  ") == "jan_kowalski"


class TestCreateSaveLoad:
    def test_create_and_load(self, tmp_path):
        student = create_student("Jan Kowalski", data_dir=tmp_path)
        assert student.student_id == "jan_kowalski"
        assert student.display_name == "Jan Kowalski"

        loaded = load_student("jan_kowalski", data_dir=tmp_path)
        assert loaded is not None
        assert loaded.display_name == "Jan Kowalski"

    def test_save_and_load_preserves_data(self, tmp_path):
        student = Student(
            student_id="test",
            display_name="Test",
            settings={"signs_per_session": 15},
        )
        student.signs["INFOR-01"] = {"status": "learned", "next_review": "2026-03-10"}
        save_student(student, data_dir=tmp_path)

        loaded = load_student("test", data_dir=tmp_path)
        assert loaded.settings["signs_per_session"] == 15
        assert loaded.signs["INFOR-01"]["status"] == "learned"

    def test_load_nonexistent_returns_none(self, tmp_path):
        assert load_student("ghost", data_dir=tmp_path) is None


class TestListStudents:
    def test_list_empty(self, tmp_path):
        assert list_students(data_dir=tmp_path) == []

    def test_list_multiple(self, tmp_path):
        create_student("Anna Nowak", data_dir=tmp_path)
        create_student("Jan Kowalski", data_dir=tmp_path)
        students = list_students(data_dir=tmp_path)
        assert len(students) == 2
        ids = [s["student_id"] for s in students]
        assert "anna_nowak" in ids
        assert "jan_kowalski" in ids


class TestDeleteStudent:
    def test_delete_existing(self, tmp_path):
        create_student("Jan Kowalski", data_dir=tmp_path)
        assert delete_student("jan_kowalski", data_dir=tmp_path) is True
        assert load_student("jan_kowalski", data_dir=tmp_path) is None
        assert list_students(data_dir=tmp_path) == []

    def test_delete_nonexistent(self, tmp_path):
        assert delete_student("ghost", data_dir=tmp_path) is False


class TestRenameStudent:
    def test_rename_existing_student(self, tmp_path):
        create_student("Jan Kowalski", data_dir=tmp_path)
        result = rename_student("jan_kowalski", "Jan Nowak", data_dir=tmp_path)
        assert result is not None
        assert result.display_name == "Jan Nowak"
        # Verify persisted in student file
        loaded = load_student("jan_kowalski", data_dir=tmp_path)
        assert loaded.display_name == "Jan Nowak"
        # Verify updated in index
        students = list_students(data_dir=tmp_path)
        assert students[0]["display_name"] == "Jan Nowak"

    def test_rename_nonexistent_returns_none(self, tmp_path):
        assert rename_student("ghost", "New Name", data_dir=tmp_path) is None

    def test_rename_preserves_progress(self, tmp_path):
        student = create_student("Jan Kowalski", data_dir=tmp_path)
        student.signs["INFOR-01"] = {"status": "learned", "next_review": "2026-03-10"}
        student.test_history.append({"score": 80, "date": "2026-03-08"})
        save_student(student, data_dir=tmp_path)

        result = rename_student("jan_kowalski", "Jan Nowak", data_dir=tmp_path)
        assert result.signs["INFOR-01"]["status"] == "learned"
        assert result.test_history[0]["score"] == 80


class TestDashboardStats:
    def test_empty_student(self):
        student = Student(student_id="test", display_name="Test")
        stats = get_dashboard_stats(student)
        assert stats.total_signs == 176
        assert stats.learned == 0
        assert stats.remaining == 176
        assert stats.due_for_review == 0

    def test_with_learned_signs(self):
        student = Student(student_id="test", display_name="Test")
        student.signs["INFOR-01"] = {
            "status": "learned",
            "next_review": "2020-01-01",  # past date = due
        }
        student.signs["INFOR-02"] = {
            "status": "learned",
            "next_review": "2099-12-31",  # future date = not due
        }
        stats = get_dashboard_stats(student)
        assert stats.learned == 2
        assert stats.remaining == 174
        assert stats.due_for_review == 1
