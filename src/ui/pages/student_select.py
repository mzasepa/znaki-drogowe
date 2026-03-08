"""Student selection and creation page."""

from nicegui import ui

from src.services.student_service import create_student, list_students, load_student
from src.ui import theme


def student_select_page():
    """Render the student selection page."""
    ui.query("body").style(theme.PAGE_STYLE)

    with ui.column().classes("w-full items-center q-pa-lg"):
        ui.label("Znaki Drogowe").style(theme.TITLE_STYLE)
        ui.label("Wybierz ucznia lub dodaj nowego").style(
            "font-size: 1.2rem; color: #666; margin-bottom: 20px;"
        )

        students = list_students()

        with ui.card().style(theme.CARD_STYLE).classes("w-96"):
            if students:
                ui.label("Istniejący uczniowie:").style(
                    "font-weight: bold; font-size: 1.1rem; margin-bottom: 8px;"
                )
                for s in students:
                    ui.button(
                        s["display_name"],
                        on_click=lambda _, sid=s["student_id"]: _select_student(sid),
                    ).props("flat").classes("w-full").style(
                        "font-size: 1.1rem; justify-content: flex-start;"
                    )
                ui.separator().classes("q-my-md")

            ui.label("Nowy uczeń:").style(
                "font-weight: bold; font-size: 1.1rem; margin-bottom: 8px;"
            )
            name_input = ui.input(
                "Imię i nazwisko",
                validation={"Wpisz imię": lambda v: len(v.strip()) > 0},
            ).classes("w-full")

            ui.button(
                "Dodaj ucznia",
                on_click=lambda: _add_student(name_input.value),
            ).style(theme.BUTTON_STYLE_BLUE).classes("w-full q-mt-sm")


def _select_student(student_id: str):
    """Navigate to dashboard for selected student."""
    from src.ui.app import set_current_student
    student = load_student(student_id)
    if student:
        set_current_student(student)
        ui.navigate.to("/dashboard")


def _add_student(name: str):
    """Create a new student and navigate to dashboard."""
    if not name or not name.strip():
        ui.notify("Wpisz imię ucznia!", type="warning")
        return
    from src.ui.app import set_current_student
    student = create_student(name.strip())
    set_current_student(student)
    ui.navigate.to("/dashboard")
