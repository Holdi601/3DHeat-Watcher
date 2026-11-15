---
title: "DCS World (živá data)"
nav_order: 10
lang: "cs"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (živá data) {#dcs-world-live-data}

Když hrajete DCS World, Watcher ukládá data, která samotná hra vysílá, abyste se na ně mohli později podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `dcs`, druh [`telemetry`](sources-and-rules.md); běží, dokud běží `DCS.exe`, a hledá nová data každých 0,1 s.*

## Co se zaznamenává {#what-is-recorded}

- vlastní pozice 10krát za sekundu jako metry na východ/nahoru/na sever od počátku mapy (z zeměpisné šířky/délky/výšky); zeměpisná šířka/délka/výška a světové metry DCS (dcs_x sever, dcs_y nahoru, dcs_z východ) jako sloupce
- orientace, indikovaná a pravá rychlost vzduchem, Mach, vertikální rychlost, úhel náběhu a skluzu, magnetický kurz, AGL a radarová výška, g ve třech osách, rychlost a rychlosti otáčení, ve vzduchu, pozice kamery a směr jejího pohledu, typ letadla
- vzlety a přistání s letištěm; havárie, katapultáže, smrti pilotů
- zabití a sestřelení s oběma typy jednotek a zbraní; ostatní herní události, jak jsou dány
- životy na misi (spawn ... session_end), zabití, smrti, vzdálenost, nejvyšší výška, nejvyšší g
- každý řádek, který hook posílá, uchovaný celý v heat.raw.parquet, s jednou za sekundu výpisem exportních tabulek letadla (motory, podvozek a klapky, náklad, protiopatření, trasa, navigace) a každým dalším zpětným voláním (pauza, chat, připojení hráčů, načítání mise)

## Odkud to pochází {#where-it-comes-from}

hook Watcheru %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, řádky UDP na 127.0.0.1:41993

## Jak to zapnout {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (přidá Scripts\Hooks\heat3d-watch.lua), potom DCS restartujte

Příkaz napište do terminálu otevřeného ve složce Watcheru (viz [Než začnete](before-you-start.md)). Pokud selže, poslední řádek vysvětlí proč; [Instalace a spuštění](installing-and-running.md) popisuje obvyklé příčiny.

`python -m heat3d_watch setup dcs` vypíše soubory, které by změnil; `python -m heat3d_watch setup dcs --apply` je změní a původní soubor ponechá jako `<file>.heat3d-backup` (viz [Příkazy](commands.md#setup)). Pro každou změnu vypíše `dcs: changed: ...`, nebo `dcs: nothing to change`, když je to už zapnuté.

## Jak to funguje {#how-it-works}

DCS World: malý hook skript Watcheru, který posílá řádky UDP na 127.0.0.1:41993.

DCS při startu spouští soubory Lua ve složce `Saved Games\DCS*\Scripts\Hooks\`; hook může číst exportní funkce (`Export.Lo*`) a přijímat zpětná volání simulace (`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) – viz `<DCS>\API\DCS_ControlAPI.html` a <https://wiki.hoggitworld.com/view/DCS_Export_Script>. `setup` tam zapíše soubor `heat3d-watch.lua` (vlastní soubor: Export.lua a hooky jiných nástrojů se nedotknou). Ten posílá deset řádků za sekundu, jeden navíc za sekundu a jeden za každou herní událost nebo zpětné volání, a nikdy nečeká na odpověď. Port je 41993, aby JoyPro (41992) a Tacview (42674) fungovaly vedle něj. Řádky (pole oddělená ';'):

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

`p` je LoGetSelfData: Position x/y/z – světové metry DCS, x sever, y nahoru, z východ – plus LatLongAlt (stupně, m), Heading/Pitch/Bank (radiány), s LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) a LoGetAccelerationUnits() x/y/z (g); a jak je popisuje `Scripts\Export.lua`, LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s), LoGetAngleOfAttack a LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad), LoGetRadarAltimeter (m), LoGetVectorVelocity (světové m/s), LoGetAngularVelocity (rad/s), LoGetInAir a bod a směrový vektor z LoGetCameraPosition (světové metry). `d` je jednou za sekundu výpis celých tabulek zploštěných na tečkované klíče: LoGetSelfData (země, koalice, jména jednotky a skupiny, úrovně typu, příznaky), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus a několik čísel (pauza, zrychlení času, sedadlo, tlak, odchylky). Watcher uchovává každý řádek celý ve vedlejším surovém souboru; `p` se také stane řádky.

