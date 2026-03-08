# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Polish educational app for teaching road signs required for the bicycle license exam ("karta rowerowa"). Built with NiceGUI (Python web framework), targeting children aged 10-12. All UI text is in Polish; code descriptions are in English.

## Commands

```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run app (opens browser at http://localhost:8080)
python main.py

# Run all tests
python -m pytest tests/ -v

# Run a single test file
python -m pytest tests/test_sign_catalog.py -v

# Run a single test
python -m pytest tests/test_sign_catalog.py::test_function_name -v
```

## Architecture

**Three-module structure** matching the learning flow:
- **Module 1 (Learning)**: Flashcard-style sign learning by category. Unknown signs repeat at end of series.
- **Module 2 (Review)**: Spaced repetition using simplified SM-2 algorithm (see `repetition_service.py` constants: `INITIAL_INTERVALS`, `MIN_EASE`, `MAX_EASE`, `MAX_INTERVAL`).
- **Module 3 (Test)**: Quiz with two question types (image→name, name→image) and wrong-answer replays.

**Layer separation**:
- `src/models/` — Data classes (`Student`, `Sign`, `SignProgress`, `TestResult`) and sign catalog (loads from `znaki/nazwy_znakow.csv`, semicolon-delimited)
- `src/services/` — Business logic per module: `learning_service`, `repetition_service`, `test_service`, plus `student_service` for CRUD
- `src/ui/pages/` — NiceGUI page components. Routes defined in `src/ui/app.py`: `/` (student select), `/dashboard`, `/learning`, `/review`, `/test`
- `src/ui/app.py` — Per-session student state via `_current_students` dict keyed by browser session ID

**Data storage**: Student progress stored as JSON files in `data/students/` (gitignored). An `index.json` maps student IDs to display names.

**Sign assets**: `znaki/` directory contains PNG images organized by category subdirectories (Ostrzegawcze, Zakazu, Nakazu, Informacyjne, Kierunku, Uzupelniajace) and a master CSV (`znaki/nazwy_znakow.csv`) with columns: category, filename, name.

**Sign catalog caching**: `sign_catalog.py` uses a module-level `_signs_cache`. Call `reload_signs()` in tests to reset it.

## Conventions

- Each feature should be introduced as a separate PR before starting the next one
- TDD approach — write tests first
- Tests use `tmp_path` fixtures for isolated student data (see `tests/conftest.py`)
- `pytest-asyncio` is available for async test needs
