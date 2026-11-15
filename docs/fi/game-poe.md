---
title: "Path of Exile (lokitiedostot)"
nav_order: 35
lang: "fi"
source: game-poe.md
source_hash: "b5783b5a5690"
nav_exclude: true
search_exclude: true
---
# Path of Exile (lokitiedostot) {#path-of-exile-log-files}

Kun pelaat Path of Exileä, watcher lukee pelin kirjoittamat tiedostot ja tallentaa, mitä tapahtui, jotta voit myöhemmin katsoa sen tilastoina ja aikajanana.

*Tekniset tiedot: sovitin `poe`, tyyppi [`log`](sources-and-rules.md); se toimii, kun `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` tai `PathOfExile_x64_KG.exe` on käynnissä, ja etsii uutta dataa 0,5 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- alueet, joihin astutaan, alueen taso, alueen tunnus ja sen siemen
- tasonnousut luokan ja tason kanssa
- kuolemat ("has been slain")
- pelaajat, jotka tulevat alueelle ja lähtevät siitä, kuiskaukset sisään ja ulos, kauppapyynnöt, hyväksytyt kaupat
- jokainen Client.txt-rivi tältä istunnolta sellaisenaan tiedostossa heat.raw.parquet
- kuolemat, saadut tasot, korkein taso, alueet, eri alueet, kuiskaukset, kauppapyynnöt, kaupat

## Mistä data tulee {#where-it-comes-from}

&lt;install>\logs\Client.txt Path of Exilestä tai Path of Exile 2:sta (seurataan; asennuskansio on käynnissä olevan suoritettavan tiedoston)

## Miten se kytketään päälle {#how-to-switch-it-on}

Mitään ei tarvitse kytkeä päälle: watcher lukee lähteen juuri sellaisena kuin peli tai alusta sen antaa.

## Miten se toimii {#how-it-works}

Path of Exile ja Path of Exile 2: asiakkaan loki, `<install>\logs\Client.txt`.

Molemmat pelit lisäävät yhteen Client.txt-tiedostoon asennuskansiossaan niin kauan kuin ne ovat asennettuina (se kasvaa käynnistysten yli). Rivit näyttävät tältä:

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- paikallinen aika, millisekuntilaskuri, tiiviste, taso ja säie, sitten se, mitä chat-ikkuna näyttää. Viestit ovat englanninkielisen asiakkaan; muun kielen asiakas kirjoittaa ne käännettyinä, eikä niitä ymmärretä täällä. Sijaintia ei ole: mikään ei anna sitä. Muotoa ei ole dokumentoinut Grinding Gear Games; se on pelin pelkkätekstinen loki, jota yhteisötyökalut (kauppa-apurit, tasoopaat) ovat lukeneet vuosia, esim. <https://github.com/klayveR/poe-log-monitor> (MIT) tapahtumalistan osalta.

Asennuskansio on käynnissä olevan suoritettavan tiedoston; ilman sitä etsitään Steam-kirjastot ja itsenäisen asiakkaan oletuskansio.

Jokainen tämän istunnon rivi tallennetaan sellaisenaan session raakatiedostoon (3DHeatin muunninsääntö), riippumatta siitä, onko sillä merkitystä tässä: `type` on taso ja lokittaja hakasulkeissa (`INFO Client`, `DEBUG Client`, `WARN Client` ...). Leimattu rivi ilman hakasulkeita on `untagged`, rivi ilman aikaleimaa `untimed`.

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

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

Aaltosulkeissa oleva avain täydentyy ajon aikana (`score.{team}` on yksi avain per joukkue). Avaimet, jotka koodi ottaa pelin kenttien taulukosta tai pelin omista tilastonimistä, eivät ole tässä listassa. Kohdassa "Mitä tallennetaan" ne on nimetty.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunninsääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): se, mitä lähde sisältää, luetaan tai tallennetaan, eikä mitään pudoteta. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan sellaisenaan session tiedostoon `heat.raw.parquet` (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja sen jälkeen nimellä säilytetyt kentät; `used` merkitsee ne, joista tuli myös rivejä). `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon, ja `lost` on 0.

**Luettu**

- `You have entered <zone>`, alueen taso, alueen tunnus ja siemen sitä edeltävästä `Generating level` -rivistä
- `<name> (<class>) is now level <n>`, `<name> has been slain`, pelaajat, jotka tulevat alueelle ja lähtevät siitä, kuiskaukset sisään ja ulos (ja se, ovatko ne kauppapyyntöjä), hyväksytyt ja peruutetut kaupat

**Tallennettu raakana**

- jokainen tämän istunnon rivi sellaisenaan, `type` on taso ja lokittaja hakasulkeissa (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client` ...), `used` siellä, missä siitä tuli rivi: globaali-, kauppa-, ryhmä- ja kiltachat, `Connecting to instance server`, AFK- ja DND-ilmoitukset, vastaukset chat-komentoihin kuten `/played` ja `/deaths`, asiakkaan lataus- ja moottoririvit; tallennettu, ei vielä tehty riveiksi
- leimattu rivi ilman hakasulkeita (`***** LOG FILE OPENING *****`) tyypillä `untagged`, rivi ilman aikaleimaa tyypillä `untimed`

**Ei saatavilla**

- sijainnit: mikään lokissa ei anna niitä
- sitä, mitä muun kielen asiakas kirjoittaa: rivit tallennetaan, mutta riveiksi tehdään vain englanninkieliset viestit
- aiempien käynnistysten rivit: Client.txt kasvaa käynnistysten yli; ennen tämän pelikerran alkua leimatut rivit jätetään (ne tallennettiin, kun ne pelattiin)
- tapot, vahinko, saalis ja passiivinen puu: peli ei kirjaa niitä lokiin

**Koko**: Client.txt kasvaa noin 0,3–3 Mt tunnissa (eniten DEBUG-riveistä alueiden latautuessa; enemmän vilkkaan kauppachatin kanssa); zstd tekee heat.raw.parquetista noin kymmenesosan

## Todennettu {#verified}

Testattu synteettisillä Client.txt-riveillä pelin muodossa. Peliä vastaan ei ole testattu.

## Lähdekoodi {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
