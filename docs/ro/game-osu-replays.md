---
title: "osu! (reluări)"
nav_order: 35
lang: "ro"
source: game-osu-replays.md
source_hash: "9a1c74c4d5e0"
nav_exclude: true
search_exclude: true
---
# osu! (reluări) {#osu-replays}

După un meci de osu!, watcher-ul transformă reluarea salvată de joc în fișiere pe care le puteți vedea pe o hartă în vizualizatorul 3DHeat.

*Detalii tehnice: adaptorul `osu-replays`, tipul [`replay`](sources-and-rules.md); rulează tot timpul (nu așteaptă ca un joc să pornească) și caută date noi la fiecare 5 s.*

## Ce se înregistrează {#what-is-recorded}

- traseul cursorului peste zona de joc (x 0..512, y 0..384) și tastele apăsate, la fiecare cadru
- scorul, combo-ul, 300-urile/100-urile/50-urile/gekis/katus/ratările, precizia, mod-urile, full combo
- bara de viață pe parcursul jocului, hash-urile hărții și ale reluării, sămânța aleatorie, id-ul scorului online

## De unde vine {#where-it-comes-from}

reluările salvate de osu! (stable): %LOCALAPPDATA%/osu!/Data/r/\*.osr (fiecare joc) și osu!/Replays/\*.osr (exportate)

## Cum se activează {#how-to-switch-it-on}

Nu trebuie activat nimic: watcher-ul citește sursa așa cum o oferă jocul sau platforma.

## Cum funcționează {#how-it-works}

Reluări și demo-uri: ce salvează un joc despre un meci, convertit odată ce meciul s-a încheiat.

O reluare conține tot ce o interfață live păstrează în jocurile multiplayer - poziția fiecărui jucător, fiecare eliminare acolo unde s-a produs - și este un fișier pe care jocul îl scrie pentru jucătorii săi, deci citirea lui nu atinge nimic din joc. Watcher-ul urmărește folderele în care jocurile le salvează, așteaptă până când un fișier nou nu mai crește (altfel jocul încă îl scrie) și îl convertește într-un fir de execuție separat, ca o conversie lungă să nu rețină restul watcher-ului.

Prima dată când este văzut un folder, reluările deja din el sunt doar notate, nu convertite; un jucător cu ani de demo-uri ar găsi altfel watcher-ul ocupat o zi întreagă. `python -m heat3d_watch replays <adapter> [folder]` convertește cele existente la cerere.

#### osu! {#osu}

osu! (stable) salvează fiecare joc în `osu!/Data/r/*.osr`, iar cele exportate în `osu!/Replays/`. Watcher-ul le citește singur, după formatul publicat de wiki-ul osu!: traseul cursorului și tastele la fiecare cadru, linia scorului, bara de viață, sămânța și id-ul scorului; fișierul este păstrat întreg alături, pe bucăți, în `heat.raw.parquet` al sesiunii.

Același modul servește și: [Counter-Strike 2 (reluări)](game-cs2-demos.md), [Dota 2 (reluări)](game-dota-replays.md), [Squad (reluări)](game-squad-demos.md), [War Thunder (reluări)](game-warthunder-replays.md), [World of Tanks (reluări)](game-wot-replays.md), [World of Warships (reluări)](game-wows-replays.md).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa verticală | `y` |
| Unități | pixeli osu! (zona de joc 512 x 384) |
| Oglindit pentru vizualizator | `z` |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, ca vizualizatorul 3DHeat să rotească și să scaleze rândurile singur; vedeți [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)”.
- Tipul `replay`: citește doar ce oferă jocul sau platforma (reluările și demo-urile pe care le salvează jocul), deci înregistrează și în jocul online, nu doar offline; marcajul decide doar dacă memoria poate fi citită vreodată.
- Memoria: **niciodată** citită de acest adaptor. Doar adaptoarele de tip `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online; vedeți [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul adaptorului le setează pe nume (fiecare `stats` din sesiune, în `meta.json`, și tabelul `stats` din `watcher.sqlite`):

`accuracy`, `full_combo`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează” de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- fiecare cadru: un rând la momentul lui (milisecundele adunate), x și y pe zona de joc, `keys` biții tastelor (mouse 1 și 2, taste 1 și 2, smoke); în mania, x ține tastele apăsate în loc de un loc
- antetul, fiecare câmp: modul, versiunea, MD5-ul hărții (fișierul numește harta doar prin el), jucătorul, MD5-ul reluării, 300, 100, 50, gekis, katus, ratări, scorul, combo-ul maxim, full combo, mod-urile (după nume în meta.json `osu.modNames`), ora jocului - ca statistici și în meta.json `osu`
- graficul barei de viață: un rând `life` pentru fiecare punct (ora, viața 0..1)
- cadrul `-12345`: sămânța aleatorie (`osu.seed`); id-ul scorului online (`osu.scoreId`); cu Target Practice, precizia lui (`osu.targetPracticeAccuracy`)

**Păstrat brut**

- fișierul întreg, pe bucăți, în heat.raw.parquet (`offset` unde începe fiecare, deci bucățile sunt fișierul): `header`, `replay_data` (cadrele comprimate LZMA, așa cum sunt stocate), `score_id`, `mod_info` și `trailing` pentru ce urmează după bucățile descrise de format (exporturile osu!lazer adaugă date acolo) - păstrat, nu citit

**Nu este disponibil**

- harta în sine (obiectele de lovit, sincronizarea): nu este într-o reluare; este numită doar prin MD5-ul ei
- reluările osu!lazer: păstrate în baza lor de date, nu ca fișiere

**Dimensiune**: sidecar-ul brut are aproximativ dimensiunea reluării (zeci până la sute de kilobytes)

## Verificat {#verified}

testat pe reluări construite după formatul .osr publicat; osu!lazer își ține reluările într-un depozit propriu și nu este citit

## Sursă {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
