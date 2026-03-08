"""Road sign catalog - loads and queries signs from CSV data."""

import csv
from dataclasses import dataclass
from pathlib import Path


SIGNS_DIR = Path(__file__).resolve().parent.parent.parent / "znaki"
CSV_PATH = SIGNS_DIR / "nazwy_znakow.csv"


@dataclass(frozen=True)
class Sign:
    sign_id: str        # e.g. "INFOR-01"
    category: str       # e.g. "Informacyjne"
    filename: str       # e.g. "INFOR-01.png"
    name: str           # e.g. "Droga z pierwszeństwem"


def _load_signs(csv_path: Path = CSV_PATH) -> list[Sign]:
    """Parse the CSV file and return a list of Sign objects."""
    signs = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader)  # skip header
        for row in reader:
            if len(row) < 3 or not row[0].strip():
                continue
            category = row[0].strip()
            filename = row[1].strip()
            name = row[2].strip()
            sign_id = filename.removesuffix(".png")
            signs.append(Sign(
                sign_id=sign_id,
                category=category,
                filename=filename,
                name=name,
            ))
    return signs


# Module-level cache
_signs_cache: list[Sign] | None = None


def _get_signs(csv_path: Path = CSV_PATH) -> list[Sign]:
    """Return cached list of all signs."""
    global _signs_cache
    if _signs_cache is None:
        _signs_cache = _load_signs(csv_path)
    return _signs_cache


def reload_signs(csv_path: Path = CSV_PATH) -> None:
    """Force reload of signs from CSV (useful for testing)."""
    global _signs_cache
    _signs_cache = _load_signs(csv_path)


def get_all_signs() -> list[Sign]:
    """Return all signs."""
    return _get_signs()


def get_categories() -> list[str]:
    """Return sorted list of unique category names."""
    return sorted({s.category for s in _get_signs()})


def get_signs_by_category(category: str) -> list[Sign]:
    """Return all signs in a given category."""
    return [s for s in _get_signs() if s.category == category]


def get_sign_by_id(sign_id: str) -> Sign | None:
    """Return a sign by its ID, or None if not found."""
    for s in _get_signs():
        if s.sign_id == sign_id:
            return s
    return None


def get_image_path(sign: Sign) -> Path:
    """Return the absolute path to the sign's image file."""
    return SIGNS_DIR / sign.category / sign.filename
