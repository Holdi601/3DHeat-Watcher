---
title: "Statistiky Steamu (platforma)"
nav_order: 43
lang: "cs"
source: game-steam-stats.md
source_hash: "24fa6512bd6d"
nav_exclude: true
search_exclude: true
---
# Statistiky Steamu (platforma) {#steam-statistics-platform}

Watcher ukládá, co statistiky Steamu evidují o vašich hrách, abyste se na svou historii mohli později podívat jako na statistiky a časovou osu.

*Technické podrobnosti: adaptér `steam-stats`, druh [`platform`](sources-and-rules.md); běží pořád (nečeká, až začne hra) a hledá nová data každých 30 s.*

## Co se zaznamenává {#what-is-recorded}

- každou statistiku, kterou hra uloží do Steamu (její vlastní názvy a hodnoty), pro každou hru, když se změní
- odemčení achievementů se zobrazovaným názvem, popisem a časem odemčení
- změny statistik se starou hodnotou, novou hodnotou a rozdílem
- čas hraní (minuty, poslední dva týdny) a čas posledního hraní

## Odkud to pochází {#where-it-comes-from}

Lokální mezipaměť statistik Steamu %STEAM%\appcache\stats\UserGameStats_&lt;account>_&lt;appid>.bin se souborem UserGameStatsSchema_&lt;appid>.bin; čas hraní z %STEAM%\userdata\\&lt;account>\config\localconfig.vdf (%STEAM% z HKCU\Software\Valve\Steam SteamPath)

## Jak to zapnout {#how-to-switch-it-on}

Nic není třeba zapínat: Watcher čte zdroj tak, jak ho hra nebo platforma poskytuje.

## Jak to funguje {#how-it-works}

Co launcher a grafický ovladač uchovávají o hraní: statistiky Steamu, achievementy, čas hraní a časové osy, a highlighty a klipy NVIDIE.

Žádný z těchto zdrojů nepotřebuje, aby hra spolupracovala nebo běžela, takže tři adaptéry zde jsou vždy zapnuté a každých několik sekund se dívají na pár souborů.

#### Statistiky Steamu (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<account>_<appid>.bin`, který klient Steamu přepisuje pokaždé, když hra uloží své statistiky, dekódovaný se schématem `UserGameStatsSchema_<appid>.bin` vedle něj (binární KeyValues, viz `_steam.py`). Statistiky jsou celá nebo desetinná čísla, jak je hra definuje; achievementy jsou bity s časem odemčení v sekundách Unixu. Čas hraní je v `<Steam>\userdata\<account>\config\localconfig.vdf` pod apps/&lt;appid>: Playtime a Playtime2wks v minutách, LastPlayed v sekundách Unixu. Steam se najde přes HKCU\Software\Valve\Steam SteamPath. Rozhraní pro statistiky: <https://partner.steamgames.com/doc/features/achievements>

Stejný modul slouží také: [NVIDIA highlights (platforma)](game-nvidia-highlights.md), [Časová osa Steamu (platforma)](game-steam-timeline.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ne |
| Osa nahoru | `y` |
| Jednotky | metry |
| Zrcadleno pro prohlížeč | žádné |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto hodnoty se zapisují do `meta.json` každé relace (`axes`) a, má-li relace pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat řádky sám otáčí a měří – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hra po síti (`multiplayer`): **ne**. `games --markdown` to ukazuje jako „single-player“.
- Druh `platform`: čte jen to, co hra nebo platforma poskytuje (co uchovává Steam nebo grafický ovladač), takže zaznamenává i v online hře, stejně jako offline; příznak rozhoduje jen o tom, zda smí být paměť vůbec čtena.
- Paměť: tímto adaptérem **nikdy** nečtena. Paměť čtou jen adaptéry `memory` a nikdy u hry označené jako hraná po síti – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (`stats` každé relace v `meta.json` a tabulka `stats` v `watcher.sqlite`):

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

Klíč ve složených závorkách se doplňuje za běhu (`score.{team}` je jeden klíč na tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedeny.

## Úplnost {#completeness}

Watcher dodržuje [pravidlo převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co zdroj obsahuje, se přečte nebo uchová, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, kterou adaptér přijme, uchová celá v `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uchovaná podle názvu; `used` označuje to, co se stalo také řádky), a `selfCheck.completeness` v `meta.json` počítá každý `type` – `lost` je 0.

**Načteno**

- každou statistiku ze souboru statistik podle jejího názvu v rozhraní API (int, float, avgrate), každý bit achievementu s časem odemčení, pojmenovaný a popsaný podle schématu
- změny oproti poslednímu čtení (stará hodnota, nová hodnota, rozdíl), nová odemčení; čas hraní, čas hraní za dva týdny a čas posledního hraní z localconfig.vdf

**Uchováno surové**

- `UserGameStats`: bajty souboru statistik celé, pokaždé, když se zaznamenají (`crc`, `PendingChanges`, bity achievementů, které schéma už nedefinuje, a každý klíč, který dekodér přeskočí, jsou v nich)
- `UserGameStatsSchema`: bajty souboru schématu vedle něj, aby šlo statistiky dekódovat z relace samotné (názvy všech statistik a achievementů ve všech jazycích, ikony, příznaky)
- `localconfig_app`: celý blok hry z localconfig.vdf jako JSON (stav cloudové synchronizace, spouštěcí parametry, odznaky a každý další klíč, který Steam u hry eviduje), když se zaznamenává její čas hraní
- soubor statistik, který dekodér nedokáže přečíst (přerušený uprostřed zápisu, nebo nové uspořádání): jeho bajty a schéma v relaci bez řádků (`used` false; `unreadable` v meta.json)

**Nedostupné**

- zbytek localconfig.vdf (přátelé, chat, nastavení Steamu): není to hry a je soukromý
- hodnoty statistik mezi dvěma zápisy: Steam soubor přepisuje, když hra uloží své statistiky, obvykle při zavření
- globální procenta achievementů a statistiky jiných hráčů: jsou na serverech Steamu, ne tady

**Velikost**: pár KB na zaznamenané relace, plus schéma (až několik set KB u hry s mnoha achievementy) – hluboko pod 1 MB za hodinu hraní; zstd zmenší text schématu na polovinu nebo víc

## Ověřeno {#verified}

testováno na skutečných souborech statistik a schémat z místní instalace; detekce změn testována na souborech vytvořených ve binárním formátu KeyValues

## Zdroj {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte ho znovu, místo úprav této stránky. -->
