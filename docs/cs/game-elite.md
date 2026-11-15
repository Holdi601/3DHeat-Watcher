---
title: "Elite Dangerous (logovací soubory)"
nav_order: 18
lang: "cs"
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (logovací soubory) {#elite-dangerous-log-files}

Když hrajete Elite Dangerous, Watcher čte soubory, které hra zapisuje, a ukládá, co se stalo, abyste se na to mohli později podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `elite`, druh [`log`](sources-and-rules.md); běží, když je spuštěný `EliteDangerous64.exe`, a hledá nová data každých 0,25 s.*

## Co se zaznamenává {#what-is-recorded}

- každá událost deníku pod svým názvem v deníku, s jejími prostými poli
- poloha v galaxii (StarPos, světelné roky) při skocích, lokacích, respawnech, smrtích, dokování a přistání
- respawn při LoadGame/Resurrect, smrt při Died, dokování a odpojení, dotyk země a vzlet, skok, session_end
- trasa na povrchu planety z Status.json: zeměpisná šířka, délka, výška, kurz a metry v tečné rovině na každém tělese (relace = název tělesa), s dalšími prostými poli Status.json (Flags, Flags2, GuiFocus, LegalState, ...)
- každý řádek deníku a každý pomocný soubor celý v heat.raw.parquet
- skoky, uražená vzdálenost ve skocích, smrti, zabití, získané kredity, splněné mise, prozkoumaná tělesa, navštívené systémy, dokování, přistání

## Odkud to pochází {#where-it-comes-from}

Herní deník %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (nejnovější soubor, sledovaný při zápisu), Status.json a další pomocné soubory \*.json (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) ve stejné složce

## Jak to zapnout {#how-to-switch-it-on}

Nic se nemusí zapínat: Watcher čte zdroj tak, jak ho hra nebo platforma poskytuje.

## Jak to funguje {#how-it-works}

Elite Dangerous: herní deník a Status.json, které hra zapisuje za běhu.

Kde: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<part>.log` – jeden JSON objekt na řádek, jeden soubor na každé spuštění (dlouhá relace pokračuje v části .02, .03 ...). Každý řádek
  má `timestamp` (UTC, ISO 8601) a `event`. Pozice v galaxii jsou
  `StarPos` [x, y, z] systému, ve světelných letech od Sluncové soustavy, u událostí `FSDJump`,
  `Location` a `CarrierJump`. Galaktický rámec Elite má osu y nahoru (směrem ke galaktickému severu),
  z směrem ke galaktickému jádru a x směrem ke galaktické délce 270 – je to levoruký
  rámec, takže prohlížeč osu z zrcadlí, aby se kreslil správným směrem.
* `Status.json` – celý se přepíše pokaždé, když se změní stav lodi: `Flags`,
  a u planety `Latitude`, `Longitude` (stupně), `Altitude` (metry),
  `Heading`, `BodyName` a `PlanetRadius` (metry).
* Ostatní pomocné soubory, každý se celý přepíše, když se zapíše odpovídající událost deníku: `Market.json`, `Outfitting.json`, `Shipyard.json`,
  `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`,
  `Backpack.json`, `FCMaterials.json`. Každý `*.json` ze složky, který hra v této
  relaci zapíše, se pokaždé, když se změní, uloží celý (pravidlo převaděče 3DHeat:
  co zdroj obsahuje, se přečte nebo uloží), pod svým názvem souboru.

Každý řádek deníku se v surové příloze relace uloží celý pod svou `event`, každý pomocný soubor pod svým názvem; řádek, který není JSON, pod `unparsed`.

Pozice na povrchu se ukládají do místní tečné roviny pro každé těleso, v metrech: první určení polohy na tělese je jeho počátek, x na východ, z na sever, y nahoru (výška), stejná orientace jako galaktický rámec, a řádky nesou název tělesa jako svou `session`, takže let nebo chůze po planetě se vykreslí jako vlastní trasa. Galaktické řádky mají relaci „galaxy“. Obě měřítka jsou v jedné tabulce; relaci vyberete v prohlížeči.

Formát: příručka Frontier „Elite Dangerous Player Journal“ (zveřejněná s každou aktualizací na oficiálních fórech, <https://forums.frontier.co.uk/> – „Journal Manual“, v4.x), události a pole podle ní; příznaky Status.json podle kapitoly „Status File“ téže příručky.

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `y` |
| Jednotky | světelné roky (galaktické řádky, relace „galaxy“); metry na východ/nahoru/na sever od prvního určení polohy na tělese (řádky povrchu, relace = název tělesa) |
| Zrcadleno pro prohlížeč | `z` |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto údaje se zapíšou do `meta.json` každé relace (`axes`) a, pokud má relace pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítko řádků nastavuje sám – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukazuje jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `log`: čte jen to, co hra nebo platforma vydává (soubory, které hra zapisuje za běhu), takže zaznamenává i v online hře, nejen offline; příznak rozhoduje jen o tom, zda se paměť smí vůbec číst.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry typu `memory` a nikdy u hry označené jako hraná online – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (u každé relace `stats` v `meta.json` a v tabulce `stats` souboru `watcher.sqlite`):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v části „Co se zaznamenává“ jsou pojmenovány.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převaděče](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, které adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky) a `selfCheck.completeness` v `meta.json` počítá každý `type` – `lost` je 0.

**Načteno**

- každý řádek deníku jako řádek pod svou `event`, s prostými poli (místní text, pokud ho hra dává; texty delší než 300 znaků se v řádku zkrátí)
- galaktické řádky (StarPos) u FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown; řádky povrchu ze Status.json a z Touchdown/Liftoff
- prosté pole Status.json (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) na řádcích povrchu
- statistiky: skoky, vzdálenost, smrti, zabití, získané kredity, mise, prozkoumaná tělesa, navštívené systémy, dokování, přistání

**Uchováno surové**

- každý řádek deníku celý, `type` = jeho `event` (FSDJump, Scan, Music, ReceiveText, ...), `used` true: seznamy a objekty, které řádky vynechávají (StarPos, Factions, Rewards, Killers, Materials, Modules, ...), jsou jen tady
- řádek deníku, který není JSON, `type` `unparsed`
- každý pomocný soubor celý pokaždé, když ho hra přepíše, `type` = jeho název souboru: `Status.json` (`used`, když vytvořil řádek povrchu), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`, a jakýkoli jiný `*.json`, který tam hra zapíše

**Nedostupné**

- pozice mezi skoky (uvnitř systému, v supercruise nebo v běžném vesmíru): hra zapisuje jen StarPos systému a u planety zeměpisnou šířku, délku a výšku
- pozice jiných lodí a hráčů: deník je účet velitele, ne celé hry
- rychlost, plyn a jiná letová telemetrie: hra ji nezapisuje
- deníky a pomocné soubory dřívějších relací: uloží se, když se hrálo (sledování začíná na konci souboru staršího než tato relace hry)
- webové rozhraní společnosti Frontier (cAPI): vyžaduje přihlášení hráče k Frontieru; není to soubor, který hra zapisuje

**Velikost**: asi 1–5 MB surového textu za hodinu: deník 0,2–2 MB, Status.json (pod 1 KB, přepisuje se až každou sekundu) 1–2 MB, sada market/outfitting/shipyard 20–150 KB na každou navštívenou stanici; zstd v heat.raw.parquet z toho udělá zhruba desetinu

## Ověřeno {#verified}

parser přehrán nad skutečnými soubory deníku z lokální instalace (počty událostí sedí se statistikami); opravy povrchu ze Status.json testovány jen na syntetických snímcích

## Zdroj {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
