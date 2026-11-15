---
title: "DCS World (live data)"
nav_order: 10
lang: "sl"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (live data) {#dcs-world-live-data}

Medtem ko igrate DCS World, watcher shrani podatke, ki jih igra sama pošilja ven, da jih lahko pozneje pogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `dcs`, vrsta [`telemetry`](sources-and-rules.md); teče, dokler je `DCS.exe` zagnan, in novih podatkov išče vsakih 0,1 s.*

## Kaj se zapiše {#what-is-recorded}

- lastni položaj 10-krat na sekundo kot metri vzhodno/navzgor/severno od izhodišča gledališča (iz zemljepisne širine/dolžine/višine); zemljepisna širina/dolžina/višina in lastni svetovni metri DCS (dcs_x sever, dcs_y gor, dcs_z vzhod) kot stolpci
- lega, indicirana in dejanska hitrost, Mach, vertikalna hitrost, napadni kot in zdrs, magnetni smerni kot, AGL in radarska višina, g na treh oseh, hitrost in hitrosti vrtenja, v zraku, položaj kamere in njen vektor pogleda, tip letala
- vzleti in pristanki z letališčem; trki, katapultiranja, smrti pilotov
- pobitja in sestrelitve z obema tipoma enot in orožjem; drugi dogodki igre, kakor so podani
- življenja na misijo (spawn ... session_end), pobitja, smrti, razdalja, največja višina, največ g
- vsaka vrstica, ki jo pošlje hook, ohranjena v celoti v `heat.raw.parquet`, z enkrat-na-sekundo izpisom tabel izvoza letala (motorji, podvozje in zakrilca, tovor, protiukrepi, pot, navigacija) in vsakim drugim povratnim klicem (pavza, klepet, igralci, ki se pridružijo, nalaganje misije)

## Od kod prihaja {#where-it-comes-from}

hook watcherja %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, UDP vrstice na 127.0.0.1:41993

## Kako ga vklopiti {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (doda Scripts\Hooks\heat3d-watch.lua), nato znova zaženite DCS

Ukaz vpišite v terminal, odprt v mapi watcherja (glej [Preden začnete](before-you-start.md)). Če ne uspe, zadnja vrstica pove, zakaj; [Namestitev in zagon](installing-and-running.md) pokrije pogoste vzroke.

`python -m heat3d_watch setup dcs` izpiše, katere datoteke bi spremenil; `python -m heat3d_watch setup dcs --apply` jih spremeni, izvirnik pa ohrani kot `<file>.heat3d-backup` (glej [Ukazi](commands.md#setup)). Za vsako spremembo izpiše `dcs: changed: ...`, ali `dcs: nothing to change`, kadar je že vklopljeno.

## Kako deluje {#how-it-works}

DCS World: majhen skript hooka watcherja, ki pošilja UDP vrstice na 127.0.0.1:41993.

DCS ob zagonu požene datoteke Lua v `Saved Games\DCS*\Scripts\Hooks\`; hook lahko bere funkcije izvoza (`Export.Lo*`) in prejema povratne klice simulacije (`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - glej `<DCS>\API\DCS_ControlAPI.html` in <https://wiki.hoggitworld.com/view/DCS_Export_Script>. `setup` ga zapiše tja v svojo datoteko `heat3d-watch.lua` (Export.lua in hooki drugih orodij se ne dotaknejo); ta pošilja deset vrstic na sekundo, še eno na sekundo in eno za vsak dogodek igre ali povratni klic, nikoli ne čaka na odgovor. Vrata so 41993, da JoyPro hook (41992) in Tacview (42674) delujeta poleg njega. Vrstice (polja, ločena s ';'):

```text
hello;v=2                                       hook je naložen
start;mission=..;map=..;me=<player id>;name=..;mp=0|1;file=..;server=0|1
mis;t=..;date.Day=..;start_time=..;weather...   datum misije, začetni čas in vreme, sploščeno
p;t=<model s>;x=;y=;z=;lat=;lon=;alt=;hdg=;pitch=;bank=;ias=;agl=;g=;type=;tas=;mach=;vv=;aoa=;aos=;
  mhdg=;ralt=;gx=;gz=;vx=;vy=;vz=;wx=;wy=;wz=;air=;cx=;cy=;cz=;cfx=;cfy=;cfz=
d;t=..;self.Name=..;eng.RPM.left=..;mech.gear.value=..;pay.Stations.1.count=..;...   enkrat na sekundo
ev;t=..;name=<onGameEvent name>;args=a|b|c      vsak onGameEvent
cb;t=..;name=<callback>;args=a|b                vsak drug povratni klic (pavza, klepet, igralci, nalaganje)
noexport;t=..                                   strežnik prepove izvoz lastnega letala
stop;t=..                                       misija se je končala
```

`p` je LoGetSelfData: Position x/y/z - lastni svetovni metri DCS, x sever, y gor, z vzhod - plus LatLongAlt (stopinje, m), Heading/Pitch/Bank (radiani), z LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) in LoGetAccelerationUnits() x/y/z (g); ter, kakor jih dokumentira `Scripts\Export.lua`, LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s), LoGetAngleOfAttack in LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad), LoGetRadarAltimeter (m), LoGetVectorVelocity (svetovne m/s), LoGetAngularVelocity (rad/s), LoGetInAir ter točko in vektor pogleda LoGetCameraPosition (svetovni metri). `d` je enkrat na sekundo izpis celih tabel, sploščenih v pike: LoGetSelfData (država, koalicija, imena enote in skupine, stopnje tipa, zastavice), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus in nekaj številk (pavza, pospešek časa, sedež, tlak, odkloni). Watcher hrani vsako vrstico v celoti v surovi spremljevalni datoteki; `p` postane tudi vrstice.

