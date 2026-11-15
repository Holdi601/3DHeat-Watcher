---
title: "Steam Timeline (plattform)"
nav_order: 43
lang: "sv"
source: game-steam-timeline.md
source_hash: "3a502e4ad09e"
nav_exclude: true
search_exclude: true
---
# Steam Timeline (plattform) {#steam-timeline-platform}

Watchern sparar det Steam Timeline håller om dina spel, så att du senare kan titta på din historik som statistik och en tidslinje.

*Tekniska detaljer: adapter `steam-timeline`, typ [`platform`](sources-and-rules.md); den körs hela tiden (den väntar inte på att ett spel startar) och letar efter ny data var 10 s.*

## Vad som spelas in {#what-is-recorded}

- en session per tidslinjefil: dess start och slut (session_start, session_end)
- prestationer upplåsta under spelandet, med tid
- ändringar av spellägen (spelar, förbereder, menyer, laddningsskärm)
- händelser spel lägger till via ISteamTimeline, med titel och beskrivning, under deras ikons namn
- spelfaser (en match, ett uppdrag) med deras taggar; händelser inuti en fas bär dess id som session
- tillståndsbeskrivningar som spelet visar på tidslinjen ("Round 3")
- Steams egna inspelningsfel

## Var den kommer ifrån {#where-it-comes-from}

%STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json

## Så slår du på det {#how-to-switch-it-on}

Steam > Inställningar > Spelinspelning: spela in i bakgrunden eller på begäran (Steam skriver tidslinjer då)

## Så fungerar det {#how-it-works}

Det launchern och grafikdrivrutinen sparar om spelandet: Steams statistik, prestationer, speltid och tidslinjer samt NVIDIAs höjdpunkter och klipp.

Ingen av dessa källor behöver att ett spel samarbetar eller körs, så de tre adaptrarna här är alltid på och tittar i ett par filer var några sekunder.

#### Steam Timeline (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`,
skrivs medan Steams spelinspelning är på. Filen är JSON med strängnummer: "daterecorded" (Unix-sekunder),
"starttime"/"endtime" (ms) och "entries", var och en {"id", "time" (ms sedan daterecorded), "type", ...}.
Typer sedda i riktiga filer:
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
Filens layout är Steams och odokumenterad; fälten är API:ets parametrar. Alla andra typer spelas in under sitt eget namn med sina fält.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Samma modul används även för: [NVIDIA-höjdpunkter (plattform)](game-nvidia-highlights.md), [Steam-statistik (plattform)](game-steam-stats.md).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner registreras | nej |
| Upåtaxel | `y` |
| Enheter | meter |
| Speglad för visaren | ingen |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv – se [Data](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerad som spelad online (`multiplayer`): **nej**. `games --markdown` visar detta som "single-player".
- Typ `platform`: den läser bara det spelet eller plattformen lämnar ut (det Steam eller grafikdrivrutinen sparar), så den spelar in även i onlinespel som offline; flaggan avgör bara om minnet någonsin får läsas.
- Minne: läses **aldrig** av denna adapter. Bara `memory`-adaptrar läser minne, och aldrig för ett spel markerat som spelat online – se [Källor och regler](sources-and-rules.md).

## Statistik som registreras {#statistics-recorded}

Statistiknycklar som adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

En nyckel inom klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell över spelets fält eller från spelets egna statistiknamn finns inte med i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

Watchern följer 3DHeats [omvandlarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det som källan innehåller läses eller behålls, aldrig kastas bort. Förutom raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som behålls med namn; `used` markerar det som också blev rader), och `meta.json`s `selfCheck.completeness` räknar varje `type` – `lost` är 0.

**Läst**

- varje post en gång, som en rad vid sin tid: dess typ, varje rent fält (title, description, icon, priority, duration, possible_clip, prestationens namn, läge, ...), en fas taggar grupperade efter `group`, prestationens visningsnamn från statistikschemat; filens start och slut

**Behållet råa**

- varje post helt som JSON under Steams egna `type` (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, vilken annan typ som helst): kapslade fält – en taggs ikon och prioritet, allt en senare Steam lägger till – finns bara här
- `timeline`: filens egna fält (daterecorded, starttime, endtime, andra), när sessionen öppnas och igen när de ändras

**Inte tillgängligt**

- inspelningen själv (video): Steam behåller den i sina egna mappar; sessionen hänvisar till tidslinjefilen med namn
- en läsning av en fil Steam skriver som inte går att tolka även med slutet stängt: räknas (`bad` i adapterns tillstånd) och läses igen vid nästa ändring, då tas dess poster

**Storlek**: några hundra poster på 100–300 byte per timme spelat: långt under 1 MB per timme

## Verifierad {#verified}

testad på riktiga tidslinjefiler från en lokal installation: prestations-, gamemode-, error- och spelens egna event-, state_description- och phase-poster; filformatet självt är odokumenterat

## Källa {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
