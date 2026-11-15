---
title: "DCS World (élő adatok)"
nav_order: 10
lang: "hu"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (élő adatok) {#dcs-world-live-data}

Miközben a DCS World-öt játszod, a watcher elmenti azokat az adatokat, amelyeket maga a játék kiküld, így később a 3DHeat megtekintőben egy térképen is megnézheted őket.

*Technikai részletek: adapter `dcs`, típus [`telemetry`](sources-and-rules.md); a `DCS.exe` futása alatt fut, és 0,1 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- a saját pozíció 10 Hz-cel, méterben kelet/magasság/észak irányban a hadszíntér kezdőpontjához képest (szélességi/hosszúsági/magassági adatokból); a szélesség, hosszúság és magasság oszlopokként, valamint a DCS saját világ-méterei (dcs_x észak, dcs_y fel, dcs_z kelet)
- hozzáállás, műszerelt és valódi légsebesség, Mach, emelkedési/süllyedési sebesség, támadási szög és oldalcsúszás, mágneses irány, AGL és radarmagasság, g három tengelyen, sebesség és forgási sebességek, levegőben van-e, a kamera pozíciója és előre mutató vektora, a gép típusa
- felszállások és leszállások a repülőtérrel; lezuhanások, katapultálások, pilótahalálok
- ölések és lelövések mindkét egységtípussal és a fegyverrel; más játékesemények, ahogy érkeznek
- küldetésenként az életek (spawn ... session_end), ölések, halálok, megtett távolság, legmagasabb pont, legnagyobb g
- minden sor, amelyet a hook küld, egészben a heat.raw.parquet-ben, egy másodpercenként kiírt táblázattal a gép exporttáblázatairól (motorok, futómű és lapok, rakomány, ellenintézkedések, útvonal, navigáció) és minden más visszahívás (szünet, csevegés, játékosok csatlakozása, küldetés betöltése)

## Honnan jön {#where-it-comes-from}

a watcher hookja %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, UDP-sorok a 127.0.0.1:41993 címre

## Hogyan kapcsolható be {#how-to-switch-it-on}

`python -m heat3d_watch setup dcs --apply` (hozzáadja a Scripts\Hooks\heat3d-watch.lua fájlt), majd indítsd újra a DCS-t

Írd be a parancsot a watcher mappájában megnyitott terminálba (lásd [Mielőtt elkezded](before-you-start.md)). Ha nem sikerül, az utolsó sor megmondja, miért; a [Telepítés és futtatás](installing-and-running.md) a szokásos okokat sorolja fel.

A `python -m heat3d_watch setup dcs` felsorolja, mely fájlokat változtatná meg; a `python -m heat3d_watch setup dcs --apply` meg is változtatja őket, az eredetit `<file>.heat3d-backup` néven megtartva (lásd [Parancsok](commands.md#setup)). Minden változásnál `dcs: changed: ...` sort ír ki, vagy `dcs: nothing to change`-et, ha már be van kapcsolva.

## Hogyan működik {#how-it-works}

DCS World: a watcher saját kis hook-szkriptje, amely UDP-sorokat küld a 127.0.0.1:41993 címre.

A DCS induláskor lefuttatja a `Saved Games\DCS*\Scripts\Hooks\` mappában lévő Lua-fájlokat; egy hook olvashatja az exportfüggvényeket (`Export.Lo*`), és megkapja a szimuláció visszahívásait (`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) – lásd `<DCS>\API\DCS_ControlAPI.html` és <https://wiki.hoggitworld.com/view/DCS_Export_Script>. A `setup` a `heat3d-watch.lua` fájlt írja oda (saját fájlja: az Export.lua és más eszközök hookjai nem változnak). Ez másodpercenként tíz sort küld, és másodpercenként még egyet, valamint minden játékeseményre vagy visszahívásra egyet, soha nem várva választ. A port 41993, hogy a JoyPro hookja (41992) és a Tacview (42674) mellette is működjön. A sorok (a mezőket ';' választja el):

```text
hello;v=2                                       the hook was loaded
start;mission=..;map=..;me=<player id>;name=..;mp=0|1;file=..;server=0|1
mis;t=..;date.Day=..;start_time=..;weather...   the mission's date, start time and weather, flattened
p;t=<model s>;x=;y=;z=;lat=;lon=;alt=;hdg=;pitch=;bank=;ias=;agl=;g=;type=;tas=;mach=;vv=;aoa=;aos=;
  mhdg=;ralt=;gx=;gz=;vx=;vy=;vz=;wx=;wy=;wz=;air=;cx=;cy=;cz=;cfx=;cfy=;cfz=
d;t=..;self.Name=..;eng.RPM.left=..;mech.gear.value=..;pay.Stations.1.count=..;...   once a second
ev;t=..;name=<onGameEvent name>;args=a|b|c      every onGameEvent
cb;t=..;name=<callback>;args=a|b                every other callback (pause, chat, players, loading)
noexport;t=..                                   the server forbids ownship export
stop;t=..                                       the mission ended
```

A `p` a LoGetSelfData: a Position x/y/z – a DCS saját világ-méterei, x észak, y fel, z kelet – plus LatLongAlt (fok, m), Heading/Pitch/Bank (radián), a LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) és LoGetAccelerationUnits() x/y/z (g) értékekkel; és, ahogy a `Scripts\Export.lua` leírja: LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s), LoGetAngleOfAttack és LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad), LoGetRadarAltimeter (m), LoGetVectorVelocity (világ m/s), LoGetAngularVelocity (rad/s), LoGetInAir, valamint a LoGetCameraPosition pontja és előre mutató vektora (világ-méter). A `d` a táblák egészének másodpercenkénti kiírása, pontozott kulcsokra lapítva: LoGetSelfData (ország, koalíció, egység- és csoportnevek, típusszintek, jelzők), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus, és néhány szám (szünet, időgyorsítás, ülés, nyomás, eltérések). A watcher minden sort egészben megtart a nyers kísérőfájlban; a `p` a sorokat is adja.

