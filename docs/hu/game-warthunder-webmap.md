---
title: "War Thunder (játékállapot)"
nav_order: 47
lang: "hu"
source: game-warthunder-webmap.md
source_hash: "d6026c277030"
nav_exclude: true
search_exclude: true
---
# War Thunder (játékállapot) {#war-thunder-game-state}

Miközben a War Thunder-t játszod, a watcher elmenti, amit a játék a saját számítógépeden futó programoknak jelent, így később a 3DHeat megtekintőben egy térképen is megnézheted.

*Technikai részletek: adapter `warthunder-webmap`, típus [`gsi`](sources-and-rules.md); a `aces.exe` futása alatt fut, és 0,5 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- a saját pozíció (térkép kelet/észak irányban, méterben; magasság a /state-ből repülőgépben, egyébként 0), kétszer másodpercenként, irány, sebesség
- megjelenések és az, amikor a saját jármű elhagyja a térképet (megsemmisült, leszállt, vissza a hangárba), bevetésenként egy
- más repülőgépek és földi egységek a kistérképen, követett azonosítókkal és oldallal (magasság nélkül)
- repülőterek, elfoglalható zónák és bázisok egyszer, és a zónák oldalváltása
- a harc-hírfolyam sorai (ki, jármű, ige); a játékos ölései és halálai, ha a neved be van állítva (`config --set player_names.warthunder-webmap=<name>`)
- megjelenések, megtett táv, legnagyobb magasság, legnagyobb valódi légsebesség, jármű; ölések és halálok, ha a neved be van állítva
- a webes térkép minden válasza egészben a heat.raw.parquet-ban – a teljes /state és /indicators, a csevegés, a csata céljai és a térkép képe is –; a csaták között külön munkamenetben

## Honnan jön {#where-it-comes-from}

a játék helyi webes térképe, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## Hogyan kapcsolható be {#how-to-switch-it-on}

Semmit nem kell bekapcsolni: a watcher azt olvassa a forrásból, ahogy a játék vagy a platform kiadja.

## Hogyan működik {#how-it-works}

War Thunder: a játék saját helyi webes térképe a <http://127.0.0.1:8111> címen.

A játék kiszolgálja azt az oldalt, amelyet második képernyőn vagy telefonon lehet mutatni (a "webes térkép"), és az ehhez tartozó JSON-okat, amíg fut – minden módban, a több játékos módot is beleértve:

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

Minden választ egészben megőriz a munkamenet nyers kísérőfájlja a végpontja alatt (map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img); a csaták között a válaszok saját munkamenetbe kerülnek.

A térképpozíció a kiterjedéssel méterré válik: u = min_x + x \* (max_x - min_x) kelet, v = max_y - y \* (max_y - min_y) észak (a kép y-ja lefelé fut). A sorok x = u, y = magasság (a saját repülőgép "H, m"-je; minden másnál 0), z = v, így az Y felfelé mutat; a z a megtekintőnek tükrözött, hogy az észak ne délre rajzolódjon.

