---
title: "Steam Timeline (platform)"
nav_order: 44
lang: "nl"
source: game-steam-timeline.md
source_hash: "3878efe0d7f1"
nav_exclude: true
search_exclude: true
---
# Steam Timeline (platform) {#steam-timeline-platform}

De watcher bewaart wat Steam Timeline over je spellen bijhoudt, zodat je je geschiedenis later kunt bekijken als statistieken en als tijdlijn.

*Technische details: adapter `steam-timeline`, soort [`platform`](sources-and-rules.md); hij draait altijd (hij wacht niet tot een spel start) en kijkt elke 10 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- één sessie per timelinebestand: het begin en einde ervan (session_start, session_end)
- achievements die tijdens het spelen worden ontgrendeld, met tijdstip
- wijzigingen van de spelmodus (spelen, voorbereiden, menu's, laadscherm)
- gebeurtenissen die spellen toevoegen via ISteamTimeline, met titel en beschrijving, onder de naam van hun pictogram
- spelfasen (een wedstrijd, een missie) met hun labels; gebeurtenissen binnen een fase dragen zijn id als session
- statusbeschrijvingen die het spel op de tijdlijn toont ("Ronde 3")
- de eigen opnamefouten van Steam

## Waar het vandaan komt {#where-it-comes-from}

%STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json

## Zo zet je het aan {#how-to-switch-it-on}

Steam > Instellingen > Game Recording: neem op de achtergrond of op verzoek op (Steam schrijft dan timelines)

## Hoe het werkt {#how-it-works}

Wat de launcher en de grafische driver over het spelen bijhouden: de statistieken,
achievements, speeltijd en tijdlijnen van Steam, en de highlights en clips van NVIDIA.

Geen van deze bronnen heeft een spel nodig dat meewerkt of draait, dus de
drie adapters hier staan altijd aan en kijken elke paar seconden naar een paar bestanden.

#### Steam Timeline (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`,
geschreven terwijl Steam Game Recording aan staat. Het bestand is JSON met getallen
als tekst: "daterecorded" (Unix-seconden), "starttime"/"endtime" (ms) en
"entries", elk {"id", "time" (ms sinds daterecorded), "type", ...}. Typen die in
echte bestanden voorkomen:
```text
achievement        achievement_name - Steam voegt deze toe voor elk spel
gamemode           mode, een ETimelineGameMode: 1 spelen, 2 voorbereiden, 3 menu's,
                   4 laadscherm
error              description - van Steam zelf ("#GameRecording_RecordingFailed")
event              een AddInstantaneousTimelineEvent/AddRangeTimelineEvent van een spel:
                   title, description, icon, priority, duration (ms),
                   possible_clip - "You killed <name>" / "with the <weapon>"
state_description  title - SetTimelineTooltip ("Round 3")
phase              een StartGamePhase..EndGamePhase-spanne: duration (ms), tags
                   [{name, icon, group, priority}] (modus, kaart ...)
```
De indeling van het bestand is van Steam en niet gedocumenteerd; de velden zijn de
parameters van de API. Elk ander type wordt bewaard onder zijn eigen naam met zijn velden.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Dezelfde module dient ook: [NVIDIA-highlights (platform)](game-nvidia-highlights.md), [Steam-statistieken (platform)](game-steam-stats.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | nee |
| Omhoog-as | `y` |
| Eenheden | meter |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities hiermee) | 1 |

Deze gaan in het `meta.json` (`axes`) van elke sessie en, als de sessie posities heeft, in de footer van `heat.parquet`, zodat de 3DHeat-viewer de rijen zelf draait en schaalt - zie [De gegevens](the-data.md).

## Multiplayer {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **nee**. `games --markdown` toont dit als "single-player".
- Soort `platform`: hij leest alleen wat het spel of platform aflevert (wat Steam of de grafische driver bijhoudt), dus hij legt ook online spel vast, net als offline spel; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: wordt door deze adapter **nooit** gelezen. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (de `stats` van elke sessie in `meta.json` en de tabel `stats` van `watcher.sqlite`):

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met de velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt die.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggegooid. Naast de rijen wordt elk pakket, elke pagina, regel of antwoord dat de adapter ontvangt, als geheel bewaard in het `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat bij naam bewaard is; `used` markeert wat ook rijen is geworden), en `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- elke entry één keer, als rij op zijn tijdstip: zijn type, elk gewoon veld (title, description, icon, priority, duration, possible_clip, de naam van het achievement, mode, ...), de labels van een fase per groep, de weergavenaam van het achievement uit het statistiekenschema; het begin en einde van het bestand

**Ruw bewaard**

- elke entry geheel als JSON onder het eigen `type` van Steam (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, elk ander type): geneste velden - het pictogram en de prioriteit van een label, alles wat een latere Steam toevoegt - staan alleen hier
- `timeline`: de eigen velden van het bestand (daterecorded, starttime, endtime, elk ander), wanneer de sessie opent en opnieuw wanneer ze veranderen

**Niet beschikbaar**

- de opname zelf (video): Steam bewaart die in eigen mappen; de sessie verwijst naar het timelinebestand bij naam
- een lezing van een bestand dat Steam schrijft en dat zelfs met gesloten einde niet te ontleden is: geteld (`bad` in de status van de adapter) en bij de volgende wijziging opnieuw gelezen, waarna de entries worden meegenomen

**Omvang**: een paar honderd entries van 100-300 bytes per uur spelen: ruim minder dan 1 MB per uur

## Getest {#verified}

getest op echte timelinebestanden van een lokale installatie: achievement-, gamemode-, error- en de eigen event-, state_description- en phase-entries van spellen; het bestandsformaat zelf is niet gedocumenteerd

## Bron {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Gegenereerd uit de adapter door tools/gen_game_pages.py; wijzig de adapter en draai het opnieuw in plaats van deze pagina te bewerken. -->
