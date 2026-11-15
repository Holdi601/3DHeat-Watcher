---
title: "World of Warships (snimci)"
nav_order: 49
lang: "bs"
source: game-wows-replays.md
source_hash: "c822aca3f6fe"
nav_exclude: true
search_exclude: true
---
# World of Warships (snimci) {#world-of-warships-replays}

Poslije meča World of Warships, watcher pretvara snimak koji je igra spremila u datoteke koje možete pogledati na mapi u pregledniku 3DHeat.

*Tehnički detalji: adapter `wows-replays`, vrsta [`replay`](sources-and-rules.md); radi stalno (ne čeka da igra krene) i svakih 5 s traži nove podatke.*

## Šta se snima {#what-is-recorded}

- pozicija i smjer svakog broda dok ga je klijent koji snima vidio (oko 6 do 7 puta u sekundi u kretanju), igračev vlastiti brod cijelo vrijeme
- igrač, saveznik ili neprijatelj, i brod (igrača koji snima po imenu, ostale po broju broda u igri); potopljeni brodovi tamo gdje su potonuli i njihovi ubice tamo gdje su stajali
- mapa; brod, ubistva i preživljavanje igrača koji snima kao statistika

## Odakle dolazi {#where-it-comes-from}

snimci koje World of Warships sprema: &lt;World of Warships>/replays/\*.wowsreplay (uz uključene snimke), pretvara ih vanjski konverter `heat3d-wows-replay` (exporters/ext/wows-replay)

## Kako to uključiti {#how-to-switch-it-on}

uključite snimanje u World of Warships (`isReplayEnabled` u njegovom preferences.xml, ili vlastita postavka igre gdje je ima) i instalirajte konverter: pip install -e &lt;3DHeat>/exporters/ext/wows-replay

Postavke iz varijabli okruženja:

- `HEAT3D_WOWS_REPLAY`: folder konvertera (klon ili raspakirano izdanje), kad nije instaliran niti pored watchera

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

#### World of Tanks i World of Warships {#world-of-tanks-and-world-of-warships}

Obje igre spremaju snimak svake bitke u `<game>/replays/` kad je snimanje uključeno
(`*.wotreplay`, `*.wowsreplay`); instalacije se nalaze preko liste Wargaming
Game Centera, `C:/Games/World_of_Tanks*` / `World_of_Warships*`, i
Steama. Kao i kod War Thundera, watcher ne čita datoteke sam: čita ih
po jedan vanjski konverter (`exporters/ext/wot-replay`, komanda
`heat3d-wot-replay`; `exporters/ext/wows-replay`, komanda
`heat3d-wows-replay`), držani odvojeno da problem s Wargamingovim uvjetima
dira samo taj konverter. Nađen na PATH-u, instaliran ili pored watchera,
pretvara svaki novi snimak u `<map>/<match>.parquet` i `<match>.match.json`
u folderu sesije; ako nedostaje, watcher jednom kaže kako ga instalirati. Red
igrača koji snima - vozilo ili brod, ubistva, šteta (World of Tanks),
je li preživio, i rezultat (World of Tanks) - postaje
statistika sesije. Šta svaki konverter čita, a šta ne, stoji u
njegovom README-u.

Isti modul služi i: [Counter-Strike 2 (snimci)](game-cs2-demos.md), [Dota 2 (snimci)](game-dota-replays.md), [osu! (snimci)](game-osu-replays.md), [Squad (snimci)](game-squad-demos.md), [War Thunder (snimci)](game-warthunder-replays.md), [World of Tanks (snimci)](game-wot-replays.md).

## Pozicije i ose {#positions-and-axes}

| | |
|---|---|
| Pozicije se snimaju | da |
| Osa gore | `y` |
| Jedinice | svjetske jedinice World of Warships (x istok, y gore, z sjever; jedna je 15 m po geometriji trupa, 30 m po dometima igre) |
| Zrcaljeno za preglednik | `z` |
| Skala jedinica (`scale`: preglednik njome množi pozicije) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima pozicije, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam rotira i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označeno kao igrano online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dozvoljeno (čita samo ono što igra objavljuje)".
- Vrsta `replay`: čita samo ono što igra ili platforma daje (snimke i demo-datoteke koje igra sprema), pa snima i u online igri kao i offline; zastavica odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj adapter je **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i to nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježene statistike {#statistics-recorded}

Ključevi statistika koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`map`, `survived`, `vehicle`, `won`

Ključ u vitičastim zagradama dovršava se za vrijeme rada (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz igrinih vlastitih imena statistika nisu na ovoj listi; "Šta se snima" iznad ih navodi.

## Potpunost {#completeness}

Konverter koji ovaj adapter pokreće slijedi 3DHeatovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što snimak drži čita se ili čuva, nikad ne odbacuje - čita se u tabelu i dokument meča, a sve ostalo se čuva cijelo u sidecar datotekama pored njih, i broji u `selfCheck.completeness` dokumenta meča. Dokumentacija samog konvertera navodi šta čita, šta čuva sirovo i šta ne može pročitati.

## Provjereno {#verified}

konverter je provjeren na javnim snimcima iz nekoliko verzija igre i testovima na izgrađenim snimcima; ovaj hook testovima sa zamjenskom komandom

## Izvor {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
