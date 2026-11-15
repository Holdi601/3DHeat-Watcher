---
title: "Microsoft Flight Simulator 2020 (lifandi gögn)"
nav_order: 31
lang: "is"
source: game-msfs2020.md
source_hash: "9b9e8389114b"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2020 (lifandi gögn) {#microsoft-flight-simulator-2020-live-data}

Meðan þú spilar Microsoft Flight Simulator 2020 vistar watcher gögnin sem leikurinn sendir sjálfur út, svo þú getir skoðað þau síðar á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `msfs2020`, gerð [`telemetry`](sources-and-rules.md); það keyrir meðan `FlightSimulator.exe` er í gangi og leitar að nýjum gögnum á 0,1 s fresti.*

## Hvað er skráð {#what-is-recorded}

- staða eigin loftfars í hverjum hermiramma, tekin á 10 Hz (breiddargráða/lengdargráða/hæð sem metrar austur/upp/norður af fyrstu mælingu; lat/lon/alt geymd sem dálkar)
- afstaða, ábendur lofthraði, hraði miðað við jörð, AGL, g, á jörðu; sannur lofthraði, Mach, lóðréttur hraði, AoA, hliðarskrið, segulstefna, hraði miðað við skrokk, hröðun og snúningshraði á um 10 Hz
- þyngd, eldsneyti, vængbörð (flaps), lendingarbúnaður, spoilers, stöðuhemill, sjálfstýring, inngjöf, RPM, veður, hermihraði, tími og myndavélarstaða einu sinni á sekúndu; heiti loftfarsins og ATC-gerð, módel og auðkenni
- flugtök, lendingar, brotlendingar, flug hafin og stöðvuð (session_start/session_end)
- flugtími, tími í lofti, vegalengd, mesta hæð, mesta g, lendingar
- hver SimConnect-skilaboð geymd í heild í heat.raw.parquet

## Hvaðan það kemur {#where-it-comes-from}

SimConnect í gegnum SimConnect.dll spilarans sjálfs (hermismappan, eða %MSFS_SDK%\SimConnect SDK\lib)

## Hvernig á að kveikja á því {#how-to-switch-it-on}

ekkert; SimConnect.dll fylgir MSFS 2020 (eða MSFS SDK)

## Hvernig það virkar {#how-it-works}

Microsoft Flight Simulator 2020 og 2024: SimConnect, í gegnum SimConnect.dll spilarans sjálfs.

SimConnect er útgefið biðlara-API hermisins (SDK-skjöl:
<https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>,
<https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>).
Watcher fylgir ekki með DLL-skrána: það hleður þeirri sem fylgdi hermi eða
SDK hans - MSFS 2020 setur `SimConnect.dll` í uppsetningarmöppu sína; MSFS 2024 á
Steam fylgir aðeins sín innri, svo spilarar 2024 setja upp MSFS 2024 SDK
(`<SDK>\SimConnect SDK\lib\SimConnect.dll`; 2024-hermirinn tekur líka við 2020-biðlurum).

Köllin, úr SimConnect.h, öll skila HRESULT (0 = S_OK):

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

Hver skilaboð byrja á SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID}
(#pragma pack 1). Þau sem eru lesin hér:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Hermibreytur (einingar beðið um svo engin umbreyting sé nauðsynleg): PLANE
LATITUDE/LONGITUDE (gráður), PLANE ALTITUDE (metrar, yfir sjávarmáli), PLANE
ALT ABOVE GROUND (metrar), PLANE PITCH/BANK DEGREES og PLANE HEADING DEGREES
TRUE (gráður; eigin formerki SimConnect - nef upp er neikvætt pitch), AIRSPEED
INDICATED og GROUND VELOCITY (hnútar), G FORCE (gforce), SIM ON GROUND (bool).
Kerfisatburðir: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded,
Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Þrjár gagnaskilgreiningar til viðbótar biðja um afganginn af fluginu (`MOTION_VARS`,
sjötti hver hermirammi), hægara ástand loftfarsins (`STATE_VARS`, einu sinni á
sekúndu) og nöfn þess (`NAME_VARS`, 256 bæta strengir, þegar þau breytast); hver
er sín eigin skilgreining, svo breyta sem ein hermiútgáfa þekkir ekki kostar
aðeins þann blokk. Hver skilaboð eru geymd í heild í hráu hliðarskrá lotunnar.

Staðsetningar fara í sama flata kortið og hjá X-Plane (x austur, y hæð, z norður
í metrum frá fyrstu mælingu setunnar); sú mæling er `geo` lotunnar, í
meta.json og fæti töflunnar.

Sama eining þjónar líka: [Microsoft Flight Simulator 2024 (lifandi gögn)](game-msfs2024.md).

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | já |
| Upp-ás | `y` |
| Einingar | metrar (austur, hæð, norður frá fyrstu mælingu) |
| Speglað fyrir skoðarann | `z` |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` (`axes`) hverrar lotu og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem "allowed (reads only what the game publishes)".
- Gerð `telemetry`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (UDP-gátt eða samnýtt minni sem leikurinn birtir), svo það skráir bæði í netspilun og án nets; merkið ræður aðeins hvort minni megi nokkurn tíma lesa.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Lykill í slaufusvigum er fylltur út við keyrslu (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; "Hvað er skráð" hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [breytireglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er hver pakki, síða, lína eða svar sem millistykkið fær geymt í heild í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, svo hver reitur sem geymdur er með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hvert `type` - `lost` er 0.

**Lesið**

- SIMOBJECT_DATA úr stöðuskilgreiningunni (hver hermirammi): breiddargráða, lengdargráða, hæð, AGL, pitch, bank, sönn stefna, IAS, hraði miðað við jörð, g, á jörðu - síðasti rammi könnunarinnar sem röð, hver rammi fyrir lendingar og flugtök
- SIMOBJECT_DATA úr hreyfiskilgreiningunni (um 10 Hz: TAS, Mach, lóðréttur hraði, AoA, hliðarskrið, segulstefna, skrokkhraði, hröðun og snúningshraði á þremur ásum) og úr ástandsskilgreiningunni (1 Hz: þyngd, eldsneyti, vængbörð, lendingarbúnaður, spoilers, stöðuhemill, sjálfstýring, hreyflar, inngjöf og RPM, útihiti, vindur, loftþrýstingur við sjávarmál, hermihraði, zulu- og staðartími, myndavélarstaða) yfir á raðirnar eins og það barst síðast
- SIMOBJECT_DATA úr nafnaskilgreiningunni (heiti, ATC-gerð, módel og auðkenni) í meta.json og `aircraft` raðanna; OPEN (forrit og útgáfa) í meta.json
- EVENT og EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (flugskráin) og AircraftLoaded (loftfarsskráin) sem flug, brotlendingar og meta.json
- QUIT lýkur lotunni

**Geymt óunnið**

- hver skilaboð sem SimConnect réttir watcher, í heild sem `payload`, undir SIMCONNECT_RECV_ID-heiti sínu: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (breyta eða atburður sem hermirinn tók ekki við, með send-auðkenni og vísi), hvert annað auðkenni undir heiti sínu eða `RECV_<id>`
- það sem aðeins hráa hliðarskráin geymir: staða hvers hermiramma milli raðanna, atburðirnir Pause, Sim, CrashReset, PositionChanged og FlightSaved, skilgreining sem hermirinn skar stutta (ein breyta sem hann þekkti ekki: blokkin er þá ekki lesin eftir nafni); `requests` í meta.json telur upp breytur og einingar hverrar skilgreiningar í röð, svo hægt sé að lesa gögnin án þessarar einingar

**Ekki tiltækt**

- önnur loftför (gervigreindarumferð, aðrir spilarar á netinu): SimConnect_RequestDataOnSimObjectType myndi kanna hvert loftfar innan radíuss - meira álag á hermi, og flug annarra spilara
- hreyfiblokkin í hverjum hermiramma: beðið er um hana í sjötta hverjum ramma (um 10 Hz, tíðni raðanna), sem heldur hráa straumnum í um fimmtungi af stærðinni; stöðublokkin er áfram í hverjum ramma
- þúsundir annarra hermibreyta (talstöðvar, ljós, mælar hvers hreyfils, bilanir): skilgreining geymir það sem hún biður um; listarnir biðja um flugið, ástand loftfarsins og tíma hermisins
- veðurathuganir, aðstaða (flugvellir, VOR), biðlaragögn viðbóta: sérstakar beiðnir, ekki gerðar

**Stærð**: um 30-55 MB á klukkustund fyrir zstd: stöðublokkin í hverjum hermiramma (um 200 bæti með rammanum, 30-60 á sekúndu), hreyfiblokkin á um 10 Hz (um 240 bæti), ástandsblokkin einu sinni á sekúndu; zstd minnkar tvöfalda tölurnar nokkrum sinnum

## Staðfest {#verified}

afkóðun skilaboða prófuð á biðminnum smíðuðum eftir sniðum SimConnect.h; lifandi SimConnect-tenging er óprófuð

## Heimild {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
