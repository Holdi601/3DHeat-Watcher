---
title: "League of Legends (replaye)"
nav_order: 30
lang: "cs"
source: game-lol-replays.md
source_hash: "216b88922360"
nav_exclude: true
search_exclude: true
---
# League of Legends (replaye) {#league-of-legends-replays}

Po zápase League of Legends Watcher promění replay, který klient uložil, na soubory, na které se můžete podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `lol-replays`, druh [`replay`](sources-and-rules.md); běží pořád (nečeká, až se hra spustí) a hledá nová data každých 5 s.*

## Co se zaznamenává {#what-is-recorded}

- šampion, role, tým, zabití, smrti, asistence, zlato, poškození šampionů a výsledek každého hráče a každé další číslo z boxu statistik na konci hry
- váš vlastní řádek jako statistiky a vaše řádky označené jako vaše (meta.json `player`), s vaším Riot ID v nastavení
- s vlastním klíčem Riot API: pozice každého hráče každou minutu se statistikami té minuty a každá událost časové osy (zabití tam, kde se stala, budovy, monstra, wardy, předměty, schopnosti), v čase stěnových hodin, který dá časová osa
- každá část souboru replaye celá v heat.raw.parquet; nedekódováno: průběh hry okamžik po okamžiku, který je zašifrovaný a zamlžený proti podvádění

## Odkud to pochází {#where-it-comes-from}

replaye, které klient League ukládá: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (jen prostá metadata z konce hry); s vlastním klíčem Riot API oficiální časová osa zápasu z Match-V5 API společnosti Riot

## Jak to zapnout {#how-to-switch-it-on}

uložte replay v klientu League (historie zápasů > stáhnout); pro pozice nastavte riot_api_key a riot_platform příkazem `config --set`

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

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Obě verze kontejneru nesou
box statistik konce hry jako prostý JSON (`statsJson`): pro každého z deseti hráčů
šampiona, zabití, smrti, asistence, zlato, poškození šampionům, předměty, tým, roli,
výhru, jeho Riot ID a každé další číslo, které hra sčítá (přes sto na hráče); všechna
se stanou řádkem `player_result` hráče. ROFL1 (záplata 14.9 a dřívější) ho má za
pevnou hlavičkou (`RIOT\0\0`, 256bajtový podpis, pak délky); ROFL2 (14.11 a novější,
`RIOT\2\0`) na konci souboru, jeho délka v posledních čtyřech bajtech (uvedeno
inženýrem Riotu, ReplayBook issue 299). Hlavička datové části ROFL1 (id hry,
délka, počty chunků a keyframů, délka klíče chunku) a její tabulka chunků (id,
typ, délka, další chunk, posun) jsou otevřeně a přečtou se; samotné chunky jsou
zašifrované a uloží se celé, nepřečtené. Rozložení z roflxd.cs (MIT).

Pozice nepocházejí ze souboru. S vlastním vývojářským klíčem Riotu hráče
(`riot_api_key` v nastavení; osobní klíč je určen přesně pro „zobrazování (vlastních)
statistik hráče“) se oficiální časová osa zápasu stahuje z Match-V5 API společnosti Riot:
pozice každého hráče jednou za minutu se vším, co o něm rámec té minuty říká (zlato,
zkušenosti, úroveň, minioni, statistiky šampiona a poškození), a každá událost časové osy –
zabití, budovy, elitní monstra, wardy, předměty, schopnosti, úrovně – jako řádek,
tam, kde se stala, pokud má místo. Bez klíče se nic nestahuje a nic se neodesílá.

Stejný modul slouží také: [VALORANT (replaye)](game-valorant-replays.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `y` |
| Jednotky | jednotky mapy Summoner's Rift (asi 15000 napříč) |
| Zrcadleno pro prohlížeč | žádné |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto údaje se zapíšou do `meta.json` každé relace (`axes`) a, pokud má relace pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítko řádků nastavuje sám – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukazuje jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `replay`: čte jen to, co hra nebo platforma vydává (replaye a dema, která hra uloží), takže zaznamenává i v online hře, nejen offline; příznak rozhoduje jen o tom, zda se paměť smí vůbec číst.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry typu `memory` a nikdy u hry označené jako hraná online – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (u každé relace `stats` v `meta.json` a v tabulce `stats` souboru `watcher.sqlite`):

`champion`, `game_seconds`, `won`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v části „Co se zaznamenává“ jsou pojmenovány.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převaděče](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, které adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky) a `selfCheck.completeness` v `meta.json` počítá každý `type` – `lost` je 0.

**Načteno**

- JSON metadat: délka hry, verze, id posledního chunku a keyframu, a `statsJson` – každé pole boxu statistik každého hráče na jeho řádku `player_result` (čísla zadaná jako text se čtou jako čísla)
- ROFL1: blok délek, hlavička datové části (id hry, délka hry, počty keyframů a chunků, id chunků startu a začátku hry, interval keyframů, klíč chunku jak je uložen) a tabulka chunků (id, typ, délka, další chunk, posun) – v meta.json `rofl` a v `text` surových řádků
- ROFL2: řetězec verze
- časová osa Match-V5 (jen s vlastním klíčem API): každý rámec účastníka na řádku `position` (nebo `participant_frame` bez místa) se všemi jeho poli zploštělými (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...); každá událost jako řádek pojmenovaný podle svého typu, umístěný tam, kde má `position`; CHAMPION_KILL jako zabití a smrt

**Uchováno surové**

- každá část .rofl celá, v pořadí v souboru (`offset`), takže části jsou tím souborem: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); jakýkoli úsek, který žádná část nepokrývá, jako `unknown`
- časová osa celá: `timeline <type>` pro každou událost, `timeline participantFrame` pro rámec každého hráče (`participant` je jeho id), `timeline` pro zbytek

**Nedostupné**

- samotná hra (pozice, schopnosti, každá jednotka, okamžik po okamžiku): chunky ROFL1 a tělo ROFL2 jsou zašifrované a pakety uvnitř zamlžené s každou záplatou; obejít to znamená rozebrat klienta, což zakazují podmínky Riotu (3.1, 7.1). Uloženo celé, nečteno
- pozice bez vašeho vlastního klíče Riot API: soubor je v otevřené podobě nemá

**Velikost**: surová příloha má zhruba velikost samotného replaye: zašifrované chunky se nekomprimují

## Ověřeno {#verified}

čtečka metadat testována na souborech sestavených podle rozložení z roflxd.cs (MIT); časová osa podle dokumentovaného JSON z Match-V5; žádný skutečný replay nebyl k dispozici k ověření

## Zdroj {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
