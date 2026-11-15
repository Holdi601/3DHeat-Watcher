---
title: "DCS World (lifandi gögn)"
nav_order: 10
lang: "is"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (lifandi gögn) {#dcs-world-live-data}

Meðan þú spilar DCS World vistar watcher gögnin sem leikurinn sendir sjálfur út, svo þú getir skoðað þau síðar á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `dcs`, gerð [`telemetry`](sources-and-rules.md); það keyrir meðan `DCS.exe` er í gangi og leitar að nýjum gögnum á 0,1 s fresti.*

## Hvað er skráð {#what-is-recorded}

- eigin staða á 10 Hz sem metrar austur/upp/norður af upphafspunkti sviðsins (úr breiddar-/lengdargráðu/hæð); lat/lon/alt og eigin heimsmetrar DCS (dcs_x norður, dcs_y upp, dcs_z austur) sem dálkar
- afstaða, ábendur og sannur lofthraði, Mach, lóðréttur hraði, árásarhorn og hliðarskrið, segulstefna, hæð yfir jörðu (AGL) og ratsjárhæð, g á þremur ásum, hraði og snúningshraði, í lofti, staða og framvísunarvektor myndavélarinnar, gerð loftfars
- flugtök og lendingar með flugvellinum; brotlendingar, útkast, dauðsföll flugmanns
- dráp og það að vera skotinn niður, með báðum einingagerðum og vopninu; aðrir leikatburðir eins og þeir berast
- líf í hverju verkefni (spawn ... session_end), dráp, dauðsföll, vegalengd, mesta hæð, mesta g
- hver lína sem krókurinn sendir geymd í heild í heat.raw.parquet, ásamt útskrift einu sinni á sekúndu af útflutningstöflum loftfarsins (hreyflar, lendingarbúnaður og vængbörð, farmur, mótvægisaðgerðir, leið, leiðsögn) og öllum öðrum köllum (hlé, spjall, spilarar sem tengjast, hleðsla verkefnis)

## Hvaðan það kemur {#where-it-comes-from}

krókur watcher, %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, UDP-línur á 127.0.0.1:41993

## Hvernig á að kveikja á því {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (bætir við Scripts\Hooks\heat3d-watch.lua), endurræstu síðan DCS

Sláðu skipunina inn í terminal sem er opnaður í möppu watcher (sjá [Áður en þú byrjar](before-you-start.md)). Ef hún mistekst segir síðasta línan hvers vegna; [Uppsetning og keyrsla](installing-and-running.md) fer yfir algengustu orsakirnar.

`python -m heat3d_watch setup dcs` sýnir þær skrár sem það myndi breyta; `python -m heat3d_watch setup dcs --apply` breytir þeim og geymir frumritið sem `<file>.heat3d-backup` (sjá [Skipanir](commands.md#setup)). Það skrifar `dcs: changed: ...` fyrir hverja breytingu, eða `dcs: nothing to change` þegar kveikt er nú þegar.

## Hvernig það virkar {#how-it-works}

DCS World: lítið króka-skrifta watcher sjálfs sem sendir UDP-línur á 127.0.0.1:41993.

DCS keyrir Lua-skrár í `Saved Games\DCS*\Scripts\Hooks\` við ræsingu; krókur getur
lesið útflutningsföllin (`Export.Lo*`) og tekið við köllum hermisins
(`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - sjá
`<DCS>\API\DCS_ControlAPI.html` og <https://wiki.hoggitworld.com/view/DCS_Export_Script>.
`setup` skrifar `heat3d-watch.lua` þangað (þetta er hans eigin skrá: Export.lua og krókar
annarra verkfæra eru ekki snertir), og hún sendir tíu línur á sekúndu, eina í viðbót á
sekúndu, og eina fyrir hvern leikatburð eða kall, og bíður aldrei eftir svari.
Gáttin er 41993 svo krókur JoyPro (41992) og Tacview (42674) haldi áfram að virka
við hlið hans. Línurnar (reitir aðskildir með ';'):

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

`p` er LoGetSelfData: Position x/y/z - eigin heimsmetrar DCS, x norður, y upp,
z austur - auk LatLongAlt (gráður, m), Heading/Pitch/Bank (radíanar), með
LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) og
LoGetAccelerationUnits() x/y/z (g); og, eins og `Scripts\Export.lua` lýsir
þeim, LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s),
LoGetAngleOfAttack og LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad),
LoGetRadarAltimeter (m), LoGetVectorVelocity (heims-m/s), LoGetAngularVelocity
(rad/s), LoGetInAir, og punktur og framvísunarvektor LoGetCameraPosition (heims-
metrar). `d` er útskrift einu sinni á sekúndu af heilum töflum, flatt út í lykla með punktum:
LoGetSelfData (land, bandalag, heiti eininga og hópa, gerðastig, merki),
LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo,
LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute,
LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus og nokkrar
tölur (hlé, tímahröðun, sæti, loftþrýstingur, frávik). Watcher
geymir hverja línu í heild í hráu hliðarskránni; `p` verður líka að röðum.

