---
title: "Bevor du anfängst"
nav_order: 2
lang: de
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Bevor du anfängst {#before-you-start}

Neu in der Kommandozeile? Diese Seite bringt dich von nichts zu einem funktionierenden
3DHeat Watcher in etwa zehn Minuten. Du tippst Befehle in ein *Terminal*, ein Fenster, in dem du eine Zeile
schreibst und Enter drückst.

## 1. Python installieren {#install-python}

1. Lade Python 3.10 oder neuer von <https://www.python.org/downloads/> herunter.
2. Starte das Installationsprogramm. Setze auf dem ersten Bildschirm den Haken bei **Add python.exe to PATH**,
   dann klicke auf **Install Now**.
3. Prüfe es: Öffne ein Terminal (Schritt 3) und tippe `python --version`. Du solltest
   `Python 3.` und eine Zahl 10 oder höher sehen.

Unter Linux oder macOS ist Python meist schon installiert: Verwende `python3`, wo diese Seiten `python` schreiben.

## 2. 3DHeat Watcher holen {#get-3dheat-watcher}

Lade das ZIP von der [Releases-Seite](https://github.com/Holdi601/3DHeat-Watcher/releases) herunter und entpacke es,
zum Beispiel nach `C:\Tools\3DHeat-Watcher`. (Wenn du Git hast, funktioniert auch `git clone`.)

## 3. Ein Terminal in diesem Ordner öffnen {#open-a-terminal-in-that-folder}

- **Windows:** Öffne den Ordner im Explorer, klicke in die Adressleiste, tippe
  `powershell` und drücke Enter. Ein blaues oder schwarzes Fenster öffnet sich, schon in diesem Ordner.
- **macOS / Linux:** Öffne *Terminal* und tippe `cd ` (mit einem Leerzeichen), ziehe den Ordner
  in das Fenster, drücke Enter.

`cd <Ordner>` wechselt das Terminal in einen anderen Ordner. Alle Befehle auf diesen Seiten tippst du im Ordner
des Werkzeugs selbst.

## 4. Installieren, was es braucht {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Am Ende solltest du `Successfully installed ...` sehen (oder `Requirement
already satisfied`).

## 5. Prüfen, ob es funktioniert {#check-it-works}

```bash
python -m heat3d_watch --version
```

Du solltest die Versionsnummer sehen, zum Beispiel `1.0.2`.

## So liest du die Befehle auf diesen Seiten {#how-to-read-the-commands-on-these-pages}

- Wörter in `<spitzen Klammern>` sind Platzhalter: Tippe deine eigene Datei oder deinen eigenen Ordner
  statt dessen, ohne die Klammern. `python -m heat3d_watch sessions --game <name>` heißt,
  du ersetzt den Teil in Klammern.
- Ein Pfad mit Leerzeichen kommt in Anführungszeichen: `"C:\My Games\my file"`.
- Zeilen, die in den Beispielen mit `#` beginnen, sind Kommentare; du tippst sie nicht.
- Erfolg sieht so aus: nach `python -m heat3d_watch games` eine Tabelle mit einer Zeile pro Spiel.

## Häufige Fehler {#common-errors}

| Du siehst | Tu das |
|---|---|
| `'python' is not recognized` oder `command not found` | Python ist nicht im PATH: Führe das Installationsprogramm noch einmal aus und hake **Add python.exe to PATH** an, dann öffne ein neues Terminal. Unter macOS/Linux probiere `python3`. |
| `No module named ...` | Schritt 4 wurde übersprungen oder im falschen Ordner ausgeführt: `cd` in den Ordner des Werkzeugs und führe es noch einmal aus. |
| `pip is not recognized` | Verwende `python -m pip ...` statt `pip ...`. |
| `No such file or directory` / `can't open file` | das Terminal ist im falschen Ordner, oder der Pfad ist falsch geschrieben: prüfe ihn, und setze Pfade mit Leerzeichen in Anführungszeichen. |
| roter Text, der mit einer `error:`-Zeile endet | lies die letzte Zeile: Sie sagt, was fehlt. Die Seite [Befehle](commands.md) listet die Meldungen. |
