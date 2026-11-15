---
title: "Ako začať"
nav_order: 2
lang: "sk"
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Ako začať {#before-you-start}

Nikdy ste nepracovali s príkazovým riadkom? Táto stránka vás za asi desať minút dostane od nuly
k funkčnému 3DHeat Watcher. Píšete príkazy do *terminálu*, okna, kde napíšete riadok a stlačíte Enter.

## 1. Nainštalujte Python {#install-python}

1. Stiahnite Python 3.10 alebo novší z <https://www.python.org/downloads/>.
2. Spustite inštalátor. Na prvej obrazovke zaškrtnite **Add python.exe to PATH**,
   potom kliknite na **Install Now**.
3. Overte to: otvorte terminál (krok 3) a napíšte `python --version`. Mali by ste
   vidieť `Python 3.` a číslo 10 alebo vyššie.

Na Linuxe alebo macOS je Python zvyčajne nainštalovaný: tam, kde tieto stránky píšu `python`, použite `python3`.

## 2. Získajte 3DHeat Watcher {#get-3dheat-watcher}

Stiahnite zip zo
[stránky vydaní](https://github.com/Holdi601/3DHeat-Watcher/releases) a rozbaľte ho, napríklad do
`C:\Tools\3DHeat-Watcher`. (Ak máte Git, funguje aj `git clone`.)

## 3. Otvorte terminál v tom priečinku {#open-a-terminal-in-that-folder}

- **Windows:** otvorte priečinok v Prieskumníkovi, kliknite na panel s adresou, napíšte
  `powershell` a stlačte Enter. Otvorí sa modré alebo čierne okno, už v tom
  priečinku.
- **macOS / Linux:** otvorte *Terminal* a napíšte `cd ` (s medzerou), presuňte
  priečinok do okna a stlačte Enter.

`cd <folder>` presunie terminál do iného priečinka. Všetky príkazy na týchto
stránkach sa píšu v priečinku nástroja.

## 4. Nainštalujte, čo potrebuje {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Na konci by ste mali vidieť `Successfully installed ...` (alebo `Requirement
already satisfied`).

## 5. Overte, že funguje {#check-it-works}

```bash
python -m heat3d_watch --version
```

Mali by ste vidieť: `1.0.2 (the version number)`.

## Ako čítať príkazy na týchto stránkach {#how-to-read-the-commands-on-these-pages}

- Slová v `<uhlových zátvorkách>` sú zástupné znaky: namiesto nich napíšte svoj súbor alebo priečinok
  bez zátvoriek. `python -m heat3d_watch sessions --game <name>` znamená,
  že nahradíte časť v zátvorkách.
- Cesta s medzerami patrí do úvodzoviek: `"C:\My Games\my file"`.
- Riadky začínajúce na `#` v príkladoch sú komentáre; nepíšte ich.
- Úspech vyzerá takto: po `python -m heat3d_watch games` tabuľka s jedným riadkom na hru.

## Bežné chyby {#common-errors}

| Vidíte | Čo robiť |
|---|---|
| `'python' is not recognized` alebo `command not found` | Python nie je v PATH: spustite inštalátor znova a zaškrtnite **Add python.exe to PATH**, potom otvorte nový terminál. Na macOS/Linuxe skúste `python3`. |
| `No module named ...` | krok 4 sa preskočil alebo sa spustil v inom priečinku: `cd` do priečinka nástroja a spustite ho znova. |
| `pip is not recognized` | použite `python -m pip ...` namiesto `pip ...`. |
| `No such file or directory` / `can't open file` | terminál je v zlom priečinku, alebo je cesta zle napísaná: skontrolujte ju a cesty s medzerami dajte do úvodzoviek. |
| červený text končiaci riadkom `error:` | prečítajte posledný riadok: hovorí, čo chýba. Stránka [Príkazy](commands.md) uvádza hlásenia. |