Staðsetningar fara í sama flata kortið og hjá hinum flughermunum (`Tangent`: x
austur, y hæð yfir sjávarmáli, z norður, metrar) út frá LatLongAlt, í kringum
fastan upphafspunkt sviðsins (`THEATRES`, úr `map` í start-línunni), svo hvert
verkefni á einu sviði deilir einu korti, og korti sem skoðarinn getur lagt
raunheiminn undir. Svið sem er ekki í töflunni fær breiddar- og lengdargráðu
fyrstu mælingar, rúnnaða í heilar gráður. Eigin x/y/z DCS eru geymd sem `dcs_x`,
`dcs_y`, `dcs_z`; mælingu án LatLongAlt er ekki hægt að staðsetja og hún er aðeins
talin (`fixes_without_latlon`). Upphafspunkturinn er `geo` lotunnar, í
meta.json og fæti töflunnar.

Rök onGameEvent, eins og DCS_ControlAPI
gefur þau: takeoff/landing (playerID, unit_missionID, airdromeName),
crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID,
killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide,
weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide),
mission_end (winner, msg).

Fjölspilunarþjónn getur bannað útflutning eigin loftfars (LoIsOwnshipExportAllowed er
false); þá eru engar staðsetningar, aðeins atburðir, og lotan segir frá því.

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | já |
| Upp-ás | `y` |
| Einingar | metrar (austur, hæð, norður frá upphafspunkti sviðsins) |
| Speglað fyrir skoðarann | `z` |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` (`axes`) hverrar lotu og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem "allowed (reads only what the game publishes)".
- Gerð `telemetry`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (UDP-gátt eða samnýtt minni sem leikurinn birtir), svo það skráir bæði í netspilun og án nets; merkið ræður aðeins hvort minni megi nokkurn tíma lesa.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

Lykill í slaufusvigum er fylltur út við keyrslu (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; "Hvað er skráð" hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [breytireglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er hver pakki, síða, lína eða svar sem millistykkið fær geymt í heild í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, svo hver reitur sem geymdur er með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hvert `type` - `lost` er 0.

**Lesið**

- `p` (10 Hz): staða, LatLongAlt, afstaða, IAS, AGL, g (x/y/z), gerð loftfars, og TAS, Mach, lóðréttur hraði, AoA, hliðarskrið, segulstefna, ratsjárhæð, heimshraði, snúningshraði, í lofti og punktur/framvísunarvektor myndavélar frá króki 2 - allt sem dálkar raðanna (einingar eins og Export.lua gefur þær)
- `start`: verkefni, svið, eigið spilaraauðkenni og nafn, fjölspilun, verkefnaskrá, þjónn; `mis`: dagsetning og upphafstími verkefnisins í meta.json
- `ev`: hver onGameEvent sem röð (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, hvert annað heiti eins og það er gefið)
- `noexport` og `stop` sem raðir og í meta.json

**Geymt óunnið**

- hver lína sem krókurinn sendir, í heild, sem `text` undir sinni gerð: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; lína af annarri gerð undir `unknown`
- `d` (1 Hz, aðeins óunnið): LoGetSelfData í heild (land, bandalag, heiti einingar og hóps, gerðastig, merki), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, vindvektor, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, radíóvitar, hlé, tímahröðun, sæti, loftþrýstingur, frávik - flatt út í lykla með punktum
- `mis`: veðurtafla verkefnisins, flött út; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage með rökum sínum

**Ekki tiltækt**

- aðrar einingar (LoGetWorldObjects, LoGetObjectById) og skynjaragögn (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): ekki beðið um - að sækja alla hluti verkefnis á 10 Hz er dýrt innan ramma DCS sjálfs, og þjónn getur lokað á þá (allow_object_export, allow_sensor_export); Tacview skráir þá
- öll verkefnistaflan (DCS.getCurrentMission geymir hverja einingu og kveikju, megabæti): aðeins dagsetning, upphafstími, veður, sortie, svið og útgáfa eru send
- onPlayerTry\*-köllin: þau svara DCS (leyfa eða hafna), svo krókurinn lætur þau í friði
- heimilisföng og UCID annarra spilara: net.get_player_info gefur þau aðeins þjóni, og spilarinn á þau ekki til að geyma
- færslur töflu umfram 800 lykla eða 6 stig á dýpt í einni `d`-línu eru skornar af, svo ein lína haldist ein gagnaeining (datagram)

**Stærð**: um 20 MB á klukkustund af `p`-línum (10 á sekúndu, um 500 bæti hver með ramma sínum) og 15-40 MB af `d`-útskriftum (ein á sekúndu, 4-10 KB eftir farmi og leið loftfarsins), fyrir zstd; endurteknu lyklarnir þjappast um tífalt

## Staðfest {#verified}

línusnið prófað með tilbúnum datagrömmum; Lua-krókurinn er óprófaður inni í DCS (skrifaður út frá hook-/export-API DCS og lista Scripts\Export.lua yfir Lo\*-föll, ekki keyrður)

## Heimild {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
