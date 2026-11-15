---
title: "Hearthstone (fișiere de jurnal)"
nav_order: 25
lang: "ro"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (fișiere de jurnal) {#hearthstone-log-files}

Cât timp jucați Hearthstone, watcher-ul citește fișierele pe care le scrie jocul și salvează ce s-a întâmplat, ca să le puteți vedea mai târziu ca statistici și ca o cronologie.

*Detalii tehnice: adaptorul `hearthstone`, tipul [`log`](sources-and-rules.md); rulează cât timp `Hearthstone.exe` rulează și caută date noi la fiecare 0,5 s.*

## Ce se înregistrează {#what-is-recorded}

- începutul și sfârșitul jocului, cu rezultatul (câștigat, pierdut, egal), numărul de ture și numele adversarului
- fiecare tură
- fiecare linie din Power.log și din celelalte jurnale, întreagă, în heat.raw.parquet
- jocuri, victorii, înfrângeri, egaluri, ture, cel mai lung joc

## De unde vine {#where-it-comes-from}

&lt;install>\Logs\Power.log (sau Logs\Hearthstone_\*\Power.log), scris odată ce %LOCALAPPDATA%\Blizzard\Hearthstone\log.config are o secțiune [Power], și orice alt \*.log pe care îl scrie jocul acolo

## Cum se activează {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` adaugă jurnalizarea [Power] în %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (copia de rezervă este păstrată); reporniți jocul

Scrieți comanda într-un terminal deschis în folderul watcher-ului (vedeți [Înainte de a începe](before-you-start.md)). Dacă eșuează, ultima linie spune de ce; [Instalarea și rularea](installing-and-running.md) acoperă cauzele obișnuite.

`python -m heat3d_watch setup hearthstone` arată fișierele pe care le-ar schimba; `python -m heat3d_watch setup hearthstone --apply` le schimbă, păstrând originalul ca `<file>.heat3d-backup` (vedeți [Comenzi](commands.md#setup)). Afișează `hearthstone: changed: ...` pentru fiecare schimbare sau `hearthstone: nothing to change` când este deja activat.

## Cum funcționează {#how-it-works}

Hearthstone: Power.log al jocului, pe care îl scrie odată ce `log.config` o cere.

Hearthstone citește `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` la pornire; o secțiune `[Power]` cu `LogLevel=1` și `FilePrinting=true` face ca jocul să scrie fiecare schimbare de stare a fiecărui joc în `<install>\Logs\Power.log` (clienții mai noi pun jurnalele fiecărei porniri într-un folder al lor, `Logs\Hearthstone_<date>\`). Aceasta este jurnalizarea de depanare documentată pe care o folosesc din 2014 uneltele de urmărire a pachetelor (configurarea Hearthstone Deck Tracker scrie aceeași secțiune). `setup()` adaugă secțiunea, cu o copie de rezervă a fișierului așa cum era; jocul trebuie repornit ca să o citească.

Liniile folosite, toate din `GameState.DebugPrintPower()` (liniile `PowerTaskList` le repetă și sunt sărite):

```text
D 20:15:01.1234567 GameState.DebugPrintPower() - CREATE_GAME
D 20:15:01.1234567 GameState.DebugPrintPower() -     Player EntityID=2 PlayerID=1 GameAccountId=[hi=1 lo=2]
D 20:15:01.1234567 GameState.DebugPrintGame() - PlayerID=1, PlayerName=Name#1234
D 20:15:02.1234567 GameState.DebugPrintPower() -     FULL_ENTITY - Updating [entityName=... id=4 zone=HAND
                   zonePos=0 cardId=CS2_029 player=1] CardID=CS2_029
D 20:16:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=TURN value=3
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=Name#1234 tag=PLAYSTATE value=WON
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=STATE value=COMPLETE
```

Partea jucătorului este cea a cărei mână de start are cărțile numite (cele ale adversarului sunt ascunse), altfel partea care nu este AI (contul 0) sau „UNKNOWN HUMAN PLAYER”. Liniile poartă doar ora din zi; data este cea de azi. Fără poziții.

Fiecare linie din Power.log este păstrată întreagă în sidecar-ul brut al sesiunii (regula convertorului 3DHeat), inclusiv repetările `PowerTaskList`, opțiunile, alegerile și actualizările de entități: `type` este metoda care a scris-o (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Orice alt jurnal pe care jocul îl scrie lângă el - `LoadingScreen.log`, `Decks.log`, `Zone.log`, `Arena.log`, ..., fiecare acolo când log.config o cere (uneltele de urmărire a pachetelor o fac des) - este urmărit la fel și păstrat cu numele său în `log`.

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | nu |
| Axa verticală | `y` |
| Unități | nu se înregistrează poziții |
| Oglindit pentru vizualizator | niciunul |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, ca vizualizatorul 3DHeat să rotească și să scaleze rândurile singur; vedeți [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)”.
- Tipul `log`: citește doar ce oferă jocul sau platforma (fișiere pe care le scrie jocul cât timp rulează), deci înregistrează și în jocul online, nu doar offline; marcajul decide doar dacă memoria poate fi citită vreodată.
- Memoria: **niciodată** citită de acest adaptor. Doar adaptoarele de tip `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online; vedeți [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul adaptorului le setează pe nume (fiecare `stats` din sesiune, în `meta.json`, și tabelul `stats` din `watcher.sqlite`):

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează” de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- `CREATE_GAME`, jucătorii (entitate, id de jucător, cont; contul 0 este AI-ul) și numele lor (`DebugPrintGame`)
- a cui este partea jucătorului, din cărțile numite ale mâinii de start
- `TAG_CHANGE` pentru TURN, PLAYSTATE (won, lost, tied) și STATE COMPLETE: ture, rezultat, adversar

**Păstrat brut**

- fiecare linie din Power.log întreagă, `type` = metoda care a scris-o (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` unde a devenit rând: fiecare carte jucată, trasă și dezvăluită, fiecare schimbare de etichetă, atac, opțiune și alegere este aici, încă nu în rânduri
- fiecare linie din celelalte jurnale din același folder (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... - orice activează log.config), cu aceleași `type`-uri, cu numele jurnalului în `log`
- o linie fără nivel și oră a zilei ca `untimed`, una fără metodă ca `untagged`

**Nu este disponibil**

- poziții: un joc de cărți nu are
- cărțile ascunse ale adversarului: jurnalul numește o carte doar când este dezvăluită
- jurnalele pe care log.config nu le activează: `setup` cere doar [Power]; celelalte jurnale apar când o altă unealtă (un urmăritor de pachete) le-a activat
- jurnalele lansărilor anterioare: fiecare lansare scrie un folder nou; cele mai vechi decât această rulare a jocului nu se mai citesc

**Dimensiune**: Power.log cu Verbose are aproximativ 1-5 MB pe joc, 10-40 MB pe oră de joc; celelalte jurnale adaugă puțin; zstd din heat.raw.parquet le face cam o zecime sau mai puțin (liniile se repetă mult)

## Verificat {#verified}

testat pe linii sintetice de Power.log în formatul jocului; netestat cu jocul

## Sursă {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
