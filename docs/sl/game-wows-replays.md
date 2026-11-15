---
title: "World of Warships (ponovitve)"
nav_order: 49
lang: "sl"
source: game-wows-replays.md
source_hash: "c822aca3f6fe"
nav_exclude: true
search_exclude: true
---
# World of Warships (ponovitve) {#world-of-warships-replays}

Po bitki World of Warships watcher spremeni ponovitev, ki jo je igra shranila, v datoteke, ki si jih lahko ogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `wows-replays`, vrsta [`replay`](sources-and-rules.md); deluje ves čas (ne čaka, da se igra začne) in išče nove podatke na vsakih 5 s.*

## Kaj se zapiše {#what-is-recorded}

- položaj in smer vsake ladje, dokler jo je posnemalni odjemalec videl (približno 6 do 7-krat na sekundo med premikanjem), ladja igralca ves čas
- igralec, zaveznik ali sovražnik, in ladja (igralčeva po imenu, druge po številki ladje, ki jo dodeli igra); potopljene ladje tam, kjer so potonile, in njihovi morilci tam, kjer so stali
- zemljevid; ladja, ubojstva in preživetje igralca, ki posname, kot statistika

## Od kod prihaja {#where-it-comes-from}

ponovitve, ki jih shranja World of Warships: &lt;World of Warships&gt;/replays/\*.wowsreplay (ko so ponovitve vklopljene), pretvori pa jih zunanji pretvornik `heat3d-wows-replay` (exporters/ext/wows-replay)

## Kako ga vklopiti {#how-to-switch-it-on}

vklopite shranjevanje ponovitev v World of Warships (`isReplayEnabled` v njegovi datoteki preferences.xml ali nastavitev igre, kjer jo ima) in namestite pretvornik: pip install -e &lt;3DHeat&gt;/exporters/ext/wows-replay

Nastavitve iz okoljskih spremenljivk:

- `HEAT3D_WOWS_REPLAY`: mapa pretvornika (klon ali razpakirana izdaja), kadar ni nameščen ali poleg watcherja

## Kako deluje {#how-it-works}

Ponovitve in demo posnetki: kar igra shrani o tekmi, pretvorjeno, ko je tekma končana.

Ponovitev vsebuje vse, kar vmesnik v večigralskih igrah zadržuje - vsak položaj igralca, vsak zadetek tam, kjer se je zgodil -, in je datoteka, ki jo igra zapiše za svoje igralce, zato branje ničesar ne spremeni v igri. Watcher gleda mape, v katere igre shranjujejo ponovitve, počaka, da nova datoteka neha rasti (sicer jo igra še piše), in jo pretvori v delovni niti, tako da dolga pretvorba nikoli ne zadrži ostalega watcherja.

Ko je mapa prvič opažena, se ponovitve, ki so v njej že, samo zabeležijo in ne pretvorijo: igralec z leti demo posnetkov bi sicer čakal, da je watcher zaseden cel dan. `python -m heat3d_watch replays <adapter> [folder]` pretvori obstoječe na zahtevo.

#### World of Tanks in World of Warships {#world-of-tanks-and-world-of-warships}

Oba shranjujeta ponovitev vsake bitke v `<game>/replays/`, kadar je snemanje vklopljeno (`*.wotreplay`, `*.wowsreplay`); namestitve se najdejo prek seznama Wargaming Game Center, `C:/Games/World_of_Tanks*` / `World_of_Warships*`, in Steama. Kot pri War Thunderju watcher datotek sam ne bere: to naredi zunanji pretvornik vsake (`exporters/ext/wot-replay`, ukaz `heat3d-wot-replay`; `exporters/ext/wows-replay`, ukaz `heat3d-wows-replay`), ločen, da težava z Wargamingovimi pogoji vpliva le na ta pretvornik. Najden na PATH, nameščen ali poleg watcherja, pretvori vsako novo ponovitev v `<map>/<match>.parquet` in `<match>.match.json` v mapi seje; kadar ga ni, watcher enkrat pove, kako ga namestiti. Vrstica igralca, ki posname - vozilo ali ladja, ubojstva, poškodbe (World of Tanks), ali je preživel, in izid (World of Tanks) - postane statistika seje. Kaj vsak pretvornik bere in česa ne, je v njegovem README.

Isti modul streže tudi: [Counter-Strike 2 (ponovitve)](game-cs2-demos.md), [Dota 2 (ponovitve)](game-dota-replays.md), [osu! (ponovitve)](game-osu-replays.md), [Squad (ponovitve)](game-squad-demos.md), [War Thunder (ponovitve)](game-warthunder-replays.md), [World of Tanks (ponovitve)](game-wot-replays.md).

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Položaji zapisani | da |
| Os navzgor | `y` |
| Enote | enote igre World of Warships (x vzhod, y navzgor, z sever; ena je 15 m po geometriji trupa, 30 m po igrinih dometih) |
| Zrcaljeno za pregledovalnik | `z` |
| Merilo enote (`scale`: pregledovalnik z njim pomnoži položaje) | 1 |

Ti podatki gredo v `meta.json` vsake seje (`axes`) in, kadar seja vsebuje položaje, v nogo `heat.parquet`, tako da pregledovalnik 3DHeat vrstice sam obrne in prilagodi merilo - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igrano na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `replay`: bere samo, kar igra ali platforma izda (ponovitve in demo posnetki, ki jih igra shrani), zato zapisuje tudi v spletni igri, ne le brez povezave; zastavica odloča samo, ali sme pomnilnik sploh kdaj biti branjen.
- Pomnilnik: tega adapterja **nikoli** ne bere. Samo adapterji `memory` berejo pomnilnik, in nikoli za igro, označeno kot igrano na spletu - glej [Viri in pravila](sources-and-rules.md).

## Zabeležena statistika {#statistics-recorded}

Ključi statistike, ki jih koda tega adapterja nastavi po imenu (`stats` vsake seje v `meta.json` in tabela `stats` v `watcher.sqlite`):

`map`, `survived`, `vehicle`, `won`

Ključ v zavitih oklepajih se dokonča med izvajanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz lastnih imen statistik igre, na tem seznamu niso; zgoraj v »Kaj se zapiše« so našteti.

## Popolnost {#completeness}

Pretvornik, ki ga ta adapter zažene, sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar ponovitev vsebuje, se prebere ali ohrani, nikoli ni izpuščeno. Prebere se v tabelo in dokument tekme, vse drugo se ohrani celo v spremljajočih datotekah ob njih in šteje v `selfCheck.completeness` dokumenta tekme. Dokumentacija pretvornika sama našteje, kaj bere, kaj ohrani surovo in česa ne more prebrati.

## Preverjeno {#verified}

Pretvornik je preverjen na javnih ponovitvah iz več različic igre in s testi na zgrajenih ponovitvah; ta del watcherja s testi z nadomestnim ukazom.

## Vir {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
