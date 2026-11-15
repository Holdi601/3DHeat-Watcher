---
title: "Minecraft (lokitiedostot)"
nav_order: 33
lang: "fi"
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (lokitiedostot) {#minecraft-log-files}

Kun pelaat Minecraftia, watcher lukee pelin kirjoittamat tiedostot ja tallentaa, mitä tapahtui, jotta voit katsoa sitä myöhemmin kartalta 3DHeat-katseluohjelmassa.

*Tekniset tiedot: sovitin `minecraft`, tyyppi [`log`](sources-and-rules.md); se toimii, kun `javaw.exe` tai `java.exe` on käynnissä, ja hakee uutta dataa 0,5 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- oman ja muiden pelaajien sijainti (lohkot = m, y ylös) joka kerta, kun maailma tallentuu, ulottuvuus istuntona
- syntymä sijaintineen, kun pelaaja kirjautuu (integroituun) palvelimeen
- liittymiset, poistumiset, kuolemat kuolemaviesteineen, edistymiset, chat-rivit
- kuolemat, edistymiset, chat-viestit; tilastotiedostosta: pelin kesto, matka, mob- ja pelaajatappot, hypyt, vahinko, louhitut lohkot, valmistetut esineet (tämän session osuus)
- jokainen lokirivi ja jokainen tallennettu tilasto-, edistymis- ja pelaajatiedosto kokonaisena heat.raw.parquet-tiedostossa

## Mistä data tulee {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (seurataan), saves\\&lt;world>\stats\\&lt;uuid>.json ja saves\\&lt;world>\playerdata\\&lt;uuid>.dat / level.dat (gzip NBT), luetaan, kun peli tallentaa ne

## Miten se kytketään päälle {#how-to-switch-it-on}

Mitään ei tarvitse kytkeä: watcher lukee lähteen sellaisena kuin peli tai alusta sen antaa.

## Miten se toimii {#how-it-works}

Minecraft (Java Edition): lokit, tilastot ja pelaajatiedostot, jotka peli kirjoittaa.

Sijainti (`%APPDATA%\.minecraft\`):

* `logs\latest.log` - pelin loki, uusi jokaisella käynnistyskerralla (vanha pakataan
  päivätyksi .log.gz-tiedostoksi). Rivit `[hh:mm:ss] [thread/LEVEL]: message`
  (modi-lataajat kirjoittavat `[ddMMMyyyy hh:mm:ss.mmm] [thread/LEVEL] [logger/]: ...`).
  Chatissa näkyvä teksti on siinä: liittymiset ja poistumiset, kuolemaviestit,
  edistymiset, chat - yhden pelaajan maailman integroitu palvelin kirjoittaa
  samat rivit vielä kerran, joten saman sekunnin sisällä toistuva rivi lasketaan
  kerran. "Setting user: &lt;name>" nimeää pelaajan; palvelimen
  "&lt;name>[...] logged in with entity id N at (x, y, z)" kertoo, missä he
  ilmestyivät.
* `saves\<world>\stats\<uuid>.json` - tilastonäyttö, kirjoitetaan kun maailma tallentuu
  (automaattitallennus muutaman minuutin välein ja poistuttaessa): `stats` ->
  `minecraft:custom` (play_time tikkeinä, mob_kills, \*_one_cm-matkat, jump,
  ...), `minecraft:mined`, `minecraft:crafted`, ... Maailman kokonaissummat; session
  luvut ovat erotus siihen, mitä tiedosto sanoi, kun peli käynnistyi. Muoto: <https://minecraft.wiki/w/Statistics>
* `saves\<world>\playerdata\<uuid>.dat` (ja `level.dat` -> Data -> Player
  yksinpelin isännälle) - gzip-pakattu NBT, kirjoitetaan samoilla tallennuksilla:
  `Pos` [x, y, z] doubleina, `Rotation` [yaw, pitch], `Dimension`
  ("minecraft:overworld"; int 0/-1/1 ennen versiota 1.16). NBT: <https://minecraft.wiki/w/NBT_format> - luetaan tässä omalla pienellä lukijalla.
* `saves\<world>\advancements\<uuid>.json` - edistymisnäytön edistyminen,
  kirjoitetaan samoilla tallennuksilla.

Koordinaatit ovat lohkoja, yksi lohko metri, y ylös; x itään, z etelään - oikeakätinen
koordinaatisto, piirretään sellaisena kuin se on. Sijainnit tulevat vain maailman tallentuessa, joten reitti on
muutama piste automaattitallennusta kohden, ei jälki; ulottuvuus on `session`, joten Nether ei piirry Overworldin päälle.

Kaikki luettu tallennetaan kokonaisena session raakatiedostoon (3DHeatin muunnossääntö):
jokainen lokirivi tasonsa nimellä (`INFO`, `WARN`, `ERROR`, ...; rivi ilman hakasulkuista alkua, kuten pinojälki,
nimellä `untagged`), ja jokainen tallennettu tiedosto tyypillään (`stats`, `advancements`, `playerdata`,
`level.dat`) - JSON tekstinä, NBT tavuina. Tilastotiedoston luvut ymmärtää vain
vasten sitä, mitä se sanoi pelin käynnistyessä, joten myös ensimmäinen kopio tallennetaan (`baseline`),
kun tiedosto muuttuu ensimmäisen kerran.

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennetaan | kyllä |
| Ylösakseli | `y` |
| Yksiköt | lohkoja (1 lohko = 1 m) |
| Peilattu katseluohjelmaa varten | ei mitään |
| Yksikköskaala (`scale`: katseluohjelma kertoo sijainnit tällä) | 1 |

Nämä menevät jokaisen session `meta.json`-tiedoston kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`-tiedoston alatunnisteeseen, joten 3DHeat-katseluohjelma kääntää ja skaalaa rivit itse - katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän muodossa "sallittu (lukee vain sen, minkä peli julkaisee)".
- Tyyppi `log`: se lukee vain sen, minkä peli tai alusta antaa ulos (tiedostot, joita peli kirjoittaa sen käydessä), joten se tallentaa myös verkkopelissä, aivan kuten offline-pelissäkin; lippu päättää vain sen, saako muistia koskaan lukea.
- Muisti: tämä sovitin **ei koskaan** lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliin, joka on merkitty pelatuksi verkossa - katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (jokaisen session `stats` `meta.json`-tiedostossa ja taulukossa `stats` tiedostossa `watcher.sqlite`):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohden). Avaimet, jotka koodi ottaa pelin kenttätaulukosta tai pelin omista tilastonimistä, eivät ole tässä luettelossa; "Mitä tallennetaan" -osio nimeää ne.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunnossääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): mitä lähde pitää sisällään, se luetaan tai tallennetaan, eikä sitä koskaan jätetä pois. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan muuttamattomana session `heat.raw.parquet`-tiedostoon (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja kaikki nimellä säilytetyt kentät; `used` merkitsee ne, mistä tuli myös rivejä), ja `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon - `lost` on 0.

**Luettu**

- latest.log: pelaajan nimi (`Setting user`), kirjautumiset sijainteineen, liittymiset, poistumiset, kuolemat kuolemaviesteineen, edistymiset, chat-rivit, palvelimen pysähtyminen
- stats/&lt;uuid>.json: pelin kesto, matka, mob- ja pelaajatappot, hypyt, annettu ja saatu vahinko, louhitut lohkot, valmistetut esineet - tämän session osuus
- playerdata/&lt;uuid>.dat ja level.dat (NBT): sijainti, ulottuvuus, yaw, pitch, terveys, XP-taso

**Tallennettu raakana**

- jokainen latest.log-rivi kokonaisena, `type` = sen taso (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`) ja säikeen nimi kentässä `thread`, `used` siinä, mistä tuli rivi; rivi ilman hakasulkuista alkua (pinojälki, modin banneri) nimellä `untagged`
- jokainen stats/&lt;uuid>.json kokonaisena tekstinä, `type` `stats` (`used`: sen luvut ovat tilastoissa), ja sen ensimmäinen kopio pelin alusta nimellä `baseline`
- jokainen advancements/&lt;uuid>.json kokonaisena tekstinä, `type` `advancements` (jokainen kriteeri ja sen täyttymisaika; ei vielä tehty riveiksi)
- jokainen playerdata/&lt;uuid>.dat ja level.dat kokonaisena tavuina (gzip-NBT), `type` `playerdata` / `level.dat`, `used` siinä, mistä tuli sijainti: inventaario, ender-arkku, tehosteet, syntymäpiste, pelisäännöt, maailman siemen ja kellonaika ovat vain täällä
- jokaisessa tallennetussa tiedostossa `world` ja `file` (sen polku kansiossa `saves`)

