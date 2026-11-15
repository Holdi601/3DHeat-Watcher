---
title: Utrzymanie stron
nav_order: 15
lang: "pl"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Utrzymanie tych stron {#maintaining-these-pages}

Lista kontrolna przy każdym wydaniu. Strony muszą mówić, co robi kod, dobrze się czytać dla początkującego, ośmiolatka i profesjonalisty, i istnieć w każdym języku, który obsługuje przeglądarka 3DHeat.

## Lista kontrolna wydania {#release-checklist}

1. **Wygeneruj ponownie strony generowane** z kodu:

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Przed zatwierdzeniem to samo z `--check` musi zakończyć się kodem 0:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Porównaj funkcje od ostatniego wydania.** `VERSION` zawiera wersję; jej tag to `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Każde nowe polecenie, opcja, kolumna, wyjście albo zachowanie dostaje wiersz na stronie, która je opisuje, i wiersz w `CHANGELOG.md` pod **Docs** z nazwą tej strony.

3. **Niezależna recenzja.** Ktoś, kto nie napisał zmiany, czyta zmienione strony - razem z diagramami i obrazkami - trzy razy: jako początkujący (nigdy nie używał terminala), jako ośmiolatek (czy pierwszy akapit mówi, czym to jest i po co, prostymi słowami?) i jako profesjonalista (czy flagi, domyślne wartości i kolumny są dokładnie tym, co robi kod?).

4. **Popraw to, co wykazała recenzja.** Obrazki mają najwyżej około 900 px szerokości, a tekst co najmniej 12 px, tak jak pokazano; diagramy są generowane z `tools/diagrams/*.json` przez `tools/flow2svg.py`. Przykłady używają tylko zmyślonych nazw (`de_x`, „Demo Valley”, `<map>`): nigdy prawdziwej mapy, gracza, id meczu ani postaci z prawdziwych plików.

5. **Tłumaczenia.** Każda przetłumaczona strona zapisuje skrót (hash) angielskiego źródła, z którego powstała. Przetłumacz ponownie strony, których skrót angielskiego źródła się zmienił, a potem niech każdy język zrecenzuje w ten sam trzy sposoby (prosto, dla początkującego, dla profesjonalisty), łącznie z podpisami na diagramach.

6. **Wypychaj tylko za zgodą właściciela.** Zatwierdzaj lokalnie; właściciel decyduje, kiedy repozytorium staje się publiczne.

## Tłumaczenia: polecenia {#translations-the-commands}

Strona jest tłumaczona na 40 języków przeglądarki 3DHeat: angielski jest w `docs/`, każdy inny język w `docs/<język>/` z tymi samymi nazwami plików. `tools/docs_i18n.py` prowadzi ewidencję:

```bash
python tools/docs_i18n.py hashes             # po każdej zmianie angielskiej: zapisz skrót każdej strony
python tools/docs_i18n.py svg-strings        # po każdej zmianie obrazka: podpisy do przetłumaczenia
python tools/docs_i18n.py status             # dla każdego języka: aktualne, nieaktualne, brakujące strony
python tools/docs_i18n.py todo --lang de     # niemieckie strony do (ponownego) przetłumaczenia
python tools/docs_i18n.py svg-build --lang de    # niemieckie obrazki z docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # oznacz niemieckie strony skrótem angielskiego źródła
python tools/docs_i18n.py check              # kończy się kodem 1, gdy skróty lub podpisy są nieaktualne
```

Tłumacz tylko to, co wypisuje `todo`: zachowaj Markdown, linki, kod, nazwy plików i kolumn, przetłumacz tytuły i opisy obrazków, a przyciski i panele przeglądarki 3DHeat nazywaj jej własnymi słowami (z `src/i18n/locales/<język>/`). Generowane strony z referencją i obrazy z terminala zostają po angielsku. Na stronie nieaktualne tłumaczenie to mówi i odsyła do angielskiej strony; brakująca wraca do angielskiego. Menu języków w nagłówku i przekierowanie strony głównej według języka przeglądarki pochodzą z `docs/_includes/`.
