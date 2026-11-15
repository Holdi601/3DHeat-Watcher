---
title: "DCS World (živé dáta)"
nav_order: 10
lang: "sk"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (živé dáta) {#dcs-world-live-data}

Keď hráte DCS World, watcher ukladá dáta, ktoré samotná hra vysiela, aby ste si ich neskôr mohli pozrieť na mape vo vieweri 3DHeat.

*Technické podrobnosti: adaptér `dcs`, druh [`telemetry`](sources-and-rules.md); beží, kým beží `DCS.exe`, a hľadá nové dáta každých 0,1 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- vlastná pozícia 10-krát za sekundu ako metre východ/výška/sever od počiatku dejiska (z zemepisnej šírky/dĺžky/výšky); zemepisná šírka, dĺžka a výška a svetové metre DCS (dcs_x sever, dcs_y hore, dcs_z východ) ako stĺpce
- postoj, indikovaná a skutočná rýchlosť, Mach, vertikálna rýchlosť, uhol náklonu a bočného sklzu, magnetický kurz, AGL a radarová výška, g na troch osiach, rýchlosť a rýchlosti otáčania, vo vzduchu, pozícia kamery a jej vektor pohľadu, typ lietadla
- vzlety a pristátia s letiskom; zrútenia, katapultáže, smrti pilota
- zabitia a zostrelenia s oboma typmi jednotiek a zbraňou; ďalšie herné udalosti podľa toho, ako sú dané
- životy na misiu (spawn ... session_end), zabitia, smrti, vzdialenosť, najvyššia výška, najvyššie g
- každý riadok, ktorý hook posiela, uchovaný celý v `heat.raw.parquet`, s výpisom tabuliek exportu lietadla raz za sekundu (motory, podvozok a klapky, náklad, protiopatrenia, trasa, navigácia) a každé ďalšie spätné volanie (pauza, chat, pripojenie hráčov, načítanie misie)

## Odkiaľ to pochádza {#where-it-comes-from}

skript hooku watchera %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, riadky UDP na 127.0.0.1:41993

## Ako to zapnúť {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (pridá Scripts\Hooks\heat3d-watch.lua), potom reštartujte DCS

Príkaz zadajte v termináli otvorenom v priečinku watchera (pozrite [Pred začiatkom](before-you-start.md)). Ak zlyhá, posledný riadok povie prečo; [Inštalácia a spustenie](installing-and-running.md) popisuje najčastejšie príčiny.

`python -m heat3d_watch setup dcs` vypíše, ktoré súbory by zmenil; `python -m heat3d_watch setup dcs --apply` ich zmení a pôvodný súbor uloží ako `<file>.heat3d-backup` (pozrite [Príkazy](commands.md#setup)). Pre každú zmenu vypíše `dcs: changed: ...`, alebo `dcs: nothing to change`, keď je to už zapnuté.

## Ako to funguje {#how-it-works}

DCS World: malý skript hooku watchera, ktorý posiela riadky UDP na 127.0.0.1:41993.

DCS pri štarte spúšťa súbory Lua v `Saved Games\DCS*\Scripts\Hooks\`; hook môže čítať exportné funkcie (`Export.Lo*`) a prijímať spätné volania simulácie (`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) – pozrite `<DCS>\API\DCS_ControlAPI.html` a <https://wiki.hoggitworld.com/view/DCS_Export_Script>. `setup` tam zapíše `heat3d-watch.lua` (je to vlastný súbor: Export.lua a hooky iných nástrojov sa nedotknú). Posiela desať riadkov za sekundu, ešte jeden za sekundu a jeden za každú hernú udalosť alebo spätné volanie, nikdy nečaká na odpoveď. Port je 41993, aby JoyPro (41992) a Tacview (42674) fungovali vedľa neho. Riadky (polia oddelené ';'):

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

`p` je LoGetSelfData: Position x/y/z – svetové metre DCS, x sever, y hore, z východ – plus LatLongAlt (stupne, m), Heading/Pitch/Bank (radiány), s LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) a LoGetAccelerationUnits() x/y/z (g); a, ako to uvádza `Scripts\Export.lua`, LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s), LoGetAngleOfAttack a LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad), LoGetRadarAltimeter (m), LoGetVectorVelocity (svetová rýchlosť m/s), LoGetAngularVelocity (rad/s), LoGetInAir a bod a vektor pohľadu z LoGetCameraPosition (svetové metre). `d` je raz za sekundu výpis celých tabuliek, sploštených do bodkovaných kľúčov: LoGetSelfData (krajina, koalícia, názvy jednotky a skupiny, úrovne typu, príznaky), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus a niekoľko čísel (pauza, zrýchlenie času, sedadlo, tlak, odchýlky). Watcher uchová každý riadok celý v surovom sprievodnom súboree; `p` sa stáva aj riadkami.

Pozície idú do rovnakej plochej mapy ako pri ostatných leteckých simuláciách (`Tangent`: x východ, y výška nad morom, z sever, metre) z LatLongAlt, okolo pevného počiatku dejiska (`THEATRES`, z `map` štartovného riadku), takže každá misia na jednom dejisku zdieľa jednu mapu a viewer na ňu môže položiť skutočný svet. Dejisko, ktoré nie je v tabuľke, použije zemepisnú šírku a dĺžku prvého údaja zaokrúhlenú na celé stupne. DCS-ové x/y/z sa ukladajú ako `dcs_x`, `dcs_y`, `dcs_z`; údaj bez LatLongAlt sa nedá umiestniť a len sa počíta (`fixes_without_latlon`). Počiatok je `geo` relácie v meta.json a päte tabuľky.

