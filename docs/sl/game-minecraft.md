---
title: "Minecraft (dnevniške datoteke)"
nav_order: 33
lang: "sl"
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (dnevniške datoteke) {#minecraft-log-files}

Medtem ko igrate Minecraft, watcher prebere datoteke, ki jih igra zapisuje, in shrani, kaj se je zgodilo, da jih lahko kasneje pogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `minecraft`, vrsta [`log`](sources-and-rules.md); teče, ko sta `javaw.exe` ali `java.exe` zagnana, in išče nove podatke vsakih 0,5 s.*

## Kaj se zapiše {#what-is-recorded}

- položaj lastnih in drugih igralcev (bloki = m, y navzgor) vsakič, ko svet shrani; dimenzija kot seja
- pojava s položajem, ko se igralec prijavi na (vgrajen) strežnik
- pridružitve, odhodi, smrti s sporočilom o smrti, dosežki, vrstice klepeta
- smrti, dosežki, sporočila v klepetu; iz datoteke statistike: čas igranja, razdalja, ubitja mobov in igralcev, skoki, škoda, pokopani bloki, izdelani predmeti (delež te seje)
- vsaka vrstica dnevnika in vsaka shranjena statistika, dosežek in datoteka igralca cela v heat.raw.parquet

## Od kod prihaja {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (sledi se), saves\\&lt;svet&gt;\stats\\&lt;uuid&gt;.json in saves\\&lt;svet&gt;\playerdata\\&lt;uuid&gt;.dat ter level.dat (gzip NBT), prebrani, ko igra to shrani

## Kako vklopiti {#how-to-switch-it-on}

Ničesar ni treba vklopiti: watcher bere vir tako, kot ga igra ali platforma ponuja.

## Kako deluje {#how-it-works}

Minecraft (Java Edition): dnevnik, statistika in datoteke igralcev, ki jih igra zapisuje.

Kje (`%APPDATA%\.minecraft\`):

* `logs\latest.log` - dnevnik igre, nov ob vsakem zagonu (stari se spakira v datirano .log.gz). Vrstice `[hh:mm:ss] [thread/LEVEL]: sporočilo` (nalagalniki modov pišejo `[ddMMMyyyy hh:mm:ss.mmm] [thread/LEVEL] [logger/]: ...`). Kar igralci vidijo v klepetu, je v njem: pridružitve in odhodi, sporočila o smrti, dosežki, klepet - vgrajen strežnik enoigralskega sveta zapiše iste vrstice še enkrat, zato se vrstica, ponovljena v isti sekundi, šteje enkrat. "Setting user: &lt;name&gt;" poimenuje igralca; strežnikov "&lt;name&gt;[...] logged in with entity id N at (x, y, z)" pove, kje se je pojavil.
* `saves\<svet>\stats\<uuid>.json` - zaslon statistike, zapisan, ko svet shrani (samodejno shranjevanje vsakih nekaj minut in ob odhodu): `stats` -> `minecraft:custom` (play_time v taktih, mob_kills, \*_one_cm razdalje, jump, ...), `minecraft:mined`, `minecraft:crafted`, ... Seštevki za svet; seja je razlika glede na to, kaj je datoteka povedala, ko se je igra zagnala. Oblika: <https://minecraft.wiki/w/Statistics>
* `saves\<svet>\playerdata\<uuid>.dat` (in `level.dat` -> Data -> Player za gostitelja enoigralskega sveta) - NBT, stisnjen z gzip, zapisan ob istih shranjevanjih: `Pos` [x, y, z] dvojne vrednosti, `Rotation` [yaw, pitch], `Dimension` ("minecraft:overworld"; int 0/-1/1 pred 1.16). NBT po <https://minecraft.wiki/w/NBT_format> - tu ga bere majhen lasten bralnik.
* `saves\<svet>\advancements\<uuid>.json` - napredek zaslona dosežkov, zapisan ob istih shranjevanjih.

Koordinate so bloki, en blok je en meter, y navzgor; x vzhod, z jug - desnosučen okvir, prikazan tak, kot je. Položaji pridejo samo, ko svet shrani, zato je pot nekaj točk na samodejno shranjevanje, ne sled; dimenzija je `session`, zato Nether ni narisan čez Overworld.

Vse prebrano se shrani cel v surovem spremljevalnem zapisu seje (pravilo pretvornika 3DHeat): vsaka vrstica dnevnika pod svojo stopnjo (`INFO`, `WARN`, `ERROR` ...; vrstica brez oglatega začetka, kot je sled sklada, kot `untagged`) in vsaka shranjena datoteka pod svojo vrsto (`stats`, `advancements`, `playerdata`, `level.dat`) - JSON kot besedilo, NBT kot bajti. Števila v datoteki statistike so razumljiva samo glede na to, kaj je datoteka povedala, ko se je igra začela, zato se shrani tudi ta prva kopija (`baseline`), ob prvi spremembi datoteke.

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Položaji zabeleženi | da |
| Navpična os | `y` |
| Enote | bloki (1 blok = 1 m) |
| Zrcaljeno za pregledovalnik | brez |
| Merilo enote (`scale`: pregledovalnik položaje pomnoži z njim) | 1 |

To gre v `meta.json` vsake seje (`axes`) in, kadar seja ima položaje, v nogo `heat.parquet`, zato pregledovalnik sam obrne in premeri vrstice - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igranje na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `log`: bere samo to, kar igra ali platforma ponudi (datoteke, ki jih igra zapisuje med delovanjem), zato zapisuje tudi pri igranju na spletu, ne samo brez njega; zastavica odloča samo, ali sme kdaj brati pomnilnik.
- Pomnilnik: **nikoli** ga ta adapter ne bere. Pomnilnik berejo samo adapterji `memory`, in nikoli za igro, označeno kot igranje na spletu - glej [Viri in pravila](sources-and-rules.md).

## Zabeležena statistika {#statistics-recorded}

Statistične ključe, ki jih koda tega adapterja nastavi po imenu (`stats` v `meta.json` vsake seje in tabela `stats` v `watcher.sqlite`):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

Ključ v zavitih oklepajih se dokonča med izvajanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele igrinih polj ali iz igrinih lastnih imen statistike, na tem seznamu niso; "Kaj se zapiše" zgoraj jih navaja.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornika](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir vsebuje, se prebere ali shrani, nikoli se ne zavrže. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani cel v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in vsako polje, shranjeno po imenu; `used` označi, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- latest.log: ime igralca (`Setting user`), prijave s položajem, pridružitve, odhodi, smrti s sporočilom o smrti, dosežki, vrstice klepeta, ustavitev strežnika
- stats/<uuid>.json: čas igranja, razdalja, ubitja mobov in igralcev, skoki, prejeta in dana škoda, pokopani bloki, izdelani predmeti - delež te seje
- playerdata/<uuid>.dat in level.dat (NBT): položaj, dimenzija, yaw, pitch, zdravje, nivo izkušenj

**Shranjeno surovo**

- vsaka vrstica latest.log cela, `type` = njena stopnja (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`), z nitjo logerja v `thread`, `used` tam, kjer je postala vrstica; vrstica brez oglatega začetka (sled sklada, banner moda) kot `untagged`
- vsak stats/<uuid>.json cel kot besedilo, `type` `stats` (`used`: njegova števila so v statistiki), z njegovo prvo kopijo od začetka igre kot `baseline`
- vsak advancements/<uuid>.json cel kot besedilo, `type` `advancements` (vsak kriterij in kdaj je bil izpolnjen; še ni spremenjen v vrstice)
- vsak playerdata/<uuid>.dat in level.dat cel kot bajti (NBT, gzip), `type` `playerdata` / `level.dat`, `used` tam, kjer je dal položaj: inventar, ender skrinja, učinki, točka ponovnega rojstva, pravila igre, seme sveta in čas so samo tukaj
- vsaka shranjena datoteka ima `world` in `file` (njena pot pod `saves`)

**Ni na voljo**

- sled potovanja: igra zapiše položaj igralca samo, ko svet shrani (vsakih nekaj minut in ob odhodu)
- položaji na strežniku, ki ga gosti nekdo drug: njegove datoteke sveta so na strežniku, ne tu; takrat se bere samo dnevnik
- sam svet (datoteke regij .mca, entitete, zemljevidi data/*.dat in napadi): obsežno in je teren, ne igra
- dnevniki prejšnjih sedenj (logs/*.log.gz): shranjeni, ko so bili igrani
- izdaja Bedrock: ne piše takega dnevnika ali datotek

**Velikost**: latest.log 0,1-2 MB na uro (več z modi); datoteka statistike 5-50 KB in datoteka igralca 5-100 KB na samodejno shranjevanje, level.dat 1-20 KB - skupaj okoli 1-5 MB na uro; zstd v heat.raw.parquet naredi besedilo približno desetkrat manjše (datoteke NBT so že stisnjene z gzip)

## Preverjeno {#verified}

preizkušeno na sintetičnih vrsticah dnevnika, JSON statistike in datotekah NBT, zgrajenih po objavljenih formatih; še nepreizkušeno z igro

## Vir {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
