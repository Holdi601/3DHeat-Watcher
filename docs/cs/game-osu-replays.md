---
title: "osu! (replaye)"
nav_order: 35
lang: "cs"
source: game-osu-replays.md
source_hash: "9a1c74c4d5e0"
nav_exclude: true
search_exclude: true
---
# osu! (replaye) {#osu-replays}

Po zápasu osu! Watcher přemění replay, který hra uložila, na soubory, na které se můžete podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `osu-replays`, druh [`replay`](sources-and-rules.md); běží pořád (nečeká, až se hra spustí) a hledá nová data každých 5 s.*

## Co se zaznamenává {#what-is-recorded}

- dráha kurzoru přes hrací pole (x 0..512, y 0..384) a stisknuté klávesy, každý snímek
- skóre, kombo, 300, 100, 50, gekis, katu, minutí, přesnost, modifikátory, full combo
- životní lišta během hry, hashe beatmapy a replaye, náhodné semínko, ID online skóre
- a všechna další čísla výsledku, která replay drží

## Odkud to pochází {#where-it-comes-from}

replaye, které ukládá osu! (stable): %LOCALAPPDATA%/osu!/Data/r/\*.osr (každá hra) a osu!/Replays/\*.osr (exportované)

## Jak to zapnout {#how-to-switch-it-on}

Nic se nemusí zapínat: Watcher čte zdroj tak, jak ho hra nebo platforma poskytuje.

## Jak to funguje {#how-it-works}

Replaye a dema: co hra uloží z zápasu, převedené, jakmile je zápas u konce.

Replay obsahuje vše, co živé rozhraní v multiplayerových hrách skrývá -
pozici každého hráče, každé zabití tam, kde se stalo -, a je to soubor, který
hra zapisuje pro své hráče, takže jeho čtení se hry vůbec nedotkne. Watcher sleduje
složky, do kterých hry replaye ukládají, počká, až nový soubor přestane růst (hra
do něj jinak stále zapisuje), a převádí ho ve vlákně na pozadí, takže dlouhý převod
nikdy nezdrží zbytek Watcheru.

Když se složka poprvé uvidí, replaye, které v ní už jsou, se jen zaznamenají, nepřevedou se:
hráč s lety nahraných dem by jinak Watcher zaměstnal na celý den. `python -m heat3d_watch replays <adaptér> [složka]` převede
existující na vyžádání.

#### osu! {#osu}

osu! (stable) ukládá každou hru do `osu!/Data/r/*.osr` a exportované do
`osu!/Replays/`. Watcher je čte sám, podle formátu, který zveřejňuje osu! wiki:
dráha kurzoru a klávesy každý snímek, řádek skóre, životní lišta, semínko a ID
skóre; soubor se vedle toho uchovává celý, po částech, v
`heat.raw.parquet` relace.

Stejný modul slouží také: [Counter-Strike 2 (replaye)](game-cs2-demos.md), [Dota 2 (replaye)](game-dota-replays.md), [Squad (replaye)](game-squad-demos.md), [War Thunder (replaye)](game-warthunder-replays.md), [World of Tanks (replaye)](game-wot-replays.md), [World of Warships (replaye)](game-wows-replays.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `y` |
| Jednotky | pixely osu! (hrací pole 512 x 384) |
| Zrcadleno pro prohlížeč | `z` |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto hodnoty se zapíší do `meta.json` (`axes`) každé relace a, pokud relace obsahuje pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítko řádků upravuje sám - viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukazuje jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `replay`: čte jen to, co hra nebo platforma vydává (replaye a dema, které hra ukládá), takže zaznamenává i v online hře i offline; příznak rozhoduje jen o tom, zda se paměť smí vůbec číst.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry `memory`, a nikdy u hry označené jako hraná online - viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (`stats` každé relace v `meta.json` a tabulka `stats` v `watcher.sqlite`):

`accuracy`, `full_combo`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedeny.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, kterou adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky), a `selfCheck.completeness` v `meta.json` počítá každý `type` - `lost` je 0.

**Načteno**

- každý snímek: řádek s časem (milisekundy sečtené), x a y na hracím poli, `keys` jako bity stisknutých kláves (myš 1 a 2, klávesy 1 a 2, kouř); v režimu mania nese x držené klávesy místo pozice
- hlavička, každé pole: režim, verze, MD5 beatmapy (soubor beatmapu označuje jen tímto), hráč, MD5 replaye, 300, 100, 50, gekis, katu, minutí, skóre, maximální kombo, full combo, modifikátory (jménem v meta.json `osu.modNames`), čas hry - jako statistiky a v meta.json `osu`
- graf životní lišty: řádek `life` pro každý bod (čas, život 0..1)
- snímek `-12345`: náhodné semínko (`osu.seed`); ID online skóre (`osu.scoreId`); v Target Practice její přesnost (`osu.targetPracticeAccuracy`)

**Uchováno surové**

- soubor celý, po částech, v heat.raw.parquet (`offset`, kde každá část začíná, takže části tvoří soubor): `header`, `replay_data` (snímky komprimované LZMA tak, jak jsou uloženy), `score_id`, `mod_info`, a `trailing` pro cokoli, co následuje za částmi, které formát popisuje (exporty osu!lazer tam přidávají data) - uloženo, nečteno

**Nedostupné**

- samotná beatmapa (objekty zásahů, časování): v replayi není; je pojmenována jen svým MD5
- replaye osu!lazer: uložené v jeho databázi, ne jako soubory

**Velikost**: surový doprovodný soubor má zhruba velikost replaye (desítky až stovky kilobajtů)

## Ověřeno {#verified}

testováno na replayích sestavených podle zveřejněného formátu .osr; osu!lazer ukládá replaye do vlastního úložiště a nečte se

## Zdroj {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte generování znovu, místo úpravy této stránky. -->
