---
title: "Counter-Strike 2 (replay-i)"
nav_order: 8
lang: "hr"
source: game-cs2-demos.md
source_hash: "d115f9085302"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (replay-i) {#counter-strike-2-replays}

Nakon utakmice Counter-Strike 2 watcher pretvara snimku koju je igra spremila u datoteke koje možete pogledati na karti u 3DHeat pregledniku.

*Tehnički podaci: adapter `cs2-demos`, vrsta [`replay`](sources-and-rules.md); radi stalno (ne čeka da igra počne) i traži nove podatke svakih 5 s.*

## Što se bilježi {#what-is-recorded}

- položaj, smjer pogleda, zdravlje i novac svakog igrača (svaki osmi tick)
- ubojstva, smrti, šteta, bacanja granata, postavljanja i deaktiviranja bombi tamo gdje su se dogodili
- runde, rezultat, ekonomija; redak u tablici rezultata prijavljenog igrača kao statistika

## Odakle dolazi {#where-it-comes-from}

demo-snimke koje CS2 sprema: &lt;CS2>/game/csgo/replays/\*.dem (preuzete iz povijesti utakmica) i &lt;CS2>/game/csgo/\*.dem (snimljene)

## Kako ga uključiti {#how-to-switch-it-on}

preuzmite demo utakmice u CS2-u (Watch > Your Matches) ili snimite jednu naredbom konzole `record`

Postavke iz varijabli okruženja:

- `HEAT3D_CS2`: mapa 3DHeat CS2-a, kad ona nije pored watchera niti instalirana

## Kako radi {#how-it-works}

Snimke i demo-snimke: ono što igra spremi o utakmici, pretvoreno kad je utakmica gotova.

Snimka sadrži sve što živo sučelje u višeigračkim igrama zadržava - položaj svakog igrača, svako ubojstvo tamo gdje se dogodilo - a to je datoteka koju igra piše za svoje igrače, pa čitanje ne dira ništa u igri. Watcher gleda mape u koje ih igre spremaju, čeka dok nova datoteka prestane rasti (inače je igra još piše), i pretvara je u radnoj niti, pa dugo pretvaranje nikad ne zaustavlja ostatak watchera.

Kad se mapa prvi put vidi, snimke koje su već u njoj samo se zabilježe, ne pretvaraju se: igrač s godinama demo-snimki inače bi čekao da watcher bude zauzet cijeli dan. `python -m heat3d_watch replays <adapter> [folder]` pretvara postojeće na zahtjev.

#### Counter-Strike 2 {#counter-strike-2}

CS2 sprema demo-snimke koje igrač preuzme iz povijesti utakmica (kartica Watch) u `<CS2>/game/csgo/replays/`, a one snimljene naredbom konzole `record` u `<CS2>/game/csgo/`. Svaka se pretvara CS2 pretvaračem ovog repozitorija (3DHeat CS2, github.com/Holdi601/3DHeat-CS2: položaj, smjer pogleda, zdravlje i novac svakog igrača svakog osmog ticka; ubojstva, smrti, šteta, bacanja granata, postavljanja i deaktiviranja bombi tamo gdje su se dogodila; runde, rezultat, ekonomija) u mapu sesije, kao tablica `<map>/<match>.parquet` i sažetak `<match>.match.json` koje čitaju karte topline i kartice Meč u pregledniku. Redak rezultata utakmice postaje statistika sesije: za igrača čiji je Steam račun prijavljen na ovom računalu (iz Steamove datoteke `loginusers.vdf`) pod običnim nazivima - ubojstva, smrti, asistencije, ADR, KAST, postotak pogodaka u glavu, prva ubojstva runde, clutchevi - te rezultat i runde.

Isti modul služi i: [Dota 2 (replay-i)](game-dota-replays.md), [osu! (replay-i)](game-osu-replays.md), [Squad (replay-i)](game-squad-demos.md), [War Thunder (replay-i)](game-warthunder-replays.md), [World of Tanks (replay-i)](game-wot-replays.md), [World of Warships (replay-i)](game-wows-replays.md).

## Položaji i osi {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Os prema gore | `z` |
| Jedinice | inči (Source jedinice) |
| Zrcaljeno za preglednik | `y` |
| Mjerilo jedinica (`scale`: preglednik množi položaje s njim) | 1 |

Ovi podaci idu u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje `heat.parquet`-a, pa preglednik 3DHeat sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igrano na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dopušteno (čita samo ono što igra objavljuje)".
- Vrsta `replay`: čita samo ono što igra ili platforma predaje (snimke i demo-snimke koje igra sprema), pa bilježi i na mreži i izvan nje; oznaka odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri `memory` čitaju memoriju, i nikad za igru označenu kao igranu na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`map`, `rounds`, `score.{team}`, `won`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ za svaki tim). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih imena statistike igre nisu na ovom popisu; navedeni su u odjeljku "Što se bilježi" gore.

## Potpunost {#completeness}

Pretvarač koji ovaj adapter pokreće slijedi 3DHeatovo [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što snimka sadrži pročita se ili sačuva, ništa se ne baca - pročita se u tablicu i dokument utakmice, a sve ostalo sačuva se cijelo u pratećim datotekama uz njih, i broji se u `selfCheck.completeness` dokumenta utakmice. Dokumentacija samog pretvarača navodi što čita, što čuva sirovo i što ne može pročitati.

## Provjereno {#verified}

pretvarač je testiran na pravim turnirskim demo-snimkama; praćenje mape i statistika testovima

## Izvor {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generirano iz adaptera pomoću tools/gen_game_pages.py; promijenite adapter i pokrenite ga ponovno umjesto uređivanja ove stranice. -->
