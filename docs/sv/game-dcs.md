---
title: "DCS World (livedata)"
nav_order: 10
lang: "sv"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (livedata) {#dcs-world-live-data}

Medan du spelar DCS World sparar watchern den data som spelet själv skickar ut, så att du senare kan titta på den på en karta i 3DHeat-visaren.

*Teknisk information: adaptern `dcs`, typ [`telemetry`](sources-and-rules.md); den körs medan `DCS.exe` är igång och letar efter ny data var 0,1 s.*

## Vad som spelas in {#what-is-recorded}

- egen position 10 gånger per sekund som meter öster/upp/norr från teaterns origo (från latitud/longitud/höjd); lat/lon/alt och DCS:s egna världsmeter (dcs_x norr, dcs_y upp, dcs_z öster) som kolumner
- attityd, visad och sann lufthastighet, Mach, vertikal hastighet, anfallsvinkel och glidvinkel, magnetisk kurs, AGL och radarhöjd, g i tre axlar, hastighet och rotationshastigheter, i luften, kamerans position och framriktningsvektor, flygplanstyp
- start och landningar med flygfältet; krascher, utkastningar, pilotdödsfall
- kills och att bli nedskjuten med båda enhetstyperna och vapnet; andra spelhändelser som de ges
- varv per uppdrag (spawn ... session_end), kills, dödsfall, sträcka, högsta höjd, högsta g
- varje rad som hooken skickar, helt sparad i heat.raw.parquet, med en en gång per sekund-dump av flygplanets exporttabeller (motorer, underrede och klaffar, last, motmedel, rutt, navigation) och varje annan callback (paus, chatt, spelare som ansluter, uppdrag som laddas)

## Varifrån det kommer {#where-it-comes-from}

watcherns hook %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, UDP-rader till 127.0.0.1:41993

## Så slår du på det {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (lägger till Scripts\Hooks\heat3d-watch.lua), starta sedan om DCS

Skriv kommandot i en terminal som är öppen i watcherns mapp (se [Innan du börjar](before-you-start.md)). Om det misslyckas säger sista raden varför; [Installera och köra](installing-and-running.md) beskriver de vanligaste orsakerna.

`python -m heat3d_watch setup dcs` visar vilka filer som skulle ändras; `python -m heat3d_watch setup dcs --apply` ändrar dem och sparar originalet som `<file>.heat3d-backup` (se [Kommandon](commands.md#setup)). Den skriver `dcs: changed: ...` för varje ändring, eller `dcs: nothing to change` när det redan är på.

## Så fungerar det {#how-it-works}

DCS World: ett litet hook-skript av watchern själv, som skickar UDP-rader till 127.0.0.1:41993.

DCS kör Lua-filer i `Saved Games\DCS*\Scripts\Hooks\` när det startar; en hook kan läsa exportfunktionerna (`Export.Lo*`) och ta emot simuleringens callbacks (`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - se `<DCS>\API\DCS_ControlAPI.html` och <https://wiki.hoggitworld.com/view/DCS_Export_Script>. `setup` skriver `heat3d-watch.lua` dit (dess egen fil: Export.lua och andra verktygs hooks rörs inte), som skickar tio rader per sekund, en till per sekund, och en per spelhändelse eller callback, utan att någonsin vänta på svar. Porten är 41993 så att JoyPros hook (41992) och Tacview (42674) fortsätter fungera bredvid den. Raderna (fälten delade med ';'):

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

`p` är LoGetSelfData: Position x/y/z - DCS:s egna världsmeter, x norr, y upp, z öster - plus LatLongAlt (grader, m), Heading/Pitch/Bank (radianer), med LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) och LoGetAccelerationUnits() x/y/z (g); och, så som `Scripts\Export.lua` beskriver dem, LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s), LoGetAngleOfAttack och LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad), LoGetRadarAltimeter (m), LoGetVectorVelocity (världens m/s), LoGetAngularVelocity (rad/s), LoGetInAir, och LoGetCameraPosition:s punkt och framriktningsvektor (världens meter). `d` är en en gång per sekund-dump av hela tabeller, utplattade till punktade nycklar: LoGetSelfData (land, koalition, enhets- och gruppnamn, typnivåer, flaggor), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus och några tal (paus, tidsacceleration, säte, tryck, avvikelser). Watchern sparar varje rad helt i den råa sidovagnen; `p` blir också raderna.

