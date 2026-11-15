---
title: "League of Legends (spelstatus)"
nav_order: 29
lang: "nl"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (spelstatus) {#league-of-legends-game-state}

Terwijl je League of Legends speelt, slaat de watcher op wat het spel aan programma's op je eigen computer meldt, zodat je het later kunt bekijken als statistieken en tijdlijn.

*Technische details: adapter `lol-live`, soort [`gsi`](sources-and-rules.md); hij draait zolang `League of Legends.exe` actief is en zoekt elke 0,5 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- geen posities: de API heeft die niet
- killfeed: kills, deaths en assists van de speler, kills van andere champions met moordenaar, slachtoffer en assisterende spelers
- draken, heralds, baronnen, torens, inhibitors, multikills, aces, first blood, begin en einde van het spel
- eigen kills, deaths, assists, creepscore, wardscore, level, goud, champion, speltijd, resultaat
- doelen die door het team van de speler zijn behaald

## Waar het vandaan komt {#where-it-comes-from}

Live Client Data API van de gameclient, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), tijdens een wedstrijd

## Hoe je het aanzet {#how-to-switch-it-on}

Niets hoeft aangezet te worden: de watcher leest de bron zoals het spel of platform die aanbiedt.

## Hoe het werkt {#how-it-works}

League of Legends: de Live Client Data API die de gameclient tijdens een wedstrijd aanbiedt.

Terwijl een wedstrijd loopt (ook in de oefenmodus en de toeschouwersmodus), antwoordt `League of Legends.exe` op <https://127.0.0.1:2999> met wat de speler in de eigen interface van het spel kan zien:

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} vanaf EventID N: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

Er zijn geen posities: de API heeft die niet, dus een League-sessie bestaat uit gebeurtenissen en statistieken, zonder warmtetabel. Het certificaat is zelfondertekend, van Riots eigen root (`riotgames.pem`, gepubliceerd op <https://static.developer.riotgames.com/docs/lol/riotgames.pem>). De gebruiksvoorwaarden daarvan zijn niet vermeld, dus het wordt niet meegeleverd: zet het op `<data>\riotgames.pem` en de verbinding wordt ermee gecontroleerd; zonder dat bestand staat de controle uit - en dan alleen voor 127.0.0.1, het enige adres waarmee deze adapter praat.

Het beleid van Riot staat toe dat tools tonen wat de speler uit het spel zelf kan weten, en niets dat daarbuiten berekend wordt (geen timers van de tegenstander): dit legt de killfeed en het scorebord vast dat de speler ziet, en de eigen cijfers van de speler.

Elk antwoord wordt ook helemaal bewaard (converterregel van 3DHeat, docs/converters.md in de repository van de viewer): `heat.raw.parquet`, `type` het eindpunt (`allgamedata`, `eventdata`), `text` de JSON zoals de client die stuurde, `status` wanneer het niet 200 was. Een antwoord dat byte voor byte gelijk is aan het vorige van zijn eindpunt (de gebeurtenislijst zolang er niets gebeurt) wordt één keer bewaard en geteld in `unchanged_replies` van meta.json. allgamedata bevat alles wat de andere eindpunten aanbieden (activeplayer\*, playerlist, playerscores, playeritems, playersummonerspells, playermainrunes, gamestats), dus die worden niet apart opgevraagd. Antwoorden vóór een wedstrijd (het laadscherm) wachten in een achterstand en gaan in de sessie van de wedstrijd; na GameEnd blijft de sessie open tot de client sluit, zodat de antwoorden van het eindscherm erbij worden bewaard.

Bron: <https://developer.riotgames.com/docs/lol#game-client-api>

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | nee |
| Omhoog-as | `z` |
| Eenheden | geen (geen posities) |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities ermee) | 1 |

Dit gaat in het `meta.json` (`axes`) van elke sessie en, als de sessie posities heeft, in de footer van `heat.parquet`. De 3DHeat-viewer draait en schaalt de rijen daardoor zelf - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `gsi`: hij leest alleen wat het spel of platform uitgeeft (een game-state-integratie of lokale API die het spel aanbiedt), dus hij legt ook online spel vast; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (elke `stats` van de sessie in `meta.json` en de tabel `stats` van `watcher.sqlite`):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met de velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggegooid. Naast de rijen wordt elk pakket, elke pagina, regel of elk antwoord dat de adapter ontvangt, ongewijzigd bewaard in `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam bewaard wordt; `used` markeert wat ook rijen werd). `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- de killfeed uit eventdata: elke gebeurtenis eenmaal, met de benoemde velden gedecodeerd (moordenaar, slachtoffer en assisters met champion en team, structuren en hun kant, drakentype, steals, multikills, aces, first blood, het resultaat) en elk ander veld van een gebeurtenis op zijn rij onder zijn eigen naam
- uit allgamedata: de eigen kills, deaths, assists, creepscore, wardscore, level, goud, champion, de speltijd, spelmodus en map

**Ruw bewaard**

- `allgamedata`: elk antwoord helemaal (`text`), elke 2 s - activePlayer (abilities, elke championstatistiek, alle runes, goud, level), allPlayers (items met slots en prijzen, runes, summoner spells, scores, level, dood en herspawntimer, skin, lane, bot), de gebeurtenissen, gameData (modus, tijd, map, terrein); `used` waar zolang de wedstrijd loopt, onwaar op het eindscherm
- `eventdata`: elk antwoord helemaal, elke 0,5 s opgevraagd vanaf het volgende gebeurtenis-id; `used` waar het nieuwe gebeurtenissen opleverde
- een antwoord dat byte voor byte gelijk is aan het vorige van zijn eindpunt, wordt één keer bewaard en geteld (`unchanged_replies` in meta.json); foutantwoorden (het RESOURCE_NOT_FOUND van het laadscherm) worden bewaard met hun `status`, vóór de start van de wedstrijd

**Niet beschikbaar**

- posities: de API heeft die niet (geen minimap, geen coördinaten)
- de andere eindpunten (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): elk levert een deel van allgamedata, dus ze worden niet opgevraagd
- de Replay API (`/replay/*` op dezelfde poort): die speelt replays en bekeken spellen af als die in game.cfg aangezet zijn; het hoort niet bij een gespeelde wedstrijd
- de eindpunten van de lockfile van de League-client: geen gepubliceerde API (zie Bronnen en regels)
- waarden tussen twee lezingen: de API antwoordt als er gevraagd wordt en duwt niets; het scorebord wordt elke 2 s opgevraagd, de gebeurtenissen elke 0,5 s

**Grootte**: allgamedata is 15-40 KB (het bevat de hele gebeurtenislijst, die groeit) elke 2 s: ongeveer 30-70 MB per uur in `raw.bin`; eventdata komt er weinig bij, omdat onveranderde antwoorden geteld en niet opgeslagen worden; zstd maakt de herhaalde JSON in `heat.raw.parquet` tot enkele MB per uur (geschat uit het gedocumenteerde formaat)

## Getest {#verified}

getest tegen een nep-server op de computer die antwoorden in het gedocumenteerde formaat levert; nog niet getest tegen het spel

## Bron {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
