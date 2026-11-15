---
title: "War Thunder (stanje igre)"
nav_order: 47
lang: "hr"
source: game-warthunder-webmap.md
source_hash: "d6026c277030"
nav_exclude: true
search_exclude: true
---
# War Thunder (stanje igre) {#war-thunder-game-state}

Dok igrate War Thunder, watcher sprema ono što igra javlja programima na vašem računalu, pa to kasnije možete pogledati na karti u 3DHeat pregledniku.

*Tehnički podaci: adapter `warthunder-webmap`, vrsta [`gsi`](sources-and-rules.md); radi dok je `aces.exe` pokrenut i traži nove podatke svakih 0,5 s.*

## Što se bilježi {#what-is-recorded}

- vlastita pozicija (istok/sjever na karti u metrima; visina iz /state u zrakoplovu, inače 0), smjer i brzina, dvaput u sekundi
- pojavljivanja i napuštanje karte od strane vlastitog vozila (uništeno, sletjelo, natrag u hangar), jedan sortie za svaki
- drugi zrakoplovi i kopnene jedinice na mini karti kao pozicije s praćenim ID-ovima i stranom (bez visine)
- aerodromi, zone zauzimanja i baze jednom, te zone koje promijene stranu
- retci feeda ubojstava i šteta (tko, vozilo, glagol); ubojstva i smrti igrača kad je vaše ime postavljeno (`config --set player_names.warthunder-webmap=<name>`)
- pojavljivanja, udaljenost, najveća visina, najveća stvarna brzina zraka, vozilo; ubojstva i smrti kad je vaše ime postavljeno
- svaki odgovor web karte, cjelovit u heat.raw.parquet - uključujući cijeli /state i /indicators, chat, ciljeve bitke i sliku karte; između bitaka u vlastitoj sesiji

## Odakle dolazi {#where-it-comes-from}

lokalna web karta igre, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## Kako ga uključiti {#how-to-switch-it-on}

Ništa se ne mora uključivati: watcher čita izvor kako ga igra ili platforma daje.

## Kako radi {#how-it-works}

War Thunder: lokalna web karta igre na <http://127.0.0.1:8111>.

Igra poslužuje stranicu koju drugi ekran ili telefon može prikazati ("web karta"), i JSON iza nje, dok radi - u svakom načinu rada, uključujući multiplayer:

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

Svaki odgovor čuva se cjelovito u sirovoj pomoćnoj datoteci sesije pod svojom krajnjom točkom (map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img); između bitaka odgovori idu u vlastitu sesiju.

Položaj na karti pretvara se u metre pomoću obuhvata: u = min_x + x \* (max_x - min_x) istok, v = max_y - y \* (max_y - min_y) sjever (y slike ide prema dolje). Redovi su x = u, y = visina (vlastiti zrakoplov "H, m"; 0 za sve drugo), z = v, pa je Y prema gore; z je zrcaljen za preglednik tako da sjever ne bude nacrtan na jugu.

