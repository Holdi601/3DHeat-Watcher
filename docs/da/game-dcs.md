---
title: "DCS World (live-data)"
nav_order: 10
lang: "da"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (live-data) {#dcs-world-live-data}

Mens du spiller DCS World, gemmer watcheren de data, spillet selv sender ud, så du senere kan se dem på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `dcs`, slags [`telemetry`](sources-and-rules.md); den kører, mens `DCS.exe` kører, og kigger efter nye data hvert 0,1 s.*

## Hvad der optages {#what-is-recorded}

- egen position 10 gange i sekundet som meter øst/op/nord fra teatrets origo (ud fra breddegrad/længdegrad/højde); lat/lon/alt og DCS' egne verdensmeter (dcs_x nord, dcs_y op, dcs_z øst) som kolonner
- attitude, angivet og sand lufthastighed, Mach, lodret hastighed, angrebsvinkel og sideglidning, magnetisk kurs, AGL og radarhøjde, g på tre akser, hastighed og rotationshastigheder, i luften, kameraets position og fremadvektor, flytype
- start og landinger med flyvepladsen; nedstyrtninger, udkastninger, pilotdød
- drab og at blive skudt ned med begge enhedstyper og våbnet; andre spilhændelser som givet
- livet pr. mission (spawn ... session_end), drab, dødsfald, distance, højeste højde, højeste g
- hver linje hooken sender, gemt helt i heat.raw.parquet, med et ét-sekunds-udtræk af flyets eksporttabeller (motorer, understel og klapper, nyttelast, modforanstaltninger, rute, navigation) og alle andre callbacks (pause, chat, spillere der joiner, indlæsning af missionen)

## Hvor det kommer fra {#where-it-comes-from}

watcherens hook %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, UDP-linjer til 127.0.0.1:41993

## Sådan slår du det til {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (tilføjer Scripts\Hooks\heat3d-watch.lua), derefter genstart DCS

Skriv kommandoen i en terminal, der er åbnet i watcherens mappe (se [Før du går i gang](before-you-start.md)). Hvis det fejler, siger den sidste linje hvorfor; [Installation og kørsel](installing-and-running.md) dækker de almindelige årsager.

`python -m heat3d_watch setup dcs` viser, hvilke filer den ville ændre; `python -m heat3d_watch setup dcs --apply` ændrer dem og gemmer originalen som `<file>.heat3d-backup` (se [Kommandoer](commands.md#setup)). Den skriver `dcs: changed: ...` for hver ændring, eller `dcs: nothing to change`, når den allerede er slået til.

## Sådan virker det {#how-it-works}

DCS World: et lille hook-script af watcherens eget, der sender UDP-linjer til 127.0.0.1:41993.

DCS kører Lua-filer i `Saved Games\DCS*\Scripts\Hooks\` ved start; en hook kan
læse eksportfunktionerne (`Export.Lo*`) og modtage simulationens callbacks
(`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - se
`<DCS>\API\DCS_ControlAPI.html` og <https://wiki.hoggitworld.com/view/DCS_Export_Script>.
`setup` skriver `heat3d-watch.lua` ddér (sin egen fil: Export.lua og andre værktøjers
hooks røres ikke), som sender ti linjer i sekundet, en til i sekundet, og en pr.
spilhændelse eller callback, uden nogensinde at vente på et svar. Porten er 41993, så
JoyPros hook (41992) og Tacview (42674) fortsat virker ved siden af den. Linjerne
(felterne er adskilt med ';'):

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

`p` er LoGetSelfData: Position x/y/z - DCS' egne verdensmeter, x nord, y op,
z øst - plus LatLongAlt (grader, m), Heading/Pitch/Bank (radianer), med
LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) og
LoGetAccelerationUnits() x/y/z (g); og, som `Scripts\Export.lua` beskriver dem,
LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s),
LoGetAngleOfAttack og LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad),
LoGetRadarAltimeter (m), LoGetVectorVelocity (verdens m/s), LoGetAngularVelocity
(rad/s), LoGetInAir, og LoGetCameraPositions punkt og fremadvektor (verdens
meter). `d` er et ét-sekunds-udtræk af hele tabeller, udfladet til punktum-nøgler:
LoGetSelfData (land, koalition, enheds- og gruppenavne, typeniveauer, flag),
LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo,
LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute,
LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus og nogle få
tal (pause, tidsacceleration, sæde, tryk, afvigelser). Watcheren gemmer hver linje
helt i det rå sidecar-lager; `p` bliver også til rækkerne.

