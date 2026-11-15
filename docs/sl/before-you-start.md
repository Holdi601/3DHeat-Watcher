---
title: "Preden začneš"
nav_order: 2
lang: sl
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Preden začneš {#before-you-start}

Še nisi vajen ukazne vrstice? Ta stran te v približno desetih minutah vodi od nič do delujočega
3DHeat Watcherja. Ukaze vtipkaš v *terminal*, okno, kjer napišeš vrstico in pritisneš Enter.

## 1. Namesti Python {#install-python}

1. Prenesi Python 3.10 ali novejši z <https://www.python.org/downloads/>.
2. Zaženi namestitev. Na prvem zaslonu obkljukaj **Add python.exe to PATH**,
   nato klikni **Install Now**.
3. Preveri: odpri terminal (korak 3) in vtipkaj `python --version`. Videti bi moral
   `Python 3.` in številko 10 ali več.

Na Linuxu ali macOS je Python ponavadi že nameščen: kjer te strani pišejo `python`, uporabi `python3`.

## 2. Pridobi 3DHeat Watcher {#get-3dheat-watcher}

Prenesi zip z [strani izdaj](https://github.com/Holdi601/3DHeat-Watcher/releases) in ga razpakiraj, na primer v
`C:\Tools\3DHeat-Watcher`. (Če imaš Git, deluje tudi `git clone`.)

## 3. Odpri terminal v tej mapi {#open-a-terminal-in-that-folder}

- **Windows:** odpri mapo v Raziskovalcu, klikni v vrstico z naslovom, vtipkaj `powershell` in pritisni Enter.
  Odpre se okno (modro ali črno), ki je že v tej mapi.
- **macOS / Linux:** odpri *Terminal* in vtipkaj `cd ` (s presledkom), povleci mapo v okno in pritisni Enter.

`cd <mapa>` premakne terminal v drugo mapo. Vsi ukazi na teh straneh se vtipkajo v mapi orodja.

## 4. Namesti, kar potrebuje {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Na koncu bi moral videti `Successfully installed ...` (ali `Requirement already satisfied`).

## 5. Preveri, da deluje {#check-it-works}

```bash
python -m heat3d_watch --version
```

Videti bi moral: `1.0.2 (številka različice)`.

## Kako brati ukaze na teh straneh {#how-to-read-the-commands-on-these-pages}

- Besede v `<kotnih oklepajih>` so nadomestila: namesto njih vtipkaj svojo datoteko ali mapo, brez oklepajev.
  `python -m heat3d_watch sessions --game <ime>` pomeni, da zamenjaš oklepajni del.
- Pot s presledki gre v narekovaje: `"C:\Moje igre\moja datoteka"`.
- Vrstice, ki se v primerih začnejo s `#`, so komentarji; ne vtipkaš jih.
- Uspeh izgleda tako: po `python -m heat3d_watch games` tabela z eno vrstico na igro.

## Pogoste napake {#common-errors}

| Kar vidiš | Kaj storiti |
|---|---|
| `'python' is not recognized` ali `command not found` | Python ni na PATH: znova zaženi namestitev in obkljukaj **Add python.exe to PATH**, nato odpri nov terminal. Na macOS/Linux poskusi `python3`. |
| `No module named ...` | korak 4 je bil preskočen ali zagnan v drugi mapi: z `cd` pojdi v mapo orodja in ga zaženi znova. |
| `pip is not recognized` | namesto `pip ...` uporabi `python -m pip ...`. |
| `No such file or directory` / `can't open file` | terminal je v napačni mapi ali je pot napačno napisana: preveri jo in daj poti s presledki v narekovaje. |
| rdeče besedilo, ki se konča z vrstico `error:` | preberi zadnjo vrstico: pove, kaj manjka. Stran [Ukazi](../commands.md) navaja sporočila. |
