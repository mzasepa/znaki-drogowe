"""NiceGUI application setup and routing."""

from nicegui import app, ui

from src.models.student import Student


# Per-session student storage
_current_students: dict[str, Student | None] = {}


def _session_id() -> str:
    """Get the current client's storage ID."""
    return app.storage.browser.get("session_id", "default")


def set_current_student(student: Student | None) -> None:
    """Set the current student for this session."""
    _current_students[_session_id()] = student


def get_current_student() -> Student | None:
    """Get the current student for this session."""
    return _current_students.get(_session_id())


def init_app():
    """Initialize the NiceGUI app with all routes."""
    from src.ui.pages.student_select import student_select_page
    from src.ui.pages.dashboard import dashboard_page

    @ui.page("/")
    def index():
        student_select_page()

    @ui.page("/dashboard")
    def dashboard():
        dashboard_page()

    from src.ui.pages.learning import learning_page
    from src.ui.pages.review import review_page
    from src.ui.pages.test import test_page

    @ui.page("/learning")
    def learning():
        learning_page()

    @ui.page("/review")
    def review():
        review_page()

    @ui.page("/test")
    def test():
        test_page()
