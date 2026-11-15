---
title: "Minecraft (logbestanden)"
nav_order: 33
lang: "nl"
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (logbestanden) {#minecraft-log-files}

Terwijl je Minecraft speelt, leest de watcher de bestanden die het spel schrijft en slaat op wat er gebeurde, zodat je het later op een kaart in de 3DHeat-viewer kunt bekijken.

*Technische details: adapter `minecraft`, soort [`log`](sources-and-rules.md); hij draait zolang `javaw.exe` of `java.exe` loopt en zoekt elke 0,5 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- de positie van de eigen speler en die van andere spelers (blokken = m, y omhoog) elke keer dat de wereld wordt opgeslagen, met de dimensie als sessie
- spawn met positie wanneer een speler inlogt op de (geïntegreerde) server
- binnenkomen, weggaan, doden met het doodsbericht, voortgang (advancements), chatregels
- doden, voortgang, chatberichten; uit het statistiekenbestand: speeltijd, afstand, kills van monsters en spelers, sprongen, schade, gedolven blokken, gemaakte items (het aandeel van deze sessie)
- elke logregel en elk opgeslagen statistiek-, voortgangs- en spelersbestand geheel in heat.raw.parquet

## Waar het vandaan komt {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (gevolgd), saves\\&lt;world>\stats\\&lt;uuid>.json en saves\\&lt;world>\playerdata\\&lt;uuid>.dat / level.dat (gzip NBT), gelezen wanneer het spel ze opslaat

## Hoe je het aanzet {#how-to-switch-it-on}

Je hoeft niets aan te zetten: de watcher leest de bron zoals het spel of het platform die aanbiedt.

## Hoe het werkt {#how-it-works}

Minecraft (Java Edition): de log-, statistiek- en spelersbestanden die het spel schrijft.

Waar (`%APPDATA%\.minecraft\`):

* `logs\latest.log` - de log van het spel, bij elke start nieuw (de oude wordt
  ingepakt tot een gedateerde .log.gz). Regels `[hh:mm:ss] [thread/LEVEL]: bericht`
  (modloaders schrijven `[ddMMMyyyy hh:mm:ss.mmm] [thread/LEVEL] [logger/]: ...`).
  Wat spelers in de chat zien staat erin: binnenkomen en weggaan, doodsberichten,
  voortgang, chat - de geïntegreerde server van een wereld voor één speler schrijft
  dezelfde regels nog een keer, dus een regel die binnen dezelfde seconde herhaald wordt, telt
  één keer. "Setting user: <name>" noemt de speler; de regel van de server
  "<name>[...] logged in with entity id N at (x, y, z)" geeft waar ze verschenen.
* `saves\<world>\stats\<uuid>.json` - het statistiekenscherm, geschreven wanneer
  de wereld wordt opgeslagen (automatisch opslaan elke paar minuten, en bij het verlaten): `stats` ->
  `minecraft:custom` (play_time in ticks, mob_kills, \*_one_cm afstanden, jump,
  ...), `minecraft:mined`, `minecraft:crafted`, ... Totalen voor de wereld; de
  cijfers van de sessie zijn het verschil met wat het bestand zei toen het spel
  startte. Formaat: <https://minecraft.wiki/w/Statistics>
* `saves\<world>\playerdata\<uuid>.dat` (en `level.dat` -> Data -> Player
  voor een host van een wereld voor één speler) - gzip-gecomprimeerde NBT, geschreven bij dezelfde opslagbeurten:
  `Pos` [x, y, z] als doubles, `Rotation` [yaw, pitch], `Dimension`
  ("minecraft:overworld"; een int 0/-1/1 vóór 1.16). NBT volgens
  <https://minecraft.wiki/w/NBT_format> - hier gelezen door een eigen kleine lezer.
* `saves\<world>\advancements\<uuid>.json` - de voortgang van het scherm met
  voortgang, geschreven bij dezelfde opslagbeurten.

Coördinaten zijn blokken, één blok is één meter, y omhoog; x oost, z zuid - een
rechtshandig stelsel, getekend zoals het is. Posities komen alleen wanneer de wereld wordt opgeslagen, dus een
route is een paar punten per automatisch opslaan, geen spoor; de dimensie is de
`session`, zodat de Nether niet over de Overworld wordt getekend.

Alles wat gelezen wordt, wordt geheel bewaard in het ruwe bijbestand van de sessie (converterregel van 3DHeat):
elke logregel onder zijn niveau (`INFO`, `WARN`, `ERROR`, ...; een regel zonder de
haakjeskop, zoals een stacktrace, als `untagged`), en elk opgeslagen bestand onder zijn soort
(`stats`, `advancements`, `playerdata`, `level.dat`) - JSON als tekst, NBT als zijn bytes. De
cijfers van een statistiekenbestand zijn alleen te begrijpen naast wat het zei toen het spel begon,
dus die eerste kopie wordt ook bewaard (`baseline`), de eerste keer dat het bestand verandert.

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `y` |
| Eenheden | blokken (1 blok = 1 m) |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities hiermee) | 1 |

Deze gaan in de `meta.json` van elke sessie (`axes`) en, wanneer de sessie posities heeft, in de footer van `heat.parquet`, zodat de 3DHeat-viewer de rijen zelf draait en schaalt - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Als online gespeeld gemarkeerd (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `log`: hij leest alleen wat het spel of platform uitgeeft (bestanden die het spel schrijft terwijl het draait), dus hij neemt ook op bij online spel, net als offline; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (de `stats` van elke sessie in `meta.json` en de tabel `stats` in `watcher.sqlite`):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggelaten. Naast de rijen wordt elk pakket, elke pagina, regel of antwoord die de adapter ontvangt ongewijzigd bewaard in de `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam is bewaard; `used` markeert wat ook rijen is geworden), en `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- latest.log: de naam van de speler (`Setting user`), inloggen met positie, binnenkomen, weggaan, doden met het doodsbericht, voortgang, chatregels, het stoppen van de server
- stats/<uuid>.json: speeltijd, afstand, kills van monsters en spelers, sprongen, schade toegebracht en ontvangen, gedolven blokken, gemaakte items - het aandeel van deze sessie
- playerdata/<uuid>.dat en level.dat (NBT): positie, dimensie, yaw, pitch, gezondheid, XP-niveau

**Ongewijzigd bewaard**

- elke regel van latest.log geheel, `type` = zijn niveau (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`) met de thread van de logger in `thread`, `used` waar het een rij werd; een regel zonder de haakjeskop (een stacktrace, een banner van een mod) als `untagged`
- elke stats/<uuid>.json geheel als tekst, `type` `stats` (`used`: zijn cijfers staan in de statistieken), met de eerste kopie uit het begin van het spel als `baseline`
- elke advancements/<uuid>.json geheel als tekst, `type` `advancements` (elk criterium en wanneer het is gehaald; nog niet in rijen omgezet)
- elke playerdata/<uuid>.dat en level.dat geheel als bytes (gzip-NBT), `type` `playerdata` / `level.dat`, `used` waar het een positie gaf: inventaris, enderkist, effecten, spawnpunt, spelregels, wereldseed en tijd staan alleen hier
- elk opgeslagen bestand heeft `world` en `file` (het pad onder `saves`)

**Niet beschikbaar**

- een spoor van posities: het spel schrijft de positie van de speler alleen wanneer de wereld wordt opgeslagen (elke paar minuten en bij het verlaten)
- posities op een server die iemand anders host: de wereldbestanden staan op de server, niet hier; dan wordt alleen de log gelezen
- de wereld zelf (region .mca-bestanden, entiteiten, data/\*.dat-kaarten en raids): groot, en het terrein, niet het spel
- logs van eerdere sessies (logs/\*.log.gz): bewaard wanneer ze gespeeld werden
- Bedrock Edition: die schrijft zo'n log of zulke bestanden niet

**Grootte**: latest.log 0,1-2 MB per uur (meer met mods); een statistiekenbestand 5-50 KB en een spelersbestand 5-100 KB per automatisch opslaan, level.dat 1-20 KB - in totaal ongeveer 1-5 MB per uur; zstd in heat.raw.parquet maakt de tekst ongeveer een tiende (de NBT-bestanden zijn al gzip)

## Geverifieerd {#verified}

getest op gesimuleerde logregels, statistieken-JSON en NBT-bestanden die volgens de gepubliceerde indelingen zijn gemaakt; nog niet getest tegen het spel

## Bron {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
