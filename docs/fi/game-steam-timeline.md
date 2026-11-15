---
title: "Steam Timeline (alusta)"
nav_order: 43
lang: "fi"
source: game-steam-timeline.md
source_hash: "3a502e4ad09e"
nav_exclude: true
search_exclude: true
---
# Steam Timeline (alusta) {#steam-timeline-platform}

Vahti tallentaa, mitä Steam Timeline pitää peleistäsi, jotta voit myöhemmin katsella historiaasi tilastoina ja aikajanana.

*Tekniset tiedot: sovitin `steam-timeline`, laji [`platform`](sources-and-rules.md); se toimii koko ajan (ei odota pelin alkua) ja etsii uutta dataa 10 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- yksi sessio per aikajanatiedosto: sen alku ja loppu (session_start, session_end)
- pelin aikana avatut saavutukset ajoineen
- pelitilan muutokset (pelataan, valmistelu, valikot, latausruutu)
- tapahtumat, joita pelit lisäävät ISteamTimeline-rajapinnan kautta, otsikolla ja kuvauksella, kuvakkeensa nimen alla
- pelivaiheet (ottelu, tehtävä) tunnisteineen ja tageineen; tapahtumat niiden sisällä kantavat vaiheen tunnisteen kentässä session
- pelin aikajanalle näyttämät tilakuvaukset ("Round 3")
- Steamin omat tallennusvirheet

## Mistä se tulee {#where-it-comes-from}

%STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json

## Miten se otetaan käyttöön {#how-to-switch-it-on}

Steam > Settings > Game Recording: tallenna taustalla tai pyynnöstä (silloin Steam kirjoittaa aikajanat).

## Miten se toimii {#how-it-works}

Mitä käynnistysohjelma ja näytönohjain pitävät yllä pelistä: Steamin tilastot, saavutukset, pelattu aika ja aikajanat sekä NVIDIAn kohokohdat ja klipit.

Mikään näistä lähteistä ei vaadi, että peli tekee yhteistyötä tai on käynnissä, joten tässä olevat kolme sovitinta ovat aina päällä ja katsovat muutamaa tiedostoa muutaman sekunnin välein.

#### Steam Timeline (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`, joka kirjoitetaan, kun Steamin pelitallennus on päällä. Tiedosto on JSON, jossa numerot ovat merkkijonoina: "daterecorded" (Unix-sekunteina), "starttime" ja "endtime" (ms) sekä "entries", joista jokainen on {"id", "time" (ms daterecordedista), "type", ...}. Oikeissa tiedostoissa nähdyt tyypit:

```text
achievement        achievement_name - Steam lisää näitä jokaiseen peliin
gamemode           mode, ETimelineGameMode: 1 pelataan, 2 valmistelu, 3 valikot,
                   4 latausruutu
error              description - Steamin oma ("#GameRecording_RecordingFailed")
event              pelin AddInstantaneousTimelineEvent/AddRangeTimelineEvent:
                   title, description, icon, priority, duration (ms),
                   possible_clip - "You killed <name>" / "with the <weapon>"
state_description  title - SetTimelineTooltip ("Round 3")
phase              StartGamePhase..EndGamePhase-jakso: duration (ms), tags
                   [{name, icon, group, priority}] (mode, map ...)
```

Tiedoston rakenne on Steamin ja dokumentoimaton; kentät ovat API:n parametreja. Mikä tahansa muu tyyppi tallennetaan omalla nimellään ja kentillään.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Saman moduulin kautta toimivat myös: [NVIDIA-kohokohdat (alusta)](game-nvidia-highlights.md), [Steam-tilastot (alusta)](game-steam-stats.md).

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

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohti). Avaimet, jotka koodi ottaa pelin kentistä tai pelin omista tilastonimistä taulukosta, eivät ole tässä luettelossa; kohdassa "Mitä tallennetaan" ne mainitaan.

## Täydellisyys {#completeness}

Vahti noudattaa 3DHeatin [muunnossääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): mitä lähde sisältää, se luetaan tai säilytetään, sitä ei koskaan pudoteta. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, säilytetään kokonaisena session `heat.raw.parquet`-tiedostossa (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja kaikki nimellä säilytetyt kentät; `used` merkitsee, mistä tuli myös rivejä). `meta.json`-tiedoston `selfCheck.completeness` laskee jokaisen `type`-arvon, ja `lost` on 0.

**Luettu**

- jokainen merkintä kerran, rivinä sen ajassa: sen tyyppi, jokainen tavallinen kenttä (title, description, icon, priority, duration, possible_clip, saavutuksen nimi, mode ...), vaiheen tagit ryhmittäin, saavutuksen näyttönimi tilastoskeemasta; tiedoston alku ja loppu

**Säilytetään raakana**

- jokainen merkintä kokonaisena JSON-muodossa Steamin oman `type`-arvon alla (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, mikä tahansa muu): sisäkkäiset kentät, kuten tagin kuvake ja prioriteetti sekä kaikki, mitä myöhempi Steam lisää, ovat vain täällä
- `timeline`: tiedoston omat kentät (daterecorded, starttime, endtime ja muut), kun sessio avautuu ja uudelleen, kun ne muuttuvat

**Ei saatavilla**

- itse tallenne (video): Steam pitää sen omissa kansioissaan; sessio viittaa aikajanatiedostoon nimellä
- tiedoston luku, jota Steam kirjoittaa ja jota ei voi jäsentää, vaikka sen loppu on suljettu: laskettu (`bad` sovittimen tilassa) ja luetaan uudelleen seuraavassa muutoksessa, jolloin sen merkinnät otetaan

**Koko**: muutama sata merkintää, 100–300 tavua kukin, per pelitunti: selvästi alle 1 MB per tunti

## Todennettu {#verified}

Testattu oikeilla aikajanatiedostoilla paikallisesta asennuksesta: saavutus-, gamemode-, error- ja pelien omat event-, state_description- ja phase-merkinnät; tiedostomuoto on itsessään dokumentoimaton.

## Lähde {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
