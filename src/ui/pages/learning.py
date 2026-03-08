"""Learning module UI - Module 1."""

from nicegui import ui

from src.models.sign_catalog import get_categories, get_image_path
from src.services.learning_service import (
    create_learning_session,
    mark_sign_known,
    mark_sign_unknown,
    advance_to_retry,
    get_unlearned_signs,
    LearningSession,
)
from src.services.student_service import save_student
from src.ui import theme


def learning_page():
    """Render the learning module page."""
    from src.ui.app import get_current_student

    student = get_current_student()
    if not student:
        ui.navigate.to("/")
        return

    ui.query("body").style(theme.PAGE_STYLE)
    container = ui.column().classes("w-full items-center q-pa-lg")

    with container:
        ui.label("Nauka znaków").style(theme.TITLE_STYLE)
        _show_category_selection(student, container)


def _show_category_selection(student, container):
    """Show category selection grid."""
    categories = get_categories()

    with ui.card().style(theme.CARD_STYLE).classes("w-full max-w-2xl"):
        ui.label("Wybierz kategorię znaków:").style(
            "font-weight: bold; font-size: 1.1rem; margin-bottom: 12px;"
        )

        with ui.column().classes("w-full q-gutter-sm"):
            for cat in categories:
                unlearned = get_unlearned_signs(student, cat)
                count = len(unlearned)
                label = cat.replace("_", " ")
                btn = ui.button(
                    f"{label} ({count} do nauki)",
                    on_click=lambda _, c=cat, cont=container: _start_learning(
                        student, c, cont
                    ),
                ).classes("w-full").style(
                    "font-size: 1rem; justify-content: flex-start;"
                )
                if count == 0:
                    btn.disable()

        ui.separator().classes("q-my-md")

        # Settings
        with ui.row().classes("items-center"):
            ui.label("Znaków w serii:").style("font-size: 1rem;")
            signs_input = ui.number(
                value=student.settings.get("signs_per_session", 10),
                min=1, max=50, step=1,
            ).style("width: 80px;")
            ui.button(
                "Zapisz",
                on_click=lambda: _save_settings(student, int(signs_input.value)),
            ).props("flat size=sm")

        ui.separator().classes("q-my-md")
        ui.button(
            "Powrót",
            on_click=lambda: ui.navigate.to("/dashboard"),
        ).style(theme.BUTTON_STYLE_GRAY)


def _save_settings(student, count):
    student.settings["signs_per_session"] = count
    save_student(student)
    ui.notify(f"Zapisano: {count} znaków w serii", type="positive")


def _start_learning(student, category, container):
    """Start a learning session for a category."""
    session = create_learning_session(student, category)
    if not session.signs:
        ui.notify("Brak znaków do nauki w tej kategorii!", type="info")
        return
    container.clear()
    with container:
        ui.label("Nauka znaków").style(theme.TITLE_STYLE)
        _show_learning_card(student, session, category, container)


def _show_learning_card(student, session: LearningSession, category, container):
    """Show the current sign learning card."""
    sign = session.current_sign
    if sign is None:
        advance_to_retry(session)
        if session.is_complete:
            _show_summary(student, session, container)
            return
        sign = session.current_sign

    card_container = ui.card().style(theme.CARD_STYLE).classes("w-full max-w-lg")

    with card_container:
        # Progress bar
        progress = session.progress / session.total if session.total else 0
        ui.label(
            f"Znak {session.progress + 1} z {session.total}"
        ).style("font-size: 0.9rem; color: #666;")
        ui.linear_progress(value=progress).classes("w-full")

        # Sign image
        img_path = get_image_path(sign)
        ui.image(str(img_path)).classes("w-64 q-my-md").style(
            "margin: 0 auto; display: block;"
        )

        # Name overlay (hidden initially)
        name_label = ui.label(sign.name).style(
            "font-size: 1.3rem; font-weight: bold; text-align: center; "
            "padding: 12px; background: #E3F2FD; border-radius: 8px; "
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
                "Znam ten znak",
                on_click=lambda: _on_known(
                    student, sign.sign_id, session, category, container, card_container
                ),
            ).style(theme.BUTTON_STYLE_GREEN)

            ui.button(
                "Nie znam",
                on_click=lambda: _on_unknown(
                    student, sign.sign_id, session, category, container,
                    card_container, name_label, countdown_label, btn_row
                ),
            ).style(theme.BUTTON_STYLE_RED)

            ui.button(
                "Pokaż nazwę",
                on_click=lambda: _on_show_name(
                    student, sign.sign_id, session, category, container,
                    card_container, name_label, countdown_label, btn_row
                ),
            ).style(theme.BUTTON_STYLE_BLUE)


def _on_known(student, sign_id, session, category, container, card_container):
    mark_sign_known(student, sign_id, session)
    save_student(student)
    card_container.delete()
    with container:
        _show_learning_card(student, session, category, container)


def _on_unknown(student, sign_id, session, category, container,
                card_container, name_label, countdown_label, btn_row):
    mark_sign_unknown(student, sign_id, session)
    save_student(student)
    name_label.set_visibility(True)
    countdown_label.set_visibility(True)
    btn_row.set_visibility(False)

    _countdown(5, countdown_label, lambda: _advance_to_next(
        card_container, container, student, session, category
    ))


def _on_show_name(student, sign_id, session, category, container,
                  card_container, name_label, countdown_label, btn_row):
    # Treat "show name" same as "don't know"
    mark_sign_unknown(student, sign_id, session)
    save_student(student)
    name_label.set_visibility(True)
    countdown_label.set_visibility(True)
    btn_row.set_visibility(False)

    _countdown(5, countdown_label, lambda: _advance_to_next(
        card_container, container, student, session, category
    ))


def _advance_to_next(card_container, container, student, session, category):
    """Delete the current card and show the next one within the container context."""
    card_container.delete()
    with container:
        _show_learning_card(student, session, category, container)


def _countdown(seconds, label, on_done):
    """Show a countdown timer, then call on_done."""
    label.text = f"Następny znak za {seconds}s..."
    if seconds <= 0:
        on_done()
        return
    ui.timer(1.0, lambda: _countdown(seconds - 1, label, on_done), once=True)


def _show_summary(student, session, container):
    """Show session summary."""
    save_student(student)
    with ui.card().style(theme.CARD_STYLE).classes("w-full max-w-lg"):
        ui.label("Sesja zakończona!").style(
            "font-size: 1.5rem; font-weight: bold; color: #27AE60; "
            "text-align: center;"
        )
        ui.label(
            f"Nauczyłeś się {len(session.learned_in_session)} znaków w tej sesji."
        ).style("font-size: 1.1rem; text-align: center; margin: 12px 0;")

        ui.button(
            "Powrót do menu",
            on_click=lambda: ui.navigate.to("/dashboard"),
        ).style(theme.BUTTON_STYLE_BLUE).classes("w-full")
