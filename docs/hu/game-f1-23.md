---
title: "EA SPORTS F1 23 (élő adatok)"
nav_order: 14
lang: "hu"
source: game-f1-23.md
source_hash: "d7b523188e51"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 23 (élő adatok) {#ea-sports-f1-23-live-data}

Miközben az EA SPORTS F1 23-at játszod, a watcher elmenti azokat az adatokat, amelyeket maga a játék küld ki, így később a 3DHeat megtekintőben egy térképen is megnézheted őket.

*Technikai részletek: adapter `f1-23`, típus [`telemetry`](sources-and-rules.md); a `F1_23.exe` futása alatt fut, és 0,1 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- minden autó pozícióját (világ XYZ, m) 10 Hz-cel, pilótanév szerint, csapattal, a saját autó megjelölve (`own_car` 1, a játékos autóindexéből), sebességgel, fokozattal, gázzal, fékkel, kormányzással, fordulatszámmal, DRS-sel, yaw-, pitch- és roll-értékekkel (fok) és g-erőkkel
- autónként a köridők és a versenyhelyezés; a célba érések és a feladások
- a játék verseny-eseményei: a szakasz kezdete és vége, leggyorsabb kör, büntetések, előzések, ütközések, biztonsági autó, piros zászló, rajtlámpák, kockás zászló, győztes, visszatekerések (`teleport`, ahol az autó volt, `spawn`, ahová visszament)
- minden szakasz pályája, típusa, köreinek száma és pilótái
- a saját körök, legjobb kör, verseny- és rajthelyzet, boxkiállások, büntetések, előzések, ütközések, megtett táv, legnagyobb sebesség
- minden csomag, amelyet a játék küld, egészben a `heat.raw.parquet`-ban – a sorokba nem olvasottak is

## Honnan jön {#where-it-comes-from}

UDP-telemetria 127.0.0.1:20777 (Documents\My Games\F1 23\hardwaresettings\hardware_settings_config.xml)

## Hogyan kapcsolható be {#how-to-switch-it-on}

A játékban: Settings > Telemetry Settings > UDP Telemetry On, IP 127.0.0.1, port 20777 – vagy `python -m heat3d_watch setup f1-23 --apply` (szerkeszti a hardware_settings_config.xml fájlt, előbb mentést készít; a játéknak zárva kell lennie). Ha egy másik alkalmazás tartja a 20777-es portot, a watcher átengedi neki

Írd be a parancsot a watcher mappájában megnyitott terminálba (lásd [Mielőtt elkezded](before-you-start.md)). Ha nem sikerül, az utolsó sor megmondja, miért; a [Telepítés és futtatás](installing-and-running.md) a szokásos okokat sorolja fel.

A `python -m heat3d_watch setup f1-23` felsorolja, mely fájlokat változtatná meg; a `python -m heat3d_watch setup f1-23 --apply` meg is változtatja őket, az eredetit `<file>.heat3d-backup` néven megtartva (lásd [Parancsok](commands.md#setup)). Minden változásnál `f1-23: changed: ...` sort ír ki, vagy `f1-23: nothing to change`-et, ha már be van kapcsolva.

## Hogyan működik {#how-it-works}

EA SPORTS F1 23, F1 24 és F1 25: a hivatalos UDP-telemetria, minden pálya-autó.

A játékok maguk küldik (Settings > Telemetry Settings, vagy a `Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml` fájlban `<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`). Little-endian, tömörítetlen, minden csomagon 29 bájtos fejléc (ugyanaz a 2023, 2024 és 2025 formátumban):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Amit beolvasunk, csomagazonosító szerint:

```text
0 Motion        CarMotionData[22], 60 bytes each: world position x y z
                (metres; Y is up), world velocity, forward and right
                vectors (int16 / 32767), g-forces, yaw pitch roll
1 Session       weather, temperatures, total laps, track length, session
                type, track id, ... network game
2 Lap Data      LapData[22]: last lap time, lap distance, race position,
                current lap number, pit stops, penalties, grid position,
                driver and result status. 50 bytes per car in 2023; 57 in
                2024 and 2025, which added the minutes parts of the deltas
                and the speed trap.
3 Event         a four-letter code and a union of details: SSTA SEND FTLP
                RTMT DRSE DRSD TMPT CHQF RCWN PENA SPTP STLG LGOT DTSV SGSV
                FLBK BUTN RDFL OVTK SCAR COLL
4 Participants  ParticipantData[22]: AI or human, driver, team, race
                number, name (48 bytes in 2023 and 2024, 32 in 2025; 58,
                60 and 57 bytes per car)
6 Car Telemetry CarTelemetryData[22], 60 bytes: speed km/h, throttle,
                steer, brake, clutch, gear, rpm, DRS ...
```

Minden csomag egészben, ahogy érkezett, megmarad a szakasz nyers kísérőfájljában (`heat.raw.parquet`, `type` a csomag neve – `motion`, `car_status` ... –, a `format`, `packet_id`, `frame` és `session_uid` mezőkkel) – a fent olvasottak és azok is, amelyeket még semmi nem olvas: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time Trial, 15 Lap Positions, bármely későbbi azonosító, és a fel nem ismert formátumú csomagok. Így egy későbbi dekóder csak a kísérőfájlt igényli.

Minden autó pozíciója a Motion csomagban van – online is, ahol a játék maga kiadja (csak az üzemanyag, az ERS, a sérülés és a gumikészlet adatai vannak visszatartva azoknál a játékosoknál, akiknél a "Your Telemetry" korlátozott). Minden autót nagyjából 10 Hz-cel rögzítünk a pilótanevük alatt ("car N", amíg a nevek meg nem érkeznek), a csapatot névvel, a játékos saját autóját pedig `own` jelöléssel.

Források: az EA "F1 25 UDP Specification" (forums.ea.com, F1 games info hub), az F1 23 és F1 24 specifikációi; ugyanezek a táblázatok a MacManley/f1-25-udp (MIT) projektben. A tesztek ezekből a kiosztásokból épített csomagokat használnak.

Ugyanez a modul szolgálja ki ezeket is: [EA SPORTS F1 24 (élő adatok)](game-f1-24.md), [EA SPORTS F1 25 (élő adatok)](game-f1-25.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Pozíciók rögzítve | igen |
| Felfelé mutató tengely | `y` |
| Mértékegység | méter |
| Tükrözve a megtekintőnek | nincs |
| Mértékegység-szorzó (`scale`: a megtekintő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json`-jába (`axes`), és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe is, így a 3DHeat megtekintő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos {#multiplayer}

- Online játszottként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így mutatja: "allowed (reads only what the game publishes)", vagyis engedélyezett, csak azt olvassa, amit a játék közzétesz.
- `telemetry` típus: csak azt olvassa, amit a játék vagy a platform kiad (egy UDP-port vagy megosztott memória, amelyet a játék közzétesz), így online játékban is rögzít, nemcsak offline; a jelző csak azt dönti el, szabad-e valaha memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amelyet online játszottként jelöltek meg – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Statisztikakulcsok, amelyeket ennek az adapternek a kódja név szerint állít be (minden munkamenet `stats`-ja a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

A kapcsos zárójeles kulcsot futásidőben egészítjük ki (`score.{team}` csapatonként egy kulcs). A kód által a játék mezőinek táblájából vagy a játék saját statisztikanevéből vett kulcsok nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher a 3DHeat [átalakítási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) követi: amit a forrás tartalmaz, azt beolvassuk vagy megtartjuk, soha nem dobjuk el. A sorokon kívül minden csomagot, oldalt, sort vagy választ, amelyet az adapter kap, egészben megőrzünk a munkamenet `heat.raw.parquet`-jában (oszlopok: `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelzi, amiből sor is lett). A `meta.json` `selfCheck.completeness` része minden `type`-ot megszámol; a `lost` 0.

**Beolvasva**

- 0 Motion: minden autó világpozíciója és sebessége, és most már a yaw, pitch, roll (fok, a specifikáció radiánjaiból) és az oldirányú, hosszanti és függőleges g-erő is, minden autó pozíciósorán
- 1 Session: pálya, szakasz típusa, körök száma, pályahossz, online vagy nem (a meta.json `sessions`-ében)
- 2 Lap Data: utolsó köridő, körszám, verseny- és rajthelyzet, boxkiállások, büntetések, eredményállapot (körök, célba érések, feladások, statisztikák)
- 3 Event: minden kód a BUTN kivételével, külön sorként, a részleteivel
- 4 Participants: pilótanevek, csapatok, az aktív autók száma (a sorok `player` és `team` mezői, a meta.json `drivers`)
- 6 Car Telemetry: sebesség, fokozat, gáz, fék, és most már a kormányzás (-1..1), fordulatszám és DRS is, minden autó pozíciósorán
- ellenőrizve az EA közzétett UDP-specifikációi ellen a 2023, 2024 és 2025 formátumhoz (a csomagméretek a tesztekben rögzítve); a játékon még nincs ellenőrizve

**Nyersen megtartva**

- minden csomag egészben a `heat.raw.parquet`-ban, `payload` a datagram, `type` az azonosítója neve: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` egy olyan azonosítóra, amelyet a specifikációk még nem sorolnak fel); oszlopok: `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- a `used` igaz a fent olvasott csomagokra (Motion, Session, Lap Data, Participants, Car Telemetry, és a BUTN-tól eltérő Event-kódok); a többi – autóbeállítások, autóállapot (üzemanyag, ERS, gumi vegyülete és kora, jelzők), végső eredmény, lobbi, autósérülés, szakasztörténet (minden autó minden köre és szektora), gumikészletek, motion ex (a saját autó felfüggesztése, kerékfordulatszámai, helyi sebessége, szögsebessége és gyorsulása), időmérő, versenypozíciók, BUTN gombesemények – későbbi dekóderre várnak
- `format <year>`: 2023 előtti formátumú csomag (más fejlécszerkezet), egészben; `short`: a 29 bájtos fejlécnél rövidebb datagram, egészben

**Nem elérhető**

- más pilóták üzemanyaga, ERS-e, sérülése és gumikészletei online, ha a "Your Telemetry" korlátozott: a játék nullákat küld nekik
- a watcher nem futása idején küldött csomagok, vagy amikor egy másik alkalmazás tartja a 20777-es portot: az UDP-t a játék nem tárolja

**Méret**: 60 Hz-es küldési sebességnél minden csomag körülbelül 0,38 MB/s (a Motion, Lap Data, Car Telemetry, Car Status és Motion Ex 60 Hz-cel, a Session History és Tyre Sets 20/s-mal, a Car Damage 10/s-mal, a Session és Car Setups 2/s-mal), plusz körülbelül 0,03 MB/s elemfejléc: vezetés óránként nagyjából 1,5 GB tömörítés előtt, az alapértelmezett 20 Hz-nél körülbelül 0,55 GB; a zstd ennek töredékére csökkenti (az üres autóhelyek és az ismétlődő értékek jól tömörülnek; valódi szakaszon még nincs mérve)

## Ellenőrizve {#verified}

Csomagokon tesztelve a 2023, 2024 és 2025 formátumban, az EA közzétett specifikációjából építve, UDP-n küldve; a játékon nincs tesztelve.

## Forrás {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
