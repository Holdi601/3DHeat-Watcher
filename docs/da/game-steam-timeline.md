---
title: "Steam Timeline (platform)"
nav_order: 43
lang: "da"
source: game-steam-timeline.md
source_hash: "3a502e4ad09e"
nav_exclude: true
search_exclude: true
---
# Steam Timeline (platform) {#steam-timeline-platform}

Watcheren gemmer det, Steam Timeline holder om dine spil, så du senere kan se din historik som statistik og en tidslinje.

*Teknisk info: adapter `steam-timeline`, type [`platform`](sources-and-rules.md); den kører hele tiden (den venter ikke på, at et spil starter) og kigger efter nye data hvert 10. sekund.*

## Hvad der optages {#what-is-recorded}

- én session pr. tidslinjefil: dens start og slut (session_start, session_end)
- achievements låst op under spil, med tidspunkt
- skift af spiltilstand (spiller, forbereder, menuer, indlæsningsskærm)
- begivenheder, spil tilføjer via ISteamTimeline, med titel og beskrivelse, under deres ikons navn
- spilfaser (en kamp, en mission) med deres tags; begivenheder inde i en fase bærer dens id som session
- tilstandsbeskrivelser, spillet viser på tidslinjen ("Round 3")
- Steams egne optagelsesfejl

## Hvor det kommer fra {#where-it-comes-from}

%STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json

## Sådan slår du det til {#how-to-switch-it-on}

Steam > Settings > Game Recording: optag i baggrunden eller efter behov (Steam skriver tidslinjer da)

## Sådan virker det {#how-it-works}

Det, launcheren og grafikdriveren gemmer om spil: Steams statistik, achievements, spilletid og tidslinjer, og NVIDIAs highlights og klip.

Ingen af disse kilder kræver, at et spil samarbejder eller kører, så de tre adaptere her er altid slået til og kigger på nogle få filer hvert par sekund.

#### Steam Timeline (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`, skrevet, mens Steam Game Recording er slået til. Filen er JSON med tekstlige tal: "daterecorded" (Unix-sekunder), "starttime"/"endtime" (ms) og "entries", hver {"id", "time" (ms siden daterecorded), "type", ...}. Typer set i rigtige filer:
```text
achievement        achievement_name - Steam tilføjer disse for alle spil
gamemode           mode, en ETimelineGameMode: 1 playing, 2 staging, 3 menus,
                   4 loading screen
error              description - Steams egen ("#GameRecording_RecordingFailed")
event              et spils AddInstantaneousTimelineEvent/AddRangeTimelineEvent:
                   title, description, icon, priority, duration (ms),
                   possible_clip - "You killed <name>" / "with the <weapon>"
state_description  title - SetTimelineTooltip ("Round 3")
phase              et StartGamePhase..EndGamePhase-spænd: duration (ms), tags
                   [{name, icon, group, priority}] (mode, map ...)
```
Filens opbygning er Steams og udokumenteret; felterne er API'ens parametre. Enhver anden type gemmes under sit eget navn med sine felter.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Det samme modul betjener også: [NVIDIA highlights (platform)](game-nvidia-highlights.md), [Steam-statistik (platform)](game-steam-stats.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner optaget | nej |
| Op-akse | `y` |
| Enheder | meter |
| Spejlet for vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse gemmes i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Multiplayer {#multiplayer}

- Markeret som spillet online (`multiplayer`): **nej**. `games --markdown` viser dette som "enkeltspiller".
- Type `platform`: den læser kun det, spillet eller platformen udleverer (det Steam eller grafikdriveren gemmer), så den optager i online-spil lige så vel som offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der optages {#statistics-recorded}

Statistiknøgler, denne adapters kode sætter ved navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

En nøgle i klammer udfyldes under kørsel (`score.{team}` er én nøgle pr. hold). Nøgler, koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne, står ikke på listen; "Hvad der optages" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeat's [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det, kilden indeholder, bliver læst eller gemt, aldrig smidt væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, helt i sessionens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text`, samt alle felter gemt ved navn; `used` markerer det, der også blev til rækker), og `meta.json`s `selfCheck.completeness` tæller hver `type` - `lost` er 0.

**Læst**

- hver post én gang, som en række på sit tidspunkt: dens type, hvert almindeligt felt (title, description, icon, priority, duration, possible_clip, achievementets navn, mode ...), en fases tags pr. gruppe, achievementets visningsnavn fra stats-skemaet; filens start og slut

**Gemt rå**

- hver post hel som JSON under Steams egen `type` (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, enhver anden): indlejrede felter - et tags ikon og prioritet, og alt, en senere Steam tilføjer - findes kun her
- `timeline`: filens egne felter (daterecorded, starttime, endtime, andre), når sessionen åbnes, og igen når de ændres

**Ikke tilgængeligt**

- selve optagelsen (video): Steam gemmer den i sine egne mapper; sessionen henviser til tidslinjefilen med navn
- en læsning af en fil, Steam skriver, som ikke kan parses, selv når dens slutning er lukket: tælles (`bad` i adapterens tilstand) og læses igen ved næste ændring, hvor dens poster tages med

**Størrelse**: få hundrede poster på 100-300 bytes pr. spilletime: langt under 1 MB pr. time

## Verificeret {#verified}

testet på rigtige tidslinjefiler fra en lokal installation: achievement-, gamemode- og error-poster samt spillenes egne event-, state_description- og phase-poster; filformatet selv er udokumenteret

## Kilde {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
