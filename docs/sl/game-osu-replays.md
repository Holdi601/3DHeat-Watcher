---
title: "osu! (posnetki)"
nav_order: 35
lang: "sl"
source: game-osu-replays.md
source_hash: "9a1c74c4d5e0"
nav_exclude: true
search_exclude: true
---
# osu! (posnetki) {#osu-replays}

Po tekmi osu! watcher spremeni posnetek, ki ga je shranila igra, v datoteke, ki si jih lahko ogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `osu-replays`, vrsta [`replay`](sources-and-rules.md); teče ves čas (ne čaka, da se igra zažene) in vsakih 5 s preverja nove podatke.*

## Kaj se zapiše {#what-is-recorded}

- pot kazalca čez igrišče (x 0..512, y 0..384) in tipke, ki so pritisnjene, na vsakem okvirju
- rezultat, kombinacija, 300/100/50, gekiji/katuji/zgrešeni, natančnost, modi, polna kombinacija
- življenjska vrstica čez igro, zgoščeni zapisi zemljevida in posnetka, naključno seme, ID spletnega rezultata

## Od kod prihajajo {#where-it-comes-from}

posnetki, ki jih shrani osu! (stabilna različica): %LOCALAPPDATA%/osu!/Data/r/\*.osr (vsaka igra) in osu!/Replays/\*.osr (izvoženi)

## Kako vklopiti {#how-to-switch-it-on}

Ničesar ni treba vklopiti: watcher bere vir tako, kot ga igra ali platforma ponuja.

## Kako deluje {#how-it-works}

Posnetki in demo zapisi: kar igra shrani o tekmi, pretvorjeno, ko je tekma končana.

Posnetek hrani vse, kar vmesnik v živo zadržuje pri igrah z več igralci -
položaj vsakega igralca, vsako pobitje, kjer se je zgodilo - in je datoteka, ki jo igra zapiše
za svoje igralce, zato branje ničesar ne spremeni v igri. Watcher gleda v mape, kamor igre
shranjujejo posnetke, počaka, da se nova datoteka neha večati (igra jo sicer še piše), in jo pretvori
v delovni niti, da dolga pretvorba nikoli ne zadrži preostalega watcherja.

Ko se mapa prvič vidi, se posnetki v njej samo zabeležijo, ne pretvorijo: igralec z leti demo zapisov bi
sicer videl, da je watcher zaposlen cel dan. `python -m heat3d_watch replays <adapter> [mapa]` pretvori
obstoječe na zahtevo.

#### osu! {#osu}

osu! (stabilna različica) shrani vsako igro v `osu!/Data/r/*.osr`, izvožene pa v
`osu!/Replays/`. Watcher jih bere sam, po formatu, ki ga objavlja osu! wiki: pot kazalca in tipke na vsakem
okvirju, vrstica rezultata, življenjska vrstica, seme in ID rezultata; datoteka se poleg tega shrani celotna,
po delih, v `heat.raw.parquet` seje.

Isti modul streže tudi: [Counter-Strike 2 (posnetki)](game-cs2-demos.md), [Dota 2 (posnetki)](game-dota-replays.md), [Squad (posnetki)](game-squad-demos.md), [War Thunder (posnetki)](game-warthunder-replays.md), [World of Tanks (posnetki)](game-wot-replays.md), [World of Warships (posnetki)](game-wows-replays.md).

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Zabeleženi položaji | da |
| Navpična os | `y` |
| Enote | piksli osu! (igrišče 512 x 384) |
| Zrcaljenje za pregledovalnik | `z` |
| Merilo enote (`scale`: pregledovalnik z njim pomnoži položaje) | 1 |

Te vrednosti gredo v `meta.json` vsake seje (`axes`) in, kadar seja vsebuje položaje, v nogo `heat.parquet`, zato pregledovalnik 3DHeat vrti in meri vrstice sam - glejte [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igranje na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `replay`: bere samo, kar igra ali platforma ponudi (posnetke in demo zapise, ki jih igra shrani), zato zapisuje tudi pri igri na spletu in ne samo offline; zastavica odloča samo o tem, ali sme kdaj brati pomnilnik.
- Pomnilnik: tega adapterja **nikoli** ne bere. Samo adapterji vrste `memory` berejo pomnilnik, in nikoli za igro, označeno kot igranje na spletu - glejte [Viri in pravila](sources-and-rules.md).

## Zabeležene statistike {#statistics-recorded}

Ključi statistik, ki jih koda tega adapterja nastavlja po imenu (`stats` v `meta.json` vsake seje in tabela `stats` v `watcher.sqlite`):

`accuracy`, `full_combo`

Ključ v zavitih oklepajih se dokonča med delovanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz imen statistik igre, na tem seznamu niso; zgoraj v "Kaj se zapiše" so našteti.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir ima, se prebere ali shrani, nikoli ne izgine. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani nedotaknjen v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in polja, shranjena po imenu; `used` označuje, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- vsak okvir: vrstica ob svojem času (milisekunde seštete), x in y na igrišču, `keys` so bitne zastavice tipk (miš 1 in 2, tipki 1 in 2, dim); v mania je x namesto mesta število pritisnjenih tipk
- glava, vsako polje: način, različica, zgoščeni zapis MD5 zemljevida (datoteka ga imenuje samo s tem), igralec, zgoščeni zapis MD5 posnetka, 300, 100, 50, gekiji, katuji, zgrešeni, rezultat, največja kombinacija, polna kombinacija, modi (po imenu v meta.json `osu.modNames`), čas igre - kot statistike in v meta.json `osu`
- graf življenjske vrstice: vrstica `life` za vsako točko (čas, življenje 0..1)
- okvir `-12345`: naključno seme (`osu.seed`); ID spletnega rezultata (`osu.scoreId`); pri Target Practice njegova natančnost (`osu.targetPracticeAccuracy`)

**Shranjeno surovo**

- datoteka cela, po delih, v heat.raw.parquet (`offset`, kjer se vsak začne, da skupaj sestavljajo datoteko): `header`, `replay_data` (okvirji, stisnjeni z LZMA, kakor so shranjeni), `score_id`, `mod_info` in `trailing` za vse, kar sledi delom, ki jih format opisuje (izvoženi posnetki osu!lazer tam dodajo podatke) - shranjeno, ne prebrano

**Ni na voljo**

- sam zemljevid: zadetki, časovanje - v posnetku ga ni; imenovan je samo z zgoščenim zapisom MD5
- posnetki osu!lazer: shranjeni so v njegovi bazi, ne kot datoteke

**Velikost**: surovi zapis je približno velik kot posnetek (desetine do stotine kilobajtov)

## Preverjeno {#verified}

preizkušeno na posnetkih, zgrajenih po objavljenem formatu .osr; osu!lazer hrani posnetke v svojem skladišču in ni branjen

## Vir {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
