---
title: "World of Warships (replay-uri)"
nav_order: 49
lang: "ro"
source: game-wows-replays.md
source_hash: "c822aca3f6fe"
nav_exclude: true
search_exclude: true
---
# World of Warships (replay-uri) {#world-of-warships-replays}

După un meci de World of Warships, watcher-ul transformă replay-ul salvat de joc în fișiere pe care le poți vedea pe o hartă în viewer-ul 3DHeat.

*Detalii tehnice: adaptorul `wows-replays`, tip [`replay`](sources-and-rules.md); rulează permanent (nu așteaptă pornirea unui joc) și caută date noi la fiecare 5 s.*

## Ce se înregistrează {#what-is-recorded}

- poziția și direcția fiecărei nave, cât timp clientul care a înregistrat a văzut-o (de aproximativ 6-7 ori pe secundă când se mișcă), nava jucătorului tot timpul
- aliat sau inamic, și nava (a jucătorului care a înregistrat după nume, celelalte după numărul navei dat de joc); navele scufundate acolo unde s-au scufundat și ucigașii lor acolo unde stăteau
- harta; nava, uciderile și supraviețuirea jucătorului care a înregistrat, ca statistici

## De unde vine {#where-it-comes-from}

replay-urile salvate de World of Warships: `<World of Warships>/replays/*.wowsreplay` (cu replay-urile pornite), convertite de convertorul extern `heat3d-wows-replay` (exporters/ext/wows-replay)

## Cum îl pornești {#how-to-switch-it-on}

pornește înregistrarea replay-urilor în World of Warships (`isReplayEnabled` în preferences.xml, sau setarea jocului acolo unde există) și instalează convertorul: pip install -e &lt;3DHeat>/exporters/ext/wows-replay

Setări din variabile de mediu:

- `HEAT3D_WOWS_REPLAY`: folderul convertorului (un clone sau o arhivă dezarhivată), când nu este instalat sau lângă watcher

## Cum funcționează {#how-it-works}

Replay-uri și demo-uri: ce salvează un joc despre un meci, convertit după ce meciul s-a terminat.

Un replay conține tot ce o interfață live ține ascuns în jocurile multiplayer -
poziția fiecărui jucător, fiecare ucidere acolo unde s-a întâmplat - și este un fișier pe care jocul îl scrie pentru jucătorii săi, deci citirea lui nu atinge nimic din joc. Watcher-ul se uită în folderele în care jocurile le salvează, așteaptă până când un fișier nou nu mai crește (altfel jocul încă îl scrie) și îl convertește într-un fir de execuție separat, astfel că o conversie lungă nu oprește restul watcher-ului.

Prima dată când este văzut un folder, replay-urile deja existente în el sunt doar notate, nu convertite: un jucător cu ani de demo-uri ar găsi altfel watcher-ul ocupat o zi întreagă. `python -m heat3d_watch replays <adapter> [folder]` convertește pe cele existente, la cerere.

#### World of Tanks și World of Warships {#world-of-tanks-and-world-of-warships}

Ambele salvează un replay al fiecărei bătălii în `<joc>/replays/` când înregistrarea este pornită (`*.wotreplay`, `*.wowsreplay`); instalările sunt găsite prin lista Wargaming Game Center, `C:/Games/World_of_Tanks*` / `World_of_Warships*`, și prin Steam. Ca la War Thunder, watcher-ul nu citește fișierele singur: un convertor extern al fiecăruia o face (`exporters/ext/wot-replay`, comanda `heat3d-wot-replay`; `exporters/ext/wows-replay`, comanda `heat3d-wows-replay`), fiecare un proiect de sine stătător. Găsit în PATH, instalat sau lângă watcher, transformă fiecare replay nou în `<map>/<match>.parquet` și `<match>.match.json` în folderul sesiunii; lipsind, watcher-ul spune o singură dată cum se instalează. Rândul jucătorului care a înregistrat - vehiculul sau nava, uciderile, daunele (World of Tanks), dacă a supraviețuit și rezultatul (World of Tanks) - devine statisticile sesiunii. Ce citește fiecare convertor și ce nu, este scris în README-ul lui.

Același modul servește și: [Counter-Strike 2 (replay-uri)](game-cs2-demos.md), [Dota 2 (replay-uri)](game-dota-replays.md), [osu! (replay-uri)](game-osu-replays.md), [Squad (replay-uri)](game-squad-demos.md), [War Thunder (replay-uri)](game-warthunder-replays.md), [World of Tanks (replay-uri)](game-wot-replays.md).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa în sus | `y` |
| Unități | unități ale lumii World of Warships (x est, y sus, z nord; una este 15 m după geometria corpului, 30 m după distanțele jocului) |
| Oglindită pentru viewer | `z` |
| Scala unității (`scale`: viewer-ul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` (`axes`) al fiecărei sesiuni și, când sesiunea are poziții, în footer-ul `heat.parquet`, ca viewer-ul 3DHeat să rotească și să scaleze rândurile singur - vezi [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` afișează asta ca "allowed (reads only what the game publishes)".
- Tip `replay`: citește doar ce oferă jocul sau platforma (replay-urile și demo-urile pe care jocul le salvează), deci înregistrează și în jocul online, nu doar offline; steagul decide doar dacă memoria poate fi citită vreodată.
- Memorie: **niciodată** citită de acest adaptor. Doar adaptoarele `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online - vezi [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul acestui adaptor le setează după nume (`stats` al fiecărei sesiuni din `meta.json` și tabelul `stats` din `watcher.sqlite`):

`map`, `survived`, `vehicle`, `won`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel cu câmpurile jocului sau din numele statisticilor jocului nu sunt în această listă; "Ce se înregistrează" de mai sus le numește.

## Completitudine {#completeness}

Convertorul pe care îl rulează acest adaptor respectă [regula de convertor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) a 3DHeat: ce conține replay-ul este citit sau păstrat, niciodată aruncat - citit în tabel și în documentul meciului, tot restul păstrat întreg în fișiere-anexă alături de ele, numărat în `selfCheck.completeness` al documentului meciului. Documentația convertorului spune ce citește, ce păstrează brut și ce nu poate citi.

## Verificat {#verified}

convertorul este verificat pe replay-uri publice din mai multe versiuni ale jocului și prin teste pe replay-uri construite; acest hook, prin teste cu o comandă de înlocuire

## Sursă {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
