---
title: "War Thunder (spiltilstand)"
nav_order: 46
lang: "da"
source: game-warthunder-webmap.md
source_hash: "34a876e38f09"
nav_exclude: true
search_exclude: true
---
# War Thunder (spiltilstand) {#war-thunder-game-state}

Mens du spiller War Thunder, gemmer watcheren det, spillet melder, i programmer på din egen computer, så du senere kan se det på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `warthunder-webmap`, slags [`gsi`](sources-and-rules.md); den kører, mens `aces.exe` kører, og kigger efter nye data hvert 0,5 s.*

## Hvad der optages {#what-is-recorded}

- egen position (kort øst/nord i meter; højde fra /state i fly, ellers 0) to gange i sekundet, retning, hastighed
- spawns, og at egen vogn forlader kortet (ødelagt, landet, tilbage til hangaren), én session pr. gang
- andre fly og landenheder på minikortet som positioner med sporede id'er og side (ingen højde)
- flyvepladser, erobringszoner og baser én gang, og zoner der skifter side
- dræbe- og skadesfeedlinjer (hvem, køretøj, verbum); spillerens drab og dødsfald, når dit navn er sat (`config --set player_names.warthunder-webmap=<name>`)
- spawns, distance, højeste højde, højeste sand lufthastighed, køretøj; drab og dødsfald med dit navn sat
- hvert svar fra webkortet gemt helt i heat.raw.parquet - hele /state og /indicators, chatten, slagets mål og kortets billede inklusive; mellem slagene i en session for sig selv

## Hvor det kommer fra {#where-it-comes-from}

spillets lokale webkort, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## Sådan slår du det til {#how-to-switch-it-on}

Intet skal slås til: watcheren læser kilden, som spillet eller platformen leverer den.

## Sådan virker det {#how-it-works}

War Thunder: spillets eget lokale webkort på <http://127.0.0.1:8111>.

Spillet serverer den side, en anden skærm eller en telefon kan vise (”webkortet”),
og den JSON, der ligger bag den, mens det kører - i alle tilstande, også multiplayer:

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

Hvert svar gemmes helt i sessionens rå sidecar under sit endepunkt
(map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img);
mellem slagene går svarene til en session for sig selv.

En kortposition bliver til meter med udstrækningen: u = min_x + x \* (max_x - min_x)
øst, v = max_y - y \* (max_y - min_y) nord (billedets y løber nedad). Rækkerne er
x = u, y = højde (egen flyveenheds "H, m"; 0 for alt andet), z = v, så
Y er op; z spejles for viewer, så nord ikke tegnes mod syd.

Farverne fortæller siderne, som spilleren ser dem: egen gul (#faC81E som standard),
squad grøn, allierede blå (#174DFF), fjender rød (#f40C00); farveblinde paletter
ændrer dem, så det er nuancen, der afgør, ikke den præcise værdi. Spillet navngiver ingen
på kortet og giver objekter ingen id'er: andre objekter får id'er her ved at følge dem
fra poll til poll (nærmeste af samme type og ikon), hvilket kan bytte om på to fly af
en type, der flyver tæt forbi hinanden. Spillerens eget navn står heller ikke i API'et:
angiv det i indstillingerne (`config --set
player_names.warthunder-webmap=<your name>`), så bliver dræbefeedlinjer om spilleren
til drab og dødsfald; uden det optages de som dræbefeedet.

Kilder: spillets egen side på <http://127.0.0.1:8111> og dens JSON; feltfakta som
dokumenteret af JoyPro 2-projektet (docs/telemetry-recording.md; GPL, kun brugt til
fakta).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner optaget | ja |
| Opadakse | `y` |
| Enheder | meter (kort øst/nord; højde kun for egen flyveenhed) |
| Spejlet for viewer | `z` |
| Enhedsskala (`scale`: viewer ganger positionerne med den) | 1 |

Disse går ind i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, i `heat.parquet`s footer, så 3DHeat-viewer selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Multiplayer {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser dette som "allowed (reads only what the game publishes)".
- Slags `gsi`: den læser kun det, spillet eller platformen udleverer (en game-state-integration eller lokal API, spillet serverer), så den optager også i online-spil, ligesom offline; flaget afgør kun, om hukommelsen nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der optages {#statistics-recorded}

Statistiknøglerne, som denne adapters kode sætter med navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der optages" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder bliver læst eller gemt, aldrig smidt væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar adapteren modtager, helt i sessionens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text` og derefter felter der gemmes efter navn; `used` markerer det, der også blev til rækker), og `meta.json`s `selfCheck.completeness` tæller hver `type` - `lost` er 0.

**Læst**

- /map_info.json: kortets udstrækning og gitter (meter, kortets id) ind i meta.json; en ugyldig en afslutter slaget
- /map_obj.json (to gange i sekundet): egen vogn, andre fly og landenheder (sporede id'er, side fra farven, ikon, retning, farve) og flyvepladser, zoner og baser som rækker
- /state (to gange i sekundet, i et fly): højde, TAS, IAS, Mach og Vy på egne rækker
- /indicators (hvert 2. s): hær og køretøjstype
- /hudmsg (en gang i sekundet): dræbe- og skadesfeedlinjer som drab, dødsfald, hits og feedrækker; andre HUD-hændelser som rækker

**Gemt rå**

- hvert svar helt, `text` JSON'en som spillet sendte den, under sit endepunkt: `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission`; `map_img` kortbilledets bytes som `payload`, én gang pr. slag
- det kun den rå sidecar indeholder: hvert /state-felt ud over de fem, der læses (AoA, AoS, Ny, Wx, gas, omdrejninger, brændstof, ... - ét flys sæt adskiller sig fra et andets), hvert /indicators-felt (flyenes instrumenter i cockpittet, hastigheden, gear, besætning og stabilisator for kampvogne), kortobjekternes andre nøgler (color[], blink, icon_bg, flyvepladsernes ender), hudmsg's sender, enemy og mode, chatten (/gamechat, en gang i sekundet), slagets mål og deres status (/mission.json, hvert 10. s i et slag), linjer sagt før watcheren startede
- mellem slagene (hangar, indlæsning) går svarene til en session for sig selv, markeret `between_battles` i meta.json, som ingen rækker har

**Ikke tilgængeligt**

- navne, id'er og højder på andre spilleres køretøjer: webkortet har ingen; id'er gives her ved at følge objekter fra poll til poll; dræbefeedet navngiver spillere uden positioner
- alt uden for webkortet: spillets replays læses af War Thunder replay-konverteren, og spillets hukommelse læses aldrig (et online-spil)
- /map_obj.json hurtigere end to gange i sekundet: polling-raten holdes lav, så spillets egen webserver ikke belastes

**Størrelse**: cirka 50-120 MB i timen JSON før zstd i et slag (map_obj 5-15 KB to gange i sekundet, state cirka 1,5 KB to gange i sekundet, indicators hvert 2. s, chatten og HUD-linjerne små) plus kortbilledet én gang pr. slag (under 2 MB); 1-2 MB i timen mellem slagene (kortudseendet to gange i sekundet, HUD og chat én gang, hver et kort svar); zstd reducerer gentagen JSON mere end tyve gange

## Verificeret {#verified}

testet mod en falsk lokal server, der leverer svar i formatet fra spillets webkort; ikke testet mod det kørende spil

## Kilde {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
