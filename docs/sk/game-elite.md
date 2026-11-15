---
title: "Elite Dangerous (súbory záznamov)"
nav_order: 18
lang: "sk"
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (súbory záznamov) {#elite-dangerous-log-files}

Počas hry Elite Dangerous watcher číta súbory, ktoré hra zapisuje, a ukladá, čo sa stalo, aby ste to neskôr mohli pozrieť na mape v 3DHeat prehliadači.

*Technické údaje: adaptér `elite`, typ [`log`](sources-and-rules.md); beží, kým beží `EliteDangerous64.exe`, a hľadá nové dáta každých 0,25 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- každá udalosť denníka pod jej názvom z denníka, s jednoduchými poľami
- poloha v galaxii (StarPos, svetelné roky) pri skokoch, lokáciách, spawnoch, smrtiach, dokovaní, pristátí
- spawn pri LoadGame/Resurrect, smrť pri Died, dokovanie/odokovanie, dotyk/odlet, skok, session_end
- trasa na povrchu planéty zo Status.json: zemepisná šírka, dĺžka, výška, smer, a metre v tangenciálnej rovine pre každé teleso (relácia = názov telesa), s ostatnými jednoduchými poľami Status.json (Flags, Flags2, GuiFocus, LegalState, ...)
- každý riadok denníka a každý pomocný súbor celý v heat.raw.parquet
- skoky, prejdená vzdialenosť skokmi, smrti, zabitia, zarobené kredity, splnené misie, preskenované telesá, navštívené systémy, dokovania, pristátia

## Odkiaľ to berie {#where-it-comes-from}

Denník hráča %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (najnovší súbor, sleduje sa, ako sa zapisuje), Status.json a ostatné pomocné súbory \*.json (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) v tom istom priečinku

## Ako to zapnúť {#how-to-switch-it-on}

Nič netreba zapínať: watcher číta zdroj tak, ako ho hra alebo platforma poskytuje.

## Ako to funguje {#how-it-works}

Elite Dangerous: denník hráča a Status.json, ktoré hra zapisuje počas behu.

Kde: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<part>.log` - jeden JSON objekt na riadok, jeden súbor na každé spustenie (dlhá relácia pokračuje v časti .02, .03 ...). Každý riadok má `timestamp` (UTC, ISO 8601) a `event`. Polohy v galaxii sú `StarPos` [x, y, z] systému, v svetelných rokoch od Sólu, pri `FSDJump`, `Location` a `CarrierJump`. Galaktický rámec Elite má y smerom nahor (ku galaktickému severu), z smerom k galaktickému jadru a x smerom ku galaktickej dĺžke 270 - je to ľavotočivý rámec, takže prehliadač zrkadlí z, aby sa vykreslil správne.
* `Status.json` - prepísaný celý vždy, keď sa zmení stav lode: `Flags`, a pri planéte `Latitude`, `Longitude` (stupne), `Altitude` (metre), `Heading`, `BodyName` a `PlanetRadius` (metre).
* Ostatné pomocné súbory, každý prepísaný celý vždy, keď sa zapíše zodpovedajúca udalosť denníka: `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`. Každý `*.json` v priečinku, ktorý hra v tomto sedení zapíše, sa uchová celý vždy, keď sa zmení, pod svojím názvom súboru (pravidlo konvertorov 3DHeat: čo zdroj obsahuje, sa načíta alebo uchová).

Každý riadok denníka sa uchová celý v surovom sprievodnom súbore relácie pod svojou `event`, každý pomocný súbor pod svojím názvom; riadok, ktorý nie je JSON, pod `unparsed`.

Polohy na povrchu sa zapisujú do lokálnej tangenciálnej roviny pre každé teleso, v metroch: prvé zameranie na telese je jeho počiatok, x na východ, z na sever, y nahor (výška), rovnaká orientácia ako galaktický rámec; riadky nesú názov telesa ako `session`, takže let alebo chôdza po planéte sa kreslí ako vlastná trasa. Galaktické riadky majú reláciu „galaxy". Obe mierky sú v jednej tabuľke; reláciu vyberiete v prehliadači.

Formát: príručka „Elite Dangerous Player Journal" od Frontieru (zverejnená s každou aktualizáciou na oficiálnych fórach, <https://forums.frontier.co.uk/> - „Journal Manual", v4.x), udalosti a polia podľa tej príručky; príznaky Status.json podľa kapitoly „Status File" z tej istej príručky.

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | áno |
| Osa nahor | `y` |
| Jednotky | svetelné roky (riadky galaxie, relácia „galaxy"); metre na východ/nahor/na sever od prvého zamerania na telese (riadky povrchu, relácia = názov telesa) |
| Zrkadlenie pre prehliadač | `z` |
| Mierka jednotiek (`scale`: prehliadač ňou násobí polohy) | 1 |

Tieto hodnoty idú do `meta.json` každej relácie (`axes`) a, keď relácia obsahuje polohy, do päty `heat.parquet`, takže 3DHeat prehliadač ich otáča a škáluje sám - pozrite [Dáta](the-data.md).

## Multiplayer {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)".
- Druh `log`: číta len to, čo hra alebo platforma sprístupňuje (súbory, ktoré hra zapisuje počas behu), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie vôbec čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online - pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z jej vlastných názvov štatistík, v tomto zozname nie sú; čo sa zaznamenáva, uvádza vyššie časť „Čo sa zaznamenáva".

## Úplnosť {#completeness}

Watcher sa riadi pravidlom konvertorov 3DHeat ([pravidlo konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)): čo zdroj obsahuje, sa načíta alebo uchová, nikdy sa nezahodí. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia uchované podľa mena; `used` označuje, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` - `lost` je 0.

**Načítané**

- každý riadok denníka ako riadok pod svojou `event`, s jednoduchými poľami (lokalizovaný text, kde ho hra dáva; texty dlhšie ako 300 znakov sa v riadku skrátia)
- riadky galaxie (StarPos) pri FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown; riadky povrchu zo Status.json a z Touchdown/Liftoff
- jednoduché polia Status.json (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) na riadkoch povrchu
- štatistiky: skoky, vzdialenosť, smrti, zarobené kredity, misie, preskenované telesá, navštívené systémy, dokovania, pristátia

**Uchované surové**

- každý riadok denníka celý, `type` = jeho `event` (FSDJump, Scan, Music, ReceiveText, ...), `used` true: zoznamy a objekty, ktoré riadky nechávajú bokom (StarPos, Factions, Rewards, Killers, Materials, Modules, ...), sú len tu
- riadok denníka, ktorý nie je JSON, `type` `unparsed`
- každý pomocný súbor celý vždy, keď ho hra prepíše, `type` = jeho názov súboru: `Status.json` (`used`, keď vytvoril riadok povrchu), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json` a každý ďalší `*.json`, ktorý hra tam zapíše

**Nie je k dispozícii**

- poloha medzi skokmi (vo vnútri systému, v supercruise alebo v normálnom priestore): hra zapisuje len StarPos systému a pri planéte zemepisnú šírku, dĺžku a výšku
- polohy iných lodí a hráčov: denník je vlastný účet veliteľa
- rýchlosť, plyn a ďalšia telemetria letu: hra ich nezapisuje
- denníky a pomocné súbory predchádzajúcich sedení: uchované, keď sa hrali (sledovanie začína na konci súboru staršieho, ako je tento beh hry)
- webové API Frontieru (cAPI): vyžaduje prihlásenie hráča do Frontieru; nie je to súbor, ktorý hra zapisuje

**Veľkosť**: približne 1-5 MB surového textu za hodinu: denník 0,2-2 MB, Status.json (pod 1 KB, prepisovaný až každú sekundu) 1-2 MB, sada market/outfitting/shipyard 20-150 KB za každú navštívenú stanicu; zstd v heat.raw.parquet to zmenší zhruba na desatinu

## Overené {#verified}

parser pustený nad skutočnými súbormi denníka z lokálnej inštalácie (počty udalostí sedia so štatistikami); opravy povrchu zo Status.json overené len na syntetických snímkach

## Zdroj {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
