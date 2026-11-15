---
title: "War Thunder (pelitila)"
nav_order: 46
lang: "fi"
source: game-warthunder-webmap.md
source_hash: "34a876e38f09"
nav_exclude: true
search_exclude: true
---
# War Thunder (pelitila) {#war-thunder-game-state}

Kun pelaat War Thunderia, watcher tallentaa pelin ilmoittamat tiedot omalle koneellesi, jotta voit myöhemmin katsoa ne kartalla 3DHeat-katselimessa.

*Tekniset tiedot: adapteri `warthunder-webmap`, tyyppi [`gsi`](sources-and-rules.md); se toimii, kun `aces.exe` on käynnissä, ja etsii uutta dataa 0,5 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- oma sijainti (kartan itä ja pohjoinen metreinä; korkeus /state-kohdasta ilma-aluksessa, muuten 0), kahdesti sekunnissa, suunta ja nopeus
- ilmestymiset ja oman ajoneuvon poistuminen kartalta (tuhoutunut, laskeutunut, takaisin hangaariin), yksi lento kerrallaan
- muut ilma-alukset ja maayksiköt minikartalla sijaintina, seurattuina tunnisteina ja puolena (ei korkeutta)
- lentokentät, valloitusalueet ja tukikohdat kerran sekä alueiden puolenvaihdot
- tappo- ja vahinkosyötteen rivit (kuka, ajoneuvo, verbi); pelaajan tappot ja kuolemat, kun nimesi on asetettu (`config --set player_names.warthunder-webmap=<nimi>`)
- ilmestymiset, etäisyys, korkein korkeus, korkein todellinen ilmanopeus, ajoneuvo; tappot ja kuolemat, kun nimesi on asetettu
- jokainen web-kartan vastaus kokonaisena heat.raw.parquet-tiedostossa: täydet /state ja /indicators, chat, taistelun tavoitteet ja kartan kuva mukaan lukien. Taistelujen välissä ne menevät omaan sessioonsa

## Mistä tiedot tulevat {#where-it-comes-from}

pelin paikallinen web-kartta, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## Kuinka se käynnistetään {#how-to-switch-it-on}

Mitään ei tarvitse kytkeä päälle: watcher lukee lähteen sellaisena kuin peli tai alusta sen antaa.

## Miten se toimii {#how-it-works}

War Thunder: pelin oma paikallinen web-kartta osoitteessa <http://127.0.0.1:8111>.

Peli palvelee sivua, jonka toinen näyttö tai puhelin voi näyttää ("web-kartta"), sekä sen takana olevan JSON-datan. Tämä toimii kaikissa tiloissa, myös moninpelissä, kun peli on käynnissä:

```text
/map_info.json   {"map_min": [x, y], "map_max": [x, y], "grid_steps", "grid_zero", "map_generation",
                  "hud_type", "valid"}: kartan laajuus metreinä; valid false hangaarissa
/map_obj.json   [{"type": aircraft|ground_model|airfield|capture_zone|bombing_point|defending_point|
                  respawn_base_*|..., "icon": Player|Fighter|Bomber|Mediumtank|SPAA|..., "color": "#rrggbb",
                  "x", "y" (0..1 kartan kuvasta, y alaspäin), "dx", "dy" (suunta),
                  lentokentät "sx", "sy", "ex", "ey"}]: mitä minikartalla näkyy; pelaajan oma ajoneuvo
                  kuvakkeella "Player"; ei tunnisteita, ei korkeuksia
/state          {"valid", "H, m", "TAS, km/h", "IAS, km/h", "M", "Vy, m/s", ...}: lennon arvot,
                  valid vain ilma-aluksessa
/indicators     {"valid", "army": air|tank|..., "type": ajoneuvo}
/hudmsg?lastEvt=N&lastDmg=M   {"events": [...], "damage": [...]} annettuja tunnuksia uudemmat, jokainen
                  {"id", "msg", "sender", "enemy", "mode", "time"}; vahinkorivit ovat muotoa
                  "Nimi (Ajoneuvo) shot down Nimi (Ajoneuvo)"
/gamechat?lastId=N  annettua tunnusta uudemmat chat-viestit, [{"id", "msg", "sender", "enemy", "mode", "time"}]
/mission.json   taistelun tavoitteet ja niiden tila
/map.img        kartan kuva, jonka päälle sivu piirtää kohteet
```

