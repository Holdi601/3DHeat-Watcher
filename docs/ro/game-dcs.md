---
title: "DCS World (date în timp real)"
nav_order: 10
lang: "ro"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (date în timp real) {#dcs-world-live-data}

Cât joci DCS World, watcher-ul salvează datele pe care jocul însuși le trimite afară, ca să te poți uita mai târziu la ele pe o hartă în vizualizatorul 3DHeat.

*Detalii tehnice: adaptorul `dcs`, tip [`telemetry`](sources-and-rules.md); rulează cât timp `DCS.exe` este pornit și caută date noi la fiecare 0,1 s.*

## Ce se înregistrează {#what-is-recorded}

- poziția ta, de 10 ori pe secundă, ca metri est/sus/nord față de originea teatrului de operațiuni (din latitudine/longitudine/altitudine); lat/lon/alt și metrii lumii ai DCS (dcs_x nord, dcs_y sus, dcs_z est) ca coloane
- atitudine, viteza indicată și reală, Mach, viteza verticală, unghiul de atac și alunecarea, cap magnetic, AGL și altitudinea radar, g pe trei axe, viteze și viteze de rotație, în aer, poziția camerei și vectorul ei înainte, tipul aeronavei
- decolări și aterizări cu aerodromul; prăbușiri, catapultări, morțile pilotului
- eliminări și doborâri, cu ambele tipuri de unități și arma; alte evenimente ale jocului, cum sunt date
- vieți per misiune (spawn ... session_end), eliminări, morți, distanță, altitudinea cea mai mare, g-ul cel mai mare
- fiecare linie trimisă de hook, păstrată integral în heat.raw.parquet, cu un export o dată pe secundă al tabelelor aeronavei (motoare, trenul și flapsurile, încărcătura, contramăsuri, rută, navigație) și fiecare alt callback (pauză, chat, jucători care intră, încărcarea misiunii)

## De unde vine {#where-it-comes-from}

hook-ul watcher-ului %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, linii UDP către 127.0.0.1:41993

## Cum îl pornești {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (adaugă Scripts\Hooks\heat3d-watch.lua), apoi repornești DCS

Scrie comanda într-un terminal deschis în folderul watcher-ului (vezi [Înainte de a începe](before-you-start.md)). Dacă eșuează, ultima linie spune de ce; [Instalarea și rularea](installing-and-running.md) acoperă cauzele obișnuite.

`python -m heat3d_watch setup dcs` arată ce fișiere ar schimba; `python -m heat3d_watch setup dcs --apply` le schimbă, păstrând originalul ca `<file>.heat3d-backup` (vezi [Comenzi](commands.md#setup)). Afișează `dcs: changed: ...` pentru fiecare modificare, sau `dcs: nothing to change` dacă este deja pornit.

## Cum funcționează {#how-it-works}

DCS World: un mic script hook al watcher-ului, care trimite linii UDP către 127.0.0.1:41993.

DCS rulează fișierele Lua din `Saved Games\DCS*\Scripts\Hooks\` la pornire; un hook poate folosi funcțiile de export (`Export.Lo*`) și primi callback-urile simulării (`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - vezi `<DCS>\API\DCS_ControlAPI.html` și <https://wiki.hoggitworld.com/view/DCS_Export_Script>. `setup` scrie `heat3d-watch.lua` acolo (fișierul lui propriu: Export.lua și hook-urile altor unelte nu sunt atinse), care trimite zece linii pe secundă, încă una pe secundă și câte una pentru fiecare eveniment de joc sau callback, fără să aștepte vreun răspuns. Portul este 41993, ca hook-ul JoyPro (41992) și Tacview (42674) să funcționeze în continuare alături de el. Liniile (câmpurile sunt despărțite prin ';'):

```text
hello;v=2                                       hook-ul a fost încărcat
start;mission=..;map=..;me=<player id>;name=..;mp=0|1;file=..;server=0|1
mis;t=..;date.Day=..;start_time=..;weather...   data misiunii, ora de start și vremea, aplatizate
p;t=<model s>;x=;y=;z=;lat=;lon=;alt=;hdg=;pitch=;bank=;ias=;agl=;g=;type=;tas=;mach=;vv=;aoa=;aos=;
  mhdg=;ralt=;gx=;gz=;vx=;vy=;vz=;wx=;wy=;wz=;air=;cx=;cy=;cz=;cfx=;cfy=;cfz=
d;t=..;self.Name=..;eng.RPM.left=..;mech.gear.value=..;pay.Stations.1.count=..;...   o dată pe secundă
ev;t=..;name=<onGameEvent name>;args=a|b|c      fiecare onGameEvent
cb;t=..;name=<callback>;args=a|b                fiecare alt callback (pauză, chat, jucători, încărcare)
noexport;t=..                                   serverul interzice exportul aeronavei proprii
stop;t=..                                       misiunea s-a încheiat
```

`p` este LoGetSelfData: Position x/y/z - metrii lumii ai DCS, x nord, y sus, z est - plus LatLongAlt (grade, m), Heading/Pitch/Bank (radiani), cu LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) și LoGetAccelerationUnits() x/y/z (g); și, cum documentează `Scripts\Export.lua`, LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s), LoGetAngleOfAttack și LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad), LoGetRadarAltimeter (m), LoGetVectorVelocity (m/s în lume), LoGetAngularVelocity (rad/s), LoGetInAir, și punctul și vectorul înainte ale LoGetCameraPosition (metri în lume). `d` este un export o dată pe secundă al tabelelor întregi, aplatizate în chei cu puncte: LoGetSelfData (țara, coaliția, numele unității și grupului, nivelurile tipului, steaguri), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus și câteva numere (pauză, accelerarea timpului, locul, presiunea, abaterile). Watcher-ul păstrează fiecare linie integral în sidecar-ul brut; `p` devine și rânduri.

