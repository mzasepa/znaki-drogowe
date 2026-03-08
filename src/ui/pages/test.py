"""Test module UI - Module 3."""

from nicegui import ui

from src.models.sign_catalog import get_image_path, get_sign_by_id
from src.services.test_service import (
    create_test_session,
    record_answer,
    create_retry_session,
    save_test_result,
    TestSession,
)
from src.services.student_service import save_student
from src.ui import theme


def test_page():
    """Render the test module page."""
    from src.ui.app import get_current_student

    student = get_current_student()
    if not student:
        ui.navigate.to("/")
        return

    ui.query("body").style(theme.PAGE_STYLE)
    container = ui.column().classes("w-full items-center q-pa-lg")

    with container:
        ui.label("Test").style(theme.TITLE_STYLE)
        _show_mode_selection(student, container)


def _show_mode_selection(student, container):
    """Show test mode selection."""
    with ui.card().style(theme.CARD_STYLE).classes("w-full max-w-lg"):
        ui.label("Wybierz tryb testu:").style(
            "font-weight: bold; font-size: 1.1rem; margin-bottom: 12px;"
        )

        # Random mode
        ui.label("Losowy test:").style("font-size: 1rem; margin-bottom: 4px;")
        count_radio = ui.radio(
            {10: "10 pytań", 20: "20 pytań", 30: "30 pytań"},
            value=20,
        ).props("inline")

        ui.button(
            "Rozpocznij losowy test",
            on_click=lambda: _start_test(
                student, "random", count_radio.value, container
            ),
        ).style(theme.BUTTON_STYLE_ORANGE).classes("w-full q-mb-md")

        ui.separator().classes("q-my-md")

        # All signs mode
        ui.button(
            "Test wszystkich znaków (176)",
            on_click=lambda: _start_test(student, "all", 176, container),
        ).style(theme.BUTTON_STYLE_BLUE).classes("w-full q-mb-md")

        ui.separator().classes("q-my-md")

        ui.button(
            "Powrót",
            on_click=lambda: ui.navigate.to("/dashboard"),
        ).style(theme.BUTTON_STYLE_GRAY).classes("w-full")


def _start_test(student, mode, count, container):
    """Start a test session."""
    session = create_test_session(mode=mode, count=count)
    container.clear()
    with container:
        ui.label("Test").style(theme.TITLE_STYLE)
        _show_question(student, session, mode, container)


def _show_question(student, session: TestSession, mode, container):
    """Show the current question."""
    question = session.current_question
    if question is None:
        # Check for retry
        if session.wrong_answers:
            _show_retry_prompt(student, session, mode, container)
        else:
            _show_final_summary(student, session, mode, container)
        return

    card = ui.card().style(theme.CARD_STYLE).classes("w-full max-w-2xl")

    with card:
        # Progress
        ui.label(
            f"Pytanie {session.current_index + 1} z {session.total}"
        ).style("font-size: 0.9rem; color: #666;")
        progress = session.current_index / session.total
        ui.linear_progress(value=progress).classes("w-full q-mb-md")

        if question.question_type == 1:
            _render_type1(student, session, question, mode, container, card)
        else:
            _render_type2(student, session, question, mode, container, card)


def _render_type1(student, session, question, mode, container, card):
    """Type 1: Show image, pick text answer."""
    img_path = get_image_path(question.sign)
    ui.image(str(img_path)).classes("w-64 q-my-md").style(
        "margin: 0 auto; display: block;"
    )
    ui.label("Jak nazywa się ten znak?").style(
        "font-size: 1.1rem; text-align: center; margin-bottom: 12px;"
    )

    with ui.column().classes("w-full q-gutter-sm"):
        buttons = []
        for i, option in enumerate(question.options):
            btn = ui.button(
                option,
                on_click=lambda _, idx=i: _handle_answer(
                    student, session, idx, mode, container, card, buttons
                ),
            ).classes("w-full").style(
                "font-size: 1rem; text-align: left; justify-content: flex-start;"
            )
            buttons.append(btn)