Položaji gredo v isti ravni zemljevid kot pri drugih letalskih simulatorjih (`Tangent`: x vzhod, y višina nad morsko gladino, z sever, metri), iz LatLongAlt, okoli fiksnega izhodišča gledališča (`THEATRES`, iz `map` začetne vrstice), zato vsaka misija na enem gledališču deli eno karto, na katero lahko pregledovalnik položi pravi svet. Gledališče, ki ni v tabeli, vzame zemljepisno širino in dolžino prve meritve, zaokroženo na cele stopinje. Lastni x/y/z DCS se ohranijo kot `dcs_x`, `dcs_y`, `dcs_z`; meritev brez LatLongAlt ni mogoče postaviti in se samo šteje (`fixes_without_latlon`). Izhodišče je `geo` seje, v meta.json in nogi tabele.

Argumenti onGameEvent, kakor jih daje DCS_ControlAPI: takeoff/landing (playerID, unit_missionID, airdromeName), crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID, killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide, weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide), mission_end (winner, msg).

Strežnik z več igralci lahko prepove izvoz lastnega letala (LoIsOwnshipExportAllowed je false); tedaj ni položajev, samo dogodki, in seja to pove.

## Osi položajev {#positions-and-axes}

| | |
|---|---|
| Zapisani položaji | da |
| Os navzgor | `y` |
| Enote | metri (vzhod, višina, sever od izhodišča gledališča) |
| Zrcaljeno za pregledovalnik | `z` |
| Merilo enot (`scale`: pregledovalnik položaje pomnoži z njim) | 1 |

Ti gredo v `meta.json` vsake seje (`axes`) in, kadar ima seja položaje, v nogo `heat.parquet`, tako pregledovalnik sam obrača in meri vrstice - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igrano na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `telemetry`: bere samo to, kar igra ali platforma objavi (vrata UDP ali deljeni pomnilnik, ki ju igra objavlja), zato zapisuje tudi pri igri na spletu, tako kot offline; zastavica odloča samo, ali sme kdaj brati pomnilnik.
- Pomnilnik: tega adapterja **nikoli** ne bere. Pomnilnik berejo samo adapterji `memory`, in nikoli za igro, označeno kot igrano na spletu - glej [Viri in pravila](sources-and-rules.md).

## Statistike {#statistics-recorded}

Ključi statistik, ki jih koda tega adapterja nastavi po imenu (`stats` vsake seje v `meta.json` in tabela `stats` v `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

Ključ v zavitih oklepajih se dokonča med delovanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz lastnih imen statistik igre, na tem seznamu niso; "Kaj se zapiše" zgoraj jih navaja.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir vsebuje, se prebere ali ohrani, nikoli ne izpusti. Poleg vrstic je vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, ohranjen v celoti v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text`, nato vsako polje, ohranjeno po imenu; `used` označi, kar je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- `p` (10 Hz): položaj, LatLongAlt, lega, IAS, AGL, g (x/y/z), tip letala ter TAS, Mach, vertikalna hitrost, napadni kot, zdrs, magnetni smerni kot, radarska višina, svetovna hitrost, hitrosti vrtenja, v zraku in točka/vektor pogleda kamere iz hooka 2 - vse kot stolpci vrstic (enote, kakor jih daje Export.lua)
- `start`: misija, gledališče, lastni ID in ime igralca, več igralcev, datoteka misije, strežnik; `mis`: datum in začetni čas misije v meta.json
- `ev`: vsak onGameEvent kot vrstica (vzlet, pristanek, trk, katapultiranje, smrt pilota, pobitje, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, vsako drugo ime, kakor je podano)
- `noexport` in `stop` kot vrstici in v meta.json

**Ohranjeno surovo**

- vsaka vrstica, ki jo pošlje hook, v celoti, kot `text` pod svojo vrsto: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; vrstica katere koli druge vrste pod `unknown`
- `d` (1 Hz, samo surovo): LoGetSelfData v celoti (država, koalicija, ime enote in skupine, stopnje tipa, zastavice), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, vektor vetra, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, radijski svetilniki, pavza, pospešek časa, sedež, tlak, odkloni - sploščeno v pikasta imena ključev
- `mis`: tabela vremena misije, sploščena; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage z njihovimi argumenti

**Ni na voljo**

- druge enote (LoGetWorldObjects, LoGetObjectById) in podatki tipal (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): ne zahtevajo se - vsak objekt misije na 10 Hz je v okviru DCS drag, strežnik pa jih omejuje (allow_object_export, allow_sensor_export); Tacview jih zapisuje
- cela tabela misije (DCS.getCurrentMission hrani vsako enoto in sprožilec, več megabajtov): pošljejo se samo njen datum, začetni čas, vreme, sortie, gledališče in različica
- povratni klici onPlayerTry\*: odgovarjajo DCS (dovoli ali zavrne), zato jih hook pusti pri miru
- naslovi drugih igralcev in UCID-ji: net.get_player_info jih da samo strežniku, in niso igralčevi, da bi jih hranil
- vnosi tabele čez 800 ključev ali 6 nivojev globoko v eni vrstici `d` se odrežejo, da ena vrstica ostane en datagram

**Velikost**: okoli 20 MB na uro vrstic `p` (10 na sekundo, okoli 500 bajtov vsaka z okvirom) in 15-40 MB izpisov `d` (en na sekundo, 4-10 KB glede na tovor in pot letala), pred zstd; ponovljeni ključi se stisnejo okoli desetkrat

## Preverjeno {#verified}

oblika vrstic preizkušena s sintetičnimi datagrami; Lua hook je nepreizkušen znotraj DCS (napisan iz API-ja DCS hook/export in seznama funkcij Lo\* v `Scripts\Export.lua`, ni bil zagnan)

## Vir {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
