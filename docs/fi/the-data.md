---
title: "Tiedot"
nav_order: 5
lang: "fi"
source: the-data.md
source_hash: "6150cdc022fc"
nav_exclude: true
search_exclude: true
---
# Tiedot {#the-data}

Kaikki tallenteet ovat tavallisia tiedostoja datakansiossa (`%LOCALAPPDATA%\3DHeat\Watcher`, ellei toisin ole asetettu,
katso [Asennus ja käynnistys](installing-and-running.md#where-everything-is)). Voit lukea, kopioida tai poistaa niitä ilman
watcheria. `.jsonl`-tiedosto on tavallista tekstiä, yksi tapahtuma rivillä (Muistio avaa sen); `.parquet`-tiedosto on taulu,
jonka 3DHeat-katselin avaa (Excel ei - `stats --csv` kirjoittaa CSV-tiedostoja taulukkolaskentaan).

## Sessiokansiot {#session-folders}
![a session folder](../assets/img/session-folder.svg)


**Sessio** on yksi istunto yhdellä lähteellä: hetkestä, jolloin peli ensimmäisen kerran sanoo jotain, siihen asti kun se
pysähtyy (peli sulkeutuu, ottelu päättyy, ajo tai lento nollataan - kunkin sovittimen sivu kertoo, mikä aloittaa ja lopettaa
sessiot). Jokainen sessio saa kansion:

```text
<data>\sessions\<game>\<YYYY-MM-DD_HH-MM-SS>_<adapter id>\
    events.jsonl
    heat.parquet
    meta.json
```

- `<game>` on pelin nimi, jossa jokainen merkki muuta kuin kirjaimet, numerot, `.`, `_` ja `-` on korvattu merkillä `-` (enintään
  60 merkkiä): `EA-SPORTS-F1-25`, `Counter-Strike-2`. Sovittimet, jotka kattavat monta peliä (Steamin tilastot, Steam Timeline,
  NVIDIA-kohokohdat), tallentavat jokaisen session sen pelin alle, johon se kuuluu.
- Aika on session alku paikallisessa ajassa. Sessiot, jotka kuvaavat menneisyyttä (replay muunnettuna ottelun jälkeen, Steamin
  tilastotiedosto), käyttävät aikaa, jonka peli tai tiedosto antaa. Kaksi sessiota, jotka alkavat samassa sekunnissa, saavat
  perään `_2`, `_3`, ...
- Session tunnus tilastotietokannassa on `<game folder>/<session folder>`.

Sessio, jossa ei tallentunut mitään (peli istui valikoissaan, tai kaatui käynnistyessään), poistetaan kun se suljetaan, jotta
jokainen käynnistys ei jätä tyhjää kansiota.

Joissakin sessioissa on enemmän tiedostoja. Counter-Strike 2 -demosession kansiossa on muuntajan oma taulu ja yhteenveto
(`<map>/<match>.parquet`, `<match>.match.json`). iRacing-session listaa `.ibt`-tiedostot, jotka simulaattori kirjoitti istunnon
aikana, `telemetry_file`-tapahtumina.

## events.jsonl {#eventsjsonl}

`events.jsonl` sisältää yhden JSON-olion per rivi, yhden rivin per tapahtuma, kirjoitettuna heti kun tapahtuma tapahtuu. Tiedosto
on rivipuskuroitu, joten kaatuminen, sähkökatko tai tapettu prosessi ei menetä mitään, mikä on jo kirjoitettu; kaatumisen takia
katkaistu rivi ohitetaan tiedostoa luettaessa, ja jokainen rivi sitä ennen säilyy.

Jokaisella rivillä on samat perussarakkeet:

| Sarake | Tyyppi | Mitä se on |
|---|---|---|
| `time` | luku | sekunteja session alusta (4 desimaalia), tai pelin oma kello, jos sovitin antaa sen |
| `ms` | kokonaisluku | seinäkellon aika, Unix-millisekunteina |
| `event` | teksti | mitä tapahtui: `position`, `spawn`, `death`, `kill`, `lap`, `teleport`, `session_start`, ... |
| `x`, `y`, `z` | luku | missä, pelin omissa yksiköissä ja akseleilla (katso `axes` tiedostossa `meta.json`); vain kun kaikki kolme tunnetaan ja ovat äärellisiä |
| `player` | teksti | kuka: nimi, tunnus tai `me` pelaajalle itselleen (katso [Pelaajan omat rivit](#the-players-own-rows)) |
| `team` | teksti | heidän puolensa, kun peli sen kertoo |
| `session` | teksti | ottelu, kierros, vaihe, elämä tai lento, johon rivi kuuluu, kun peli sen kertoo |

Muut kentät, joita peli raportoi, seuraavat omalla nimellään (`speed_kmh`, `gear`, `lap_time`, `weapon`, `victim`, `hero`, ...).
Kentät ilman arvoa jätetään pois, ja niin tehdään myös lukuja, jotka eivät ole äärellisiä. Kaksi keksittyä riviä:

```json
{"time":12.3456,"ms":1777660501123,"event":"position","x":-412.5,"y":12.1,"z":233.0,"player":"me","session":"1","speed_kmh":187.4,"gear":5}
{"time":15.0,"ms":1777660503667,"event":"lap","x":-380.2,"y":12.0,"z":250.9,"player":"me","session":"1","lap_time":92.418,"lap":3}
```

Rivit ilman sijaintia (tappo-syötteen rivi, tasonnousu, tilastomuutos) jäävät `events.jsonl`-tiedostoon ja lasketaan
tilastoihin. Vain rivit, joilla on sijainti, menevät tauluun.

### Pelaajan omat rivit {#the-players-own-rows}

Lähde kertoo, keitä omat rivit ovat, eikä niitä koskaan arvata. Rivi on pelaajan oma, kun

- sen `player` on `me`: useimmat sovittimet, joiden lähde on pelaajan oma peli (oman auton tai koneen telemetria, pelin
  tilatieto, päiväkirja);
- sillä on `own_car` 1: kilpapelit, jotka tallentavat jokaisen auton kuljettajansa nimellä (EA SPORTS F1 pelaajan auton
  pelaajaindeksin mukaan, RaceRoom oman paikkansa mukaan, Automobilista 2 ja Project CARS 2 katsotun osallistujan mukaan)
  merkitsevät pelaajan auton näin ja pitävät kuljettajan nimen kentässä `player`;
- sen `player` on session `player` tiedostossa `meta.json`: nimi, jonka lähde antaa pelaajalle - Elite Dangerousin komentaja
  (päiväkirja on aina pelaajan), League of Legendsin replayn rivi Riot ID:stä asetuksissa.

War Thunder ja Rocket League nimeävät jokaisen pelaajan eivätkä kerro, kuka olet; kun nimesi on asetuksessa `player_names`,
omat rivisi muuttuvat `me`:ksi. [NVIDIA-kohokohdat](nvidia-highlights.md) etsivät hetken juuri näistä riveistä.

## heat.parquet {#heatparquet}

Kun sessio suljetaan, rivit `events.jsonl`-tiedostosta, joilla on `x`, `y` ja `z`, kirjoitetaan tiedostoon `heat.parquet`. Tämä
on taulu, jonka 3DHeat-katselin avaa. Jos sessiolla ei ole sijainteja, taulua ei kirjoiteta.

- Sarakkeet ovat `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session`, ja niiden jälkeen jokainen muu kenttä siinä
  järjestyksessä, jossa se ensimmäisen kerran esiintyy.
- `x`, `y`, `z` ja `time` ovat 64-bittisiä liukulukuja ja `ms` 64-bittinen kokonaisluku. Lisäsarake, jonka arvot ovat kaikki lukuja,
  on 64-bittinen liukuluku; mikä tahansa muu sarake on sanakirjakoodattua tekstiä (puuttuvat arvot ovat tyhjää tekstiä, ja listat ja
  oliot kirjoitetaan JSON-tekstinä).
- Tiedoston metatiedoissa on avain `heat3d`, jossa ovat lukuohjeet, joten katselin kytkee sarakkeet ja akselit itse (esimerkki,
  jossa `extra`-listaa on lyhennetty):

```json
{
  "version": 1,
  "kind": "heat3d-watch",
  "game": "EA SPORTS F1 25",
  "axes": {"up": "y", "flipX": false, "flipY": false, "flipZ": false, "scale": 1.0},
  "columns": {
    "x": "x", "y": "y", "z": "z",
    "time": "time", "timeUnit": "seconds",
    "personId": "player", "teamId": "team", "sessionId": "session",
    "extra": ["event", "speed_kmh", "gear", "lap_time", "lap"]
  }
}
```

`up` on pelin ylösakseli, `flipX`/`flipY`/`flipZ` peilaavat akselin, jotta vasenkätinen maailma ei piirry peilikuvana, ja `scale` on
katselimen yksikkömittakaava: katselin kertoo jokaisen sijainnin sillä ladatessaan taulun (0.01 muuttaisi senttimetrit metreiksi).
Jokainen sovitin kirjoittaa 1 ja pitää pelin omat yksiköt - useimmille metrit, Counter-Strike 2:lle Source-yksiköt (tuumat), Rocket
League Unreal-yksiköt (senttimetrit) - koska pelistä viety taso on samoissa yksiköissä, joten rivit osuvat sen päälle. `units`
tiedostossa `meta.json` kertoo, mikä yksikkö on. Jokaisen pelin sivu luettelee arvonsa kohdassa "Positions and axes".

Lentosimulaattorit (DCS World, Microsoft Flight Simulator, X-Plane, IL-2:n Tacview-tallenteet) sijoittavat rivinsä maapallolle, ja
niiden alatunniste kertoo, missä, jotta katselin voi asettaa todellisen maailman niiden alle:

```json
"geo": {"lat0": 42.0, "lon0": 42.0, "projection": "tangent-plane", "east": "x", "north": "z", "up": "y"}
```

`lat0`/`lon0` (asteita) ovat tasokartan origo, jossa rivit ovat; `east`, `north` ja `up` nimeävät sarakkeet, jotka sisältävät metrit
itään ja pohjoiseen siitä sekä korkeuden merenpinnasta. Origo on ensimmäinen kiinnitys X-Planelle ja MSFS:lle, tallenteen
vertailupiste IL-2:lle, ja teatterin kiinteä origo DCS:lle (ensimmäinen kiinnitys pyöristettynä kokonaisiin asteisiin teatterilla,
jota watcher ei tunne). Taulussa, jolla ei ole paikkaa maapallolla, ei ole avainta `geo`, ja muu alatunniste on sama kummassakin tapauksessa.

`heat.parquet` voidaan aina rakentaa uudelleen tiedostosta `events.jsonl` komennolla
`python -m heat3d_watch table <session folder>` (katso [Komennot](commands.md#table)). Tästä on hyötyä, kun `pyarrow` puuttui session
tallennuksen aikana.

## meta.json {#metajson}

`meta.json` tiivistää session. Se kirjoitetaan, kun sessio avataan, enintään 30 sekunnin välein kun tapahtumia tai tilastoja tulee,
ja kun sessio suljetaan. Tilastot pidetään muistissa näiden kirjoitusten välillä, joten kaatuminen voi menettää enintään viimeisen
puolen minuutin tilastot.

```json
{
  "format": "heat3d-watch-session",
  "version": 1,
  "watcher": "1.0.2",
  "game": "EA SPORTS F1 25",
  "adapter": "f1-25",
  "source": "UDP telemetry 127.0.0.1:20777 (...)",
  "multiplayer": true,
  "started": "2026-05-01T20:15:03",
  "ended": "2026-05-01T21:02:11",
  "seconds": 2828.0,
  "axes": {"up": "y", "flip_x": false, "flip_y": false, "flip_z": false, "scale": 1.0, "units": "metres"},
  "events": {"position": 52110, "lap": 412, "teleport": 3},
  "positions": 52530,
  "stats": {"laps": 20, "best_lap": 91.874, "distance_km": 106.3, "race_position": 4},
  "track": "..."
}
```

Session, jonka lähde nimeää pelaajan (katso [Pelaajan omat rivit](#the-players-own-rows)), saa myös kentän `"player"`: nimen, jolla
pelaajan omat rivit kulkevat. Lentosimulaattorien session tiedostossa on myös `"geo": {"lat0": .., "lon0": ..}`, jonka alatunniste
toistaa.

- `started` / `ended`: paikallinen aika sekunnin tarkkuudella; `ended` on `null`, kun sessio on käynnissä.
- `events`: kuinka monta kertaa kukin tapahtuma tapahtui, yleisin ensin. `positions` on rivien määrä, joilla on sijainti.
- `stats`: session luvut. Sovitin asettaa jokaisen, lisää siihen tai pitää korkeimman tai pienimmän arvon.
- Kaikki muu, mitä sovitin tietää istunnosta, tulee ylimmälle tasolle: rata, kartta, tehtävä, ottelun tunnus, Steamin sovellustunnus,
  replay-tiedosto, muistiprofiili ja versio. Session, joka on viimeistelty palautuksella, saa kentän `"recovered": true`.

## watcher.sqlite {#watchersqlite}

`watcher.sqlite` on tilastotietokanta. Rivi lisätään jokaiselle sessiolle, kun se suljetaan. Kolme taulua ovat tavallisia, joten mikä
tahansa SQL-työkalu, muistikirja tai taulukkolaskenta voi lukea ne ilman watcheria:

```sql
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,          -- <game folder>/<session folder>
  game TEXT NOT NULL,
  adapter TEXT NOT NULL,
  started REAL NOT NULL,        -- Unix seconds
  ended REAL,                   -- Unix seconds
  seconds REAL,
  folder TEXT NOT NULL,         -- the session folder's full path
  events INTEGER NOT NULL DEFAULT 0,
  positions INTEGER NOT NULL DEFAULT 0,
  multiplayer INTEGER NOT NULL DEFAULT 0,
  source TEXT
);
CREATE TABLE events (           -- per session, how many times each event happened
  session TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  event TEXT NOT NULL,
  count INTEGER NOT NULL,
  PRIMARY KEY (session, event)
);
CREATE TABLE stats (            -- per session, every number the game reported or the watcher counted
  session TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  key TEXT NOT NULL,
  value REAL,                   -- numbers
  text TEXT,                    -- everything else (a map name, a result, a hero)
  PRIMARY KEY (session, key)
);
```

Session, joka tallennetaan uudelleen (palautus, replay muunnetaan uudelleen), korvaa omat rivinsä. `multiplayer` on sovittimen lippu
(jotkin sovittimet asettavat sen sessiokohtaisesti, esimerkiksi DCS tehtävästä), ei tarkistus siitä, olitko verkossa. Totuusarvo
`stats`-taulussa tallennetaan tekstinä.

Esimerkkikysely, paras kierros pelikohtaisesti kaikista sessioista (pienempi on parempi):

```sql
SELECT s.game, MIN(t.value) AS best_lap
FROM stats t JOIN sessions s ON s.id = t.session
WHERE t.key = 'best_lap'
GROUP BY s.game;
```

`python -m heat3d_watch stats` tulostaa yhteissummat näistä tauluista (katso [Komennot](commands.md#stats)); sen sarake `best` on
pienin arvo ajoille, jotka pidetään parhaana aikana, ja sijoituksille, ja korkein muille.

## Palautus kaatumisen jälkeen {#recovery-after-a-crash}

Kun `run` käynnistyy, se etsii sessioita, jotka edellinen watcher jätti auki: `meta.json`, jossa ei ole `ended`-kenttää, ja
`events.jsonl`, jossa on vähintään yksi rivi. Se viimeistelee jokaisen:

- tapahtumien määrät ja sijaintien lukumäärä lasketaan uudelleen `events.jsonl`-tiedostosta, ohittaen katkaistun rivin;
- lopetus on viimeisen rivin seinäkellon aika (`ms`);
- tilastot ovat viimeisimmän `meta.json`-kirjoituksen tilastot (enintään 30 sekuntia vanhoja);
- lisätään `"recovered": true`, kirjoitetaan `heat.parquet`, ja sessio menee tiedostoon `watcher.sqlite`.

Loki kertoo "finished N session(s) left open by an earlier run". Lukitustiedosto estää toista watcheria "palauttamasta" käynnissä
olevan watcherin sessioita.

## CSV-vienti {#csv-export}
![stats --csv and table](../assets/img/csv-and-table.svg)


```bash
python -m heat3d_watch stats --csv out
```

kirjoittaa tiedostot `out\sessions.csv`, `out\events.csv` ja `out\stats.csv`. Jokainen tiedosto on yksi taulu tiedostosta
`watcher.sqlite`, kokonaisena, otsikkorivin kanssa, UTF-8-muodossa. Ajat ovat Unix-sekunteja kuten tietokannassa. `--game` ei rajaa
vientiä; jokainen sessio kirjoitetaan.

## Session avaaminen 3DHeat-katselimessa {#opening-a-session-in-the-3dheat-viewer}

Katselin: [github.com/Holdi601/3DHeat](https://github.com/Holdi601/3DHeat), dokumentaatio
[holdi601.github.io/3DHeat](https://holdi601.github.io/3DHeat/) - sen
[`.3dheat`-säiliö](https://holdi601.github.io/3DHeat/container.html) -sivu kuvaa yhden tiedoston per ottelu -muodon, jonka
replay-muuntajat voivat kirjoittaa.

Avaa session `heat.parquet` 3DHeat-katselimessa. Alatunniste kertoo katselimelle, mikä sarake on sijainti, aika, pelaaja, puoli ja
sessio, ja mihin suuntaan on ylös, joten mitään ei tarvitse kytkeä käsin. Sijainnit ovat pelin omissa maailmankoordinaateissa.
Kun ne piirretään muilla 3DHeat-työkaluilla viedyn tason päälle (esimerkiksi [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles)
-työkalulla), ne osuvat kohdalleen siellä, missä ne tapahtuivat.

- **Lämpökartat** käyttävät jokaista riviä, jolla on sijainti, suodatettuna sarakkeilla `event`, `player`, `team` tai `session` kuten
  mikä tahansa muu sarake.
- **Viivalämpö** piirtää viivan pelaajan jokaiselta riviltä seuraavaan, ja toistossa jokainen pelaaja on piste, joka liikkuu reitillä
  häntä perässään. Katselimen Reitit-paneeli valitsee sarakkeesta `event`, mitkä tapahtumat **aloittavat** reitin ja mitkä **lopettavat**
  sen. Watcher kirjoittaa rajaavat tapahtumat riveinä, joilla on sijainti, joten ne voi valita siellä:
  - aloitukset: `spawn`, `respawn`, `session_start`. Aloitus sulkee reitin, joka oli auki, piirtämättä viivaa uuteen paikkaan.
  - lopetukset: `death`, `finish`, `session_end` ja `teleport`. Viiva kulkee itse lopetusriviin asti, eli siihen paikkaan, jossa pelaaja
    kuoli, pysähtyi tai vietiin pois.

  Hyppy - paikka, johon on päästy matkustamatta sinne - on kaksi riviä: `teleport` paikassa, josta **lähdettiin**, ja aloitus paikassa,
  johon **saavuttiin**, heti sen jälkeen. Ajoneuvosovittimet kirjoittavat sellaisen aina, kun auto liikkui pidemmälle kuin se olisi voinut
  ajaa (takaisinkelaus tai flashback, nollaus tielle, takaisin kuoppiin, pikamatka), `spawn`-rivillä saapumispaikassa (`respawn` BeamNGn
  nollaukselle); `teleport`-rivi kantaa saapumispaikan kenttinä `to_x`, `to_y`, `to_z` ja matkan kenttänä `metres`, aloitusrivi
  `after: "teleport"`. Rekkasovittimet tekevät saman lautalle, junalle tai ladatulle tallennukselle, ja lentosovittimet hypylle, johon
  mikään lentokone ei pystyisi. Kun `teleport` on lopetuksissa ja `spawn` aloituksissa - mitä katselin ehdottaa itse - reitti päättyy
  paikassa, josta hyppy lähti, ja seuraava alkaa paikassa, johon se saapui, eikä mikään viiva ylitä karttaa. Reitti ei koskaan kulje
  `session`-sarakkeen muutoksen yli. Sijaintirivi kirjoitetaan muutaman kerran sekunnissa (useimmille telemetrioille 10 Hz), mikä antaa
  sujuvan viivan.
- Sarake `session` jakaa istunnon kierroksiin, vaiheisiin, elämiin tai ruumiisiin (Elite Dangerous pitää galaksirivit ja kunkin planeetan
  pinnan rivit erillään tällä tavalla). Valitse yksi katselimessa nähdäksesi vain sen osan.

Mitä katselin tekee riveille - suodattimet, värit, toisto - on kuvattu katselimen omassa dokumentaatiossa. Counter-Strike 2 -demosessiot
avataan muuntajan tiedostoilla `<map>/<match>.parquet` ja `<match>.match.json` katselimen lämpökartta- ja ottelu-välilehdillä.
iRacingin sijainnit tulevat session listaamista `.ibt`-tiedostoista, jotka katselin lukee itse.
