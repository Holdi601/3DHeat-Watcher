---
title: "War Thunder (replaye)"
nav_order: 46
lang: "cs"
source: game-warthunder-replays.md
source_hash: "81f03926431d"
nav_exclude: true
search_exclude: true
---
# War Thunder (replaye) {#war-thunder-replays}

Po zápase War Thunder Watcher promění replay, který hra uložila, na soubory, na které se můžete podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `warthunder-replays`, druh [`replay`](sources-and-rules.md); běží pořád (nečeká, až začne hra) a hledá nová data každých 5 s.*

## Co se zaznamenává {#what-is-recorded}

- pozice a postoj každého letadla zhruba 4krát za sekundu (kolikrát ho replay obsahuje)
- pozice pozemních jednotek z pozemní synchronizace replaye (v replayích z roku 2026; ne v těch z roku 2025)
- kdo byla každá jednotka (hráč, id vozidla, tým), tam, kde ji zmiňuje zabití nebo zásah; zabití, smrti a zásahy tam, kde se staly; chat; mapa
- zabití, smrti, skóre a dobytí autora replaye jako statistiky

## Odkud to pochází {#where-it-comes-from}

replaye, která ukládá War Thunder: &lt;War Thunder>/Replays/\*.wrpl (se zapnutým ukládáním replayů), převádí externí převodník `heat3d-wt-replay` (exporters/ext/warthunder-replay)

## Jak to zapnout {#how-to-switch-it-on}

zapněte ukládání replayů v nastavení War Thunder a nainstalujte převodník: pip install -e &lt;3DHeat>/exporters/ext/warthunder-replay

Nastavení z proměnných prostředí:

- `HEAT3D_WT_REPLAY`: složka převodníku (klon nebo rozbalená verze), když není nainstalován nebo vedle Watcheru

## Jak to funguje {#how-it-works}

Replaye a dema: to, co hra uloží o zápase, převedené až po jeho skončení.

Replay obsahuje všechno, co živé rozhraní v online hrách zadržuje – pozici každého hráče, každé zabití na místě, kde se stalo – a je to soubor, který hra zapisuje pro své hráče, takže čtení se hry vůbec nedotkne. Watcher sleduje složky, do kterých hry replaye ukládají, počká, až nový soubor přestane růst (jinak by ho hra ještě zapisovala), a převádí ho ve vlákně na pozadí, takže dlouhý převod nikdy nezdrží zbytek Watcheru.

Když se složka objeví poprvé, replaye, které už v ní jsou, se jen zaznamenají a nepřevádějí: hráč s lety nahraných dem by jinak Watcher zaměstnal na celý den. Příkaz `python -m heat3d_watch replays <adapter> [folder]` převede ty stávající na vyžádání.

#### War Thunder {#war-thunder}

War Thunder ukládá replay každé bitvy do `<War Thunder>/Replays/*.wrpl`, když je ukládání replayů v jeho nastavení zapnuté. Watcher je sám nečte: čte je externí převodník (3DHeat War Thunder replay converter, `exporters/ext/warthunder-replay`, příkaz `heat3d-wt-replay`), samostatný projekt. Když je příkaz na PATH, nebo je balíček nainstalován či vedle Watcheru, každý nový replay se jím převede do složky relace jako `<map>/<match>.parquet` a `<match>.match.json`; když není, Watcher jednou řekne, jak ho nainstalovat, a složku nechá být. Co převodník čte a co ne, je v jeho README. Řádek výsledků autora replaye – zabití, zabití pozemních cílů, smrti, asistence, skóre, dobytí – se stane statistikami relace.

Stejný modul slouží také: [Counter-Strike 2 (replaye)](game-cs2-demos.md), [Dota 2 (replaye)](game-dota-replays.md), [osu! (replaye)](game-osu-replays.md), [Squad (replaye)](game-squad-demos.md), [World of Tanks (replaye)](game-wot-replays.md), [World of Warships (replaye)](game-wows-replays.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `y` |
| Jednotky | metry (x na východ, y nahoru, z na sever) |
| Zrcadleno pro prohlížeč | `z` |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto hodnoty se zapisují do `meta.json` každé relace (`axes`) a, má-li relace pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat řádky sám otáčí a měří – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hra po síti (`multiplayer`): **ano**. `games --markdown` to ukazuje jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `replay`: čte jen to, co hra nebo platforma vydává (replaye a dema, která hra uloží), takže zaznamenává i v online hře, stejně jako offline; příznak rozhoduje jen o tom, zda smí být paměť vůbec čtena.
- Paměť: tímto adaptérem **nikdy** nečtena. Paměť čtou jen adaptéry `memory` a nikdy u hry označené jako hraná po síti – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (`stats` každé relace v `meta.json` a tabulka `stats` v `watcher.sqlite`):

`map`

Klíč ve složených závorkách se doplňuje za běhu (`score.{team}` je jeden klíč na tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedeny.

## Úplnost {#completeness}

Převodník, který tento adaptér spouští, dodržuje [pravidlo převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co replay obsahuje, se přečte nebo uchová, nikdy se nezahodí – přečte se do tabulky a dokumentu zápasu, všechno ostatní se uchová celé v doprovodných souborech vedle nich a počítá se v `selfCheck.completeness` dokumentu zápasu. Vlastní dokumentace převodníku vypisuje, co čte, co uchovává v surové podobě a co nedokáže přečíst.

## Ověřeno {#verified}

převodník je ověřen na veřejných replayích z několika verzí hry (zabití a jména souhlasí s výsledky) a testy na sestavených replayích; tento hák je ověřen testy s pomocným příkazem

## Zdroj {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte ho znovu, místo úprav této stránky. -->
