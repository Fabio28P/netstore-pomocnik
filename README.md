# NetStore Pomocnik

Lokalna aplikacja do przygotowania i wystawienia oferty na własnym koncie Allegro. Wersja 1.0 zawiera panel w języku polskim, logowanie OAuth, edytor zdjęć i sekcji opisu, podgląd, zapis szkicu i publikację po zatwierdzeniu.

## Uruchomienie na Windows

1. Pobierz repozytorium: **Code → Download ZIP** i rozpakuj cały folder (nie uruchamiaj pliku wewnątrz ZIP).
2. Zainstaluj Python 3.10 lub nowszy z [python.org](https://www.python.org/downloads/windows/). Podczas instalacji zaznacz **Add Python to PATH**.
3. Kliknij dwukrotnie **URUCHOM.bat**. Nie wymaga instalowania dodatkowych bibliotek.
4. Otworzy się panel pod `http://localhost:8000`. Zostaw okno programu otwarte. Jeśli przeglądarka nie otworzy się automatycznie, wpisz ten adres ręcznie.
5. Rozwiń **Połączenie z Allegro**, wpisz Client ID i Client Secret swojej aplikacji **NetStore Pomocnik**, wybierz środowisko i kliknij **Zapisz konfigurację**.
6. Kliknij **Połącz z Allegro**. Zaloguj się na stronie Allegro i udziel zgody. Powrócisz do panelu.

Linux/macOS: `python3 app.py`. Zamknięcie terminala kończy działanie aplikacji.

## Konfiguracja w Allegro Developer Apps

Typ aplikacji: dostęp do przeglądarki (`authorization_code`). Adres przekierowania musi być dokładnie taki:

```text
http://localhost:8000/allegro/callback
```

Uprawnienia:
- `allegro:api:sale:offers:read`
- `allegro:api:sale:offers:write`
- `allegro:api:sale:settings:read`

User-Agent wysyłany przez program:

```text
NetStore-Pomocnik/1.0 (+https://github.com/Fabio28P/netstore-pomocnik)
```

Sandbox wymaga osobnego konta i osobnej aplikacji zarejestrowanej w środowisku testowym. Klucze produkcyjne nie działają w Sandbox.

## Pierwsza oferta

Panel startuje z edytowalnym opisem rolki do LG Magic MR21/MR22/MR23 zgodnie z danymi podanymi przez właściciela projektu: cena 18 zł, 1000 sztuk, jedna rolka w zestawie, druk 3D, czas wysyłki 1 dzień. Zgodność produktu należy sprawdzić przed publikacją.

1. Dodaj zdjęcia PNG/JPG. Pierwsze jest zdjęciem głównym. Zmień kolejność strzałkami, jeśli trzeba.
2. Przejrzyj i popraw sekcje opisu. Podgląd jest przybliżeniem układu, ostateczne renderowanie należy do Allegro.
3. Kliknij **Pobierz ustawienia ze wzoru**. Domyślna oferta wzorcowa: `18866219051`. Musi należeć do autoryzowanego konta. Kopiowane są cennik dostawy, warunki posprzedażowe, lokalizacja i ustawienia płatności; czas wysyłki ustawiany jest na 1 dzień. Produkt, jego parametry i zdjęcia nie są kopiowane.
4. Kliknij **Wczytaj pola** i uzupełnij parametry kategorii. Wybierz istniejący produkt tylko przy dokładnej zgodności; bez wyboru aplikacja wysyła dane nowego produktu wraz z ofertą.
5. Wybierz producenta odpowiedzialnego z danych Twojego konta i uzupełnij informacje o bezpieczeństwie, jeżeli wymagane. Nie przypisuj LG jako producenta zamiennika tylko dlatego, że pasuje do pilota LG.
6. **Zapisz na komputerze** zachowuje pracę lokalnie, bez wysyłania do Allegro.
7. **Zapisz szkic w Allegro** wysyła ofertę ze statusem `INACTIVE`. Allegro może zwrócić brakujące parametry lub inne błędy — popraw je przed ponownym zapisem.
8. Po zapisie i kontroli treści zaznacz potwierdzenie, kliknij **Opublikuj ofertę**, a następnie **Sprawdź status**. Dopiero status `ACTIVE` potwierdza publikację.

## Zakres i ograniczenia wersji 1.0

- To działający kod lokalnej aplikacji, nie usługa hostowana i nie plik EXE. Wymaga Pythona.
- Obsługuje jedną przygotowywaną ofertę. Nie zawiera jeszcze menedżera wielu produktów ani edycji aktywnych ofert.
- Opisy korzystają z edytowalnego szablonu. Nie ma jeszcze automatycznego pisania przez AI, rozpoznawania produktu ze zdjęć ani generowania zdjęć. Aplikacja nie wymaga klucza do usługi AI.
- Parametry tekstowe i słownikowe są obsługiwane w formularzu. Nietypowe kategorie mogą wymagać rozszerzenia formularza (np. wartości zakresowe lub własne wartości słownikowe).
- Wybór producenta obejmuje pierwsze 100 wpisów. Nowych producentów dodaje się w Allegro.
- Testy jednostkowe i lokalne nie zastępują pierwszego testu OAuth i wystawienia oferty w Sandbox. Nie wykonano rzeczywistej autoryzacji, przesłania zdjęć ani publikacji na koncie użytkownika podczas przygotowania kodu.

## Dane lokalne

Konfiguracja, tokeny i szkic zapisują się w katalogu `.netstore-pomocnik` w folderze użytkownika systemowego, poza repozytorium. Na Windows zwykle jest to `C:\Users\NAZWA\.netstore-pomocnik`. Pliki te zawierają dane poufne w postaci jawnego JSON — nie udostępniaj ich ani nie dodawaj do GitHub. Ochrona dostępu zależy także od konta systemowego. Rozłączanie usuwa lokalne tokeny; upoważnienie można odwołać również w Allegro.

Program nasłuchuje wyłącznie na `127.0.0.1`, sprawdza Host/Origin i token CSRF. OAuth korzysta ze state i PKCE. Sekrety nie są zwracane do panelu ani drukowane w logach. Refresh token służy do odświeżania dostępu. Nie udostępniaj portu programu w internecie.

Po niejednoznacznym wyniku zapisu (np. zerwaniu połączenia) program blokuje ponowne tworzenie i pozwala wyszukać ofertę po własnym identyfikatorze. Nie ponawiaj tworzenia ręcznie, zanim nie sprawdzisz wyniku w Allegro. Po odzyskaniu szkicu zapisz go ponownie przed publikacją.

## Testy

```text
python -m unittest -v
```

Testy sprawdzają m.in. poprawność danych, niedopuszczenie do skopiowania starego produktu, kodowanie opisu, ochronę przed powtórzeniem zapisu i publikacją bez potwierdzenia.

## Dokumentacja i kontakt

- [Autoryzacja Allegro](https://developer.allegro.pl/tutorials/uwierzytelnianie-i-autoryzacja-zlq9e75GdIR)
- [Wystawianie ofert](https://developer.allegro.pl/tutorials/jak-jednym-requestem-wystawic-oferte-powiazana-z-produktem-D7Kj9gw4xFA)
- [Specyfikacja API](https://developer.allegro.pl/swagger.yaml)
- [Zgłoszenia do NetStore Pomocnik](https://github.com/Fabio28P/netstore-pomocnik/issues)
