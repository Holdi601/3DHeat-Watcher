---
title: "Squad (ponovitve)"
nav_order: 41
lang: "sl"
source: game-squad-demos.md
source_hash: "82c24e6df01c"
nav_exclude: true
search_exclude: true
---
# Squad (ponovitve) {#squad-replays}

Po tekmi Squad watcher spremeni ponovitev, ki jo je igra shranila, v datoteke, ki si jih lahko ogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `squad-demos`, vrsta [`replay`](sources-and-rules.md); deluje ves čas (ne čaka, da se igra začne) in išče nove podatke na vsakih 5 s.*

## Kaj se zapiše {#what-is-recorded}

- položaj, smer telesa in hitrost vsakega igralca vsakič, ko jih strežnik replicira (največ 8-krat na sekundo), peš in v kopenskih vozilih
- ime, ekipo, frakcijo in skupino vsakega igralca, z upoštevanjem menjav ekip
- ne: gibanja helikopterjev, zadetki in postavljeni predmeti - glej README bralnika

## Od kod prihaja {#where-it-comes-from}

demo posnetki strežnika, ki jih Squad snema z ukazom skrbnika AdminDemoRec: &lt;server&gt;/SquadGame/Saved/Demos/\*.replay, bere pa jih zunanji bralnik `heat3d-squad-demo` (exporters/ext/squad-demo)

## Kako ga vklopiti {#how-to-switch-it-on}

posnemite na strežniku: skrbniku v Admins.cfg dodelite dovoljenje `demos`, nato v konzoli igre zaženite AdminDemoRec &lt;name&gt; in AdminDemoStop; demo kopirajte sem in namestite bralnik: pip install -e &lt;3DHeat&gt;/exporters/ext/squad-demo

Nastavitve iz okoljskih spremenljivk:

- `HEAT3D_SQUAD_DEMO`: mapa pretvornika (klon ali razpakirana izdaja), kadar ni nameščen ali poleg watcherja

## Kako deluje {#how-it-works}

Ponovitve in demo posnetki: kar igra shrani o tekmi, pretvorjeno, ko je tekma končana.

Ponovitev vsebuje vse, kar vmesnik v večigralskih igrah zadržuje - vsak položaj igralca, vsak zadetek tam, kjer se je zgodil -, in je datoteka, ki jo igra zapiše za svoje igralce, zato branje ničesar ne spremeni v igri. Watcher gleda mape, v katere igre shranjujejo ponovitve, počaka, da nova datoteka neha rasti (sicer jo igra še piše), in jo pretvori v delovni niti, tako da dolga pretvorba nikoli ne zadrži ostalega watcherja.

Ko je mapa prvič opažena, se ponovitve, ki so v njej že, samo zabeležijo in ne pretvorijo: igralec z leti demo posnetkov bi sicer čakal, da je watcher zaseden cel dan. `python -m heat3d_watch replays <adapter> [folder]` pretvori obstoječe na zahtevo.

#### Squad {#squad}

Namenski strežniki Squad posnamejo demo tekme, ko skrbnik z dovoljenjem `demos` zažene AdminDemoRec &lt;name&gt; (in AdminDemoStop), v `<server>/SquadGame/Saved/Demos/<name>.replay` - omrežna ponovitev Unreal Engine, ki vsebuje, kar je strežnik replikiral, vključno z gibanjem vsakega igralca. Watcher jih sam ne bere: to naredi zunanji bralnik (bralnik demo posnetkov Squad iz 3DHeat, `exporters/ext/squad-demo`, ukaz `heat3d-squad-demo`), samostojen projekt. Zažene se nad vsakim novim demo posnetkom v mapah, v katere piše lokalni strežnik, ali v mapi, ki jo nastavitve dodajo za demo posnetke, prenesene z najetega strežnika, in rezultat je v mapi seje kot `<map>/<match>.parquet` in `<match>.match.json`. Plast, zemljevid, število igralcev in dolžina tekme postanejo statistika seje.

Isti modul streže tudi: [Counter-Strike 2 (ponovitve)](game-cs2-demos.md), [Dota 2 (ponovitve)](game-dota-replays.md), [osu! (ponovitve)](game-osu-replays.md), [War Thunder (ponovitve)](game-warthunder-replays.md), [World of Tanks (ponovitve)](game-wot-replays.md), [World of Warships (ponovitve)](game-wows-replays.md).

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Položaji zapisani | da |
| Os navzgor | `z` |
| Enote | enote Unreal (centimetri) |
| Zrcaljeno za pregledovalnik | brez |
| Merilo enote (`scale`: pregledovalnik z njim pomnoži položaje) | 1 |

Ti podatki gredo v `meta.json` vsake seje (`axes`) in, kadar seja vsebuje položaje, v nogo `heat.parquet`, tako da pregledovalnik 3DHeat vrstice sam obrne in prilagodi merilo - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igrano na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `replay`: bere samo, kar igra ali platforma izda (ponovitve in demo posnetki, ki jih igra shrani), zato zapisuje tudi v spletni igri, ne le brez povezave; zastavica odloča samo, ali sme pomnilnik sploh kdaj biti branjen.
- Pomnilnik: tega adapterja **nikoli** ne bere. Samo adapterji `memory` berejo pomnilnik, in nikoli za igro, označeno kot igrano na spletu - glej [Viri in pravila](sources-and-rules.md).

## Zabeležena statistika {#statistics-recorded}

Ključi statistike, ki jih koda tega adapterja nastavi po imenu (`stats` vsake seje v `meta.json` in tabela `stats` v `watcher.sqlite`):

`layer`, `map`, `match_seconds`, `players`

Ključ v zavitih oklepajih se dokonča med izvajanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz lastnih imen statistik igre, na tem seznamu niso; zgoraj v »Kaj se zapiše« so našteti.

## Popolnost {#completeness}

Pretvornik, ki ga ta adapter zažene, sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar ponovitev vsebuje, se prebere ali ohrani, nikoli ni izpuščeno. Prebere se v tabelo in dokument tekme, vse drugo se ohrani celo v spremljajočih datotekah ob njih in šteje v `selfCheck.completeness` dokumenta tekme. Dokumentacija pretvornika sama našteje, kaj bere, kaj ohrani surovo in česa ne more prebrati.

## Preverjeno {#verified}

Bralnik je preverjen na javnih demo posnetkih strežnikov (gibanje se ujema s hitrostjo, ki jo nosi; ekipa vsake vrstice se ujema s frakcijo njenega vojaka) in s testi na zgrajenih demo posnetkih; ta del watcherja s testi z nadomestnim ukazom.

## Vir {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
