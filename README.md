# NetStore Pomocnik

Lokalna aplikacja do przygotowania i wystawienia oferty na własnym koncie Allegro. Wersja 1.3 zawiera panel w języku polskim, logowanie OAuth, edytor zdjęć i sekcji opisu, podgląd, zapis szkicu i publikację po zatwierdzeniu.

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
NetStore-Pomocnik/1.3 (+https://github.com/Fabio28P/netstore-pomocnik)
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

## Zakres i ograniczenia wersji 1.3

- To działający kod lokalnej aplikacji, nie usługa hostowana i nie plik EXE. Wymaga Pythona.
- Foldery produktów mają osobne szkice i identyfikatory ofert. Pracujesz nad jednym wybranym produktem naraz; bez edycji aktywnych ofert i bez automatycznej publikacji całej kolejki.
- Opisy można generować przez OpenAI API na podstawie wpisanych faktów i zapisanego profilu sklepu. Szablon i edycja ręczna nadal działają bez klucza AI. Może analizować pomniejszone zdjęcia do doboru układu, jeśli zaznaczysz tę opcję. Nie generuje nowych zdjęć.
- Parametry tekstowe i słownikowe są obsługiwane w formularzu. Nietypowe kategorie mogą wymagać rozszerzenia formularza (np. wartości zakresowe).
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
4. Kliknij **Wygeneruj opis**. Do OpenAI trafiają tylko fakty z tego pola oraz zapisany profil sklepu. Klucze Allegro i pozostałe ustawienia oferty nie są wysyłane. Opcjonalna analiza układu dodatkowo wysyła pomniejszone zdjęcia.
5. Sprawdź propozycję i pytania o brakujące dane. **Zastosuj tytuł i opis** przenosi propozycję do edytora. **Cofnij zastosowanie** przywraca poprzedni tekst; **Odrzuć propozycję** zamyka podgląd.
6. Zapisz poprawiony szkic w Allegro przed publikacją. Generator nie zmienia ceny, ilości, parametrów ani ustawień dostawy i nie publikuje oferty.

Profil NetStore zawiera ustalone zasady: konkretny język, krótkie sekcje, ważne informacje dla klienta, bez pustych haseł, emoji i powtarzania zalet. Dane o konkretnej rolce nie są stałą wiedzą o wszystkich produktach. Model jest instruowany, by nie wymyślać cech, lecz wynik zawsze wymaga sprawdzenia przez sprzedawcę.

Klucz jest przechowywany jawnie w lokalnym pliku `ai-config.json` obok pozostałych danych programu, poza repozytorium. Można go usunąć przyciskiem **Usuń klucz AI**. Nie udostępniaj folderu danych programu. Żądania używają `store: false`; nie jest to obietnica braku wszelkich logów po stronie dostawcy — obowiązują zasady danych API.

Testy generatora wykorzystują odpowiedzi symulowane: poprawny wynik, przerwane generowanie, walidację i brak klucza. Nie wykonano płatnego wywołania z kluczem użytkownika.

Dokumentacja: [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs), [model](https://developers.openai.com/api/docs/models/gpt-4.1-mini), [rozliczenia API](https://platform.openai.com/settings/organization/billing/overview).

Aktualizacja: zamknij program, pobierz nowy ZIP, rozpakuj go i uruchom nowy `URUCHOM.bat`. Dotychczasowe ustawienia i szkic są poza folderem programu, więc pozostają dostępne.

## Wersja 1.3 — Gemini Free Tier, foldery i wymagane parametry

### Darmowy limit Gemini

Wybierz **Gemini** w ustawieniach AI. Domyślny model to `gemini-2.5-flash-lite`, który według [cennika Google](https://ai.google.dev/gemini-api/docs/pricing) ma bezpłatny poziom tekstowego API. Utwórz klucz w [Google AI Studio](https://aistudio.google.com/api-keys) dla projektu **Free Tier**. Wpisz go lokalnie, kliknij **Wstaw uzgodniony styl NetStore**, potem **Zapisz ustawienia AI**.

Bezpłatny dostęp ma limity i zależy od dostępności na koncie. Program nie włącza płatności, nie sprawdza poziomu rozliczeń projektu i nie przełącza automatycznie na płatne API. Przy projekcie z aktywnymi płatnościami użycie może być naliczane zgodnie z cennikiem. Po HTTP 429 aplikacja zatrzymuje generowanie i wyświetla komunikat. Dane podlegają warunkom dostawcy; bezpłatny poziom może wykorzystywać treści do ulepszania usług Google. Nie wysyłaj poufnych informacji.

OpenAI pozostaje osobną opcją. Przy zmianie dostawcy trzeba podać właściwy klucz; klucz OpenAI nigdy nie zostanie wysłany do Google ani odwrotnie. Gemini korzysta z udokumentowanej metody [generateContent](https://ai.google.dev/api/generate-content) ze strukturalną odpowiedzią JSON.

### Folder „3d Sklep”

1. Kliknij wybór folderu w sekcji **Produkty z folderu** i wskaż `C:\Users\rybab\OneDrive\Pulpit\3d Sklep`.
2. Wybierz podfolder produktu z listy, np. **Lg magic scroll MR23GN**, i kliknij **Wczytaj produkt z folderu**.
3. Program odczyta PNG/JPG (maks. 10 zdjęć, 25 MB razem) oraz opcjonalny `opis.txt` lub `produkt.txt` z tego samego podfolderu. Inne TXT, PDF i 3MF są pomijane. Zdjęcia muszą być lokalnie dostępne — w OneDrive pobierz je na komputer.
4. Dla nowego produktu podaj cenę, ilość i fakty. Żadne dane o poprzedniej rolce nie są automatycznie przypisywane nowemu produktowi. Wczytane pliki tekstowe sprawdź przed generowaniem.
5. Generuj opis, sprawdź pytania, zastosuj propozycję, uzupełnij wymagane parametry i zapisz szkic w Allegro. Publikację uruchamiasz po sprawdzeniu przyciskiem **Opublikuj ofertę**.

Aplikacja zapamiętuje szkic dla ścieżki podfolderu. Powrót do folderu przywraca zapisany szkic, a nie nadpisuje go nowymi plikami. Nowe zdjęcia można dodać w galerii. Wybór folderu jest jednorazowy na sesję przeglądarki; to import na żądanie, nie usługa stale obserwująca dysk. Sama lista wybranych plików nie jest wysyłana do usług AI. Treść opiera się na faktach tekstowych. Opcjonalnie zdjęcia wysyłane są do AI do doboru ilustracji; do Allegro trafiają przy zapisie szkicu.

Przykładowa zawartość `opis.txt` (uzupełnij prawdziwymi danymi):

```text
Produkt: rolka zamienna do pilota.
Zgodne modele: wpisz wyłącznie potwierdzone modele.
Kupujący otrzymuje: jedna część, bez pilota.
Wykonanie: druk 3D (jeżeli dotyczy).
Kolor: wpisz kolor produktu.
Montaż i ograniczenia: wpisz informacje sprawdzone dla tej części.
```

### Błąd 422: Kod producenta, Model, Marka

Pobierane i łączone są teraz parametry oferty i parametry tworzenia produktu. Pola wymagane są na początku formularza. Zapis zatrzymuje się przed wysłaniem zdjęć i wskazuje nazwy brakujących pól. Parametry produktowe są kierowane do danych produktu niezależnie od wcześniejszego przypisania w formularzu.

- **Kod producenta**: rzeczywisty kod części; jeśli sam ją produkujesz, stosuj własne, jednoznaczne oznaczenie.
- **Model**: oznaczenie modelu sprzedawanej części.
- **Marka**: marka części, nie automatycznie LG. Jeśli jest bez marki, wybierz odpowiednią dostępną opcję zgodnie ze stanem faktycznym. Gdy wybierasz „inna” i Allegro wymaga własnej wartości, wpisz ją w dodatkowym polu.

Nie kopiujemy kodu `printefix` ani kompatybilności AN-MR18BA z tekstu służącego za wzór stylistyczny. Po pobraniu ustawień starej oferty pola parametrów wczytują się automatycznie.

Opis obsługuje **pogrubienia** (zapis `**ważna fraza**`) i listy (wiersze zaczynające się od `- `). HTML jest escapowany. Testy: 19 testów, w tym obsługa Gemini, limitów, przełączania folderów i parametrów wymaganych. Testy API są symulowane, bez rzeczywistego generowania ani publikacji na koncie użytkownika.

## Aktualizacja 1.3 — komunikaty, rozbudowane opisy i układ zdjęć

### Czytelne odpowiedzi Allegro

Po zapisie zobaczysz krótkie podsumowanie, oddzielnie błędy i uwagi. Pusta lista `errors` oznacza brak błędów w otrzymanej walidacji; uwagi nie są ukrywane ani traktowane jako potwierdzenie zgodności prawnej. Pełny JSON jest dostępny pod **Szczegóły odpowiedzi Allegro**. Znane uwagi o informacjach bezpieczeństwa oraz wysyłce zagranicznej mają krótkie polskie objaśnienia. Nieznane uwagi są pokazywane w oryginalnej treści.

### Instrukcja stylu z przykładami

Plik `style_guide.txt` zawiera bieżący standard i dwa przykłady redakcyjne: rolkę pilota oraz narzędzie do dysz. Jest przekazywany przy każdym generowaniu. To instrukcja i przykłady (few-shot), nie fine-tuning ani trwałe trenowanie modelu. Cel: zwykle 280–420 słów, 5–7 sekcji, wstęp o problemie klienta, korzyści, zastosowanie, montaż, ograniczenia i zawartość zestawu. Przy małej liczbie faktów wynik może być krótszy i zawierać pytania. Materiał PETG, modele pilotów i inne cechy z przykładów nie mogą być przenoszone do nowego produktu bez danych.

Nowy standard redakcyjny działa również przy wcześniej zapisanym profilu. Możesz dodatkowo kliknąć **Wstaw uzgodniony styl NetStore** i zapisać ustawienia AI. Nagłówki nie zawierają widocznych `###`. Pogrubienia i listy są renderowane w podglądzie oraz opisie Allegro.

### Zdjęcia i rozmieszczenie

Opcja **Wyślij pomniejszone zdjęcia do wybranego AI, aby dobrać układ opisu** jest domyślnie włączona. Przed generowaniem możesz ją wyłączyć. Włączona wysyła maksymalnie 10 kopii zdjęć, pomniejszonych do 768 px, do skonfigurowanego dostawcy. Obowiązują jego zasady danych i limity; analiza zdjęć może zwiększać użycie API.

Model przypisuje zdjęcia do sekcji na podstawie ich treści wizualnej. Fakty techniczne nadal muszą pochodzić z opisu produktu. Program usuwa powtórzenia i nieprawidłowe indeksy, rozmieszcza nieprzypisane ilustracje oraz pokazuje pozostałe zdjęcia w wierszach galerii po opisie. Wszystkie zdjęcia są uwzględnione raz w opisie. Każda sekcja ma listę **Zdjęcie 1, 2… / Sekcja bez zdjęcia**, więc można poprawić przypisanie ręcznie. Podgląd i wysyłany opis stosują te same przypisania. Allegro dostosowuje ostateczny wygląd do urządzenia kupującego.

Bez analizy zdjęć program rozkłada je równomiernie na sekcje. Nie deklaruje, że rozpoznał ich zawartość. Kolejność głównej galerii oferty nadal ustalasz strzałkami przy miniaturach.

### Weryfikacja

24 testy Pythona oraz testy formatowania komunikatów (`node test_messages.cjs`). Testy obejmują przypisanie czterech zdjęć bez pominięć i powtórzeń, nieprawidłowe indeksy, nagłówki, strukturę żądań AI oraz zachowanie nieznanych ostrzeżeń. Wywołania AI są symulowane. Nie oceniono nowego opisu wygenerowanego na żywo na koncie użytkownika.

### Miejsce wysyłki

W sekcji „Dostawa i warunki sprzedaży” wpisz miejsce wysyłki i kliknij „Zapisz jako domyślne miejsce wysyłki”. Dane są przechowywane lokalnie, poza repozytorium, i przekazywane do Allegro przy zapisie oferty. Nowe produkty korzystają z lokalnych ustawień; każdy szkic może mieć własne miejsce wysyłki. Wzór nie nadpisuje lokalizacji. Bez skonfigurowanej lokalizacji program prosi o jej uzupełnienie, zamiast kopiować ją z innej oferty.

Aktualizacja programu nie zmienia już zapisanych ofert w Allegro. Szkic trzeba ponownie zapisać; aktywną ofertę popraw bezpośrednio w Allegro.
