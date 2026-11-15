---
title: "Hearthstone (lokitiedostot)"
nav_order: 25
lang: "fi"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (lokitiedostot) {#hearthstone-log-files}

Kun pelaat Hearthstonea, watcher lukee pelin kirjoittamat tiedostot ja tallentaa, mitä tapahtui, jotta voit myöhemmin katsoa sen tilastoina ja aikajanana.

*Tekniset tiedot: sovitin `hearthstone`, tyyppi [`log`](sources-and-rules.md); se toimii, kun `Hearthstone.exe` on käynnissä, ja etsii uutta dataa 0,5 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- pelin alku ja loppu tuloksineen (voitto, tappio, tasapeli), vuorot ja vastustajan nimi
- jokainen vuoro
- jokainen Power.log-rivi ja muut lokit sellaisenaan tiedostossa heat.raw.parquet
- pelit, voitot, tappiot, tasapelit, vuorot, pisin peli

## Mistä data tulee {#where-it-comes-from}

&lt;install>\Logs\Power.log (tai Logs\Hearthstone_\*\Power.log), kirjoitetaan, kun %LOCALAPPDATA%\Blizzard\Hearthstone\log.config sisältää [Power]-osion, ja kaikki muut \*.log-tiedostot, joita peli kirjoittaa siihen

## Miten se kytketään päälle {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` lisää [Power]-lokituksen tiedostoon %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (varmuuskopio tallennetaan). Käynnistä peli uudelleen.

Kirjoita komento terminaaliin, joka on avattu watcherin kansiossa (katso [Ennen aloittamista](before-you-start.md)). Jos se epäonnistuu, viimeinen rivi kertoo syyn; [Asennus ja käyttö](installing-and-running.md) kertoo yleisimmät syyt.

`python -m heat3d_watch setup hearthstone` listaa tiedostot, joita se muuttaisi; `python -m heat3d_watch setup hearthstone --apply` muuttaa ne ja säilyttää alkuperäisen nimellä `<file>.heat3d-backup` (katso [Komennot](commands.md#setup)). Jokaisesta muutoksesta se tulostaa `hearthstone: changed: ...`, tai `hearthstone: nothing to change`, jos se on jo päällä.

## Miten se toimii {#how-it-works}

Hearthstone: pelin Power.log, jonka peli kirjoittaa, kun log.config pyytää sitä.

Hearthstone lukee tiedoston `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` käynnistyksessä. `[Power]`-osio, jossa `LogLevel=1` ja `FilePrinting=true`, saa sen kirjoittamaan jokaisen pelin tilamuutokset tiedostoon `<install>\Logs\Power.log` (uudemmat asiakkaat laittavat jokaisen käynnistyksen lokit omaan kansioonsa, `Logs\Hearthstone_<date>\`). Tämä on dokumentoitu vianjäljityslokitus, jota pelikorttiseurantaohjelmat ovat käyttäneet vuodesta 2014 (Hearthstone Deck Trackerin asennus kirjoittaa saman osion). `setup()` lisää osion ja tekee varmuuskopion tiedostosta sellaisena kuin se oli. Peli tarvitsee uudelleenkäynnistyksen, jotta se lukee asetuksen.

Käytetyt rivit, kaikki `GameState.DebugPrintPower()`-metodista (`PowerTaskList`-rivit toistavat ne, ja ne ohitetaan):

```text
D 20:15:01.1234567 GameState.DebugPrintPower() - CREATE_GAME
D 20:15:01.1234567 GameState.DebugPrintPower() -     Player EntityID=2 PlayerID=1 GameAccountId=[hi=1 lo=2]
D 20:15:01.1234567 GameState.DebugPrintGame() - PlayerID=1, PlayerName=Name#1234
D 20:15:02.1234567 GameState.DebugPrintPower() -     FULL_ENTITY - Updating [entityName=... id=4 zone=HAND
                   zonePos=0 cardId=CS2_029 player=1] CardID=CS2_029
D 20:16:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=TURN value=3
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=Name#1234 tag=PLAYSTATE value=WON
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=STATE value=COMPLETE
```

Pelaajan oma puoli on se, jonka aloituskädessä on nimetyt kortit (vastustajan kortit ovat piilossa). Muuten se on puoli, joka ei ole tekoäly (tili 0) tai "UNKNOWN HUMAN PLAYER". Rivit kantavat vain vuorokauden ajan; päivämäärä on tämän päivän.
Sijainteja ei ole.

Jokainen Power.log-rivi tallennetaan sellaisenaan session raakatiedostoon (3DHeatin muunninsääntö), mukaan lukien `PowerTaskList`-toistot, valinnat ja kohdepäivitykset. `type` on metodi, joka kirjoitti rivin (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions` ...). Mikä tahansa muu loki, jonka peli kirjoittaa sen viereen (`LoadingScreen.log`, `Decks.log`, `Zone.log`, `Arena.log` ...; kukin, kun log.config pyytää sitä, usein pelikorttiseurantaohjelmat tekevät niin), seurataan samalla tavalla ja tallennetaan sen nimen kanssa kentässä `log`.

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

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

Aaltosulkeissa oleva avain täydentyy ajon aikana (`score.{team}` on yksi avain per joukkue). Avaimet, jotka koodi ottaa pelin kenttien taulukosta tai pelin omista tilastonimistä, eivät ole tässä listassa. Kohdassa "Mitä tallennetaan" ne on nimetty.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunninsääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): se, mitä lähde sisältää, luetaan tai tallennetaan, eikä mitään pudoteta. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan sellaisenaan session tiedostoon `heat.raw.parquet` (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja sen jälkeen nimellä säilytetyt kentät; `used` merkitsee ne, joista tuli myös rivejä). `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon, ja `lost` on 0.

**Luettu**

- `CREATE_GAME`, pelaajat (entiteetti, pelaajan tunnus, tili; tili 0 on tekoäly) ja heidän nimensä (`DebugPrintGame`)
- kumpi puoli on pelaajan, nimettyjen korttien perusteella aloituskädestä
- `TAG_CHANGE` kohteista TURN, PLAYSTATE (won, lost, tied) ja STATE COMPLETE: vuorot, tulos, vastustaja

**Tallennettu raakana**

- jokainen Power.log-rivi sellaisenaan, `type` on metodi, joka sen kirjoitti (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard` ...), `log` on `Power`, `used` siellä, missä siitä tuli rivi: jokainen pelattu, nostettu ja paljastettu kortti, jokainen tilamuutos, hyökkäys, valinta ja vaihtoehto on tässä, ei vielä riveinä
- jokaisen muun lokin rivi samasta kansiosta (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX` ... mitä log.config kytkee päälle), samoilla `type`-arvoilla, ja lokin nimi kentässä `log`
- rivi ilman tason ja vuorokaudenajan merkintää tallennetaan tyypillä `untimed`, rivi ilman metodia tyypillä `untagged`

**Ei saatavilla**

- sijainnit: korttipelillä ei ole niitä
- vastustajan piilotetut kortit: loki nimeää kortin vasta, kun se on paljastettu
- lokit, joita log.config ei kytke päälle: `setup` pyytää vain [Power]-lokia; muut tulevat, kun toinen työkalu (pelikorttiseurantaohjelma) on kytkenyt ne päälle
- aiempien käynnistysten lokit: jokainen käynnistys kirjoittaa uuden kansion; ne, jotka ovat vanhempia kuin pelin tämä käynnistys, eivät lue uudelleen

**Koko**: Power.log Verbose-tilassa on noin 1–5 Mt per peli, 10–40 Mt tunnissa pelaamista; muut lokit lisäävät vähän; zstd tekee heat.raw.parquetista noin kymmenesosan tai vähemmän (rivit toistuvat paljon)

## Todennettu {#verified}

Testattu synteettisillä Power.log-riveillä pelin muodossa. Peliä vastaan ei ole testattu.

## Lähdekoodi {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
