---
title: "War Thunder (stanje igre)"
nav_order: 47
lang: "bs"
source: game-warthunder-webmap.md
source_hash: "d6026c277030"
nav_exclude: true
search_exclude: true
---
# War Thunder (stanje igre) {#war-thunder-game-state}

Dok igrate War Thunder, watcher sprema ono što igra javlja programima na vašem vlastitom računaru, da to poslije možete pogledati na mapi u pregledniku 3DHeat.

*Tehnički detalji: adapter `warthunder-webmap`, vrsta [`gsi`](sources-and-rules.md); radi dok radi `aces.exe` i svakih 0,5 s traži nove podatke.*

## Šta se snima {#what-is-recorded}

- vlastita pozicija (mapa istok/sjever u metrima; visina iz /state u letjelici, inače 0) dvaput u sekundi, smjer, brzina
- spawnovi i vlastito vozilo koje napušta mapu (uništeno, sletjelo, nazad u hangar), po jedan sortie za svaki
- druge letjelice i kopnene jedinice na minimapi kao pozicije s praćenim id-ovima i stranom (bez visine)
- aerodromi, zone zauzimanja i baze jednom, i zone koje mijenjaju stranu
- linije kill i damage feeda (ko, vozilo, glagol); igračeva ubistva i smrti kad je postavljeno vaše ime (`config --set player_names.warthunder-webmap=<name>`)
- spawnovi, udaljenost, najveća visina, najveća prava brzina zraka, vozilo; ubistva i smrti kad je postavljeno vaše ime
- svaki odgovor web mape čuva se cijel u heat.raw.parquet - cijeli /state i /indicators, chat, ciljevi bitke i slika mape uključeni; između bitaka u vlastitoj sesiji

## Odakle dolazi {#where-it-comes-from}

lokalna web mapa igre, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## Kako to uključiti {#how-to-switch-it-on}

Ništa ne treba uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

## Kako radi {#how-it-works}

War Thunder: vlastita lokalna web mapa igre na <http://127.0.0.1:8111>.

Igra dok radi služi stranicu koju može prikazati drugi ekran ili telefon ("web mapa"),
i JSON iza nje - u svakom načinu, uključujući multiplayer:

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

Svaki odgovor čuva se cijel u sirovom sidecaru sesije pod svojim endpointom
(map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img);
između bitaka odgovori idu u vlastitu sesiju.

Pozicija na mapi postaje metri preko opsega: u = min_x + x \* (max_x - min_x)
istok, v = max_y - y \* (max_y - min_y) sjever (y slike ide dolje). Redovi su
x = u, y = visina ("H, m" vlastite letjelice; 0 za sve ostalo), z = v, pa je
Y gore; z je zrcaljeno za preglednik da sjever ne bude nacrtan na jugu.

Boje kažu strane onako kako ih igrač vidi: vlastita žuta (#faC81E zadano),
squad zelena, saveznici plava (#174DFF), neprijatelji crvena (#f40C00); palete za daltoniste
ih mijenjaju, pa odlučuje nijansa, a ne tačna vrijednost. Igra na mapi
nikoga ne imenuje i objektima ne daje id-ove: ovdje drugi objekti dobivaju id-ove praćenjem
od poll-a do poll-a (najbliži istog tipa i ikone), što može zamijeniti dvije
letjelice istog tipa koje prolaze blizu. Ni igračevo vlastito ime nije u
API-ju: upišite ga u postavke (`config --set
player_names.warthunder-webmap=<your name>`) i linije kill feeda o
igraču postaju ubistva i smrti; bez toga se bilježe kao kill feed.

Izvori: vlastita stranica igre na <http://127.0.0.1:8111> i njen JSON; činjenice o poljima
kako ih dokumentira projekat JoyPro 2 (docs/telemetry-recording.md; GPL, korišteno samo
radi činjenica).

## Pozicije i ose {#positions-and-axes}

| | |
|---|---|
| Pozicije se snimaju | da |
| Osa gore | `y` |
| Jedinice | metri (mapa istok/sjever; visina samo za vlastitu letjelicu) |
| Zrcaljeno za preglednik | `z` |
| Skala jedinica (`scale`: preglednik njome množi pozicije) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima pozicije, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam rotira i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označeno kao igrano online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dozvoljeno (čita samo ono što igra objavljuje)".
- Vrsta `gsi`: čita samo ono što igra ili platforma daje (game-state integracija ili lokalni API koji igra služi), pa snima i u online igri kao i offline; zastavica odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj adapter je **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i to nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježene statistike {#statistics-recorded}

Ključevi statistika koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

Ključ u vitičastim zagradama dovršava se za vrijeme rada (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz igrinih vlastitih imena statistika nisu na ovoj listi; "Šta se snima" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeatovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor drži čita se ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, zatim svako polje čuvano po imenu; `used` označava šta je postalo i redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- /map_info.json: opseg i mreža mape (metri, id mape) u meta.json; nevažeći završava bitku
- /map_obj.json (dvaput u sekundi): vlastito vozilo, druge letjelice i kopnene jedinice (praćeni id-ovi, strana iz boje, ikona, smjer, boja) te aerodromi, zone i baze kao redovi
- /state (dvaput u sekundi, u letjelici): visina, TAS, IAS, Mach i Vy na vlastitim redovima
- /indicators (svake 2 s): army i tip vozila
- /hudmsg (jednom u sekundi): linije kill i damage feeda kao ubistva, smrti, pogoci i redovi feeda; ostali HUD događaji kao redovi

**Čuva se sirovo**

- svaki odgovor cijel, `text` je JSON onako kako ga je igra poslala, pod svojim endpointom: `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission`; `map_img` bajtovi slike mape kao `payload`, jednom po bici
- ono što drži samo sirovi sidecar: svako polje /state preko pročitanih pet (AoA, AoS, Ny, Wx, gas, RPM, gorivo, ... - set jedne letjelice razlikuje se od druge), svako polje /indicators (instrumenti kokpita letjelica, brzina, stajni trap, posada i stabilizator tenkova), ostali ključevi objekata mape (color[], blink, icon_bg, krajevi aerodroma), sender, enemy i mode iz hudmsg, chat (/gamechat, jednom u sekundi), ciljevi bitke i njihov status (/mission.json, svakih 10 s u bici), linije izgovorene prije nego što je watcher počeo
- između bitaka (hangar, učitavanje) odgovori idu u vlastitu sesiju, označenu `between_battles` u meta.json, koja nema redova

**Nije dostupno**

- imena, id-ovi i visine vozila drugih igrača: web mapa ih nema (id-ovi se ovdje daju praćenjem objekata od poll-a do poll-a); kill feed imenuje igrače bez pozicija
- sve izvan web mape: snimke igre čita konverter snimaka za warthunder, a memorija igre se nikad ne čita (online igra)
- /map_obj.json brže od dvaput u sekundi: učestalost traženja drži se niskom da se vlastiti web server igre ne optereti

**Veličina**: oko 50-120 MB na sat JSON-a prije zstd u bici (map_obj 5-15 KB dvaput u sekundi, state oko 1,5 KB dvaput u sekundi, indicators svake 2 s, chat i HUD linije male) plus slika mape jednom po bici (ispod 2 MB); 1-2 MB na sat između bitaka (izgled mape dvaput u sekundi, HUD i chat jednom, svaki kratak odgovor); zstd ponovljeni JSON smanjuje znatno više od deset puta

## Provjereno {#verified}

testirano prema lažnom lokalnom serveru koji služi odgovore u formatu web mape igre; neprovjereno na igri koja radi

## Izvor {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
