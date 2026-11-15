---
title: "League of Legends (pelitila)"
nav_order: 29
lang: "fi"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (pelitila) {#league-of-legends-game-state}

Kun pelaat League of Legendsia, watcher tallentaa sen, mitä peli raportoi omalla tietokoneellasi oleville ohjelmille, jotta voit myöhemmin katsoa sen tilastoina ja aikajanana.

*Tekniset tiedot: sovitin `lol-live`, tyyppi [`gsi`](sources-and-rules.md); se toimii, kun `League of Legends.exe` on käynnissä, ja etsii uutta dataa 0,5 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- ei sijainteja: rajapinnassa ei ole niitä
- tapahtumavirta: pelaajan tappamat, kuolemat ja avustukset sekä muiden sankarien tapot tappajan, uhrin ja avustajien kanssa
- lohikäärmeet, heraldit, baronit, tornit, inhibiittorit, moniteot, ässät, ensimmäinen veri, pelin alku ja loppu
- oman pelaajan tapot, kuolemat, avustukset, creep-pisteet, vartijapisteet, taso, kulta, sankari, pelin aika, tulos
- tavoitteet, jotka pelaajan joukkue otti

## Mistä data tulee {#where-it-comes-from}

Live Client Data API -rajapinta pelin asiakkaasta, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), ottelun aikana

## Miten se kytketään päälle {#how-to-switch-it-on}

Mitään ei tarvitse kytkeä päälle: watcher lukee lähteen juuri sellaisena kuin peli tai alusta sen antaa.

## Miten se toimii {#how-it-works}

League of Legends: Live Client Data API, jonka pelin asiakas tarjoaa ottelun aikana.

Kun ottelu on käynnissä (myös harjoitustyökalussa ja katsojatilassa), `League of Legends.exe` vastaa osoitteessa <https://127.0.0.1:2999> sillä, minkä pelaaja näkee pelin omassa käyttöliittymässä:

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} from EventID N on: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

