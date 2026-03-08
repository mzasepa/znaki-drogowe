"""Student data model and related dataclasses."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SignProgress:
    status: str = "unseen"  # "unseen", "learning", "learned"
    first_seen: str | None = None
    learned_at: str | None = None
    review_history: list[dict] = field(default_factory=list)
    next_review: str | None = None
    interval_days: int = 0
    ease_factor: float = 2.5
    consecutive_correct: int = 0


@dataclass
class WrongAnswer:
    sign_id: str
    question_type: int
    chosen_answer: str
    correct_answer: str


@dataclass
class TestResult:
    date: str
    mode: str
    total_questions: int
    correct_answers: int
    wrong_answers: list[dict] = field(default_factory=list)


@dataclass
class Student:
    student_id: str
    display_name: str
    created_at: str = ""
    settings: dict = field(default_factory=lambda: {"signs_per_session": 10})
    signs: dict = field(default_factory=dict)  # sign_id -> dict
    test_history: list[dict] = field(default_factory=list)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat(timespec="seconds")


@dataclass
class DashboardStats:
    total_signs: int
    learned: int
    remaining: int
    due_for_review: int