Argumenty onGameEvent, tak ako ich dáva DCS_ControlAPI: takeoff/landing (playerID, unit_missionID, airdromeName), crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID, killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide, weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide), mission_end (winner, msg).

Viachráčový server môže zakázať export vlastnej lode (LoIsOwnshipExportAllowed je false); potom nie sú pozície, len udalosti, a relácia to hovorí.

## Pozície a osi {#positions-and-axes}

| | |
|---|---|
| Pozície sa zaznamenávajú | áno |
| Os nahor | `y` |
| Jednotky | metre (východ, výška, sever od počiatku dejiska) |
| Zrkadlené pre viewer | `z` |
| Mierka (`scale`: viewer pozície násobí týmto číslom) | 1 |

Tieto hodnoty idú do `meta.json` každej relácie (`axes`) a, ak relácia obsahuje pozície, do päty `heat.parquet`, takže viewer 3DHeat riadky otáča a mení mierku sám – pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hraná online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)“.
- Druh `telemetry`: číta len to, čo hra alebo platforma vydáva (UDP port alebo zdieľaná pamäť, ktorú hra zverejňuje), takže zaznamenáva aj online hru, aj offline; príznak rozhoduje len o tom, či sa smie čítať pamäť.
- Pamäť: tento adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry `memory` a nikdy pre hru označenú ako hranú online – pozrite [Pravidlá a zdroje](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Štatistické kľúče, ktoré kód tohto adaptéra nastavuje podľa názvu (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

Kľúč v zložených zátvorkách sa doplní až za behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z vlastných názvov štatistík hry, v tomto zozname nie sú; „Čo sa zaznamenáva“ vyššie ich uvádza.

## Úplnosť {#completeness}

Watcher sa riadi [pravidlom konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: čo zdroj obsahuje, sa prečíta alebo uchová, nikdy sa nezahodí. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celý v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a potom každé pole, ktoré sa podľa názvu ponechalo; `used` označuje, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` – `lost` je 0.

**Prečítané**

- `p` (10 Hz): pozícia, LatLongAlt, postoj, IAS, AGL, g (x/y/z), typ lietadla, a z hooku 2 TAS, Mach, vertikálna rýchlosť, uhol náklonu, uhol bočného sklzu, magnetický kurz, radarová výška, svetová rýchlosť, rýchlosti otáčania, vo vzduchu a bod a vektor pohľadu kamery – všetko ako stĺpce riadkov (jednotky tak, ako ich dáva Export.lua)
- `start`: misia, dejisko, vlastné id a meno hráča, viacráčová hra, súbor misie, server; `mis`: dátum misie a čas začiatku do meta.json
- `ev`: každý onGameEvent ako riadok (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, každý ďalší názov tak, ako prišiel)
- `noexport` a `stop` ako riadky a v meta.json

**Uchované surové**

- každý riadok, ktorý hook posiela, celý, ako `text` pod jeho druhom: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; riadok iného druhu pod `unknown`
- `d` (1 Hz, len surové): LoGetSelfData celé (krajina, koalícia, názov jednotky a skupiny, úrovne typu, príznaky), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, vektor vetra, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, rádiové majáky, pauza, zrýchlenie času, sedadlo, tlak, odchýlky – sploštené do bodkovaných kľúčov
- `mis`: tabuľka počasia misie, sploštená; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage s ich argumentmi

**Nie je k dispozícii**

- ostatné jednotky (LoGetWorldObjects, LoGetObjectById) a údaje senzorov (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): nevyžadujú sa – každý objekt misie 10-krát za sekundu je pri vnútornom rámci DCS drahý a server ich blokuje (allow_object_export, allow_sensor_export); Tacview ich zaznamenáva
- celá tabuľka misie (DCS.getCurrentMission obsahuje každú jednotku a spúšťač, megabajty): posielajú sa len dátum, čas začiatku, počasie, sortie, dejisko a verzia
- spätné volania onPlayerTry\*: odpovedajú DCS (povoliť alebo odmietnuť), takže ich hook nechá na pokoji
- adresy iných hráčov a UCID: net.get_player_info ich dáva len serveru a nie sú hráčovou vecou, aby si ich ponechal
- položky tabuliek nad 800 kľúčov alebo nad 6 úrovní do hĺbky v jednom riadku `d` sa odrežú, aby jeden riadok zostal jedným datagramom

**Veľkosť**: asi 20 MB za hodinu riadkov `p` (10 za sekundu, asi 500 bajtov každý s rámcom) a 15–40 MB výpisov `d` (jeden za sekundu, 4–10 KB podľa nákladu a trasy lietadla), pred zstd; opakujúce sa kľúče sa stlačia asi desaťnásobne

## Overené {#verified}

formát riadkov testovaný na syntetických datagramoch; Lua hook netestovaný v DCS (napísaný podľa API hookov DCS a zoznamu funkcií Lo\* v Scripts\Export.lua, nespustený)

## Zdroj {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