A pozíciók ugyanabba a lapos térképbe kerülnek, mint a más repülőszimulátorok (`Tangent`: x kelet, y tengerszint feletti magasság, z észak, méterben), a LatLongAlt-ből, a hadszíntér rögzített kezdőpontja körül (`THEATRES`, az indulósor `map`-jából), így minden küldetés egy hadszíntéren ugyanazt a térképet használja, és a megtekintő alá lehet fektetni a valódi világot. A táblázatban nem szereplő hadszíntérnél az első mérés szélességi és hosszúsági fokát veszi, egész fokra kerekítve. A DCS saját x/y/z értékei `dcs_x`, `dcs_y`, `dcs_z` néven maradnak meg; a LatLongAlt nélküli mérés nem helyezhető el, csak számolódik (`fixes_without_latlon`). A kezdőpont a munkamenet `geo` adata, a meta.json-ban és a tábla láblécében.

Az onGameEvent argumentumai, ahogy a DCS_ControlAPI adja őket: takeoff/landing (playerID, unit_missionID, airdromeName), crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID, killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide, weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide), mission_end (winner, msg).

Egy többjátékos szerver megtilthatja a saját gép adatainak exportját (LoIsOwnshipExportAllowed hamis); akkor nincsenek pozíciók, csak események, és a munkamenet ezt jelzi.

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Pozíciók rögzítve | igen |
| Felfelé mutató tengely | `y` |
| Mértékegység | méter (kelet, magasság, észak a hadszíntér kezdőpontjától) |
| Tükrözve a megtekintőnek | `z` |
| Mértékegység-szorzó (`scale`: a megtekintő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json`-jába (`axes`), és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe is, így a 3DHeat megtekintő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos {#multiplayer}

- Online játszottként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így mutatja: "allowed (reads only what the game publishes)", vagyis engedélyezett, csak azt olvassa, amit a játék közzétesz.
- `telemetry` típus: csak azt olvassa, amit a játék vagy a platform kiad (egy UDP-port vagy megosztott memória, amelyet a játék közzétesz), így online játékban is rögzít, nemcsak offline; a jelző csak azt dönti el, szabad-e valaha memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amelyet online játszottként jelöltek meg – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Statisztikakulcsok, amelyeket ennek az adapternek a kódja név szerint állít be (minden munkamenet `stats`-ja a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

A kapcsos zárójeles kulcsot futásidőben egészítjük ki (`score.{team}` csapatonként egy kulcs). A kód által a játék mezőinek táblájából vagy a játék saját statisztikanevéből vett kulcsok nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher a 3DHeat [átalakítási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) követi: amit a forrás tartalmaz, azt beolvassuk vagy megtartjuk, soha nem dobjuk el. A sorokon kívül minden csomagot, oldalt, sort vagy választ, amelyet az adapter kap, egészben megőrzünk a munkamenet `heat.raw.parquet`-jában (oszlopok: `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelzi, amiből sor is lett). A `meta.json` `selfCheck.completeness` része minden `type`-ot megszámol; a `lost` 0.

