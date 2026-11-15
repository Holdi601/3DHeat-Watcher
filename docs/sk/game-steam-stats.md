---
title: "Štatistiky Steamu (platforma)"
nav_order: 43
lang: "sk"
source: game-steam-stats.md
source_hash: "24fa6512bd6d"
nav_exclude: true
search_exclude: true
---
# Štatistiky Steamu (platforma) {#steam-statistics-platform}

Watcher ukladá to, čo Štatistiky Steamu uchovávajú o vašich hrách, aby ste si históriu mohli neskôr pozrieť ako štatistiky a časovú os.

*Technické podrobnosti: adaptér `steam-stats`, druh [`platform`](sources-and-rules.md); beží stále (nečaká, kým sa spustí hra) a hľadá nové dáta každých 30 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- každá štatistika, ktorú hra uchováva v Steame (jej vlastné mená a hodnoty), pre každú hru, pri každej zmene
- odomknutia úspechov s zobrazovaným názvom, popisom a časom odomknutia
- zmeny štatistík so starou hodnotou, novou hodnotou a rozdielom
- čas hrania (minúty, posledné dva týždne) a čas poslednej hry

## Odkiaľ to pochádza {#where-it-comes-from}

lokálna vyrovnávacia pamäť štatistík Steamu %STEAM%\appcache\stats\UserGameStats_&lt;account>_&lt;appid>.bin so súborom UserGameStatsSchema_&lt;appid>.bin; čas hrania z %STEAM%\userdata\\&lt;account>\config\localconfig.vdf (%STEAM% z HKCU\Software\Valve\Steam SteamPath)

## Ako to zapnúť {#how-to-switch-it-on}

Nič netreba zapínať: watcher číta zdroj tak, ako ho hra alebo platforma poskytuje.

## Ako to funguje {#how-it-works}

To, čo si launcher a grafický ovládač uchovávajú o hraní: štatistiky Steamu,
úspechy, čas hrania a časové osi a highlighty a klipy NVIDIA.

Žiaden z týchto zdrojov nepotrebuje, aby hra spolupracovala alebo bežala, takže
tri tu uvedené adaptéry sú vždy zapnuté a každých niekoľko sekúnd čítajú pár súborov.

#### Štatistiky Steamu (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<account>_<appid>.bin`, ktorý klient Steamu
prepíše zakaždým, keď hra uloží svoje štatistiky, dekódovaný so schémou
`UserGameStatsSchema_<appid>.bin` vedľa neho (binárny KeyValues, pozrite `_steam.py`).
Štatistiky sú celé alebo desatinné čísla podľa toho, čo hra definuje; úspechy sú
bity s časom odomknutia v sekundách Unixu. Čas hrania je v
`<Steam>\userdata\<account>\config\localconfig.vdf` pod apps/&lt;appid>:
Playtime a Playtime2wks v minútach, LastPlayed v sekundách Unixu.
Steam sa nájde cez HKCU\Software\Valve\Steam SteamPath.
Rozhranie štatistík: <https://partner.steamgames.com/doc/features/achievements>

Ten istý modul slúži aj pre: [NVIDIA highlighty (platforma)](game-nvidia-highlights.md), [Časová os Steamu (platforma)](game-steam-timeline.md).

## Pozície a osi {#positions-and-axes}

| | |
|---|---|
| Pozície sa zaznamenávajú | nie |
| Os nahor | `y` |
| Jednotky | metre |
| Zrkadlené pre viewer | žiadne |
| Mierka jednotiek (`scale`: viewer násobí pozície touto hodnotou) | 1 |

Tieto hodnoty sa zapíšu do `meta.json` každej relácie (`axes`) a, ak relácia obsahuje pozície, do päty `heat.parquet`, takže viewer 3DHeat otáča a mierni riadky sám - pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hrané online (`multiplayer`): **nie**. `games --markdown` to zobrazí ako "jednohráčová".
- Druh `platform`: číta len to, čo hra alebo platforma vydáva (čo uchováva Steam alebo grafický ovládač), takže zaznamenáva aj online hru, aj hru offline; príznak rozhoduje len o tom, či sa pamäť smie čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry `memory` a nikdy pre hru označenú ako hranú online - pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

Kľúč v zložených zátvorkách sa dopĺňa pri behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z mien štatistík hry, v tomto zozname nie sú; "Čo sa zaznamenáva" vyššie ich uvádza.

## Úplnosť {#completeness}

Watcher dodržiava [pravidlo konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, čo zdroj obsahuje, sa číta alebo uchováva, nikdy sa nezahadzuje. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text`, a potom každé pole uchované podľa mena; `used` označuje, čo sa stalo aj riadkom), a `selfCheck.completeness` v `meta.json` počíta každý `type` - `lost` je 0.

**Prečítané**

- každá štatistika zo súboru štatistík podľa jej mena v rozhraní (int, float, avgrate), každý bit úspechu s časom odomknutia, pomenovaný a opísaný schémou
- zmeny oproti poslednému čítaniu (stará, nová, rozdiel), nové odomknutia; čas hrania, čas hrania za dva týždne a čas poslednej hry z localconfig.vdf

**Uchované surové**

- `UserGameStats`: bajty súboru štatistík celé, zakaždým, keď sa zapíše (`crc`, `PendingChanges`, bity úspechov, ktoré schéma už nedefinuje, a každý kľúč, ktorý dekodér preskočí, sú v ňom)
- `UserGameStatsSchema`: bajty súboru schémy vedľa neho, aby sa štatistiky dali dekódovať iba zo relácie (názvy každej štatistiky a úspechu vo všetkých jazykoch, ikony, príznaky)
- `localconfig_app`: celý blok hry z localconfig.vdf ako JSON (stav cloudovej synchronizácie, spúšťacie možnosti, odznaky a každý ďalší kľúč, ktorý Steam pre hru uchováva), keď sa zaznamenáva jej čas hrania
- súbor štatistík, ktorý dekodér nedokáže prečítať (prerušený uprostred zápisu alebo nové rozloženie): jeho bajty a schéma v relácii bez riadkov (`used` false; `unreadable` v meta.json)

**Nedostupné**

- zvyšok localconfig.vdf (priatelia, chat, nastavenia Steamu): nie je hry a je súkromný
- hodnoty štatistík medzi dvoma zápismi: Steam prepíše súbor, keď hra ukladá svoje štatistiky, zvyčajne pri zatvorení
- globálne percentá úspechov a štatistiky iných hráčov: sú na serveroch Steamu, nie tu

**Veľkosť**: niekoľko KB na každé zaznamenané sedenie, plus schéma (až niekoľko stoviek KB pre hru s mnohými úspechmi) - ďaleko pod 1 MB na hodinu hrania; zstd zmenší text schémy o polovicu alebo viac

## Overené {#verified}

otestované na skutočných súboroch štatistík a schémach z lokálnej inštalácie; detekcia zmien testovaná na súboroch vytvorených v binárnom formáte KeyValues

## Zdroj {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
