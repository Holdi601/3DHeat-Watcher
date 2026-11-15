---
title: "Rocket League (spelstatus)"
nav_order: 40
lang: "nl"
source: game-rocketleague-stats.md
source_hash: "3da6ea772068"
nav_exclude: true
search_exclude: true
---
# Rocket League (spelstatus) {#rocket-league-game-state}

Terwijl je Rocket League speelt, slaat de watcher op wat het spel meldt aan programma's op je eigen computer, zodat je het later op een kaart in de 3DHeat-viewer kunt bekijken.

*Technische details: adapter `rocketleague-stats`, soort [`gsi`](sources-and-rules.md); hij draait zolang `RocketLeague.exe` loopt en zoekt elke 0,05 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- balraakmomenten met de plek van de bal (XYZ, Unreal-eenheden), wie hem raakte en de snelheden
- goals met de inslagplek, de scorer, de assist en de snelheid; treffers op de lat met de plek
- het statistiekenoverzicht (demolitions, saves, shots, epic saves, ...), aftrappen, replays, begin en einde van de wedstrijd, de winnaar
- eigen goals, assists, saves, schoten, demo's, aanrakingen, de stand en de teamscores, uit UpdateState
- de eindregel van elke speler aan het eind van de wedstrijd
- je eigen rijen als `me`: de speler die je in de instellingen opgeeft (`config --set player_names.rocketleague-stats=<naam>`), anders degene die de camera van het spel buiten replays volgt
- geen posities van auto's: de API heeft ze niet

## Waar het vandaan komt {#where-it-comes-from}

Stats API: TCP-JSON-stroom van 127.0.0.1:49123 (poort in &lt;RL>\TAGame\Config\TAStatsAPI.ini of DefaultStatsAPI.ini)

## Hoe je het aanzet {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (zet PacketSendRate=30), start daarna Rocket League

Typ de opdracht in een terminal die geopend is in de map van de watcher (zie [Voordat je begint](before-you-start.md)). Als het mislukt, zegt de laatste regel waarom; [Installeren en uitvoeren](installing-and-running.md) beschrijft de gebruikelijke oorzaken.

