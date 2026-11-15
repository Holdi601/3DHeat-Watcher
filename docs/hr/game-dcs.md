---
title: "DCS World (živi podaci)"
nav_order: 10
lang: "hr"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (živi podaci) {#dcs-world-live-data}

Dok igrate DCS World, watcher sprema podatke koje sama igra šalje van, pa to kasnije možete pogledati na karti u 3DHeat pregledniku.

*Tehnički podaci: adapter `dcs`, vrsta [`telemetry`](sources-and-rules.md); radi dok je `DCS.exe` pokrenut i traži nove podatke svakih 0,1 s.*

## Što se bilježi {#what-is-recorded}

- vlastita pozicija 10 puta u sekundi, kao metri istočno/gore/sjeverno od ishodišta bojišnice (iz geografske širine/dužine/visine); lat/lon/alt i DCS-ove vlastite svjetske metre (dcs_x sjever, dcs_y gore, dcs_z istok) kao stupci
- stav, indicirana i stvarna brzina zraka, Mach, vertikalna brzina, napadni kut i klizanje, magnetski kurs, AGL i radarska visina, g na tri osi, brzina i brzine rotacije, u zraku, položaj kamere i vektor gledanja kamere, tip letjelice
- polijetanja i slijetanja s aerodromom; padovi, katapultiranja, smrti pilota
- ubojstva i obaranja, s oba tipa jedinica i oružjem; ostali događaji igre kako su dani
- životi po misiji (spawn ... session_end), ubojstva, smrti, udaljenost, najveća visina, najveći g
- svaki redak koji hook šalje, cjelovit u heat.raw.parquet, uz jednom u sekundi ispis tablica letjelice (motori, podvozje i zakrilca, teret, protumjere, ruta, navigacija) i svaki ostali povratni poziv (pauza, chat, ulazak igrača, učitavanje misije)

## Odakle dolazi {#where-it-comes-from}

watcherov hook %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, UDP redovi na 127.0.0.1:41993

## Kako ga uključiti {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (dodaje Scripts\Hooks\heat3d-watch.lua), zatim ponovno pokrenite DCS

Upišite naredbu u terminal otvoren u mapi watchera (vidi [Prije nego što počnete](before-you-start.md)). Ako ne uspije, zadnji redak kaže zašto; [Instalacija i pokretanje](installing-and-running.md) opisuje najčešće uzroke.

`python -m heat3d_watch setup dcs` navodi datoteke koje bi promijenio; `python -m heat3d_watch setup dcs --apply` ih mijenja i čuva original kao `<file>.heat3d-backup` (vidi [Naredbe](commands.md#setup)). Za svaku promjenu ispisuje `dcs: changed: ...`, a kad je već uključeno, `dcs: nothing to change`.

## Kako radi {#how-it-works}

DCS World: mala hook skripta watchera koja šalje UDP redove na 127.0.0.1:41993.

DCS pri pokretanju pokreće Lua datoteke u `Saved Games\DCS*\Scripts\Hooks\`; hook može čitati funkcije izvoza (`Export.Lo*`) i primati povratne pozive simulacije (`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - vidi `<DCS>\API\DCS_ControlAPI.html` i <https://wiki.hoggitworld.com/view/DCS_Export_Script>. `setup` tamo zapisuje `heat3d-watch.lua` (vlastitu datoteku: Export.lua i hookovi drugih alata se ne diraju), koja šalje deset redaka u sekundi, još jedan u sekundi, i po jedan za svaki događaj igre ili povratni poziv, nikad ne čekajući odgovor. Port je 41993 da hook JoyPro-a (41992) i Tacview (42674) rade uz njega. Redovi (polja odvojena ';'):

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

`p` je LoGetSelfData: Position x/y/z - DCS-ove vlastite svjetske metre, x sjever, y gore, z istok - plus LatLongAlt (stupnjevi, m), Heading/Pitch/Bank (radijani), uz LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) i LoGetAccelerationUnits() x/y/z (g); i, kako to navodi `Scripts\Export.lua`, LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s), LoGetAngleOfAttack i LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad), LoGetRadarAltimeter (m), LoGetVectorVelocity (svjetske m/s), LoGetAngularVelocity (rad/s), LoGetInAir te točku i vektor smjera iz LoGetCameraPosition (svjetske metre). `d` je jednom u sekundi ispis cijelih tablica, izravnanih u točkaste ključeve: LoGetSelfData (država, koalicija, imena jedinice i grupe, razine tipa, zastavice), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus i nekoliko brojeva (pauza, ubrzanje vremena, sjedalo, tlak, odstupanja). Watcher čuva svaki redak cjelovito u pomoćnoj sirovoj datoteci; `p` postaje i retci.

