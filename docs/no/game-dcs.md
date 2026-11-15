---
title: "DCS World (direkte data)"
nav_order: 10
lang: "no"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (direkte data) {#dcs-world-live-data}

Mens du spiller DCS World, lagrer watcheren dataene spillet selv sender ut, slik at du senere kan se på dem på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `dcs`, type [`telemetry`](sources-and-rules.md); den kjører mens `DCS.exe` går og ser etter nye data hvert 0,1 s.*

## Hva som tas opp {#what-is-recorded}

- egen posisjon 10 ganger i sekundet, som meter øst/opp/nord fra teatrets origo (fra breddegrad/lengdegrad/høyde); lat/lon/alt og DCS' egne verdensmeter (dcs_x nord, dcs_y opp, dcs_z øst) som kolonner
- stilling, indikert og sann flyhastighet, Mach, vertikal hastighet, angrepsvinkel og sideglidning, magnetisk kurs, AGL og radarhøyde, g på tre akser, hastighet og rotasjonshastigheter, i luften, kameraets posisjon og fremoverretning, flytype
- start og landinger med flyplassen; krasj, utkast, pilotdødsfall
- drap og å bli skutt ned, med begge enhetstypene og våpenet; andre spillhendelser slik de er gitt
- liv per oppdrag (spawn ... session_end), drap, dødsfall, distanse, høyeste høyde, høyeste g
- hver linje hooken sender, helt, i heat.raw.parquet, med en dump hvert sekund av flyets eksporttabeller (motorer, understell og klaffer, last, mottiltak, rute, navigasjon) og alle andre callbacks (pause, chat, spillere som kobler til, oppdrag som lastes)

## Hvor det kommer fra {#where-it-comes-from}

watcherens hook %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, UDP-linjer til 127.0.0.1:41993

## Slik slår du det på {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (legger til Scripts\Hooks\heat3d-watch.lua), start deretter DCS på nytt

Skriv kommandoen i en terminal som er åpnet i watcher-mappen (se [Før du starter](before-you-start.md)). Hvis den feiler, sier siste linje hvorfor. [Installere og kjøre](installing-and-running.md) dekker de vanlige årsakene.

`python -m heat3d_watch setup dcs` lister filene den ville endret. `python -m heat3d_watch setup dcs --apply` endrer dem og tar vare på originalen som `<file>.heat3d-backup` (se [Kommandoer](commands.md#setup)). Den skriver `dcs: changed: ...` for hver endring, eller `dcs: nothing to change` når det allerede er slått på.

## Slik fungerer det {#how-it-works}

DCS World: et lite hook-skript watcheren har laget selv, som sender UDP-linjer til 127.0.0.1:41993.

DCS kjører Lua-filer i `Saved Games\DCS*\Scripts\Hooks\` ved start; en hook kan lese eksportfunksjonene (`Export.Lo*`) og ta imot simuleringens callbacks (`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - se `<DCS>\API\DCS_ControlAPI.html` og <https://wiki.hoggitworld.com/view/DCS_Export_Script>. `setup` skriver `heat3d-watch.lua` dit (sin egen fil: Export.lua og andre verktøys hooks røres ikke). Den sender ti linjer i sekundet, en ekstra i sekundet, og én per spillhendelse eller callback, uten å vente på svar. Porten er 41993, slik at JoyPros hook (41992) og Tacview (42674) fortsatt virker ved siden av. Linjene (felt skilt med ';'):

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

`p` er LoGetSelfData: Position x/y/z - DCS' egne verdensmeter, x nord, y opp, z øst - pluss LatLongAlt (grader, m), Heading/Pitch/Bank (radianer), med LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) og LoGetAccelerationUnits() x/y/z (g); og, slik `Scripts\Export.lua` dokumenterer dem, LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s), LoGetAngleOfAttack og LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad), LoGetRadarAltimeter (m), LoGetVectorVelocity (verdens m/s), LoGetAngularVelocity (rad/s), LoGetInAir, og LoGetCameraPositions punkt og fremoverretning (verdens meter). `d` er en dump hvert sekund av hele tabeller, flatet til prikkede nøkler: LoGetSelfData (land, koalisjon, enhets- og gruppenavn, typenivåer, flagg), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus og noen få tall (pause, tidsakselerasjon, sete, trykk, avvik). Watcheren tar vare på hver linje hel i den rå sidefilen; `p` blir også til radene.

Posisjoner havner i det samme flate kartet som de andre flysimulatorenes (`Tangent`: x øst, y høyde over havet, z nord, meter) fra LatLongAlt, rundt teatrets faste origo (`THEATRES`, fra `map` på startlinjen), slik at hvert oppdrag på ett teater deler ett kart, og et kart viewer kan legge den virkelige verden under. Et teater som ikke står i tabellen, tar første fixs breddegrad og lengdegrad avrundet til hele grader. DCS' egne x/y/z tas vare på som `dcs_x`, `dcs_y`, `dcs_z`; en fix uten LatLongAlt kan ikke plasseres og telles bare (`fixes_without_latlon`). Origo er øktens `geo`, i meta.json og tabellens footer.

onGameEvent-argumentene, slik DCS_ControlAPI gir dem: takeoff/landing (playerID, unit_missionID, airdromeName), crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID, killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide, weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide), mission_end (winner, msg).

En flerspillerserver kan forby eksport av eget fly (LoIsOwnshipExportAllowed er false); da finnes det ingen posisjoner, bare hendelser, og økten sier det.

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner registreres | ja |
| Opp-akse | `y` |
| Enheter | meter (øst, høyde, nord fra teatrets origo) |
| Speilet for visningen | `z` |
| Enhetsskala (`scale`: visningen ganger posisjonene med den) | 1 |

Disse havner i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet`s footer, slik at 3DHeat-vieweren snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som "allowed (reads only what the game publishes)".
- Type `telemetry`: den leser bare det spillet eller plattformen gir ut (en UDP-port eller delt minne som spillet publiserer), så den tar opp også i nettspill, både på nett og offline; flagget avgjør bare om minnet noen gang kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill som er merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som registreres {#statistics-recorded}

Statistikknøkler som denne adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

En nøkkel i klammer fylles ut ved kjøretid (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell over spillets felt eller fra spillets egne statistikknavn står ikke i denne listen; "Hva som tas opp" over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller tas vare på, og slettes aldri. I tillegg til radene tas hver pakke, side, linje eller svar adapteren mottar, vare på hel i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, pluss felt som tas vare på med navn; `used` markerer det som også ble til rader), og `selfCheck.completeness` i `meta.json` teller hver `type` - `lost` er 0.

**Leses**

- `p` (10 Hz): posisjon, LatLongAlt, stilling, IAS, AGL, g (x/y/z), flytype, og hook 2s TAS, Mach, vertikal hastighet, AoA, sideglidning, magnetisk kurs, radarhøyde, verdenshastighet, rotasjonshastigheter, i luften og kameraets punkt/fremoverretning - alt som radkolonner (enheter slik Export.lua gir dem)
- `start`: oppdrag, teater, egen spiller-id og navn, flerspiller, oppdragsfil, server; `mis`: oppdragets dato og starttid inn i meta.json
- `ev`: hver onGameEvent som en rad (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, og andre navn slik de er gitt)
- `noexport` og `stop` som rader og i meta.json

**Tatt vare på rått**

- hver linje hooken sender, hel, som `text` under sin type: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; en linje av en annen type under `unknown`
- `d` (1 Hz, bare rått): LoGetSelfData hel (land, koalisjon, enhets- og gruppenavn, typenivåer, flagg), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, vindvektor, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, radiofyr, pause, tidsakselerasjon, sete, trykk, avvik - flatet til prikkede nøkler
- `mis`: oppdragets værtabell, flatet; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage med argumentene sine

**Ikke tilgjengelig**

- andre enheter (LoGetWorldObjects, LoGetObjectById) og sensordata (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): ikke bedt om - hvert objekt i et oppdrag 10 ganger i sekundet er kostbart inne i DCS' egen ramme, og en server styrer dem (allow_object_export, allow_sensor_export); Tacview tar dem opp
- hele oppdragstabellen (DCS.getCurrentMission holder alle enheter og utløsere, megabyte): bare dato, starttid, vær, sortie, teater og versjon sendes
- callbackene onPlayerTry\*: de svarer DCS (tillat eller nekt), så hooken lar dem være
- andre spilleres adresser og UCIDer: net.get_player_info gir dem bare til en server, og de er ikke spillerens å ta vare på
- en tabells oppføringer over 800 nøkler eller 6 nivåer dypt i én `d`-linje kuttes, slik at én linje forblir én datagram

**Størrelse**: omtrent 20 MB per time med `p`-linjer (10 i sekundet, omtrent 500 byte hver med sin ramme) og 15-40 MB med `d`-dumper (én i sekundet, 4-10 KB avhengig av flyets last og rute), før zstd; de gjentatte nøklene komprimeres omtrent tiasganger

## Verifisert {#verified}

linjeformatet testet med syntetiske datagrammer; Lua-hooken er ikke testet inne i DCS (skrevet fra DCS' hook/eksport-API og Scripts\Export.lua sin liste over Lo\*-funksjoner, ikke kjørt)

## Kilde {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
