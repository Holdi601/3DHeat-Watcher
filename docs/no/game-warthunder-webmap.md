---
title: "War Thunder (spilltilstand)"
nav_order: 46
lang: "no"
source: game-warthunder-webmap.md
source_hash: "34a876e38f09"
nav_exclude: true
search_exclude: true
---
# War Thunder (spilltilstand) {#war-thunder-game-state}

Mens du spiller War Thunder, lagrer watcheren det spillet melder til programmer på din egen datamaskin, slik at du senere kan se på det på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `warthunder-webmap`, type [`gsi`](sources-and-rules.md); den kjører mens `aces.exe` går og ser etter nye data hvert 0,5 s.*

## Hva som tas opp {#what-is-recorded}

- egen posisjon (kart øst/nord i meter; høyde fra /state i fly, ellers 0) to ganger i sekundet, kurs, fart
- spawn, og at eget kjøretøy forlater kartet (ødelagt, landet, tilbake i hangaren), én sortie hver gang
- andre fly og bakkeenheter på minikartet som posisjoner med sporede id-er og side (ingen høyde)
- flyplasser, erobringssoner og baser én gang, og soner som bytter side
- drap- og skadelinjer fra drapslisten (hvem, kjøretøy, verb); spillerens drap og dødsfall når navnet ditt er satt (`config --set player_names.warthunder-webmap=<name>`)
- spawn, distanse, topphøyde, topp sann flyhastighet, kjøretøy; drap og dødsfall når navnet ditt er satt
- hvert svar fra webkartet, helt, i heat.raw.parquet - /state og /indicators fullt ut, chatten, slagmarkens mål og kartbildet inkludert; mellom kampene i en egen økt

## Hvor det kommer fra {#where-it-comes-from}

spillets lokale webkart, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## Slik slår du det på {#how-to-switch-it-on}

Ingenting må slås på: watcheren leser kilden slik spillet eller plattformen gir den.

## Slik fungerer det {#how-it-works}

War Thunder: spillets eget lokale webkart på <http://127.0.0.1:8111>.

Spillet tilbyr siden en annen skjerm eller en telefon kan vise ("webkartet"), og JSON-en bak den, mens det kjører - i alle moduser, også flerspiller:

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

Hvert svar tas vare på helt i øktens rå sidefil under sitt endepunkt (map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img); mellom kampene går svarene til en egen økt.

En kartposisjon blir til meter med utstrekningen: u = min_x + x \* (max_x - min_x) øst, v = max_y - y \* (max_y - min_y) nord (bildets y går nedover). Radene er x = u, y = høyde (den egne flyets "H, m"; 0 for alt annet), z = v, så Y er opp; z speiles for visningen, slik at nord ikke tegnes sør.

Farger forteller sidene slik spilleren ser dem: egen gul (#faC81E som standard), squad grønn, allierte blå (#174DFF), fiender røde (#f40C00); fargeblinde paletter endrer dem, så det er fargetonen som avgjør, ikke den nøyaktige verdien. Spillet navngir ingen på kartet og gir objekter ingen id-er: andre objekter får id-er her ved å følge dem fra poll til poll (nærmeste av samme type og ikon), noe som kan bytte om to fly av samme type som passerer tett. Spillerens eget navn står heller ikke i API-et: gi det i innstillingene (`config --set player_names.warthunder-webmap=<your name>`), så blir drapslinjer om spilleren til drap og dødsfall; uten det tas de opp som drapslisten.

Kilder: spillets egen side på <http://127.0.0.1:8111> og dens JSON; feltfakta slik JoyPro 2-prosjektet dokumenterer dem (docs/telemetry-recording.md; GPL, brukt bare for fakta).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner registreres | ja |
| Opp-akse | `y` |
| Enheter | meter (kart øst/nord; høyde bare for eget fly) |
| Speilet for visningen | `z` |
| Enhetsskala (`scale`: visningen ganger posisjonene med den) | 1 |

Disse havner i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet`s footer, slik at 3DHeat-vieweren snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som "allowed (reads only what the game publishes)".
- Type `gsi`: den leser bare det spillet eller plattformen gir ut (en game-state integration eller lokal API som spillet tilbyr), så den tar opp også i nettspill, både på nett og offline; flagget avgjør bare om minnet noen gang kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill som er merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som registreres {#statistics-recorded}

Statistikknøkler som denne adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

En nøkkel i klammer fylles ut ved kjøretid (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell over spillets felt eller fra spillets egne statistikknavn står ikke i denne listen; "Hva som tas opp" over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller tas vare på, og slettes aldri. I tillegg til radene tas hver pakke, side, linje eller svar adapteren mottar, vare på hel i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, pluss felt som tas vare på med navn; `used` markerer det som også ble til rader), og `selfCheck.completeness` i `meta.json` teller hver `type` - `lost` er 0.

**Leses**

- /map_info.json: kartets utstrekning og rutenett (meter, kart-id) inn i meta.json; en ugyldig en avslutter slaget
- /map_obj.json (to ganger i sekundet): eget kjøretøy, andre fly og bakkeenheter (sporede id-er, side ut fra fargen, ikon, kurs, farge) og flyplasser, soner og baser som rader
- /state (to ganger i sekundet, i et fly): høyde, TAS, IAS, Mach og Vy på egne rader
- /indicators (hvert 2. s): hær og kjøretøytype
- /hudmsg (én gang i sekundet): drap- og skadelinjer i drapslisten som drap, dødsfall, treff og feedrader; andre HUD-hendelser som rader

**Tatt vare på rått**

- hvert svar helt, `text` er JSON-en slik spillet sendte den, under sitt endepunkt: `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission`; `map_img` er kartbildets bytes som `payload`, én gang per slag
- det bare den rå sidefilen har: hvert /state-felt utover de fem som leses (AoA, AoS, Ny, Wx, gass, turtall, drivstoff, ... - ett fly har andre felt enn et annet), hvert /indicators-felt (flyenes instrumenter, fart, gir, mannskap og stabilisator for stridsvogner), kartobjektenes andre nøkler (color[], blink, icon_bg, flyplassenes ender), hudmsgs sender, fiende og modus, chatten (/gamechat, én gang i sekundet), slagmarkens mål og deres status (/mission.json, hvert 10. s i et slag), linjer sagt før watcheren startet
- mellom kampene (hangar, lasting) går svarene til en egen økt, merket `between_battles` i meta.json, som ikke har rader

**Ikke tilgjengelig**

- navn, id-er og høyder for andre spilleres kjøretøy: webkartet har ingen (id-ene gis her ved å følge objekter fra poll til poll); drapslisten navngir spillere uten posisjoner
- alt utenfor webkartet: spillets repriser leses av konverteringsverktøyet for War Thunder-repriser, og spillets minne leses aldri (et nettspill)
- /map_obj.json raskere enn to ganger i sekundet: pollingfrekvensen holdes lav, så spillets egen webtjener ikke belastes

**Størrelse**: omtrent 50-120 MB per time med JSON før zstd i et slag (map_obj 5-15 KB to ganger i sekundet, state omtrent 1,5 KB to ganger i sekundet, indicators hvert 2. s, chat og HUD-linjer små) pluss kartbildet én gang per slag (under 2 MB); 1-2 MB per time mellom slagene (kartutseendet to ganger i sekundet, HUD og chat én gang, hver et kort svar); zstd reduserer gjentatt JSON godt over tiasganger

## Verifisert {#verified}

testet mot en falsk lokal tjener som sender svar i formatet til spillets webkart; ikke testet mot det kjørende spillet

## Kilde {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
