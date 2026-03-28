# Znaki Drogowe

Program edukacyjny do nauki znaków drogowych wymaganych na egzaminie na kartę rowerową.

## Funkcjonalności

- **Zarządzanie uczniami** — dodawanie nowych uczniów, zmiana imienia (ikona ołówka) oraz usuwanie uczniów (ikona kosza) na stronie wyboru ucznia.
- **Moduł 1 - Nauka znaków** — wybierz kategorię i ucz się znaków z fiszek. Znaki, których nie znasz, powtarzają się na końcu serii.
- **Moduł 2 - Powtórki** — system powtórek oparty na algorytmie spaced repetition (SM-2), dostosowany do dzieci 10-12 lat. Znaki prezentowane w losowej kolejności.
- **Moduł 3 - Test** — test z nauczonych znaków (10/20/30 pytań) lub test ze wszystkich 176 znaków. Dwa typy pytań: obraz→nazwa i nazwa→obraz. Błędne odpowiedzi powtarzane w dogrywce.

## Wymagania

- Python 3.11+
- Przeglądarka internetowa (Chrome, Firefox, Safari, Edge)

## Instalacja i uruchomienie

```bash
pip install -r requirements.txt
python main.py
```

Po uruchomieniu `python main.py` program automatycznie otworzy przeglądarkę pod adresem `http://localhost:8080`.

### Instalacja w środowisku wirtualnym (venv)

Jeśli nie możesz instalować bibliotek Pythona globalnie (np. brak uprawnień administratora), użyj środowiska wirtualnego:

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Linux (Fedora):**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Przy każdym kolejnym uruchomieniu należy najpierw aktywować środowisko wirtualne (`source .venv/bin/activate` lub `.venv\Scripts\activate` na Windows), a następnie uruchomić `python main.py`.

## Zamykanie programu

Aby zakończyć działanie programu, naciśnij `Ctrl+C` w terminalu, w którym został uruchomiony.

## Uruchamianie testów

```bash
source .venv/bin/activate   # lub .venv\Scripts\activate na Windows
python -m pytest tests/ -v
```

## Struktura projektu

```
znaki_drogowe/
  main.py                    # Punkt wejścia
  src/
    models/
      sign_catalog.py        # Katalog znaków (ładowanie CSV)
      student.py             # Model danych ucznia
    services/
      student_service.py     # CRUD uczniów
      learning_service.py    # Logika nauki (Moduł 1)
      repetition_service.py  # Silnik powtórek SM-2 (Moduł 2)
      test_service.py        # Logika testów (Moduł 3)
    ui/
      app.py                 # Konfiguracja NiceGUI
      theme.py               # Kolorystyka UI
      pages/                 # Strony interfejsu
  tests/                     # Testy jednostkowe i integracyjne
  data/students/             # Dane uczniów (JSON)
  znaki/                     # Obrazy PNG znaków + CSV
```

## Technologie

- **NiceGUI 2.x** — framework UI (Python → przeglądarka)
- **pytest** — testy
- **JSON** — persystencja danych uczniów
