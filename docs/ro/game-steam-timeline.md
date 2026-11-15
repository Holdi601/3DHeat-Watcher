---
title: "Cronologia Steam (platformă)"
nav_order: 44
lang: "ro"
source: game-steam-timeline.md
source_hash: "3878efe0d7f1"
nav_exclude: true
search_exclude: true
---
# Cronologia Steam (platformă) {#steam-timeline-platform}

Watcher-ul salvează ce păstrează Steam Timeline despre jocurile tale, ca să îți poți vedea istoricul mai târziu, ca statistici și ca cronologie.

*Detalii tehnice: adaptorul `steam-timeline`, tip [`platform`](sources-and-rules.md); rulează permanent (nu așteaptă pornirea unui joc) și caută date noi la fiecare 10 s.*

## Ce se înregistrează {#what-is-recorded}

- o sesiune pentru fiecare fișier de cronologie: începutul și sfârșitul ei (session_start, session_end)
- realizările deblocate în timpul jocului, cu momentul lor
- schimbările de mod de joc (joc, pregătire, meniuri, ecran de încărcare)
- evenimentele adăugate de jocuri prin ISteamTimeline, cu titlu și descriere, sub numele iconiței lor
- fazele jocului (un meci, o misiune) cu etichetele lor; evenimentele dintr-o fază poartă id-ul ei ca session
- descrierile de stare pe care jocul le arată pe cronologie ("Runda 3")
- erorile de înregistrare ale Steam însuși

## De unde vine {#where-it-comes-from}

%STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json

## Cum îl pornești {#how-to-switch-it-on}

Steam > Settings > Game Recording: înregistrează în fundal sau la cerere (atunci Steam scrie cronologiile)

## Cum funcționează {#how-it-works}

Ce păstrează lansatorul și driver-ul grafic despre joc: statisticile, realizările, timpul de joc și cronologiile Steam, precum și highlight-urile și clipurile NVIDIA.

Niciuna dintre aceste surse nu are nevoie ca un joc să colaboreze sau să ruleze, așa că cele trei adaptoare de aici sunt mereu pornite și citesc câteva fișiere la fiecare câteva secunde.

#### Cronologia Steam (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`, scris cât timp Steam Game Recording este pornit. Fișierul este JSON cu numere scrise ca șiruri: "daterecorded" (secunde Unix), "starttime"/"endtime" (ms) și "entries", fiecare {"id", "time" (ms de la daterecorded), "type", ...}. Tipuri văzute în fișiere reale:
```text
achievement        achievement_name - Steam adds these for every game
gamemode           mode, an ETimelineGameMode: 1 playing, 2 staging, 3 menus,
                   4 loading screen
error              description - Steam's own ("#GameRecording_RecordingFailed")
event              a game's AddInstantaneousTimelineEvent/AddRangeTimelineEvent:
                   title, description, icon, priority, duration (ms),
                   possible_clip - "You killed <name>" / "with the <weapon>"
state_description  title - SetTimelineTooltip ("Round 3")
phase              a StartGamePhase..EndGamePhase span: duration (ms), tags
                   [{name, icon, group, priority}] (mode, map ...)
```
Structura fișierului este a Steam și nedocumentată; câmpurile sunt parametrii API-ului. Orice alt tip este înregistrat sub numele lui, cu câmpurile lui.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Același modul servește și: [Highlight-uri NVIDIA (platformă)](game-nvidia-highlights.md), [Statistici Steam (platformă)](game-steam-stats.md).

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

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel cu câmpurile jocului sau din numele statisticilor jocului nu sunt în această listă; "Ce se înregistrează" de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează [regula de convertor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) a 3DHeat: ce conține sursa este citit sau păstrat, niciodată aruncat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat după nume; `used` marchează ce a devenit și rânduri), iar `selfCheck.completeness` din `meta.json` numără fiecare `type` - `lost` este 0.

**Citit**

- fiecare intrare, o dată, ca rând la momentul ei: tipul ei, fiecare câmp simplu (titlu, descriere, iconiță, prioritate, durată, possible_clip, numele realizării, mod, ...), etichetele unei faze pe grupe, numele afișat al realizării din schema statisticilor; începutul și sfârșitul fișierului

**Păstrat brut**

- fiecare intrare întreagă, ca JSON, sub `type`-ul Steam (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, orice alt tip): câmpurile imbricate - iconița și prioritatea unei etichete, orice adaugă un Steam mai nou - sunt doar aici
- `timeline`: câmpurile fișierului (daterecorded, starttime, endtime, orice altele), când sesiunea se deschide și din nou când se schimbă

**Nu este disponibil**

- înregistrarea în sine (video): Steam o ține în folderele lui; sesiunea se referă la fișierul de cronologie după nume
- o citire a unui fișier pe care Steam îl scrie și care nu poate fi analizat nici după ce i s-a închis finalul: numărată (`bad` în starea adaptorului) și citită din nou la următoarea schimbare, când intrările lui sunt preluate

**Dimensiune**: câteva sute de intrări de 100-300 de octeți pe oră de joc: mult sub 1 MB pe oră

## Verificat {#verified}

testat pe fișiere reale de cronologie dintr-o instalare locală: intrări achievement, gamemode, error, și intrările event, state_description și phase ale jocurilor; formatul fișierului în sine este nedocumentat

## Sursă {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
