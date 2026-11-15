---
title: "Dota 2 (toistot)"
nav_order: 12
lang: "fi"
source: game-dota-replays.md
source_hash: "c0ed25c261f6"
nav_exclude: true
search_exclude: true
---
# Dota 2 (toistot) {#dota-2-replays}

Kun Dota 2 -ottelu on päättynyt, watcher muuttaa pelin tallentaman toiston tiedostoiksi, joita voit katsoa kartalla 3DHeat-katselimessa.

*Tekniset tiedot: adapteri `dota-replays`, tyyppi [`replay`](sources-and-rules.md); se toimii koko ajan (ei odota pelin käynnistymistä) ja etsii uutta dataa 5 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- jokaisen sankarin sijainti, korkeus, terveys ja taso 7,5 kertaa sekunnissa, kun hän on elossa
- tappot ja kuolemat siellä, missä ne tapahtuivat; tornit, kasarmit, Roshan ja Tormentorit siellä, missä ne kaatuivat; vartiot siellä, missä ne asetettiin
- jokaisen pelaajan kartta-merkinnät, piirrokset ja käskyt (liiku, hyökkää, loitsu, osta ...) siellä, minne ne osoittivat
- pistemäärä ja jokaisen pelaajan rivi; kirjautuneen pelaajan rivi tilastoina
- kaikki muu, mitä toisto sisältää, säilytettynä kokonaisena taulun rinnalla: jokainen kehys ja verkkoviesti, jokainen entiteettimuutos ja jokainen merkkijonotaulun merkintä

## Mistä tiedot tulevat {#where-it-comes-from}

Dota 2:n tallentamat toistot: &lt;Dota>/game/dota/replays/&lt;match id>.dem (ladattu asiakkaassa tai komennolla `dota-replay <match id>`)

## Kuinka se käynnistetään {#how-to-switch-it-on}

lataa ottelun toisto Dota 2:ssa tai hae julkinen toisto: `python -m heat3d_watch dota-replay <match id>`. Asenna lukija: github.com/Holdi601/3DHeat-Ext-DotaReplay (`heat3d-dota-replay`, tuo mukanaan gem-dota)

Kirjoita komento terminaaliin, joka on avattu watcherin kansiossa (katso [Ennen aloittamista](before-you-start.md)). Jos se epäonnistuu, viimeinen rivi kertoo syyn; [Asennus ja käynnistys](installing-and-running.md) kattaa yleisimmät syyt.

Asetukset ympäristömuuttujista:

- `HEAT3D_DOTA_REPLAY`: lukijan kansio (kloonattu tai purettu julkaisu), kun se ei ole asennettu tai watcherin vieressä

## Miten se toimii {#how-it-works}

Toistot ja demot: se, minkä peli tallentaa ottelusta, muunnettuna kerran ottelun päätyttyä.

Toisto sisältää kaiken, mitä elävä käyttöliittymä pitää moninpeleissä piilossa: jokaisen pelaajan sijainnin ja jokaisen tappon siellä, missä se tapahtui. Se on tiedosto, jonka peli kirjoittaa pelaajilleen, joten sen lukeminen ei koske peliin mitenkään. Watcher katsoo kansioita, joihin pelit tallentavat toistot, odottaa, että uusi tiedosto lakkaa kasvamasta (muuten peli vielä kirjoittaa sitä), ja muuntaa sen työsäikeessä. Pitkä muunnos ei siis pysäytä muuta watcheria.

Kun kansio nähdään ensimmäisen kerran, siinä jo olevia toistoja vain merkitään, eikä niitä muunneta. Muuten watcher olisi kiireinen päivän ajan kenellä tahansa, jolla on vuosien demot. Komento `python -m heat3d_watch replays <adapter> [folder]` muuntaa olemassa olevat toistot pyynnöstä.

#### Dota 2 {#dota-2}

