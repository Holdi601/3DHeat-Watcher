---
title: "World of Warships (replay-i)"
nav_order: 49
lang: "hr"
source: game-wows-replays.md
source_hash: "c822aca3f6fe"
nav_exclude: true
search_exclude: true
---
# World of Warships (replay-i) {#world-of-warships-replays}

Nakon bitke u World of Warshipsu watcher pretvara snimku koju je igra spremila u datoteke koje možete pogledati na karti u 3DHeat pregledniku.

*Tehnički podaci: adapter `wows-replays`, vrsta [`replay`](sources-and-rules.md); radi stalno (ne čeka da igra počne) i traži nove podatke svakih 5 s.*

## Što se bilježi {#what-is-recorded}

- položaj i smjer svakog broda dok ga snimajući klijent vidi (oko 6 do 7 puta u sekundi dok se kreće), vlastiti brod cijelo vrijeme
- igrač, saveznik ili neprijatelj, i brod (brod snimajućeg igrača po nazivu, ostali po broju broda u igri); potopljeni brodovi tamo gdje su potonuli i njihovi ubojice tamo gdje su stajali
- karta; brod, ubojstva i preživljavanje igrača koji je snimao, kao statistika

## Odakle dolazi {#where-it-comes-from}

snimke koje World of Warships sprema: &lt;World of Warships>/replays/\*.wowsreplay (uz uključene snimke), pretvara ih vanjski pretvarač `heat3d-wows-replay` (exporters/ext/wows-replay)

## Kako ga uključiti {#how-to-switch-it-on}

uključite snimanje snimki u World of Warshipsu (`isReplayEnabled` u njegovoj datoteci preferences.xml, ili vlastita postavka igre tamo gdje je ima) i instalirajte pretvarač: pip install -e &lt;3DHeat>/exporters/ext/wows-replay

Postavke iz varijabli okruženja:

- `HEAT3D_WOWS_REPLAY`: mapa pretvarača (klon ili raspakirano izdanje), kad nije instaliran niti pored watchera

## Kako radi {#how-it-works}

Snimke i demo-snimke: ono što igra spremi o utakmici, pretvoreno kad je utakmica gotova.

Snimka sadrži sve što živo sučelje u višeigračkim igrama zadržava - položaj svakog igrača, svako ubojstvo tamo gdje se dogodilo - a to je datoteka koju igra piše za svoje igrače, pa čitanje ne dira ništa u igri. Watcher gleda mape u koje ih igre spremaju, čeka dok nova datoteka prestane rasti (inače je igra još piše), i pretvara je u radnoj niti, pa dugo pretvaranje nikad ne zaustavlja ostatak watchera.

Kad se mapa prvi put vidi, snimke koje su već u njoj samo se zabilježe, ne pretvaraju se: igrač s godinama demo-snimki inače bi čekao da watcher bude zauzet cijeli dan. `python -m heat3d_watch replays <adapter> [folder]` pretvara postojeće na zahtjev.

#### World of Tanks i World of Warships {#world-of-tanks-and-world-of-warships}

Obje spremaju snimku svake bitke u `<game>/replays/` kad je snimanje uključeno (`*.wotreplay`, `*.wowsreplay`); instalacije se pronalaze kroz popis Wargaming Game Centera, `C:/Games/World_of_Tanks*` / `World_of_Warships*`, i Steam. Kao i kod War Thundera, watcher ih sam ne čita: to radi vanjski pretvarač svake (`exporters/ext/wot-replay`, naredba `heat3d-wot-replay`; `exporters/ext/wows-replay`, naredba `heat3d-wows-replay`), odvojen da problem s Wargamingovim uvjetima korištenja dira samo taj pretvarač. Kad je pronađen na PATH-u, instaliran ili pored watchera, pretvara svaku novu snimku u `<map>/<match>.parquet` i `<match>.match.json` u mapi sesije; kad nedostaje, watcher jednom kaže kako ga instalirati. Redak igrača koji je snimao - vozilo ili brod, ubojstva, šteta (World of Tanks), je li preživio i ishod (World of Tanks) - postaje statistika sesije. Što svaki pretvarač čita, a što ne, navedeno je u njegovom README-u.

Isti modul služi i: [Counter-Strike 2 (replay-i)](game-cs2-demos.md), [Dota 2 (replay-i)](game-dota-replays.md), [osu! (replay-i)](game-osu-replays.md), [Squad (replay-i)](game-squad-demos.md), [War Thunder (replay-i)](game-warthunder-replays.md), [World of Tanks (replay-i)](game-wot-replays.md).

## Položaji i osi {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Os prema gore | `y` |
| Jedinice | jedinice svijeta World of Warshipsa (x istok, y gore, z sjever; jedna je 15 m po geometriji trupa, 30 m po dometima igre) |
| Zrcaljeno za preglednik | `z` |
| Mjerilo jedinica (`scale`: preglednik množi položaje s njim) | 1 |

Ovi podaci idu u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje `heat.parquet`-a, pa preglednik 3DHeat sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igrano na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dopušteno (čita samo ono što igra objavljuje)".
- Vrsta `replay`: čita samo ono što igra ili platforma predaje (snimke i demo-snimke koje igra sprema), pa bilježi i na mreži i izvan nje; oznaka odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri `memory` čitaju memoriju, i nikad za igru označenu kao igranu na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`map`, `survived`, `vehicle`, `won`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ za svaki tim). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih imena statistike igre nisu na ovom popisu; navedeni su u odjeljku "Što se bilježi" gore.

## Potpunost {#completeness}

Pretvarač koji ovaj adapter pokreće slijedi 3DHeatovo [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što snimka sadrži pročita se ili sačuva, ništa se ne baca - pročita se u tablicu i dokument utakmice, a sve ostalo sačuva se cijelo u pratećim datotekama uz njih, i broji se u `selfCheck.completeness` dokumenta utakmice. Dokumentacija samog pretvarača navodi što čita, što čuva sirovo i što ne može pročitati.

## Provjereno {#verified}

pretvarač je provjeren na javnim snimkama iz nekoliko verzija igre i testovima na izgrađenim snimkama; ovaj dio provjeren je testovima sa zamjenskom naredbom

## Izvor {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generirano iz adaptera pomoću tools/gen_game_pages.py; promijenite adapter i pokrenite ga ponovno umjesto uređivanja ove stranice. -->
