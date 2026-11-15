---
title: "Než začnete"
nav_order: 2
lang: "cs"
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Než začnete {#before-you-start}

Nikdy jste nepracovali s příkazovým řádkem? Tato stránka vás provede od nuly až k funkčnímu
3DHeat Watcheru zhruba za deset minut. Píšete příkazy do *terminálu*, okna, kde napíšete řádek
a stisknete Enter.

## 1. Nainstalujte Python {#install-python}

1. Stáhněte Python 3.10 nebo novější z <https://www.python.org/downloads/>.
2. Spusťte instalátor. Na první obrazovce zaškrtněte **Add python.exe to PATH**,
   pak klikněte na **Install Now**.
3. Ověřte to: otevřete terminál (krok 3) a napište `python --version`. Měli byste
   vidět `Python 3.` a číslo 10 nebo vyšší.

Na Linuxu nebo macOS bývá Python obvykle nainstalovaný: kde tyto stránky píšou `python`, napište `python3`.

## 2. Získejte 3DHeat Watcher {#get-3dheat-watcher}

Stáhněte zip ze stránky [Releases](https://github.com/Holdi601/3DHeat-Watcher/releases) a rozbalte ho,
například do `C:\Tools\3DHeat-Watcher`. (Pokud máte Git, funguje i `git clone`.)

## 3. Otevřete terminál ve složce {#open-a-terminal-in-that-folder}

- **Windows:** otevřete složku v Průzkumníku, klikněte do adresního řádku, napište
  `powershell` a stiskněte Enter. Otevře se modré nebo černé okno, které už bude
  v této složce.
- **macOS / Linux:** otevřete *Terminal* a napište `cd ` (s mezerou), přetáhněte
  složku do okna a stiskněte Enter.

`cd <folder>` přesune terminál do jiné složky. Všechny příkazy na těchto stránkách se píší
ve složce nástroje.

## 4. Nainstalujte, co potřebuje {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Na konci byste měli vidět `Successfully installed ...` (nebo `Requirement
already satisfied`).

## 5. Ověřte, že funguje {#check-it-works}

```bash
python -m heat3d_watch --version
```

Měli byste vidět: `1.0.2 (číslo verze)`.

## Jak číst příkazy na těchto stránkách {#how-to-read-the-commands-on-these-pages}

- Slova v `<lomených závorkách>` jsou zástupné texty: místo nich napište svůj vlastní soubor
  nebo složku, bez závorek. `python -m heat3d_watch sessions --game <name>` znamená,
  že nahradíte část v závorkách.
- Cesta s mezerami patří do uvozovek: `"C:\My Games\my file"`.
- Řádky v příkladech začínající na `#` jsou poznámky; nepíšete je.
- Úspěch vypadá takto: po `python -m heat3d_watch games` tabulka s jedním řádkem na každou hru.

## Časté chyby {#common-errors}

| Zobrazí se | Co udělat |
|---|---|
| `'python' is not recognized` nebo `command not found` | Python není v PATH: spusťte instalátor znovu a zaškrtněte **Add python.exe to PATH**, pak otevřete nový terminál. Na macOS/Linuxu zkuste `python3`. |
| `No module named ...` | krok 4 se přeskočil, nebo běžel v jiné složce: `cd` do složky nástroje a spusťte ho znovu. |
| `pip is not recognized` | místo `pip ...` napište `python -m pip ...`. |
| `No such file or directory` / `can't open file` | terminál je ve špatné složce, nebo je cesta přepsaná: zkontrolujte ji a cesty s mezerami dejte do uvozovek. |
| červený text končící řádkem `error:` | přečtěte poslední řádek: říká, co chybí. Stránka [Příkazy](../commands.md) uvádí hlášení. |
