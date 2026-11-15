---
title: "Path of Exile (logbestanden)"
nav_order: 36
lang: "nl"
source: game-poe.md
source_hash: "9facfd5a1551"
nav_exclude: true
search_exclude: true
---
# Path of Exile (logbestanden) {#path-of-exile-log-files}

Terwijl je Path of Exile speelt, leest de watcher de bestanden die het spel schrijft en slaat hij op wat er gebeurde, zodat je het later kunt bekijken als statistieken en tijdlijn.

*Technische details: adapter `poe`, soort [`log`](sources-and-rules.md); hij draait zolang `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` of `PathOfExile_x64_KG.exe` actief is en zoekt elke 0,5 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- zones waar je binnengaat, met het gebiedsniveau, het gebieds-id en zijn seed
- level-ups met klasse en level
- doden ("has been slain")
- spelers die het gebied in en uit gaan, fluisterberichten in en uit, handelsverzoeken, geaccepteerde handel
- elke Client.txt-regel van deze sessie ongewijzigd in heat.raw.parquet
- doden, behaalde levels, hoogste level, betreden zones, verschillende zones, fluisterberichten, handelsverzoeken, handel

## Waar het vandaan komt {#where-it-comes-from}

&lt;install>\logs\Client.txt van Path of Exile of Path of Exile 2 (wordt gevolgd; de installatiemap is die van het draaiende uitvoerbare bestand)

## Hoe je het aanzet {#how-to-switch-it-on}

Niets hoeft aangezet te worden: de watcher leest de bron zoals het spel of platform die aanbiedt.

## Hoe het werkt {#how-it-works}

Path of Exile en Path of Exile 2: het clientlogboek, `<install>\logs\Client.txt`.

Beide spellen voegen aan één Client.txt in hun installatiemap toe zolang ze geïnstalleerd zijn (het groeit over alle starts heen). Regels zien er zo uit:

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- lokale tijd, een milliseconde-teller, een hash, het level en de thread, daarna wat het chatvenster toont. De berichten zijn van de Engelstalige client; een client in een andere taal schrijft ze vertaald en wordt hier niet begrepen. Niets geeft een positie. Het formaat is niet door Grinding Gear Games gedocumenteerd; het is het platte-tekstlogboek van het spel, zoals communitytools (handelshulpmiddelen, levelgidsen) het al jaren lezen - bijv. <https://github.com/klayveR/poe-log-monitor> (MIT) voor de lijst met gebeurtenissen.

De installatiemap is die van het draaiende uitvoerbare bestand; zonder die worden de Steam-bibliotheken en de standaardmap van de zelfstandige client doorzocht.

Elke regel van deze sessie wordt ongewijzigd bewaard in het ruwe bijbestand van de sessie (converterregel van 3DHeat), of hij iets betekent of niet: `type` is het niveau en de logger tussen haakjes (`INFO Client`, `DEBUG Client`, `WARN Client`, ...), een tijdgestempelde regel zonder haakjes is `untagged`, een regel zonder tijdstempel `untimed`.

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | nee |
| Omhoog-as | `y` |
| Eenheden | geen posities opgeslagen |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities ermee) | 1 |

Dit gaat in het `meta.json` (`axes`) van elke sessie en, als de sessie posities heeft, in de footer van `heat.parquet`. De 3DHeat-viewer draait en schaalt de rijen daardoor zelf - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `log`: hij leest alleen wat het spel of platform uitgeeft (bestanden die het spel schrijft terwijl het draait), dus hij legt ook online spel vast; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (elke `stats` van de sessie in `meta.json` en de tabel `stats` van `watcher.sqlite`):

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met de velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggegooid. Naast de rijen wordt elk pakket, elke pagina, regel of elk antwoord dat de adapter ontvangt, ongewijzigd bewaard in `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam bewaard wordt; `used` markeert wat ook rijen werd). `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- `You have entered <zone>`, met het gebiedsniveau, het gebieds-id en de seed van de regel `Generating level` ervoor
- `<name> (<class>) is now level <n>`, `<name> has been slain`, spelers die het gebied in en uit gaan, fluisterberichten in en uit (met of het een handelsverzoek is), geaccepteerde en geannuleerde handel

**Ruw bewaard**

- elke regel van deze sessie ongewijzigd, `type` = het niveau en de logger tussen haakjes (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client`, ...), `used` waar hij een rij werd: globale, handels-, groeps- en gildechat, `Connecting to instance server`, AFK- en DND-meldingen, de antwoorden op chatcommando's zoals `/played` en `/deaths`, de laad- en motorregels van de client - bewaard, nog niet tot rijen gemaakt
- een tijdgestempelde regel zonder haakjes (`***** LOG FILE OPENING *****`) als `untagged`, een regel zonder tijdstempel als `untimed`

**Niet beschikbaar**

- posities: niets in het logboek geeft er een
- wat een client in een andere taal schrijft: de regels worden bewaard, maar alleen de Engelse berichten worden tot rijen gemaakt
- regels van eerdere starts: Client.txt groeit over starts heen; regels met een tijdstempel van vóór deze run van het spel blijven liggen (ze zijn bewaard toen ze gespeeld werden)
- doden, schade, buit en de passieve boom: het spel logt die niet

**Grootte**: Client.txt groeit ongeveer 0,3-3 MB per uur (meest door DEBUG-regels tijdens het laden van gebieden, meer bij drukke handelschat); zstd in heat.raw.parquet maakt het ongeveer een tiende

## Getest {#verified}

getest op synthetische Client.txt-regels in het formaat van het spel; nog niet getest tegen het spel

## Bron {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
