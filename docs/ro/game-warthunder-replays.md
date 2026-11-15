---
title: "War Thunder (replay-uri)"
nav_order: 46
lang: "ro"
source: game-warthunder-replays.md
source_hash: "81f03926431d"
nav_exclude: true
search_exclude: true
---
# War Thunder (replay-uri) {#war-thunder-replays}

După un meci de War Thunder, watcher-ul transformă replay-ul salvat de joc în fișiere pe care le poți vedea pe o hartă în viewer-ul 3DHeat.

*Detalii tehnice: adaptorul `warthunder-replays`, tip [`replay`](sources-and-rules.md); rulează permanent (nu așteaptă pornirea unui joc) și caută date noi la fiecare 5 s.*

## Ce se înregistrează {#what-is-recorded}

- poziția și atitudinea fiecărui avion, de aproximativ 4 ori pe secundă (câte conține replay-ul)
- pozițiile unităților terestre din sincronizarea terestră a replay-ului (în replay-urile din 2026; nu în cele din 2025)
- cine era fiecare unitate (jucător, id-ul vehiculului, echipa), acolo unde o ucidere sau o lovitură o numește; uciderile, morțile și loviturile acolo unde s-au întâmplat; chatul; harta
- uciderile, morțile, scorul și capturile autorului replay-ului, ca statistici

## De unde vine {#where-it-comes-from}

replay-urile salvate de War Thunder: `<War Thunder>/Replays/*.wrpl` (cu salvarea replay-urilor pornită), convertite de convertorul extern `heat3d-wt-replay` (exporters/ext/warthunder-replay)

## Cum îl pornești {#how-to-switch-it-on}

pornește salvarea replay-urilor în opțiunile War Thunder și instalează convertorul: pip install -e &lt;3DHeat>/exporters/ext/warthunder-replay

Setări din variabile de mediu:

- `HEAT3D_WT_REPLAY`: folderul convertorului (un clone sau o arhivă dezarhivată), când nu este instalat sau lângă watcher

## Cum funcționează {#how-it-works}

Replay-uri și demo-uri: ce salvează un joc despre un meci, convertit după ce meciul s-a terminat.

Un replay conține tot ce o interfață live ține ascuns în jocurile multiplayer -
poziția fiecărui jucător, fiecare ucidere acolo unde s-a întâmplat - și este un fișier pe care jocul îl scrie pentru jucătorii săi, deci citirea lui nu atinge nimic din joc. Watcher-ul se uită în folderele în care jocurile le salvează, așteaptă până când un fișier nou nu mai crește (altfel jocul încă îl scrie) și îl convertește într-un fir de execuție separat, astfel că o conversie lungă nu oprește restul watcher-ului.

Prima dată când este văzut un folder, replay-urile deja existente în el sunt doar notate, nu convertite: un jucător cu ani de demo-uri ar găsi altfel watcher-ul ocupat o zi întreagă. `python -m heat3d_watch replays <adapter> [folder]` convertește pe cele existente, la cerere.

#### War Thunder {#war-thunder}

War Thunder salvează un replay al fiecărei bătălii în `<War Thunder>/Replays/*.wrpl` când salvarea replay-urilor este pornită în opțiunile lui. Watcher-ul nu le citește singur: o face un convertor extern (convertorul de replay-uri 3DHeat War Thunder, `exporters/ext/warthunder-replay`, comanda `heat3d-wt-replay`), ținut separat, ca o problemă de la el să nu atingă nimic altceva. Când comanda este în PATH, sau pachetul este instalat ori lângă watcher, fiecare replay nou trece prin el și ajunge în folderul sesiunii ca `<map>/<match>.parquet` și `<match>.match.json`; când nu este, watcher-ul spune o singură dată cum se instalează și lasă folderul în pace. Ce citește convertorul și ce nu, este scris în README-ul lui. Rândul autorului replay-ului din rezultate - uciderile, uciderile de la sol, morțile, asistențele, scorul, capturile - devine statisticile sesiunii.

Același modul servește și: [Counter-Strike 2 (replay-uri)](game-cs2-demos.md), [Dota 2 (replay-uri)](game-dota-replays.md), [osu! (replay-uri)](game-osu-replays.md), [Squad (replay-uri)](game-squad-demos.md), [World of Tanks (replay-uri)](game-wot-replays.md), [World of Warships (replay-uri)](game-wows-replays.md).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa în sus | `y` |
| Unități | metri (x est, y sus, z nord) |
| Oglindită pentru viewer | `z` |
| Scala unității (`scale`: viewer-ul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` (`axes`) al fiecărei sesiuni și, când sesiunea are poziții, în footer-ul `heat.parquet`, ca viewer-ul 3DHeat să rotească și să scaleze rândurile singur - vezi [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` afișează asta ca "allowed (reads only what the game publishes)".
- Tip `replay`: citește doar ce oferă jocul sau platforma (replay-urile și demo-urile pe care jocul le salvează), deci înregistrează și în jocul online, nu doar offline; steagul decide doar dacă memoria poate fi citită vreodată.
- Memorie: **niciodată** citită de acest adaptor. Doar adaptoarele `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online - vezi [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul acestui adaptor le setează după nume (`stats` al fiecărei sesiuni din `meta.json` și tabelul `stats` din `watcher.sqlite`):

`map`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel cu câmpurile jocului sau din numele statisticilor jocului nu sunt în această listă; "Ce se înregistrează" de mai sus le numește.

## Completitudine {#completeness}

Convertorul pe care îl rulează acest adaptor respectă [regula de convertor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) a 3DHeat: ce conține replay-ul este citit sau păstrat, niciodată aruncat - citit în tabel și în documentul meciului, tot restul păstrat întreg în fișiere-anexă alături de ele, numărat în `selfCheck.completeness` al documentului meciului. Documentația convertorului spune ce citește, ce păstrează brut și ce nu poate citi.

## Verificat {#verified}

convertorul este verificat pe replay-uri publice din mai multe versiuni ale jocului (uciderile și numele concordă cu rezultatele) și prin teste pe replay-uri construite; acest hook, prin teste cu o comandă de înlocuire

## Sursă {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
