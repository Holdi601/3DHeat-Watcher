---
title: "Steam-tilastot (alusta)"
nav_order: 42
lang: "fi"
source: game-steam-stats.md
source_hash: "09ecf3611c02"
nav_exclude: true
search_exclude: true
---
# Steam-tilastot (alusta) {#steam-statistics-platform}

Vahti tallentaa, mitä Steam-tilastot pitää peleistäsi, jotta voit myöhemmin katsella historiaasi tilastoina ja aikajanana.

*Tekniset tiedot: sovitin `steam-stats`, laji [`platform`](sources-and-rules.md); se toimii koko ajan (ei odota pelin alkua) ja etsii uutta dataa 30 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- jokainen tilasto, jonka peli tallentaa Steamiin (pelin omat nimet ja arvot), pelikohtaisesti kun se muuttuu
- saavutusten avaukset näyttönimineen, kuvauksineen ja avausaikoineen
- tilastomuutokset vanhoine arvoineen, uusine arvoineen ja erotuksineen
- pelattu aika (minuutteina, viimeiset kaksi viikkoa) ja viimeksi pelattu aika

## Mistä se tulee {#where-it-comes-from}

Steamin paikallinen tilasto-välimuisti %STEAM%\appcache\stats\UserGameStats_&lt;account>_&lt;appid>.bin, ja sen rinnalla UserGameStatsSchema_&lt;appid>.bin; pelattu aika tiedostosta %STEAM%\userdata\\&lt;account>\config\localconfig.vdf (%STEAM% saadaan rekisteristä HKCU\Software\Valve\Steam, arvo SteamPath)

## Miten se otetaan käyttöön {#how-to-switch-it-on}

Mitään ei tarvitse kytkeä päälle: vahti lukee lähteen sellaisena kuin peli tai alusta sen antaa.

## Miten se toimii {#how-it-works}

Mitä käynnistysohjelma ja näytönohjain pitävät yllä pelistä: Steamin tilastot, saavutukset, pelattu aika ja aikajanat sekä NVIDIAn kohokohdat ja klipit.

Mikään näistä lähteistä ei vaadi, että peli tekee yhteistyötä tai on käynnissä, joten tässä olevat kolme sovitinta ovat aina päällä ja katsovat muutamaa tiedostoa muutaman sekunnin välein.

#### Steam-tilastot (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<account>_<appid>.bin`, jonka Steam-asiakas kirjoittaa uudelleen aina kun peli tallentaa tilastonsa, ja se puretaan sen rinnalla olevalla skeemalla `UserGameStatsSchema_<appid>.bin` (binäärinen KeyValues, katso `_steam.py`). Tilastot ovat kokonaislukuja tai liukulukuja pelin määritelmän mukaan; saavutukset ovat bittejä, joiden avausaika on Unix-sekunteina. Pelattu aika on tiedostossa `<Steam>\userdata\<account>\config\localconfig.vdf` kohdassa apps/<appid>: Playtime ja Playtime2wks minuutteina, LastPlayed Unix-sekunteina. Steam löytyy rekisteristä kohdasta HKCU\Software\Valve\Steam, arvo SteamPath.
Tilasto-API: <https://partner.steamgames.com/doc/features/achievements>

Saman moduulin kautta toimivat myös: [NVIDIA-kohokohdat (alusta)](game-nvidia-highlights.md), [Steam Timeline (alusta)](game-steam-timeline.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennettu | ei |
| Ylösakseli | `y` |
| Yksiköt | metriä |
| Peilattu katselimelle | ei mitään |
| Yksikkömittakaava (`scale`: katselin kertoo sijainnit sillä) | 1 |

Nämä tulevat kunkin session `meta.json`-tiedoston kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`-tiedoston alatunnisteeseen, joten 3DHeat-katselin kääntää ja skaalaa rivit itse — katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **ei**. `games --markdown` näyttää tämän muodossa "single-player".
- Laji `platform`: se lukee vain sen, minkä peli tai alusta antaa ulos (minkä Steam tai näytönohjain pitää yllä), joten se tallentaa myös verkkopelissä eikä vain offline-pelissä; lippu päättää vain, saako muistia koskaan lukea.
- Muisti: **ei koskaan**. Tämä sovitin ei lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliltä, joka on merkitty pelatuksi verkossa — katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (kunkin session `stats` `meta.json`-tiedostossa ja `watcher.sqlite`-tiedoston `stats`-taulussa):

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohti). Avaimet, jotka koodi ottaa pelin kentistä tai pelin omista tilastonimistä taulukosta, eivät ole tässä luettelossa; kohdassa "Mitä tallennetaan" ne mainitaan.

## Täydellisyys {#completeness}

Vahti noudattaa 3DHeatin [muunnossääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): mitä lähde sisältää, se luetaan tai säilytetään, sitä ei koskaan pudoteta. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, säilytetään kokonaisena session `heat.raw.parquet`-tiedostossa (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja kaikki nimellä säilytetyt kentät; `used` merkitsee, mistä tuli myös rivejä). `meta.json`-tiedoston `selfCheck.completeness` laskee jokaisen `type`-arvon, ja `lost` on 0.

**Luettu**

- jokainen tilasto tilastotiedostosta API-nimellään (int, float, avgrate), jokainen saavutusbitti avausaikoineen, skeeman nimeämänä ja kuvaamana
- muutokset edelliseen lukuun verrattuna (vanha, uusi, erotus), uudet avaukset; pelattu aika, kahden viikon pelattu aika ja viimeksi pelattu localconfig.vdf-tiedostosta

**Säilytetään raakana**

- `UserGameStats`: tilastotiedoston tavut kokonaisena, joka kerta kun se tallennetaan (`crc`, `PendingChanges`, saavutusbitit, joita skeema ei enää määrittele, ja mikä tahansa avain, jonka purkaja ohittaa, ovat siinä)
- `UserGameStatsSchema`: skeematiedoston tavut sen vieressä, jotta tilastot voi purkaa pelkästä sessiosta (jokaisen tilaston ja saavutuksen nimet kaikilla kielillä, kuvakkeet, liput)
- `localconfig_app`: pelin koko lohko localconfig.vdf-tiedostosta JSON-muodossa (pilvisynkronoinnin tila, käynnistysasetukset, merkit ja jokainen muu avain, jonka Steam pitää pelikohtaisesti), kun sen pelattu aika tallennetaan
- tilastotiedosto, jota purkaja ei osaa lukea (katkaistu kesken kirjoituksen tai uusi asettelu): sen tavut ja skeema sessiossa ilman rivejä (`used` false; `unreadable` tiedostossa meta.json)

**Ei saatavilla**

- localconfig.vdf:n muu osa (kaverit, keskustelu, Steamin asetukset): ei pelin, ja yksityistä
- tilastoarvot kahden kirjoituksen välillä: Steam kirjoittaa tiedoston uudelleen, kun peli tallentaa tilastonsa, yleensä kun se sulkeutuu
- maailmanlaajuiset saavutusprosentit ja muiden pelaajien tilastot: ne ovat Steamin palvelimilla, eivät täällä

**Koko**: muutama kt per tallennettu pelikerta ja skeema (jopa muutamia satoja kt pelille, jossa on paljon saavutuksia), selvästi alle 1 MB per pelitunti; zstd pienentää skeeman tekstin puoleen tai enemmän.

## Todennettu {#verified}

Testattu oikeilla tilasto- ja skeematiedostoilla paikallisesta asennuksesta; muutosten havaitseminen testattu tiedostoilla, jotka on rakennettu binäärisessä KeyValues-muodossa.

## Lähde {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
