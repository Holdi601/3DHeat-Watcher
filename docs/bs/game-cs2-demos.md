---
title: "Counter-Strike 2 (snimci)"
nav_order: 8
lang: "bs"
source: game-cs2-demos.md
source_hash: "d115f9085302"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (snimci) {#counter-strike-2-replays}

Poslije meča Counter-Strike 2, watcher pretvara snimak koji je igra spremila u datoteke koje možete pogledati na mapi u pregledniku 3DHeat.

*Tehnički detalji: adapter `cs2-demos`, vrsta [`replay`](sources-and-rules.md); radi stalno (ne čeka da igra krene) i svakih 5 s traži nove podatke.*

## Šta se snima {#what-is-recorded}

- pozicija, smjer pogleda, zdravlje i novac svakog igrača (svaki 8. tick)
- ubistva, smrti, šteta, granate, postavljanja i deaktiviranja bombe tamo gdje su se desili
- runde, rezultat, ekonomija; red prijavljenog igrača iz tabele rezultata kao statistika

## Odakle dolazi {#where-it-comes-from}

demo-datoteke koje CS2 sprema: &lt;CS2>/game/csgo/replays/\*.dem (preuzete iz historije mečeva) i &lt;CS2>/game/csgo/\*.dem (snimljene)

## Kako to uključiti {#how-to-switch-it-on}

preuzmite demo meča u CS2 (Watch > Your Matches), ili ga snimite komandom `record` u konzoli

Postavke iz varijabli okruženja:

- `HEAT3D_CS2`: folder programa 3DHeat CS2, kad nije pored watchera niti instaliran

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

#### Counter-Strike 2 {#counter-strike-2}

CS2 sprema demo-datoteke koje igrač preuzme iz historije mečeva (kartica Watch) u
`<CS2>/game/csgo/replays/`, a one snimljene konzolnom komandom `record`
u `<CS2>/game/csgo/`. Svaka se pretvara vlastitim CS2 konverterom ovog repozitorija
(3DHeat CS2, github.com/Holdi601/3DHeat-CS2: pozicija, smjer pogleda, zdravlje i
novac svakog igrača na svaki osmi tick; ubistva, smrti, šteta, granate, postavljanja i deaktiviranja
bombe tamo gdje su se desili; runde, rezultat, ekonomija) u folder sesije, kao tabela
`<map>/<match>.parquet` i sažetak `<match>.match.json` koje čitaju kartice Heat
i Match preglednika. Tabela rezultata meča postaje statistika sesije:
za igrača čiji je Steam nalog prijavljen na ovom računaru (iz Steamovog
`loginusers.vdf`) pod njihovim običnim imenima - kills, deaths, assists, ADR, KAST,
postotak headshotova, opening kills, clutches - te rezultat i runde.

Isti modul služi i: [Dota 2 (snimci)](game-dota-replays.md), [osu! (snimci)](game-osu-replays.md), [Squad (snimci)](game-squad-demos.md), [War Thunder (snimci)](game-warthunder-replays.md), [World of Tanks (snimci)](game-wot-replays.md), [World of Warships (snimci)](game-wows-replays.md).

## Pozicije i ose {#positions-and-axes}

| | |
|---|---|
| Pozicije se snimaju | da |
| Osa gore | `z` |
| Jedinice | inči (Source jedinice) |
| Zrcaljeno za preglednik | `y` |
| Skala jedinica (`scale`: preglednik njome množi pozicije) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima pozicije, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam rotira i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označeno kao igrano online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dozvoljeno (čita samo ono što igra objavljuje)".
- Vrsta `replay`: čita samo ono što igra ili platforma daje (snimke i demo-datoteke koje igra sprema), pa snima i u online igri kao i offline; zastavica odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj adapter je **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i to nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježene statistike {#statistics-recorded}

Ključevi statistika koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`map`, `rounds`, `score.{team}`, `won`

Ključ u vitičastim zagradama dovršava se za vrijeme rada (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz igrinih vlastitih imena statistika nisu na ovoj listi; "Šta se snima" iznad ih navodi.

## Potpunost {#completeness}

Konverter koji ovaj adapter pokreće slijedi 3DHeatovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što snimak drži čita se ili čuva, nikad ne odbacuje - čita se u tabelu i dokument meča, a sve ostalo se čuva cijelo u sidecar datotekama pored njih, i broji u `selfCheck.completeness` dokumenta meča. Dokumentacija samog konvertera navodi šta čita, šta čuva sirovo i šta ne može pročitati.

## Provjereno {#verified}

konverter je testiran na pravim turnirskim demo-datotekama; praćenje foldera i statistika testovima

## Izvor {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
