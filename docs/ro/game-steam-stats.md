---
title: "Statistici Steam (platformă)"
nav_order: 43
lang: "ro"
source: game-steam-stats.md
source_hash: "24fa6512bd6d"
nav_exclude: true
search_exclude: true
---
# Statistici Steam (platformă) {#steam-statistics-platform}

Watcher-ul salvează ce păstrează statisticile Steam despre jocurile tale, ca să îți poți vedea istoricul mai târziu, ca statistici și ca cronologie.

*Detalii tehnice: adaptorul `steam-stats`, tip [`platform`](sources-and-rules.md); rulează permanent (nu așteaptă pornirea unui joc) și caută date noi la fiecare 30 s.*

## Ce se înregistrează {#what-is-recorded}

- fiecare statistică pe care un joc o păstrează în Steam (numele și valorile lui), pe joc, de fiecare dată când se schimbă
- deblocările de realizări, cu numele afișat, descrierea și momentul deblocării
- schimbările de statistici, cu valoarea veche, valoarea nouă și diferența
- timpul de joc (minute, ultimele două săptămâni) și ultima dată când ai jucat

## De unde vine {#where-it-comes-from}

Cache-ul local de statistici Steam %STEAM%\appcache\stats\UserGameStats_&lt;account>_&lt;appid>.bin, cu UserGameStatsSchema_&lt;appid>.bin; timpul de joc din %STEAM%\userdata\\&lt;account>\config\localconfig.vdf (%STEAM% din HKCU\Software\Valve\Steam SteamPath)

## Cum îl pornești {#how-to-switch-it-on}

Nu trebuie pornit nimic: watcher-ul citește sursa așa cum o oferă jocul sau platforma.

## Cum funcționează {#how-it-works}

Ce păstrează lansatorul și driver-ul grafic despre joc: statisticile, realizările, timpul de joc și cronologiile Steam, precum și highlight-urile și clipurile NVIDIA.

Niciuna dintre aceste surse nu are nevoie ca un joc să colaboreze sau să ruleze, așa că cele trei adaptoare de aici sunt mereu pornite și citesc câteva fișiere la fiecare câteva secunde.

#### Statistici Steam (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<account>_<appid>.bin`, rescris de clientul Steam ori de câte ori un joc își salvează statisticile, decodat cu schema `UserGameStatsSchema_<appid>.bin` de lângă el (KeyValues binar, vezi `_steam.py`). Statisticile sunt numere întregi sau reale, așa cum le definește jocul; realizările sunt biți, cu momentul deblocării în secunde Unix. Timpul de joc este în `<Steam>\userdata\<account>\config\localconfig.vdf`, sub apps/&lt;appid>: Playtime și Playtime2wks în minute, LastPlayed în secunde Unix. Steam este găsit prin HKCU\Software\Valve\Steam SteamPath.
API-ul de statistici: <https://partner.steamgames.com/doc/features/achievements>

Același modul servește și: [Highlight-uri NVIDIA (platformă)](game-nvidia-highlights.md), [Cronologia Steam (platformă)](game-steam-timeline.md).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | nu |
| Axa în sus | `y` |
| Unități | metri |
| Oglindită pentru viewer | niciuna |
| Scala unității (`scale`: viewer-ul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` (`axes`) al fiecărei sesiuni și, când sesiunea are poziții, în footer-ul `heat.parquet`, ca viewer-ul 3DHeat să rotească și să scaleze rândurile singur - vezi [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **nu**. `games --markdown` afișează asta ca "single-player".
- Tip `platform`: citește doar ce oferă jocul sau platforma (ce păstrează Steam sau driver-ul grafic), deci înregistrează și în jocul online, nu doar offline; steagul decide doar dacă memoria poate fi citită vreodată.
- Memorie: **niciodată** citită de acest adaptor. Doar adaptoarele `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online - vezi [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul acestui adaptor le setează după nume (`stats` al fiecărei sesiuni din `meta.json` și tabelul `stats` din `watcher.sqlite`):

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel cu câmpurile jocului sau din numele statisticilor jocului nu sunt în această listă; "Ce se înregistrează" de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează [regula de convertor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) a 3DHeat: ce conține sursa este citit sau păstrat, niciodată aruncat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat după nume; `used` marchează ce a devenit și rânduri), iar `selfCheck.completeness` din `meta.json` numără fiecare `type` - `lost` este 0.

**Citit**

- fiecare statistică din fișierul de statistici, după numele ei din API (int, float, avgrate), fiecare bit de realizare cu momentul deblocării, numit și descris după schemă
- schimbările față de ultima citire (veche, nouă, diferență), deblocările noi; timpul de joc, timpul din ultimele două săptămâni și ultima dată jucată din localconfig.vdf

**Păstrat brut**

- `UserGameStats`: octeții fișierului de statistici, întregi, de fiecare dată când sunt înregistrați (`crc`, `PendingChanges`, biții de realizare pe care schema nu îi mai definește și orice cheie pe care decodorul o sare se află în el)
- `UserGameStatsSchema`: octeții fișierului de schemă, alături, ca statisticile să poată fi decodate doar din sesiune (numele fiecărei statistici și realizări în toate limbile, iconițe, steaguri)
- `localconfig_app`: blocul întreg al jocului din localconfig.vdf, ca JSON (starea sincronizării în cloud, opțiunile de lansare, insignele și orice altă cheie pe care Steam o ține pentru joc), când îi este înregistrat timpul de joc
- un fișier de statistici pe care decodorul nu îl poate citi (tăiat în timpul scrierii sau cu un layout nou): octeții lui și schema, într-o sesiune fără rânduri (`used` fals; `unreadable` în meta.json)

**Nu este disponibil**

- restul localconfig.vdf (prieteni, chat, setările Steam): nu ține de joc și este privat
- valorile statisticilor între două scrieri: Steam rescrie fișierul când jocul își salvează statisticile, de obicei când se închide
- procentele globale ale realizărilor și statisticile altor jucători: sunt pe serverele Steam, nu aici

**Dimensiune**: câțiva KB pe fiecare sesiune înregistrată, plus schema (până la câteva sute de KB pentru un joc cu multe realizări) - mult sub 1 MB pe oră de joc; zstd micșorează textul schemei cu jumătate sau mai mult

## Verificat {#verified}

testat pe fișiere reale de statistici și scheme dintr-o instalare locală; detectarea schimbărilor testată pe fișiere construite în formatul binar KeyValues

## Sursă {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
