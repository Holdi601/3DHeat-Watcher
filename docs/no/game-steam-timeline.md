---
title: "Steam-tidslinje (plattform)"
nav_order: 43
lang: "no"
source: game-steam-timeline.md
source_hash: "3a502e4ad09e"
nav_exclude: true
search_exclude: true
---
# Steam-tidslinje (plattform) {#steam-timeline-platform}

Watcheren lagrer det Steam-tidslinjen holder om spillene dine, slik at du senere kan se på historikken din som statistikk og tidslinje.

*Tekniske detaljer: adapter `steam-timeline`, type [`platform`](sources-and-rules.md); den kjører hele tiden (den venter ikke på at et spill starter) og ser etter nye data hvert 10. s.*

## Hva som tas opp {#what-is-recorded}

- én sesjon per tidslinjefil: start og slutt (session_start, session_end)
- oppnåelser låst opp under spilling, med tidspunkt
- endringer av spillmodus (spiller, forbereder, menyer, lasteskjerm)
- hendelser spill legger til via ISteamTimeline, med tittel og beskrivelse, under ikonets navn
- spillfaser (en kamp, et oppdrag) med sine merkelapper; hendelser inne i en bærer dens id som session
- tilstandsbeskrivelser spillet viser på tidslinjen ("Runde 3")
- Steams egne feil ved opptak

## Hvor det kommer fra {#where-it-comes-from}

%STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json

## Slik slår du det på {#how-to-switch-it-on}

Steam > Innstillinger > Spillopptak: ta opp i bakgrunnen eller på forespørsel (Steam skriver tidslinjer da)

## Slik fungerer det {#how-it-works}

Det launcheren og grafikkdriveren holder om spilling: Steams statistikk,
oppnåelser, spilletid og tidslinjer, og NVIDIAs høydepunkter og klipp.

Ingen av disse kildene krever at et spill samarbeider eller kjører, så de tre adapterne
her er alltid på og ser på noen få filer hvert par sekund.

#### Steam-tidslinje (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`,
skrevet mens Steams spillopptak er på. Filen er JSON med tall som tekst: "daterecorded"
(Unix-sekunder), "starttime"/"endtime" (ms) og "entries", hver {"id", "time" (ms siden
daterecorded), "type", ...}. Typer sett i ekte filer:
```text
achievement        achievement_name - Steam legger til disse for hvert spill
gamemode           mode, en ETimelineGameMode: 1 spiller, 2 forbereder, 3 menyer,
                   4 lasteskjerm
error              description - Steams egen ("#GameRecording_RecordingFailed")
event              et spills AddInstantaneousTimelineEvent/AddRangeTimelineEvent:
                   title, description, icon, priority, duration (ms),
                   possible_clip - "You killed <name>" / "with the <weapon>"
state_description  title - SetTimelineTooltip ("Round 3")
phase              et StartGamePhase..EndGamePhase-spenn: duration (ms), tags
                   [{name, icon, group, priority}] (mode, map ...)
```
Filoppsettet er Steams og udokumentert; feltene er API-ets parametere. Enhver annen type
beholdes under sitt eget navn med sine felt.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Den samme modulen betjener også: [NVIDIA-høydepunkter (plattform)](game-nvidia-highlights.md), [Steam-statistikk (plattform)](game-steam-stats.md).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner tatt opp | nei |
| Opp-akse | `y` |
| Enheter | meter |
| Speilvendt for visningen | ingen |
| Enhetsskala (`scale`: visningen ganger posisjonene med den) | 1 |

Disse går inn i hver sesjons `meta.json` (`axes`) og, når sesjonen har posisjoner, i `heat.parquet`s fotnote, så 3DHeat-visningen snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **nei**. `games --markdown` viser dette som "enkeltspiller".
- Type `platform`: den leser bare det spillet eller plattformen gir ut (det Steam eller grafikkdriveren beholder), så den tar opp også i nettspill, ikke bare offline; flagget avgjør bare om minne noensinne kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som tas opp {#statistics-recorded}

Statistikknøkler som adapterens kode setter med navn (hver sesjons `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

En nøkkel i klammer fylles ut ved kjøring (`score.{team}` er én nøkkel per lag). Nøkler koden henter fra en tabell over spillets felt eller fra spillets egne statistikknavn står ikke i denne listen; «Hva som tas opp» ovenfor nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller beholdes, og det blir aldri kastet. Ved siden av radene beholdes hver pakke, side, linje eller svar adapteren mottar, helt i sesjonens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, pluss hvert felt som beholdes med navn; `used` markerer det som også ble rader), og `meta.json`s `selfCheck.completeness` teller hver `type` - `lost` er 0.

**Lest**

- hver oppføring én gang, som en rad ved sitt tidspunkt: type, hvert vanlige felt (tittel, beskrivelse, ikon, prioritet, varighet, possible_clip, oppnåelsens navn, modus ...), en fases merkelapper etter gruppe, oppnåelsens visningsnavn fra statistikkskjemaet; filens start og slutt

**Beholdt rått**

- hver oppføring hel som JSON under Steams egen `type` (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, enhver annen): nøstede felt - en merkelapps ikon og prioritet, og alt senere Steam legger til - finnes bare her
- `timeline`: filens egne felt (daterecorded, starttime, endtime, alle andre), når sesjonen åpnes og igjen når de endres

**Ikke tilgjengelig**

- selve opptaket (video): Steam beholder det i sine egne mapper; sesjonen viser til tidslinjefilen med navn
- en lesing av en fil Steam skriver, som ikke kan tolkes selv med slutten lukket: telles (`bad` i adapterens tilstand) og leses igjen ved neste endring, der oppføringene tas

**Størrelse**: noen hundre oppføringer på 100-300 byte per time spilt: godt under 1 MB per time

## Verifisert {#verified}

testet på ekte tidslinjefiler fra en lokal installasjon: oppnåelse-, gamemode-, error- og spillenes egne event-, state_description- og phase-oppføringer; filformatet selv er udokumentert

## Kilde {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