Pozicije idu u istu ravnu kartu kao kod drugih simulatora letenja (`Tangent`: x istok, y visina iznad mora, z sjever, metri) iz LatLongAlt, oko fiksnog ishodišta bojišnice (`THEATRES`, iz `map` početnog retka), pa svaka misija na istoj bojišnici dijeli jednu kartu, na koju se može položiti stvarni svijet. Bojišnica koje nema u tablici uzima geografsku širinu i dužinu prvog mjerenja zaokruženu na cijele stupnjeve. DCS-ovi x/y/z čuvaju se kao `dcs_x`, `dcs_y`, `dcs_z`; mjerenje bez LatLongAlt ne može se smjestiti i samo se broji (`fixes_without_latlon`). Ishodište je `geo` sesije, u meta.json i u podnožju tablice.

Argumenti onGameEvent-a, kako ih daje DCS_ControlAPI: takeoff/landing (playerID, unit_missionID, airdromeName), crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID, killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide, weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide), mission_end (winner, msg).

Poslužitelj za više igrača može zabraniti izvoz vlastitog zrakoplova (LoIsOwnshipExportAllowed je false); tada nema pozicija, samo događaji, i sesija to kaže.

## Pozicije i osi {#positions-and-axes}

| | |
|---|---|
| Pozicije se bilježe | da |
| Os prema gore | `y` |
| Jedinice | metri (istok, visina, sjever od ishodišta bojišnice) |
| Zrcaljeno za preglednik | `z` |
| Mjerilo jedinice (`scale`: preglednik pozicije množi njime) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima pozicije, u podnožje `heat.parquet`, pa 3DHeat preglednik sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igra na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `telemetry`: čita samo ono što igra ili platforma daje (UDP port ili dijeljena memorija koju igra objavljuje), pa bilježi i u igri na mreži i izvan nje; zastavica odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri `memory` čitaju memoriju, i nikad za igru označenu kao igra na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Statistika koja se bilježi {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ za svaki tim). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih imena statistike igre nisu na ovom popisu; navedeni su u odjeljku "Što se bilježi" gore.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača 3DHeata](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cjelovito u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje koje je sačuvano po imenu; `used` označava što je postalo i retkom), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- `p` (10 Hz): pozicija, LatLongAlt, stav, IAS, AGL, g (x/y/z), tip letjelice, i TAS, Mach, vertikalna brzina, napadni kut, klizanje, magnetski kurs, radarska visina, svjetska brzina, brzine rotacije, u-zraku te točka i vektor smjera kamere iz hooka 2 - sve kao stupci redaka (jedinice kako ih daje Export.lua)
- `start`: misija, bojišnica, vlastiti ID i ime igrača, igra na mreži, datoteka misije, poslužitelj; `mis`: datum i početno vrijeme misije u meta.json
- `ev`: svaki onGameEvent kao redak (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, svaki ostali naziv kako je dan)
- `noexport` i `stop` kao retci i u meta.json

**Čuva se u izvornom obliku**

- svaki redak koji hook šalje, cjelovit, kao `text` pod svojom vrstom: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; redak bilo koje druge vrste pod `unknown`
- `d` (1 Hz, samo sirovo): LoGetSelfData cjelovito (država, koalicija, imena jedinice i grupe, razine tipa, zastavice), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, vektor vjetra, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, radio svjetionici, pauza, ubrzanje vremena, sjedalo, tlak, odstupanja - izravnano u točkaste ključeve
- `mis`: tablica vremenskih uvjeta misije, izravnana; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage s njihovim argumentima

**Nije dostupno**

- ostale jedinice (LoGetWorldObjects, LoGetObjectById) i podaci senzora (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): nisu zatraženi - svaki objekt misije na 10 Hz skup je unutar okvira same DCS-a, a poslužitelj ih ograničava (allow_object_export, allow_sensor_export); Tacview ih bilježi
- cijela tablica misije (DCS.getCurrentMission sadrži svaku jedinicu i okidač, megabajti): šalju se samo njezin datum, početno vrijeme, vremenski uvjeti, sortie, bojišnica i verzija
- povratni pozivi onPlayerTry\*: odgovaraju DCS-u (dopuste ili odbiju), pa ih hook ne dira
- adrese i UCID-ovi drugih igrača: net.get_player_info ih daje samo poslužitelju, a nisu za čuvanje
- unosi tablice iznad 800 ključeva ili 6 razina dubine u jednom `d` retku se odsijecaju, pa jedan redak ostaje jedan datagram

**Veličina**: oko 20 MB na sat `p` redaka (10 u sekundi, oko 500 bajtova svaki s okvirom) i 15-40 MB `d` ispisa (jednom u sekundi, 4-10 KB ovisno o teretu i ruti letjelice), prije zstd; ponovljeni ključevi se stisnu oko deset puta

## Provjereno {#verified}

format retka testiran sintetičkim datagramima; Lua hook nije testiran unutar DCS-a (napisan prema API-ju DCS hookova i izvoza i prema popisu Lo\* funkcija u Scripts\Export.lua, nije pokretan)

## Izvor {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
