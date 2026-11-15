---
title: "DCS World (të dhëna të drejtpërdrejta)"
nav_order: 10
lang: "sq"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (të dhëna të drejtpërdrejta) {#dcs-world-live-data}

Ndërsa luan DCS World, watcher-i ruan të dhënat që dërgon vetë loja, që më vonë t'i shohësh në një hartë në shikuesin 3DHeat.

*Detaje teknike: adapteri `dcs`, lloji [`telemetry`](sources-and-rules.md); ekzekutohet sa kohë `DCS.exe` është në punë dhe kërkon të dhëna të reja çdo 0.1 s.*

## Çfarë regjistrohet {#what-is-recorded}

- pozicioni i vetë lojtarit në 10 Hz si metra lindje/lart/veri nga origjina e teatrit (nga gjerësia/gjatësia gjeografike/lartësia); lat/lon/alt dhe metrat botërorë të vetë DCS (dcs_x veri, dcs_y lart, dcs_z lindje) si kolona
- qëndrimi, shpejtësia e treguar dhe e vërtetë, Mach, shpejtësia vertikale, këndi i sulmit dhe i rrëshqitjes anësore, drejtimi magnetik, lartësia AGL dhe e radarit, g në tri boshte, shpejtësia dhe shpejtësitë e rrotullimit, në ajër, pozicioni i kamerës dhe vektori përpara, lloji i avionit
- ngritjet dhe uljet me fushën ajrore; përplasjet, katapultimet, vdekjet e pilotit
- vrasjet dhe rrëzimi me të dy llojet e njësive dhe armën; ngjarjet e tjera të lojës siç jepen
- jetët për çdo mision (spawn ... session_end), vrasjet, vdekjet, largësia, lartësia më e madhe, g më i madh
- çdo rresht që dërgon hook-u ruhet i plotë në heat.raw.parquet, me një dump një herë në sekondë të tabelave të eksportit të avionit (motorët, ingranazhi dhe flapat, ngarkesa, kundërmasat, itinerari, navigimi) dhe çdo callback tjetër (pauzë, chat, lojtarë që hyjnë, ngarkimi i misionit)

## Nga vjen {#where-it-comes-from}

hook-u i watcher-it %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, rreshta UDP te 127.0.0.1:41993

## Si aktivizohet {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (shton Scripts\Hooks\heat3d-watch.lua), pastaj rinise DCS

Shkruaje komandën në një terminal të hapur në dosjen e watcher-it (shih [Para se të fillosh](before-you-start.md)). Nëse dështon, rreshti i fundit tregon pse; [Instalimi dhe ekzekutimi](installing-and-running.md) përmban shkaqet më të zakonshme.

`python -m heat3d_watch setup dcs` liston skedarët që do të ndryshonte; `python -m heat3d_watch setup dcs --apply` i ndryshon, duke e ruajtur origjinalin si `<file>.heat3d-backup` (shih [Komandat](commands.md#setup)). Shfaq `dcs: changed: ...` për çdo ndryshim, ose `dcs: nothing to change` kur është tashmë i aktivizuar.

## Si funksionon {#how-it-works}

DCS World: një skript i vogël hook i vetë watcher-it, që dërgon rreshta UDP te 127.0.0.1:41993.

DCS ekzekuton skedarë Lua te `Saved Games\DCS*\Scripts\Hooks\` kur niset; një hook mund të
lexojë funksionet e eksportit (`Export.Lo*`) dhe të marrë callback-et e simulimit
(`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - shih
`<DCS>\API\DCS_ControlAPI.html` dhe <https://wiki.hoggitworld.com/view/DCS_Export_Script>.
`setup` shkruan aty `heat3d-watch.lua` (skedarin e vet: Export.lua dhe hook-et e
mjeteve të tjera nuk preken), i cili dërgon dhjetë rreshta në sekondë, një tjetër në
sekondë, dhe një për çdo ngjarje loje ose callback, pa pritur kurrë përgjigje. Porta
është 41993, që hook-u i JoyPro (41992) dhe Tacview (42674) të vazhdojnë të punojnë pranë
tij. Rreshtat (fushat ndahen me ';'):

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

`p` është LoGetSelfData: Position x/y/z - metrat botërorë të vetë DCS, x veri, y lart,
z lindje - plus LatLongAlt (shkallë, m), Heading/Pitch/Bank (radianë), me
LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) dhe
LoGetAccelerationUnits() x/y/z (g); dhe, siç i dokumenton `Scripts\Export.lua`,
LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s),
LoGetAngleOfAttack dhe LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad),
LoGetRadarAltimeter (m), LoGetVectorVelocity (m/s botërore), LoGetAngularVelocity
(rad/s), LoGetInAir, dhe pika dhe vektori përpara i LoGetCameraPosition (metra
botërorë). `d` është një dump një herë në sekondë i tabelave të plota, të sheshuara në çelësa me pika:
LoGetSelfData (vendi, koalicioni, emrat e njësisë dhe grupit, nivelet e llojit, flamujt),
LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo,
LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute,
LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus dhe disa
numra (pauza, përshpejtimi i kohës, ulësja, presioni, devijimet). Watcher-i
i ruan të gjithë rreshtat të plotë në skedarin raw anësor; `p` bëhet edhe rreshta.

