---
title: "Rocket League (pelitila)"
nav_order: 39
lang: "fi"
source: game-rocketleague-stats.md
source_hash: "fd70d0540bb9"
nav_exclude: true
search_exclude: true
---
# Rocket League (pelitila) {#rocket-league-game-state}

Kun pelaat Rocket Leagueä, watcher tallentaa sen, mitä peli raportoi oman tietokoneesi ohjelmille, jotta voit katsoa sitä myöhemmin kartalta 3DHeat-katseluohjelmassa.

*Tekniset tiedot: sovitin `rocketleague-stats`, tyyppi [`gsi`](sources-and-rules.md); se toimii, kun `RocketLeague.exe` on käynnissä, ja hakee uutta dataa 0,05 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- pallo-osumat pallon paikalla (XYZ, Unreal-yksiköt), osuman tekijä ja nopeudet
- maalit osumapaikalla, maalintekijä, syöttäjä ja nopeus; poikkipuun osumat paikalla
- tilastovirta (pommitukset, torjunnat, laukaukset, epäpelastukset, ...), aloituspotkut, uusinnat, ottelun alku ja loppu, voittaja
- omat maalit, syötöt, torjunnat, laukaukset, pommitukset, kosketukset, pistemäärä ja joukkueiden pisteet UpdateState-viestistä
- jokaisen pelaajan lopullinen rivi ottelun päättyessä
- omat rivisi nimellä `me`: asetuksissa nimetty pelaaja (`config --set player_names.rocketleague-stats=<name>`), muuten se, jota pelin kamera seuraa uusintojen ulkopuolella
- autojen sijainteja ei ole: rajapinnassa niitä ei ole

## Mistä data tulee {#where-it-comes-from}

Stats API: TCP JSON-virta osoitteesta 127.0.0.1:49123 (portti kohdassa &lt;RL>\TAGame\Config\TAStatsAPI.ini tai DefaultStatsAPI.ini)

## Miten se kytketään päälle {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (asettaa PacketSendRate=30), käynnistä sitten Rocket League

Kirjoita komento terminaaliin, joka on avattu watcherin kansiossa (katso [Ennen aloitusta](before-you-start.md)). Jos se epäonnistuu, viimeinen rivi kertoo syyn; [Asennus ja käynnistys](installing-and-running.md) kertoo yleisimmät syyt.

