---
title: "VALORANT (replaye)"
nav_order: 45
lang: "cs"
source: game-valorant-replays.md
source_hash: "10a648aabdf1"
nav_exclude: true
search_exclude: true
---
# VALORANT (replaye) {#valorant-replays}

Po zápase VALORANT Watcher promění replay, který hra uložila, na soubory, na které se můžete podívat jako na statistiky a časovou osu.

*Technické podrobnosti: adaptér `valorant-replays`, druh [`replay`](sources-and-rules.md); běží pořád (nečeká, až se hra spustí) a hledá nová data každých 5 s.*

## Co se zaznamenává {#what-is-recorded}

- mapa, id zápasu a vybraní agenti; informační blok replaye (délka, verze, název, čas nahrávání, příznaky komprese a šifrování)
- časová osa událostí serveru: zabití (zabíječ a oběť jako id v síti), začátky kol, položené spiky, odminované a explodující spiky, použité ultimáty, výměny stran – každá s id a metadaty
- každý chunk souboru celý v heat.raw.parquet; nedekódováno: pozice, jména nebo skóre – ty jsou v zamlženém proudu

## Odkud to pochází {#where-it-comes-from}

replaye, které ukládá VALORANT: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (jen části, které nejsou zamlžené)

## Jak to zapnout {#how-to-switch-it-on}

uložte replay ve VALORANTu (kariéra > zápas > stáhnout replay)

## Jak to funguje {#how-it-works}

League of Legends a Valorant replaye: co z nich lze přečíst tak, jak jsou.

Obě hry ukládají replaye na disk hráče a obě chrání to, co je uvnitř:
data průběhu hry okamžik po okamžiku jsou zamlžená, a to pokaždé jinak při každé záplatě,
aby je nešlo použít k podvádění. Obejít to znamená rozebrat herní kód firmy,
což zakazují podmínky Riotu (Podmínky služby 3.1 a 7.1)
– proto se to tu nedělá. Co každý soubor nese otevřeně, se přečte, a zbytek se
uloží tak, jak je: každá část souboru celá v `heat.raw.parquet` relace (pravidlo
převaděče 3DHeat, docs/converters.md v repozitáři prohlížeče), počítaná v
`selfCheck.completeness` v meta.json.

#### Valorant (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, lokální replay Unreal Engine
(rozložení podle vrfkit, Apache-2.0, a ValorantReplayParser, MIT). Otevřeně:
informační blok replaye (délka, síťová verze, changelist, jeho název, kdy byl
nahrán, zda je komprimovaný nebo šifrovaný), mapa, id zápasu a vybraní agenti
(v hlavičce) a časová osa událostí serveru – zabití (zabíječ a oběť jako síťová
id, ne jména), začátky kol, položené spiky, odminované a explodující spiky, použité
ultimáty, výměny stran – každá s časem, id a metadaty. Pozice, jména, skóre a
všechno ostatní jsou v zamlženém proudu (chunky s daty replaye a kontrolními body),
který se uloží celý a nečte.

Stejný modul slouží také: [League of Legends (replaye)](game-lol-replays.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ne |
| Osa nahoru | `z` |
| Jednotky | světové jednotky VALORANTu |
| Zrcadleno pro prohlížeč | žádné |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto údaje se zapíšou do `meta.json` každé relace (`axes`) a, pokud má relace pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítko řádků nastavuje sám – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukazuje jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `replay`: čte jen to, co hra nebo platforma vydává (replaye a dema, která hra uloží), takže zaznamenává i v online hře, nejen offline; příznak rozhoduje jen o tom, zda se paměť smí vůbec číst.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry typu `memory` a nikdy u hry označené jako hraná online – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (u každé relace `stats` v `meta.json` a v tabulce `stats` souboru `watcher.sqlite`):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v části „Co se zaznamenává“ jsou pojmenovány.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převaděče](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, které adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky) a `selfCheck.completeness` v `meta.json` počítá každý `type` – `lost` je 0.

**Načteno**

- informační blok, každé pole (meta.json `vrf`): verze souboru, vlastní verze, délka, síťová verze, changelist, název, příznak živého zápasu, čas nahrání, příznaky komprimace a šifrování, klíč jak je uložen
- chunk hlavičky: mapa, id zápasu a vybraní agenti (poznáni podle jejich tvaru)
- každý chunk událostí: id, skupina, metadata, čas začátku a konce, a z jeho dat název události, její čas v sekundách a čísla před ní (síťová id zabíječe a oběti) – každý jako řádek

**Uchováno surové**

- každý chunk celý, v pořadí v souboru (`offset`), takže části jsou tím souborem: `info`, `header`, `event <group>`, `replay_data`, `checkpoint`, `chunk <n>` pro typ, který rozložení nepojmenovává, `trailing` pro bajty za posledním úplným chunkem

**Nedostupné**

- pozice, jména, skóre, schopnosti, každý rámec hry: chunky s daty replaye a kontrolními body jsou zamlžené; číst je znamená rozebrat klienta, což zakazují podmínky Riotu. Uloženo celé, nečteno
- obsah šifrovaného replaye: projde se a uloží celý, uvnitř se nic nečte

**Velikost**: surová příloha má zhruba velikost samotného replaye: zamlžený proud se nekomprimuje

## Ověřeno {#verified}

sestaveno podle kontejnerového rozložení dokumentovaného v vrfkit (Apache-2.0); netestováno na skutečném replayi, žádný nebyl k dispozici – před čtením se kontroluje a nesouhlasící části se přeskočí

## Zdroj {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
