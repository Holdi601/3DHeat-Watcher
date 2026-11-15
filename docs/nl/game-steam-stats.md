---
title: "Steam-statistieken (platform)"
nav_order: 43
lang: "nl"
source: game-steam-stats.md
source_hash: "24fa6512bd6d"
nav_exclude: true
search_exclude: true
---
# Steam-statistieken (platform) {#steam-statistics-platform}

De watcher bewaart wat Steam-statistieken over je spellen bijhoudt, zodat je je geschiedenis later kunt bekijken als statistieken en als tijdlijn.

*Technische details: adapter `steam-stats`, soort [`platform`](sources-and-rules.md); hij draait altijd (hij wacht niet tot een spel start) en kijkt elke 30 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- elke statistiek die een spel in Steam opslaat (de eigen namen en waarden ervan), per spel, bij elke wijziging
- ontgrendelde achievements met weergavenaam, beschrijving en ontgrendeltijd
- wijzigingen van statistieken met oude waarde, nieuwe waarde en verschil
- speeltijd (minuten, laatste twee weken) en het laatst gespeeld-tijdstip

## Waar het vandaan komt {#where-it-comes-from}

Steam's lokale statistiekencache %STEAM%\appcache\stats\UserGameStats_&lt;account>_&lt;appid>.bin met UserGameStatsSchema_&lt;appid>.bin; speeltijd uit %STEAM%\userdata\\&lt;account>\config\localconfig.vdf (%STEAM% uit HKCU\Software\Valve\Steam SteamPath)

## Zo zet je het aan {#how-to-switch-it-on}

Je hoeft niets aan te zetten: de watcher leest de bron zoals het spel of platform die aflevert.

## Hoe het werkt {#how-it-works}

Wat de launcher en de grafische driver over het spelen bijhouden: de statistieken,
achievements, speeltijd en tijdlijnen van Steam, en de highlights en clips van NVIDIA.

Geen van deze bronnen heeft een spel nodig dat meewerkt of draait, dus de
drie adapters hier staan altijd aan en kijken elke paar seconden naar een paar bestanden.

#### Steam-statistieken (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<account>_<appid>.bin`, door de Steam-client
herschreven zodra een spel zijn statistieken opslaat, gedecodeerd met het schema
`UserGameStatsSchema_<appid>.bin` ernaast (binaire KeyValues, zie `_steam.py`).
Statistieken zijn gehele getallen of kommagetallen zoals het spel ze definieert;
achievements zijn bits met een ontgrendeltijd in Unix-seconden. Speeltijd staat in
`<Steam>\userdata\<account>\config\localconfig.vdf` onder apps/&lt;appid>:
Playtime en Playtime2wks in minuten, LastPlayed in Unix-seconden.
Steam wordt gevonden via HKCU\Software\Valve\Steam SteamPath.
Statistieken-API: <https://partner.steamgames.com/doc/features/achievements>

Dezelfde module dient ook: [NVIDIA-highlights (platform)](game-nvidia-highlights.md), [Steam Timeline (platform)](game-steam-timeline.md).

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

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met de velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt die.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggegooid. Naast de rijen wordt elk pakket, elke pagina, regel of antwoord dat de adapter ontvangt, als geheel bewaard in het `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat bij naam bewaard is; `used` markeert wat ook rijen is geworden), en `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- elke statistiek uit het statistiekenbestand bij haar API-naam (int, float, avgrate), elke achievement-bit met zijn ontgrendeltijd, benoemd en beschreven door het schema
- wijzigingen ten opzichte van de laatste lezing (oud, nieuw, verschil), nieuwe ontgrendelingen; speeltijd, speeltijd van twee weken en laatst gespeeld uit localconfig.vdf

**Ruw bewaard**

- `UserGameStats`: de bytes van het statistiekenbestand, geheel, elke keer dat het wordt vastgelegd (de `crc`, `PendingChanges`, achievement-bits die het schema niet meer definieert en elke sleutel die de decoder overslaat staan erin)
- `UserGameStatsSchema`: de bytes van het schemabestand ernaast, zodat de statistieken alleen uit de sessie gedecodeerd kunnen worden (de namen van elke statistiek en elk achievement in elke taal, pictogrammen, vlaggen)
- `localconfig_app`: het hele blok van het spel uit localconfig.vdf als JSON (de cloud-syncstatus, startopties, badges en elke andere sleutel die Steam per spel bijhoudt) wanneer de speeltijd wordt vastgelegd
- een statistiekenbestand dat de decoder niet kan lezen (midden in het schrijven afgekapt, of een nieuwe indeling): de bytes en het schema in een sessie zonder rijen (`used` false; `unreadable` in meta.json)

**Niet beschikbaar**

- de rest van localconfig.vdf (vrienden, chat, Steam-instellingen): hoort niet bij het spel en is privé
- statistiekwaarden tussen twee schrijfbeurten: Steam herschrijft het bestand wanneer het spel zijn statistieken opslaat, meestal bij het afsluiten
- wereldwijde achievement-percentages en statistieken van andere spelers: die staan op Steam's servers, niet hier

**Omvang**: een paar KB per vastgelegde speelsessie, plus het schema (tot een paar honderd KB voor een spel met veel achievements) - ruim minder dan 1 MB per uur spelen; zstd verkleint de tekst van het schema met de helft of meer

## Getest {#verified}

getest op echte statistiekenbestanden en schema's van een lokale installatie; wijzigingsdetectie getest op bestanden die in het binaire KeyValues-formaat zijn gebouwd

## Bron {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Gegenereerd uit de adapter door tools/gen_game_pages.py; wijzig de adapter en draai het opnieuw in plaats van deze pagina te bewerken. -->
