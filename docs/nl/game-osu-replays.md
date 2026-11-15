---
title: "osu! (replays)"
nav_order: 35
lang: "nl"
source: game-osu-replays.md
source_hash: "9a1c74c4d5e0"
nav_exclude: true
search_exclude: true
---
# osu! (replays) {#osu-replays}

Na een wedstrijd van osu! zet de watcher de replay die het spel heeft bewaard om in bestanden die je op een kaart in de 3DHeat-viewer kunt bekijken.

*Technische details: adapter `osu-replays`, soort [`replay`](sources-and-rules.md); hij draait altijd (hij wacht niet tot een spel start) en zoekt elke 5 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- het pad van de cursor over het speelveld (x 0..512, y 0..384) en de toetsen die ingedrukt zijn, elk frame
- score, combo, 300s/100s/50s/gekis/katus/missers, nauwkeurigheid, mods, full combo
- de levensbalk over het spel, de hashes van de beatmap en de replay, het willekeurige zaad, het online score-id

## Waar het vandaan komt {#where-it-comes-from}

replays die osu! (stable) bewaart: %LOCALAPPDATA%/osu!/Data/r/\*.osr (elke speelbeurt) en osu!/Replays/\*.osr (geëxporteerd)

## Hoe je het aanzet {#how-to-switch-it-on}

Niets hoeft aangezet te worden: de watcher leest de bron zoals het spel of platform die aanbiedt.

## Hoe het werkt {#how-it-works}

Replays en demo's: wat een spel van een wedstrijd bewaart, eenmaal omgezet als de wedstrijd voorbij is.

Een replay bevat alles wat een live-interface bij multiplayerspellen achterhoudt - elke positie van elke speler, elke kill waar hij gebeurde - en het is een bestand dat het spel voor zijn spelers schrijft, dus het lezen ervan raakt niets in het spel aan. De watcher kijkt naar de mappen waar spellen ze bewaren, wacht tot een nieuw bestand niet meer groeit (het spel schrijft er anders nog in), en zet het om in een werkthread, zodat een lange omzetting de rest van de watcher nooit ophoudt.

De eerste keer dat een map wordt gezien, worden de replays die er al in staan alleen genoteerd, niet omgezet: een speler met jaren aan demo's zou de watcher anders een dag lang bezighouden. `python -m heat3d_watch replays <adapter> [folder]` zet de bestaande op verzoek om.

#### osu! {#osu}

osu! (stable) bewaart elk spel in `osu!/Data/r/*.osr` en geëxporteerde in `osu!/Replays/`. De watcher leest ze zelf, volgens het formaat dat de osu!-wiki publiceert: het pad van de cursor en de toetsen elk frame, de scoreregel, de levensbalk, het zaad en het score-id. Het bestand wordt er helemaal naast bewaard, deel voor deel, in de `heat.raw.parquet` van de sessie.

Dezelfde module dient ook: [Counter-Strike 2 (replays)](game-cs2-demos.md), [Dota 2 (replays)](game-dota-replays.md), [Squad (replays)](game-squad-demos.md), [War Thunder (replays)](game-warthunder-replays.md), [World of Tanks (replays)](game-wot-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Opwaartse as | `y` |
| Eenheden | osu!-pixels (speelveld 512 x 384) |
| Gespiegeld voor de viewer | `z` |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities daarmee) | 1 |

Deze gaan naar de `meta.json` van elke sessie (`axes`) en, als de sessie posities heeft, naar de footer van `heat.parquet`, zodat de 3DHeat-viewer de rijen zelf draait en schaalt - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `replay`: hij leest alleen wat het spel of platform uitgeeft (replays en demo's die het spel bewaart), dus hij legt ook online spel vast, net als offline spel; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam zet (de `stats` van elke sessie in `meta.json` en de `stats`-tabel van `watcher.sqlite`):

`accuracy`, `full_combo`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met de velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggegooid. Naast de rijen wordt elk pakket, elke pagina, regel of elk antwoord dat de adapter ontvangt helemaal bewaard in de `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam wordt bewaard; `used` markeert wat ook rijen werd), en `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- elk frame: een rij op zijn tijd (milliseconden opgeteld), x en y op het speelveld, `keys` de toetsbits (muis 1 en 2, toetsen 1 en 2, smoke); in mania houdt x de ingedrukte toetsen in plaats van een plek
- de header, elk veld: modus, versie, de MD5 van de beatmap (het bestand noemt de beatmap alleen daarmee), de speler, de MD5 van de replay, 300s, 100s, 50s, gekis, katus, missers, score, max combo, full combo, mods (op naam in meta.json `osu.modNames`), de tijd van het spel - als statistieken en in meta.json `osu`
- de grafiek van de levensbalk: een `life`-rij per punt (tijd, leven 0..1)
- het frame `-12345`: het willekeurige zaad (`osu.seed`); het online score-id (`osu.scoreId`); bij Target Practice de nauwkeurigheid daarvan (`osu.targetPracticeAccuracy`)

**Ruw bewaard**

- het bestand helemaal, deel voor deel, in heat.raw.parquet (`offset` waar elk deel begint, zodat de delen het bestand vormen): `header`, `replay_data` (de LZMA-gecomprimeerde frames zoals opgeslagen), `score_id`, `mod_info`, en `trailing` voor wat er volgt op de delen die het formaat beschrijft (de exports van osu!lazer voegen daar data toe) - bewaard, niet gelezen

**Niet beschikbaar**

- de beatmap zelf (hit objects, timing): niet in een replay; hij wordt alleen met zijn MD5 genoemd
- de replays van osu!lazer zelf: bewaard in zijn database, niet als bestanden

**Grootte**: de ruwe bijlage is ongeveer zo groot als de replay (tientallen tot honderden kilobytes)

## Gecontroleerd {#verified}

getest op replays die volgens het gepubliceerde .osr-formaat zijn gemaakt; osu!lazer bewaart replays in zijn eigen opslag en wordt niet gelezen

## Bron {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
