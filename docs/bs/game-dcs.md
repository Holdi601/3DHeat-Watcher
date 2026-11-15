---
title: "DCS World (podaci uživo)"
nav_order: 10
lang: "bs"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (podaci uživo) {#dcs-world-live-data}

Dok igrate DCS World, watcher sprema podatke koje igra sama šalje, da ih poslije možete pogledati na mapi u pregledniku 3DHeat.

*Tehnički detalji: adapter `dcs`, vrsta [`telemetry`](sources-and-rules.md); radi dok radi `DCS.exe` i svakih 0,1 s traži nove podatke.*

## Šta se snima {#what-is-recorded}

- vlastita pozicija na 10 Hz kao metri istok/gore/sjever od ishodišta teatra (iz geografske širine/dužine/visine); lat/lon/alt i DCS-ovi vlastiti svjetski metri (dcs_x sjever, dcs_y gore, dcs_z istok) kao kolone
- stav, indicirana i prava brzina zraka, Mach, vertikalna brzina, napadni ugao i klizanje, magnetski smjer, AGL i radarska visina, g na tri ose, brzina i stope rotacije, u zraku, pozicija kamere i vektor naprijed, tip letjelice
- polijetanja i slijetanja s aerodromom; rušenja, katapultiranja, smrti pilota
- ubistva i obaranje s oba tipa jedinica i oružjem; ostali događaji igre kako su dati
- životi po misiji (spawn ... session_end), ubistva, smrti, udaljenost, najveća visina, najveći g
- svaka linija koju hook pošalje čuva se cijela u heat.raw.parquet, s jednom u sekundi ispisom izvoznih tabela letjelice (motori, stajni trap i zakrilca, teret, protumjere, ruta, navigacija) i svaki drugi callback (pauza, chat, pridruživanje igrača, učitavanje misije)

## Odakle dolazi {#where-it-comes-from}

watcherov hook %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, UDP linije na 127.0.0.1:41993

## Kako to uključiti {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (dodaje Scripts\Hooks\heat3d-watch.lua), zatim ponovo pokrenite DCS

Komandu upišite u terminal otvoren u folderu watchera (vidite [Prije nego počnete](before-you-start.md)). Ako ne uspije, zadnja linija kaže zašto; [Instalacija i pokretanje](installing-and-running.md) opisuje uobičajene uzroke.

`python -m heat3d_watch setup dcs` navodi datoteke koje bi promijenio; `python -m heat3d_watch setup dcs --apply` ih mijenja i čuva original kao `<file>.heat3d-backup` (vidite [Komande](commands.md#setup)). Za svaku promjenu ispisuje `dcs: changed: ...`, ili `dcs: nothing to change` kad je već uključeno.

## Kako radi {#how-it-works}

DCS World: mala hook skripta watchera, koja šalje UDP linije na 127.0.0.1:41993.

DCS pri pokretanju izvršava Lua datoteke iz `Saved Games\DCS*\Scripts\Hooks\`; hook može
čitati izvozne funkcije (`Export.Lo*`) i primati callbackove simulacije
(`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - vidite
`<DCS>\API\DCS_ControlAPI.html` i <https://wiki.hoggitworld.com/view/DCS_Export_Script>.
`setup` tu upisuje `heat3d-watch.lua` (vlastitu datoteku: Export.lua i hookovi
drugih alata se ne diraju), koja šalje deset linija u sekundi, jednu više u
sekundi, i po jednu za svaki događaj igre ili callback, nikad ne čekajući odgovor. Port
je 41993 da JoyProov hook (41992) i Tacview (42674) rade pored
njega. Linije (polja odvojena znakom ';'):

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

`p` je LoGetSelfData: Position x/y/z - DCS-ovi vlastiti svjetski metri, x sjever, y gore,
z istok - plus LatLongAlt (stepeni, m), Heading/Pitch/Bank (radijani), uz
LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) i
LoGetAccelerationUnits() x/y/z (g); i, kako ih dokumentira `Scripts\Export.lua`,
LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s),
LoGetAngleOfAttack i LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad),
LoGetRadarAltimeter (m), LoGetVectorVelocity (svjetski m/s), LoGetAngularVelocity
(rad/s), LoGetInAir, te tačka i vektor naprijed iz LoGetCameraPosition (svjetski
metri). `d` je ispis cijelih tabela jednom u sekundi, spljošten u ključeve s tačkama:
LoGetSelfData (država, koalicija, imena jedinice i grupe, nivoi tipa, zastavice),
LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo,
LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute,
LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus i nekoliko
brojeva (pauza, ubrzanje vremena, sjedalo, pritisak, odstupanja). Watcher
čuva svaku liniju cijelu u sirovom sidecaru; `p` postaje i redovi.

