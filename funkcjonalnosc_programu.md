# Program: Znaki drogowe

## Zalożenia architektoniczne

- nowoczesny UX,
- możliwość uruchomienia programu na dowolnym systemie operacyjnym
- backend może być w python
- jeśli wykorzystany jest python, to należy uruchamiać program w środowisku wirtualnym
- dodatkowe biblioteki python powinny być doinstallowane w tymże środowisku wirtualnym
- program powinien być lekki (bez ciężkich silników np. dla frontend)
- program powinien mieć plik README.md, w którym znajdą się wszelkie konieczne informacje jak uruchomić program i co jest do tego potrzebne. Jeśli konieczne są inne kroki do uruchomienia programu na Windows, MacOS lub Linux (Fedora, Ubuntu, Debian), podaj istrukcję dla każdego systemu operacyjnego osobno
- zarekomenduj najbardziej efektywne technologie, które powinny zostać użute
- wszystkie instrukcje, pliki, menu mają być w języku polskim
- osoba korzystająca z programu ma 10-12 lat i powinna być w stanie go uruchomić
- nie korzystaj z zewnętrznej bazy. Jeśli konieczne jest zapisanie danych użytkownika zrób to w pliku tekstowym (zaproponuj efektywny format)
- Zapisz cały projekt w moim github jako projekt publiczny
- Każda funkcjonalność powinna być wprowadzona jako nowy PR zanim kolejna będzie dodana.
- Dla całego programu przygotuj testy (jednostkowe, funkcjonalne, end to end).
- Wykorzystaj TDD jako metodę programowania.
- Dodaj opis kodu w języku angielskim (wszystko inne w języku polskim).

## Funcjonalności

- Głównym celem programu jest nauczenie dziecka znaków drogowych wymaganych na egzaminie na kartę rowerową
- Program ma mieć 3 moduł
- Moduł 1 - Nauka znaków
- Moduł 2 - Powtórki znaków, których użutkownik się nauczył
- Moduł 3 - Test ze wszystkich znaków
- Uruchamiając program użytkownik dodania nowego ucznia lub wybrania już istniejącego ucznia
- Dla każdego ucznia prowadzony będzie rejest prostępu (zrób wstępny raport, aby określić co ma być w takim rejestrze). 
- Po wybraniu ucznia, uczen powinien zobaczyc swoj status (ile znakow sie juz nauczyl, ile mu jeszcze zostalo, ile znaków powinnien powtórzyć). Dodatkowo uczeń może wybrać czy chce się uczyć nowych znaków (Moduł 1), powtórzyć znaki już przysfojone (Moduł 2), zrobić test (Moduł 3). Dodatkowo uczeń powinnien mieć możliwość wyjścia z programu (wylogowania się lub zmiany ucznia).
- Po wykonaniu danego modułu program wraca do interfejsu opisanego w poprzednim punkcie (status, nauka, powtórka, test)

### Funkcjonalność Modułu 1 - Nauka znaków

- Uczeń powinien móc zdefiniować ile znaków chce się uczyć w jednej serii (zdefiniowanie tego powinno nastąpić w ustawieniach globalnych ucznia
- Uczeń powinien mieć możliwość wyboru zestawu znków do nauczenia (odpowiada to podkatalogom w katalogu znaki) (np. Informacyjne, Zakazu)
- W trybie uczenia, uczniowi wyświetal się zdjęcie znaku (plik PNG). Uczeń ma do dyspozycji 3 klawisze: znam ten znaj, nie znam tego znaku, pokaż nazwę tego znaku. Jeśli uczeń kliknie znam ten znak, znak traktowany jest jako nauczony i trafia do zbioru znaków dla modułu 2. Jeśli uczen klikinie klawisz nie znam tego znaku, to znak trafia do list znaków do nauczenia (pojawia się nazwa znaku na 5 sekund i następnie system przechodzi do nauki kolejnego znaku) i na końcu serji znaki do nauczenia są prezentowana ponownie. Proces powtaża się, aż uczeń nie nauczy się wszystkich znaków z grupy wybranej do nauki. Jak uczeń klkie pokaż nazwę tego znaku, to znak jest traktowany jako nienienauczony. 
- postęp nauki ucznia jest zapisywany w rejestrze ucznia

### Funkcjonalność Modułu 2 - Powtórki znaków, których użytkownik się nauczył

- Znaki losowane są z puli znaków nauczonych.
- Uczeń powinien dostać do powtórznia wszystkie znaki z ostatniego cyklu nauki (Moduł 1), które opanował
- Dodatkowo uczeń powinien dostać zestaw znaków, których już się wcześniej nauczuł, aby powtórzyć i utrwalić wiedzę.
- Zrób badanie i ustal parametry ile i jak często znaki powinny być powtarzane, aby utrwalić je w pamięci.

### Funkcjonalność Modułu 3 - Test ze wszytkich znaków

- Występują dwa tryby.
- Tryb 1 - wybierz 10,20, lub 30 znaków z dowolnej kategorji. Uczń może wybrać ile znaków ma być przetestowanych
- Tryb 2 - testowanie wszystkich znaków jakie są. Jest to test sprawdź pełną wiedzę.
- W przypakdu będnej odpowiedzi (w dowolnym z trybów) pytanie o znak jest powtarzane po zakończeniu całej serji.
- Występują 2 główne typy pytań:
- Pytania typu 1 - Wyświetlany jest znak (plik PNG) i pod spodem pojawiają się 4 odpowiedzi. Jedna z nich jest poporawna. Pozostałe trzy to nazwy innych losowych znaków wybranych z tej samej kategorii.
- Pytania typu 2 - Pojawia się nazwa znaku i 4 znaki (pliki PNG). Jeden poprawny i trzy inne z tej samej kategorii. Uczeń musi wskazać poprawny znaj, aby odpowiedź zostąła zaliczona.y
- Poprawna odpowiedź jest losowo umieszczana jako pierwsza, druga, trzecia lub czwarta.
- Program rejestruje pytanie i odpowiedź, aby na końcu przedstawić podsumowanie. Jeśli błędna odpowiedź została wybrana, to jest ona zaznaczona i podana jest równiez odpowiedź poprawna.

## Inne

- Podziel ten projekt na kroki (funkcjonalności) i zaproponuj ich wprowadzanie mając na uwagę typ mojej subskrypcji, ilość tokenów, itd.
- Planuj wszystko w trybie plan mode.
- Jak masz jakie kolwiek pytania, to zadaj je zanim rozpoczniesz proces implementajci funcjonalności
