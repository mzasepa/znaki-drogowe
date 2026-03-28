"""Spaced repetition engine - simplified SM-2 for children."""

import random
from dataclasses import dataclass, field
from datetime import date, timedelta

from src.models.student import Student
from src.models.sign_catalog import get_sign_by_id, Sign


MAX_DAILY_REVIEWS = 30
INITIAL_INTERVALS = {1: 1, 2: 3, 3: 7, 4: 14}
MAX_INTERVAL = 30
MIN_EASE = 1.3
MAX_EASE = 3.0


@dataclass
class ReviewSession:
    signs: list[Sign]
    current_index: int = 0
    correct: list[str] = field(default_factory=list)
    incorrect: list[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return self.current_index >= len(self.signs)

    @property
    def current_sign(self) -> Sign | None:
        if self.current_index < len(self.signs):
            return self.signs[self.current_index]
        return None

    @property
    def total(self) -> int:
        return len(self.signs)


def get_signs_due_for_review(student: Student) -> list[str]:
    """Return sign IDs that are due for review (next_review <= today)."""
    today = date.today().isoformat()
    due = []
    for sign_id, data in student.signs.items():
        if (data.get("status") == "learned"
                and data.get("next_review", "") <= today):
            due.append(sign_id)
    return due


def create_review_session(student: Student) -> ReviewSession:
    """Create a review session from due signs, limited to MAX_DAILY_REVIEWS."""
    due_ids = get_signs_due_for_review(student)
    due_ids = due_ids[:MAX_DAILY_REVIEWS]
    signs = []
    for sid in due_ids:
        sign = get_sign_by_id(sid)
        if sign:
            signs.append(sign)
    random.shuffle(signs)
    return ReviewSession(signs=signs)


def calculate_next_review(sign_data: dict, correct: bool) -> dict:
    """Calculate updated review schedule based on answer correctness.

    Returns updated sign_data dict.
    """
    data = dict(sign_data)

    if correct:
        data["consecutive_correct"] = data.get("consecutive_correct", 0) + 1
        n = data["consecutive_correct"]

        if n in INITIAL_INTERVALS:
            data["interval_days"] = INITIAL_INTERVALS[n]
        else:
            ease = data.get("ease_factor", 2.5)
            prev_interval = data.get("interval_days", 14)
            data["interval_days"] = min(
                int(prev_interval * ease), MAX_INTERVAL
            )

        # Increase ease factor
        ease = data.get("ease_factor", 2.5) + 0.1
        data["ease_factor"] = min(ease, MAX_EASE)
    else:
        # Wrong answer: reset
        data["consecutive_correct"] = 0
        data["interval_days"] = 1
        ease = data.get("ease_factor", 2.5) - 0.2
        data["ease_factor"] = max(ease, MIN_EASE)

    today = date.today()
    data["next_review"] = (today + timedelta(days=data["interval_days"])).isoformat()

    return data


def record_review_result(student: Student, sign_id: str, correct: bool) -> None:
    """Record a review result and update the student's sign data."""
    if sign_id not in student.signs:
        return

    today = date.today().isoformat()
    data = student.signs[sign_id]
    data.setdefault("review_history", [])
    data["review_history"].append({"date": today, "correct": correct})

    updated = calculate_next_review(data, correct)
    student.signs[sign_id] = updated
