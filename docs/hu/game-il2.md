---
title: "IL-2 Sturmovik: Great Battles (élő adatok)"
nav_order: 26
lang: "hu"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (élő adatok) {#il-2-sturmovik-great-battles-live-data}

Amíg az IL-2 Sturmovik: Great Battles-t játszod, a watcher elmenti azokat az adatokat, amelyeket maga a játék kiküld, így később statisztikaként és idővonalként is megnézheted őket.

*Műszaki részletek: adapter `il2`, típus [`telemetry`](sources-and-rules.md); akkor fut, amikor az `Il-2.exe` vagy az `IL2Series.exe` fut, és 0,1 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- bevetések: a felvett repülőgép (spawn) és az a pillanat, amikor a kimenet leáll (session_end) – nincs világpozíció: a játék nem küld ilyet
- ledobott bombák és kilőtt rakéták (tömeg), találatok és az elszenvedett sérülések, robbanások, géppuskasorozatok – a repülőgéphez képest helyi pozíciókkal
- egyenértékű légsebesség, AGL, függőleges sebesség, g, motorfordulatszám másodpercenként egyszer, a csomag többi jelzőjével együtt (szívónyomás, motorrázkódás, futómű-állapot és -nyomás, AoA, oldalcsúszás, gyorsulás x/y/z, pilótafülke-rázkódás, csűrők, légfékek)
- bevetések, kilőtt lövedékek, bombák, rakéták, elszenvedett találatok, legnagyobb sebesség, legnagyobb g, repülési idő; szerver neve és a pilóta neve online
- minden telemetria-csomag egészben a heat.raw.parquet fájlban

## Honnan származik {#where-it-comes-from}

a játék telemetria-UDP kimenete a 127.0.0.1:41995 címre ([KEY = telemetrydevice] a &lt;játék>\data\startup.cfg fájlban)

## Hogyan kapcsold be {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (hozzáadja: addrN = "127.0.0.1:41995", enable = true), majd indítsd újra az IL-2-t

Írd be a parancsot a watcher mappájában megnyitott terminálba (lásd [Mielőtt elkezdenéd](before-you-start.md)). Ha nem sikerül, az utolsó sor megmondja, miért; a [Telepítés és futtatás](installing-and-running.md) a szokásos okokat ismerteti.

`python -m heat3d_watch setup il2` felsorolja, mely fájlokat módosítaná; `python -m heat3d_watch setup il2 --apply` módosítja őket, az eredetit `<file>.heat3d-backup` néven megtartva (lásd [Parancsok](commands.md#setup)). Minden módosításról kiírja az `il2: changed: ...` sort, vagy az `il2: nothing to change` sort, ha már be van kapcsolva.

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

Ugyanez a modul szolgálja ki még: [IL-2 Sturmovik: Great Battles (felvételek)](game-il2-tacview.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Rögzített pozíciók | nem |
| Felfelé mutató tengely | `y` |
| Mértékegység | nincs: a telemetriának nincsenek világpozíciói |
| Tükrözés a megjelenítőnek | nincs |
| Mértékskála (`scale`: a megjelenítő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json` fájljának `axes` mezőjébe, és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe, így a 3DHeat megjelenítő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos mód {#multiplayer}

- Online játékként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így jeleníti meg: "engedélyezett (csak azt olvassa, amit a játék közzétesz)".
- Típus `telemetry`: csak azt olvassa, amit a játék vagy a platform kiad (egy UDP-port vagy megosztott memória, amelyet a játék közzétesz), ezért online játék közben is rögzít, nem csak offline; a jelző csak azt dönti el, szabad-e egyáltalán memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amely online játékként van jelölve – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Ennek az adapternek a kódja névről név beállított statisztikakulcsai (minden munkamenet `stats` mezője a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

A kapcsos zárójelben lévő kulcsot futásidőben töltik ki (`score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevéből vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertálási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megtartja, soha nem dobja el. A sorokon kívül minden csomagot, lapot, sort vagy választ, amelyet az adapter kap, egészben megtart a munkamenet `heat.raw.parquet` fájljában (oszlopai `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), a `meta.json` `selfCheck.completeness` adatai pedig minden `type`-ot számolnak – a `lost` értéke 0.

**Beolvasva**

- SET_FOCUS (a felvett repülőgép: egy bevetés), DROP_BOMB és ROCKET_LAUNCH (tömeg, helyi pozíció), HIT és DAMAGE (helyi pozíció, erő), EXPLOSION (helyi pozíció, sugár), GUN_FIRE (kilőtt lövedékek lekérdezésenként) sorokként
- SETUP_ENG (index, id, helyi pozíció, legnagyobb fordulatszám), SETUP_GUN (index, helyi pozíció, lövedéktömeg, torkolati sebesség) és SETUP_LGEAR (index, id, helyi pozíció) sorokként: a repülőgép motorjai, fegyverei és futóművei a bevetés kezdetekor
- SRV_TITLE, SRV_ADDR, SRS_ADDR és CLIENT_DAT (pilótanév) a meta.json-ba; a CTRL_DAT koalíciója a bevetés csapataként
- mind a tizenöt jelző a specifikáció szerint a másodpercenkénti `state` soron (egy érték számként, motoronként, futóműlábanként vagy tengelyenként egy lista); a legnagyobb sebesség, g és AGL minden csomagból

**Nyers formában megtartva**

- minden datagram egészben `payload`-ként, a Packet_ID alatt: a telemetria `0x54000101` (akkor használt, ha sort vagy meta.json-bejegyzést készített), bármely más azonosító önmagaként, egy túl rövid datagram, amely nem telemetria, `short` alatt
- amit csak a nyers melléklet tartalmaz: a jelzők a sorok között (a játék 50 Hz / decimation ütemben küldi), egy SETUP-esemény, amely rövidebb a specifikáció elrendezésénél, a specifikáció által fel nem sorolt eseményazonosítók

**Nem elérhető**

- világpozíció: a telemetria-kimenetnek nincs; az események pozíciói a repülőgéphez képest helyiek; az il2-tacview adapter a játék saját Tacview-felvételeiből olvassa a pozíciókat
- más repülőgépek és játékosok: a kimenet csak a játékos saját repülőgépét írja le

**Méret**: setup 10 Hz-es beállításával (decimation 5; egy csomag körülbelül 160 bájt plusz a kerete) óránként körülbelül 8 MB, a játék teljes 50 Hz-es ütemében 40 MB, tömörítés (zstd) előtt; a zstd az ismétlődő floatokat a töredékére zsugorítja

## Ellenőrizve {#verified}

a játék saját Il2_TeleOutput specifikációjából (1.2-es változat) épített csomagokon tesztelve; a startup.cfg módosításai a fájl egy másolatán tesztelve; a futó játékon még nem tesztelve

## Forrás {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
