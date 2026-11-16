---
title: "War Thunder (ponovitve)"
nav_order: 46
lang: "sl"
source: game-warthunder-replays.md
source_hash: "81f03926431d"
nav_exclude: true
search_exclude: true
---
# War Thunder (ponovitve) {#war-thunder-replays}

Po bitki War Thunder watcher spremeni ponovitev, ki jo je igra shranila, v datoteke, ki si jih lahko ogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `warthunder-replays`, vrsta [`replay`](sources-and-rules.md); deluje ves čas (ne čaka, da se igra začne) in išče nove podatke na vsakih 5 s.*

## Kaj se zapiše {#what-is-recorded}

- položaj in drža vsakega letala približno 4-krat na sekundo (kolikor jih ponovitev vsebuje)
- položaji kopenskih enot iz kopenske sinhronizacije ponovitve (v ponovitvah iz leta 2026; v tistih iz leta 2025 ne)
- kdo je bila vsaka enota (igralec, id vozila, ekipa), kjer jo kak zadetek ali poškodba imenuje; zadetki, smrti in poškodbe, kjer so se zgodile; klepet; zemljevid
- ubojstva, smrti, točke in zavzetja avtorja ponovitve kot statistika

## Od kod prihaja {#where-it-comes-from}

ponovitve, ki jih shranja War Thunder: &lt;War Thunder&gt;/Replays/\*.wrpl (ko je shranjevanje ponovitev vklopljeno), pretvori pa jih zunanji pretvornik `heat3d-wt-replay` (exporters/ext/warthunder-replay)

## Kako ga vklopiti {#how-to-switch-it-on}

vklopite shranjevanje ponovitev v nastavitvah War Thunderja in namestite pretvornik: pip install -e &lt;3DHeat&gt;/exporters/ext/warthunder-replay

Nastavitve iz okoljskih spremenljivk:

- `HEAT3D_WT_REPLAY`: mapa pretvornika (klon ali razpakirana izdaja), kadar ni nameščen ali poleg watcherja

## Kako deluje {#how-it-works}

Ponovitve in demo posnetki: kar igra shrani o tekmi, pretvorjeno, ko je tekma končana.

Ponovitev vsebuje vse, kar vmesnik v večigralskih igrah zadržuje - vsak položaj igralca, vsak zadetek tam, kjer se je zgodil -, in je datoteka, ki jo igra zapiše za svoje igralce, zato branje ničesar ne spremeni v igri. Watcher gleda mape, v katere igre shranjujejo ponovitve, počaka, da nova datoteka neha rasti (sicer jo igra še piše), in jo pretvori v delovni niti, tako da dolga pretvorba nikoli ne zadrži ostalega watcherja.

Ko je mapa prvič opažena, se ponovitve, ki so v njej že, samo zabeležijo in ne pretvorijo: igralec z leti demo posnetkov bi sicer čakal, da je watcher zaseden cel dan. `python -m heat3d_watch replays <adapter> [folder]` pretvori obstoječe na zahtevo.

#### War Thunder {#war-thunder}

War Thunder shrani ponovitev vsake bitke v `<War Thunder>/Replays/*.wrpl`, kadar je shranjevanje ponovitev vklopljeno v nastavitvah. Watcher je sam ne bere: to naredi zunanji pretvornik (3DHeat War Thunder replay converter, `exporters/ext/warthunder-replay`, ukaz `heat3d-wt-replay`), samostojen projekt. Kadar je ukaz na PATH ali je paket nameščen ali poleg watcherja, se vsaka nova ponovitev požene skozenj, rezultat pa je v mapi seje kot `<map>/<match>.parquet` in `<match>.match.json`; kadar ni, watcher enkrat pove, kako ga namestiti, in mapo pusti pri miru. Kaj pretvornik bere in česa ne, je v njegovem README. Vrstica avtorja ponovitve iz rezultatov - ubojstva, ubojstva s tal, smrti, asistence, točke, zavzetja - postane statistika seje.

Isti modul streže tudi: [Counter-Strike 2 (ponovitve)](game-cs2-demos.md), [Dota 2 (ponovitve)](game-dota-replays.md), [osu! (ponovitve)](game-osu-replays.md), [Squad (ponovitve)](game-squad-demos.md), [World of Tanks (ponovitve)](game-wot-replays.md), [World of Warships (ponovitve)](game-wows-replays.md).

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Položaji zapisani | da |
| Os navzgor | `y` |
| Enote | metri (x vzhod, y navzgor, z sever) |
| Zrcaljeno za pregledovalnik | `z` |
| Merilo enote (`scale`: pregledovalnik z njim pomnoži položaje) | 1 |

Ti podatki gredo v `meta.json` vsake seje (`axes`) in, kadar seja vsebuje položaje, v nogo `heat.parquet`, tako da pregledovalnik 3DHeat vrstice sam obrne in prilagodi merilo - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igrano na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `replay`: bere samo, kar igra ali platforma izda (ponovitve in demo posnetki, ki jih igra shrani), zato zapisuje tudi v spletni igri, ne le brez povezave; zastavica odloča samo, ali sme pomnilnik sploh kdaj biti branjen.
- Pomnilnik: tega adapterja **nikoli** ne bere. Samo adapterji `memory` berejo pomnilnik, in nikoli za igro, označeno kot igrano na spletu - glej [Viri in pravila](sources-and-rules.md).

## Zabeležena statistika {#statistics-recorded}

Ključi statistike, ki jih koda tega adapterja nastavi po imenu (`stats` vsake seje v `meta.json` in tabela `stats` v `watcher.sqlite`):

`map`

Ključ v zavitih oklepajih se dokonča med izvajanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz lastnih imen statistik igre, na tem seznamu niso; zgoraj v »Kaj se zapiše« so našteti.

## Popolnost {#completeness}

Pretvornik, ki ga ta adapter zažene, sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar ponovitev vsebuje, se prebere ali ohrani, nikoli ni izpuščeno. Prebere se v tabelo in dokument tekme, vse drugo se ohrani celo v spremljajočih datotekah ob njih in šteje v `selfCheck.completeness` dokumenta tekme. Dokumentacija pretvornika sama našteje, kaj bere, kaj ohrani surovo in česa ne more prebrati.

## Preverjeno {#verified}

Pretvornik je preverjen na javnih ponovitvah iz več različic igre (imena in ubojstva se ujemajo z rezultati) in s testi na zgrajenih ponovitvah; ta del watcherja s testi z nadomestnim ukazom.

## Vir {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
