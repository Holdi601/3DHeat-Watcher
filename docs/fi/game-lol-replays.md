---
title: "League of Legends (replayt)"
nav_order: 30
lang: "fi"
source: game-lol-replays.md
source_hash: "ed26619fa904"
nav_exclude: true
search_exclude: true
---
# League of Legends (replayt) {#league-of-legends-replays}

Kun ottelu League of Legendsissa päättyy, watcher muuttaa pelin tallentaman replayn tiedostoiksi, joita voit katsoa kartalta 3DHeat-katseluohjelmassa.

*Tekniset tiedot: sovitin `lol-replays`, tyyppi [`replay`](sources-and-rules.md); se toimii koko ajan (ei odota pelin käynnistymistä) ja hakee uutta dataa 5 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- jokaisen pelaajan sankari, rooli, joukkue, tapot, kuolemat, avustukset, kulta, vahinko sankareille ja tulos sekä kaikki muut luvut pelin lopun tulostaulusta
- oma rivisi tilastoina, ja omat rivisi nimettyinä omiksi (meta.json `player`), Riot ID:si asetuksissa
- omalla Riot API -avaimellasi: jokaisen pelaajan sijainti minuutin välein minuutin tilastoineen sekä jokainen aikajanan tapahtuma (tapot siellä, missä ne tapahtuivat, rakennukset, hirviöt, vartijat, esineet, taidot) sen seinäkellon ajan mukaan, jonka aikajana antaa
- jokainen replay-tiedoston osa kokonaisena heat.raw.parquet-tiedostossa; ei dekoodattuna: liike hetkeltä toiselle, joka on salattu ja hämärretty huijaamisen estämiseksi

## Mistä data tulee {#where-it-comes-from}

replayt, jotka League-asiakasohjelma tallentaa: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (vain pelin lopun tavalliset metatiedot); omalla Riot API -avaimella ottelun virallinen aikajana Riotin Match-V5 API:sta

## Miten se kytketään päälle {#how-to-switch-it-on}

tallenna replay League-asiakasohjelmassa (otteluhistoria > lataa) ja asenna lukija: github.com/Holdi601/3DHeat-Ext-Riot (`heat3d-riot-replays`); sijainteja varten aseta riot_api_key ja riot_platform komennolla `config --set`

Asetukset ympäristömuuttujista:

- `HEAT3D_RIOT_REPLAYS`: lukijan kansio (kloonaus tai purettu julkaisu), kun se ei ole asennettu tai watcherin vieressä

## Miten se toimii {#how-it-works}

League of Legends- ja Valorant-replayt: se osa, joka niistä voidaan lukea sellaisenaan.

Molemmat pelit tallentavat replayt pelaajan levylle, ja molemmat suojaavat sisältönsä:
hetkeltä toiselle tapahtuva pelidata on hämärretty, ja hämäröinti vaihtuu joka päivityksen mukana,
jotta sitä ei voi käyttää huijaamiseen. Sen murtaminen tarkoittaisi pelin oman koodin purkamista, mitä Riotin
käyttöehdot kieltävät (käyttöehdot 3.1 ja 7.1) - joten 3DHeatissa sitä ei tehdä missään. Se, mitä kukin tiedosto
kertoo avoimesti, luetaan, ja loppu tallennetaan sellaisenaan: jokainen tiedoston osa kokonaisena
session `heat.raw.parquet`-tiedostossa (3DHeatin muunnossääntö, docs/converters.md katseluohjelman
repositoriossa), ja se lasketaan meta.json:n `selfCheck.completeness`-kentässä.

Watcher ei lue tiedostoja itse: sen tekee ulkoinen lukija (3DHeat
Riot, github.com/Holdi601/3DHeat-Ext-Riot, `exporters/ext/riot-replays`,
komento `heat3d-riot-replays`). Se on erillään, jotta Riotin ehtoihin liittyvä ongelma
koskee vain sitä. Jos lukija löytyy PATHista, on asennettu tai watcherin vieressä, se lukee jokaisen uuden replayn;
jos sitä ei ole, watcher kertoo kerran, miten se asennetaan. Mitä lukija lukee, sen watcher tallentaa
sessioon; alla oleva Match-V5-aikajana haetaan watcherin itsensä toimesta, koska sitä ei ole tiedostossa.

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Molemmat konttiversiot kantavat pelin lopun
tulostaulun avoimena JSON-tekstinä (`statsJson`): jokaiselle kymmenelle pelaajalle sankarin, tapot, kuolemat,
avustukset, kullan, vahingon sankareille, esineet, joukkueen, roolin, voiton, heidän Riot ID:nsä ja jokaisen muun luvun,
jonka peli laskee yhteen (yli sata pelaajaa kohden); kaikki nämä tulevat pelaajan
`player_result`-riviksi. ROFL1 (versio 14.9 ja sitä vanhemmat) on kiinteän otsikon jälkeen (`RIOT\0\0`, 256 tavun
allekirjoitus, sitten pituudet); ROFL2 (14.11 alkaen, `RIOT\2\0`) tiedoston lopussa, sen pituus viimeisissä neljässä tavussa
(Riotin insinöörin kertoma, ReplayBook-ongelma 299). ROFL1:n payload-otsikko (pelin tunnus, pituus, osien ja keyframe-kehysten
määrät, osan avainen pituus) ja sen osataulukko (tunnus, tyyppi, pituus, seuraava osa, offset) ovat avoimia ja luetaan; osat itse ovat
salattuja ja tallennetaan kokonaisina lukematta.

