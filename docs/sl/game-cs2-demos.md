---
title: "Counter-Strike 2 (ponovitve)"
nav_order: 8
lang: "sl"
source: game-cs2-demos.md
source_hash: "d115f9085302"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (ponovitve) {#counter-strike-2-replays}

Po tekmi Counter-Strike 2 watcher spremeni ponovitev, ki jo je igra shranila, v datoteke, ki si jih lahko ogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `cs2-demos`, vrsta [`replay`](sources-and-rules.md); deluje ves čas (ne čaka, da se igra začne) in išče nove podatke na vsakih 5 s.*

## Kaj se zapiše {#what-is-recorded}

- položaj, smer pogleda, zdravje in denar vsakega igralca (vsak osmi tick)
- zadetki, smrti, poškodbe, granate, postavitve in deaktivacije bomb, kje so se zgodile
- krogi, rezultat, ekonomija; vrstica rezultatne table prijavljenega igralca kot statistika

## Od kod prihaja {#where-it-comes-from}

demo posnetki, ki jih shranja CS2: &lt;CS2&gt;/game/csgo/replays/\*.dem (preneseni iz zgodovine tekem) in &lt;CS2&gt;/game/csgo/\*.dem (posneti)

## Kako ga vklopiti {#how-to-switch-it-on}

prenesite demo tekme v CS2 (Watch > Your Matches) ali ga posnemite z ukazom konzole `record`

Nastavitve iz okoljskih spremenljivk:

- `HEAT3D_CS2`: mapa 3DHeat CS2, kadar ni poleg watcherja ali nameščena

## Kako deluje {#how-it-works}

Ponovitve in demo posnetki: kar igra shrani o tekmi, pretvorjeno, ko je tekma končana.

Ponovitev vsebuje vse, kar vmesnik v večigralskih igrah zadržuje - vsak položaj igralca, vsak zadetek tam, kjer se je zgodil -, in je datoteka, ki jo igra zapiše za svoje igralce, zato branje ničesar ne spremeni v igri. Watcher gleda mape, v katere igre shranjujejo ponovitve, počaka, da nova datoteka neha rasti (sicer jo igra še piše), in jo pretvori v delovni niti, tako da dolga pretvorba nikoli ne zadrži ostalega watcherja.

Ko je mapa prvič opažena, se ponovitve, ki so v njej že, samo zabeležijo in ne pretvorijo: igralec z leti demo posnetkov bi sicer čakal, da je watcher zaseden cel dan. `python -m heat3d_watch replays <adapter> [folder]` pretvori obstoječe na zahtevo.

#### Counter-Strike 2 {#counter-strike-2}

CS2 shranjuje demo posnetke, ki jih igralec prenese iz zgodovine tekem (zavihek Watch), v `<CS2>/game/csgo/replays/`, in tiste, posnete z ukazom konzole `record`, v `<CS2>/game/csgo/`. Vsak se pretvori s pretvornikom CS2 iz tega repozitorija (3DHeat CS2, github.com/Holdi601/3DHeat-CS2: položaj, smer pogleda, zdravje in denar vsakega igralca na vsakem osmem ticku; zadetki, smrti, poškodbe, granate, postavitve in deaktivacije bomb, kje so se zgodile; krogi, rezultat, ekonomija) v mapo seje kot tabelo `<map>/<match>.parquet` in povzetek `<match>.match.json`, ki ju bereta zavihka Toplotni zemljevid in Tekma v pregledovalniku. Rezultatna tabla tekme postane statistika seje: za igralca, čigar račun Steam je prijavljen na tem računalniku (iz Steamove datoteke `loginusers.vdf`), pod navadnimi imeni - ubojstva, smrti, asistence, ADR, KAST, odstotek zadetkov v glavo, prvi zadetki v krogu, clutchi - ter rezultat in krogi.

Isti modul streže tudi: [Dota 2 (ponovitve)](game-dota-replays.md), [osu! (ponovitve)](game-osu-replays.md), [Squad (ponovitve)](game-squad-demos.md), [War Thunder (ponovitve)](game-warthunder-replays.md), [World of Tanks (ponovitve)](game-wot-replays.md), [World of Warships (ponovitve)](game-wows-replays.md).

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Položaji zapisani | da |
| Os navzgor | `z` |
| Enote | palci (enote Source) |
| Zrcaljeno za pregledovalnik | `y` |
| Merilo enote (`scale`: pregledovalnik z njim pomnoži položaje) | 1 |

Ti podatki gredo v `meta.json` vsake seje (`axes`) in, kadar seja vsebuje položaje, v nogo `heat.parquet`, tako da pregledovalnik 3DHeat vrstice sam obrne in prilagodi merilo - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igrano na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `replay`: bere samo, kar igra ali platforma izda (ponovitve in demo posnetki, ki jih igra shrani), zato zapisuje tudi v spletni igri, ne le brez povezave; zastavica odloča samo, ali sme pomnilnik sploh kdaj biti branjen.
- Pomnilnik: tega adapterja **nikoli** ne bere. Samo adapterji `memory` berejo pomnilnik, in nikoli za igro, označeno kot igrano na spletu - glej [Viri in pravila](sources-and-rules.md).

## Zabeležena statistika {#statistics-recorded}

Ključi statistike, ki jih koda tega adapterja nastavi po imenu (`stats` vsake seje v `meta.json` in tabela `stats` v `watcher.sqlite`):

`map`, `rounds`, `score.{team}`, `won`

Ključ v zavitih oklepajih se dokonča med izvajanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz lastnih imen statistik igre, na tem seznamu niso; zgoraj v »Kaj se zapiše« so našteti.

## Popolnost {#completeness}

Pretvornik, ki ga ta adapter zažene, sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar ponovitev vsebuje, se prebere ali ohrani, nikoli ni izpuščeno. Prebere se v tabelo in dokument tekme, vse drugo se ohrani celo v spremljajočih datotekah ob njih in šteje v `selfCheck.completeness` dokumenta tekme. Dokumentacija pretvornika sama našteje, kaj bere, kaj ohrani surovo in česa ne more prebrati.

## Preverjeno {#verified}

Pretvornik je preizkušen na pravih turnirskih demo posnetkih; nadzor mape in statistika s testi.

## Vir {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