`python -m heat3d_watch setup rocketleague-stats` toont welke bestanden het zou wijzigen; `python -m heat3d_watch setup rocketleague-stats --apply` wijzigt ze en bewaart het origineel als `<file>.heat3d-backup` (zie [Opdrachten](commands.md#setup)). Het schrijft `rocketleague-stats: changed: ...` voor elke wijziging, of `rocketleague-stats: nothing to change` wanneer het al aanstaat.

## Hoe het werkt {#how-it-works}

Rocket League: de officiële Stats API, een lokale socket waarnaar het spel de wedstrijdgegevens schrijft.

Aangezet in `<RL>\TAGame\Config\TAStatsAPI.ini` - of `DefaultStatsAPI.ini`
wanneer die niet bestaat, want het spel leest alleen dat bestand - onder
`[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   UpdateState-berichten per seconde; 0 (de standaard) zet de API uit, hooguit 120
Port             de TCP-poort waarop het spel luistert, standaard 49123 (WebPort 49124 is een WebSocket-kopie)
```

Het spel is de server: een client verbindt met 127.0.0.1:49123 en leest een stroom
JSON-objecten `{"Event": naam, "Data": {...}}` (sommige versies sturen Data als
JSON-tekst), de een na de ander zonder scheidingstekens. Gebeurtenissen worden verstuurd op
het moment dat ze plaatsvinden, los van de snelheid:

```text
UpdateState   MatchGuid, Players[] (Name, PrimaryId, Shortcut, TeamNum 0 blauw / 1 oranje,
              Score, Goals, Shots, Assists, Saves, Touches, CarTouches, Demos; autostatus
              alleen voor toeschouwers), Game (Teams[], TimeSeconds, bOvertime, Ball {Speed,
              TeamNum}, bReplay, bHasWinner, Winner, Arena, bHasTarget, Target)
BallHit       Players[] (Name, Shortcut, TeamNum), Ball {PreHitSpeed, PostHitSpeed, Location {X,Y,Z}}
GoalScored    GoalSpeed, GoalTime, ImpactLocation {X,Y,Z}, Scorer, Assister, BallLastTouch
CrossbarHit   BallLocation {X,Y,Z}, BallSpeed, ImpactForce, BallLastTouch
StatfeedEvent EventName, Type, MainTarget, SecondaryTarget
MatchEnded    WinnerTeamNum
MatchCreated, MatchInitialized, CountdownBegin, RoundStarted, GoalReplayStart/WillEnd/End,
MatchPaused/Unpaused, PodiumStart, ReplayCreated, MatchDestroyed, ClockUpdatedSeconds
```

Locaties zijn Unreal-eenheden (centimeters), Z omhoog; het veld is ongeveer 8200 x 10240
met de goals op Y = +-5120. Posities van auto's maken geen deel uit van de API: wat een plek heeft,
is de bal waar hij werd geraakt, gescoord of de lat raakte.

Elk bericht wordt ook geheel bewaard (converterregel van 3DHeat, docs/converters.md
in de repository van de viewer): `heat.raw.parquet`, `type` de Event-naam van het bericht,
`text` het object zoals het uit de stroom kwam. Een UpdateState die byte voor byte gelijk is aan
de vorige (een gepauzeerde wedstrijd, een menu) wordt één keer bewaard en geteld in
`unchanged_replies` in meta.json. Berichten tussen wedstrijden wachten in een achterstand op de
sessie van de volgende wedstrijd; wat overblijft wanneer het spel sluit, krijgt een eigen sessie.
Tekens tussen objecten die geen JSON zijn, worden bewaard als "junk".

Bronnen: <https://www.rocketleague.com/en/developer/stats-api> (de officiële pagina);
hoofdletters van de velden en de TCP-indeling gecontroleerd met de rlstatsapi-client
(<https://docs.rs/crate/rlstatsapi>, MIT; alleen voor de feiten gelezen).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `z` |
| Eenheden | Unreal-eenheden (centimeters) |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities hiermee) | 1 |

Deze gaan in de `meta.json` van elke sessie (`axes`) en, wanneer de sessie posities heeft, in de footer van `heat.parquet`, zodat de 3DHeat-viewer de rijen zelf draait en schaalt - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Als online gespeeld gemarkeerd (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `gsi`: hij leest alleen wat het spel of platform uitgeeft (een game-state-integratie of lokale API die het spel aanbiedt), dus hij neemt ook op bij online spel, net als offline; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (de `stats` van elke sessie in `meta.json` en de tabel `stats` in `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggelaten. Naast de rijen wordt elk pakket, elke pagina, regel of antwoord die de adapter ontvangt ongewijzigd bewaard in de `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam is bewaard; `used` markeert wat ook rijen is geworden), en `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- BallHit (plek, wie, team, snelheden voor en na), GoalScored (inslagplek, scorer, assist, snelheid, goaltijd), CrossbarHit (plek, laatste aanraking, snelheid, kracht), StatfeedEvent (gebeurtenis, type, hoofd- en tweede doel), MatchEnded (winnaar, resultaat), de naam van elke andere gebeurtenis als rij
- uit UpdateState: de arena, het doel van de camera buiten replays (wie `me` is), teamscores, de goals, assists, saves, schoten, demo's, aanrakingen, aanrakingen met de auto en de stand van elke speler (die van jou als statistieken, die van iedereen als `player_result` aan het eind van de wedstrijd); overtime uit ClockUpdatedSeconds

**Ongewijzigd bewaard**

- elk bericht geheel zoals het uit de stroom kwam (`text`), onder zijn eigen Event-naam: `UpdateState` (de PrimaryId en Shortcut van elke speler, de klok, de snelheid en het team van de bal, teamnamen en kleuren, replay- en winnaarvlaggen, en de autostatus waar het spel die stuurt), `BallHit`, `GoalScored` (met de laatste aanraking van de bal), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` en elke gebeurtenis die een latere versie toevoegt
- een UpdateState die byte voor byte gelijk is aan de vorige (gepauzeerd, menu's) wordt één keer bewaard en geteld (`unchanged_replies` in meta.json)
- berichten tussen wedstrijden: op hun eigen tijd vóór de start van de volgende wedstrijd; na de laatste wedstrijd in een eigen sessie (`raw_only` in meta.json)
- `unreadable`: een object dat geen Stats API-bericht is; `junk`: tekens tussen objecten

**Niet beschikbaar**

- posities van auto's en de autostatus tijdens het spelen: het spel stuurt die alleen naar toeschouwers
- UpdateState tussen twee verzendingen: het spel stuurt er PacketSendRate per seconde (`setup` zet 30, het spel staat tot 120 toe); de gebeurtenissen worden verstuurd op het moment dat ze plaatsvinden
- de WebSocket-kopie op WebPort (49124): dezelfde berichten als de TCP-poort, niet twee keer gelezen

**Grootte**: een UpdateState is 1-3 KB voor zes spelers, 30 per seconde: ongeveer 100-300 MB per uur in `raw.bin` terwijl een wedstrijd loopt, een tiende of minder in de zstd-`heat.raw.parquet` (geschat uit de gedocumenteerde indeling, niet op het spel gemeten)

## Geverifieerd {#verified}

getest op berichten in de gedocumenteerde indeling die door een nep-lokale server zijn verstuurd; nog niet getest tegen het spel

## Bron {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