Dota 2 tallentaa toistot, jotka pelaaja lataa (ottelun tiedot tai Watch > Replays), tiedostoon `<Dota>/game/dota/replays/<match id>.dem`. Valve säilyttää jokaisen julkisen ottelun toiston palvelimillaan muutaman viikon ajan. Komento `python -m heat3d_watch dota-replay <match id>` hakee toiston tunnuksella OpenDotan kautta. Watcher ei lue niitä itse: ulkoinen lukija lukee (3DHeat Dota Replay, github.com/Holdi601/3DHeat-Ext-DotaReplay, `exporters/ext/dota-replay`, komento `heat3d-dota-replay`, lukee gem-dota:n kautta, MIT-lisenssi). Lukija on erillään, jotta sen ongelma ei koske mitään muuta. Se ajetaan omassa prosessissaan jokaiselle uudelle toistolle, kun se on PATHissa, asennettuna tai watcherin vieressä. Jos se puuttuu, watcher kertoo kerran, miten se asennetaan. Lukija kirjoittaa jokaisen sankarin sijainnin, korkeuden, terveyden, tason, katseen suunnan, manan, kokemuksen, ominaisuudet ja esineet 7,5 kertaa sekunnissa, kun hän on elossa. Se kirjoittaa myös tappot ja kuolemat siellä, missä ne tapahtuivat, tornit, kasarmit, Roshanin ja Tormentorit siellä, missä ne kaatuivat, jokaisen vartion siellä, missä se asetettiin ja missä se päättyi, taistelulokin merkinnät sankareista (vahinko, parannukset, loitsut, esineet, ostot, runet, kulta, kokemus, muokkaajat) sekä jokaisen pelaajan kartta-merkinnät, piirrokset ja käskyt. Ne menevät tiedostoon `dota/<match>.parquet`. Muut yksiköt (oliot, kesyt, kuvat, kouririt, rakennukset) kirjoitetaan kerran sekunnissa tiedostoon `<match>.units.parquet`. Koko taistelulokki menee tiedostoon `<match>.combatlog.parquet`. Ottelu, chat, draft, kaikki muu lukijan purkama ja pelin oma ottelun päätöstiedot menevät tiedostoon `<match>.match.json` session kansioon. Kaikki muu, mitä toisto sisältää, säilytetään kokonaisena näiden rinnalla (3DHeatin muuntimen sääntö): jokainen kehys ja verkkoviesti tiedostossa `<match>.packets.parquet`, jokainen entiteettiominaisuuden muutos tiedostossa `<match>.entities.parquet` ja jokainen merkkijonotaulun merkintä tiedostossa `<match>.strings.parquet`. Ne lasketaan ottelun asiakirjan kohdassa `selfCheck.completeness`. Sijainnit ovat Dota-maailmayksiköitä, samat kuin pelin game-state integration ilmoittaa. Kirjautuneen pelaajan tulosrivistä tulee session tilastot: tappot, kuolemat, avustukset, viimeiset osumat, denies, nettoarvo, GPM, XPM, sankarivahinko, vartiot ja se, voitettiinko ottelu. Uusi Dota-päivitys voi muuttaa toiston entiteettejä ennen kuin gem seuraa perässä. Toisto, jonka gem ei pysty lukemaan loppuun, muunnetaan niin pitkälle kuin pystytään, ja se merkitään yhteenvedossä `incomplete`-tunnisteella.

Sama moduuli palvelee myös: [Counter-Strike 2 (toistot)](game-cs2-demos.md), [Squad (toistot)](game-squad-demos.md), [War Thunder (toistot)](game-warthunder-replays.md), [World of Tanks (toistot)](game-wot-replays.md), [World of Warships (toistot)](game-wows-replays.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennettu | kyllä |
| Ylösakseli | `z` |
| Yksiköt | Dota-maailmayksiköt (Hammer-yksiköt; kartta on noin 16400 yli) |
| Peilattu katselimelle | `y` |
| Yksikkökerroin (`scale`: katselin kertoo sijainnit sillä) | 1 |

Nämä menevät kunkin session `meta.json`-tiedostoon (`axes`) ja, kun sessiossa on sijainteja, tiedoston `heat.parquet` alatunnisteeseen. Siksi 3DHeat-katselin kääntää ja skaalaa rivit itse; katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän tekstillä "allowed (reads only what the game publishes)".
- Tyyppi `replay`: se lukee vain sen, minkä peli tai alusta luovuttaa (toistot ja demot, jotka peli tallentaa). Se tallentaa siis myös verkkopelit, samoin kuin offline-pelit. Lippu päättää vain, saako muistia koskaan lukea.
- Muisti: **ei koskaan**. Tämä sovitin ei lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan verkkopeliksi merkitystä pelistä. Katso [Lähteet ja säännöt](sources-and-rules.md).

## Tallennetut tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (kunkin session `stats` tiedostossa `meta.json` ja `watcher.sqlite`-tiedoston taulussa `stats`):

`duration`, `hero`, `score.{team}`, `team`, `won`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohden). Avaimet, jotka koodi ottaa pelin kenttien taulukosta tai pelin omista tilastonimistä, eivät ole tässä luettelossa; yllä oleva "Mitä tallennetaan" -osio nimeää ne.

## Täydellisyys {#completeness}

