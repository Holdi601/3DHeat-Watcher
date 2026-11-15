---
title: "Microsoft Flight Simulator 2020 (live data)"
nav_order: 31
lang: "nl"
source: game-msfs2020.md
source_hash: "9b9e8389114b"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2020 (live data) {#microsoft-flight-simulator-2020-live-data}

Terwijl je Microsoft Flight Simulator 2020 speelt, slaat de watcher de data op die het spel zelf uitstuurt. Zo kun je die later op een kaart in de 3DHeat-viewer bekijken.

*Technische details: adapter `msfs2020`, soort [`telemetry`](sources-and-rules.md); hij draait zolang `FlightSimulator.exe` actief is en zoekt elke 0,1 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- positie van het eigen vliegtuig in elk simulatieframe, gemeten 10 keer per seconde (breedtegraad/lengtegraad/hoogte als meters oost/omhoog/noord vanaf de eerste meting; lat/lon/alt bewaard als kolommen)
- houding, aangegeven vliegsnelheid, grondsnelheid, AGL, g, op de grond; echte vliegsnelheid, Mach, verticale snelheid, AoA, sliphoek, magnetische koers, lichaamssnelheden, versnellingen en draaisnelheden, ongeveer 10 keer per seconde
- gewicht, brandstof, kleppen, landingsgestel, spoilers, parkeerrem, automatische piloot, gas, toerental, weer, simulatiesnelheid, tijd en camerastand, eenmaal per seconde; de titel en het ATC-type, model en id van het vliegtuig
- start, landing, crashes, vluchten gestart en gestopt (session_start/session_end)
- vliegtijd, tijd in de lucht, afstand, hoogste hoogte, hoogste g, landingen
- elk SimConnect-bericht heel in heat.raw.parquet

## Waar het vandaan komt {#where-it-comes-from}

SimConnect via de eigen SimConnect.dll van de speler (de simulatiemap, of %MSFS_SDK%\SimConnect SDK\lib)

## Zo zet je het aan {#how-to-switch-it-on}

niets; SimConnect.dll komt mee met MSFS 2020 (of de MSFS-SDK)

## Hoe het werkt {#how-it-works}

Microsoft Flight Simulator 2020 en 2024: SimConnect, via de eigen SimConnect.dll van de speler.

SimConnect is de gepubliceerde client-API van de simulator (SDK-documentatie:
<https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>,
<https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>).
De watcher levert de DLL niet mee: hij laadt die welke bij de simulator of zijn SDK hoort - MSFS 2020 zet `SimConnect.dll` in zijn installatiemap; MSFS 2024 op Steam bevat alleen zijn interne versie, dus spelers van 2024 installeren de MSFS 2024-SDK
(`<SDK>\SimConnect SDK\lib\SimConnect.dll`; de simulator van 2024 accepteert ook 2020-clients).

De aanroepen, uit SimConnect.h, geven allemaal een HRESULT terug (0 = S_OK):

```text
SimConnect_Open(HANDLE*, LPCSTR name, HWND, DWORD, HANDLE, DWORD config)
SimConnect_AddToDataDefinition(HANDLE, DWORD define, LPCSTR var, LPCSTR units,
                               SIMCONNECT_DATATYPE (FLOAT64 = 4), float epsilon, DWORD datum)
SimConnect_RequestDataOnSimObject(HANDLE, DWORD request, DWORD define, DWORD object (0 = user),
                                  SIMCONNECT_PERIOD (SIM_FRAME = 3), DWORD flags, DWORD origin,
                                  DWORD interval, DWORD limit)
SimConnect_SubscribeToSystemEvent(HANDLE, DWORD event, LPCSTR name)
SimConnect_GetNextDispatch(HANDLE, SIMCONNECT_RECV**, DWORD*)   E_FAIL when nothing waits
SimConnect_Close(HANDLE)
```

Elk bericht begint met SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID}
(#pragma pack 1). Deze worden hier gelezen:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Simulatievariabelen (gevraagde eenheden, zodat er geen omrekening nodig is): PLANE
LATITUDE/LONGITUDE (graden), PLANE ALTITUDE (meter, boven zeeniveau), PLANE
ALT ABOVE GROUND (meter), PLANE PITCH/BANK DEGREES en PLANE HEADING DEGREES
TRUE (graden; de eigen tekens van SimConnect - neus omhoog is negatieve pitch), AIRSPEED
INDICATED en GROUND VELOCITY (knopen), G FORCE (gforce), SIM ON GROUND (bool).
Systeemgebeurtenissen: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded,
Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Drie andere gegevensdefinities vragen de rest van de vlucht op (`MOTION_VARS`,
elk zesde simulatieframe), de langzamere toestand van het vliegtuig (`STATE_VARS`, eenmaal
per seconde) en de namen ervan (`NAME_VARS`, tekenreeksen van 256 bytes, als ze veranderen); elk
is een eigen definitie, dus een variabele die een simulatieversie niet kent, kost
alleen dat blok. Elk bericht wordt heel bewaard in de ruwe bijlage van de sessie.

Posities gaan in dezelfde platte kaart als die van X-Plane (x oost, y hoogte, z noord,
in meters vanaf de eerste meting van de zitting); die meting is de `geo` van de sessie, in
meta.json en de footer van de tabel.

Dezelfde module levert ook: [Microsoft Flight Simulator 2024 (live data)](game-msfs2024.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `y` |
| Eenheden | meter (oost, hoogte, noord vanaf de eerste meting) |
| Gespiegeld voor de viewer | `z` |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities ermee) | 1 |

Deze gaan in het `meta.json` (`axes`) van elke sessie en, als de sessie posities heeft, in de footer van `heat.parquet`. Zo draait en schaalt de 3DHeat-viewer de rijen zelf - zie [De gegevens](the-data.md).

## Meerspelers {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `telemetry`: het leest alleen wat het spel of platform uitgeeft (een UDP-poort of gedeeld geheugen dat het spel publiceert), dus het legt ook online spel vast, net als offline. De vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: wordt door deze adapter **nooit** gelezen. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam zet (de `stats` van elke sessie in `meta.json` en de tabel `stats` in `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is een sleutel per team). Sleutels die de code uit een tabel met velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt die wel.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat, wordt gelezen of bewaard, nooit weggegooid. Naast de rijen wordt elk pakket, elke pagina, regel of antwoord dat de adapter ontvangt, heel bewaard in `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam bewaard is; `used` markeert wat ook rijen werd). De `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- SIMOBJECT_DATA van de positiedefinitie (elk simulatieframe): breedtegraad, lengtegraad, hoogte, AGL, pitch, bank, echte koers, IAS, grondsnelheid, g, op de grond - het laatste frame van de meting als rij, elk frame voor touchdowns en start
- SIMOBJECT_DATA van de bewegingsdefinitie (ongeveer 10 Hz: TAS, Mach, verticale snelheid, AoA, sliphoek, magnetische koers, lichaamssnelheid, versnelling en draaisnelheid op drie assen) en van de toestandsdefinitie (1 Hz: gewichten, brandstof, kleppen, landingsgestel, spoilers, parkeerrem, automatische piloot, motoren, gas en toerental, buitentemperatuur, wind, luchtdruk op zeeniveau, simulatiesnelheid, zulu- en lokale tijd, camerastand) op de rijen zoals ze laatst binnenkwamen
- SIMOBJECT_DATA van de naamdefinitie (titel, ATC-type, model en id) in meta.json en de `aircraft` van de rijen; OPEN (applicatie en versie) in meta.json
- EVENT en EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (het vluchtbestand) en AircraftLoaded (het vliegtuigbestand) als vluchten, crashes en meta.json
- QUIT beëindigt de sessie

**Heel bewaard**

- elk bericht dat SimConnect naar de watcher stuurt, heel als `payload`, onder zijn SIMCONNECT_RECV_ID-naam: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (een variabele of gebeurtenis die de simulator niet accepteerde, met het send-id en de index), elk ander id op zijn naam of `RECV_<id>`
- wat alleen de ruwe bijlage bevat: elke positie per simulatieframe tussen de rijen, de gebeurtenissen Pause, Sim, CrashReset, PositionChanged en FlightSaved, een definitie die de simulator afkapte (één variabele die hij niet kende: dat blok wordt dan niet op naam gelezen); `requests` in meta.json somt elke definitie op met zijn variabelen en eenheden, in volgorde, zodat de payloads zonder deze module te lezen zijn

**Niet beschikbaar**

- andere vliegtuigen (AI-verkeer, andere spelers online): SimConnect_RequestDataOnSimObjectType zou elk vliegtuig in een straal opvragen - meer belasting voor de simulator, en de vluchten van andere spelers
- het bewegingsblok elk simulatieframe: het wordt elk zesde frame gevraagd (ongeveer 10 Hz, de snelheid van de rijen), wat de ruwe stroom ongeveer een vijfde van de grootte houdt; het positieblok blijft elk frame
- de duizenden andere simulatievariabelen (radio's, lampen, elke motormeter, storingen): een definitie bevat wat ze vraagt; de lijsten vragen de vlucht, de toestand van het vliegtuig en de tijd van de simulator
- weerwaarnemingen, faciliteiten (vliegvelden, VOR's), clientdata van add-ons: aparte aanvragen, niet gedaan

**Grootte**: ongeveer 30-55 MB per uur vóór zstd: het positieblok elk simulatieframe (ongeveer 200 bytes met zijn frame, 30-60 per seconde), het bewegingsblok op ongeveer 10 Hz (ongeveer 240 bytes), het toestandsblok eenmaal per seconde; zstd verkleint de doubles een paar keer

## Geverifieerd {#verified}

decodering van berichten getest op buffers gebouwd uit de lay-outs van SimConnect.h; de live SimConnect-verbinding is niet getest

## Bron {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Gegenereerd uit de adapter door tools/gen_game_pages.py; wijzig de adapter en voer het opnieuw uit in plaats van deze pagina te bewerken. -->
