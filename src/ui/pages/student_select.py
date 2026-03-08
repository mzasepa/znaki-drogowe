"""Student selection and creation page."""

from nicegui import ui

from src.services.student_service import (
    create_student,
    delete_student,
    list_students,
    load_student,
    rename_student,
)
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
                    with ui.row().classes("w-full items-center no-wrap"):
                        ui.button(
                            s["display_name"],
                            on_click=lambda _, sid=s["student_id"]: _select_student(sid),
                        ).props("flat").classes("flex-grow").style(
                            "font-size: 1.1rem; justify-content: flex-start;"
                        )
                        ui.button(
                            icon="edit",
                            on_click=lambda _, sid=s["student_id"], name=s["display_name"]: _show_rename_dialog(sid, name),
                        ).props("flat round dense").style("color: #4A90D9;")
                        ui.button(
                            icon="delete",
                            on_click=lambda _, sid=s["student_id"], name=s["display_name"]: _show_delete_dialog(sid, name),
                        ).props("flat round dense").style("color: #E74C3C;")
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


def _show_rename_dialog(student_id: str, current_name: str):
    """Show a dialog to rename a student."""
    with ui.dialog() as dialog, ui.card().style("min-width: 300px;"):
        ui.label("Zmień imię ucznia").style(
            "font-weight: bold; font-size: 1.1rem; margin-bottom: 8px;"
        )
        name_input = ui.input("Nowe imię", value=current_name).classes("w-full")

        with ui.row().classes("w-full justify-end q-mt-md"):
            ui.button("Anuluj", on_click=dialog.close).props("flat")
            ui.button(
                "Zapisz",
                on_click=lambda: _do_rename(dialog, student_id, name_input.value),
            ).style(theme.BUTTON_STYLE_BLUE)

    dialog.open()


def _do_rename(dialog, student_id: str, new_name: str):
    """Perform the rename and refresh the page."""
    if not new_name or not new_name.strip():
        ui.notify("Wpisz imię ucznia!", type="warning")
        return
    rename_student(student_id, new_name.strip())
    dialog.close()
    ui.navigate.to("/")


def _show_delete_dialog(student_id: str, display_name: str):
    """Show a confirmation dialog before deleting a student."""
    with ui.dialog() as dialog, ui.card().style("min-width: 300px;"):
        ui.label("Usunąć ucznia?").style(
            "font-weight: bold; font-size: 1.1rem; margin-bottom: 8px;"
        )
        ui.label(f"Czy na pewno chcesz usunąć ucznia {display_name}? "
                 "Wszystkie postępy zostaną utracone.")

        with ui.row().classes("w-full justify-end q-mt-md"):
            ui.button("Anuluj", on_click=dialog.close).props("flat")
            ui.button(
                "Usuń",
                on_click=lambda: _do_delete(dialog, student_id),
            ).style(theme.BUTTON_STYLE_RED)

    dialog.open()


def _do_delete(dialog, student_id: str):
    """Perform the deletion and refresh the page."""
    delete_student(student_id)
    dialog.close()
    ui.navigate.to("/")
