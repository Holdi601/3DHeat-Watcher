---
title: "DCS World (live-data)"
nav_order: 10
lang: "fi"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (live-data) {#dcs-world-live-data}

Kun pelaat DCS Worldia, watcher tallentaa datan, jonka peli itse lähettää ulos, jotta voit myöhemmin katsoa sen kartalla 3DHeat-katselimessa.

*Tekniset tiedot: adapteri `dcs`, tyyppi [`telemetry`](sources-and-rules.md); se toimii, kun `DCS.exe` on käynnissä, ja etsii uutta dataa 0,1 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- oma sijainti 10 Hz:n taajuudella metreinä itään, ylös ja pohjoiseen teatterin lähtöpisteestä (leveys-, pituusasteesta ja korkeudesta laskettuna); lat/lon/alt sekä DCS:n omat maailmametrit (dcs_x pohjoinen, dcs_y ylös, dcs_z itä) sarakkeina
- asento, mittarinopeus ja todellinen ilmanopeus, Mach, pystynopeus, hyökkäyskulma ja luisuminen, magneettinen suunta, AGL ja tutkakorkeus, g kolmella akselilla, nopeus ja pyörimisnopeudet, ilmassa-tieto, kameran sijainti ja eteenpäin osoittava vektori, ilma-aluksen tyyppi
- lentoonlähdöt ja laskut lentokentän kanssa; törmäykset, poistumiset ja lentäjän kuolemat
- tappot ja oman koneen ammutuksi tuleminen molempien yksikkötyyppien ja aseen kanssa; muut pelitapahtumat sellaisina kuin ne annetaan
- tehtävän elinajat (spawn ... session_end), tappot, kuolemat, matka, korkein korkeus ja korkein g
- jokainen koukun lähettämä rivi kokonaisena tiedostossa heat.raw.parquet, sekä kerran sekunnissa lentokoneen vientitaulukot (moottorit, telineet ja läpät, kuorma, vastatoimet, reitti, navigointi) ja jokainen muu takaisinkutsu (tauko, chat, pelaajien liittyminen, tehtävän lataus)

## Mistä tiedot tulevat {#where-it-comes-from}

watcherin koukku %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, UDP-rivit osoitteeseen 127.0.0.1:41993

## Kuinka se käynnistetään {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (lisää tiedoston Scripts\Hooks\heat3d-watch.lua), sitten käynnistä DCS uudelleen

Kirjoita komento terminaaliin, joka on avattu watcherin kansiossa (katso [Ennen aloittamista](before-you-start.md)). Jos se epäonnistuu, viimeinen rivi kertoo syyn; [Asennus ja käynnistys](installing-and-running.md) kattaa yleisimmät syyt.

`python -m heat3d_watch setup dcs` listaa tiedostot, jotka se muuttaisi; `python -m heat3d_watch setup dcs --apply` tekee muutokset ja tallentaa alkuperäisen tiedostona `<file>.heat3d-backup` (katso [Komennot](commands.md#setup)). Se tulostaa `dcs: changed: ...` jokaisesta muutoksesta tai `dcs: nothing to change`, jos asetus on jo päällä.

## Miten se toimii {#how-it-works}

DCS World: watcherin oma pieni koukkuskripti, joka lähettää UDP-rivejä osoitteeseen 127.0.0.1:41993.

DCS ajaa tiedostoja `Saved Games\DCS*\Scripts\Hooks\`-kansiosta käynnistyessään. Koukku voi lukea vientifunktioita (`Export.Lo*`) ja vastaanottaa simulaation takaisinkutsut (`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent). Katso `<DCS>\API\DCS_ControlAPI.html` ja <https://wiki.hoggitworld.com/view/DCS_Export_Script>. `setup` kirjoittaa `heat3d-watch.lua`-tiedoston sinne. Se on oma tiedostonsa, eikä Export.lua:ta tai muiden työkalujen koukkuja kosketa. Tiedosto lähettää kymmenen riviä sekunnissa, yhden lisäksi sekunnissa ja yhden jokaista pelitapahtumaa tai takaisinkutsua kohden, eikä koskaan odota vastausta. Portti on 41993, jotta JoyPron koukku (41992) ja Tacview (42674) toimivat sen rinnalla. Rivit (kentät erotettu merkillä ';'):

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

`p` on LoGetSelfData: sijainti x/y/z (DCS:n omat maailmametrit, x pohjoinen, y ylös, z itä) sekä LatLongAlt (astetta, m), Heading/Pitch/Bank (radiaaneina), LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) ja LoGetAccelerationUnits() x/y/z (g). Lisäksi, kuten `Scripts\Export.lua` ne dokumentoi: LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s), LoGetAngleOfAttack ja LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad), LoGetRadarAltimeter (m), LoGetVectorVelocity (maailman m/s), LoGetAngularVelocity (rad/s), LoGetInAir sekä LoGetCameraPositionin piste ja eteenpäin osoittava vektori (maailman metriä). `d` on kerran sekunnissa otettu kokonaisten taulukoiden vedos, litistettynä pisteellä erotettuihin avaimiin: LoGetSelfData (maa, koalitio, yksikön ja ryhmän nimet, tyyppitasot, liput), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus sekä muutama luku (tauko, ajan kiihdytys, paikka, paine, poikkeamat). Watcher säilyttää jokaisen rivin kokonaisena raakatiedostossa. `p` menee myös riveiksi.

