---
title: "Zanim zaczniesz"
nav_order: 2
lang: "pl"
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Zanim zaczniesz {#before-you-start}

Nigdy nie korzystano z wiersza poleceń? Ta strona prowadzi krok po kroku od zera do działającego
3DHeat Watcher w około dziesięć minut. Polecenia wpisuje się w *terminalu*, oknie, w którym pisze się wiersz
i naciska Enter.

## 1. Zainstalować Pythona {#install-python}

1. Pobrać Pythona 3.10 lub nowszego ze strony <https://www.python.org/downloads/>.
2. Uruchomić instalator. Na pierwszym ekranie zaznaczyć **Add python.exe to PATH**,
   a potem kliknąć **Install Now**.
3. Sprawdzić: otworzyć terminal (krok 3) i wpisać `python --version`. Powinno pojawić się
   `Python 3.` i numer 10 lub wyższy.

W Linuksie albo macOS Python zwykle jest już zainstalowany: tam, gdzie te strony piszą `python`, używa się `python3`.

## 2. Pobrać 3DHeat Watcher {#get-3dheat-watcher}

Pobrać zip ze strony [Releases](https://github.com/Holdi601/3DHeat-Watcher/releases) i rozpakować go,
na przykład do `C:\Tools\3DHeat-Watcher`. (Jeśli jest Git, działa też `git clone`.)

## 3. Otworzyć terminal w tym folderze {#open-a-terminal-in-that-folder}

- **Windows:** otworzyć folder w Eksploratorze plików, kliknąć pasek adresu, wpisać
  `powershell` i nacisnąć Enter. Otworzy się niebieskie lub czarne okno, już w tym folderze.
- **macOS / Linux:** otworzyć *Terminal* i wpisać `cd ` (ze spacją), przeciągnąć
  folder do okna i nacisnąć Enter.

`cd <folder>` przenosi terminal do innego folderu. Wszystkie polecenia na tych
stronach wpisuje się w folderze samego narzędzia.

## 4. Zainstalować, czego potrzeba {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Na końcu powinno pojawić się `Successfully installed ...` (albo `Requirement
already satisfied`).

## 5. Sprawdzić, czy działa {#check-it-works}

```bash
python -m heat3d_watch --version
```

Powinien pojawić się numer wersji: `1.0.2`.

## Jak czytać polecenia na tych stronach {#how-to-read-the-commands-on-these-pages}

- Słowa w `<nawiasach ostrokątnych>` są symbolami zastępczymi: w ich miejsce wpisuje się własny plik albo folder,
  bez nawiasów. `python -m heat3d_watch sessions --game <name>` oznacza, że zastępuje się część w nawiasach.
- Ścieżkę ze spacjami ujmuje się w cudzysłów: `"C:\My Games\my file"`.
- Linie zaczynające się od `#` w przykładach są komentarzami; nie wpisuje się ich.
- Sukces wygląda tak: po `python -m heat3d_watch games` pojawia się tabela z jedną linią na grę.

## Typowe błędy {#common-errors}

| Widać | Co zrobić |
|---|---|
| `'python' is not recognized` albo `command not found` | Python nie jest w PATH: uruchomić instalator ponownie, zaznaczyć **Add python.exe to PATH**, potem otworzyć nowy terminal. W macOS/Linux spróbować `python3`. |
| `No module named ...` | krok 4 został pominięty albo wykonano go w innym folderze: przejść poleceniem `cd` do folderu narzędzia i uruchomić go ponownie. |
| `pip is not recognized` | zamiast `pip ...` używać `python -m pip ...`. |
| `No such file or directory` / `can't open file` | terminal jest w złym folderze albo ścieżka ma literówkę: sprawdzić ją i ująć ścieżki ze spacjami w cudzysłów. |
| czerwony tekst kończący się linią `error:` | przeczytać ostatnią linię: mówi, czego brakuje. Strona [Polecenia](commands.md) wymienia komunikaty. |