Muunnin noudattaa 3DHeatin [muuntimen sääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): toistossa oleva tieto luetaan tai säilytetään, sitä ei koskaan jätetä pois. Taulun lisäksi kaikki muu, mitä toisto sisältää, säilytetään kokonaisena sen sivutiedostoissa session kansiossa `dota/`: `<match>.packets.parquet`, `<match>.entities.parquet`, `<match>.strings.parquet` (sarakkeet `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, kun kukin on käytössä). Ottelun asiakirjan (`<match>.match.json`) kohta `selfCheck.completeness` laskee jokaisen `type`-arvon määrän, ja `lost` on 0.

**Luetaan**

- taulu (`dota/<match>.parquet`): jokaisen sankarin sijainti, korkeus, terveys, taso, katseen suunta, mana, kokemus, ominaisuudet, panssari, nopeus, vahinko, esineet ja pelaajan kohdistin 7,5 kertaa sekunnissa; tappot, kuolemat, tavoitteet, vartiot, taistelulokin merkinnät sankareista; kartta-merkinnät (`ping`, DOTA_UM_LocationPing), kartta-piirrokset (`map_line`, DOTA_UM_MapLine) ja jokainen yksikkökäsky (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` käskyn tyyppi, `value` loitsun tai esineen tunnus, `text` kohteen luokka; käskyn kohdepisteessä, muuten sankarin kohdalla)
- `<match>.units.parquet`: jokainen muu yksikkö kerran sekunnissa; `<match>.combatlog.parquet`: koko taistelulokki sellaisena kuin gem sen lukee, jokainen kenttä
- ottelun asiakirja: kaikki, minkä gem purkaa, ja toiston omat tietueet kokonaisina: `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: toiston pituus, jokaisen pelaajan nimi, sankari, Steam-tunnus, joukkue), `matchDetails` (DOTA_UM_MatchDetails: pelipalvelimen ottelun lopun tulostaulu, jokaisen pelaajan luvut, esineet, vahinko tyypeittäin, valinnat ja kiellot) sekä `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: tappot, kuolemat, avustukset, taso, viimeiset osumat ja denies virrasta luettuina ja verrattuina `matchDetails`-tietoon, pelaajittain

**Säilytetään raakana**

- `<match>.packets.parquet`: jokainen kehys, joka ei ole paketti (`type` `frame <n>`), ja jokainen verkkoviesti (`message <n>`, `name` Valven nimi), kokonaisena kentässä `payload` tiedoston järjestyksessä (`seq`, `frame`). `decoded` on protobuf JSON-muodossa (tavukenttä annetaan pituutensa kanssa). Jokainen viestityyppi on purettu: svc_PacketEntities (entiteettivirta), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, taistelulokin viestit, GE_SosStartSoundEvent, DOTA_UM_TE_* (ammukset, animaatiot, veri), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick ja muut. Lähetystaulukot, luokkalista ja palvelimen tiedot, joita myöhempi entiteettidekooderi tarvitsee, ovat näiden joukossa
- `<match>.entities.parquet`: jokaisen entiteetin jokainen ominaisuus joka kerta, kun se muuttui (`type` ominaisuus, `name` luokka, `entity` sen indeksi; `value`, `vector` tai `decoded`), sen koko tila luotaessa sekä jokainen luonti, sisääntulo, poistuminen ja tuhoutuminen. Koko ottelusta tulee miljoonia rivejä
- `<match>.strings.parquet`: jokainen merkkijonotaulun merkintä jokaisesta päivityksestä ja jokaisesta koko tilannekuvasta, arvo kokonaisena; `userinfo`, `ActiveModifiers` ja `EconItems` purettuina niiden protobufeista
- ottelun asiakirjan `selfCheck.completeness` laskee kehykset ja viestit Valven nimellä, taistelulokin merkinnät (`combatlog <type>`), pelitapahtumat (`gameevent <name>`), merkkijonotaulun merkinnät (`stringtable <name>`) ja entiteettipäivitykset (`entity <class>`). Muutama säilytetään vain raakana (kokonaiset entiteettikuvat, jotka gem ohittaa, koska se rakentaa tilan muutoksista, ja taulujen merkinnät, joiden arvoja mikään ei lue). Lost on 0.

**Ei saatavilla**

- ääni: toistossa on äänen asetukset, mutta ei äänidataa
- nimet hajautusten ja tunnusten takana: äänet ja partikkelit on nimetty pelin tiedostojen hajautusarvoilla, kyvyt tunnuksilla. Toisto ei kanna nimiä. Esineet nimetään gem:n luettelon kautta, kun sillä on ne
- kaikki, minkä vain pelaajien omat asiakkaat tiesivät (heidän kameransa, heidän ruutunsa), palvelimen lähettämän lisäksi. Kohdistin ja jokainen käsky ovat mukana

**Koko**: lisätiedostot yhteensä ovat hieman itse toistoa suurempia, suurimmat ovat paketit ja entiteetit. Koko ottelu vie yhdessä prosessissa minuutin tai kaksi.

## Todennettu {#verified}

tarkistettu julkisen ottelun toistolla: tappot, kuolemat, avustukset, taso, viimeiset osumat ja denies täsmäävät pelin oman ottelun lopun tietueen kanssa kaikille kymmenelle pelaajalle. Jokainen viesti paketti-lisätiedostossa serialisoituu takaisin tavu tavulta. Taulu ja tilastot on testattu synteettisellä datalla.

## Lähde {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
