"""Tests for sign catalog loading and querying."""

import pytest
from pathlib import Path

from src.models.sign_catalog import (
    get_all_signs,
    get_categories,
    get_signs_by_category,
    get_sign_by_id,
    get_image_path,
    _load_signs,
    Sign,
)


class TestLoadSigns:
    def test_loads_all_176_signs(self):
        signs = get_all_signs()
        assert len(signs) == 176

    def test_sign_has_correct_fields(self):
        signs = get_all_signs()
        sign = signs[0]
        assert sign.sign_id == "INFOR-01"
        assert sign.category == "Informacyjne"
        assert sign.filename == "INFOR-01.png"
        assert sign.name == "Droga z pierwszeństwem"

    def test_all_signs_have_non_empty_fields(self):
        for sign in get_all_signs():
            assert sign.sign_id
            assert sign.category
            assert sign.filename
            assert sign.name


class TestCategories:
    def test_has_11_categories(self):
        categories = get_categories()
        assert len(categories) == 11

    def test_categories_are_sorted(self):
        categories = get_categories()
        assert categories == sorted(categories)

    def test_known_categories_present(self):
        categories = get_categories()
        assert "Informacyjne" in categories
        assert "Zakazu" in categories
        assert "Ostrzegawcze" in categories


class TestSignsByCategory:
    def test_informacyjne_count(self):
        signs = get_signs_by_category("Informacyjne")
        assert len(signs) == 35

    def test_zakazu_count(self):
        signs = get_signs_by_category("Zakazu")
        assert len(signs) == 20

    def test_empty_for_unknown_category(self):
        signs = get_signs_by_category("Nieistniejaca")
        assert signs == []

    def test_all_signs_in_category_match(self):
        for sign in get_signs_by_category("Nakazu"):
            assert sign.category == "Nakazu"


class TestGetSignById:
    def test_finds_existing_sign(self):
        sign = get_sign_by_id("ZAKAZ-01")
        assert sign is not None
        assert sign.name == "Zakaz ruchu w obu kierunkach"

    def test_returns_none_for_unknown(self):
        assert get_sign_by_id("FAKE-99") is None


class TestImagePath:
    def test_image_path_structure(self):
        sign = get_sign_by_id("INFOR-01")
        path = get_image_path(sign)
        assert path.name == "INFOR-01.png"
        assert path.parent.name == "Informacyjne"

    def test_image_file_exists(self):
        sign = get_sign_by_id("INFOR-01")
        path = get_image_path(sign)
        assert path.exists()

    def test_all_images_exist(self):
        for sign in get_all_signs():
            path = get_image_path(sign)
            assert path.exists(), f"Missing image: {path}"


class TestMalformedCsv:
    def test_skips_empty_rows(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(
            "NAZWA_KATALOGU;NAZWA_PLIKU;NAZWA_ZNAKU\n"
            "Kat;SIGN-01.png;Nazwa\n"
            ";;;\n"
            "\n"
            "Kat;SIGN-02.png;Nazwa2\n",
            encoding="utf-8",
        )
        signs = _load_signs(csv_file)
        assert len(signs) == 2
