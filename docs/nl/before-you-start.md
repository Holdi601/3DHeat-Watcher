---
title: Voordat je begint
nav_order: 2
lang: "nl"
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Voordat je begint {#before-you-start}

Nog nooit met de opdrachtregel gewerkt? Deze pagina brengt je in ongeveer tien minuten van niets naar
een werkende 3DHeat Watcher. Je typt opdrachten in een *terminal*, een venster
waarin je een regel schrijft en op Enter drukt.

## 1. Installeer Python {#install-python}

1. Download Python 3.10 of later via <https://www.python.org/downloads/>.
2. Start het installatieprogramma. Vink op het eerste scherm **Add python.exe to PATH** aan,
   en klik dan op **Install Now**.
3. Controleer het: open een terminal (stap 3) en typ `python --version`. Je ziet
   `Python 3.` en een getal van 10 of hoger.

Op Linux of macOS is Python meestal al geïnstalleerd: gebruik `python3` waar deze pagina's `python` schrijven.

## 2. Haal 3DHeat Watcher op {#get-3dheat-watcher}

Download de zip van de
[Releases-pagina](https://github.com/Holdi601/3DHeat-Watcher/releases) en pak hem uit, bijvoorbeeld
naar `C:\Tools\3DHeat-Watcher`. (Heb je Git, dan werkt `git clone` ook.)

## 3. Open een terminal in die map {#open-a-terminal-in-that-folder}

- **Windows:** open de map in Verkenner, klik in de adresbalk, typ
  `powershell` en druk op Enter. Er opent een blauw of zwart venster, al in
  die map.
- **macOS / Linux:** open *Terminal* en typ `cd ` (met een spatie), sleep de
  map in het venster en druk op Enter.

`cd <folder>` verplaatst de terminal naar een andere map. Alle commando's op deze
pagina's typ je in de eigen map van het hulpmiddel.

## 4. Installeer wat het nodig heeft {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Je ziet `Successfully installed ...` aan het eind (of `Requirement
already satisfied`).

## 5. Controleer of het werkt {#check-it-works}

```bash
python -m heat3d_watch --version
```

Je ziet het versienummer, bijvoorbeeld `1.0.2`.

## Zo lees je de commando's op deze pagina's {#how-to-read-the-commands-on-these-pages}

- Woorden tussen `<punthaken>` zijn plaatsaanduidingen: typ in plaats daarvan je eigen bestand of map,
  zonder de haken. `python -m heat3d_watch sessions --game <name>` betekent
  dat je het gedeelte tussen haken vervangt.
- Een pad met spaties hoort tussen aanhalingstekens: `"C:\My Games\my file"`.
- Regels die in de voorbeelden met `#` beginnen, zijn opmerkingen; die typ je niet.
- Succes ziet er zo uit: na `python -m heat3d_watch games` een tabel met één regel per spel.

## Veelvoorkomende fouten {#common-errors}

| Je ziet | Doe dit |
|---|---|
| `'python' is not recognized` of `command not found` | Python staat niet in PATH: voer het installatieprogramma opnieuw uit en vink **Add python.exe to PATH** aan, en open daarna een nieuwe terminal. Op macOS/Linux probeer je `python3`. |
| `No module named ...` | stap 4 is overgeslagen of in een andere map uitgevoerd: ga met `cd` naar de map van het hulpmiddel en voer het opnieuw uit. |
| `pip is not recognized` | gebruik `python -m pip ...` in plaats van `pip ...`. |
| `No such file or directory` / `can't open file` | de terminal staat in de verkeerde map, of het pad is verkeerd getypt: controleer het, en zet paden met spaties tussen aanhalingstekens. |
| rode tekst die eindigt op een `error:`-regel | lees de laatste regel: die zegt wat er ontbreekt. De pagina [Commando's](../commands.md) somt de meldingen op. |
