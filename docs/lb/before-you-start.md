---
title: "Ier Dir ufänkt"
nav_order: 2
lang: lb
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Ier Dir ufänkt {#before-you-start}

Nei op der Kommandozeil? Dës Säit bréngt Iech a ronn zéng Minutten vun Null bis bei en
funktionéierenden 3DHeat Watcher. Dir tippt Kommandoe an e *Terminal*, e Fënster,
wou Dir eng Zeil schreift an Enter dréckt.

## 1. Python installéieren {#install-python}

1. Luet Python 3.10 oder méi nei vun <https://www.python.org/downloads/> erof.
2. Startt den Installer. Um éischten Ecran **Add python.exe to PATH** ukräizen,
   dann op **Install Now** klicken.
3. Préift et: mécht e Terminal op (Schrëtt 3) an tippt `python --version`. Dir sollt
   `Python 3.` an eng Zuel vun 10 oder méi gesinn.

Op Linux oder macOS ass Python meeschtens schonn installéiert: benotzt `python3`, wou
dës Säiten `python` soen.

## 2. 3DHeat Watcher kréien {#get-3dheat-watcher}

Luet den Zip vun der
[Releases-Säit](https://github.com/Holdi601/3DHeat-Watcher/releases) erof an entpackt en, zum
Beispill no `C:\Tools\3DHeat-Watcher`. (Wann Dir Git hutt, geet `git clone` och.)

## 3. E Terminal an deem Dossier opmaachen {#open-a-terminal-in-that-folder}

- **Windows:** Mécht den Dossier am File Explorer op, klickt an d'Adressleist, tippt
  `powershell` an dréckt Enter. E bloe oder schwaarzt Fënster geet op, schonn an
  deem Dossier.
- **macOS / Linux:** Mécht *Terminal* op an tippt `cd ` (mat engem Espace), zitt den
  Dossier an d'Fënster, dréckt Enter.

`cd <folder>` setzt d'Terminal an en anere Dossier. All Kommandoe op dëse
Säite ginn am eegenen Dossier vum Tool getippt.

## 4. Installéieren, wat et brauch {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Dir sollt um Enn `Successfully installed ...` gesinn (oder `Requirement
already satisfied`).

## 5. Préift, ob et funktionéiert {#check-it-works}

```bash
python -m heat3d_watch --version
```

Dir sollt gesinn: `1.0.2 (the version number)`.

## Wéi Dir d'Kommandoe op dëse Säite liest {#how-to-read-the-commands-on-these-pages}

- Wierder an `<spëtze Klammeren>` si Platzhalter: tippt Är eege Datei oder Ären Dossier
  amplaz, ouni d'Klammeren. `python -m heat3d_watch sessions --game <name>` heescht,
  Dir ersetzt dat Deel an de Klammeren.
- E Wee mat Espacen kënnt an Ureechnungszeechen: `"C:\My Games\my file"`.
- Zeilen, déi an de Beispiller mat `#` ufänken, si Kommentarer; Dir tippt se net.
- Erfolleg gesäit esou aus: no `python -m heat3d_watch games` eng Tabell mat enger Zeil pro Spill.

## Heefeg Feeler {#common-errors}

| Dir gesitt | Maacht dat |
|---|---|
| `'python' is not recognized` oder `command not found` | Python ass net um PATH: startt den Installer nach eemol a kräizt **Add python.exe to PATH** un, dann mécht en neit Terminal op. Op macOS/Linux probéiert `python3`. |
| `No module named ...` | Schrëtt 4 gouf iwwersprong oder an engem anere Dossier gemaach: mat `cd` an den Dossier vum Tool goen an en nach eemol ausféieren. |
| `pip is not recognized` | benotzt `python -m pip ...` amplaz `pip ...`. |
| `No such file or directory` / `can't open file` | d'Terminal ass am falschen Dossier, oder de Wee ass falsch getippt: préift en, a setzt Weeër mat Espacen an Ureechnungszeechen. |
| roude Text, deen mat enger `error:`-Zeil ophält | liest déi lescht Zeil: si seet, wat feelt. D'Säit [Kommandoen](../commands.md) lëscht d'Meldungen op. |
