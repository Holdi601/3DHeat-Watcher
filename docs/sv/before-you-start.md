---
title: Innan du börjar
nav_order: 2
lang: "sv"
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Innan du börjar {#before-you-start}

Har du aldrig använt kommandoraden förut? Den här sidan tar dig från noll till en fungerande
3DHeat Watcher på ungefär tio minuter. Du skriver kommandon i en *terminal*, ett fönster
där du skriver en rad och trycker på Enter.

## 1. Installera Python {#install-python}

1. Ladda ner Python 3.10 eller senare från <https://www.python.org/downloads/>.
2. Kör installationsprogrammet. På första skärmen kryssar du i **Add python.exe to PATH**,
   och klickar sedan på **Install Now**.
3. Kontrollera: öppna en terminal (steg 3) och skriv `python --version`. Du bör
   se `Python 3.` och ett tal på 10 eller mer.

På Linux eller macOS är Python oftast redan installerat: använd `python3` där
sidorna säger `python`.

## 2. Hämta 3DHeat Watcher {#get-3dheat-watcher}

Ladda ner zip-filen från
[utgivningssidan](https://github.com/Holdi601/3DHeat-Watcher/releases) och packa upp den, till
exempel till `C:\Tools\3DHeat-Watcher`. (Har du Git fungerar `git clone` också.)

## 3. Öppna en terminal i den mappen {#open-a-terminal-in-that-folder}

- **Windows:** öppna mappen i Utforskaren, klicka i adressfältet, skriv
  `powershell` och tryck på Enter. Ett blått eller svart fönster öppnas, redan i
  den mappen.
- **macOS / Linux:** öppna *Terminal* och skriv `cd ` (med ett mellanslag), dra
  mappen till fönstret, tryck på Enter.

`cd <folder>` flyttar terminalen till en annan mapp. Alla kommandon på de här
sidorna skrivs i verktygets egen mapp.

## 4. Installera det som behövs {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Du bör se `Successfully installed ...` på slutet (eller `Requirement
already satisfied`).

## 5. Kontrollera att det fungerar {#check-it-works}

```bash
python -m heat3d_watch --version
```

Du bör se: `1.0.2 (versionsnumret)`.

## Så läser du kommandona på de här sidorna {#how-to-read-the-commands-on-these-pages}

- Ord inom `<vinkelparenteser>` är platshållare: skriv in din egen fil eller mapp
  i stället, utan parenteserna. I `python -m heat3d_watch sessions --game <name>` ersätter du `<name>` med spelets namn.
- En sökväg med mellanslag skrivs inom citattecken: `"C:\My Games\my file"`.
- Rader som börjar med `#` i exemplen är kommentarer; du skriver dem inte.
- Lyckat ser ut så här: efter `python -m heat3d_watch games`, en tabell med en rad per spel.

## Vanliga fel {#common-errors}

| Du ser | Gör så här |
|---|---|
| `'python' is not recognized` eller `command not found` | Python finns inte på PATH: kör installationsprogrammet igen och kryssa i **Add python.exe to PATH**, öppna sedan en ny terminal. På macOS/Linux prova `python3`. |
| `No module named ...` | steg 4 hoppades över eller kördes i en annan mapp: `cd` till verktygets mapp och kör igen. |
| `pip is not recognized` | använd `python -m pip ...` i stället för `pip ...`. |
| `No such file or directory` / `can't open file` | terminalen står i fel mapp, eller sökvägen är felstavad: kontrollera den, och sätt sökvägar med mellanslag inom citattecken. |
| röd text som slutar med en `error:`-rad | läs sista raden: den säger vad som saknas. Sidan [Kommandon](commands.md) listar meddelandena. |
