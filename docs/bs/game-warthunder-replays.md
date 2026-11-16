---
title: "War Thunder (snimci)"
nav_order: 46
lang: "bs"
source: game-warthunder-replays.md
source_hash: "81f03926431d"
nav_exclude: true
search_exclude: true
---
# War Thunder (snimci) {#war-thunder-replays}

Poslije meča War Thunder, watcher pretvara snimak koji je igra spremila u datoteke koje možete pogledati na mapi u pregledniku 3DHeat.

*Tehnički detalji: adapter `warthunder-replays`, vrsta [`replay`](sources-and-rules.md); radi stalno (ne čeka da igra krene) i svakih 5 s traži nove podatke.*

## Šta se snima {#what-is-recorded}

- pozicija i stav svakog zrakoplova oko 4 puta u sekundi (koliko ih snimak sadrži)
- pozicije kopnenih jedinica iz kopnene sinkronizacije snimka (u snimcima iz 2026; ne u onima iz 2025)
- ko je bila koja jedinica (igrač, id vozila, tim) tamo gdje je ubistvo ili pogodak imenuje; ubistva, smrti i pogodci tamo gdje su se desili; chat; mapa
- ubistva, smrti, rezultat i zauzimanja autora snimka kao statistika

## Odakle dolazi {#where-it-comes-from}

snimci koje War Thunder sprema: &lt;War Thunder>/Replays/\*.wrpl (uz uključeno spremanje snimaka), pretvara ih vanjski konverter `heat3d-wt-replay` (exporters/ext/warthunder-replay)

## Kako to uključiti {#how-to-switch-it-on}

uključite spremanje snimaka u opcijama War Thundera i instalirajte konverter: pip install -e &lt;3DHeat>/exporters/ext/warthunder-replay

Postavke iz varijabli okruženja:

- `HEAT3D_WT_REPLAY`: folder konvertera (klon ili raspakirano izdanje), kad nije instaliran niti pored watchera

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

#### War Thunder {#war-thunder}

War Thunder sprema snimak svake bitke u `<War Thunder>/Replays/*.wrpl`
kad je spremanje snimaka uključeno u njegovim opcijama. Watcher ih ne čita
sam: čita ih vanjski konverter (3DHeat War Thunder replay converter,
`exporters/ext/warthunder-replay`, komanda `heat3d-wt-replay`), zaseban
projekat. Kad je komanda na PATH-u, ili je
paket instaliran ili pored watchera, svaki novi snimak se propušta kroz
nju u folder sesije kao `<map>/<match>.parquet` i `<match>.match.json`;
kad nije, watcher jednom kaže kako je instalirati i ostavlja folder na miru.
Šta konverter čita, a šta ne, stoji u njegovom README-u. Red autora
snimka iz rezultata - ubistva, kopnena ubistva, smrti, asistencije,
rezultat, zauzimanja - postaje statistika sesije.

Isti modul služi i: [Counter-Strike 2 (snimci)](game-cs2-demos.md), [Dota 2 (snimci)](game-dota-replays.md), [osu! (snimci)](game-osu-replays.md), [Squad (snimci)](game-squad-demos.md), [World of Tanks (snimci)](game-wot-replays.md), [World of Warships (snimci)](game-wows-replays.md).

## Pozicije i ose {#positions-and-axes}

| | |
|---|---|
| Pozicije se snimaju | da |
| Osa gore | `y` |
| Jedinice | metri (x istok, y gore, z sjever) |
| Zrcaljeno za preglednik | `z` |
| Skala jedinica (`scale`: preglednik njome množi pozicije) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima pozicije, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam rotira i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označeno kao igrano online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dozvoljeno (čita samo ono što igra objavljuje)".
- Vrsta `replay`: čita samo ono što igra ili platforma daje (snimke i demo-datoteke koje igra sprema), pa snima i u online igri kao i offline; zastavica odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj adapter je **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i to nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježene statistike {#statistics-recorded}

Ključevi statistika koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`map`

Ključ u vitičastim zagradama dovršava se za vrijeme rada (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz igrinih vlastitih imena statistika nisu na ovoj listi; "Šta se snima" iznad ih navodi.

## Potpunost {#completeness}

Konverter koji ovaj adapter pokreće slijedi 3DHeatovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što snimak drži čita se ili čuva, nikad ne odbacuje - čita se u tabelu i dokument meča, a sve ostalo se čuva cijelo u sidecar datotekama pored njih, i broji u `selfCheck.completeness` dokumenta meča. Dokumentacija samog konvertera navodi šta čita, šta čuva sirovo i šta ne može pročitati.

## Provjereno {#verified}

konverter je provjeren na javnim snimcima iz nekoliko verzija igre (ubistva i imena se slažu s rezultatima) i testovima na izgrađenim snimcima; ovaj hook testovima sa zamjenskom komandom

## Izvor {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
