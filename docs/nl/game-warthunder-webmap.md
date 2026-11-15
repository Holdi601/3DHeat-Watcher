---
title: "War Thunder (spelstatus)"
nav_order: 47
lang: "nl"
source: game-warthunder-webmap.md
source_hash: "d6026c277030"
nav_exclude: true
search_exclude: true
---
# War Thunder (spelstatus) {#war-thunder-game-state}

Terwijl je War Thunder speelt, slaat de watcher op wat het spel meldt aan programma's op je eigen computer. Zo kun je het later op een kaart in de 3DHeat-viewer bekijken.

*Technische details: adapter `warthunder-webmap`, soort [`gsi`](sources-and-rules.md); hij draait zolang `aces.exe` actief is en zoekt elke 0,5 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- eigen positie (oost/noord op de kaart in meters; hoogte uit /state in een vliegtuig, anders 0) twee keer per seconde, koers, snelheid
- spawns en het verlaten van de kaart door het eigen voertuig (vernietigd, geland, terug naar de hangar), één sortie per keer
- andere vliegtuigen en grondeenheden op de minimap als posities met gevolgde id's en zijde (geen hoogte)
- vliegvelden, veroveringszones en bases één keer, en zones die van zijde wisselen
- regels uit de kill- en schadefeed (wie, voertuig, werkwoord); de kills en doden van de speler als je naam ingesteld is (`config --set player_names.warthunder-webmap=<name>`)
- spawns, afstand, hoogste hoogte, hoogste echte snelheid (TAS), voertuig; kills en doden als je naam ingesteld is
- elk antwoord van de webmap heel bewaard in heat.raw.parquet - de volledige /state en /indicators, de chat, de doelen van het gevecht en het beeld van de kaart inbegrepen; tussen gevechten in een eigen sessie

## Waar het vandaan komt {#where-it-comes-from}

de lokale webmap van het spel, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## Zo zet je het aan {#how-to-switch-it-on}

Er hoeft niets aangezet te worden: de watcher leest de bron zoals het spel of platform die aanbiedt.

## Hoe het werkt {#how-it-works}

War Thunder: de eigen lokale webmap van het spel op <http://127.0.0.1:8111>.

Het spel levert de pagina die een tweede scherm of een telefoon kan tonen (de "webmap"), en de JSON die erachter zit, terwijl het draait - in elke modus, ook multiplayer:

```text
/map_info.json   {"map_min": [x, y], "map_max": [x, y], "grid_steps", "grid_zero", "map_generation",
                  "hud_type", "valid"}: the map's extent in metres; valid false in the hangar
/map_obj.json    [{"type": aircraft|ground_model|airfield|capture_zone|bombing_point|defending_point|
                  respawn_base_*|..., "icon": Player|Fighter|Bomber|Mediumtank|SPAA|..., "color": "#rrggbb",
                  "x", "y" (0..1 of the map picture, y down), "dx", "dy" (direction),
                  airfields "sx", "sy", "ex", "ey"}]: what the minimap shows, the player's own
                  vehicle with icon "Player"; no ids, no heights
/state           {"valid", "H, m", "TAS, km/h", "IAS, km/h", "M", "Vy, m/s", ...}: flight values,
                  valid only in an aircraft
/indicators      {"valid", "army": air|tank|..., "type": the vehicle}
/hudmsg?lastEvt=N&lastDmg=M   {"events": [...], "damage": [...]} newer than the ids given, each
                  {"id", "msg", "sender", "enemy", "mode", "time"}; damage lines read like
                  "Name (Vehicle) shot down Name (Vehicle)"
/gamechat?lastId=N  the chat newer than the id given, [{"id", "msg", "sender", "enemy", "mode", "time"}]
/mission.json    the battle's objectives and their status
/map.img         the map's picture the page draws the objects on
```

Elk antwoord wordt heel bewaard in de ruwe bijlage van de sessie, onder zijn eindpunt
(map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img);
tussen gevechten gaan de antwoorden naar een eigen sessie.

Een positie op de kaart wordt meters met de omvang: u = min_x + x \* (max_x - min_x)
oost, v = max_y - y \* (max_y - min_y) noord (de y van de afbeelding loopt naar beneden). Rijen zijn
x = u, y = hoogte (de `H, m` van het eigen vliegtuig; 0 voor al het andere), z = v, dus
Y is omhoog; z wordt voor de viewer gespiegeld zodat noord niet naar het zuiden getekend wordt.

