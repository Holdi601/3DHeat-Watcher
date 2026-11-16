---
title: "Squad (replay-i)"
nav_order: 41
lang: "hr"
source: game-squad-demos.md
source_hash: "82c24e6df01c"
nav_exclude: true
search_exclude: true
---
# Squad (replay-i) {#squad-replays}

Nakon utakmice Squad watcher pretvara snimku koju je igra spremila u datoteke koje možete pogledati na karti u 3DHeat pregledniku.

*Tehnički podaci: adapter `squad-demos`, vrsta [`replay`](sources-and-rules.md); radi stalno (ne čeka da igra počne) i traži nove podatke svakih 5 s.*

## Što se bilježi {#what-is-recorded}

- položaj, kut tijela i brzinu svakog igrača svaki put kad ga server replicira (do 8 puta u sekundi), pješice i u kopnenim vozilima
- ime, tim, frakciju i odred svakog igrača, uz praćenje promjena tima
- ne: kretanje helikoptera, ubojstva i postavljive objekte - vidi README čitača

## Odakle dolazi {#where-it-comes-from}

demo-snimke servera koje Squad sprema administratorskom naredbom AdminDemoRec: &lt;server>/SquadGame/Saved/Demos/\*.replay, čita ih vanjski čitač `heat3d-squad-demo` (exporters/ext/squad-demo)

## Kako ga uključiti {#how-to-switch-it-on}

snimajte na serveru: dajte administratoru dozvolu `demos` u Admins.cfg, zatim u konzoli igre upišite AdminDemoRec &lt;name>, a za kraj AdminDemoStop; kopirajte demo ovdje i instalirajte čitač: pip install -e &lt;3DHeat>/exporters/ext/squad-demo

Postavke iz varijabli okruženja:

- `HEAT3D_SQUAD_DEMO`: mapa pretvarača (klon ili raspakirano izdanje), kad nije instaliran niti pored watchera

## Kako radi {#how-it-works}

Snimke i demo-snimke: ono što igra spremi o utakmici, pretvoreno kad je utakmica gotova.

Snimka sadrži sve što živo sučelje u višeigračkim igrama zadržava - položaj svakog igrača, svako ubojstvo tamo gdje se dogodilo - a to je datoteka koju igra piše za svoje igrače, pa čitanje ne dira ništa u igri. Watcher gleda mape u koje ih igre spremaju, čeka dok nova datoteka prestane rasti (inače je igra još piše), i pretvara je u radnoj niti, pa dugo pretvaranje nikad ne zaustavlja ostatak watchera.

Kad se mapa prvi put vidi, snimke koje su već u njoj samo se zabilježe, ne pretvaraju se: igrač s godinama demo-snimki inače bi čekao da watcher bude zauzet cijeli dan. `python -m heat3d_watch replays <adapter> [folder]` pretvara postojeće na zahtjev.

#### Squad {#squad}

Squadovi namjenski serveri snimaju demo utakmice kad administrator s dozvolom `demos` pokrene AdminDemoRec &lt;name> (i AdminDemoStop), u `<server>/SquadGame/Saved/Demos/<name>.replay` - Unreal Engine mrežna snimka koja sadrži ono što je server replicirao, uključujući kretanje svakog igrača. Watcher ih sam ne čita: to radi vanjski čitač (3DHeat Squad demo čitač, `exporters/ext/squad-demo`, naredba `heat3d-squad-demo`), zaseban projekt. Pokreće se na svakoj novoj demo-snimci u mapama u koje piše lokalni server, ili u mapi koju postavke dodaju za demo-snimke kopirane s iznajmljenog servera, i u mapu sesije sprema kao `<map>/<match>.parquet` i `<match>.match.json`. Sloj, mapa, broj igrača i trajanje utakmice postaju statistika sesije.

Isti modul služi i: [Counter-Strike 2 (replay-i)](game-cs2-demos.md), [Dota 2 (replay-i)](game-dota-replays.md), [osu! (replay-i)](game-osu-replays.md), [War Thunder (replay-i)](game-warthunder-replays.md), [World of Tanks (replay-i)](game-wot-replays.md), [World of Warships (replay-i)](game-wows-replays.md).

## Položaji i osi {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Os prema gore | `z` |
| Jedinice | Unreal jedinice (centimetri) |
| Zrcaljeno za preglednik | nijedno |
| Mjerilo jedinica (`scale`: preglednik množi položaje s njim) | 1 |

Ovi podaci idu u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje `heat.parquet`-a, pa preglednik 3DHeat sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igrano na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dopušteno (čita samo ono što igra objavljuje)".
- Vrsta `replay`: čita samo ono što igra ili platforma predaje (snimke i demo-snimke koje igra sprema), pa bilježi i na mreži i izvan nje; oznaka odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri `memory` čitaju memoriju, i nikad za igru označenu kao igranu na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`layer`, `map`, `match_seconds`, `players`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ za svaki tim). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih imena statistike igre nisu na ovom popisu; navedeni su u odjeljku "Što se bilježi" gore.

## Potpunost {#completeness}

Pretvarač koji ovaj adapter pokreće slijedi 3DHeatovo [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što snimka sadrži pročita se ili sačuva, ništa se ne baca - pročita se u tablicu i dokument utakmice, a sve ostalo sačuva se cijelo u pratećim datotekama uz njih, i broji se u `selfCheck.completeness` dokumenta utakmice. Dokumentacija samog pretvarača navodi što čita, što čuva sirovo i što ne može pročitati.

## Provjereno {#verified}

čitač je provjeren na javnim serverskim demo-snimkama (kretanje se slaže s brzinom koju nosi; tim svakog retka odgovara frakciji njegovog vojnika) i testovima na izgrađenim demo-snimkama; ovaj dio provjeren je testovima sa zamjenskom naredbom

## Izvor {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generirano iz adaptera pomoću tools/gen_game_pages.py; promijenite adapter i pokrenite ga ponovno umjesto uređivanja ove stranice. -->
