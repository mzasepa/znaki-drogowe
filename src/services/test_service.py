"""Test module logic - Module 3."""

import random
from dataclasses import dataclass, field
from datetime import datetime

from src.models.student import Student
from src.models.sign_catalog import (
    Sign, get_all_signs, get_signs_by_category, get_sign_by_id,
)


@dataclass
class Question:
    sign: Sign
    question_type: int  # 1 = image->text, 2 = text->images
    correct_answer: str  # sign name or sign_id
    options: list[str]  # 4 options (names for type 1, sign_ids for type 2)
    correct_index: int  # position of correct answer (0-3)


@dataclass
class TestSession:
    questions: list[Question]
    current_index: int = 0
    answers: list[bool] = field(default_factory=list)
    wrong_answers: list[dict] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return self.current_index >= len(self.questions)

    @property
    def current_question(self) -> Question | None:
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    @property
    def total(self) -> int:
        return len(self.questions)

    @property
    def correct_count(self) -> int:
        return sum(self.answers)


def _get_distractors(sign: Sign, count: int = 3) -> list[Sign]:
    """Get distractor signs from the same category. Fall back to others if needed."""
    same_cat = [s for s in get_signs_by_category(sign.category) if s.sign_id != sign.sign_id]
    if len(same_cat) >= count:
        return random.sample(same_cat, count)
    # Not enough in category - supplement from other categories
    others = [s for s in get_all_signs() if s.sign_id != sign.sign_id and s.category != sign.category]
    needed = count - len(same_cat)
    return same_cat + random.sample(others, min(needed, len(others)))


def generate_question(sign: Sign, question_type: int | None = None) -> Question:
    """Generate a question for a given sign."""
    if question_type is None:
        question_type = random.choice([1, 2])

    distractors = _get_distractors(sign, 3)
    correct_index = random.randint(0, 3)

    if question_type == 1:
        # Image shown, pick text answer
        options = [d.name for d in distractors]
        options.insert(correct_index, sign.name)
        return Question(
            sign=sign,
            question_type=1,
            correct_answer=sign.name,
            options=options,
            correct_index=correct_index,
        )
    else:
        # Text shown, pick image answer
        options = [d.sign_id for d in distractors]
        options.insert(correct_index, sign.sign_id)
        return Question(
            sign=sign,
            question_type=2,
            correct_answer=sign.sign_id,
            options=options,
            correct_index=correct_index,
        )


def create_test_session(
    mode: str = "random", count: int = 20
) -> TestSession:
    """Create a test session.

    mode: "random" (pick count signs) or "all" (all 176 signs)
    count: number of signs for random mode (10, 20, or 30)
    """
    all_signs = get_all_signs()
    if mode == "all":
        selected = list(all_signs)
    else:
        selected = random.sample(all_signs, min(count, len(all_signs)))

    random.shuffle(selected)
    questions = [generate_question(s) for s in selected]
    return TestSession(questions=questions)


def record_answer(session: TestSession, chosen_index: int) -> bool:
    """Record an answer. Returns True if correct."""
    q = session.current_question
    if q is None:
        return False

    correct = chosen_index == q.correct_index
    session.answers.append(correct)

    if not correct:
        chosen_text = q.options[chosen_index] if chosen_index < len(q.options) else ""
        session.wrong_answers.append({
            "sign_id": q.sign.sign_id,
            "question_type": q.question_type,
            "chosen_answer": chosen_text,
            "correct_answer": q.correct_answer,
        })

    session.current_index += 1
    return correct


def create_retry_session(wrong_answers: list[dict]) -> TestSession | None:
    """Create a retry session from wrong answers."""
    if not wrong_answers:
        return None
    signs = []
    for wa in wrong_answers:
        sign = get_sign_by_id(wa["sign_id"])
        if sign:
            signs.append(sign)
    if not signs:
        return None
    random.shuffle(signs)
    questions = [generate_question(s) for s in signs]
    return TestSession(questions=questions)


def save_test_result(student: Student, session: TestSession, mode: str) -> None:
    """Save test results to student history."""
    result = {
        "date": datetime.now().isoformat(timespec="seconds"),
        "mode": mode,
        "total_questions": session.total,
        "correct_answers": session.correct_count,
        "wrong_answers": list(session.wrong_answers),
    }
    student.test_history.append(result)
