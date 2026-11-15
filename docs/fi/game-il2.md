---
title: "IL-2 Sturmovik: Great Battles (reaaliaikadata)"
nav_order: 26
lang: "fi"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (reaaliaikadata) {#il-2-sturmovik-great-battles-live-data}

Kun pelaat IL-2 Sturmovik: Great Battlesia, watcher tallentaa datan, jonka peli itse lähettää ulos. Voit katsoa sitä myöhemmin tilastoina ja aikajanana.

*Tekniset tiedot: sovitin `il2`, tyyppi [`telemetry`](sources-and-rules.md); se toimii, kun `Il-2.exe` tai `IL2Series.exe` on käynnissä, ja hakee uutta dataa 0,1 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- lennot: otettu lentokone (spawn) ja hetki, jolloin tuloste loppuu (session_end) - ei maailman sijaintia, koska peli ei lähetä sitä
- pommit ja raketit, jotka on irrotettu (massa), osumat ja vastaanotettu vaurio, räjähdykset, konekiväärisarjat - sijainnit ovat lentokoneen suhteen paikallisia
- vastaava lentonopeus, AGL, pystynopeus, g, moottorin kierrosluku kerran sekunnissa, sekä kaikki muut indikaattorit, jotka paketti kantaa (imupaine, moottorin tärinä, vaihdetila ja paine, AoA, luisto, kiihtyvyys x/y/z, ohjaamon tärinä, läpät, ilmajarrut)
- lennot, ammutut kierrokset, pommit, raketit, vastaanotetut osumat, suurin nopeus, suurin g, lentoaika; palvelimen nimi ja lentäjän nimi verkossa
- jokainen telemetriapaketti kokonaisena heat.raw.parquet-tiedostossa

## Mistä data tulee {#where-it-comes-from}

pelin telemetrian UDP-tuloste osoitteeseen 127.0.0.1:41995 ([KEY = telemetrydevice] tiedostossa &lt;game>\data\startup.cfg)

## Miten se kytketään päälle {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (lisää addrN = "127.0.0.1:41995", enable = true), käynnistä IL-2 uudelleen

Kirjoita komento terminaaliin, joka on avattu watcherin kansiossa (katso [Ennen aloitusta](before-you-start.md)). Jos se epäonnistuu, viimeinen rivi kertoo syyn; [Asennus ja käynnistys](installing-and-running.md) kertoo yleisimmät syyt.

`python -m heat3d_watch setup il2` luettelee tiedostot, joita se muuttaisi; `python -m heat3d_watch setup il2 --apply` muuttaa ne ja säilyttää alkuperäisen nimellä `<file>.heat3d-backup` (katso [Komennot](commands.md#setup)). Se tulostaa `il2: changed: ...` jokaisesta muutoksesta tai `il2: nothing to change`, jos asetus on jo päällä.

## Miten se toimii {#how-it-works}

IL-2 Sturmovik: Great Battles - pelin telemetrian UDP-tuloste ja sen omat Tacview-tallenteet.

1. Telemetria ("Telemetry output of IL2 v4.003", revisio 1.2, toimitettu tiedostona
   `<game>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Kytketään päälle tiedostossa
   `<game>\data\startup.cfg`, osiossa `[KEY = telemetrydevice]`: `addr`,
   `addr1`, ... = "IP[:portti]" (useita kohteita kerralla), `decimation` (50 Hz /
   n), `enable`, `port`. `setup` lisää yhden kohteen, 127.0.0.1:41995 (JoyPro käyttää
   41994:ää, pelin oletus on 4322), ja kytkee tulosteen päälle. Paketit,
   little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Indikaattorit: 0 ENG_RPM, 1 ENG_MP, 2/3 moottorin tärinä, 4 LGEARS_STATE, 5
   LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz painovoima mukaan lukien), 9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14
   VERTICAL_SPEED (m/s). Tapahtumat (2 tavun pakattu): 0 SET_FOCUS (STRING: pituustavu
   + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float
   max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass,
   float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float
   pos[3]}, 4 DROP_BOMB ja 5 ROCKET_LAUNCH
   {float pos[3], float mass, WORD flags}, 6 HIT ja 7 DAMAGE {float pos[3],
   float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE
   gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long
   client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short
   coalition}. Tapahtumien sijainnit ovat pelaajan lentokoneen suhteen paikallisia; virrassa
   ei ole lainkaan maailman sijaintia - nämä ovat siis tapahtumia ja lukuja, ei rataa.

2. Tacview-tallenne: `tacviewrecord = 1` kohdassa `[KEY = track_record]` saa pelin
   kirjoittamaan `<game>\data\Tracks\*.acmi` (moninpelissä palvelin päättää).
   Valmis tiedosto muunnetaan: jokainen lentokone, ajoneuvo ja alus sijainteineen, synnyt ja
   poistuminen (tuhoutunut tai poissa), lentoonlähdöt ja laskeutumiset, kun tallenne ne sisältää. ACMI 2.x -tekstimuoto,
   tavallinen tai pakattu, kuten <https://www.tacview.net/documentation/acmi/en/> kuvaa - "#t"-rivit siirtävät kelloa,
   "id,Key=Value,..."-rivit asettavat ominaisuuksia (heksa-id:t, pilkut escapoitu "\\,"-muotoon, rivin lopussa oleva "\\" jatkaa riviä),
   "-id" poistaa kohteen, kohde 0 kantaa yleiset tiedot (ReferenceLongitude/Latitude, RecordingTime, ...) ja tapahtumat
   ("Event=Destroyed\|id\|text"). T = Lon\|Lat\|Alt[\|U\|V] tai
   Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], pituus- ja leveysaste suhteessa
   viitepisteeseen, tyhjät kentät ennallaan. Sijainnit menevät litteään karttaan viitepisteen ympärille:
   x itään, y korkeus, z pohjoiseen, metreinä. Viitepiste on session `geo`, joka kulkee meta.json-tiedostossa ja
   taulukon alatunnisteessa, jotta katseluohjelma voi asettaa oikean maailman ratojen alle.

Saman moduulin kautta toimii myös: [IL-2 Sturmovik: Great Battles (tallenteet)](game-il2-tacview.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennetaan | ei |
| Ylösakseli | `y` |
| Yksiköt | ei yksiköitä: telemetriassa ei ole maailman sijainteja |
| Peilattu katseluohjelmaa varten | ei mitään |
| Yksikköskaala (`scale`: katseluohjelma kertoo sijainnit tällä) | 1 |

Nämä menevät jokaisen session `meta.json`-tiedoston kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`-tiedoston alatunnisteeseen, joten 3DHeat-katseluohjelma kääntää ja skaalaa rivit itse - katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän muodossa "sallittu (lukee vain sen, minkä peli julkaisee)".
- Tyyppi `telemetry`: se lukee vain sen, minkä peli tai alusta antaa ulos (UDP-portin tai jaetun muistin, jonka peli julkaisee), joten se tallentaa myös verkkopelissä, aivan kuten offline-pelissäkin; lippu päättää vain sen, saako muistia koskaan lukea.
- Muisti: tämä sovitin **ei koskaan** lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliin, joka on merkitty pelatuksi verkossa - katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (jokaisen session `stats` `meta.json`-tiedostossa ja taulukossa `stats` tiedostossa `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohden). Avaimet, jotka koodi ottaa pelin kenttätaulukosta tai pelin omista tilastonimistä, eivät ole tässä luettelossa; "Mitä tallennetaan" -osio nimeää ne.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunnossääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): mitä lähde pitää sisällään, se luetaan tai tallennetaan, eikä sitä koskaan jätetä pois. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan muuttamattomana session `heat.raw.parquet`-tiedostoon (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja kaikki nimellä säilytetyt kentät; `used` merkitsee ne, mistä tuli myös rivejä), ja `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon - `lost` on 0.

**Luettu**

- SET_FOCUS (otettu lentokone: lento), DROP_BOMB ja ROCKET_LAUNCH (massa, paikallinen sijainti), HIT ja DAMAGE (paikallinen sijainti, voima), EXPLOSION (paikallinen sijainti, säde), GUN_FIRE (kierrosta kyselyä kohden) rivinä
- SETUP_ENG (index, id, paikallinen sijainti, suurin kierrosluku), SETUP_GUN (index, paikallinen sijainti, projektiilin massa, suuaukon nopeus) ja SETUP_LGEAR (index, id, paikallinen sijainti) rivinä: lentokoneen moottorit, aseet ja telineet, kun lento alkaa
- SRV_TITLE, SRV_ADDR, SRS_ADDR ja CLIENT_DAT (lentäjän nimi) meta.json-tiedostoon; CTRL_DATan joukkue lennon joukkueena
- kaikki spesifikaation viisitoista indikaattoria kerran sekunnissa olevalla `state`-rivillä (yksi arvo numerona, yksi per moottori, vaihdetelin tai akseli listana); suurin nopeus, g ja AGL jokaisesta paketista

**Tallennettu raakana**

- jokainen datagrammi kokonaisena `payload`-kenttänä Packet_ID:nsa alla: `0x54000101` telemetrialle (käytetty, kun se teki rivin tai meta.json-merkinnän), muu tunnus sellaisenaan, datagrammi, joka on liian lyhyt sen tulkitsemiseen, nimellä `short`
- mitä vain raakatiedostossa on: indikaattorit sekuntien välissä (peli lähettää ne 50 Hz / decimation), SETUP-tapahtuma, joka on lyhyempi kuin spesifikaation asettelu, tapahtumatunnukset, joita spesifikaatio ei luettele

**Ei saatavilla**

- maailman sijainti: telemetriatulosteessa sitä ei ole (tapahtumien sijainnit ovat lentokoneen suhteen paikallisia); il2-tacview-sovitin lukee sijainnit pelin omista Tacview-tallenteista
- muut lentokoneet ja pelaajat: tuloste kuvaa vain pelaajan oman lentokoneen

**Koko**: noin 8 MB tunnissa setupin 10 Hz:llä (decimation 5; paketti on noin 160 tavua plus kehys), 40 MB pelin täydellä 50 Hz:llä, ennen zstd:tä; zstd pienentää toistuvat floatit murto-osaan

## Testattu {#verified}

testattu paketeilla, jotka on rakennettu pelin oman Il2_TeleOutput-spesifikaation (rev 1.2) mukaan; startup.cfg-muokkaukset testattu tiedoston kopiolla; ei testattu käynnissä olevan pelin kanssa

## Lähde {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