Positionerna går in i samma platta karta som de andra flygsimmarnas (`Tangent`: x öster, y höjd över havet, z norr, meter) från LatLongAlt, runt teaterns fasta origo (`THEATRES`, från `map` på startraden), så att varje uppdrag på en teater delar en karta, och en som visaren kan lägga den riktiga världen under. En teater som inte finns i tabellen tar första fixens latitud och longitud avrundade till hela grader. DCS:s egna x/y/z sparas som `dcs_x`, `dcs_y`, `dcs_z`; en fix utan LatLongAlt kan inte placeras och räknas bara (`fixes_without_latlon`). Origo är sessionens `geo`, i meta.json och tabellens footer.

onGameEvent:s argument, så som DCS_ControlAPI ger dem: takeoff/landing (playerID, unit_missionID, airdromeName), crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID, killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide, weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide), mission_end (winner, msg).

En flerspelarserver kan förbjuda export av egenfarkosten (LoIsOwnshipExportAllowed är false); då finns inga positioner, bara händelser, och sessionen säger det.

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | ja |
| Uppåtaxel | `y` |
| Enheter | meter (öster, höjd, norr från teaterns origo) |
| Speglad för visaren | `z` |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s footer, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Multiplayer {#multiplayer}

- Markerad som spelad online (`multiplayer`): **ja**. `games --markdown` visar detta som "tillåten (läser bara det spelet publicerar)".
- Typ `telemetry`: den läser bara det spelet eller plattformen lämnar ut (en UDP-port eller delat minne som spelet publicerar), så den spelar in även i onlinespel så väl som offline; flaggan avgör bara om minnet någonsin får läsas.
- Minne: läses **aldrig** av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

En nyckel inom klammerparenteser fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte med i den här listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

Watchern följer 3DHeats [omvandlarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text`, plus eventuella fält som sparas med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- `p` (10 Hz): position, LatLongAlt, attityd, IAS, AGL, g (x/y/z), flygplanstyp, och hook 2:s TAS, Mach, vertikal hastighet, AoA, glidvinkel, magnetisk kurs, radarhöjd, världshastighet, rotationshastigheter, i luften och kameran punkt/framriktning - allt som radkolumner (enheter som Export.lua ger dem)
- `start`: uppdrag, teater, egen spelar-id och namn, multiplayer, uppdragsfil, server; `mis`: uppdragets datum och starttid i meta.json
- `ev`: varje onGameEvent som en rad (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, varje annat namn som det ges)
- `noexport` och `stop` som rader och i meta.json

**Sparas råa**

- varje rad som hooken skickar, helt, som `text` under sin typ: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; en rad av någon annan typ under `unknown`
- `d` (1 Hz, bara råa): LoGetSelfData helt (land, koalition, enhets- och gruppnamn, typnivåer, flaggor), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, vindvektor, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, radiofyrar, paus, tidsacceleration, säte, tryck, avvikelser - utplattat till punktade nycklar
- `mis`: uppdragets vädertabell, utplattad; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage med deras argument

**Inte tillgängligt**

- andra enheter (LoGetWorldObjects, LoGetObjectById) och sensordata (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): inte begärt - varje objekt i ett uppdrag 10 gånger per sekund är dyrt inuti DCS:s egen ram, och en server styr dem (allow_object_export, allow_sensor_export); Tacview spelar in dem
- hela uppdragstabellen (DCS.getCurrentMission innehåller varje enhet och trigger, megabyte): bara dess datum, starttid, väder, sortie, teater och version skickas
- callbacks onPlayerTry\*: de svarar DCS (tillåter eller nekar), så hooken låter dem vara
- andra spelares adresser och UCID:n: net.get_player_info ger dem bara till en server, och de är inte spelarens att spara
- en tabells poster efter 800 nycklar eller 6 nivåer djupt i en `d`-rad kapas, så att en rad förblir ett datagram

**Storlek**: ungefär 20 MB per timme av `p`-rader (10 per sekund, cirka 500 byte vardera med sin ram) och 15-40 MB av `d`-dumpar (en per sekund, 4-10 KB beroende på flygplanets last och rutt), före zstd; de upprepade nycklarna komprimeras cirka tiofaldigt

## Verifierad {#verified}

radformatet testat med syntetiska datagram; Lua-hooken är inte testad inne i DCS (skriven utifrån DCS:s hook- och exportgränssnitt och Scripts\Export.lua:s lista över Lo\*-funktioner, inte körd)

## Källa {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
