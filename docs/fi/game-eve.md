---
title: "EVE Online (lokitiedostot)"
nav_order: 20
lang: "fi"
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (lokitiedostot) {#eve-online-log-files}

Kun pelaat EVE Onlinea, watcher lukee pelin kirjoittamat tiedostot ja tallentaa, mitä tapahtui, jotta voit myöhemmin katsoa sen tilastoina ja aikajanana.

*Tekniset tiedot: sovitin `eve`, tyyppi [`log`](sources-and-rules.md); se toimii, kun `exefile.exe` on käynnissä, ja etsii uutta dataa 0,5 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- vahinko annettu ja saatu toisen aluksen kanssa, lentäjä, yhtiön lyhenne, ase ja osuman laatu
- ohilaukaukset annettuina ja saatuina
- palkkiot maksettuina (NPC-tapot) ISK:ssa
- hypyt järjestelmien välillä
- jokainen gamelog- ja chat-lokirivi sellaisenaan tiedostossa heat.raw.parquet
- vahinko annettu ja saatu, osumat, ohilaukaukset, palkkiotapot ja ISK, hypyt

## Mistä data tulee {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt ja niiden vieressä Chatlogs\\\*.txt (jokainen tiedosto, joka on kirjoitettu asiakkaan käynnistyksestä lähtien)

## Miten se kytketään päälle {#how-to-switch-it-on}

Mitään ei tarvitse kytkeä päälle: watcher lukee lähteen juuri sellaisena kuin peli tai alusta sen antaa.

## Miten se toimii {#how-it-works}

EVE Online: asiakkaan pelilokit, `Documents\EVE\logs\Gamelogs\*.txt`.

Asiakas kirjoittaa yhden tiedoston per hahmo per kirjautuminen, muodossa `<yyyymmdd>_<hhmmss>[_<hahmon tunnus>].txt`. Tiedostoon kirjoittaminen on oletuksena päällä. Useat samanaikaiset asiakkaat kirjoittavat omansa, joten seurataan jokaista pelin käynnistymisen jälkeen kirjoitettua tiedostoa. Otsikko ja rivit (EVE-aika on UTC):

```text
------------------------------------------------------------
  Gamelog
  Listener: Character Name
  Session Started: 2024.07.02 19:41:40
------------------------------------------------------------
[ 2024.07.02 20:31:28 ] (combat) <color=0xff00ffff><b>200</b> <color=0x77ffffff><font size=10>to</font>
    <b><color=0xffffffff>Pilot[TICK](../Ship)</b><font size=10><color=0x77ffffff> - Weapon - Penetrates
[ 2024.06.25 15:20:01 ] (combat) <color=0xffcc0000><b>375</b> ... from ... - Weapon - Hits
[ 2024.06.25 15:21:00 ] (bounty) <font size=12><b><color=0xff00aa00>15,000 ISK</b> added to next bounty payout
[ 2024.06.25 15:30:00 ] (None) Jumping from System A to System B
```

(combat-rivi on tiedostossa yksi rivi.) Muotoilutagit poistetaan ennen vertailua. Tiedosto on vuosien varrella ollut sekä UTF-8- että UTF-16-muodossa, ja molemmat luetaan.
Muotoa ei ole dokumentoinut CCP. Se on asiakkaan pelkkätekstinen loki, joka luetaan samalla tavalla kuin yhteisön taisteluloki-työkalut sen lukevat (esim. <https://docs.rs/crate/eve-log-parser>). Sijainteja ei ole.

Sen vieressä on `Documents\EVE\logs\Chatlogs\<kanava>_<yyyymmdd>_<hhmmss>[_<id>].txt`: yksi tiedosto chat-kanavaa kohden per kirjautuminen (kun chat-lokitus on päällä, mikä on asiakkaan oletus). Tiedosto on UTF-16:ssa, ja sen otsikko nimeää kanavan ja kuuntelijan. Rivit ovat muotoa `[ yyyy.mm.dd hh:mm:ss ] Sender > message`.

Jokainen rivi molemmista tallennetaan sellaisenaan session raakatiedostoon (3DHeatin muunninsääntö): gamelog-rivi kanavansa nimellä hakasulkeissa (`combat`, `notify`, `bounty`, `None` ...), chat-rivi tyypillä `chat` kanavansa kanssa, ja otsikkorivit tyypillä `gamelog header` tai `chatlog header`.

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennettu | ei |
| Ylösakseli | `y` |
| Yksiköt | sijainteja ei tallenneta |
| Peilattu katselinta varten | ei mitään |
| Yksikköskaala (`scale`: katselin kertoo sijainnit sillä) | 1 |

Nämä menevät kunkin session `meta.json`:n kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`:n footeriin. Näin 3DHeat-katselin kääntää ja skaalaa rivit itse, katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän muodossa "allowed (reads only what the game publishes)".
- Tyyppi `log`: se lukee vain sen, minkä peli tai alusta antaa ulos (pelin ajon aikana kirjoittamat tiedostot). Siksi se tallentaa myös verkkopelissä, aivan kuten offline-pelissä. Lippu ratkaisee vain sen, saako muistia koskaan lukea.
- Muisti: tämän sovittimen lukema **ei koskaan**. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliin, joka on merkitty verkkopeliksi. Katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (session `stats` tiedostossa `meta.json` ja taulussa `stats` tiedostossa `watcher.sqlite`):

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

Aaltosulkeissa oleva avain täydentyy ajon aikana (`score.{team}` on yksi avain per joukkue). Avaimet, jotka koodi ottaa pelin kenttien taulukosta tai pelin omista tilastonimistä, eivät ole tässä listassa. Kohdassa "Mitä tallennetaan" ne on nimetty.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunninsääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): se, mitä lähde sisältää, luetaan tai tallennetaan, eikä mitään pudoteta. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan sellaisenaan session tiedostoon `heat.raw.parquet` (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja sen jälkeen nimellä säilytetyt kentät; `used` merkitsee ne, joista tuli myös rivejä). `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon, ja `lost` on 0.

**Luettu**

- gamelogin `(combat)`-osumat annettuina ja saatuina (määrä, toinen lentäjä, yhtiön lyhenne, alus, ase, osuman laatu) sekä ohilaukaukset molempiin suuntiin
- gamelogin `(bounty)`-maksut ISK:ssa ja rivit `Jumping from A to B`
- gamelogin otsakkeen Listener: kenen loki se on

**Tallennettu raakana**

- jokainen gamelog-rivi sellaisenaan, `type` on sen kanava hakasulkeissa (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None` ...), mukana `file` ja `listener`; `used` siellä, missä siitä tuli rivi; otsakerivit tyypillä `gamelog header`
- jokainen chat-lokirivi sellaisenaan (Local, yhtiö, laivasto, yksityiset kanavat sekä `EVE System` -ilmoitukset, kuten Local-kanavan vaihtuminen hypyn jälkeen), `type` `chat`, mukana `channel`, `listener` ja `file`; otsakerivit tyypillä `chatlog header`. Ei vielä tehty riveiksi
- muotoilutagit (`<color>`, `<b>`, `<font>`) pysyvät raakatekstissä; riveillä ne on poistettu

**Ei saatavilla**

- sijainnit: asiakas ei kirjoita niitä lokeihinsa
- muiden lentäjien taistelut: gamelog on kuuntelijan oma
- aiempien kirjautumisten lokit: jokainen kirjautuminen kirjoittaa uudet tiedostot; ne, jotka ovat vanhempia kuin asiakkaan tämä käynnistys, eivät lue uudelleen
- chat, kun pelaaja on kytkenyt chat-lokituksen pois asiakkaan asetuksista
- asiakkaan oma välimuisti ja asetustiedostot: eivät lokeja, eikä niitä ole dokumentoitu

**Koko**: gamelog on 0,1–2 Mt tunnissa (eniten taistelussa); chat-lokit riippuvat avoimista kanavista: vilkas Local- tai laivastokanava 0,5–3 Mt tunnissa; zstd tekee heat.raw.parquetista noin kymmenesosan

## Todennettu {#verified}

Testattu synteettisillä gamelog-riveillä yhteisön jäsenten julkaisemassa muodossa. Peliä vastaan ei ole testattu.

## Lähdekoodi {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
