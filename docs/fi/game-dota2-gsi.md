---
title: "Dota 2 (pelitila)"
nav_order: 13
lang: "fi"
source: game-dota2-gsi.md
source_hash: "100a0d704bbe"
nav_exclude: true
search_exclude: true
---
# Dota 2 (pelitila) {#dota-2-game-state}

Kun pelaat Dota 2:ta, watcher tallentaa pelin ilmoittamat tiedot omalle koneellesi, jotta voit myöhemmin katsoa ne kartalla 3DHeat-katselimessa.

*Tekniset tiedot: adapteri `dota2-gsi`, tyyppi [`gsi`](sources-and-rules.md); se toimii, kun `dota2.exe` on käynnissä, ja etsii uutta dataa 0,05 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- oman sankarin sijainti (maailman X/Y, Dota-yksiköt; ei korkeutta), kun olet elossa
- oman sankarin ilmestymiset, kuolemat (kuolemisen jälkeinen odotusaika mukaan lukien) ja uudelleensyntymiset
- tappot, kun tappolaskuri kasvaa
- tuhotut rakennukset, Roshan, pelitapahtumat (roshan_killed, aegis_picked_up, ...), pelitilat ja tulos
- tappot, kuolemat, avustukset, viimeiset osumat, denies, kulta, GPM, XPM, taso ja sankari

## Mistä tiedot tulevat {#where-it-comes-from}

Game State Integration: HTTP-POST-pyynnöt osoitteeseen 127.0.0.1:3312, asetukset tiedostossa &lt;Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg

## Kuinka se käynnistetään {#how-to-switch-it-on}

`python -m heat3d_watch setup dota2-gsi --apply`, sitten käynnistä Dota 2 (peli lukee tiedoston käynnistyessään)

Kirjoita komento terminaaliin, joka on avattu watcherin kansiossa (katso [Ennen aloittamista](before-you-start.md)). Jos se epäonnistuu, viimeinen rivi kertoo syyn; [Asennus ja käynnistys](installing-and-running.md) kattaa yleisimmät syyt.

