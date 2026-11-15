---
title: Qabel ma tibda
nav_order: 2
lang: mt
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Qabel ma tibda {#before-you-start}

Ġdid mal-linja tal-kmandi? Din il-paġna tieħdok minn xejn sa 3DHeat Watcher li jaħdem f'madwar
għaxar minuti. Tittajpja kmandi f'*terminal*, tieqa fejn tikteb linja u tagħfas Enter.

## 1. Installa Python {#install-python}

1. Niżżel Python 3.10 jew aktar ġdid minn <https://www.python.org/downloads/>.
2. Ħaddem l-installer. Fl-ewwel skrin immarka **Add python.exe to PATH**,
   imbagħad ikklikkja **Install Now**.
3. Iċċekkjah: iftaħ terminal (pass 3) u ittajpja `python --version`. Għandek
   tara `Python 3.` u numru ta' 10 jew aktar.

Fuq Linux jew macOS, Python spiss ikun diġà installat: uża `python3` fejn
dawn il-paġni jgħidu `python`.

## 2. Ġib 3DHeat Watcher {#get-3dheat-watcher}

Niżżel iz-zip mill-
[paġna tar-Releases](https://github.com/Holdi601/3DHeat-Watcher/releases) u ħollu, pereżempju
f'`C:\Tools\3DHeat-Watcher`. (Jekk għandek Git, `git clone` jaħdem ukoll.)

## 3. Iftaħ terminal f'dak il-folder {#open-a-terminal-in-that-folder}

- **Windows:** iftaħ il-folder fil-File Explorer, ikklikkja l-bar tal-indirizz, ittajpja
  `powershell` u agħfas Enter. Tiftaħ tieqa blu jew sewda, diġà f'dak il-
  folder.
- **macOS / Linux:** iftaħ *Terminal* u ittajpja `cd ` (b'spazju), kaxkar il-
  folder fit-tieqa, agħfas Enter.

`cd <folder>` ibiddel it-terminal għal folder ieħor. Kull kmand f'dawn il-
paġni jiġi ttajpjat fil-folder proprju tal-għodda.

## 4. Installa dak li teħtieġ {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Fl-aħħar għandek tara `Successfully installed ...` (jew `Requirement
already satisfied`).

## 5. Iċċekkja li taħdem {#check-it-works}

```bash
python -m heat3d_watch --version
```

Għandek tara: `1.0.2 (the version number)`.

## Kif taqra l-kmandi f'dawn il-paġni {#how-to-read-the-commands-on-these-pages}

- Kliem bejn `<parentesi angolari>` huma placeholders: ittajpja l-fajl jew il-folder tiegħek
  minflok, mingħajr il-parentesi. `python -m heat3d_watch sessions --game <name>` ifisser
  li tibdel il-parti bejn il-parentesi.
- Triq b'spazji tmur bejn virgoletti: `"C:\My Games\my file"`.
- Linji li jibdew b'`#` fl-eżempji huma kummenti; ma tittajpjahomx.
- Is-suċċess jidher hekk: wara `python -m heat3d_watch games`, tabella b'linja waħda għal kull logħba.

## Żbalji komuni {#common-errors}

| Tara | Agħmel dan |
|---|---|
| `'python' is not recognized` jew `command not found` | Python mhuwiex fuq PATH: erġa' ħaddem l-installer u immarka **Add python.exe to PATH**, imbagħad iftaħ terminal ġdid. Fuq macOS/Linux ipprova `python3`. |
| `No module named ...` | il-pass 4 tqabbeż jew inħadem f'folder ieħor: mur b'`cd` fil-folder tal-għodda u erġa' ħaddmu. |
| `pip is not recognized` | uża `python -m pip ...` minflok `pip ...`. |
| `No such file or directory` / `can't open file` | it-terminal qiegħed fil-folder ħażin, jew it-triq hija ħażina: iċċekkjaha, u poġġi triq b'spazji bejn virgoletti. |
| test aħmar li jispiċċa b'linja `error:` | aqra l-aħħar linja: tgħid x'inhu nieqes. Il-paġna [Kmandi](../commands.md) telenka l-messaġġi. |