`python -m heat3d_watch setup rocketleague-stats` luettelee tiedostot, joita se muuttaisi; `python -m heat3d_watch setup rocketleague-stats --apply` muuttaa ne ja säilyttää alkuperäisen nimellä `<file>.heat3d-backup` (katso [Komennot](commands.md#setup)). Se tulostaa `rocketleague-stats: changed: ...` jokaisesta muutoksesta tai `rocketleague-stats: nothing to change`, jos asetus on jo päällä.

## Miten se toimii {#how-it-works}

Rocket League: virallinen Stats API, paikallinen soketti, johon peli kirjoittaa ottelun tiedot.

Kytketään päälle tiedostossa `<RL>\TAGame\Config\TAStatsAPI.ini` - tai `DefaultStatsAPI.ini`,
jos edellistä ei ole, sillä peli lukee sen vain silloin - kohdassa
`[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   UpdateState-viestit sekunnissa; 0 (oletus) kytkee rajapinnan pois, enintään 120
Port             TCP-portti, jota peli kuuntelee, oletus 49123 (WebPort 49124 on WebSocket-kopio)
```

Peli on palvelin: asiakas yhdistää osoitteeseen 127.0.0.1:49123 ja lukee
virran JSON-objekteja `{"Event": nimi, "Data": {...}}` (jotkin versiot lähettävät Dataa
JSON-merkkijonona), peräkkäin ilman erottimia. Tapahtumat lähetetään sillä tikillä, jolla ne tapahtuvat,
taajuudesta riippumatta:

```text
UpdateState   MatchGuid, Players[] (Name, PrimaryId, Shortcut, TeamNum 0 sininen / 1 oranssi,
              Score, Goals, Shots, Assists, Saves, Touches, CarTouches, Demos; auton tila
              vain katsojille), Game (Teams[], TimeSeconds, bOvertime, Ball {Speed,
              TeamNum}, bReplay, bHasWinner, Winner, Arena, bHasTarget, Target)
BallHit       Players[] (Name, Shortcut, TeamNum), Ball {PreHitSpeed, PostHitSpeed, Location {X,Y,Z}}
GoalScored    GoalSpeed, GoalTime, ImpactLocation {X,Y,Z}, Scorer, Assister, BallLastTouch
CrossbarHit   BallLocation {X,Y,Z}, BallSpeed, ImpactForce, BallLastTouch
StatfeedEvent EventName, Type, MainTarget, SecondaryTarget
MatchEnded    WinnerTeamNum
MatchCreated, MatchInitialized, CountdownBegin, RoundStarted, GoalReplayStart/WillEnd/End,
MatchPaused/Unpaused, PodiumStart, ReplayCreated, MatchDestroyed, ClockUpdatedSeconds
```

Sijainnit ovat Unreal-yksiköitä (senttimetrejä), Z ylös; kenttä on noin 8200 x 10240,
maalit kohdassa Y = +-5120. Autojen sijainnit eivät kuulu rajapintaan: paikan saa vain pallo sillä hetkellä,
kun se osui, tuli maaliin tai osui poikkipuuhun.

Jokainen viesti tallennetaan myös kokonaisena (3DHeatin muunnossääntö, docs/converters.md
katseluohjelman repositoriossa): `heat.raw.parquet`, `type` on viestin Event-nimi, `text` on objekti sellaisena kuin se tuli virrasta.
UpdateState, joka on tavu tavulta sama kuin edellinen (pysäytetty ottelu, valikot), tallennetaan kerran ja lasketaan
meta.json:n `unchanged_replies`-kenttään. Ottelujen välissä tulevat viestit odottavat takalogissa seuraavan ottelun sessiota; se, mikä jää jäljelle, kun peli sulkeutuu, saa oman sessionsa.
Objektien välissä olevat merkit, jotka eivät ole JSONia, tallennetaan nimellä "junk".

Lähteet: <https://www.rocketleague.com/en/developer/stats-api> (virallinen sivu);
kenttien kirjoitus ja TCP-kehystys vahvistettu rlstatsapi-asiakasohjelmaa vasten
(<https://docs.rs/crate/rlstatsapi>, MIT; luettu vain tosiasioiden vuoksi).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennetaan | kyllä |
| Ylösakseli | `z` |
| Yksiköt | Unreal-yksiköt (senttimetrejä) |
| Peilattu katseluohjelmaa varten | ei mitään |
| Yksikköskaala (`scale`: katseluohjelma kertoo sijainnit tällä) | 1 |

Nämä menevät jokaisen session `meta.json`-tiedoston kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`-tiedoston alatunnisteeseen, joten 3DHeat-katseluohjelma kääntää ja skaalaa rivit itse - katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän muodossa "sallittu (lukee vain sen, minkä peli julkaisee)".
- Tyyppi `gsi`: se lukee vain sen, minkä peli tai alusta antaa ulos (pelitilan integraatio tai paikallinen rajapinta, jonka peli tarjoaa), joten se tallentaa myös verkkopelissä, aivan kuten offline-pelissäkin; lippu päättää vain sen, saako muistia koskaan lukea.
- Muisti: tämä sovitin **ei koskaan** lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliin, joka on merkitty pelatuksi verkossa - katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (jokaisen session `stats` `meta.json`-tiedostossa ja taulukossa `stats` tiedostossa `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohden). Avaimet, jotka koodi ottaa pelin kenttätaulukosta tai pelin omista tilastonimistä, eivät ole tässä luettelossa; "Mitä tallennetaan" -osio nimeää ne.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunnossääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): mitä lähde pitää sisällään, se luetaan tai tallennetaan, eikä sitä koskaan jätetä pois. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan muuttamattomana session `heat.raw.parquet`-tiedostoon (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja kaikki nimellä säilytetyt kentät; `used` merkitsee ne, mistä tuli myös rivejä), ja `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon - `lost` on 0.

**Luettu**

- BallHit (paikka, kuka, joukkue, nopeudet ennen ja jälkeen), GoalScored (osumapaikka, maalintekijä, syöttäjä, nopeus, maaliaika), CrossbarHit (paikka, viimeinen kosketus, nopeus, voima), StatfeedEvent (tapahtuma, tyyppi, päätilanne ja toissijainen kohde), MatchEnded (voittaja, tulos), jokainen muu tapahtuman nimi rivinä
- UpdateState-viestistä: areena, kameran kohde uusintojen ulkopuolella (kuka `me` on), joukkueiden pisteet, jokaisen pelaajan maalit, syötöt, torjunnat, laukaukset, pommitukset, kosketukset, autokosketukset ja pistemäärä (oma tilastoina, kaikkien `player_result`-rivinä ottelun päättyessä); ylityöaika ClockUpdatedSeconds-viestistä

**Tallennettu raakana**

- jokainen viesti kokonaisena sellaisena kuin se tuli virrasta (`text`), sen omalla Event-nimellä: `UpdateState` (jokaisen pelaajan PrimaryId ja Shortcut, kello, pallon nopeus ja joukkue, joukkueiden nimet ja värit, uusinta- ja voittajalaput, ja auton tila, kun peli sen lähettää), `BallHit`, `GoalScored` (pallon viimeisin kosketus), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` ja mikä tahansa tapahtuma, jonka myöhempi versio lisää
- UpdateState, joka on tavu tavulta sama kuin edellinen (pysäytetty, valikot), tallennetaan kerran ja lasketaan (`unchanged_replies` meta.json:ssa)
- viestit ottelujen välissä: omalla ajallaan ennen seuraavan ottelun alkua; viimeisen ottelun jälkeen omassa sessiossaan (`raw_only` meta.json:ssa)
- `unreadable`: objekti, joka ei ole Stats API -viesti; `junk`: objektien väliset merkit

**Ei saatavilla**

- auton sijainnit ja auton tila pelatessa: peli lähettää ne vain katsojille
- UpdateState kahden lähetyksen välillä: peli lähettää PacketSendRate-arvon verran sekunnissa (`setup` asettaa 30, peli sallii enintään 120); tapahtumat lähetetään sillä tikillä, jolla ne tapahtuvat
- WebSocket-kopio WebPort-portissa (49124): samat viestit kuin TCP-portissa, ei lueta kahdesti

**Koko**: UpdateState on 1-3 KB kuudelle pelaajalle, 30 kertaa sekunnissa: noin 100-300 MB tunnissa `raw.bin`-tiedostossa, kun ottelu on käynnissä, ja kymmenesosa tai vähemmän zstd-pakatussa `heat.raw.parquet`-tiedostossa (arvio dokumentoidusta muodosta, ei mitattu pelissä)

## Testattu {#verified}

testattu dokumentoidussa muodossa olevilla viesteillä, joita väärennetty paikallinen palvelin lähetti; ei testattu pelin kanssa

## Lähde {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