Sijainnit menevät samaan tasaiseen karttaan kuin muiden lentosimulaattorien (`Tangent`: x itään, y merenpinnan yläpuolinen korkeus, z pohjoiseen, metreinä). Ne lasketaan LatLongAlt-arvoista teatterin kiinteän lähtöpisteen (`THEATRES`, rivin `start` kartasta) ympäri. Näin jokainen tehtävä samalla teatterilla jakaa yhden kartan, jolle viewer voi asettaa todellisen maailman. Teatteri, jota taulukossa ei ole, ottaa ensimmäisen mittauksen leveys- ja pituusasteet pyöristettyinä kokonaisiin asteisiin. DCS:n omat x/y/z tallennetaan nimillä `dcs_x`, `dcs_y`, `dcs_z`. Mittaus ilman LatLongAlt-arvoa ei ole sijoitettavissa, joten se vain lasketaan (`fixes_without_latlon`). Lähtöpiste on session `geo`, joka on tiedostossa meta.json ja taulun alatunnisteessa.

onGameEventin argumentit DCS_ControlAPI:n mukaan: takeoff/landing (playerID, unit_missionID, airdromeName), crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID, killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide, weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide), mission_end (winner, msg).

Moninpelipalvelin voi kieltää oman koneen tietojen viennin (LoIsOwnshipExportAllowed on false). Silloin sijainteja ei ole, vain tapahtumat, ja sessio kertoo sen.

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennettu | kyllä |
| Ylösakseli | `y` |
| Yksiköt | metriä (itä, korkeus ja pohjoinen teatterin lähtöpisteestä) |
| Peilattu katselimelle | `z` |
| Yksikkökerroin (`scale`: katselin kertoo sijainnit sillä) | 1 |

Nämä menevät kunkin session `meta.json`-tiedostoon (`axes`) ja, kun sessiossa on sijainteja, tiedoston `heat.parquet` alatunnisteeseen. Siksi 3DHeat-katselin kääntää ja skaalaa rivit itse; katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän tekstillä "allowed (reads only what the game publishes)".
- Tyyppi `telemetry`: se lukee vain sen, minkä peli tai alusta luovuttaa (UDP-portti tai jaettu muisti, jonka peli julkaisee). Se tallentaa siis myös verkkopelit, samoin kuin offline-pelit. Lippu päättää vain, saako muistia koskaan lukea.
- Muisti: **ei koskaan**. Tämä sovitin ei lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan verkkopeliksi merkitystä pelistä. Katso [Lähteet ja säännöt](sources-and-rules.md).

