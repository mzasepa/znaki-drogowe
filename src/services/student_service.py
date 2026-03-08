"""Student CRUD operations and persistence."""

import json
import re
import unicodedata
from datetime import date
from pathlib import Path

from src.models.student import Student, DashboardStats
from src.models.sign_catalog import get_all_signs


DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "students"
INDEX_FILE = DATA_DIR / "index.json"


def _sanitize_id(name: str) -> str:
    """Convert a display name to a filesystem-safe student ID.

    Removes diacritics (e.g. 'Łukasz' -> 'lukasz'), lowercases,
    and replaces spaces with underscores.
    """
    # Normalize unicode: decompose, then remove combining marks
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_str = "".join(c for c in nfkd if not unicodedata.combining(c))
    # Handle Polish Ł/ł specifically (not decomposed by NFKD)
    ascii_str = ascii_str.replace("Ł", "L").replace("ł", "l")
    # Keep only alphanumeric and spaces, then convert
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", ascii_str)
    return re.sub(r"\s+", "_", cleaned.strip()).lower()


def _load_index() -> dict:
    """Load the student index file."""
    if not INDEX_FILE.exists():
        return {"students": []}
    with open(INDEX_FILE, encoding="utf-8") as f:
        return json.load(f)


def _save_index(index: dict) -> None:
    """Save the student index file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def _student_file(student_id: str) -> Path:
    return DATA_DIR / f"{student_id}.json"


def create_student(display_name: str, data_dir: Path = DATA_DIR) -> Student:
    """Create a new student and save to disk."""
    student_id = _sanitize_id(display_name)
    student = Student(student_id=student_id, display_name=display_name)
    save_student(student, data_dir)

    # Update index
    index_file = data_dir / "index.json"
    index = {"students": []}
    if index_file.exists():
        with open(index_file, encoding="utf-8") as f:
            index = json.load(f)

    if student_id not in [s["student_id"] for s in index["students"]]:
        index["students"].append({
            "student_id": student_id,
            "display_name": display_name,
        })
        data_dir.mkdir(parents=True, exist_ok=True)
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    return student


def save_student(student: Student, data_dir: Path = DATA_DIR) -> None:
    """Save student data to JSON file."""
    data_dir.mkdir(parents=True, exist_ok=True)
    filepath = data_dir / f"{student.student_id}.json"
    data = {
        "student_id": student.student_id,
        "display_name": student.display_name,
        "created_at": student.created_at,
        "settings": student.settings,
        "signs": student.signs,
        "test_history": student.test_history,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_student(student_id: str, data_dir: Path = DATA_DIR) -> Student | None:
    """Load student from JSON file. Returns None if not found."""
    filepath = data_dir / f"{student_id}.json"
    if not filepath.exists():
        return None
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)
    return Student(**data)


def list_students(data_dir: Path = DATA_DIR) -> list[dict]:
    """Return list of student summaries from index."""
    index_file = data_dir / "index.json"
    if not index_file.exists():
        return []
    with open(index_file, encoding="utf-8") as f:
        index = json.load(f)
    return index.get("students", [])


def delete_student(student_id: str, data_dir: Path = DATA_DIR) -> bool:
    """Delete a student's data and remove from index."""
    filepath = data_dir / f"{student_id}.json"
    deleted = False
    if filepath.exists():
        filepath.unlink()
        deleted = True

    index_file = data_dir / "index.json"
    if index_file.exists():
        with open(index_file, encoding="utf-8") as f:
            index = json.load(f)
        index["students"] = [
            s for s in index["students"] if s["student_id"] != student_id
        ]
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    return deleted


def get_dashboard_stats(student: Student) -> DashboardStats:
    """Calculate dashboard statistics for a student."""
    total = len(get_all_signs())
    learned = sum(
        1 for s in student.signs.values()
        if s.get("status") == "learned"
    )
    today = date.today().isoformat()
    due = sum(
        1 for s in student.signs.values()
        if s.get("status") == "learned" and s.get("next_review", "") <= today
    )
    return DashboardStats(
        total_signs=total,
        learned=learned,
        remaining=total - learned,
        due_for_review=due,
    )