Jokainen vastaus säilytetään kokonaisena session raakatiedostossa sen päätepisteen nimellä (map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img). Taistelujen välissä vastaukset menevät omaan sessioonsa.

Kartan sijainti muutetaan metreiksi laajuuden avulla: u = min_x + x \* (max_x - min_x) itään, v = max_y - y \* (max_y - min_y) pohjoiseen (kuvan y kulkee alaspäin). Rivit ovat x = u, y = korkeus (oman ilma-aluksen "H, m"; muilla 0), z = v. Y on siis ylös. Z on peilattu katselimelle, jotta pohjoinen ei piirtyisi etelään.

Värit kertovat puolet pelaajan näkemällä tavalla: oma keltainen (oletus #faC81E), squad vihreä, liittolaiset sininen (#174DFF) ja viholliset punainen (#f40C00). Värisokeille tarkoitetut paletit muuttavat niitä, joten sävy ratkaisee, ei tarkka arvo. Peli ei nimeä ketään minikartalla eikä anna kohteille tunnisteita. Muut kohteet saavat tunnisteet täällä seuraamalla niitä kyselystä toiseen (lähin saman tyypin ja kuvakkeen kohde). Tämä voi vaihtaa kaksi ohi lentävää samaa tyyppiä keskenään. Pelaajan oma nimi ei ole API:ssa. Anna se asetuksissa (`config --set player_names.warthunder-webmap=<oma nimesi>`), jolloin tappo-syötteen rivit pelaajaan liittyen muuttuvat tapoiksi ja kuolemiksi. Ilman sitä ne tallennetaan tappo-syötteenä.

Lähteet: pelin oma sivu osoitteessa <http://127.0.0.1:8111> ja sen JSON. Kenttätiedot kuten JoyPro 2 -projekti on dokumentoinut (docs/telemetry-recording.md; GPL, käytetty vain faktoihin).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennettu | kyllä |
| Ylösakseli | `y` |
| Yksiköt | metriä (kartan itä ja pohjoinen; korkeus vain omalle ilma-alukselle) |
| Peilattu katselimelle | `z` |
| Yksikkökerroin (`scale`: katselin kertoo sijainnit sillä) | 1 |

Nämä menevät kunkin session `meta.json`-tiedostoon (`axes`) ja, kun sessiossa on sijainteja, tiedoston `heat.parquet` alatunnisteeseen. Siksi 3DHeat-katselin kääntää ja skaalaa rivit itse; katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän tekstillä "allowed (reads only what the game publishes)".
- Tyyppi `gsi`: se lukee vain sen, minkä peli tai alusta luovuttaa (game-state integration tai paikallinen rajapinta, jonka peli palvelee). Se tallentaa siis myös verkkopelit, samoin kuin offline-pelit. Lippu päättää vain, saako muistia koskaan lukea.
- Muisti: **ei koskaan**. Tämä sovitin ei lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan verkkopeliksi merkitystä pelistä. Katso [Lähteet ja säännöt](sources-and-rules.md).

## Tallennetut tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (kunkin session `stats` tiedostossa `meta.json` ja `watcher.sqlite`-tiedoston taulussa `stats`):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohden). Avaimet, jotka koodi ottaa pelin kenttien taulukosta tai pelin omista tilastonimistä, eivät ole tässä luettelossa; yllä oleva "Mitä tallennetaan" -osio nimeää ne.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muuntimen sääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): lähteessä oleva tieto luetaan tai säilytetään, sitä ei koskaan jätetä pois. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, säilytetään kokonaisena session tiedostossa `heat.raw.parquet` (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja kaikki nimellä säilytetyt kentät; `used` merkitsee ne, joista tuli myös rivejä). Tiedoston `meta.json` kohdan `selfCheck.completeness` laskuri kertoo jokaisen `type`-arvon määrän, ja `lost` on 0.

**Luetaan**

- /map_info.json: kartan laajuus ja ruudukko (metriä, kartan tunnus) tiedostoon meta.json; virheellinen tieto päättää taistelun
- /map_obj.json (kahdesti sekunnissa): oma ajoneuvo, muut ilma-alukset ja maayksiköt (seurattavat tunnisteet, puoli värin perusteella, kuvake, suunta, väri) sekä lentokentät, alueet ja tukikohdat riveinä
- /state (kahdesti sekunnissa ilma-aluksessa): korkeus, TAS, IAS, Mach ja Vy oman rivin arvoina
- /indicators (2 s välein): armeija ja ajoneuvon tyyppi
- /hudmsg (kerran sekunnissa): tappo- ja vahinkosyötteen rivit tappoina, kuolemina, osumina ja syötteen rivinä; muut HUD-tapahtumat riveinä

**Säilytetään raakana**

- jokainen vastaus kokonaisena, `text` on JSON sellaisena kuin peli sen lähetti, päätepisteen nimen alla: `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission`. `map_img` on kartan kuvan tavut `payload`-kentässä, kerran taistelua kohden
- ainoastaan raakasessiossa: jokainen /state-kenttä viiden luetun lisäksi (AoA, AoS, Ny, Wx, kaasu, kierrokset, polttoaine ... yhden ilma-aluksen joukko poikkeaa toisen joukosta), jokainen /indicators-kenttä (ilma-alusten mittaristot, tankkien nopeus, vaihde, miehistö ja stabilisaattori), kohteiden muut avaimet kartalla (color[], blink, icon_bg, lentokenttien päät), hudmsg:n sender, enemy ja mode, chat (/gamechat, kerran sekunnissa), taistelun tavoitteet ja niiden tila (/mission.json, 10 s välein taistelun aikana) sekä rivit, jotka sanottiin ennen kuin watcher käynnistyi
- taistelujen välissä (hangaari, lataus) vastaukset menevät omaan sessioonsa, jonka meta.json merkitsee `between_battles`-tunnisteella ja jolla ei ole rivejä

**Ei saatavilla**

- muiden pelaajien ajoneuvojen nimet, tunnisteet ja korkeudet: web-kartalla niitä ei ole (tunnisteet annetaan täällä seuraamalla kohteita kyselystä toiseen). Tappo-syöte nimeää pelaajat ilman sijainteja
- kaikki web-kartan ulkopuolella: pelin toistot luetaan War Thunder -toistomuuntimella, eikä pelin muistia lueta koskaan (verkkopeli)
- /map_obj.json useammin kuin kahdesti sekunnissa: kyselynopeus pidetään matalana, jotta pelin oma web-palvelin ei kuormitu

**Koko**: noin 50–120 Mt tunnissa JSON-dataa pakkaamattomana taistelun aikana (map_obj 5–15 kt kahdesti sekunnissa, state noin 1,5 kt kahdesti sekunnissa, indicators 2 s välein, chat ja HUD-rivit pieniä), lisäksi kartan kuva kerran taistelua kohden (alle 2 Mt). Taistelujen välissä 1–2 Mt tunnissa (kartan ulkoasu kahdesti sekunnissa, HUD ja chat kerran, kukin lyhyenä vastauksena). zstd pienentää toistuvaa JSONia yli kymmenkertaisesti.

## Todennettu {#verified}

testattu paikallista väärennettyä palvelinta vastaan, joka antaa vastaukset pelin web-kartan muodossa. Käynnissä olevaa peliä ei ole testattu.

## Lähde {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
