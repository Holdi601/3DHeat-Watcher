---
title: "World of Tanks (replaye)"
nav_order: 48
lang: "cs"
source: game-wot-replays.md
source_hash: "4cff18c29936"
nav_exclude: true
search_exclude: true
---
# World of Tanks (replaye) {#world-of-tanks-replays}

Po zápase World of Tanks Watcher promění replay, který hra uložila, na soubory, na které se můžete podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `wot-replays`, druh [`replay`](sources-and-rules.md); běží pořád (nečeká, až začne hra) a hledá nová data každých 5 s.*

## Co se zaznamenává {#what-is-recorded}

- pozice a směr každého vozidla zhruba 10krát za sekundu, dokud o něm nahrávací klient věděl: vlastní tým po celou dobu, nepřítel, dokud byl zpozorován
- hráč, tým a vozidlo (národ:tank) každého; smrti, tam kde oběť padla, a zabití, tam kde vrah stál, na zhruba sekundu přesně, podle výsledků
- mapa; zabití, poškození, přežití a výsledek nahrávajícího hráče jako statistiky

## Odkud to pochází {#where-it-comes-from}

replaye, která ukládá World of Tanks: &lt;World of Tanks>/replays/\*.wotreplay (se zapnutým nahráváním bitev), převádí externí převodník `heat3d-wot-replay` (exporters/ext/wot-replay)

## Jak to zapnout {#how-to-switch-it-on}

zapněte nahrávání bitev v nastavení World of Tanks (General > Record battles) a nainstalujte převodník: pip install -e &lt;3DHeat>/exporters/ext/wot-replay

Nastavení z proměnných prostředí:

- `HEAT3D_WOT_REPLAY`: složka převodníku (klon nebo rozbalená verze), když není nainstalován nebo vedle Watcheru

## Jak to funguje {#how-it-works}

Replaye a dema: to, co hra uloží o zápase, převedené až po jeho skončení.

Replay obsahuje všechno, co živé rozhraní v online hrách zadržuje – pozici každého hráče, každé zabití na místě, kde se stalo – a je to soubor, který hra zapisuje pro své hráče, takže čtení se hry vůbec nedotkne. Watcher sleduje složky, do kterých hry replaye ukládají, počká, až nový soubor přestane růst (jinak by ho hra ještě zapisovala), a převádí ho ve vlákně na pozadí, takže dlouhý převod nikdy nezdrží zbytek Watcheru.

Když se složka objeví poprvé, replaye, které už v ní jsou, se jen zaznamenají a nepřevádějí: hráč s lety nahraných dem by jinak Watcher zaměstnal na celý den. Příkaz `python -m heat3d_watch replays <adapter> [folder]` převede ty stávající na vyžádání.

#### World of Tanks a World of Warships {#world-of-tanks-and-world-of-warships}

Obě hry ukládají replay každé bitvy do `<game>/replays/`, když je nahrávání zapnuté (`*.wotreplay`, `*.wowsreplay`); instalace se hledají přes seznam Wargaming Game Center, `C:/Games/World_of_Tanks*` / `World_of_Warships*`, a Steam. Stejně jako u War Thunder Watcher soubory sám nečte: čte je externí převodník každé z nich (`exporters/ext/wot-replay`, příkaz `heat3d-wot-replay`; `exporters/ext/wows-replay`, příkaz `heat3d-wows-replay`), každý jako samostatný projekt. Když je nalezen na PATH, nainstalován, nebo vedle Watcheru, promění každý nový replay v `<map>/<match>.parquet` a `<match>.match.json` ve složce relace; když chybí, Watcher jednou řekne, jak ho nainstalovat. Řádek nahrávajícího hráče – vozidlo nebo loď, zabití, poškození (World of Tanks), zda přežil, a výsledek (World of Tanks) – se stane statistikami relace. Co každý převodník čte a co ne, je v jeho README.

Stejný modul slouží také: [Counter-Strike 2 (replaye)](game-cs2-demos.md), [Dota 2 (replaye)](game-dota-replays.md), [osu! (replaye)](game-osu-replays.md), [Squad (replaye)](game-squad-demos.md), [War Thunder (replaye)](game-warthunder-replays.md), [World of Warships (replaye)](game-wows-replays.md).

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

`map`, `survived`, `vehicle`, `won`

Klíč ve složených závorkách se doplňuje za běhu (`score.{team}` je jeden klíč na tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedeny.

## Úplnost {#completeness}

Převodník, který tento adaptér spouští, dodržuje [pravidlo převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co replay obsahuje, se přečte nebo uchová, nikdy se nezahodí – přečte se do tabulky a dokumentu zápasu, všechno ostatní se uchová celé v doprovodných souborech vedle nich a počítá se v `selfCheck.completeness` dokumentu zápasu. Vlastní dokumentace převodníku vypisuje, co čte, co uchovává v surové podobě a co nedokáže přečíst.

## Ověřeno {#verified}

převodník je ověřen na veřejných replayích z několika verzí hry a testy na sestavených replayích; tento hák je ověřen testy s pomocným příkazem

## Zdroj {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte ho znovu, místo úprav této stránky. -->
