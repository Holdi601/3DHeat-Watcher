---
title: "Squad (snimci)"
nav_order: 41
lang: "bs"
source: game-squad-demos.md
source_hash: "82c24e6df01c"
nav_exclude: true
search_exclude: true
---
# Squad (snimci) {#squad-replays}

Poslije meča Squad, watcher pretvara snimak koji je igra spremila u datoteke koje možete pogledati na mapi u pregledniku 3DHeat.

*Tehnički detalji: adapter `squad-demos`, vrsta [`replay`](sources-and-rules.md); radi stalno (ne čeka da igra krene) i svakih 5 s traži nove podatke.*

## Šta se snima {#what-is-recorded}

- pozicija, yaw tijela i brzina svakog igrača svaki put kad ih server replicira (do 8 puta u sekundi), pješice i u kopnenim vozilima
- ime, tim, frakcija i odred svakog igrača, uz praćenje promjena tima
- ne: kretanje helikoptera, ubistva i postavljivi objekti - vidite README čitača

## Odakle dolazi {#where-it-comes-from}

serverske demo-datoteke koje Squad snima admin komandom AdminDemoRec: &lt;server>/SquadGame/Saved/Demos/\*.replay, čita ih vanjski čitač `heat3d-squad-demo` (exporters/ext/squad-demo)

## Kako to uključiti {#how-to-switch-it-on}

snimajte na serveru: dajte adminu dozvolu `demos` u Admins.cfg, zatim AdminDemoRec &lt;name> i AdminDemoStop u konzoli igre; kopirajte demo ovamo i instalirajte čitač: pip install -e &lt;3DHeat>/exporters/ext/squad-demo

Postavke iz varijabli okruženja:

- `HEAT3D_SQUAD_DEMO`: folder konvertera (klon ili raspakirano izdanje), kad nije instaliran niti pored watchera

## Kako radi {#how-it-works}

Snimci i demo-datoteke: ono što igra sprema od meča, pretvoreno kad meč završi.

Snimak sadrži sve što uživo sučelje u multiplayer igrama zadržava za sebe -
poziciju svakog igrača, svako ubistvo tamo gdje se desilo - a to je datoteka koju
igra sama piše za svoje igrače, pa čitanje ne dira ništa u igri. Watcher
gleda foldere u koje igre spremaju snimke, čeka da nova datoteka prestane
rasti (inače je igra još piše) i pretvara je u radnoj
niti, pa duga pretvorba nikad ne zadržava ostatak watchera.

Kad se folder vidi prvi put, snimci koji su već u njemu samo se zabilježe, ne
pretvaraju se: igrač s godinama demo-datoteka inače bi našao watcher zauzet
cijeli dan. `python -m heat3d_watch replays <adapter> [folder]` pretvara
postojeće na zahtjev.

#### Squad {#squad}

Squadovi dedicirani serveri snimaju demo meča kad admin s dozvolom
`demos` pokrene AdminDemoRec &lt;name> (i AdminDemoStop), u
`<server>/SquadGame/Saved/Demos/<name>.replay` - mrežni snimak Unreal Enginea
koji sadrži ono što je server replicirao, uključujući kretanje svakog igrača.
Watcher ih ne čita sam: čita ih vanjski čitač (3DHeat Squad
demo reader, `exporters/ext/squad-demo`, komanda `heat3d-squad-demo`), zaseban
projekat. Pokreće se na svakom novom
demu u folderima u koje piše lokalni server, ili u folderu koji postavke dodaju
za demo-datoteke kopirane s iznajmljenog servera, u folder sesije kao
`<map>/<match>.parquet` i `<match>.match.json`. Layer, mapa, broj
igrača i trajanje meča postaju statistika sesije.

Isti modul služi i: [Counter-Strike 2 (snimci)](game-cs2-demos.md), [Dota 2 (snimci)](game-dota-replays.md), [osu! (snimci)](game-osu-replays.md), [War Thunder (snimci)](game-warthunder-replays.md), [World of Tanks (snimci)](game-wot-replays.md), [World of Warships (snimci)](game-wows-replays.md).

## Pozicije i ose {#positions-and-axes}

| | |
|---|---|
| Pozicije se snimaju | da |
| Osa gore | `z` |
| Jedinice | Unreal jedinice (centimetri) |
| Zrcaljeno za preglednik | nema |
| Skala jedinica (`scale`: preglednik njome množi pozicije) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima pozicije, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam rotira i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označeno kao igrano online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dozvoljeno (čita samo ono što igra objavljuje)".
- Vrsta `replay`: čita samo ono što igra ili platforma daje (snimke i demo-datoteke koje igra sprema), pa snima i u online igri kao i offline; zastavica odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj adapter je **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i to nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježene statistike {#statistics-recorded}

Ključevi statistika koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`layer`, `map`, `match_seconds`, `players`

Ključ u vitičastim zagradama dovršava se za vrijeme rada (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz igrinih vlastitih imena statistika nisu na ovoj listi; "Šta se snima" iznad ih navodi.

## Potpunost {#completeness}

Konverter koji ovaj adapter pokreće slijedi 3DHeatovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što snimak drži čita se ili čuva, nikad ne odbacuje - čita se u tabelu i dokument meča, a sve ostalo se čuva cijelo u sidecar datotekama pored njih, i broji u `selfCheck.completeness` dokumenta meča. Dokumentacija samog konvertera navodi šta čita, šta čuva sirovo i šta ne može pročitati.

## Provjereno {#verified}

čitač je provjeren na javnim serverskim demo-datotekama (kretanje se slaže s brzinom koju nosi; tim svakog reda odgovara frakciji njegovog vojnika) i testovima na izgrađenim demo-datotekama; ovaj hook testovima sa zamjenskom komandom

## Izvor {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
