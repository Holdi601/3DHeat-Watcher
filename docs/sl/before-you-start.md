---
title: "Preden začneš"
nav_order: 2
lang: "sl"
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Preden začneš {#before-you-start}

Še niste vajeni ukazne vrstice? Ta stran vas v približno desetih minutah vodi od nič do delujočega
3DHeat Watcherja. Ukaze vtipkate v *terminal*, okno, kjer napišete vrstico in pritisnete Enter.

## 1. Namesti Python {#install-python}

1. Prenesite Python 3.10 ali novejši z <https://www.python.org/downloads/>.
2. Zaženite namestitev. Na prvem zaslonu obkljukajte **Add python.exe to PATH**,
   nato kliknite **Install Now**.
3. Preverite: odprite terminal (korak 3) in vtipkajte `python --version`. Videti bi morali
   `Python 3.` in številko 10 ali več.

Na Linuxu ali macOS je Python ponavadi že nameščen: kjer te strani pišejo `python`, uporabite `python3`.

## 2. Pridobi 3DHeat Watcher {#get-3dheat-watcher}

Prenesite zip z [strani izdaj](https://github.com/Holdi601/3DHeat-Watcher/releases) in ga razpakirajte, na primer v
`C:\Tools\3DHeat-Watcher`. (Če imate Git, deluje tudi `git clone`.)

## 3. Odpri terminal v tej mapi {#open-a-terminal-in-that-folder}

- **Windows:** odprite mapo v Raziskovalcu, kliknite v vrstico z naslovom, vtipkajte `powershell` in pritisnite Enter.
  Odpre se okno (modro ali črno), ki je že v tej mapi.
- **macOS / Linux:** odprite *Terminal* in vtipkajte `cd ` (s presledkom), povlecite mapo v okno in pritisnite Enter.

`cd <mapa>` premakne terminal v drugo mapo. Vsi ukazi na teh straneh se vtipkajo v mapi orodja.

## 4. Namesti, kar potrebuje {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Na koncu bi morali videti `Successfully installed ...` (ali `Requirement already satisfied`).

## 5. Preveri, da deluje {#check-it-works}

```bash
python -m heat3d_watch --version
```

Videti bi morali: `1.0.2 (številka različice)`.

## Kako brati ukaze na teh straneh {#how-to-read-the-commands-on-these-pages}

- Besede v `<kotnih oklepajih>` so nadomestila: namesto njih vtipkajte svojo datoteko ali mapo, brez oklepajev.
  `python -m heat3d_watch sessions --game <ime>` pomeni, da zamenjate oklepajni del.
- Pot s presledki gre v narekovaje: `"C:\Moje igre\moja datoteka"`.
- Vrstice, ki se v primerih začnejo s `#`, so komentarji; ne vtipkaš jih.
- Uspeh izgleda tako: po `python -m heat3d_watch games` tabela z eno vrstico na igro.

## Pogoste napake {#common-errors}

| Kar vidiš | Kaj storiti |
|---|---|
| `'python' is not recognized` ali `command not found` | Python ni na PATH: znova zaženite namestitev in obkljukajte **Add python.exe to PATH**, nato odprite nov terminal. Na macOS/Linux poskusi `python3`. |
| `No module named ...` | korak 4 je bil preskočen ali zagnan v drugi mapi: z `cd` pojdite v mapo orodja in ga zaženite znova. |
| `pip is not recognized` | namesto `pip ...` uporabi `python -m pip ...`. |
| `No such file or directory` / `can't open file` | terminal je v napačni mapi ali je pot napačno napisana: preverite jo in dajte poti s presledki v narekovaje. |
| rdeče besedilo, ki se konča z vrstico `error:` | preberite zadnjo vrstico: pove, kaj manjka. Stran [Ukazi](commands.md) navaja sporočila. |
