---
title: "Microsoft Flight Simulator 2024 (live-data)"
nav_order: 32
lang: "fi"
source: game-msfs2024.md
source_hash: "011c18a23252"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2024 (live-data) {#microsoft-flight-simulator-2024-live-data}

Kun pelaat Microsoft Flight Simulator 2024:ää, watcher tallentaa pelin lähettämän datan, jotta voit myöhemmin katsoa sen kartalla 3DHeat-katselimessa.

*Tekniset tiedot: adapteri `msfs2024`, tyyppi [`telemetry`](sources-and-rules.md); se toimii, kun `FlightSimulator2024.exe` on käynnissä, ja etsii uutta dataa 0,1 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- oman ilma-aluksen sijainti jokaisella simulaatiokehyksellä, otettuna 10 Hz:n taajuudella (leveys-, pituusaste ja korkeus metreinä itään, ylös ja pohjoiseen ensimmäisestä paikasta; lat/lon/alt tallennetaan sarakkeina)
- asento, mittarinopeus, maanopeus, AGL, g, maassa-tieto; todellinen ilmanopeus, Mach, pystynopeus, AoA, sivuliuku, magneettinen suunta, runko-nopeudet, kiihtyvyydet ja pyörimisnopeudet noin 10 Hz:n taajuudella
- paino, polttoaine, läpät, telineet, spoilerit, seisontajarru, autopilot, kaasu, kierrosluku, sää, simulaation nopeus, aika ja kameran tila kerran sekunnissa; ilma-aluksen nimi, ATC-tyyppi, malli ja tunnus
- lentoonlähdöt, laskut, törmäykset, lennot aloitettu ja lopetettu (session_start/session_end)
- lentoaika, ilmassaoloaika, matka, korkein korkeus, korkein g ja laskut
- jokainen SimConnect-viesti kokonaisena heat.raw.parquet-tiedostossa

## Mistä tiedot tulevat {#where-it-comes-from}

SimConnect pelaajan oman SimConnect.dll-tiedoston kautta (simulaattorin kansio tai %MSFS2024_SDK%\SimConnect SDK\lib)

## Kuinka se käynnistetään {#how-to-switch-it-on}

ei mitään simulaattorissa; tarvitaan SimConnect.dll. MSFS 2020:ssä se on kansiossa, MSFS 2024:n pelaajat asentavat MSFS 2024 SDK:n

## Miten se toimii {#how-it-works}

Microsoft Flight Simulator 2020 ja 2024: SimConnect pelaajan oman SimConnect.dll-tiedoston kautta.

SimConnect on simulaattorin julkaistu asiakasrajapinta (SDK-dokumentaatio: <https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>, <https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>). Watcher ei toimita DLL-tiedostoa itse. Se lataa sen, joka tuli simulaattorin tai sen SDK:n mukana. MSFS 2020 asettaa `SimConnect.dll`-tiedoston asennuskansioonsa. MSFS 2024 Steamissa sisältää vain oman sisäisen versionsa, joten 2024:n pelaajat asentavat MSFS 2024 SDK:n (`<SDK>\SimConnect SDK\lib\SimConnect.dll`; 2024-simulaattori hyväksyy myös 2020-asiakkaat).

Kutsut SimConnect.h-tiedostosta, kaikki palauttavat HRESULT-arvon (0 = S_OK):

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

Jokainen viesti alkaa rakenteella SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID} (#pragma pack 1). Nämä luetaan tässä:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Simulaatiomuuttujat (pyydetyt yksiköt, joten muunnosta ei tarvita): PLANE LATITUDE/LONGITUDE (astetta), PLANE ALTITUDE (metriä merenpinnasta), PLANE ALT ABOVE GROUND (metriä), PLANE PITCH/BANK DEGREES ja PLANE HEADING DEGREES TRUE (astetta; SimConnectin omat merkit, nokka ylös on negatiivinen pitch), AIRSPEED INDICATED ja GROUND VELOCITY (solmua), G FORCE (gforce), SIM ON GROUND (bool). Järjestelmätapahtumat: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded, Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Kolme muuta datamääritystä pyytävät lennon loput tiedot (`MOTION_VARS`, joka kuudennella simulaatiokehyksellä), ilma-aluksen hitaamman tilan (`STATE_VARS`, kerran sekunnissa) ja sen nimet (`NAME_VARS`, 256 tavun merkkijonot, kun ne muuttuvat). Jokainen on oma määrityksensä, joten muuttuja, jonka simulaattorin versio ei tunne, maksaa vain sen lohkon. Jokainen viesti säilytetään kokonaisena session raakatiedostossa.

Sijainnit menevät samaan tasaiseen karttaan kuin X-Planen (x itään, y korkeus, z pohjoiseen metreinä lennon ensimmäisestä paikasta). Tuo paikka on session `geo`, joka on tiedostossa meta.json ja taulun alatunnisteessa.

Sama moduuli palvelee myös: [Microsoft Flight Simulator 2020 (live-data)](game-msfs2020.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennettu | kyllä |
| Ylösakseli | `y` |
| Yksiköt | metriä (itä, korkeus ja pohjoinen ensimmäisestä paikasta) |
| Peilattu katselimelle | `z` |
| Yksikkökerroin (`scale`: katselin kertoo sijainnit sillä) | 1 |

Nämä menevät kunkin session `meta.json`-tiedostoon (`axes`) ja, kun sessiossa on sijainteja, tiedoston `heat.parquet` alatunnisteeseen. Siksi 3DHeat-katselin kääntää ja skaalaa rivit itse; katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän tekstillä "allowed (reads only what the game publishes)".
- Tyyppi `telemetry`: se lukee vain sen, minkä peli tai alusta luovuttaa (UDP-portti tai jaettu muisti, jonka peli julkaisee). Se tallentaa siis myös verkkopelit, samoin kuin offline-pelit. Lippu päättää vain, saako muistia koskaan lukea.
- Muisti: **ei koskaan**. Tämä sovitin ei lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan verkkopeliksi merkitystä pelistä. Katso [Lähteet ja säännöt](sources-and-rules.md).

## Tallennetut tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (kunkin session `stats` tiedostossa `meta.json` ja `watcher.sqlite`-tiedoston taulussa `stats`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohden). Avaimet, jotka koodi ottaa pelin kenttien taulukosta tai pelin omista tilastonimistä, eivät ole tässä luettelossa; yllä oleva "Mitä tallennetaan" -osio nimeää ne.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muuntimen sääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): lähteessä oleva tieto luetaan tai säilytetään, sitä ei koskaan jätetä pois. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, säilytetään kokonaisena session tiedostossa `heat.raw.parquet` (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja kaikki nimellä säilytetyt kentät; `used` merkitsee ne, joista tuli myös rivejä). Tiedoston `meta.json` kohdan `selfCheck.completeness` laskuri kertoo jokaisen `type`-arvon määrän, ja `lost` on 0.

**Luetaan**

- SIMOBJECT_DATA sijaintimäärityksestä (joka simulaatiokehys): leveysaste, pituusaste, korkeus, AGL, pitch, bank, todellinen suunta, IAS, maanopeus, g, maassa-tieto. Kyselyn viimeinen kehys on rivinä, ja jokainen kehys tallennetaan kosketuksille ja lentoonlähdöille
- SIMOBJECT_DATA liikemääritykseltä (noin 10 Hz: TAS, Mach, pystynopeus, AoA, sivuliuku, magneettinen suunta, runkonopeus, kiihtyvyys ja pyörimisnopeus kolmella akselilla) ja tilamääritykseltä (1 Hz: painot, polttoaine, läpät, telineet, spoilerit, seisontajarru, autopilot, moottorit, kaasu ja kierrosluku, ulkolämpötila, tuuli, merenpinnan paine, simulaation nopeus, zulu- ja paikallinen aika, kameran tila). Ne menevät riveille viimeksi vastaanotettuina
- SIMOBJECT_DATA nimimäärityksestä (nimi, ATC-tyyppi, malli ja tunnus) tiedostoon meta.json ja rivien `aircraft`-kenttään; OPEN (sovellus ja versio) tiedostoon meta.json
- EVENT ja EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (lentotiedosto) ja AircraftLoaded (ilma-aluksen tiedosto) lentoina, törmäyksinä ja tiedostoon meta.json
- QUIT päättää session

**Säilytetään raakana**

- jokainen viesti, jonka SimConnect antaa watcherille, kokonaisena `payload`-kentässä sen SIMCONNECT_RECV_ID-nimen alla: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (muuttuja tai tapahtuma, jonka simulaattori ei hyväksynyt, lähetystunnuksen ja indeksin kanssa), mikä tahansa muu tunnus nimellään tai `RECV_<id>`
- vain raakasessio sisältää: jokaisen simulaatiokehyksen sijainnin rivien välissä, tapahtumat Pause, Sim, CrashReset, PositionChanged ja FlightSaved, sekä määrityksen, jonka simulaattori katkaisi (yksi muuttuja, jota se ei tuntenut: lohkoa ei silloin lueta nimillä). Tiedoston meta.json kohta `requests` listaa jokaisen määrityksen muuttujat ja yksiköt järjestyksessä, joten hyötykuormat voi lukea ilman tätä moduulia

**Ei saatavilla**

- muut ilma-alukset (tekoälyliikenne, muut pelaajat verkossa): SimConnect_RequestDataOnSimObjectType kysyisi jokaisen ilma-aluksen säteeltä, mikä kuormittaisi simulaattoria enemmän ja tuo muiden pelaajien lennot mukaan
- liikelohko joka simulaatiokehyksellä: se pyydetään joka kuudennella kehyksellä (noin 10 Hz, rivien nopeus), mikä pitää raakasyötteen noin viidesosassa koosta. Sijaintilohko pysyy joka kehyksellä
- tuhannet muut simulaatiomuuttujat (radiot, valot, jokaisen moottorin mittarit, viat): määritys pitää sen, mitä se pyytää, ja listat pyytävät lennon, ilma-aluksen tilan ja simulaation ajan
- säähavainnot, laitokset (lentokentät, VOR:t) ja lisäosien tiedot: erilliset pyynnöt, joita ei tehdä

**Koko**: noin 30–55 Mt tunnissa ennen zstd-pakkausta. Sijaintilohko joka simulaatiokehyksellä (noin 200 tavua kehyksen kanssa, 30–60 sekunnissa), liikelohko noin 10 Hz:llä (noin 240 tavua) ja tilalohko kerran sekunnissa. zstd pienentää liukuluvut useita kertoja.

## Todennettu {#verified}

viestien purku testattu puskureilla, jotka on rakennettu SimConnect.h-tiedoston rakenteista. Elävä SimConnect-yhteys on testaamatta.

## Lähde {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
