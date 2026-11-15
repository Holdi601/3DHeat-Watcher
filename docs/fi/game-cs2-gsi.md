---
title: "Counter-Strike 2 (pelitila)"
nav_order: 9
lang: "fi"
source: game-cs2-gsi.md
source_hash: "2eda1106e11f"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (pelitila) {#counter-strike-2-game-state}

Kun pelaat Counter-Strike 2:ta, watcher tallentaa pelin ilmoittamat tiedot omalle koneellesi, jotta voit myöhemmin katsoa ne kartalla 3DHeat-katselimessa.

*Tekniset tiedot: adapteri `cs2-gsi`, tyyppi [`gsi`](sources-and-rules.md); se toimii, kun `cs2.exe` on käynnissä, ja etsii uutta dataa 0,05 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- oma sijainti (maailman XYZ, tuumaa) ja katselusuunta enintään 10 Hz:n taajuudella, kun olet elossa
- ilmestymiset (kierroksen ensimmäinen näkeminen, uudelleensyntymiset) ja kuolemat (terveys nollaan tai kuolemien määrä)
- tappot aktiivisella aseella ottelutilastojen mukaan
- kierrokset (alku, loppu, voittaja), pommi asetettu, purettu tai räjähtänyt, ottelun vaiheet ja tulos
- tappot, avustukset, kuolemat, MVP:t, pistemäärä, raha, vahinko, päänsyötöt sekä voitetut ja hävityt kierrokset

## Mistä tiedot tulevat {#where-it-comes-from}

Game State Integration: HTTP-POST-pyynnöt osoitteeseen 127.0.0.1:3311, asetukset tiedostossa &lt;CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg

## Kuinka se käynnistetään {#how-to-switch-it-on}

`python -m heat3d_watch setup cs2-gsi --apply`, sitten käynnistä CS2 (peli lukee tiedoston käynnistyessään)

Kirjoita komento terminaaliin, joka on avattu watcherin kansiossa (katso [Ennen aloittamista](before-you-start.md)). Jos se epäonnistuu, viimeinen rivi kertoo syyn; [Asennus ja käynnistys](installing-and-running.md) kattaa yleisimmät syyt.

`python -m heat3d_watch setup cs2-gsi` listaa tiedostot, jotka se muuttaisi; `python -m heat3d_watch setup cs2-gsi --apply` tekee muutokset ja tallentaa alkuperäisen tiedostona `<file>.heat3d-backup` (katso [Komennot](commands.md#setup)). Se tulostaa `cs2-gsi: changed: ...` jokaisesta muutoksesta tai `cs2-gsi: nothing to change`, jos asetus on jo päällä.

Asetukset ympäristömuuttujista:

- `HEAT3D_CS2_GSI_PORT`: portti, johon peli lähettää (oletus 3311); pelin cfg-tiedoston on nimettävä sama portti

## Miten se toimii {#how-it-works}

Valven Game State Integration: Counter-Strike 2 ja Dota 2 kertovat paikalliselle web-palvelimelle, mitä pelissä tapahtuu.

Molemmat pelit lukevat jokaisen `gamestate_integration_*.cfg`-tiedoston cfg-kansiostaan käynnistyessään. Sen jälkeen ne lähettävät JSON-asiakirjan kunkin tiedoston `uri`-osoitteeseen aina, kun tila muuttuu (enintään `throttle`-sekunnin välein, ja `heartbeat`-sekunnin välein, kun mikään ei muutu). Watcher on tuo web-palvelin: se kuuntelee vain osoitetta 127.0.0.1, vastaa jokaiseen POST-pyyntöön heti koodilla 200 ja tekee työnsä omassa kyselysäikeessään.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

Pelaajalle lähetetään se, minkä peli päättää pelaajan saavan nähdä, ja siten se on, mitä voidaan tallentaa:

- CS2: `provider` (oma steamid), `map` (nimi, tila, vaihe warmup/live/intermission/gameover, kierros, joukkueiden CT- ja T-pistemäärä), `round` (vaihe freezetime/live/over, pommi asetettu/räjähtänyt/purettu, win_team), `player` (katseltava pelaaja: oma hahmo kun olet elossa, joukkuetoveri kuoleman jälkeen) tiloineen `state` (terveys, panssari, raha, round_kills, round_killhs, round_totaldmg), `match_stats` (tappot, avustukset, kuolemat, mvp:t, pistemäärä), `position` ja `forward` merkkijonoina "x, y, z" maailmayksiköissä (tuumaa, Z ylös), `weapons`; `bomb` vain katsojille. Muiden pelaajien sijainteja (`allplayers_*`) lähetetään vain katsojille ja GOTV:lle, joten niitä ei pyydetä.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player` (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero` (xpos/ypos maailmayksiköissä, level, alive, respawn_seconds), `buildings` (terveys tornia, kasarmia ja ancient-rakennusta kohden), `roshan`, `events` (roshan_killed, aegis_picked_up, ...). Korkeutta ei ole: z on aina 0. Lisäksi pyydetään ja säilytetään kokonaisina: `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`, `neutralitems`, `league` (peli lähettää sen, minkä pelaajan oma asiakas näkee; mitkä niistä sisältävät jotain pelatessa eikä katsellessa, on testaamatta).

Jokainen asiakirja säilytetään myös kokonaisena (3DHeatin muuntimen sääntö, docs/converters.md viewer-repositoriossa): `heat.raw.parquet`, `type` "gsi", `text` on JSON sellaisenaan lähetettynä. Vain cfg-tiedoston token on peitetty, koska se on watcherin oma salaisuus, ei pelidataa. Asiakirjat, jotka tulevat, kun ottelua ei ole auki (valikot, lataus, ottelujen välit), odottavat kansiossa `Backlog` ja menevät seuraavan ottelun sessioon ennen sen alkua. Pelin sulkeutuessa jäljelle jääneet saavat oman sessionsa, jossa on vain ne. Lukukelvottomat lähetykset ja väärällä tokenilla tehdyt lähetykset säilytetään myös ("gsi-unreadable", "gsi-bad-auth").

Lähteet: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration> (muoto, jonka CS2 säilytti), <https://github.com/antonpup/CounterStrike2GSI> ja <https://github.com/antonpup/Dota2GSI> (kenttälistat; MIT-lisenssi, luettu vain faktoja varten).

Saman moduulin kautta toimii myös: [Dota 2 (pelitila)](game-dota2-gsi.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennettu | kyllä |
| Ylösakseli | `z` |
| Yksiköt | tuumaa (Hammer-yksiköt) |
| Peilattu katselimelle | `y` |
| Yksikkökerroin (`scale`: katselin kertoo sijainnit sillä) | 1 |

Nämä menevät kunkin session `meta.json`-tiedostoon (`axes`) ja, kun sessiossa on sijainteja, tiedoston `heat.parquet` alatunnisteeseen. Siksi 3DHeat-katselin kääntää ja skaalaa rivit itse; katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän tekstillä "allowed (reads only what the game publishes)".
- Tyyppi `gsi`: se lukee vain sen, minkä peli tai alusta luovuttaa (game-state integration tai paikallinen rajapinta, jonka peli palvelee). Se tallentaa siis myös verkkopelit, samoin kuin offline-pelit. Lippu päättää vain, saako muistia koskaan lukea.
- Muisti: **ei koskaan**. Tämä sovitin ei lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan verkkopeliksi merkitystä pelistä. Katso [Lähteet ja säännöt](sources-and-rules.md).

## Tallennetut tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (kunkin session `stats` tiedostossa `meta.json` ja `watcher.sqlite`-tiedoston taulussa `stats`):

`bad_auth`, `bad_packets`, `dropped_packets`, `money`, `result`, `score_other`, `score_own`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohden). Avaimet, jotka koodi ottaa pelin kenttien taulukosta tai pelin omista tilastonimistä, eivät ole tässä luettelossa; yllä oleva "Mitä tallennetaan" -osio nimeää ne.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muuntimen sääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): lähteessä oleva tieto luetaan tai säilytetään, sitä ei koskaan jätetä pois. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, säilytetään kokonaisena session tiedostossa `heat.raw.parquet` (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja kaikki nimellä säilytetyt kentät; `used` merkitsee ne, joista tuli myös rivejä). Tiedoston `meta.json` kohdan `selfCheck.completeness` laskuri kertoo jokaisen `type`-arvon määrän, ja `lost` on 0.

**Luetaan**

- katseltavan pelaajan sijainti, katselusuunta, terveys, panssari, raha, aktiivinen ase, kypärä, purkutyökalu, välähdys-, savu- ja tulimäärät sekä varusteiden arvo. Ne kirjautuvat jokaiselle sijaintirivillä, kun pelaaja on oma (provider steamid = pelaajan steamid)
- ilmestymiset, kuolemat (terveys nollaan tai ottelutilastojen kuolemamäärä), tappot (tappolaskurin kasvu)
- ottelun vaiheet, kierrokset (vapaa-aika, live, ohi, voittaja), pommi asetettu, purettu tai räjähtänyt, tulos
- tappot, avustukset, kuolemat, MVP:t, pistemäärä, raha, vahinko, päänsyötöt sekä voitetut ja hävityt kierrokset tilastoina

**Säilytetään raakana**

- `gsi`: jokainen pelin lähettämä asiakirja kokonaisena sellaisenaan (`text`). `used` on tosi, kun sitä luettiin ottelussa. Mukana ovat provider (versio, aikaleima), map (tila, joukkueiden nimet, peräkkäiset kierroshäviöt, aikalisät, sarjavoitot ja `round_wins` kunkin kierroksen voittoehdolla), round, katseltava pelaaja (kilta, tarkkailijapaikka, toiminta, jokainen ase skinillään, ammuksineen ja varastoineen), bomb, vaiheiden laskurit sekä pelin oma `previously`- ja `added`-erotus edellisestä lähetyksestä
- valikoista, latauksesta ja ottelujen välistä tulevat asiakirjat: säilytetään samalla tavalla omalla ajallaan ennen seuraavan ottelun alkua. Viimeisen ottelun jälkeen ne ovat omassa sessionsa (`raw_only` tiedostossa meta.json)
- `gsi-unreadable`: lähetys, joka ei ole JSON-olio, sen tavut `payload`-kentässä ja `length`
- `gsi-bad-auth`: lähetys, jonka token on eri kuin cfg-tiedoston token

**Ei saatavilla**

- muut pelaajat (`allplayers_*`) ja kranaatit (`allgrenades`): peli lähettää ne vain katsojille ja GOTV:lle, eikä watcher pyydä niitä (katso Lähteet ja säännöt). Demossa on jokainen pelaaja; katso [Counter-Strike 2 (toistot)](game-cs2-demos.md)
- tilat lähetysten välissä: peli lähettää enintään 0,1 s välein (`throttle`) ja vain muutoksen yhteydessä, muuten 10 s välein (`heartbeat`)
- cfg-tiedoston token, peitettynä jokaisessa tallennetussa asiakirjassa: watcherin oma salaisuus, ei pelidataa
- yli 10 000 odottavaa lähetystä (jos watcher jumittuu) lasketaan tilastoon `dropped_packets` eikä niitä tallenneta. Yli 4 Mt:n lähetys tallennetaan tyypillä `gsi-unreadable` pituutensa kanssa, mutta ilman tavujaan

**Koko**: pelaajan asiakirja on 2–4 kt, ja sitä lähetetään jopa 10 kertaa sekunnissa, kun jokin muuttuu. Tämä on noin 30–150 Mt tunnissa `raw.bin`-tiedostossa ottelun aikana, ja kymmenesosa tai vähemmän zstd-pakatussa `heat.raw.parquet`-tiedostossa. Arvio perustuu julkaistuun muotoon, ei pelissä mitattuun.

## Todennettu {#verified}

testattu asiakirjoilla, jotka ovat julkaistussa GSI-muodossa ja lähetetty käynnissä olevalle sovittimelle. Asennus ja cfg-kansion haku testattu paikallisella asennuksella. Käynnissä olevaa peliä ei ole testattu.

## Lähde {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
