# NetStore Pomocnik

Lokalna aplikacja do przygotowania i wystawienia oferty na własnym koncie Allegro. Wersja 1.1 zawiera panel w języku polskim, logowanie OAuth, edytor zdjęć i sekcji opisu, podgląd, zapis szkicu i publikację po zatwierdzeniu.

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
NetStore-Pomocnik/1.1 (+https://github.com/Fabio28P/netstore-pomocnik)
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

## Zakres i ograniczenia wersji 1.1

- To działający kod lokalnej aplikacji, nie usługa hostowana i nie plik EXE. Wymaga Pythona.
- Obsługuje jedną przygotowywaną ofertę. Nie zawiera jeszcze menedżera wielu produktów ani edycji aktywnych ofert.
- Opisy można generować przez OpenAI API na podstawie wpisanych faktów i zapisanego profilu sklepu. Szablon i edycja ręczna nadal działają bez klucza AI. Ta wersja nie analizuje ani nie generuje zdjęć.
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

## Generator opisów — wersja 1.1

Panel ma niebieską kolorystykę. Nowa sekcja **Generator opisów — ustawienia OpenAI** pozwala zapisać lokalny klucz API, nazwę modelu i profil sklepu.

1. Utwórz klucz w [OpenAI API](https://platform.openai.com/api-keys) i skonfiguruj rozliczenia API. To osobna usługa od abonamentu ChatGPT; program nie loguje się do Twojej rozmowy ani nie pobiera jej historii.
2. Wpisz klucz wyłącznie w lokalnym panelu i kliknij **Zapisz ustawienia AI**. Domyślny model: `gpt-4.1-mini`; można wpisać inny model obsługujący Responses API i Structured Outputs, dostępny na własnym koncie.
3. W polu **Co wiemy o produkcie?** wpisz potwierdzone cechy. Początkowy wpis zawiera dane rolki ustalone przez właściciela. Dla innego produktu zastąp je jego własnymi danymi.
4. Kliknij **Wygeneruj opis**. Do OpenAI trafiają tylko fakty z tego pola oraz zapisany profil sklepu. Zdjęcia, klucze Allegro i pozostałe ustawienia oferty nie są wysyłane.
5. Sprawdź propozycję i pytania o brakujące dane. **Zastosuj tytuł i opis** przenosi propozycję do edytora. **Cofnij zastosowanie** przywraca poprzedni tekst; **Odrzuć propozycję** zamyka podgląd.
6. Zapisz poprawiony szkic w Allegro przed publikacją. Generator nie zmienia ceny, ilości, parametrów ani ustawień dostawy i nie publikuje oferty.

Profil NetStore zawiera ustalone zasady: konkretny język, krótkie sekcje, ważne informacje dla klienta, bez pustych haseł, emoji i powtarzania zalet. Dane o konkretnej rolce nie są stałą wiedzą o wszystkich produktach. Model jest instruowany, by nie wymyślać cech, lecz wynik zawsze wymaga sprawdzenia przez sprzedawcę.

Klucz jest przechowywany jawnie w lokalnym pliku `ai-config.json` obok pozostałych danych programu, poza repozytorium. Można go usunąć przyciskiem **Usuń klucz AI**. Nie udostępniaj folderu danych programu. Żądania używają `store: false`; nie jest to obietnica braku wszelkich logów po stronie dostawcy — obowiązują zasady danych API.

Testy generatora wykorzystują odpowiedzi symulowane: poprawny wynik, przerwane generowanie, walidację i brak klucza. Nie wykonano płatnego wywołania z kluczem użytkownika.

Dokumentacja: [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs), [model](https://developers.openai.com/api/docs/models/gpt-4.1-mini), [rozliczenia API](https://platform.openai.com/settings/organization/billing/overview).

Aktualizacja: zamknij program, pobierz nowy ZIP, rozpakuj go i uruchom nowy `URUCHOM.bat`. Dotychczasowe ustawienia i szkic są poza folderem programu, więc pozostają dostępne.
