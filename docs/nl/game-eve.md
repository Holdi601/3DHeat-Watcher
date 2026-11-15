---
title: "EVE Online (logbestanden)"
nav_order: 20
lang: "nl"
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (logbestanden) {#eve-online-log-files}

Terwijl je EVE Online speelt, leest de watcher de bestanden die het spel schrijft en slaat hij op wat er gebeurde, zodat je het later kunt bekijken als statistieken en tijdlijn.

*Technische details: adapter `eve`, soort [`log`](sources-and-rules.md); hij draait zolang `exefile.exe` actief is en zoekt elke 0,5 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- toegebrachte en ontvangen schade met het andere schip, piloot, corporatie-ticker, wapen en de kwaliteit van de treffer
- toegebrachte en ontvangen missers
- uitbetaalde bounties (NPC-kills) met ISK
- sprongen tussen systemen
- elke gamelog- en chatlogregel ongewijzigd in heat.raw.parquet
- toegebrachte en ontvangen schade, treffers, missers, bounty-kills en ISK, sprongen

## Waar het vandaan komt {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt en de Chatlogs\\\*.txt ernaast (elk bestand dat is geschreven sinds de client is gestart)

## Hoe je het aanzet {#how-to-switch-it-on}

Niets hoeft aangezet te worden: de watcher leest de bron zoals het spel of platform die aanbiedt.

## Hoe het werkt {#how-it-works}

EVE Online: de gamelogs van de client, `Documents\EVE\logs\Gamelogs\*.txt`.

De client schrijft één bestand per personage per login, `<yyyymmdd>_<hhmmss>[_<character id>].txt`; loggen naar een bestand staat standaard aan. Meerdere clients die naast elkaar draaien schrijven elk hun eigen bestand, dus elk bestand dat sinds het spel startte geschreven is, wordt gevolgd. Kop en regels (EVE-tijd is UTC):

```text
------------------------------------------------------------
  Gamelog
  Listener: Character Name
  Session Started: 2024.07.02 19:41:40
------------------------------------------------------------
[ 2024.07.02 20:31:28 ] (combat) <color=0xff00ffff><b>200</b> <color=0x77ffffff><font size=10>to</font>
    <b><color=0xffffffff>Pilot[TICK](../Ship)</b><font size=10><color=0x77ffffff> - Weapon - Penetrates
[ 2024.06.25 15:20:01 ] (combat) <color=0xffcc0000><b>375</b> ... from ... - Weapon - Hits
[ 2024.06.25 15:21:00 ] (bounty) <font size=12><b><color=0xff00aa00>15,000 ISK</b> added to next bounty payout
[ 2024.06.25 15:30:00 ] (None) Jumping from System A to System B
```

(de combat-regel is één regel in het bestand). Opmaaktags worden weggehaald voordat er gezocht wordt. Het bestand was door de jaren heen UTF-8 en UTF-16; beide worden gelezen. Het formaat is niet door CCP gedocumenteerd; het is het platte-tekstlogboek van de client, gelezen zoals communitytools voor gevechtslogs het lezen (bijv. <https://docs.rs/crate/eve-log-parser>). Geen posities.

Daarnaast `Documents\EVE\logs\Chatlogs\<channel>_<yyyymmdd>_<hhmmss>[_<id>].txt`: één bestand per chatkanaal per login (als chatlogging aan staat, de standaard van de client), UTF-16, een kop met het kanaal en de luisteraar, daarna `[ yyyy.mm.dd hh:mm:ss ] Afzender > bericht`.

Elke regel van beide wordt ongewijzigd bewaard in het ruwe bijbestand van de sessie (converterregel van 3DHeat): een gamelogregel onder zijn kanaal tussen haakjes (`combat`, `notify`, `bounty`, `None`, ...), een chatregel als `chat` met zijn kanaal, en de kopregels als `gamelog header` / `chatlog header`.

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

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met de velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggegooid. Naast de rijen wordt elk pakket, elke pagina, regel of elk antwoord dat de adapter ontvangt, ongewijzigd bewaard in `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam bewaard wordt; `used` markeert wat ook rijen werd). `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- gamelog-regels `(combat)` met toegebrachte en ontvangen treffers (bedrag, andere piloot, corporatie-ticker, schip, wapen, kwaliteit van de treffer) en missers in beide richtingen
- gamelog-regels `(bounty)` met uitbetalingen in ISK, en de regels `Jumping from A to B`
- de Listener in de kop van de gamelog: van wie het logboek is

**Ruw bewaard**

- elke gamelogregel ongewijzigd, `type` = zijn kanaal tussen haakjes (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), met `file` en `listener`; `used` waar hij een rij werd; de kopregels als `gamelog header`
- elke chatlogregel ongewijzigd (Local, corporatie, fleet, privékanalen, de meldingen van `EVE System` zoals een wisseling van Local-kanaal bij een sprong), `type` `chat`, met `channel`, `listener` en `file`; de kopregels als `chatlog header`. Nog niet tot rijen gemaakt
- de opmaaktags (`<color>`, `<b>`, `<font>`) blijven in de ruwe tekst; in de rijen zijn ze weggehaald

**Niet beschikbaar**

- posities: de client schrijft er geen naar zijn logs
- gevechten van andere piloten: een gamelog is van de luisteraar zelf
- logs van eerdere logins: elke login schrijft nieuwe bestanden; die ouder zijn dan deze run van de client worden niet opnieuw gelezen
- chat als de speler het chatlogboek in de instellingen van de client heeft uitgezet
- de cache- en instellingenbestanden van de client: geen logs, en niet gedocumenteerd

**Grootte**: een gamelog is 0,1-2 MB per uur (meest in gevechten); chatlogs hangen af van de geopende kanalen - een druk Local- of fleetkanaal 0,5-3 MB per uur; zstd in heat.raw.parquet maakt het ongeveer een tiende

## Getest {#verified}

getest op synthetische gamelog-regels in het formaat van gepubliceerde community-parsers; nog niet getest tegen het spel

## Bron {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
