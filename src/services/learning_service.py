"""Learning module logic - Module 1."""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta

from src.models.student import Student
from src.models.sign_catalog import get_signs_by_category, Sign


@dataclass
class LearningSession:
    signs: list[Sign]
    current_index: int = 0
    learned_in_session: list[str] = field(default_factory=list)
    not_learned: list[Sign] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return self.current_index >= len(self.signs) and not self.not_learned

    @property
    def current_sign(self) -> Sign | None:
        if self.current_index < len(self.signs):
            return self.signs[self.current_index]
        return None

    @property
    def total(self) -> int:
        return len(self.signs)

    @property
    def progress(self) -> int:
        return min(self.current_index, len(self.signs))


def get_unlearned_signs(student: Student, category: str) -> list[Sign]:
    """Return signs in a category that the student hasn't learned yet."""
    all_in_cat = get_signs_by_category(category)
    return [s for s in all_in_cat if s.sign_id not in student.signs
            or student.signs[s.sign_id].get("status") != "learned"]


def create_learning_session(
    student: Student, category: str, batch_size: int | None = None
) -> LearningSession:
    """Create a learning session with unlearned signs from a category."""
    if batch_size is None:
        batch_size = student.settings.get("signs_per_session", 10)
    unlearned = get_unlearned_signs(student, category)
    signs = unlearned[:batch_size]
    return LearningSession(signs=signs)


def mark_sign_known(student: Student, sign_id: str, session: LearningSession) -> None:
    """Mark a sign as known/learned and advance session."""
    now = datetime.now().isoformat(timespec="seconds")
    today = date.today()

    if sign_id not in student.signs:
        student.signs[sign_id] = {
            "status": "learned",
            "first_seen": now,
            "learned_at": now,
            "review_history": [],
            "next_review": (today + timedelta(days=1)).isoformat(),
            "interval_days": 1,
            "ease_factor": 2.5,
            "consecutive_correct": 0,
        }
    else:
        student.signs[sign_id]["status"] = "learned"
        student.signs[sign_id]["learned_at"] = now
        student.signs[sign_id]["next_review"] = (today + timedelta(days=1)).isoformat()
        student.signs[sign_id]["interval_days"] = 1

    session.learned_in_session.append(sign_id)
    session.current_index += 1


def mark_sign_unknown(student: Student, sign_id: str, session: LearningSession) -> None:
    """Mark a sign as not known - it goes to retry queue."""
    now = datetime.now().isoformat(timespec="seconds")
    if sign_id not in student.signs:
        student.signs[sign_id] = {
            "status": "learning",
            "first_seen": now,
            "learned_at": None,
            "review_history": [],
            "next_review": None,
            "interval_days": 0,
            "ease_factor": 2.5,
            "consecutive_correct": 0,
        }

    current = session.current_sign
    if current:
        session.not_learned.append(current)
    session.current_index += 1


def advance_to_retry(session: LearningSession) -> None:
    """When all signs are shown, move not_learned back to the queue for retry."""
    if session.current_index >= len(session.signs) and session.not_learned:
        session.signs = list(session.not_learned)
        session.not_learned = []
        session.current_index = 0
