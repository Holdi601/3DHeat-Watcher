---
title: "Squad (replaye)"
nav_order: 41
lang: "cs"
source: game-squad-demos.md
source_hash: "82c24e6df01c"
nav_exclude: true
search_exclude: true
---
# Squad (replaye) {#squad-replays}

Po zápase Squad Watcher promění replay, který hra uložila, na soubory, na které se můžete podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `squad-demos`, druh [`replay`](sources-and-rules.md); běží pořád (nečeká, až začne hra) a hledá nová data každých 5 s.*

## Co se zaznamenává {#what-is-recorded}

- pozice každého hráče, úhel natočení těla a rychlost pokaždé, když je server replikuje (až 8krát za sekundu), pěšky i v pozemních vozidlech
- jméno, tým, frakce a squad každého hráče, s průběhem změn týmu
- ne: pohyb vrtulníků, zabití a rozmístitelné předměty – viz README čtečky

## Odkud to pochází {#where-it-comes-from}

dema serverů, která Squad nahrává administrátorským příkazem AdminDemoRec: &lt;server>/SquadGame/Saved/Demos/\*.replay, čte externí čtečka `heat3d-squad-demo` (exporters/ext/squad-demo)

## Jak to zapnout {#how-to-switch-it-on}

nahrávejte na serveru: dejte administrátorovi oprávnění `demos` v Admins.cfg, pak v konzoli hry spusťte AdminDemoRec &lt;name> a AdminDemoStop; dema zkopírujte sem a nainstalujte čtečku: pip install -e &lt;3DHeat>/exporters/ext/squad-demo

Nastavení z proměnných prostředí:

- `HEAT3D_SQUAD_DEMO`: složka převodníku (klon nebo rozbalená verze), když není nainstalován nebo vedle Watcheru

## Jak to funguje {#how-it-works}

Replaye a dema: to, co hra uloží o zápase, převedené až po jeho skončení.

Replay obsahuje všechno, co živé rozhraní v online hrách zadržuje – pozici každého hráče, každé zabití na místě, kde se stalo – a je to soubor, který hra zapisuje pro své hráče, takže čtení se hry vůbec nedotkne. Watcher sleduje složky, do kterých hry replaye ukládají, počká, až nový soubor přestane růst (jinak by ho hra ještě zapisovala), a převádí ho ve vlákně na pozadí, takže dlouhý převod nikdy nezdrží zbytek Watcheru.

Když se složka objeví poprvé, replaye, které už v ní jsou, se jen zaznamenají a nepřevádějí: hráč s lety nahraných dem by jinak Watcher zaměstnal na celý den. Příkaz `python -m heat3d_watch replays <adapter> [folder]` převede ty stávající na vyžádání.

#### Squad {#squad}

Dedikované servery Squadu nahrají demo zápasu, když administrátor s oprávněním `demos` spustí AdminDemoRec &lt;name> (a AdminDemoStop), do `<server>/SquadGame/Saved/Demos/<name>.replay` – replay síťového enginu Unreal Engine, který obsahuje, co server replikoval, včetně pohybu každého hráče. Watcher je sám nečte: čte je externí čtečka (3DHeat Squad demo reader, `exporters/ext/squad-demo`, příkaz `heat3d-squad-demo`), samostatný projekt. Spouští se nad každým novým demem ve složkách, do kterých zapisuje lokální server, nebo ve složce, kterou nastavení přidá pro dema zkopírovaná z pronajatého serveru, a výsledek jde do složky relace jako `<map>/<match>.parquet` a `<match>.match.json`. Vrstva, mapa, počet hráčů a délka zápasu se stanou statistikami relace.

Stejný modul slouží také: [Counter-Strike 2 (replaye)](game-cs2-demos.md), [Dota 2 (replaye)](game-dota-replays.md), [osu! (replaye)](game-osu-replays.md), [War Thunder (replaye)](game-warthunder-replays.md), [World of Tanks (replaye)](game-wot-replays.md), [World of Warships (replaye)](game-wows-replays.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `z` |
| Jednotky | jednotky Unreal (centimetry) |
| Zrcadleno pro prohlížeč | žádné |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto hodnoty se zapisují do `meta.json` každé relace (`axes`) a, má-li relace pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat řádky sám otáčí a měří – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hra po síti (`multiplayer`): **ano**. `games --markdown` to ukazuje jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `replay`: čte jen to, co hra nebo platforma vydává (replaye a dema, která hra uloží), takže zaznamenává i v online hře, stejně jako offline; příznak rozhoduje jen o tom, zda smí být paměť vůbec čtena.
- Paměť: tímto adaptérem **nikdy** nečtena. Paměť čtou jen adaptéry `memory` a nikdy u hry označené jako hraná po síti – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (`stats` každé relace v `meta.json` a tabulka `stats` v `watcher.sqlite`):

`layer`, `map`, `match_seconds`, `players`

Klíč ve složených závorkách se doplňuje za běhu (`score.{team}` je jeden klíč na tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedeny.

## Úplnost {#completeness}

Převodník, který tento adaptér spouští, dodržuje [pravidlo převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co replay obsahuje, se přečte nebo uchová, nikdy se nezahodí – přečte se do tabulky a dokumentu zápasu, všechno ostatní se uchová celé v doprovodných souborech vedle nich a počítá se v `selfCheck.completeness` dokumentu zápasu. Vlastní dokumentace převodníku vypisuje, co čte, co uchovává v surové podobě a co nedokáže přečíst.

## Ověřeno {#verified}

čtečka je ověřena na veřejných serverových demech (pohyb odpovídá rychlosti, kterou nese; tým každého řádku odpovídá frakci jeho vojáka) a testy na sestavených demech; tento hák je ověřen testy s pomocným příkazem

## Zdroj {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte ho znovu, místo úprav této stránky. -->
