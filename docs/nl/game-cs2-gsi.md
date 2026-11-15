---
title: "Counter-Strike 2 (spelstatus)"
nav_order: 9
lang: "nl"
source: game-cs2-gsi.md
source_hash: "2eda1106e11f"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (spelstatus) {#counter-strike-2-game-state}

Terwijl je Counter-Strike 2 speelt, slaat de watcher op wat het spel meldt aan programma's op je eigen computer. Zo kun je het later op een kaart in de 3DHeat-viewer bekijken.

*Technische details: adapter `cs2-gsi`, soort [`gsi`](sources-and-rules.md); hij draait zolang `cs2.exe` actief is en zoekt elke 0,05 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- eigen positie (wereld-XYZ, in inch) en kijkrichting tot 10 keer per seconde terwijl je leeft
- spawns (de eerste keer dat je in een ronde wordt gezien, en respawns) en doden (gezondheid naar 0, of het aantal doden)
- kills met het actieve wapen, uit de wedstrijdstatistieken
- rondes (start, einde, winnaar), bom geplant/onschadelijk gemaakt/ontploft, wedstrijdfasen en het resultaat
- kills, assists, doden, MVP's, score, geld, schade, headshot-kills, gewonnen en verloren rondes

## Waar het vandaan komt {#where-it-comes-from}

Game State Integration: HTTP-POST's naar 127.0.0.1:3311, ingesteld door &lt;CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg

## Zo zet je het aan {#how-to-switch-it-on}

`python -m heat3d_watch setup cs2-gsi --apply`, en start daarna CS2 (het leest het bestand bij het opstarten)

Typ het commando in een terminal die geopend is in de map van de watcher (zie [Voordat je begint](before-you-start.md)). Als het mislukt, zegt de laatste regel waarom. [Installeren en uitvoeren](installing-and-running.md) beschrijft de gewone oorzaken.

`python -m heat3d_watch setup cs2-gsi` laat zien welke bestanden het zou wijzigen. `python -m heat3d_watch setup cs2-gsi --apply` wijzigt ze en bewaart het origineel als `<file>.heat3d-backup` (zie [Commando's](commands.md#setup)). Het toont `cs2-gsi: changed: ...` voor elke wijziging, of `cs2-gsi: nothing to change` als het al aan staat.

Instellingen uit omgevingsvariabelen:

- `HEAT3D_CS2_GSI_PORT`: de poort waarnaar het spel stuurt (standaard 3311); het cfg-bestand van het spel moet dezelfde poort noemen

## Hoe het werkt {#how-it-works}

Valve Game State Integration: Counter-Strike 2 en Dota 2 vertellen een lokale webserver wat er gebeurt.

Beide spellen lezen bij het starten elk `gamestate_integration_*.cfg` in hun cfg-map. Vanaf dan sturen ze een JSON-document naar de `uri` van elk bestand zodra de toestand verandert (hooguit elke `throttle` seconden, en elke `heartbeat` seconden als er niets verandert). De watcher is die webserver: hij luistert alleen op 127.0.0.1, antwoordt op elke POST meteen met 200 en doet het werk in zijn eigen pollthread.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

Wat een speler krijgt toegestuurd, en dus wat opgeslagen kan worden, bepaalt het spel zelf: wat een speler mag zien.

- CS2: `provider` (de eigen steamid), `map` (naam, modus, fase warmup/live/tussenpauze/gameover, ronde, score team_ct/team_t), `round` (fase freezetime/live/over, bom geplant/ontploft/onschadelijk gemaakt, win_team), `player` (de speler die *bekeken* wordt: jezelf terwijl je leeft, een teamgenoot na je dood) met `state` (gezondheid, pantser, geld, round_kills, round_killhs, round_totaldmg), `match_stats` (kills, assists, deaths, mvps, score), `position` en `forward` als tekenreeksen "x, y, z" in wereldeenheden (inch, Z omhoog), `weapons`; `bomb` alleen voor toeschouwers. Posities van andere spelers (`allplayers_*`) worden alleen naar toeschouwers en GOTV gestuurd, dus die worden niet opgevraagd.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player` (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero` (xpos/ypos in wereldeenheden, level, alive, respawn_seconds), `buildings` (gezondheid per toren/barak/ancient), `roshan`, `events` (roshan_killed, aegis_picked_up, ...). Er is geen hoogte: z is 0. Ook opgevraagd en heel bewaard: `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`, `neutralitems`, `league` (het spel stuurt wat de eigen client van de speler heeft; welke daarvan iets bevatten tijdens het spelen in plaats van kijken, is niet getest).

Elk document wordt ook heel bewaard (de converterregel van 3DHeat, docs/converters.md in de repository van de viewer): `heat.raw.parquet`, `type` "gsi", `text` de JSON zoals die verstuurd is, alleen met het token uit het cfg-bestand onleesbaar gemaakt. Dat token is het eigen geheim van de watcher, geen spelgegevens. Documenten die verstuurd worden terwijl er geen wedstrijd open is (menu's, laden, tussen wedstrijden) wachten in een `Backlog` en gaan naar de sessie van de volgende wedstrijd, vóór de start ervan. Wat overblijft als het spel sluit, krijgt een eigen sessie die alleen die documenten bevat. Onleesbare verzoeken en verzoeken met een verkeerd token worden ook bewaard ("gsi-unreadable", "gsi-bad-auth").

Bronnen: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration>
(het formaat dat CS2 behield), <https://github.com/antonpup/CounterStrike2GSI> en
<https://github.com/antonpup/Dota2GSI> (lijsten met velden; MIT, alleen voor de feiten gelezen).

Dezelfde module levert ook: [Dota 2 (spelstatus)](game-dota2-gsi.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `z` |
| Eenheden | inch (Hammer-eenheden) |
| Gespiegeld voor de viewer | `y` |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities ermee) | 1 |

Deze gaan in het `meta.json` (`axes`) van elke sessie en, als de sessie posities heeft, in de footer van `heat.parquet`. Zo draait en schaalt de 3DHeat-viewer de rijen zelf - zie [De gegevens](the-data.md).

## Meerspelers {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `gsi`: het leest alleen wat het spel of platform uitgeeft (een game-state integration of lokale API die het spel aanbiedt), dus het legt ook online spel vast, net als offline. De vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: wordt door deze adapter **nooit** gelezen. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam zet (de `stats` van elke sessie in `meta.json` en de tabel `stats` in `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `money`, `result`, `score_other`, `score_own`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is een sleutel per team). Sleutels die de code uit een tabel met velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt die wel.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat, wordt gelezen of bewaard, nooit weggegooid. Naast de rijen wordt elk pakket, elke pagina, regel of antwoord dat de adapter ontvangt, heel bewaard in `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam bewaard is; `used` markeert wat ook rijen werd). De `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- de positie, kijkrichting, gezondheid, pantser, geld, actief wapen, helm, defusekit, flash-/rook-/vuur-hoeveelheden en uitrustingswaarde van de bekeken speler, op elke positierij terwijl het de eigen speler is (provider-steamid = steamid van de speler)
- spawns, doden (gezondheid naar 0, of het aantal doden uit de wedstrijdstatistieken), kills (als het aantal kills stijgt)
- wedstrijdfasen, rondes (freeze time, live, over, winnaar), bom geplant/onschadelijk gemaakt/ontploft, het resultaat
- kills, assists, deaths, MVP's, score, geld, schade, headshot-kills, gewonnen en verloren rondes als statistieken

**Heel bewaard**

- `gsi`: elk document dat het spel stuurt, heel, zoals verstuurd (`text`), `used` true als het in een wedstrijd gelezen is - provider (versie, tijdstempel), map (modus, teamnamen, opeenvolgende rondeverliezen, time-outs, seriewinsten, `round_wins` met de winvoorwaarde van elke ronde), round, de bekeken speler (clan, observer-slot, activiteit, elk wapen met skin, munitie en reserve), bom, faseaftellingen, en het eigen `previously`/`added`-verschil van het spel ten opzichte van de vorige post
- documenten uit menu's, laden en tussen wedstrijden: op dezelfde manier bewaard, op hun eigen tijdstip vóór de start van de volgende wedstrijd; na de laatste wedstrijd in een eigen sessie (`raw_only` in meta.json)
- `gsi-unreadable`: een verzoek dat geen JSON-object is, met de bytes als `payload` en `length`
- `gsi-bad-auth`: een verzoek met een ander token dan dat van het cfg-bestand

**Niet beschikbaar**

- andere spelers (`allplayers_*`) en granaten (`allgrenades`): het spel stuurt die alleen naar toeschouwers en GOTV, en de watcher vraagt ze niet op (Bronnen en regels); een demo heeft elke speler - zie [Counter-Strike 2 (replays)](game-cs2-demos.md)
- toestanden tussen verzoeken: het spel stuurt hooguit elke 0,1 s (`throttle`) en alleen bij een verandering, anders elke 10 s (`heartbeat`)
- het token uit het cfg-bestand, onleesbaar gemaakt in elk bewaard document: het eigen geheim van de watcher, geen spelgegevens
- verzoeken boven 10.000 wachtend (de watcher liep vast) worden geteld als `dropped_packets`, niet bewaard; een verzoek van meer dan 4 MB wordt bewaard als `gsi-unreadable` met zijn lengte, maar zonder de bytes

**Grootte**: het document van een speler is 2-4 KB, tot 10 keer per seconde verstuurd zolang er iets verandert: ongeveer 30-150 MB per uur in `raw.bin` terwijl de wedstrijd loopt, een tiende daarvan of minder in de zstd-`heat.raw.parquet` (geschat uit het gepubliceerde formaat, niet gemeten op het spel)

## Geverifieerd {#verified}

getest op documenten in het gepubliceerde GSI-formaat, verstuurd naar de lopende adapter; het opzoeken van de installatie en de cfg-map getest op een lokale installatie; niet getest tegen het lopende spel

## Bron {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Gegenereerd uit de adapter door tools/gen_game_pages.py; wijzig de adapter en voer het opnieuw uit in plaats van deze pagina te bewerken. -->