Boje pokazuju strane onako kako ih igrač vidi: vlastita žuta (#faC81E zadano), iz vlastite skupine zelena, saveznici plava (#174DFF), neprijatelji crvena (#f40C00); palete za daltonizam mijenjaju ih, pa odlučuje nijansa, a ne točna vrijednost. Igra ne imenuje nikoga na karti i ne daje objektima ID-ove: ostalim objektima ID-ovi se ovdje dodjeljuju praćenjem od očitanja do očitanja (najbliži istog tipa i ikone), što može zamijeniti dva zrakoplova iste vrste koja prolaze blizu jedan drugome. Ni ime igrača nije u API-ju: upišite ga u postavkama (`config --set player_names.warthunder-webmap=<your name>`), pa retci feeda o igraču postaju ubojstva i smrti; bez toga se bilježe kao feed ubojstava.

Izvori: stranica same igre na <http://127.0.0.1:8111> i njezin JSON; činjenice o poljima kako ih dokumentira projekt JoyPro 2 (docs/telemetry-recording.md; GPL, korišteno samo za činjenice).

## Pozicije i osi {#positions-and-axes}

| | |
|---|---|
| Pozicije se bilježe | da |
| Os prema gore | `y` |
| Jedinice | metri (istok/sjever na karti; visina samo za vlastiti zrakoplov) |
| Zrcaljeno za preglednik | `z` |
| Mjerilo jedinice (`scale`: preglednik pozicije množi njime) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima pozicije, u podnožje `heat.parquet`, pa 3DHeat preglednik sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igra na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `gsi`: čita samo ono što igra ili platforma daje (game-state integration ili lokalni API koji igra poslužuje), pa bilježi i u igri na mreži i izvan nje; zastavica odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri `memory` čitaju memoriju, i nikad za igru označenu kao igra na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Statistika koja se bilježi {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ za svaki tim). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih imena statistike igre nisu na ovom popisu; navedeni su u odjeljku "Što se bilježi" gore.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača 3DHeata](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cjelovito u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje koje je sačuvano po imenu; `used` označava što je postalo i retkom), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- /map_info.json: obuhvat karte i mreža (metri, ID karte) u meta.json; neispravan prekida bitku
- /map_obj.json (dvaput u sekundi): vlastito vozilo, drugi zrakoplovi i kopnene jedinice (praćeni ID-ovi, strana iz boje, ikona, smjer, boja) i aerodromi, zone i baze kao redovi
- /state (dvaput u sekundi, u zrakoplovu): visina, TAS, IAS, Mach i Vy na vlastitim redovima
- /indicators (svake 2 s): vojska i tip vozila
- /hudmsg (jednom u sekundi): retci feeda ubojstava i šteta kao ubojstva, smrti, pogodci i redovi feeda; ostali HUD događaji kao redovi

**Čuva se u izvornom obliku**

- svaki odgovor cjelovit, `text` je JSON kako ga je igra poslala, pod svojom krajnjom točkom: `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission`; `map_img` bajtovi slike karte kao `payload`, jednom po bitki
- što drži samo sirova pomoćna datoteka: svako polje /state-a osim pet pročitanih (AoA, AoS, Ny, Wx, gas, okretaji, gorivo, ...; skup se razlikuje od zrakoplova do zrakoplova), svako polje /indicators-a (instrumenti kabine zrakoplova, brzina, mjenjač, posada i stabilizator tenkova), ostali ključevi objekata na karti (color[], blink, icon_bg, krajevi aerodroma), `sender`, `enemy` i `mode` iz hudmsg-a, chat (/gamechat, jednom u sekundi), ciljevi bitke i njihov status (/mission.json, svakih 10 s u bitci), retci rečeni prije nego je watcher počeo
- između bitaka (hangar, učitavanje) odgovori idu u vlastitu sesiju, označenu `between_battles` u meta.json, koja nema redove

**Nije dostupno**

- imena, ID-ovi i visine vozila drugih igrača: web karta ih nema (ID-ovi se ovdje daju praćenjem objekata od očitanja do očitanja); feed ubojstava imenuje igrače bez pozicija
- sve izvan web karte: replayi igre čita pretvarač replaya War Thundera, a memorija igre nikad se ne čita (igra na mreži)
- /map_obj.json brže od dva puta u sekundi: brzina očitavanja drži se niskom da se vlastiti web poslužitelj igre ne opterećuje

**Veličina**: oko 50-120 MB na sat JSON-a prije zstd u bitci (map_obj 5-15 KB dvaput u sekundi, state oko 1.5 KB dvaput u sekundi, indicators svake 2 s, chat i HUD retci mali) plus slika karte jednom po bitki (ispod 2 MB); 1-2 MB na sat između bitaka (izgled karte dvaput u sekundi, HUD i chat jednom, svaki kratak odgovor); zstd smanji ponovljeni JSON više od deset puta

## Provjereno {#verified}

testirano na lažnom lokalnom poslužitelju koji poslužuje odgovore u formatu web karte igre; nije testirano na pokrenutoj igri

## Izvor {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
