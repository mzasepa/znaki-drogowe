"""Review module UI - Module 2."""

from nicegui import ui

from src.models.sign_catalog import get_image_path, get_sign_by_id
from src.services.repetition_service import (
    create_review_session,
    record_review_result,
    ReviewSession,
)
from src.services.student_service import save_student
from src.ui import theme


def review_page():
    """Render the review module page."""
    from src.ui.app import get_current_student

    student = get_current_student()
    if not student:
        ui.navigate.to("/")
        return

    ui.query("body").style(theme.PAGE_STYLE)
    container = ui.column().classes("w-full items-center q-pa-lg")

    with container:
        ui.label("Powtórki").style(theme.TITLE_STYLE)
        session = create_review_session(student)

        if session.total == 0:
            _show_empty_state(container)
        else:
            _show_review_card(student, session, container)


def _show_empty_state(container):
    """Show message when no signs are due for review."""
    with ui.card().style(theme.CARD_STYLE).classes("w-full max-w-lg"):
        ui.label("Nie masz znaków do powtórzenia.").style(
            "font-size: 1.3rem; font-weight: bold; text-align: center; "
            "margin-bottom: 8px;"
        )
        ui.label("Wróć jutro!").style(
            "font-size: 1.1rem; text-align: center; color: #666; "
            "margin-bottom: 16px;"
        )
        ui.button(
            "Powrót do menu",
            on_click=lambda: ui.navigate.to("/dashboard"),
        ).style(theme.BUTTON_STYLE_BLUE).classes("w-full")


def _show_review_card(student, session: ReviewSession, container):
    """Show the current review card."""
    sign = session.current_sign
    if sign is None:
        _show_summary(student, session, container)
        return

    card_container = ui.card().style(theme.CARD_STYLE).classes("w-full max-w-lg")

    with card_container:
        # Progress
        progress = session.current_index / session.total
        pct = round(progress * 100)
        ui.label(
            f"Znak {session.current_index + 1} z {session.total} ({pct}%)"
        ).style("font-size: 0.9rem; color: #666;")
        with ui.linear_progress(value=progress, show_value=False, size="20px").classes("w-full"):
            ui.label(f"{pct}%").classes("absolute-center text-sm text-white")

        # Sign image
        img_path = get_image_path(sign)
        ui.image(str(img_path)).classes("w-64 q-my-md").style(
            "margin: 0 auto; display: block;"
        )

        # Name (hidden)
        name_label = ui.label(sign.name).style(
            "font-size: 1.3rem; font-weight: bold; text-align: center; "
            "padding: 12px; background: #FFEBEE; border-radius: 8px; "
            "margin-bottom: 12px;"
        )
        name_label.set_visibility(False)

        countdown_label = ui.label("").style(
            "font-size: 0.9rem; color: #666; text-align: center;"
        )
        countdown_label.set_visibility(False)

        # Buttons
        btn_row = ui.row().classes("w-full justify-center q-gutter-sm")
        with btn_row:
            ui.button(
                "Znam",
                on_click=lambda: _on_correct(
                    student, sign.sign_id, session, container, card_container
                ),
            ).style(theme.BUTTON_STYLE_GREEN)

            ui.button(
                "Nie znam",
                on_click=lambda: _on_incorrect(
                    student, sign.sign_id, session, container,
                    card_container, name_label, countdown_label, btn_row
                ),
            ).style(theme.BUTTON_STYLE_RED)


def _on_correct(student, sign_id, session, container, card_container):
    record_review_result(student, sign_id, correct=True)
    session.correct.append(sign_id)
    session.current_index += 1
    save_student(student)
    _advance_to_next(card_container, container, student, session)


def _on_incorrect(student, sign_id, session, container,
                  card_container, name_label, countdown_label, btn_row):
    record_review_result(student, sign_id, correct=False)
    session.incorrect.append(sign_id)
    session.current_index += 1
    save_student(student)

    name_label.set_visibility(True)
    countdown_label.set_visibility(True)
    btn_row.set_visibility(False)

    _countdown(5, countdown_label, lambda: _advance_to_next(
        card_container, container, student, session
    ))


def _advance_to_next(card_container, container, student, session):
    """Delete the current card and show the next one within the container context."""
    card_container.delete()
    with container:
        _show_review_card(student, session, container)


def _countdown(seconds, label, on_done):
    label.text = f"Następny znak za {seconds}s..."
    if seconds <= 0:
        on_done()
        return
    ui.timer(1.0, lambda: _countdown(seconds - 1, label, on_done), once=True)


def _show_summary(student, session, container):
    """Show review session summary."""
    save_student(student)
    correct = len(session.correct)
    incorrect = len(session.incorrect)

    with ui.card().style(theme.CARD_STYLE).classes("w-full max-w-lg"):
        ui.label("Powtórka zakończona!").style(
            "font-size: 1.5rem; font-weight: bold; color: #27AE60; "
            "text-align: center;"
        )
        ui.label(
            f"Powtórzyłeś {session.total} znaków."
        ).style("font-size: 1.1rem; text-align: center; margin: 8px 0;")
        ui.label(
            f"Poprawne: {correct}. Do poprawy: {incorrect}."
        ).style("font-size: 1.1rem; text-align: center; margin-bottom: 16px;")

        ui.button(
            "Powrót do menu",
            on_click=lambda: ui.navigate.to("/dashboard"),
        ).style(theme.BUTTON_STYLE_BLUE).classes("w-full")
