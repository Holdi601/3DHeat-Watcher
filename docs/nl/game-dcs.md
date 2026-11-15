---
title: "DCS World (live data)"
nav_order: 10
lang: "nl"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (live data) {#dcs-world-live-data}

Terwijl je DCS World speelt, slaat de watcher de data op die het spel zelf uitstuurt. Zo kun je die later op een kaart in de 3DHeat-viewer bekijken.

*Technische details: adapter `dcs`, soort [`telemetry`](sources-and-rules.md); hij draait zolang `DCS.exe` actief is en zoekt elke 0,1 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- eigen positie tien keer per seconde, in meters oost/omhoog/noord van de oorsprong van het theater (uit breedtegraad/lengtegraad/hoogte); lat/lon/alt en de eigen wereldmeters van DCS (dcs_x noord, dcs_y omhoog, dcs_z oost) als kolommen
- houding, aangegeven en echte vliegsnelheid, Mach, verticale snelheid, invalshoek en sliphoek, magnetische koers, AGL en radarhoogte, g op drie assen, snelheid en draaisnelheden, in de lucht, de positie en voorwaartse vector van de camera, vliegtuigtype
- start en landing met het vliegveld; neerstorten, uitwerpen, doodgaan van piloten
- kills en neergeschoten worden, met beide eenheidstypes en het wapen; andere spelgebeurtenissen zoals ze gegeven worden
- levens per missie (spawn ... session_end), kills, doden, afstand, hoogste hoogte, hoogste g
- elke regel die de hook verstuurt, heel bewaard in heat.raw.parquet, met een eenmaal-per-seconde dump van de exporttabellen van het vliegtuig (motoren, wielen en kleppen, lading, tegenmaatregelen, route, navigatie) en elke andere callback (pauze, chat, spelers die meedoen, missie laden)

## Waar het vandaan komt {#where-it-comes-from}

het hookscript van de watcher `%USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua`, UDP-regels naar 127.0.0.1:41993

## Zo zet je het aan {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (voegt Scripts\Hooks\heat3d-watch.lua toe), start daarna DCS opnieuw

Typ het commando in een terminal die geopend is in de map van de watcher (zie [Voordat je begint](before-you-start.md)). Als het mislukt, zegt de laatste regel waarom. [Installeren en uitvoeren](installing-and-running.md) beschrijft de gewone oorzaken.

`python -m heat3d_watch setup dcs` laat zien welke bestanden het zou wijzigen. `python -m heat3d_watch setup dcs --apply` wijzigt ze en bewaart het origineel als `<file>.heat3d-backup` (zie [Commando's](commands.md#setup)). Het toont `dcs: changed: ...` voor elke wijziging, of `dcs: nothing to change` als het al aan staat.

## Hoe het werkt {#how-it-works}

DCS World: een klein hookscript van de watcher zelf, dat UDP-regels stuurt naar 127.0.0.1:41993.

DCS draait Lua-bestanden in `Saved Games\DCS*\Scripts\Hooks\` bij het starten. Een hook kan de exportfuncties (`Export.Lo*`) lezen en de callbacks van de simulatie ontvangen (`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - zie `<DCS>\API\DCS_ControlAPI.html` en <https://wiki.hoggitworld.com/view/DCS_Export_Script>.
`setup` schrijft `heat3d-watch.lua` daar (een eigen bestand: Export.lua en de hooks van andere tools worden niet aangeraakt). Dat stuurt tien regels per seconde, nog een per seconde, en één per spelgebeurtenis of callback, zonder ooit op een antwoord te wachten. De poort is 41993 zodat de hook van JoyPro (41992) en Tacview (42674) ernaast blijven werken. De regels (velden gesplitst met ';'):

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

`p` is LoGetSelfData: Position x/y/z - DCS's eigen wereldmeters, x noord, y omhoog, z oost - plus LatLongAlt (graden, m), Heading/Pitch/Bank (radialen), met LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) en LoGetAccelerationUnits() x/y/z (g); en, zoals `Scripts\Export.lua` ze beschrijft, LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s), LoGetAngleOfAttack en LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad), LoGetRadarAltimeter (m), LoGetVectorVelocity (wereld m/s), LoGetAngularVelocity (rad/s), LoGetInAir, en het punt en de voorwaartse vector van LoGetCameraPosition (wereldmeters). `d` is een eenmaal-per-seconde dump van hele tabellen, platgeslagen naar gepunte sleutels: LoGetSelfData (land, coalitie, namen van eenheid en groep, typeniveaus, vlaggen), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus en een paar getallen (pauze, tijdversnelling, stoel, druk, afwijkingen). De watcher bewaart elke regel heel in de ruwe bijlage; `p` wordt ook de rijen.

Posities gaan in dezelfde platte kaart als die van de andere vluchtsimulators (`Tangent`: x oost, y hoogte boven zeeniveau, z noord, meters) vanuit LatLongAlt, rond de vaste oorsprong van het theater (`THEATRES`, uit de `map` van de startregel). Zo deelt elke missie op één theater dezelfde kaart, en kan de viewer de echte wereld eronder leggen. Een theater dat niet in de tabel staat, neemt de breedte- en lengtegraad van de eerste meting, afgerond op hele graden. De x/y/z van DCS zelf worden bewaard als `dcs_x`, `dcs_y`, `dcs_z`; een meting zonder LatLongAlt kan niet geplaatst worden en wordt alleen geteld (`fixes_without_latlon`). De oorsprong is de `geo` van de sessie, in meta.json en de footer van de tabel.

De argumenten van onGameEvent, zoals DCS_ControlAPI ze geeft: takeoff/landing (playerID, unit_missionID, airdromeName), crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID, killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide, weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide), mission_end (winner, msg).

Een multiplayerserver kan het exporteren van het eigen vliegtuig verbieden (LoIsOwnshipExportAllowed is false); dan zijn er geen posities, alleen gebeurtenissen, en de sessie zegt dat.

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `y` |
| Eenheden | meter (oost, hoogte, noord vanaf de oorsprong van het theater) |
| Gespiegeld voor de viewer | `z` |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities ermee) | 1 |

Deze gaan in het `meta.json` (`axes`) van elke sessie en, als de sessie posities heeft, in de footer van `heat.parquet`. Zo draait en schaalt de 3DHeat-viewer de rijen zelf - zie [De gegevens](the-data.md).

## Meerspelers {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `telemetry`: het leest alleen wat het spel of platform uitgeeft (een UDP-poort of gedeeld geheugen dat het spel publiceert), dus het legt ook online spel vast, net als offline. De vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: wordt door deze adapter **nooit** gelezen. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam zet (de `stats` van elke sessie in `meta.json` en de tabel `stats` in `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is een sleutel per team). Sleutels die de code uit een tabel met velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt die wel.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat, wordt gelezen of bewaard, nooit weggegooid. Naast de rijen wordt elk pakket, elke pagina, regel of antwoord dat de adapter ontvangt, heel bewaard in `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam bewaard is; `used` markeert wat ook rijen werd). De `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- `p` (10 Hz): positie, LatLongAlt, houding, IAS, AGL, g (x/y/z), vliegtuigtype, en de TAS, Mach, verticale snelheid, AoA, sliphoek, magnetische koers, radarhoogte, wereldsnelheid, draaisnelheden, in-de-lucht en het punt/de voorwaartse vector van de camera van hook 2 - allemaal als rijkolommen (eenheden zoals Export.lua ze geeft)
- `start`: missie, theater, eigen speler-id en naam, multiplayer, missiebestand, server; `mis`: de datum en starttijd van de missie in meta.json
- `ev`: elke onGameEvent als rij (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, elke andere naam zoals gegeven)
- `noexport` en `stop` als rijen en in meta.json

**Heel bewaard**

- elke regel die de hook verstuurt, heel, als `text` onder zijn soort: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; een regel van een andere soort onder `unknown`
- `d` (1 Hz, alleen ruw): LoGetSelfData heel (land, coalitie, naam van eenheid en groep, typeniveaus, vlaggen), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, windvector, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, radiobakens, pauze, tijdversnelling, stoel, druk, afwijkingen - platgeslagen naar gepunte sleutels
- `mis`: de weertabel van de missie, platgeslagen; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage met hun argumenten

**Niet beschikbaar**

- andere eenheden (LoGetWorldObjects, LoGetObjectById) en sensordata (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): niet opgevraagd - elk object van een missie op 10 Hz is duur binnen elk beeld van DCS, en een server beperkt ze (allow_object_export, allow_sensor_export); Tacview legt ze vast
- de hele missietabel (DCS.getCurrentMission bevat elke eenheid en trigger, megabytes groot): alleen de datum, starttijd, weer, sortie, theater en versie worden gestuurd
- de callbacks onPlayerTry\*: ze antwoorden DCS (toestaan of weigeren), dus de hook laat ze met rust
- adressen en UCID's van andere spelers: net.get_player_info geeft die alleen aan een server, en ze zijn niet van de speler om te bewaren
- de items van een tabel boven 800 sleutels of 6 niveaus diep in één `d`-regel worden afgekapt, zodat één regel één datagram blijft

**Grootte**: ongeveer 20 MB per uur aan `p`-regels (10 per seconde, ongeveer 500 bytes elk met zijn frame) en 15-40 MB aan `d`-dumps (één per seconde, 4-10 KB afhankelijk van de lading en route van het vliegtuig), vóór zstd; de herhaalde sleutels comprimeren ongeveer tien keer

## Geverifieerd {#verified}

regelformaat getest met synthetische datagrammen; de Lua-hook is niet getest binnen DCS (geschreven vanuit de hook/export-API van DCS en de lijst met Lo\*-functies in Scripts\Export.lua, niet uitgevoerd)

## Bron {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Gegenereerd uit de adapter door tools/gen_game_pages.py; wijzig de adapter en voer het opnieuw uit in plaats van deze pagina te bewerken. -->