Pozicije idu u istu ravnu mapu kao kod drugih simulatora letenja (`Tangent`: x
istok, y visina iznad mora, z sjever, metri) iz LatLongAlt, oko
fiksnog ishodišta teatra (`THEATRES`, iz `map` u start liniji), pa svaka
misija na jednom teatru dijeli jednu mapu, na koju preglednik može položiti stvarni
svijet. Teatar kojeg nema u tabeli uzima geografsku širinu i dužinu prvog
fixa zaokružene na cijele stepene. DCS-ovi vlastiti x/y/z čuvaju se kao `dcs_x`,
`dcs_y`, `dcs_z`; fix bez LatLongAlt ne može se postaviti i samo se
broji (`fixes_without_latlon`). Ishodište je `geo` sesije, u
meta.json i podnožju tabele.

Argumenti za onGameEvent, kako ih daje DCS_ControlAPI:
takeoff/landing (playerID, unit_missionID, airdromeName),
crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID,
killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide,
weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide),
mission_end (winner, msg).

Multiplayer server može zabraniti izvoz vlastite letjelice (LoIsOwnshipExportAllowed je
false); tada nema pozicija, samo događaja, i sesija to kaže.

## Pozicije i ose {#positions-and-axes}

| | |
|---|---|
| Pozicije se snimaju | da |
| Osa gore | `y` |
| Jedinice | metri (istok, visina, sjever od ishodišta teatra) |
| Zrcaljeno za preglednik | `z` |
| Skala jedinica (`scale`: preglednik njome množi pozicije) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima pozicije, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam rotira i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označeno kao igrano online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dozvoljeno (čita samo ono što igra objavljuje)".
- Vrsta `telemetry`: čita samo ono što igra ili platforma daje (UDP port ili dijeljena memorija koju igra objavljuje), pa snima i u online igri kao i offline; zastavica odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj adapter je **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i to nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježene statistike {#statistics-recorded}

Ključevi statistika koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

Ključ u vitičastim zagradama dovršava se za vrijeme rada (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz igrinih vlastitih imena statistika nisu na ovoj listi; "Šta se snima" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeatovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor drži čita se ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, zatim svako polje čuvano po imenu; `used` označava šta je postalo i redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- `p` (10 Hz): pozicija, LatLongAlt, stav, IAS, AGL, g (x/y/z), tip letjelice, te TAS, Mach, vertikalna brzina, AoA, klizanje, magnetski smjer, radarska visina, svjetska brzina, stope rotacije, u zraku i tačka/vektor naprijed kamere iz hooka 2 - sve kao kolone redova (jedinice kako ih daje Export.lua)
- `start`: misija, teatar, vlastiti id i ime igrača, multiplayer, datoteka misije, server; `mis`: datum i vrijeme početka misije u meta.json
- `ev`: svaki onGameEvent kao red (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, svako drugo ime kako je dato)
- `noexport` i `stop` kao redovi i u meta.json

**Čuva se sirovo**

- svaka linija koju hook pošalje, cijela, kao `text` pod svojom vrstom: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; linija bilo koje druge vrste pod `unknown`
- `d` (1 Hz, samo sirovo): cijeli LoGetSelfData (država, koalicija, ime jedinice i grupe, nivoi tipa, zastavice), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, vektor vjetra, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, radio farovi, pauza, ubrzanje vremena, sjedalo, pritisak, odstupanja - spljošteno u ključeve s tačkama
- `mis`: tabela vremena misije, spljoštena; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage s njihovim argumentima

**Nije dostupno**

- druge jedinice (LoGetWorldObjects, LoGetObjectById) i podaci senzora (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): ne traže se - svaki objekt misije na 10 Hz je skup unutar DCS-ovog vlastitog frejma, a server ih zabranjuje (allow_object_export, allow_sensor_export); Tacview ih snima
- cijela tabela misije (DCS.getCurrentMission drži svaku jedinicu i trigger, megabajte): šalju se samo njen datum, vrijeme početka, vrijeme, sortie, teatar i verzija
- onPlayerTry\* callbackovi: oni odgovaraju DCS-u (dopustite ili odbij), pa ih hook ne dira
- adrese i UCID-ovi drugih igrača: net.get_player_info ih daje samo serveru, a nisu ono što igrač smije čuvati
- unosi tabele preko 800 ključeva ili dublje od 6 nivoa u jednoj `d` liniji se odsijecaju, da jedna linija ostane jedan datagram

**Veličina**: oko 20 MB na sat `p` linija (10 u sekundi, oko 500 bajtova svaka s okvirom) i 15-40 MB `d` ispisa (jedan u sekundi, 4-10 KB zavisno o teretu i ruti letjelice), prije zstd; ponovljeni ključevi se komprimiraju oko deset puta

## Provjereno {#verified}

format linije testiran sintetičkim datagramima; Lua hook je neprovjeren unutar DCS-a (napisan iz DCS hook/export API-ja i liste funkcija Lo\* iz Scripts\Export.lua, nije pokrenut)

## Izvor {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