A színek a játékos látása szerint jelölik az oldalakat: a saját sárga (alapértelmezésben #faC81E), a rajtársak zöldek, a szövetségesek kékek (#174DFF), az ellenségek pirosak (#f40C00); a színvakok palettái megváltoztatják őket, ezért az árnyalat dönt, nem a pontos érték. A játék senkit nem nevez meg a térképen, és a tárgyaknak nincsenek azonosítóik: a többi tárgy itt azonosítót kap, úgy, hogy pollról pollra követjük őket (a legközelebbi azonos típusú és ikonú), ami két, egymás közelében elhaladó, azonos típusú gépet felcserélhet. A játékos saját neve sincs meg az API-ban: add meg a beállításokban (`config --set player_names.warthunder-webmap=<your name>`), és a hírfolyam játékossal kapcsolatos sorai ölésekké és halálokká válnak; ha nincs, a hírfolyam sorainak tekintjük őket.

Források: a játék saját oldala a <http://127.0.0.1:8111> címen és a JSON-jai; a mezőkre vonatkozó tények a JoyPro 2 projekt dokumentációjából (docs/telemetry-recording.md; GPL, csak tényekért használva).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Pozíciók rögzítve | igen |
| Felfelé mutató tengely | `y` |
| Mértékegység | méter (térkép kelet/észak; magasság csak a saját repülőgépnél) |
| Tükrözve a megtekintőnek | `z` |
| Mértékegység-szorzó (`scale`: a megtekintő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json`-jába (`axes`), és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe is, így a 3DHeat megtekintő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos {#multiplayer}

- Online játszottként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így mutatja: "allowed (reads only what the game publishes)", vagyis engedélyezett, csak azt olvassa, amit a játék közzétesz.
- `gsi` típus: csak azt olvassa, amit a játék vagy a platform kiad (game-state integration vagy helyi API, amelyet a játék a játékos gépének szolgáltat), így online játékban is rögzít, nemcsak offline; a jelző csak azt dönti el, szabad-e valaha memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amelyet online játszottként jelöltek meg – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Statisztikakulcsok, amelyeket ennek az adapternek a kódja név szerint állít be (minden munkamenet `stats`-ja a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

A kapcsos zárójeles kulcsot futásidőben egészítjük ki (`score.{team}` csapatonként egy kulcs). A kód által a játék mezőinek táblájából vagy a játék saját statisztikanevéből vett kulcsok nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher a 3DHeat [átalakítási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) követi: amit a forrás tartalmaz, azt beolvassuk vagy megtartjuk, soha nem dobjuk el. A sorokon kívül minden csomagot, oldalt, sort vagy választ, amelyet az adapter kap, egészben megőrzünk a munkamenet `heat.raw.parquet`-jában (oszlopok: `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelzi, amiből sor is lett). A `meta.json` `selfCheck.completeness` része minden `type`-ot megszámol; a `lost` 0.

**Beolvasva**

- /map_info.json: a térkép kiterjedése és rácsa (méter, a térkép azonosítója) a meta.json-ba; egy érvénytelen véget vet a csatának
- /map_obj.json (másodpercenként kétszer): a saját jármű, más repülőgépek és földi egységek (követett azonosítók, oldal a színből, ikon, irány, szín), valamint a repülőterek, zónák és bázisok sorokként
- /state (másodpercenként kétszer, repülőgépben): magasság, TAS, IAS, Mach és Vy a saját sorokon
- /indicators (2 másodpercenként): hadsereg- és járműtípus
- /hudmsg (másodpercenként): a hírfolyam ölés- és sebzéssorai ölésekként, halálokként, találatokként és hírfolyam-sorokként; más HUD-események sorként

**Nyersen megtartva**

- minden válasz egészben, a `text` a JSON úgy, ahogy a játék küldte, a végpontja alatt: `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission`; a `map_img` a térképkép bájtjai `payload`-ként, csatánként egyszer
- csak a nyers kísérőfájl tartalmazza: a /state minden mezője az öt beolvasottön túl (AoA, AoS, Ny, Wx, gázkar, fordulatszám, üzemanyag, ... – egy gép készlete eltér egy másikétól), az /indicators minden mezője (a repülőgépek műszerei, a tankok sebessége, sebessége, legénysége és stabilizátora), a térképobjektumok többi kulcsa (color[], blink, icon_bg, airfield ends), a hudmsg sender, enemy és mode mezői, a csevegés (/gamechat, másodpercenként), a csata céljai és állapotuk (/mission.json, csatában 10 másodpercenként), a watcher indulása előtt mondott sorok
- a csaták között (hangár, betöltés) a válaszok saját munkamenetbe kerülnek, amelyet a meta.json `between_battles` jelöl, és nincsenek sorai

**Nem elérhető**

- más játékosok járműveinek nevei, azonosítói és magassága: a webes térkép nem adja meg (az azonosítókat itt pollról pollra követett tárgyak kapják); a hírfolyam játékosokat nevez meg, pozíció nélkül
- minden, ami a webes térképen kívül van: a játék visszajátszásait a War Thunder visszajátszás-átalakító olvassa, a játék memóriáját pedig soha nem olvassuk (online játék)
- a /map_obj.json másodpercenként kétnél gyakrabban: a lekérdezési gyakoriság alacsony marad, hogy a játék saját webszervere ne terhelődjön

**Méret**: csatában körülbelül 50–120 MB JSON óránként a zstd előtt (a map_obj 5–15 KB másodpercenként kétszer, a state kb. 1,5 KB másodpercenként kétszer, az indicators 2 másodpercenként, a csevegés és a HUD-sorok kicsik), plusz a térképkép csatánként egyszer (2 MB alatt); csaták között óránként 1–2 MB (a térkép nézete másodpercenként kétszer, a HUD és a csevegés egyszer, mindegyik rövid válasz); a zstd az ismétlődő JSON-t tízszeresnél jobban csökkenti

## Ellenőrizve {#verified}

Egy helyettesítő helyi szerveren tesztelve, amely a játék webes térképének formátumában válaszol; a játékon nincs tesztelve.

## Forrás {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
