"""Shared test fixtures."""

import json
import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_data_dir(tmp_path):
    """Provide a temporary data directory for student files."""
    students_dir = tmp_path / "students"
    students_dir.mkdir()
    return tmp_path


@pytest.fixture
def sample_student_data():
    """Return minimal student data dict for testing."""
    return {
        "student_id": "jan_kowalski",
        "display_name": "Jan Kowalski",
        "created_at": "2026-03-07T10:00:00",
        "settings": {"signs_per_session": 10},
        "signs": {},
        "test_history": [],
    }