## Tallennetut tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (kunkin session `stats` tiedostossa `meta.json` ja `watcher.sqlite`-tiedoston taulussa `stats`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohden). Avaimet, jotka koodi ottaa pelin kenttien taulukosta tai pelin omista tilastonimistä, eivät ole tässä luettelossa; yllä oleva "Mitä tallennetaan" -osio nimeää ne.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muuntimen sääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): lähteessä oleva tieto luetaan tai säilytetään, sitä ei koskaan jätetä pois. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, säilytetään kokonaisena session tiedostossa `heat.raw.parquet` (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja kaikki nimellä säilytetyt kentät; `used` merkitsee ne, joista tuli myös rivejä). Tiedoston `meta.json` kohdan `selfCheck.completeness` laskuri kertoo jokaisen `type`-arvon määrän, ja `lost` on 0.

**Luetaan**

- `p` (10 Hz): sijainti, LatLongAlt, asento, IAS, AGL, g (x/y/z), ilma-aluksen tyyppi sekä koukun 2 TAS, Mach, pystynopeus, AoA, luisuminen, magneettinen suunta, tutkakorkeus, maailman nopeus, pyörimisnopeudet, ilmassa-tieto ja kameran piste ja eteenpäin osoittava vektori. Kaikki ovat rivien sarakkeina (yksiköt niin kuin Export.lua ne antaa)
- `start`: tehtävä, teatteri, oman pelaajan tunnus ja nimi, moninpeli, tehtävätiedosto, palvelin; `mis`: tehtävän päivämäärä ja aloitusaika tiedostoon meta.json
- `ev`: jokainen onGameEvent rivinä (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, muu nimi sellaisenaan)
- `noexport` ja `stop` riveinä ja tiedostoon meta.json

**Säilytetään raakana**

- jokainen koukun lähettämä rivi kokonaisena `text`-kentässä sen tyypin alla: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`. Rivin tyyppiä, jota ei tunneta, säilytetään nimellä `unknown`
- `d` (1 Hz, vain raakana): LoGetSelfData kokonaisena (maa, koalitio, yksikön ja ryhmän nimi, tyyppitasot, liput), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, tuulivektori, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, radiomajakat, tauko, ajan kiihdytys, paikka, paine, poikkeamat, litistettyinä pisteellä erotettuina avaimina
- `mis`: tehtävän säätaulukko litistettynä; `cb`: onSimulationPause/Resume, onMissionLoad*, onNet*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage argumentteineen

**Ei saatavilla**

- muut yksiköt (LoGetWorldObjects, LoGetObjectById) ja tutkadata (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): ei pyydetty. Tehtävän jokainen kohde 10 Hz:llä on kallista DCS:n omassa kehyksessä, ja palvelin rajoittaa niitä (allow_object_export, allow_sensor_export). Tacview tallentaa ne
- koko tehtävätaulukko (DCS.getCurrentMission sisältää jokaisen yksikön ja laukaisimen, megatavuja): lähetetään vain sen päivämäärä, aloitusaika, sää, lento, teatteri ja versio
- `onPlayerTry*`-takaisinkutsut: ne vastaavat DCS:lle (sallivat tai kieltävät), joten koukku jättää ne rauhaan
- muiden pelaajien osoitteet ja UCID-tunnukset: net.get_player_info antaa ne vain palvelimelle, eikä ne kuulu tallennettaviksi
- taulukon merkinnät yli 800 avaimen tai 6 tason syvyyden jälkeen yhdessä `d`-rivissä katkaistaan, jotta yksi rivi pysyy yhtenä datagrammina

**Koko**: noin 20 Mt tunnissa `p`-rivejä (10 sekunnissa, noin 500 tavua kehyksineen) ja 15–40 Mt `d`-vedoksia (yksi sekunnissa, 4–10 kt koneen kuorman ja reitin mukaan), ennen zstd-pakkausta. Toistuvat avaimet pakkautuvat noin kymmenkertaisesti.

## Todennettu {#verified}

rivimuoto testattu synteettisillä datagrammeilla. Lua-koukku on testaamatta DCS:n sisällä: se on kirjoitettu DCS:n koukku- ja vientirajapinnasta sekä Scripts\Export.lua:n Lo*-funktioluettelosta, eikä sitä ole ajettu.

## Lähde {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