Sijainteja ei ole: rajapinnassa ei ole niitä, joten League-sessio koostuu tapahtumista ja tilastoista, ei lämpötaulukosta. Sertifikaatti on itse allekirjoitettu, Riotin oman juurivarmenteen (`riotgames.pem`, julkaistu osoitteessa <https://static.developer.riotgames.com/docs/lol/riotgames.pem>) allekirjoittama. Sen käyttöehtoja ei ole kerrottu, joten sitä ei toimiteta mukana: laita se kohtaan `<data>\riotgames.pem`, jolloin yhteys todennetaan sillä. Ilman sitä todennus on pois päältä, ja vain 127.0.0.1-osoitteelle, ainoalle osoitteelle, johon tämä sovitin puhuu.

Riotin käytäntö sallii työkalujen näyttää sen, minkä pelaaja voi tietää itse pelistä, eikä mitään sen ylittävää laskettua (ei vihollisen ajastimia). Tämä tallentaa tapahtumavirran ja tulostaulun, jonka pelaaja näkee, sekä pelaajan omat luvut.

Jokainen vastaus tallennetaan myös sellaisenaan (3DHeatin muunninsääntö, docs/converters.md katselimen repositoriossa): `heat.raw.parquet`, `type` on päätepiste ("allgamedata", "eventdata"), `text` on JSON sellaisena kuin asiakas sen lähetti, `status` kun se ei ollut 200. Vastaus, joka on tavu tavulta sama kuin saman päätepisteen edellinen (tapahtumalista, kun mitään ei tapahdu), tallennetaan kerran ja lasketaan meta.json:n kenttään `unchanged_replies`. allgamedata sisältää kaiken, mitä muut päätepisteet tarjoavat (activeplayer*, playerlist, playerscores, playeritems, playersummonerspells, playermainrunes, gamestats), joten niitä ei kysytä erikseen. Vastaukset ennen ottelua (latausruutu) odottavat takalokissa ja menevät ottelun sessioon. GameEndin jälkeen sessio pysyy auki, kunnes asiakas sulkeutuu, joten lopputaulukon vastaukset tallentuvat siihen.

Lähde: <https://developer.riotgames.com/docs/lol#game-client-api>

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennettu | ei |
| Ylösakseli | `z` |
| Yksiköt | ei yksiköitä (ei sijainteja) |
| Peilattu katselinta varten | ei mitään |
| Yksikköskaala (`scale`: katselin kertoo sijainnit sillä) | 1 |

Nämä menevät kunkin session `meta.json`:n kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`:n footeriin. Näin 3DHeat-katselin kääntää ja skaalaa rivit itse, katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän muodossa "allowed (reads only what the game publishes)".
- Tyyppi `gsi`: se lukee vain sen, minkä peli tai alusta antaa ulos (pelin tilaintegraatio tai paikallinen rajapinta, jonka peli tarjoaa). Siksi se tallentaa myös verkkopelissä, aivan kuten offline-pelissä. Lippu ratkaisee vain sen, saako muistia koskaan lukea.
- Muisti: tämän sovittimen lukema **ei koskaan**. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliin, joka on merkitty verkkopeliksi. Katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (session `stats` tiedostossa `meta.json` ja taulussa `stats` tiedostossa `watcher.sqlite`):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

Aaltosulkeissa oleva avain täydentyy ajon aikana (`score.{team}` on yksi avain per joukkue). Avaimet, jotka koodi ottaa pelin kenttien taulukosta tai pelin omista tilastonimistä, eivät ole tässä listassa. Kohdassa "Mitä tallennetaan" ne on nimetty.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunninsääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): se, mitä lähde sisältää, luetaan tai tallennetaan, eikä mitään pudoteta. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan sellaisenaan session tiedostoon `heat.raw.parquet` (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja sen jälkeen nimellä säilytetyt kentät; `used` merkitsee ne, joista tuli myös rivejä). `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon, ja `lost` on 0.

**Luettu**

- tapahtumavirta eventdatasta: jokainen tapahtuma kerran, sen nimetyt kentät purettuina (tappaja, uhri ja avustajat sankareineen ja joukkueineen, rakenteet ja niiden puoli, lohikäärmeen tyyppi, varastetut tavoitteet, moniteot, ässät, ensimmäinen veri, tulos), ja jokainen muu tapahtuman kenttä omalla rivillään omalla nimellään
- allgamedatasta: oman pelaajan tapot, kuolemat, avustukset, creep-pisteet, vartijapisteet, taso, kulta, sankari, pelin aika, pelimuoto ja kartta

**Tallennettu raakana**

- `allgamedata`: jokainen vastaus sellaisenaan (`text`), joka 2 s: activePlayer (kyvyt, jokainen sankarin ominaisuus, täydet riimut, kulta, taso), allPlayers (esineet paikkoineen ja hintoineen, riimut, loitsut, pisteet, taso, kuollut ja uudelleensyntymisen ajastin, skini, linja, botti), tapahtumat, gameData (tila, aika, kartta, maasto); `used` on tosi, kun ottelu on käynnissä, epätosi lopputaulukolla
- `eventdata`: jokainen vastaus sellaisenaan, kysytty joka 0,5 s seuraavasta tapahtuma-id:stä alkaen; `used` on tosi, kun se toi uusia tapahtumia
- vastaus, joka on tavu tavulta sama kuin saman päätepisteen edellinen, tallennetaan kerran ja lasketaan (`unchanged_replies` meta.json:ssa); virhevastaukset (latausruudun RESOURCE_NOT_FOUND) tallennetaan `status`-kentän kanssa ennen ottelun alkua

**Ei saatavilla**

- sijainnit: rajapinnassa ei ole niitä (ei minikarttaa, ei koordinaatteja)
- muut päätepisteet (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): kukin tarjoaa osan allgamedatasta, joten niitä ei kysytä
- Replay-rajapinta (`/replay/*` samassa portissa): se toistaa tallenteita ja katsottuja pelejä, kun se on kytketty päälle game.cfg:ssä; se ei kuulu pelattuun otteluun
- League-asiakkaan lukkotiedoston päätepisteet: eivät julkaistu rajapinta (katso Lähteet ja säännöt)
- arvot kahden lukukerran välillä: rajapinta vastaa, kun siltä kysytään, eikä työnnä tietoja; tulostaulua kysytään 2 s välein, tapahtumia 0,5 s välein

**Koko**: allgamedata on 15–40 KB (se sisältää koko tapahtumalistan, joka kasvaa) 2 s välein: noin 30–70 Mt tunnissa `raw.bin`-tiedostossa; eventdata lisää vähän, koska muuttumattomat vastaukset lasketaan eikä tallenneta; zstd pienentää toistuvan JSONin `heat.raw.parquet`-tiedostossa muutamaan Mt:iin tunnissa (arvioitu dokumentoidusta muodosta)

## Todennettu {#verified}

Testattu paikallisella valepalvelimella, joka tarjoaa vastaukset dokumentoidussa muodossa. Peliä vastaan ei ole testattu.

## Lähdekoodi {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