`python -m heat3d_watch setup dota2-gsi` listaa tiedostot, jotka se muuttaisi; `python -m heat3d_watch setup dota2-gsi --apply` tekee muutokset ja tallentaa alkuperäisen tiedostona `<file>.heat3d-backup` (katso [Komennot](commands.md#setup)). Se tulostaa `dota2-gsi: changed: ...` jokaisesta muutoksesta tai `dota2-gsi: nothing to change`, jos asetus on jo päällä.

Asetukset ympäristömuuttujista:

- `HEAT3D_DOTA_GSI_PORT`: portti, johon peli lähettää (oletus 3312); pelin cfg-tiedoston on nimettävä sama portti

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

Saman moduulin kautta toimii myös: [Counter-Strike 2 (pelitila)](game-cs2-gsi.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennettu | kyllä |
| Ylösakseli | `z` |
| Yksiköt | Dota-maailmayksiköt (z on aina 0) |
| Peilattu katselimelle | `y` |
| Yksikkökerroin (`scale`: katselin kertoo sijainnit sillä) | 1 |

Nämä menevät kunkin session `meta.json`-tiedostoon (`axes`) ja, kun sessiossa on sijainteja, tiedoston `heat.parquet` alatunnisteeseen. Siksi 3DHeat-katselin kääntää ja skaalaa rivit itse; katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän tekstillä "allowed (reads only what the game publishes)".
- Tyyppi `gsi`: se lukee vain sen, minkä peli tai alusta luovuttaa (game-state integration tai paikallinen rajapinta, jonka peli palvelee). Se tallentaa siis myös verkkopelit, samoin kuin offline-pelit. Lippu päättää vain, saako muistia koskaan lukea.
- Muisti: **ei koskaan**. Tämä sovitin ei lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan verkkopeliksi merkitystä pelistä. Katso [Lähteet ja säännöt](sources-and-rules.md).

## Tallennetut tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (kunkin session `stats` tiedostossa `meta.json` ja `watcher.sqlite`-tiedoston taulussa `stats`):

`bad_auth`, `bad_packets`, `dropped_packets`, `hero`, `level`, `result`, `roshan_kills_seen`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohden). Avaimet, jotka koodi ottaa pelin kenttien taulukosta tai pelin omista tilastonimistä, eivät ole tässä luettelossa; yllä oleva "Mitä tallennetaan" -osio nimeää ne.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muuntimen sääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): lähteessä oleva tieto luetaan tai säilytetään, sitä ei koskaan jätetä pois. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, säilytetään kokonaisena session tiedostossa `heat.raw.parquet` (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja kaikki nimellä säilytetyt kentät; `used` merkitsee ne, joista tuli myös rivejä). Tiedoston `meta.json` kohdan `selfCheck.completeness` laskuri kertoo jokaisen `type`-arvon määrän, ja `lost` on 0.

**Luetaan**

- oman sankarin sijainti (x/y), elossa-tieto, taso, terveys, enimmäisterveys, mana, enimmäismana; ilmestymiset, kuolemat kuolemisen jälkeisellä odotusajalla, uudelleensyntymiset
- tappot (tappolaskurin kasvu); tappot, kuolemat, avustukset, viimeiset osumat, denies, kulta, GPM, XPM, nettoarvo, taso ja sankari tilastoina
- tuhotut rakennukset, Roshan kaatunut ja takaisin, jokainen `events`-kohdan merkintä kerran, pelitilat, voittaja

**Säilytetään raakana**

- `gsi`: jokainen pelin lähettämä asiakirja kokonaisena sellaisenaan (`text`). `used` on tosi, kun sitä luettiin ottelussa. Cfg-tiedosto pyytää kaikki viisitoista osaa: provider, map (päivä/yö, tauko, vartijoiden jäähtymiset, pistemäärät), player (luotettava ja epäluotettava kulta, putket, tappolista, annetut komennot ja muut), hero (vaikutukset, talentit, Aghanimin, attribuutit), abilities, items, buildings, roshan, events, draft, wearables, minimap, couriers, neutralitems, league sekä pelin oma `previously`- ja `added`-erotus
- valikoista, latauksesta ja ottelujen välistä tulevat asiakirjat: säilytetään samalla tavalla omalla ajallaan ennen seuraavan ottelun alkua. Viimeisen ottelun jälkeen ne ovat omassa sessionsa (`raw_only` tiedostossa meta.json)
- `gsi-unreadable`: lähetys, joka ei ole JSON-olio, sen tavut `payload`-kentässä ja `length`
- `gsi-bad-auth`: lähetys, jonka token on eri kuin cfg-tiedoston token

**Ei saatavilla**

- muut sankarit pelatessa: peli lähettää oman sankarin, ja jokaisen pelaajan tiedot vain katsojille. Ne säilytetään silloin raakana, mutta niitä ei piirretä. Useat osat (draft, minimap, couriers) sisältävät vain sen, minkä pelaajan oma asiakas näkee, ja pelatessa se on testaamatta
- tilat lähetysten välissä: enintään yksi 0,1 s välein (`throttle`), ja 10 s välein, kun mikään ei muutu (`heartbeat`)
- cfg-tiedoston token, peitettynä jokaisessa tallennetussa asiakirjassa: watcherin oma salaisuus, ei pelidataa
- yli 10 000 odottavaa lähetystä (jos watcher jumittuu) lasketaan tilastoon `dropped_packets` eikä niitä tallenneta. Yli 4 Mt:n lähetys tallennetaan tyypillä `gsi-unreadable` pituutensa kanssa, mutta ilman tavujaan

**Koko**: kaikilla osilla varustettu pelaajan asiakirja on noin 5–15 kt, ja sitä lähetetään jopa 10 kertaa sekunnissa (kello muuttuu joka lähetyksessä). Tämä on noin 100–500 Mt tunnissa `raw.bin`-tiedostossa ottelun aikana ja noin kymmenesosa zstd-pakatussa `heat.raw.parquet`-tiedostossa. Katsojan asiakirja, jossa on kaikki pelaajat ja minimap, on useita kertoja suurempi. Arvio perustuu julkaistuun muotoon, ei pelissä mitattuun.

## Todennettu {#verified}

testattu asiakirjoilla, jotka ovat julkaistussa GSI-muodossa ja lähetetty käynnissä olevalle sovittimelle. Käynnissä olevaa peliä ei ole testattu.

## Lähde {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