Pozițiile intră în aceeași hartă plată ca ale celorlalte simulatoare de zbor (`Tangent`: x est, y altitudine deasupra mării, z nord, în metri) din LatLongAlt, în jurul originii fixe a teatrului (`THEATRES`, din `map` al liniei de start), așa că fiecare misiune de pe același teatru are aceeași hartă, pe care vizualizatorul poate să o suprapună peste lumea reală. Un teatru care nu este în tabel ia latitudinea și longitudinea primei măsurători rotunjite la grade întregi. x/y/z ai DCS se păstrează ca `dcs_x`, `dcs_y`, `dcs_z`; o măsurătoare fără LatLongAlt nu poate fi plasată și se numără doar (`fixes_without_latlon`). Originea este `geo` al sesiunii, în meta.json și în subsolul tabelului.

Argumentele onGameEvent, așa cum le dă DCS_ControlAPI: takeoff/landing (playerID, unit_missionID, airdromeName), crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID, killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide, weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide), mission_end (winner, msg).

Un server multiplayer poate interzice exportul aeronavei proprii (LoIsOwnshipExportAllowed este fals); atunci nu există poziții, doar evenimente, iar sesiunea o spune.

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa în sus | `y` |
| Unități | metri (est, altitudine, nord față de originea teatrului) |
| Oglindită pentru vizualizator | `z` |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, așa că vizualizatorul 3DHeat rotește și scalează singur rândurile - vezi [Datele](the-data.md).

## Joc online {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)”.
- Tip `telemetry`: citește doar ce scoate jocul sau platforma (un port UDP sau o memorie partajată publicată de joc), deci înregistrează și în jocul online, nu doar offline; steagul decide doar dacă memoria are voie să fie citită vreodată.
- Memorie: **niciodată** citită de acest adaptor. Doar adaptoarele `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online - vezi [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistică pe care codul acestui adaptor le setează după nume (`stats` din `meta.json` al fiecărei sesiuni și tabelul `stats` din `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor jocului nu sunt în această listă; „Ce se înregistrează” de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează [regula de convertor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) a 3DHeat: ce are sursa este citit sau păstrat, niciodată aruncat. În afară de rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat integral în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat după nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type` - `lost` este 0.

**Citit**

- `p` (10 Hz): poziția, LatLongAlt, atitudinea, IAS, AGL, g (x/y/z), tipul aeronavei și TAS, Mach, viteza verticală, AoA, alunecarea, capul magnetic, altitudinea radar, viteza în lume, vitezele de rotație, în aer și punctul/vectorul înainte ale camerei ale hook-ului 2 - toate ca coloane de rând (unitățile cum le dă Export.lua)
- `start`: misiunea, teatrul, id-ul și numele propriu de jucător, multiplayer, fișierul misiunii, serverul; `mis`: data misiunii și ora de start în meta.json
- `ev`: fiecare onGameEvent ca rând (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, orice alt nume ca atare)
- `noexport` și `stop` ca rânduri și în meta.json

**Păstrat brut**

- fiecare linie trimisă de hook, integral, ca `text` sub tipul ei: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; o linie de alt tip sub `unknown`
- `d` (1 Hz, doar brut): LoGetSelfData integral (țara, coaliția, numele unității și grupului, nivelurile tipului, steaguri), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, vectorul vântului, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, balize radio, pauză, accelerarea timpului, locul, presiunea, abaterile - aplatizate în chei cu puncte
- `mis`: tabelul meteo al misiunii, aplatizat; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage cu argumentele lor

**Nedisponibil**

- alte unități (LoGetWorldObjects, LoGetObjectById) și date de senzori (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): nu sunt cerute - fiecare obiect al unei misiuni, la 10 Hz, costă mult în cadrul propriu al DCS, iar un server le restricționează (allow_object_export, allow_sensor_export); Tacview le înregistrează
- tabelul întreg al misiunii (DCS.getCurrentMission ține fiecare unitate și declanșator, megaocteți): se trimit doar data, ora de start, vremea, sortia, teatrul și versiunea
- callback-urile onPlayerTry\*: ele răspund DCS-ului (permit sau refuză), deci hook-ul nu se atinge de ele
- adresele și UCID-urile celorlalți jucători: net.get_player_info le dă doar unui server, iar ele nu sunt ale jucătorului ca să le păstreze
- intrările unui tabel peste 800 de chei sau peste 6 niveluri adâncime dintr-o linie `d` sunt tăiate, ca o linie să rămână un singur datagram

**Dimensiune**: aproximativ 20 MB pe oră pentru liniile `p` (10 pe secundă, circa 500 de octeți fiecare cu cadrul lor) și 15-40 MB pentru exporturile `d` (câte una pe secundă, 4-10 KB în funcție de încărcătura și ruta aeronavei), înainte de zstd; cheile care se repetă se comprimă de circa zece ori

## Verificat {#verified}

formatul liniilor testat cu datagrame sintetice; hook-ul Lua netestat în DCS (scris din API-ul hook/export al DCS și din lista funcțiilor Lo\* din Scripts\Export.lua, nerulat)

## Sursă {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