**Beolvasva**

- `p` (10 Hz): pozíció, LatLongAlt, hozzáállás, IAS, AGL, g (x/y/z), a gép típusa, és a 2-es hook TAS, Mach, emelkedési sebesség, AoA, oldalcsúszás, mágneses irány, radarmagasság, világsebesség, forgási sebességek, levegőben van-e, valamint a kamera pont- és előre vektora – mind sor-oszlopként (a mértékegységek ahogy az Export.lua adja)
- `start`: küldetés, hadszíntér, saját játékos-azonosító és név, többjátékos, küldetésfájl, szerver; `mis`: a küldetés dátuma és kezdési ideje a meta.json-ba
- `ev`: minden onGameEvent sorként (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, és minden más név, ahogy érkezik)
- `noexport` és `stop` sorként és a meta.json-ban

**Nyersen megtartva**

- minden sor, amelyet a hook küld, egészben, `text`-ként a fajtája alatt: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; más fajtájú sor `unknown` alatt
- `d` (másodpercenként, csak nyersen): LoGetSelfData egészben (ország, koalíció, egység- és csoportnév, típusszintek, jelzők), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, a szélvektor, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, rádióbóják, szünet, időgyorsítás, ülés, nyomás, eltérések – pontozott kulcsokra lapítva
- `mis`: a küldetés időjárási táblázata, lapítva; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage az argumentumaikkal

**Nem elérhető**

- más egységek (LoGetWorldObjects, LoGetObjectById) és érzékelőadatok (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): nincsenek kérve – a küldetés minden objektuma 10 Hz-cel költséges a DCS saját keretén belül, és a szerver korlátozza őket (allow_object_export, allow_sensor_export); a Tacview rögzíti őket
- a teljes küldetés-táblázat (a DCS.getCurrentMission minden egységet és triggert tartalmaz, megabájtokban): csak a dátuma, a kezdési ideje, az időjárása, a bevetése, a hadszíntere és a verziója megy ki
- az onPlayerTry\* visszahívások: válaszolnak a DCS-nek (engedélyeznek vagy elutasítanak), ezért a hook nem nyúl hozzájuk
- más játékosok címei és UCID-jei: a net.get_player_info csak szervernek adja ki őket, és nem a játékos tulajdonai
- egy táblázat bejegyzései 800 kulcs után vagy 6 szintnél mélyebben egy `d` sorban levágódnak, hogy egy sor egy datagram maradjon

**Méret**: körülbelül 20 MB óránként a `p` sorokból (másodpercenként 10, soronként kb. 500 bájt a keretével), és 15–40 MB a `d` kiírásokból (másodpercenként egy, 4–10 KB a géptől, a rakománytól és az útvonaltól függően), a zstd előtt; az ismétlődő kulcsok tízszeresen tömörülnek

## Ellenőrizve {#verified}

A sorformátum szintetikus datagramokkal tesztelve; a Lua-hook a DCS-en belül nincs tesztelve (a DCS hook/export API-jából és a Scripts\Export.lua Lo\* függvénylistájából írva, nem futtatva)

## Forrás {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