def _render_type2(student, session, question, mode, container, card):
    """Type 2: Show name, pick image answer."""
    ui.label(question.sign.name).style(
        "font-size: 1.5rem; font-weight: bold; text-align: center; "
        "margin-bottom: 16px;"
    )
    ui.label("Wskaż poprawny znak:").style(
        "font-size: 1.1rem; text-align: center; margin-bottom: 12px;"
    )

    with ui.grid(columns=2).classes("w-full q-gutter-sm").style(
        "justify-items: center;"
    ):
        buttons = []
        for i, sign_id in enumerate(question.options):
            sign = get_sign_by_id(sign_id)
            if sign:
                img_path = get_image_path(sign)
                with ui.card().style(
                    "padding: 8px; cursor: pointer; border-radius: 12px;"
                ) as img_card:
                    ui.image(str(img_path)).classes("w-32")
                    img_card.on(
                        "click",
                        lambda _, idx=i: _handle_answer(
                            student, session, idx, mode, container, card, buttons
                        ),
                    )
                    buttons.append(img_card)


def _handle_answer(student, session, chosen_idx, mode, container, card, buttons):
    """Handle an answer selection with visual feedback."""
    question = session.current_question
    if question is None:
        return

    correct = record_answer(session, chosen_idx)

    # Visual feedback
    if question.question_type == 1:
        for i, btn in enumerate(buttons):
            if i == question.correct_index:
                btn.style(add="background-color: #27AE60 !important; color: white !important;")
            elif i == chosen_idx and not correct:
                btn.style(add="background-color: #E74C3C !important; color: white !important;")
            btn.disable()
    else:
        for i, btn in enumerate(buttons):
            if i == question.correct_index:
                btn.style(add="border: 3px solid #27AE60;")
            elif i == chosen_idx and not correct:
                btn.style(add="border: 3px solid #E74C3C;")

    # Pause then next question
    delay = 0.5 if correct else 2.0
    ui.timer(
        delay,
        lambda: (card.delete(), _show_question(student, session, mode, container)),
        once=True,
    )


def _show_retry_prompt(student, session, mode, container):
    """Offer retry for wrong answers."""
    with ui.card().style(theme.CARD_STYLE).classes("w-full max-w-lg"):
        wrong_count = len(session.wrong_answers)
        ui.label(f"Masz {wrong_count} błędnych odpowiedzi.").style(
            "font-size: 1.2rem; text-align: center; margin-bottom: 8px;"
        )
        ui.label("Spróbuj jeszcze raz!").style(
            "font-size: 1.1rem; text-align: center; color: #666; "
            "margin-bottom: 16px;"
        )

        def start_retry():
            retry = create_retry_session(session.wrong_answers)
            if retry:
                container.clear()
                with container:
                    ui.label("Dogrywka").style(theme.TITLE_STYLE)
                    _show_question(student, retry, mode, container)

        ui.button(
            "Powtórz błędne pytania",
            on_click=start_retry,
        ).style(theme.BUTTON_STYLE_ORANGE).classes("w-full q-mb-sm")

        ui.button(
            "Zakończ test",
            on_click=lambda: _show_final_summary(
                student, session, mode, container
            ),
        ).style(theme.BUTTON_STYLE_GRAY).classes("w-full")


def _show_final_summary(student, session, mode, container):
    """Show final test summary."""
    save_test_result(student, session, mode)
    save_student(student)

    total = session.total
    correct = session.correct_count
    pct = int(correct / total * 100) if total > 0 else 0

    with ui.card().style(theme.CARD_STYLE).classes("w-full max-w-lg"):
        color = "#27AE60" if pct >= 80 else "#F5A623" if pct >= 50 else "#E74C3C"
        ui.label("Test zakończony!").style(
            f"font-size: 1.5rem; font-weight: bold; color: {color}; "
            "text-align: center;"
        )
        ui.label(f"Wynik: {correct}/{total} ({pct}%)").style(
            "font-size: 1.3rem; text-align: center; margin: 12px 0;"
        )

        if session.wrong_answers:
            ui.separator().classes("q-my-md")
            ui.label("Błędne odpowiedzi:").style(
                "font-weight: bold; font-size: 1rem; margin-bottom: 8px;"
            )
            for wa in session.wrong_answers:
                sign = get_sign_by_id(wa["sign_id"])
                if sign:
                    with ui.row().classes("items-center q-mb-sm"):
                        img_path = get_image_path(sign)
                        ui.image(str(img_path)).classes("w-16")
                        with ui.column():
                            ui.label(f"Twoja: {wa['chosen_answer']}").style(
                                "color: #E74C3C; font-size: 0.9rem;"
                            )
                            ui.label(f"Poprawna: {wa['correct_answer']}").style(
                                "color: #27AE60; font-size: 0.9rem;"
                            )

        ui.separator().classes("q-my-md")
        ui.button(
            "Powrót do menu",
            on_click=lambda: ui.navigate.to("/dashboard"),
        ).style(theme.BUTTON_STYLE_BLUE).classes("w-full")