Sijainnit eivät tule tiedostosta. Pelaajan oman Riot-kehittäjäavaimen kanssa (`riot_api_key` asetuksissa; henkilökohtainen avain on tarkoitettu juuri tähän,
"showing (self) player stats") ottelun virallinen aikajana haetaan Riotin Match-V5 API:sta: jokaisen pelaajan sijainti kerran minuutissa
kaikkine minuutin kehyksen kertomine tietoineen (kulta, kokemus, taso, minionit, sankarin ja vahingon tilastot), ja jokainen aikajanan tapahtuma -
tapot, rakennukset, eliittihirviöt, vartijat, esineet, taidot, tasot - rivinä, siinä missä se tapahtui, kun paikka on tiedossa. Ilman avainta ei haeta mitään eikä lähetetä mitään.

Samaa moduulia käyttää myös: [VALORANT (replayt)](game-valorant-replays.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennetaan | kyllä |
| Ylösakseli | `y` |
| Yksiköt | Summoner's Rift -kartan yksiköt (noin 15000 poikki) |
| Peilattu katseluohjelmaa varten | ei mitään |
| Yksikköskaala (`scale`: katseluohjelma kertoo sijainnit tällä) | 1 |

Nämä menevät jokaisen session `meta.json`-tiedoston kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`-tiedoston alatunnisteeseen, joten 3DHeat-katseluohjelma kääntää ja skaalaa rivit itse - katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän muodossa "sallittu (lukee vain sen, minkä peli julkaisee)".
- Tyyppi `replay`: se lukee vain sen, minkä peli tai alusta antaa ulos (pelin tallentamat tallenteet ja demot), joten se tallentaa myös verkkopelissä, aivan kuten offline-pelissäkin; lippu päättää vain sen, saako muistia koskaan lukea.
- Muisti: tämä sovitin **ei koskaan** lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliin, joka on merkitty pelatuksi verkossa - katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (jokaisen session `stats` `meta.json`-tiedostossa ja taulukossa `stats` tiedostossa `watcher.sqlite`):

`champion`, `game_seconds`, `won`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohden). Avaimet, jotka koodi ottaa pelin kenttätaulukosta tai pelin omista tilastonimistä, eivät ole tässä luettelossa; "Mitä tallennetaan" -osio nimeää ne.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunnossääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): mitä lähde pitää sisällään, se luetaan tai tallennetaan, eikä sitä koskaan jätetä pois. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan muuttamattomana session `heat.raw.parquet`-tiedostoon (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja kaikki nimellä säilytetyt kentät; `used` merkitsee ne, mistä tuli myös rivejä), ja `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon - `lost` on 0.

**Luettu**

- metatiedot JSON-muodossa: pelin pituus, versio, viimeisen osan ja keyframe-tunnukset sekä `statsJson` - jokaisen pelaajan tulostaulun jokainen kenttä omalla `player_result`-rivillään (luvut tekstinä luetaan lukuina)
- ROFL1: pituuslohko, payload-otsikko (pelin tunnus, pelin pituus, keyframe- ja osamäärät, käynnistys- ja pelin alun osatunnukset, keyframe-väli, osan avain tallennettuna) ja osataulukko (tunnus, tyyppi, pituus, seuraava osa, offset) - meta.json:ssa `rofl` ja raakarivien `text`-kentässä
- ROFL2: versiomerkkijono
- Match-V5-aikajana (vain oma API-avain): jokainen osallistujakehys `position`-rivinä (tai `participant_frame`, kun paikkaa ei ole) kaikkine kenttineen litistettynä (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...); jokainen tapahtuma rivinä tyyppinsä nimellä, sijoitettuna siihen, missä sillä on `position`; CHAMPION_KILL tappona ja kuolemana

**Tallennettu raakana**

- jokainen .rofl-tiedoston osa kokonaisena tiedoston järjestyksessä (`offset`), joten osat ovat tiedosto: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); jokainen tavujono, jota mikään osa ei kata, nimellä `unknown`
- aikajana kokonaisena: `timeline <type>` jokaiselle tapahtumalle, `timeline participantFrame` jokaisen pelaajan kehykselle (`participant` on hänen tunnuksensa), `timeline` muille

**Ei saatavilla**

- itse peli (sijainnit, kyvyt, jokainen yksikkö hetkeltä toiselle): ROFL1:n osat ja ROFL2:n body ovat salattuja, ja paketit niiden sisällä hämärretään jokaisen päivityksen mukana; niiden läpi pääsy tarkoittaisi asiakasohjelman purkamista, mitä Riotin käyttöehdot kieltävät (3.1, 7.1). Tallennettu kokonaisena, ei luettu
- sijainnit ilman omaa Riot API -avainta: tiedostossa niitä ei ole avoimena

**Koko**: raakatallenne on noin replayn oman kokoinen: salatut osat eivät pakkaudu

## Testattu {#verified}

lukija (heat3d-riot-replays) testattu tiedostoilla, jotka on rakennettu roflxd.cs:n (MIT) kuvaamien asetteluiden mukaan; aikajana Match-V5:n dokumentoitua JSONia vasten; oikeaa replayta ei ollut saatavilla tarkistettavaksi

## Lähde {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
