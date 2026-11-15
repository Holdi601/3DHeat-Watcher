---
title: "IL-2 Sturmovik: Great Battles (felvételek)"
nav_order: 27
lang: "hu"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (felvételek) {#il-2-sturmovik-great-battles-replays}

Egy IL-2 Sturmovik: Great Battles-meccs után a watcher a játék által mentett felvételt olyan fájlokká alakítja, amelyeket térképen megnézhetsz a 3DHeat megjelenítőben.

*Műszaki részletek: adapter `il2-tacview`, típus [`replay`](sources-and-rules.md); mindig fut (nem vár a játék indulására), és 5 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- minden repülőgép, jármű és hajó a felvételen: pozíciók másodpercenként egyszer (méter kelet/fel/észak a felvétel referenciapontjától; a szélesség/hosszúság/magasság oszlopokként)
- megjelenések, megsemmisülések (halál) és elhagyások (left), felszállások és leszállások, ha a felvétel tartalmazza
- objektumok, megsemmisítések, felszállások, leszállások és a felvétel hossza
- a felvétel minden sora egészben a heat.raw.parquet fájlban, a sorok idején

## Honnan származik {#where-it-comes-from}

a játék saját Tacview-felvételei: &lt;játék>\data\Tracks\\\*.acmi (ACMI 2.x szöveg, sima vagy tömörített)

## Hogyan kapcsold be {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 a [KEY = track_record] szakaszban)

Írd be a parancsot a watcher mappájában megnyitott terminálba (lásd [Mielőtt elkezdenéd](before-you-start.md)). Ha nem sikerül, az utolsó sor megmondja, miért; a [Telepítés és futtatás](installing-and-running.md) a szokásos okokat ismerteti.

`python -m heat3d_watch setup il2-tacview` felsorolja, mely fájlokat módosítaná; `python -m heat3d_watch setup il2-tacview --apply` módosítja őket, az eredetit `<file>.heat3d-backup` néven megtartva (lásd [Parancsok](commands.md#setup)). Minden módosításról kiírja az `il2-tacview: changed: ...` sort, vagy az `il2-tacview: nothing to change` sort, ha már be van kapcsolva.

## Hogyan működik {#how-it-works}

IL-2 Sturmovik: Great Battles – a játék telemetria-UDP kimenete és saját Tacview-felvételei.

1. Telemetria ("Telemetry output of IL2 v4.003", 1.2-es változat, a `<game>\Doc\UDP_Output\Il2_TeleOutput.pdf` fájlban). A `<game>\data\startup.cfg` fájl `[KEY = telemetrydevice]` szakaszában kapcsolódik be: `addr`, `addr1`, ... = "IP[:port]" (több célpont egyszerre), `decimation` (50 Hz / n), `enable`, `port`. A `setup` egy célpontot ad hozzá, 127.0.0.1:41995-öt (a JoyPro a 41994-et használja, a játék alapértelmezettje a 4322), és bekapcsolja a kimenetet. A csomagok, kis-endian formátumban:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Jelzők: 0 ENG_RPM, 1 ENG_MP, 2/3 motorrázkódás, 4 LGEARS_STATE, 5 LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz, a gravitációval együtt), 9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14 VERTICAL_SPEED (m/s). Események (2 bájtos csomagolással): 0 SET_FOCUS (STRING: hosszbájt + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass, float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float pos[3]}, 4 DROP_BOMB és 5 ROCKET_LAUNCH {float pos[3], float mass, WORD flags}, 6 HIT és 7 DAMAGE {float pos[3], float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short coalition}. Az eseményhelyzetek a játékos repülőgépéhez képest helyiek; a folyamban egyáltalán nincs világpozíció – ezért ezek események és számok, nem pálya.

2. Tacview-felvétel: a `tacviewrecord = 1` a `[KEY = track_record]` szakaszban arra készteti a játékot, hogy `<game>\data\Tracks\*.acmi` fájlokat írjon (többjátékos módban a szerver dönt). Egy kész fájl átalakításra kerül: minden repülőgép, jármű és hajó a pozícióival, megjelenésével és eltűnésével (megsemmisülve vagy elhagyva), felszállásaival és leszállásaival, ha a felvétel tartalmazza. ACMI 2.x szöveges formátum, sima vagy tömörített, a <https://www.tacview.net/documentation/acmi/en/> leírása szerint – a "#t" sorok mozgatják az órát, a "id,Key=Value,..." sorok tulajdonságokat állítanak be (hex azonosítók, a vesszők escapelve "\\,", a sor végi "\\" a sort folytatja), a "-id" eltávolít egy objektumot, a 0-s objektum tartalmazza a globálisokat (ReferenceLongitude/Latitude, RecordingTime, ...) és az eseményeket ("Event=Destroyed\|id\|text"). T = Lon\|Lat\|Alt[\|U\|V] vagy Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], a hosszúság és szélesség a referenciához képest, az üres mezők változatlanok. A pozíciók egy lapos térképbe kerülnek a referenciapont körül: x kelet, y magasság, z észak, méter. A referenciapont a munkamenet `geo` mezője, a `meta.json`-ban és a tábla láblécében van, így a megjelenítő a valódi világot ki tudja rakni a pályák alá.

Ugyanez a modul szolgálja ki még: [IL-2 Sturmovik: Great Battles (élő adatok)](game-il2.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Rögzített pozíciók | igen |
| Felfelé mutató tengely | `y` |
| Mértékegység | méter (kelet, magasság, észak az első rögzítéstől) |
| Tükrözés a megjelenítőnek | `z` |
| Mértékskála (`scale`: a megjelenítő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json` fájljának `axes` mezőjébe, és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe, így a 3DHeat megjelenítő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos mód {#multiplayer}

- Online játékként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így jeleníti meg: "engedélyezett (csak azt olvassa, amit a játék közzétesz)".
- Típus `replay`: csak azt olvassa, amit a játék vagy a platform kiad (a játék által mentett visszajátszásokat és demókat), ezért online játék közben is rögzít, nem csak offline; a jelző csak azt dönti el, szabad-e egyáltalán memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amely online játékként van jelölve – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Ennek az adapternek a kódja névről név beállított statisztikakulcsai (minden munkamenet `stats` mezője a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

A kapcsos zárójelben lévő kulcsot futásidőben töltik ki (`score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevéből vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertálási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megtartja, soha nem dobja el. A sorokon kívül minden csomagot, lapot, sort vagy választ, amelyet az adapter kap, egészben megtart a munkamenet `heat.raw.parquet` fájljában (oszlopai `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), a `meta.json` `selfCheck.completeness` adatai pedig minden `type`-ot számolnak – a `lost` értéke 0.

**Beolvasva**

- minden objektum T-je (hosszúság, szélesség, magasság, roll, pitch, yaw, U, V, heading) pozícióként, objektumonként másodpercenként egyszer, a Name, Type, Pilot, Coalition/Color, Country, Group és Parent mezőkkel
- megjelenések, eltávolítások (halál, ha előbb jött egy Destroyed esemény, egyébként left), TakenOff és Landed események, Message és Bookmark események sorokként
- a globálisok ReferenceLongitude/Latitude (a térkép kezdőpontja), RecordingTime/ReferenceTime (mikor), DataSource, DataRecorder és Title a meta.json-ba

**Nyers formában megtartva**

- minden nem üres logikai sor egészben `text`-ként (a visszafelé mutató perjellel folytatott sort összefűzve, ahogy az ACMI olvassa), a típusa szerint: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` és `event` (0-s objektum), `object` (id,Key=Value,...)
- amit csak a nyers melléklet tartalmaz: a másodpercenkénti sorok közötti pozíciók, fegyverek, lövedékek, fáklyák, csalétkek és más objektumok, amelyek nem pályaként vannak rajzolva, minden más tulajdonság (telemetria, mint az IAS, AOA, gáz, üzemanyag, ahol a felvétel tartalmazza), a többi globális (Comments, Briefing, Author, Category), a beolvasottakon kívüli események (Timeout, LeftArea, ...)

**Nem elérhető**

- semmi, ami a felvételben nincs; amit a játék nem ír a felvételeibe, az nincs bennük

**Méret**: nagyjából a felvétel saját szövege plusz soronként körülbelül 70 bájt, tömörítés (zstd) előtt: egy 100 MB-os felvételből körülbelül 150–250 MB nyers adat lesz, amelyet a zstd közel a tömörített felvétel méretére hoz vissza

## Ellenőrizve {#verified}

szintetikus ACMI 2.2 fájlokon tesztelve (szöveges és tömörített); a játék egy felvételén még nem tesztelve

## Forrás {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