**Ei saatavilla**

- sijaintijälki: peli kirjoittaa pelaajan sijainnin vain maailman tallentuessa (muutaman minuutin välein ja poistuttaessa)
- sijainnit palvelimella, jonka joku muu isännöi: sen maailman tiedostot ovat palvelimella, ei täällä; silloin luetaan vain loki
- maailma itse (region .mca-tiedostot, entiteetit, data/\*.dat-kartat ja raidit): suuri, ja se on maasto, ei pelaaminen
- aiempien sessioiden lokit (logs/\*.log.gz): tallennetaan, kun niitä pelattiin
- Bedrock Edition: se ei kirjoita tällaista lokia tai tiedostoja

**Koko**: latest.log 0,1-2 MB tunnissa (enemmän modien kanssa); tilastotiedosto 5-50 KB ja pelaajatiedosto 5-100 KB automaattitallennusta kohden, level.dat 1-20 KB - yhteensä noin 1-5 MB tunnissa; zstd heat.raw.parquet-tiedostossa tekee tekstistä noin kymmenesosan (NBT-tiedostot ovat jo gzip-pakattuja)

## Testattu {#verified}

testattu synteettisillä lokiriveillä, stats-JSONilla ja NBT-tiedostoilla, jotka on rakennettu julkaistujen muotojen mukaan; ei testattu pelin kanssa

## Lähde {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
