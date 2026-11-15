---
title: "osu! (replaye)"
nav_order: 35
lang: "sk"
source: game-osu-replays.md
source_hash: "9a1c74c4d5e0"
nav_exclude: true
search_exclude: true
---
# osu! (replaye) {#osu-replays}

Po zápase osu! watcher premení replay, ktorý hra uložila, na súbory, ktoré si môžete pozrieť na mape v 3DHeat prehliadači.

*Technické údaje: adaptér `osu-replays`, typ [`replay`](sources-and-rules.md); beží stále (nečaká, kým sa spustí hra) a hľadá nové dáta každých 5 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- dráha kurzora po hracej ploche (x 0..512, y 0..384) a stlačené klávesy, každý snímok
- skóre, combo, 300, 100, 50, gekis, katu, minuté, presnosť, mody, full combo
- life bar počas hry, hashe mapy a replaye, náhodné seed, ID online skóre

## Odkiaľ to berie {#where-it-comes-from}

replaye, ktoré ukladá osu! (stable): %LOCALAPPDATA%/osu!/Data/r/\*.osr (každá hra) a osu!/Replays/\*.osr (exportované)

## Ako to zapnúť {#how-to-switch-it-on}

Nič netreba zapínať: watcher číta zdroj tak, ako ho hra alebo platforma poskytuje.

## Ako to funguje {#how-it-works}

Replaye a dema: to, čo hra uloží z zápasu, prevedené, keď zápas skončí.

Replay obsahuje všetko, čo živé rozhranie v multiplayer hrách zadržiava –
polohu každého hráča, každé zabitie tam, kde sa stalo – a je to súbor, ktorý hra zapisuje pre svojich hráčov, takže jeho čítanie sa hry nijako nedotýka. Watcher sleduje priečinky, do ktorých hry replaye ukladajú, počká, kým sa nový súbor prestane zväčšovať (inak ho hra ešte zapisuje), a prevedie ho vo worker vlákne, takže dlhý prevod nezdrží ostatok watchera.

Keď sa priečinok prvýkrát uvidí, replaye, ktoré v ňom už sú, sa len zaznamenajú, nie prevedú: hráč s rokmi dem by inak zistil, že watcher je zaneprázdnený celý deň. `python -m heat3d_watch replays <adaptér> [priečinok]` prevedie existujúce na požiadanie.

#### osu! {#osu}

osu! (stable) ukladá každú hru do `osu!/Data/r/*.osr` a exportované do
`osu!/Replays/`. Watcher ich číta sám, podľa formátu, ktorý zverejňuje osu! wiki: dráha kurzora a klávesy každý snímok, riadok skóre, life bar, seed a ID skóre; súbor sa okrem toho uchová celý po častiach v `heat.raw.parquet` relácie.

Rovnaký modul slúži aj: [Counter-Strike 2 (replaye)](game-cs2-demos.md), [Dota 2 (replaye)](game-dota-replays.md), [Squad (replaye)](game-squad-demos.md), [War Thunder (replaye)](game-warthunder-replays.md), [World of Tanks (replaye)](game-wot-replays.md), [World of Warships (replaye)](game-wows-replays.md).

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | áno |
| Os nahor | `y` |
| Jednotky | pixely osu! (hracia plocha 512 x 384) |
| Zrkadlenie pre prehliadač | `z` |
| Mierka jednotiek (`scale`: prehliadač polohy touto hodnotou násobí) | 1 |

Tieto údaje idú do `meta.json` každej relácie (`axes`) a, ak má relácia polohy, do päty súboru `heat.parquet`, takže 3DHeat prehliadač si riadky sám otočí a zmení ich mierku – pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)“.
- Typ `replay`: číta len to, čo hra alebo platforma vydáva (replaye a dema, ktoré hra ukladá), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online – pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (štatistiky každej relácie `stats` v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`accuracy`, `full_combo`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč na tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z názvov štatistík hry, v tomto zozname nie sú; „Čo sa zaznamenáva“ vyššie ich pomenúva.

## Úplnosť {#completeness}

Watcher sa riadi [pravidlom konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, čo zdroj obsahuje, sa číta alebo uchováva, nikdy sa nezahadzuje. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia, ktoré sa uchovávajú podľa mena; `used` označuje to, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` – `lost` je 0.

**Čítané**

- každý snímok: riadok v jeho čase (milisekundy sčítané), x a y na hracej ploche, `keys` ako bity kláves (myš 1 a 2, klávesy 1 a 2, dym); v mania drží x namiesto miesta stlačené klávesy
- hlavička, každé pole: režim, verzia, MD5 mapy (súbor mapu pomenúva len ním), hráč, MD5 replaye, 300, 100, 50, gekis, katu, minuté, skóre, maximálne combo, full combo, mody (menami v meta.json `osu.modNames`), čas hry – ako štatistiky a v meta.json `osu`
- graf life baru: riadok `life` na každý bod (čas, life 0..1)
- snímok `-12345`: náhodné seed (`osu.seed`); ID online skóre (`osu.scoreId`); pri Target Practice jeho presnosť (`osu.targetPracticeAccuracy`)

**Uchované surové**

- súbor celý, po častiach, v heat.raw.parquet (`offset`, kde každá časť začína, aby časti boli súborom): `header`, `replay_data` (snímky komprimované LZMA tak, ako sú uložené), `score_id`, `mod_info`, a `trailing` pre to, čo nasleduje za časťami, ktoré formát popisuje (exporty osu!lazer tam pridávajú údaje) – uchované, nečítané

**Nedostupné**

- samotná mapa (objekty zásahov, časovanie): v replayi nie je; pomenovaná je len svojím MD5
- replaye osu!lazer: uložené v jeho databáze, nie ako súbory

**Veľkosť**: surový sprievodný súbor má približne veľkosť replaye (desiatky až stovky kilobajtov)

## Overené {#verified}

testované na replayoch zostavených podľa zverejneného formátu .osr; osu!lazer ukladá replaye vo svojom úložisku a nečíta sa

## Zdroj {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generované z adaptéra nástrojom tools/gen_game_pages.py; zmeňte adaptér a spustite to znova, namiesto úpravy tejto stránky. -->
