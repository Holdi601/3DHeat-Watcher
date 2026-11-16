---
title: "Squad (replay-uri)"
nav_order: 41
lang: "ro"
source: game-squad-demos.md
source_hash: "82c24e6df01c"
nav_exclude: true
search_exclude: true
---
# Squad (replay-uri) {#squad-replays}

După un meci de Squad, watcher-ul transformă replay-ul salvat de joc în fișiere pe care le poți vedea pe o hartă în viewer-ul 3DHeat.

*Detalii tehnice: adaptorul `squad-demos`, tip [`replay`](sources-and-rules.md); rulează permanent (nu așteaptă pornirea unui joc) și caută date noi la fiecare 5 s.*

## Ce se înregistrează {#what-is-recorded}

- poziția, unghiul corpului și viteza fiecărui jucător de fiecare dată când serverul le replică (până la de 8 ori pe secundă), pe jos și în vehiculele terestre
- numele, echipa, fracțiunea și squad-ul fiecărui jucător, urmărind schimbările de echipă
- nu: mișcarea elicopterelor, uciderile și dispozitivele desfășurabile - vezi README-ul cititorului

## De unde vine {#where-it-comes-from}

demo-urile de server pe care Squad le înregistrează cu comanda de admin AdminDemoRec: &lt;server>/SquadGame/Saved/Demos/\*.replay, citite de cititorul extern `heat3d-squad-demo` (exporters/ext/squad-demo)

## Cum îl pornești {#how-to-switch-it-on}

înregistrează pe server: dă adminului permisiunea `demos` în Admins.cfg, apoi AdminDemoRec &lt;name> și AdminDemoStop în consola jocului; copiază demo-ul aici și instalează cititorul: pip install -e &lt;3DHeat>/exporters/ext/squad-demo

Setări din variabile de mediu:

- `HEAT3D_SQUAD_DEMO`: folderul convertorului (un clone sau o arhivă dezarhivată), când nu este instalat sau lângă watcher

## Cum funcționează {#how-it-works}

Replay-uri și demo-uri: ce salvează un joc despre un meci, convertit după ce meciul s-a terminat.

Un replay conține tot ce o interfață live ține ascuns în jocurile multiplayer -
poziția fiecărui jucător, fiecare ucidere acolo unde s-a întâmplat - și este un fișier pe care jocul îl scrie pentru jucătorii săi, deci citirea lui nu atinge nimic din joc. Watcher-ul se uită în folderele în care jocurile le salvează, așteaptă până când un fișier nou nu mai crește (altfel jocul încă îl scrie) și îl convertește într-un fir de execuție separat, astfel că o conversie lungă nu oprește restul watcher-ului.

Prima dată când este văzut un folder, replay-urile deja existente în el sunt doar notate, nu convertite: un jucător cu ani de demo-uri ar găsi altfel watcher-ul ocupat o zi întreagă. `python -m heat3d_watch replays <adapter> [folder]` convertește pe cele existente, la cerere.

#### Squad {#squad}

Serverele dedicate ale Squad înregistrează un demo al unui meci când un admin cu permisiunea `demos` rulează AdminDemoRec &lt;name> (și AdminDemoStop), în `<server>/SquadGame/Saved/Demos/<name>.replay` - un replay de rețea Unreal Engine care conține ce a replicat serverul, inclusiv toată mișcarea jucătorilor. Watcher-ul nu le citește singur: o face un cititor extern (cititorul de demo-uri 3DHeat Squad, `exporters/ext/squad-demo`, comanda `heat3d-squad-demo`), un proiect de sine stătător. Este rulat pe fiecare demo nou din folderele în care scrie un server local sau dintr-un folder adăugat în setări pentru demo-urile copiate de pe un server închiriat, și produce în folderul sesiunii `<map>/<match>.parquet` și `<match>.match.json`. Stratul (layer-ul), harta, numărul de jucători și durata meciului devin statisticile sesiunii.

Același modul servește și: [Counter-Strike 2 (replay-uri)](game-cs2-demos.md), [Dota 2 (replay-uri)](game-dota-replays.md), [osu! (replay-uri)](game-osu-replays.md), [War Thunder (replay-uri)](game-warthunder-replays.md), [World of Tanks (replay-uri)](game-wot-replays.md), [World of Warships (replay-uri)](game-wows-replays.md).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa în sus | `z` |
| Unități | unități Unreal (centimetri) |
| Oglindită pentru viewer | niciuna |
| Scala unității (`scale`: viewer-ul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` (`axes`) al fiecărei sesiuni și, când sesiunea are poziții, în footer-ul `heat.parquet`, ca viewer-ul 3DHeat să rotească și să scaleze rândurile singur - vezi [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` afișează asta ca "allowed (reads only what the game publishes)".
- Tip `replay`: citește doar ce oferă jocul sau platforma (replay-urile și demo-urile pe care jocul le salvează), deci înregistrează și în jocul online, nu doar offline; steagul decide doar dacă memoria poate fi citită vreodată.
- Memorie: **niciodată** citită de acest adaptor. Doar adaptoarele `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online - vezi [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul acestui adaptor le setează după nume (`stats` al fiecărei sesiuni din `meta.json` și tabelul `stats` din `watcher.sqlite`):

`layer`, `map`, `match_seconds`, `players`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel cu câmpurile jocului sau din numele statisticilor jocului nu sunt în această listă; "Ce se înregistrează" de mai sus le numește.

## Completitudine {#completeness}

Convertorul pe care îl rulează acest adaptor respectă [regula de convertor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) a 3DHeat: ce conține replay-ul este citit sau păstrat, niciodată aruncat - citit în tabel și în documentul meciului, tot restul păstrat întreg în fișiere-anexă alături de ele, numărat în `selfCheck.completeness` al documentului meciului. Documentația convertorului spune ce citește, ce păstrează brut și ce nu poate citi.

## Verificat {#verified}

cititorul este verificat pe demo-uri publice de server (mișcarea concordă cu viteza pe care o transportă; echipa fiecărui rând se potrivește cu fracțiunea soldatului său) și prin teste pe demo-uri construite; acest hook, prin teste cu o comandă de înlocuire

## Sursă {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
