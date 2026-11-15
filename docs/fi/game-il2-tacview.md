---
title: "IL-2 Sturmovik: Great Battles (tallenteet)"
nav_order: 27
lang: "fi"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (tallenteet) {#il-2-sturmovik-great-battles-replays}

Kun IL-2 Sturmovik: Great Battles -ottelu päättyy, watcher muuttaa pelin tallentaman tallenteen tiedostoiksi, joita voit katsoa kartalta 3DHeat-katseluohjelmassa.

*Tekniset tiedot: sovitin `il2-tacview`, tyyppi [`replay`](sources-and-rules.md); se toimii koko ajan (ei odota pelin käynnistymistä) ja hakee uutta dataa 5 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- jokainen tallenteen lentokone, ajoneuvo ja alus: sijainnit kerran sekunnissa (metriä itään/ylös/pohjoiseen tallenteen viitepisteestä; leveys-, pituusaste ja korkeus sarakkeina)
- synnyt, tuhoutumiset (kuolema) ja poistumiset (left), lentoonlähdöt ja laskeutumiset, kun ne on tallennettu
- kohteet, tuhotut, lentoonlähdöt, laskeutumiset ja pituus tallenteittain
- jokainen tallenteen rivi kokonaisena heat.raw.parquet-tiedostossa, rivien kellossa

## Mistä data tulee {#where-it-comes-from}

pelin oman Tacview-tallenteet &lt;game>\data\Tracks\\\*.acmi (ACMI 2.x -teksti, tavallinen tai pakattu)

## Miten se kytketään päälle {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 kohdassa [KEY = track_record])

Kirjoita komento terminaaliin, joka on avattu watcherin kansiossa (katso [Ennen aloitusta](before-you-start.md)). Jos se epäonnistuu, viimeinen rivi kertoo syyn; [Asennus ja käynnistys](installing-and-running.md) kertoo yleisimmät syyt.

`python -m heat3d_watch setup il2-tacview` luettelee tiedostot, joita se muuttaisi; `python -m heat3d_watch setup il2-tacview --apply` muuttaa ne ja säilyttää alkuperäisen nimellä `<file>.heat3d-backup` (katso [Komennot](commands.md#setup)). Se tulostaa `il2-tacview: changed: ...` jokaisesta muutoksesta tai `il2-tacview: nothing to change`, jos asetus on jo päällä.

## Miten se toimii {#how-it-works}

IL-2 Sturmovik: Great Battles - pelin telemetriatuloste UDP:llä ja sen omat Tacview-tallenteet.

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

Saman moduulin kautta toimii myös: [IL-2 Sturmovik: Great Battles (reaaliaikadata)](game-il2.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennetaan | kyllä |
| Ylösakseli | `y` |
| Yksiköt | metriä (itään, korkeus, pohjoiseen ensimmäisestä kiinnityksestä) |
| Peilattu katseluohjelmaa varten | `z` |
| Yksikköskaala (`scale`: katseluohjelma kertoo sijainnit tällä) | 1 |

Nämä menevät jokaisen session `meta.json`-tiedoston kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`-tiedoston alatunnisteeseen, joten 3DHeat-katseluohjelma kääntää ja skaalaa rivit itse - katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän muodossa "sallittu (lukee vain sen, minkä peli julkaisee)".
- Tyyppi `replay`: se lukee vain sen, minkä peli tai alusta antaa ulos (pelin tallentamat tallenteet ja demot), joten se tallentaa myös verkkopelissä, aivan kuten offline-pelissäkin; lippu päättää vain sen, saako muistia koskaan lukea.
- Muisti: tämä sovitin **ei koskaan** lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliin, joka on merkitty pelatuksi verkossa - katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (jokaisen session `stats` `meta.json`-tiedostossa ja taulukossa `stats` tiedostossa `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohden). Avaimet, jotka koodi ottaa pelin kenttätaulukosta tai pelin omista tilastonimistä, eivät ole tässä luettelossa; "Mitä tallennetaan" -osio nimeää ne.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunnossääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): mitä lähde pitää sisällään, se luetaan tai tallennetaan, eikä sitä koskaan jätetä pois. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan muuttamattomana session `heat.raw.parquet`-tiedostoon (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja kaikki nimellä säilytetyt kentät; `used` merkitsee ne, mistä tuli myös rivejä), ja `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon - `lost` on 0.

**Luettu**

- jokaisen kohteen T (pituusaste, leveysaste, korkeus, kallistukset, pitch, yaw, U, V, suunta) sijaintina kerran sekunnissa kohdetta kohden, mukana Name, Type, Pilot, Coalition/Color, Country, Group ja Parent
- synnyt, poistumiset (kuolema, jos Destroyed-tapahtuma tuli ensin, muuten left), TakenOff- ja Landed-tapahtumat sekä Message- ja Bookmark-tapahtumat rivinä
- yleiset tiedot ReferenceLongitude/Latitude (kartan origo), RecordingTime/ReferenceTime (milloin), DataSource, DataRecorder ja Title meta.json-tiedostoon

**Tallennettu raakana**

- jokainen ei-tyhjä looginen rivi kokonaisena `text`-kentässä (rivi, jota jatketaan lopussa olevalla kenoviivalla, liitetään, kuten ACMI sen lukee), tyypinsä mukaan: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` ja `event` (kohde 0), `object` (id,Key=Value,...)
- mitä vain raakatiedostossa on: positiot sekuntien välissä, aseet, ammukset, soihdut, chaff ja muut kohteet, joita ei piirretä ratoina, jokainen muu ominaisuus (telemetria kuten IAS, AOA, kaasu, polttoaine, kun tallenne sen sisältää), muut yleiset tiedot (Comments, Briefing, Author, Category), luetut tapahtumat lukuunottamatta (Timeout, LeftArea, ...)

**Ei saatavilla**

- mitään, mitä tallenne ei sisällä; mitä peli ei kirjoita tallenteisiinsa, sitä niissä ei ole

**Koko**: tallenteen oma teksti ja noin 70 tavua per rivi ennen zstd:tä: 100 MB:n tallenne tekee noin 150-250 MB raakaa, jonka zstd pakkaa lähelle pakatun tallenteen kokoa

## Testattu {#verified}

testattu synteettisillä ACMI 2.2 -tiedostoilla (teksti ja pakattu); ei testattu pelin tallenteella

## Lähde {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
