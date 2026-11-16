---
title: "War Thunder (replay-i)"
nav_order: 46
lang: "hr"
source: game-warthunder-replays.md
source_hash: "81f03926431d"
nav_exclude: true
search_exclude: true
---
# War Thunder (replay-i) {#war-thunder-replays}

Nakon bitke u War Thunderu watcher pretvara snimku koju je igra spremila u datoteke koje možete pogledati na karti u 3DHeat pregledniku.

*Tehnički podaci: adapter `warthunder-replays`, vrsta [`replay`](sources-and-rules.md); radi stalno (ne čeka da igra počne) i traži nove podatke svakih 5 s.*

## Što se bilježi {#what-is-recorded}

- položaj i stav svakog zrakoplova oko 4 puta u sekundi (koliko god snimka sadrži)
- položaji kopnenih jedinica iz sinkronizacije kopnenih jedinica u snimci (u snimkama iz 2026., ne u onima iz 2025.)
- tko je bila svaka jedinica (igrač, id vozila, tim) tamo gdje ju ubojstvo ili pogodak imenuje; ubojstva, smrti i pogoci tamo gdje su se dogodili; chat; karta
- ubojstva, smrti, rezultat i zauzimanja autora snimke kao statistika

## Odakle dolazi {#where-it-comes-from}

snimke koje War Thunder sprema: &lt;War Thunder>/Replays/\*.wrpl (uz uključeno spremanje snimki), pretvara ih vanjski pretvarač `heat3d-wt-replay` (exporters/ext/warthunder-replay)

## Kako ga uključiti {#how-to-switch-it-on}

uključite spremanje snimki u opcijama War Thundera i instalirajte pretvarač: pip install -e &lt;3DHeat>/exporters/ext/warthunder-replay

Postavke iz varijabli okruženja:

- `HEAT3D_WT_REPLAY`: mapa pretvarača (klon ili raspakirano izdanje), kad nije instaliran niti pored watchera

## Kako radi {#how-it-works}

Snimke i demo-snimke: ono što igra spremi o utakmici, pretvoreno kad je utakmica gotova.

Snimka sadrži sve što živo sučelje u višeigračkim igrama zadržava - položaj svakog igrača, svako ubojstvo tamo gdje se dogodilo - a to je datoteka koju igra piše za svoje igrače, pa čitanje ne dira ništa u igri. Watcher gleda mape u koje ih igre spremaju, čeka dok nova datoteka prestane rasti (inače je igra još piše), i pretvara je u radnoj niti, pa dugo pretvaranje nikad ne zaustavlja ostatak watchera.

Kad se mapa prvi put vidi, snimke koje su već u njoj samo se zabilježe, ne pretvaraju se: igrač s godinama demo-snimki inače bi čekao da watcher bude zauzet cijeli dan. `python -m heat3d_watch replays <adapter> [folder]` pretvara postojeće na zahtjev.

#### War Thunder {#war-thunder}

War Thunder sprema snimku svake bitke u `<War Thunder>/Replays/*.wrpl` kad je spremanje snimki uključeno u njegovim opcijama. Watcher ih sam ne čita: to radi vanjski pretvarač (3DHeat pretvarač War Thunder snimki, `exporters/ext/warthunder-replay`, naredba `heat3d-wt-replay`), zaseban projekt. Kad je naredba na PATH-u, ili je paket instaliran ili pored watchera, svaka nova snimka prolazi kroz njega u mapu sesije kao `<map>/<match>.parquet` i `<match>.match.json`; kad nije, watcher jednom kaže kako ga instalirati i ostavi mapu na miru. Što pretvarač čita, a što ne, navedeno je u njegovom README-u. Redak autora snimke iz rezultata - ubojstva, ubojstva na tlu, smrti, asistencije, rezultat, zauzimanja - postaje statistika sesije.

Isti modul služi i: [Counter-Strike 2 (replay-i)](game-cs2-demos.md), [Dota 2 (replay-i)](game-dota-replays.md), [osu! (replay-i)](game-osu-replays.md), [Squad (replay-i)](game-squad-demos.md), [World of Tanks (replay-i)](game-wot-replays.md), [World of Warships (replay-i)](game-wows-replays.md).

## Položaji i osi {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Os prema gore | `y` |
| Jedinice | metri (x istok, y gore, z sjever) |
| Zrcaljeno za preglednik | `z` |
| Mjerilo jedinica (`scale`: preglednik množi položaje s njim) | 1 |

Ovi podaci idu u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje `heat.parquet`-a, pa preglednik 3DHeat sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igrano na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dopušteno (čita samo ono što igra objavljuje)".
- Vrsta `replay`: čita samo ono što igra ili platforma predaje (snimke i demo-snimke koje igra sprema), pa bilježi i na mreži i izvan nje; oznaka odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri `memory` čitaju memoriju, i nikad za igru označenu kao igranu na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`map`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ za svaki tim). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih imena statistike igre nisu na ovom popisu; navedeni su u odjeljku "Što se bilježi" gore.

## Potpunost {#completeness}

Pretvarač koji ovaj adapter pokreće slijedi 3DHeatovo [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što snimka sadrži pročita se ili sačuva, ništa se ne baca - pročita se u tablicu i dokument utakmice, a sve ostalo sačuva se cijelo u pratećim datotekama uz njih, i broji se u `selfCheck.completeness` dokumenta utakmice. Dokumentacija samog pretvarača navodi što čita, što čuva sirovo i što ne može pročitati.

## Provjereno {#verified}

pretvarač je provjeren na javnim snimkama iz nekoliko verzija igre (ubojstva i imena se slažu s rezultatima) i testovima na izgrađenim snimkama; ovaj dio provjeren je testovima sa zamjenskom naredbom

## Izvor {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generirano iz adaptera pomoću tools/gen_game_pages.py; promijenite adapter i pokrenite ga ponovno umjesto uređivanja ove stranice. -->
