---
title: "Counter-Strike 2 (replaye)"
nav_order: 8
lang: "cs"
source: game-cs2-demos.md
source_hash: "d115f9085302"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (replaye) {#counter-strike-2-replays}

Po zápase Counter-Strike 2 Watcher promění replay, který hra uložila, na soubory, na které se můžete podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `cs2-demos`, druh [`replay`](sources-and-rules.md); běží pořád (nečeká, až začne hra) a hledá nová data každých 5 s.*

## Co se zaznamenává {#what-is-recorded}

- pozice každého hráče, směr pohledu, zdraví a peníze (každý 8. tick)
- zabití, smrti, poškození, granáty, položení a odminování bomby tam, kde se staly
- kola, skóre, ekonomika; řádek přihlášeného hráče v tabulce skóre jako statistiky

## Odkud to pochází {#where-it-comes-from}

dema, která ukládá CS2: &lt;CS2>/game/csgo/replays/\*.dem (stažená z historie zápasů) a &lt;CS2>/game/csgo/\*.dem (nahraná)

## Jak to zapnout {#how-to-switch-it-on}

stáhněte dema zápasu v CS2 (Watch > Your Matches), nebo ho nahrajte konzolovým příkazem `record`

Nastavení z proměnných prostředí:

- `HEAT3D_CS2`: složka 3DHeat CS2, když není vedle Watcheru nebo nainstalovaná

## Jak to funguje {#how-it-works}

Replaye a dema: to, co hra uloží o zápase, převedené až po jeho skončení.

Replay obsahuje všechno, co živé rozhraní v online hrách zadržuje – pozici každého hráče, každé zabití na místě, kde se stalo – a je to soubor, který hra zapisuje pro své hráče, takže čtení se hry vůbec nedotkne. Watcher sleduje složky, do kterých hry replaye ukládají, počká, až nový soubor přestane růst (jinak by ho hra ještě zapisovala), a převádí ho ve vlákně na pozadí, takže dlouhý převod nikdy nezdrží zbytek Watcheru.

Když se složka objeví poprvé, replaye, které už v ní jsou, se jen zaznamenají a nepřevádějí: hráč s lety nahraných dem by jinak Watcher zaměstnal na celý den. Příkaz `python -m heat3d_watch replays <adapter> [folder]` převede ty stávající na vyžádání.

#### Counter-Strike 2 {#counter-strike-2}

CS2 ukládá dema, která hráč stáhne z historie zápasů (karta Watch), do `<CS2>/game/csgo/replays/` a ta nahraná příkazem konzole `record` do `<CS2>/game/csgo/`. Každé se převádí vlastním převodníkem tohoto repozitáře pro CS2 (3DHeat CS2, github.com/Holdi601/3DHeat-CS2: pozice, směr pohledu, zdraví a peníze každého hráče každý osmý tick; zabití, smrti, poškození, granáty, položení a odminování bomby tam, kde se staly; kola, skóre, ekonomika) do složky relace jako tabulka `<map>/<match>.parquet` a souhrn `<match>.match.json`, které čtou karty prohlížeče Teplotní mapa a Zápas. Tabulka skóre zápasu se stane statistikami relace: pro hráče, jehož účet Steamu je přihlášen na tomto počítači (ze souboru Steamu `loginusers.vdf`), pod jeho prostými názvy – zabití, smrti, asistence, ADR, KAST, procento headshotů, první zabití, clutche – a skóre a kola.

Stejný modul slouží také: [Dota 2 (replaye)](game-dota-replays.md), [osu! (replaye)](game-osu-replays.md), [Squad (replaye)](game-squad-demos.md), [War Thunder (replaye)](game-warthunder-replays.md), [World of Tanks (replaye)](game-wot-replays.md), [World of Warships (replaye)](game-wows-replays.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `z` |
| Jednotky | palce (jednotky Source) |
| Zrcadleno pro prohlížeč | `y` |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto hodnoty se zapisují do `meta.json` každé relace (`axes`) a, má-li relace pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat řádky sám otáčí a měří – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hra po síti (`multiplayer`): **ano**. `games --markdown` to ukazuje jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `replay`: čte jen to, co hra nebo platforma vydává (replaye a dema, která hra uloží), takže zaznamenává i v online hře, stejně jako offline; příznak rozhoduje jen o tom, zda smí být paměť vůbec čtena.
- Paměť: tímto adaptérem **nikdy** nečtena. Paměť čtou jen adaptéry `memory` a nikdy u hry označené jako hraná po síti – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (`stats` každé relace v `meta.json` a tabulka `stats` v `watcher.sqlite`):

`map`, `rounds`, `score.{team}`, `won`

Klíč ve složených závorkách se doplňuje za běhu (`score.{team}` je jeden klíč na tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedeny.

## Úplnost {#completeness}

Převodník, který tento adaptér spouští, dodržuje [pravidlo převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co replay obsahuje, se přečte nebo uchová, nikdy se nezahodí – přečte se do tabulky a dokumentu zápasu, všechno ostatní se uchová celé v doprovodných souborech vedle nich a počítá se v `selfCheck.completeness` dokumentu zápasu. Vlastní dokumentace převodníku vypisuje, co čte, co uchovává v surové podobě a co nedokáže přečíst.

## Ověřeno {#verified}

převodník je ověřen na skutečných turnajových demech; sledování složky a statistiky testy

## Zdroj {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte ho znovu, místo úprav této stránky. -->
