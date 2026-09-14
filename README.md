# NetStore Pomocnik

NetStore Pomocnik to projekt aplikacji do wystawiania i zarządzania ofertami na własnym koncie sprzedawcy Allegro za pośrednictwem Allegro REST API. Celem jest usprawnienie przygotowywania ofert oraz aktualizacji informacji o sprzedawanych produktach.

## Status projektu

Projekt jest na etapie przygotowania. Repozytorium zawiera obecnie dokumentację, bez kodu aplikacji i wersji do uruchomienia. Poniższe funkcje oraz sposób działania opisują planowany zakres.

## Planowane funkcje

- Połączenie aplikacji z kontem sprzedawcy Allegro.
- Przygotowywanie ofert: tytuły, opisy, zdjęcia, kategorie i parametry produktów.
- Wystawianie ofert po zatwierdzeniu przez użytkownika.
- Pobieranie listy ofert i sprawdzanie ich statusu.
- Aktualizacja cen, liczby dostępnych sztuk i danych ofert.
- Prezentowanie wyników operacji oraz błędów wymagających poprawy danych.

## Planowany sposób korzystania

1. Użytkownik konfiguruje aplikację i autoryzuje dostęp do swojego konta Allegro.
2. Przygotowuje dane produktu i oferty.
3. Sprawdza dane oraz zatwierdza wysłanie do Allegro.
4. Aplikacja wykonuje operację przez API i pokazuje jej wynik.
5. Użytkownik może przeglądać i aktualizować swoje oferty.

## Przygotowanie integracji z Allegro

Dostęp do API wymaga rejestracji aplikacji w panelu [Moje aplikacje Allegro](https://apps.developer.allegro.pl/). Autoryzacja korzysta z OAuth. Szczegóły konfiguracji i instrukcja uruchomienia zostaną dodane po wyborze technologii oraz wdrożeniu integracji.

Pierwsze testy integracji są planowane w środowisku testowym Allegro Sandbox.

### Adres dokumentacji aplikacji

Adres strony opisującej cel działania NetStore Pomocnik:

https://github.com/Fabio28P/netstore-pomocnik

Można go podać jako adres dokumentacji aplikacji. Nie jest to adres przekierowania OAuth ani adres uruchomionego programu.

### Identyfikacja aplikacji — User-Agent

Allegro wymaga własnego nagłówka `User-Agent`, zawierającego nazwę aplikacji, wersję i adres dokumentacji. Przykład do dostosowania przy wdrożeniu:

```text
NetStorePomocnik/0.1.0 (+https://github.com/Fabio28P/netstore-pomocnik)
```

Nazwa musi być spójna z nazwą zarejestrowanej aplikacji, a wersja odpowiadać faktycznie używanemu wydaniu. Powyższy numer jest przykładowy i nie oznacza dostępnego wydania.

Źródło: [Informacje podstawowe Allegro REST API](https://developer.allegro.pl/tutorials/informacje-podstawowe-b21569boAI1).

## Założenia dotyczące bezpieczeństwa

Przy implementacji przyjmujemy następujące zasady:

- Dostęp obejmuje wyłącznie uprawnienia potrzebne do obsługi ofert.
- Hasło do Allegro nie jest przechowywane w aplikacji.
- Sekrety aplikacji i tokeny autoryzacyjne pozostają poza repozytorium.
- Tokeny i inne dane uwierzytelniające nie trafiają do logów ani zgłoszeń błędów.
- Testy poprzedzają uruchomienie operacji na rzeczywistych ofertach.

## Uruchomienie

Instrukcja instalacji, wymagania techniczne i konfiguracja zostaną uzupełnione wraz z pierwszą działającą wersją. Na obecnym etapie nie ma poleceń instalacyjnych ani pliku konfiguracyjnego aplikacji.

## Plan prac

- [x] Utworzenie repozytorium i dokumentacji projektu.
- [ ] Wybór technologii i przygotowanie kodu aplikacji.
- [ ] Konfiguracja dostępu do Allegro API.
- [ ] Implementacja autoryzacji konta sprzedawcy.
- [ ] Pobieranie ofert i przygotowanie pierwszej oferty testowej.
- [ ] Obsługa publikacji, edycji i błędów API.
- [ ] Testy w Sandbox i uzupełnienie instrukcji użytkownika.

## Zgłaszanie problemów

Błędy oraz propozycje zmian można zgłaszać w sekcji [Issues](https://github.com/Fabio28P/netstore-pomocnik/issues). Zgłoszenie powinno zawierać opis problemu i kroki jego odtworzenia, bez haseł, sekretów i tokenów.

## Oficjalna dokumentacja Allegro

- [Portal Allegro REST API](https://developer.allegro.pl/)
- [Informacje podstawowe i wymagania integracji](https://developer.allegro.pl/tutorials/informacje-podstawowe-b21569boAI1)
