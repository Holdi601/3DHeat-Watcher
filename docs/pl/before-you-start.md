---
title: "Zanim zaczniesz"
nav_order: 2
lang: pl
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Zanim zaczniesz {#before-you-start}

Nigdy nie używałeś wiersza poleceń? Ta strona przeprowadzi cię od zera do działającego
3DHeat Watcher w około dziesięć minut. Wpisujesz polecenia w *terminalu*, oknie, w którym piszesz linię
i naciskasz Enter.

## 1. Zainstaluj Pythona {#install-python}

1. Pobierz Pythona 3.10 lub nowszego ze strony <https://www.python.org/downloads/>.
2. Uruchom instalator. Na pierwszym ekranie zaznacz **Add python.exe to PATH**,
   a potem kliknij **Install Now**.
3. Sprawdź: otwórz terminal (krok 3) i wpisz `python --version`. Powinieneś zobaczyć
   `Python 3.` i numer 10 lub wyższy.

W Linuksie albo macOS Python zwykle jest już zainstalowany: tam, gdzie te strony piszą `python`, użyj `python3`.

## 2. Pobierz 3DHeat Watcher {#get-3dheat-watcher}

Pobierz zip ze strony [Releases](https://github.com/Holdi601/3DHeat-Watcher/releases) i rozpakuj go,
na przykład do `C:\Tools\3DHeat-Watcher`. (Jeśli masz Gita, też działa `git clone`.)

## 3. Otwórz terminal w tym folderze {#open-a-terminal-in-that-folder}

- **Windows:** otwórz folder w Eksploratorze plików, kliknij pasek adresu, wpisz
  `powershell` i naciśnij Enter. Otworzy się niebieskie lub czarne okno, już w tym folderze.
- **macOS / Linux:** otwórz *Terminal* i wpisz `cd ` (ze spacją), przeciągnij
  folder do okna i naciśnij Enter.

`cd <folder>` przenosi terminal do innego folderu. Wszystkie polecenia na tych
stronach wpisujesz w folderze samego narzędzia.

## 4. Zainstaluj, czego potrzebuje {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Na końcu powinieneś zobaczyć `Successfully installed ...` (albo `Requirement
already satisfied`).

## 5. Sprawdź, czy działa {#check-it-works}

```bash
python -m heat3d_watch --version
```

Powinieneś zobaczyć: `1.0.2` (numer wersji).

## Jak czytać polecenia na tych stronach {#how-to-read-the-commands-on-these-pages}

- Słowa w `<nawiasach ostrokątnych>` są symbolami zastępczymi: wpisz zamiast nich własny plik albo folder,
  bez nawiasów. `python -m heat3d_watch sessions --game <name>` oznacza, że zastępujesz część w nawiasach.
- Ścieżka ze spacjami idzie w cudzysłowy: `"C:\My Games\my file"`.
- Linie zaczynające się od `#` w przykładach są komentarzami; nie wpisujesz ich.
- Sukces wygląda tak: po `python -m heat3d_watch games` pojawia się tabela z jedną linią na grę.

## Typowe błędy {#common-errors}

| Widzisz | Zrób to |
|---|---|
| `'python' is not recognized` albo `command not found` | Python nie jest w PATH: uruchom instalator ponownie i zaznacz **Add python.exe to PATH**, potem otwórz nowy terminal. W macOS/Linux spróbuj `python3`. |
| `No module named ...` | krok 4 został pominięty albo wykonano go w innym folderze: wejdź poleceniem `cd` do folderu narzędzia i uruchom go ponownie. |
| `pip is not recognized` | zamiast `pip ...` użyj `python -m pip ...`. |
| `No such file or directory` / `can't open file` | terminal jest w złym folderze albo ścieżka ma literówkę: sprawdź ją i ujmij ścieżki ze spacjami w cudzysłowy. |
| czerwony tekst kończący się linią `error:` | przeczytaj ostatnią linię: mówi, czego brakuje. Strona [Polecenia](../commands.md) wymienia komunikaty. |
