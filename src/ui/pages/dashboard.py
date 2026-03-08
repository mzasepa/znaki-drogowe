"""Main dashboard page after student login."""

from nicegui import ui

from src.services.student_service import get_dashboard_stats, save_student
from src.ui import theme


def dashboard_page():
    """Render the main dashboard."""
    from src.ui.app import get_current_student

    student = get_current_student()
    if not student:
        ui.navigate.to("/")
        return

    ui.query("body").style(theme.PAGE_STYLE)
    stats = get_dashboard_stats(student)

    with ui.column().classes("w-full items-center q-pa-lg"):
        ui.label(f"Cześć, {student.display_name}!").style(theme.TITLE_STYLE)

        # Stats cards
        with ui.row().classes("q-gutter-md q-my-lg"):
            _stat_card("Nauczone", str(stats.learned), theme.SUCCESS)
            _stat_card("Pozostało", str(stats.remaining), theme.ACCENT)
            _stat_card("Do powtórki", str(stats.due_for_review), theme.PRIMARY)

        # Module buttons
        with ui.card().style(theme.CARD_STYLE).classes("w-96"):
            ui.button(
                "Nauka znaków",
                on_click=lambda: ui.navigate.to("/learning"),
            ).style(theme.BUTTON_STYLE_GREEN).classes("w-full q-mb-sm")

            ui.button(
                "Powtórki",
                on_click=lambda: ui.navigate.to("/review"),
            ).style(theme.BUTTON_STYLE_BLUE).classes("w-full q-mb-sm")

            ui.button(
                "Test",
                on_click=lambda: ui.navigate.to("/test"),
            ).style(theme.BUTTON_STYLE_ORANGE).classes("w-full q-mb-sm")

            ui.separator().classes("q-my-sm")

            ui.button(
                "Wyloguj",
                on_click=_logout,
            ).style(theme.BUTTON_STYLE_GRAY).classes("w-full")


def _stat_card(title: str, value: str, color: str):
    """Render a single stat card."""
    with ui.card().style(
        f"padding: 16px 24px; border-radius: 12px; text-align: center; "
        f"border-top: 4px solid {color}; min-width: 100px;"
    ):
        ui.label(value).style(f"font-size: 2rem; font-weight: bold; color: {color};")
        ui.label(title).style("font-size: 0.9rem; color: #666;")


def _logout():
    """Return to student selection."""
    from src.ui.app import set_current_student
    set_current_student(None)
    ui.navigate.to("/")