Positioner lægges i det samme flade kort som de andre flysimulatorers (`Tangent`: x
øst, y højde over havet, z nord, meter) ud fra LatLongAlt, omkring teatrets faste
origo (`THEATRES`, fra `map` i start-linjen), så hver mission på samme teater deler ét
kort, og viewer kan lægge den rigtige verden under det. Et teater, der ikke står i
tabellen, bruger den første fix' breddegrad og længdegrad afrundet til hele grader.
DCS' egne x/y/z gemmes som `dcs_x`, `dcs_y`, `dcs_z`; en fix uden LatLongAlt kan ikke
placeres og tælles kun (`fixes_without_latlon`). Origo er sessionens `geo`, i
meta.json og tabellens footer.

onGameEvent's argumenter, som DCS_ControlAPI
giver dem: takeoff/landing (playerID, unit_missionID, airdromeName),
crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID,
killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide,
weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide),
mission_end (winner, msg).

En multiplayer-server kan forbyde eksport af egen flyveenhed (LoIsOwnshipExportAllowed er
falsk); så er der ingen positioner, kun hændelser, og sessionen siger det.

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner optaget | ja |
| Opadakse | `y` |
| Enheder | meter (øst, højde, nord fra teatrets origo) |
| Spejlet for viewer | `z` |
| Enhedsskala (`scale`: viewer ganger positionerne med den) | 1 |

Disse går ind i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, i `heat.parquet`s footer, så 3DHeat-viewer selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Multiplayer {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser dette som "allowed (reads only what the game publishes)".
- Slags `telemetry`: den læser kun det, spillet eller platformen udleverer (en UDP-port eller delt hukommelse, spillet udgiver), så den optager også i online-spil, ligesom offline; flaget afgør kun, om hukommelsen nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der optages {#statistics-recorded}

Statistiknøglerne, som denne adapters kode sætter med navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der optages" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder bliver læst eller gemt, aldrig smidt væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar adapteren modtager, helt i sessionens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text` og derefter felter der gemmes efter navn; `used` markerer det, der også blev til rækker), og `meta.json`s `selfCheck.completeness` tæller hver `type` - `lost` er 0.

**Læst**

- `p` (10 Hz): position, LatLongAlt, attitude, IAS, AGL, g (x/y/z), flytype, og hook 2's TAS, Mach, lodret hastighed, AoA, sideglidning, magnetisk kurs, radarhøjde, verdenshastighed, rotationshastigheder, i luften og kameraets punkt/fremadvektor - alt som rækkekolonner (enheder som Export.lua giver dem)
- `start`: mission, teater, egen spiller-id og navn, multiplayer, missionsfil, server; `mis`: missionens dato og starttidspunkt i meta.json
- `ev`: hver onGameEvent som en række (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, andre navne som givet)
- `noexport` og `stop` som rækker og i meta.json

**Gemt rå**

- hver linje hooken sender, helt, som `text` under sin slags: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; en linje af en anden slags under `unknown`
- `d` (1 Hz, kun rå): LoGetSelfData helt (land, koalition, enheds- og gruppenavn, typeniveauer, flag), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, vindvektor, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, radiobaker, pause, tidsacceleration, sæde, tryk, afvigelser - udfladet til punktum-nøgler
- `mis`: missionens vejrtabel, udfladet; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage med deres argumenter

**Ikke tilgængeligt**

- andre enheder (LoGetWorldObjects, LoGetObjectById) og sensordata (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): ikke bedt om - hvert objekt i en mission 10 gange i sekundet er dyrt inde i DCS' egen ramme, og en server styrer dem (allow_object_export, allow_sensor_export); Tacview optager dem
- hele missionstabellen (DCS.getCurrentMission holder hver enhed og trigger, megabytes): kun dens dato, starttidspunkt, vejr, sortie, teater og version sendes
- callbacks onPlayerTry\*: de svarer DCS (tillad eller afvis), så hooken lader dem være
- andre spilleres adresser og UCID'er: net.get_player_info giver dem kun til en server, og de er ikke spillerens at gemme
- en tabels poster ud over 800 nøgler eller 6 niveauer dybt i en `d`-linje bliver skåret af, så én linje forbliver én datagram

**Størrelse**: cirka 20 MB i timen af `p`-linjer (10 i sekundet, cirka 500 bytes hver med sin ramme) og 15-40 MB af `d`-udtræk (ét i sekundet, 4-10 KB afhængigt af flyets nyttelast og rute), før zstd; de gentagne nøgler komprimeres cirka tyve gange

## Verificeret {#verified}

linjeformatet testet med syntetiske datagrammer; Lua-hooken er ikke testet inde i DCS (skrevet ud fra DCS' hook/export-API og Scripts\Export.lua's liste over Lo\*-funktioner, ikke kørt)

## Kilde {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