Kleuren vertellen de zijden zoals de speler ze ziet: eigen geel (#faC81E standaard), squad groen, geallieerden blauw (#174DFF), vijanden rood (#f40C00); kleurenblinde paletten veranderen ze, dus de tint beslist, niet de precieze waarde. Het spel noemt niemand op de kaart en geeft objecten geen id's: andere objecten krijgen hier id's doordat ze van poll tot poll gevolgd worden (het dichtstbijzijnde van hetzelfde type en icoon), wat twee vliegtuigen van één type die dicht langs elkaar vliegen kunnen verwisselen. De eigen naam van de speler staat ook niet in de API: geef die in de instellingen (`config --set player_names.warthunder-webmap=<your name>`), dan worden kill-feedregels over de speler kills en doden; zonder die naam worden ze als gewone kill-feed-regels opgeslagen.

Bronnen: de eigen pagina van het spel op <http://127.0.0.1:8111> en zijn JSON; de veldfeiten
zoals gedocumenteerd door het project JoyPro 2 (docs/telemetry-recording.md; GPL, alleen voor de feiten gebruikt).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `y` |
| Eenheden | meter (oost/noord op de kaart; hoogte alleen voor het eigen vliegtuig) |
| Gespiegeld voor de viewer | `z` |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities ermee) | 1 |

Deze gaan in het `meta.json` (`axes`) van elke sessie en, als de sessie posities heeft, in de footer van `heat.parquet`. Zo draait en schaalt de 3DHeat-viewer de rijen zelf - zie [De gegevens](the-data.md).

## Meerspelers {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `gsi`: het leest alleen wat het spel of platform uitgeeft (een game-state integration of lokale API die het spel aanbiedt), dus het legt ook online spel vast, net als offline. De vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: wordt door deze adapter **nooit** gelezen. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam zet (de `stats` van elke sessie in `meta.json` en de tabel `stats` in `watcher.sqlite`):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is een sleutel per team). Sleutels die de code uit een tabel met velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt die wel.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat, wordt gelezen of bewaard, nooit weggegooid. Naast de rijen wordt elk pakket, elke pagina, regel of antwoord dat de adapter ontvangt, heel bewaard in `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam bewaard is; `used` markeert wat ook rijen werd). De `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- /map_info.json: de omvang en het raster van de kaart (meters, het id van de kaart) in meta.json; een ongeldige stopt het gevecht
- /map_obj.json (twee keer per seconde): het eigen voertuig, andere vliegtuigen en grondeenheden (gevolgde id's, zijde uit de kleur, icoon, koers, kleur) en vliegvelden, zones en bases als rijen
- /state (twee keer per seconde, in een vliegtuig): hoogte, TAS, IAS, Mach en Vy op de eigen rijen
- /indicators (elke 2 s): leger en voertuigtype
- /hudmsg (eenmaal per seconde): regels uit de kill- en schadefeed als kills, doden, treffers en feedrijen; andere HUD-gebeurtenissen als rijen

**Heel bewaard**

- elk antwoord heel, `text` de JSON zoals het spel die stuurde, onder zijn eindpunt: `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission`; `map_img` de bytes van het beeld van de kaart als `payload`, één keer per gevecht
- wat alleen de ruwe bijlage bevat: elk /state-veld buiten de vijf die gelezen worden (AoA, AoS, Ny, Wx, gas, toerental, brandstof, ... - de set verschilt per vliegtuig), elk /indicators-veld (de cockpitinstrumenten van vliegtuigen, de snelheid, versnelling, bemanning en stabilisator van tanks), de andere sleutels van de kaartobjecten (color[], blink, icon_bg, einden van vliegvelden), de sender, enemy en mode van hudmsg, de chat (/gamechat, eenmaal per seconde), de doelen van het gevecht en hun status (/mission.json, elke 10 s in een gevecht), regels die gezegd zijn voordat de watcher startte
- tussen gevechten (hangar, laden) gaan de antwoorden naar een eigen sessie, in meta.json gemarkeerd als `between_battles`, die geen rijen heeft

**Niet beschikbaar**

- namen, id's en hoogten van de voertuigen van andere spelers: de webmap heeft die niet (id's worden hier gegeven door objecten van poll tot poll te volgen); de kill-feed noemt spelers zonder posities
- alles buiten de webmap: de replays van het spel worden door de warthunder-replayconverter gelezen, en het geheugen van het spel wordt nooit gelezen (een online spel)
- /map_obj.json sneller dan twee keer per seconde: de polsfrequentie blijft laag, zodat de eigen webserver van het spel niet belast wordt

**Grootte**: ongeveer 50-120 MB per uur aan JSON vóór zstd in een gevecht (map_obj 5-15 KB twee keer per seconde, state ongeveer 1,5 KB twee keer per seconde, indicators elke 2 s, de chat en HUD-regels klein) plus het beeld van de kaart één keer per gevecht (minder dan 2 MB); 1-2 MB per uur tussen gevechten (het kaartbeeld twee keer per seconde, HUD en chat één keer, elk een kort antwoord); zstd verkleint herhaalde JSON meer dan tien keer

## Geverifieerd {#verified}

getest tegen een nep-server die antwoorden gaf in het formaat van de webmap van het spel; niet getest tegen het lopende spel

## Bron {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Gegenereerd uit de adapter door tools/gen_game_pages.py; wijzig de adapter en voer het opnieuw uit in plaats van deze pagina te bewerken. -->
