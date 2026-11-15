---
title: Før du starter
nav_order: 2
lang: "no"
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Før du starter {#before-you-start}

Ny til kommandolinjen? Denne siden tar deg fra null til en fungerende
3DHeat Watcher på omtrent ti minutter. Du skriver kommandoer inn i en *terminal*, et vindu
der du skriver en linje og trykker Enter.

## 1. Installer Python {#install-python}

1. Last ned Python 3.10 eller nyere fra <https://www.python.org/downloads/>.
2. Kjør installasjonen. På første skjerm, kryss av **Add python.exe to PATH**,
   deretter klikk på **Install Now**.
3. Sjekk det: åpne en terminal (steg 3) og skriv `python --version`. Du bør
   se `Python 3.` og et tall på 10 eller mer.

På Linux eller macOS er Python vanligvis installert allerede: bruk `python3` der
disse sidene skriver `python`.

## 2. Skaff 3DHeat Watcher {#get-3dheat-watcher}

Last ned zip-filen fra
[Utgivelser-siden](https://github.com/Holdi601/3DHeat-Watcher/releases) og pakk den ut, for
eksempel til `C:\Tools\3DHeat-Watcher`. (Har du Git, fungerer `git clone` også.)

## 3. Åpne en terminal i den mappen {#open-a-terminal-in-that-folder}

- **Windows:** åpne mappen i Filutforsker, klikk i adressefeltet, skriv
  `powershell` og trykk Enter. Et blått eller svart vindu åpnes, allerede i
  den mappen.
- **macOS / Linux:** åpne *Terminal* og skriv `cd ` (med et mellomrom), dra
  mappen inn i vinduet, trykk Enter.

`cd <folder>` flytter terminalen til en annen mappe. Alle kommandoene på disse
sidene skrives i verktøyets egen mappe.

## 4. Installer det den trenger {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Du bør se `Successfully installed ...` til slutt (eller `Requirement
already satisfied`).

## 5. Sjekk at det virker {#check-it-works}

```bash
python -m heat3d_watch --version
```

Du bør se: `1.0.2 (versjonsnummeret)`.

## Slik leser du kommandoene på disse sidene {#how-to-read-the-commands-on-these-pages}

- Ord i `<vinkelparenteser>` er plassholdere: skriv inn din egen fil eller mappe i stedet,
  uten parentesene. `python -m heat3d_watch sessions --game <name>` betyr
  at du erstatter den innrammede delen.
- En sti med mellomrom står i anførselstegn: `"C:\My Games\my file"`.
- Linjer som starter med `#` i eksemplene er kommentarer; du skriver dem ikke.
- Suksess ser slik ut: etter `python -m heat3d_watch games`, en tabell med én linje per spill.

## Vanlige feil {#common-errors}

| Du ser | Gjør dette |
|---|---|
| `'python' is not recognized` eller `command not found` | Python er ikke på PATH: kjør installasjonen på nytt og kryss av **Add python.exe to PATH**, og åpne deretter en ny terminal. På macOS/Linux prøv `python3`. |
| `No module named ...` | steg 4 ble hoppet over, eller kjørt i en annen mappe: `cd` til verktøyets mappe og kjør det på nytt. |
| `pip is not recognized` | bruk `python -m pip ...` i stedet for `pip ...`. |
| `No such file or directory` / `can't open file` | terminalen står i feil mappe, eller stien er skrevet feil: sjekk den, og sett stier med mellomrom i anførselstegn. |
| rød tekst som slutter med en `error:`-linje | les siste linje: den sier hva som mangler. Siden [Kommandoer](commands.md) lister meldingene. |