Pozice jdou do stejné ploché mapy jako u ostatních leteckých simulátorů (`Tangent`: x východ, y výška nad hladinou moře, z sever, metry) z LatLongAlt, kolem pevného počátku divadla (`THEATRES`, z `map` startovního řádku), takže každá mise na jednom divadle sdílí jednu mapu, pod kterou může prohlížeč položit skutečný svět. Divadlo, které v tabulce není, vezme zeměpisnou šířku a délku prvního určení zaokrouhlenou na celé stupně. DCS x/y/z se uchovají jako `dcs_x`, `dcs_y`, `dcs_z`; určení bez LatLongAlt nejde umístit a počítá se jen jako `fixes_without_latlon`. Počátek je `geo` relace, v meta.json a v patičce tabulky.

Argumenty onGameEvent podle DCS_ControlAPI: takeoff/landing (playerID, unit_missionID, airdromeName), crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID, killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide, weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide), mission_end (winner, msg).

Server s více hráči může zakázat export vlastního letadla (LoIsOwnshipExportAllowed je false); pak nejsou žádné pozice, jen události, a relace to řekne.

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `y` |
| Jednotky | metry (východ, výška, sever od počátku divadla) |
| Zrcadleno pro prohlížeč | `z` |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto hodnoty se zapisují do `meta.json` každé relace (`axes`) a, když relace má pozice, do patičky `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítkuje řádky sám – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukáže jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `telemetry`: čte jen to, co hra nebo platforma vydává (UDP port nebo sdílená paměť, kterou hra zveřejňuje), takže nahrává i v online hře, stejně jako offline; příznak rozhoduje jen o tom, zda se smí číst paměť.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry `memory` a nikdy u hry označené jako hraná online – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle jména (každé relace `stats` v `meta.json` a tabulka `stats` v `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč na každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedené jménem.

## Úplnost {#completeness}

Watcher dodržuje [pravidlo převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co zdroj obsahuje, se načte nebo uchová, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, kterou adaptér dostane, uchovává celý v `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uchovaná podle jména; `used` označuje, co se také stalo řádky), a `selfCheck.completeness` v `meta.json` počítá každý `type` – `lost` je 0.

**Načteno**

- `p` (10 Hz): pozice, LatLongAlt, orientace, IAS, AGL, g (x/y/z), typ letadla, a z hooku 2 TAS, Mach, vertikální rychlost, AoA, skluz, magnetický kurz, radarová výška, světová rychlost, rychlosti otáčení, ve vzduchu a bod/směr pohledu kamery – vše jako sloupce řádků (jednotky, jak je dává Export.lua)
- `start`: mise, divadlo, vlastní id a jméno hráče, více hráčů, soubor mise, server; `mis`: datum a čas začátku mise do meta.json
- `ev`: každý onGameEvent jako řádek (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, jakékoli jiné jméno, jak je dané)
- `noexport` a `stop` jako řádky a v meta.json

**Uchováno surové**

- každý řádek, který hook posílá, celý, jako `text` pod svým druhem: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; řádek jakéhokoli jiného druhu pod `unknown`
- `d` (1 Hz, jen surově): LoGetSelfData celá (země, koalice, jméno jednotky a skupiny, úrovně typu, příznaky), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, vektor větru, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, rádiové majáky, pauza, zrychlení času, sedadlo, tlak, odchylky – zploštěné na tečkované klíče
- `mis`: tabulka počasí mise, zploštěná; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage s jejich argumenty

**Nedostupné**

- ostatní jednotky (LoGetWorldObjects, LoGetObjectById) a data senzorů (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): nevyžádáno – každý objekt mise 10krát za sekundu je uvnitř rámce DCS drahý a server je omezuje (allow_object_export, allow_sensor_export); Tacview je zaznamenává
- celá tabulka mise (DCS.getCurrentMission drží každou jednotku a spoušť, megabajty): posílají se jen datum, čas začátku, počasí, sortie, divadlo a verze
- zpětná volání onPlayerTry\*: odpovídají DCS (povolit nebo odmítnout), takže hook je nechává být
- adresy ostatních hráčů a UCID: net.get_player_info je dá jen serveru a nejsou k uchování pro hráče
- položky tabulky nad 800 klíčů nebo hlouběji než 6 úrovní v jednom řádku `d` se ořežou, aby jeden řádek zůstal jedním datagramem

**Velikost**: asi 20 MB za hodinu řádků `p` (10 za sekundu, asi 500 bajtů každý i s rámcem) a 15–40 MB výpisů `d` (jeden za sekundu, 4–10 KB podle nákladu a trasy letadla), před zstd; opakované klíče se stlačí zhruba desetkrát

## Ověřeno {#verified}

formát řádků testován syntetickými datagramy; Lua hook neotestován uvnitř DCS (napsán z API hooků a exportu DCS a ze seznamu funkcí Lo* v Scripts\Export.lua, nespuštěn)

## Zdroj {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte ho znovu, místo úprav této stránky. -->
