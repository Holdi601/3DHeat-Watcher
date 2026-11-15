---
title: "Counter-Strike 2 (replay-uri)"
nav_order: 8
lang: "ro"
source: game-cs2-demos.md
source_hash: "d115f9085302"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (replay-uri) {#counter-strike-2-replays}

După un meci de Counter-Strike 2, watcher-ul transformă replay-ul salvat de joc în fișiere pe care le poți vedea pe o hartă în viewer-ul 3DHeat.

*Detalii tehnice: adaptorul `cs2-demos`, tip [`replay`](sources-and-rules.md); rulează permanent (nu așteaptă pornirea unui joc) și caută date noi la fiecare 5 s.*

## Ce se înregistrează {#what-is-recorded}

- poziția fiecărui jucător, direcția privirii, viața și banii (la fiecare al 8-lea tick)
- uciderile, morțile, daunele, grenadele, plasările și dezamorsările de bombă, acolo unde s-au întâmplat
- runde, scor, economie; rândul de scor al jucătorului conectat, ca statistici

## De unde vine {#where-it-comes-from}

demo-urile salvate de CS2: &lt;CS2>/game/csgo/replays/\*.dem (descărcate din istoricul meciurilor) și &lt;CS2>/game/csgo/\*.dem (înregistrate)

## Cum îl pornești {#how-to-switch-it-on}

descarcă demo-ul unui meci în CS2 (Watch > Your Matches) sau înregistrează unul cu comanda din consolă `record`

Setări din variabile de mediu:

- `HEAT3D_CS2`: folderul 3DHeat CS2, când nu este lângă watcher sau instalat

## Cum funcționează {#how-it-works}

Replay-uri și demo-uri: ce salvează un joc despre un meci, convertit după ce meciul s-a terminat.

Un replay conține tot ce o interfață live ține ascuns în jocurile multiplayer -
poziția fiecărui jucător, fiecare ucidere acolo unde s-a întâmplat - și este un fișier pe care jocul îl scrie pentru jucătorii săi, deci citirea lui nu atinge nimic din joc. Watcher-ul se uită în folderele în care jocurile le salvează, așteaptă până când un fișier nou nu mai crește (altfel jocul încă îl scrie) și îl convertește într-un fir de execuție separat, astfel că o conversie lungă nu oprește restul watcher-ului.

Prima dată când este văzut un folder, replay-urile deja existente în el sunt doar notate, nu convertite: un jucător cu ani de demo-uri ar găsi altfel watcher-ul ocupat o zi întreagă. `python -m heat3d_watch replays <adapter> [folder]` convertește pe cele existente, la cerere.

#### Counter-Strike 2 {#counter-strike-2}

CS2 salvează demo-urile pe care le descarcă jucătorul din istoricul meciurilor (tab-ul Watch) în `<CS2>/game/csgo/replays/`, iar pe cele înregistrate cu comanda din consolă `record` le salvează în `<CS2>/game/csgo/`. Fiecare este convertit cu convertorul propriu al acestui depozit pentru CS2 (3DHeat CS2, github.com/Holdi601/3DHeat-CS2: poziția, direcția privirii, viața și banii fiecărui jucător la al 8-lea tick; uciderile, morțile, daunele, grenadele, plasările și dezamorsările acolo unde s-au întâmplat; runde, scor, economie) în folderul sesiunii, ca tabelul `<map>/<match>.parquet` și rezumatul `<match>.match.json` pe care le citesc tab-urile Hartă termică și Meci ale viewer-ului. Tabelul de scor al meciului devine statisticile sesiunii: pentru jucătorul al cărui cont Steam este conectat pe acest calculator (din `loginusers.vdf` al Steam) sub numele simple - uciderile, morțile, asistențele, ADR, KAST, procentul de headshot-uri, primele ucideri, clutch-urile - plus scorul și rundele.

Același modul servește și: [Dota 2 (replay-uri)](game-dota-replays.md), [osu! (replay-uri)](game-osu-replays.md), [Squad (replay-uri)](game-squad-demos.md), [War Thunder (replay-uri)](game-warthunder-replays.md), [World of Tanks (replay-uri)](game-wot-replays.md), [World of Warships (replay-uri)](game-wows-replays.md).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa în sus | `z` |
| Unități | inci (unități Source) |
| Oglindită pentru viewer | `y` |
| Scala unității (`scale`: viewer-ul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` (`axes`) al fiecărei sesiuni și, când sesiunea are poziții, în footer-ul `heat.parquet`, ca viewer-ul 3DHeat să rotească și să scaleze rândurile singur - vezi [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` afișează asta ca "allowed (reads only what the game publishes)".
- Tip `replay`: citește doar ce oferă jocul sau platforma (replay-urile și demo-urile pe care jocul le salvează), deci înregistrează și în jocul online, nu doar offline; steagul decide doar dacă memoria poate fi citită vreodată.
- Memorie: **niciodată** citită de acest adaptor. Doar adaptoarele `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online - vezi [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul acestui adaptor le setează după nume (`stats` al fiecărei sesiuni din `meta.json` și tabelul `stats` din `watcher.sqlite`):

`map`, `rounds`, `score.{team}`, `won`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel cu câmpurile jocului sau din numele statisticilor jocului nu sunt în această listă; "Ce se înregistrează" de mai sus le numește.

## Completitudine {#completeness}

Convertorul pe care îl rulează acest adaptor respectă [regula de convertor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) a 3DHeat: ce conține replay-ul este citit sau păstrat, niciodată aruncat - citit în tabel și în documentul meciului, tot restul păstrat întreg în fișiere-anexă alături de ele, numărat în `selfCheck.completeness` al documentului meciului. Documentația convertorului spune ce citește, ce păstrează brut și ce nu poate citi.

## Verificat {#verified}

convertorul este testat pe demo-uri reale de turnee; urmărirea folderului și statisticile, prin teste

## Sursă {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