Pozicionet shkojnë në të njëjtën hartë të sheshtë si ato të simulatorëve të tjerë të fluturimit (`Tangent`: x
lindje, y lartësia mbi nivelin e detit, z veri, metra) nga LatLongAlt, përreth
origjinës së fiksuar të teatrit (`THEATRES`, nga `map` i rreshtit start), kështu që çdo
mision në një teatër ndan një hartë të vetme, dhe një ku shikuesi mund të vendosë
botën e vërtetë poshtë. Një teatër që nuk është në tabelë merr gjerësinë dhe
gjatësinë gjeografike të pozicionit të parë, të rrumbullakosura në gradë të plota. x/y/z e vetë DCS ruhen si `dcs_x`,
`dcs_y`, `dcs_z`; një pozicion pa LatLongAlt nuk mund të vendoset dhe vetëm
numërohet (`fixes_without_latlon`). Origjina është `geo` e seancës, në
meta.json dhe në fundin e tabelës.

Argumentet e onGameEvent, siç i jep DCS_ControlAPI:
takeoff/landing (playerID, unit_missionID, airdromeName),
crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID,
killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide,
weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide),
mission_end (winner, msg).

Një server me shumë lojtarë mund ta ndalojë eksportin e avionit të vetë lojtarit (LoIsOwnshipExportAllowed është
false); atëherë nuk ka pozicione, vetëm ngjarje, dhe seanca e thotë këtë.

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet regjistrohen | po |
| Boshti lart | `y` |
| Njësitë | metra (lindje, lartësi, veri nga origjina e teatrit) |
| Pasqyruar për shikuesin | `z` |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto shkojnë në `meta.json` të çdo seance (`axes`) dhe, kur seanca ka pozicione, në fundin e `heat.parquet`, që shikuesi 3DHeat t'i rrotullojë dhe shkallëzojë rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si luajtur online (`multiplayer`): **po**. `games --markdown` e shfaq këtë si "allowed (reads only what the game publishes)".
- Lloji `telemetry`: lexon vetëm çfarë jep loja ose platforma (një port UDP ose memorie e përbashkët që e boton loja), ndaj regjistron edhe në lojë online edhe offline; flamuri vendos vetëm nëse mund të lexohet ndonjëherë memoria.
- Memoria: **kurrë** nuk lexohet nga ky adapter. Vetëm adapterat `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adapteri i vendos me emër (`stats` e çdo seance në `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

Një çelës në kllapa gjarpëruese plotësohet gjatë ekzekutimit (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë fushash të lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher-i ndjek [rregullin e konvertuesve](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, nuk hidhet kurrë. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që merr adapteri ruhet e plotë në `heat.raw.parquet` të seancës (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e mbajtur me emër; `used` shënon çfarë u bë edhe rresht), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexohet**

- `p` (10 Hz): pozicioni, LatLongAlt, qëndrimi, IAS, AGL, g (x/y/z), lloji i avionit, dhe TAS, Mach, shpejtësia vertikale, AoA, rrëshqitja anësore, drejtimi magnetik, lartësia e radarit, shpejtësia botërore, shpejtësitë e rrotullimit, në ajër dhe pika/vektori përpara i kamerës të hook-ut 2 - të gjitha si kolona rreshtash (njësitë siç i jep Export.lua)
- `start`: misioni, teatri, id-ja dhe emri i vetë lojtarit, multiplayer, skedari i misionit, serveri; `mis`: data dhe ora e fillimit të misionit në meta.json
- `ev`: çdo onGameEvent si rresht (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, çdo emër tjetër siç jepet)
- `noexport` dhe `stop` si rreshta dhe në meta.json

**Ruhet i papërpunuar**

- çdo rresht që dërgon hook-u, i plotë, si `text` nën llojin e tij: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; një rresht i çdo lloji tjetër nën `unknown`
- `d` (1 Hz, vetëm raw): LoGetSelfData e plotë (vendi, koalicioni, emri i njësisë dhe grupit, nivelet e llojit, flamujt), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, vektori i erës, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, radiofaret, pauza, përshpejtimi i kohës, ulësja, presioni, devijimet - të sheshuara në çelësa me pika
- `mis`: tabela e motit të misionit, e sheshuar; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage me argumentet e tyre

**Nuk disponohet**

- njësitë e tjera (LoGetWorldObjects, LoGetObjectById) dhe të dhënat e sensorëve (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): nuk kërkohen - çdo objekt i një misioni në 10 Hz është i kushtueshëm brenda kuadrit të vetë DCS, dhe një server i kufizon (allow_object_export, allow_sensor_export); Tacview i regjistron
- tabela e plotë e misionit (DCS.getCurrentMission mban çdo njësi dhe trigger, megabajta): dërgohen vetëm data, ora e fillimit, moti, sortia, teatri dhe versioni
- callback-et onPlayerTry\*: i përgjigjen DCS (lejo ose refuzo), ndaj hook-u i lë të paprekura
- adresat dhe UCID-të e lojtarëve të tjerë: net.get_player_info i jep vetëm një serveri, dhe nuk janë të lojtarit që t'i mbajë
- hyrjet e një tabele përtej 800 çelësave ose 6 nivelesh thellësi në një rresht `d` priten, që një rresht të mbetet një datagram

**Madhësia**: rreth 20 MB në orë rreshta `p` (10 në sekondë, rreth 500 bajte secili me kuadrin e vet) dhe 15-40 MB dump-e `d` (një në sekondë, 4-10 KB sipas ngarkesës dhe itinerarit të avionit), para zstd; çelësat e përsëritur ngjeshen rreth dhjetë herë

## Verifikuar {#verified}

formati i rreshtave i provuar me datagrame sintetike; hook-u Lua është i paprovuar brenda DCS (shkruar nga API-ja e hook/eksportit të DCS dhe lista e funksioneve Lo\* të Scripts\Export.lua, jo i ekzekutuar)

## Burimi {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Gjeneruar nga adapteri me tools/gen_game_pages.py; ndrysho adapterin dhe ekzekuto përsëri, mos e redakto këtë faqe. -->
