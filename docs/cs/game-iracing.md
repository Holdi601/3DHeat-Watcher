---
title: "iRacing (živá data)"
nav_order: 28
lang: "cs"
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (živá data) {#iracing-live-data}

Když hrajete iRacing, Watcher ukládá data, která hra sama posílá ven, abyste se na ně mohli později podívat jako na statistiky a časovou osu.

*Technické podrobnosti: adaptér `iracing`, druh [`telemetry`](sources-and-rules.md); běží, když je spuštěný `iRacingSim64DX11.exe` nebo `iRacingSim64.exe`, a hledá nová data každých 0,1 s.*

## Co se zaznamenává {#what-is-recorded}

- jízda 5krát za sekundu bez pozice (iRacing ji živě nedává): rychlost, rychlostní stupeň, plyn, brzda, kolo, podíl kola, pořadí v závodě a ve třídě, incidenty
- začátek relace, nasedání a vystupování z auta, vjezd a výjezd z boxové uličky, kola s časem kola, incidenty s jejich body, šachovnicová vlajka, konec
- soubory telemetrie .ibt zapsané během jízdy (zeměpisná šířka, délka, výška – prohlížeč je čte)
- kola, nejlepší kolo, incidenty, pořadí v závodě, zastávky v boxech, vzdálenost, nejvyšší rychlost
- celá sdílená paměť v `heat.raw.parquet`: hlavička, hlavičky proměnných, informace o relaci, každý přečtený řádek telemetrie

## Odkud to pochází {#where-it-comes-from}

sdílená paměť Local\IRSDKMemMapFileName (iRacing SDK); soubory .ibt v %USERPROFILE%\Documents\iRacing\telemetry

## Jak to zapnout {#how-to-switch-it-on}

Pro živá data nic. Pro pozice: zapněte záznam telemetrie v autě (Alt+L) nebo nastavte irsdkLog=1 v app.ini

## Jak to funguje {#how-it-works}

iRacing živě: sdílená paměť iRacing SDK, čtená nativně.

iRacing zveřejňuje svou telemetrii pro aplikace v pojmenovaném mapování souboru,
`Local\IRSDKMemMapFileName`, které simulátor vytvoří, zatímco běží (a signalizuje
`Local\IRSDKDataValidEvent` při každé aktualizaci; to tu není potřeba, Watcher
čte desetkrát za sekundu). Rozložení je podle `irsdk_defines.h` z SDK,
také podle pyirsdk (MIT) – tady znovu napsané z těchto údajů:

```text
irsdk_header (little-endian int32s)
    0 ver, 4 status (bit 0: connected), 8 tickRate,
    12 sessionInfoUpdate, 16 sessionInfoLen, 20 sessionInfoOffset,
    24 numVars, 28 varHeaderOffset, 32 numBuf, 36 bufLen, 40 pad[2],
    48 varBuf[4]: { tickCount, bufOffset, pad[2] } (16 bytes each)
irsdk_varHeader (144 bytes, numVars of them at varHeaderOffset)
    0 type (0 char, 1 bool, 2 int, 3 bitfield, 4 float, 5 double),
    4 offset (into a line), 8 count, 12 countAsTime + 3 pad,
    16 name[32], 48 desc[64], 112 unit[32]
session info: YAML text at sessionInfoOffset, rewritten when
    sessionInfoUpdate changes (track, sessions, drivers)
```

Simulátor zapisuje `numBuf` řádků střídavě dokola; nejnovější je ten s
nejvyšším tickCount, a řádek se přečte znovu, pokud se jeho tickCount během kopírování
posunul.

Živá data nemají pozici ve světě – zeměpisná šířka, délka a výška jsou jen v souborech
`.ibt`, které iRacing loguje do `Documents\iRacing\telemetry` (Alt+L v autě, nebo
`irsdkLog=1`), a ty čte prohlížeč 3DHeat sám. Watcher tedy zaznamenává jízdu jako
události bez souřadnic – rychlost, kolo, podíl kola, pořadí v závodě, incidenty –
plus kola, incidenty, zastávky v boxech a šachovnicovou vlajku, a na konci soubory
.ibt zapsané během jízdy jako události `telemetry_file`, aby je prohlížeč mohl otevřít.

Vedle řádků se uchovává celá mapa paměti v surovém záznamu relace
(`heat.raw.parquet`): pevná část hlavičky (`header`, pokaždé, když se změní), hlavičky
proměnných (`var_headers`, celé i jako JSON v `text`, pokaždé, když se změní rozložení),
YAML informací o relaci (`session_info`, jeho text pokaždé, když se pohne
`sessionInfoUpdate`) a nejnovější řádek telemetrie (`telemetry`, každá proměnná
z něj, při každém čtení, které najde nový tik). Hlavičky proměnných a jeden řádek
stačí, aby pozdější dekodér přečetl kteroukoli proměnnou.

Zdroj: iRacing SDK (irsdk_defines.h, dokumentace „iRacing SDK“ na fóru); kutu/pyirsdk
(MIT) pro ověření posunů.

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ne |
| Osa nahoru | `y` |
| Jednotky | živé pozice nejsou; soubory .ibt nesou zeměpisnou šířku, délku a výšku |
| Zrcadleno pro prohlížeč | žádné |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto údaje se zapíšou do `meta.json` každé relace (`axes`) a, pokud má relace pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítko řádků nastavuje sám – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukazuje jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `telemetry`: čte jen to, co hra nebo platforma vydává (UDP port nebo sdílená paměť, kterou hra zveřejňuje), takže zaznamenává i v online hře, nejen offline; příznak rozhoduje jen o tom, zda se paměť smí vůbec číst.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry typu `memory` a nikdy u hry označené jako hraná online – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (u každé relace `stats` v `meta.json` a v tabulce `stats` souboru `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v části „Co se zaznamenává“ jsou pojmenovány.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převaděče](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, které adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky) a `selfCheck.completeness` v `meta.json` počítá každý `type` – `lost` je 0.

**Načteno**

- z nejnovějšího řádku telemetrie: čas relace, číslo, stav a id, na trati, replay, kolo, dokončená kola, podíl a metry kola, poslední a nejlepší kolo, rychlost, rychlostní stupeň, plyn, brzda, otáčky, jízda v boxové uličce, povrch trati, pořadí v závodě a ve třídě, vlastní počet incidentů (řádky `driving` 5krát za sekundu a události)
- nově také na řádcích `driving`: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (stupně, z radiánů simulátoru – jen když hlavička proměnné udává jednotku rad), `fuel_l` (jednotka l), `lat_accel` a `lon_accel` (jednotka m/s^2)
- z YAML informací o relaci: index auta hráče, trať a konfigurace, typy relací, jméno každého jezdce, auto, tým a číslo (řádky session_start, meta.json)
- ověřeno proti bloku sestavenému podle irsdk_defines.h v testech; zatím neověřeno proti simulátoru

**Uchováno surové**

- `telemetry`: nejnovější řádek celý, každá proměnná, kterou simulátor zveřejňuje (pole CarIdx každého auta, pneumatiky, zavěšení, pole ve vysokém rychlostním režimu `_ST`, kde je simulátor má ...), při každém čtení, které najde nový tik; `tick` je počet ticků simulátoru; `used` je false, dokud hraje replay
- `var_headers`: hlavičky proměnných celé (každá 144 bajtů) a v `text` jako JSON (název, typ, posun, počet, jednotka, popis), pokaždé, když se změní rozložení – dost na to, aby se přečetla každá proměnná každého uloženého řádku
- `session_info`: YAML text celý, pokaždé, když se pohne jeho čítač aktualizací (víkend, relace a výsledky, jezdci, nastavení auta, rádio, seznamy kamer), `update` je čítač
- `header`: 112bajtová hlavička iRacing celá, pokaždé, když se změní (verze, stav, tick rate, posuny, ticky řádků)

**Nedostupné**

- pozice ve světě živě: sdílená paměť žádnou nemá; zeměpisná šířka, délka a výška jsou jen v souborech .ibt (když je zapnuté logování), které čte prohlížeč – Watcher jmenuje ty, které byly zapsány během jízdy
- ticky mezi dvěma čteními: simulátor zapisuje 60 řádků za sekundu do 3 nebo 4 slotů a Watcher čte desetkrát za sekundu, takže většina ticků se přepíše dřív, než by šly přečíst; soubor .ibt má každý tik, když je logování zapnuté

**Velikost**: řádek telemetrie má několik KB (asi 5 až 10 KB se všemi poli každého auta), uchovává se až desetkrát za sekundu, k tomu hlavička (112 bajtů) stejně často a YAML informací o relaci (desítky KB), když se změní: asi 0,2 až 0,4 GB za hodinu na trati před komprimací; zstd to srazí na zlomek (zatím neměřeno na skutečné relaci)

## Ověřeno {#verified}

testováno na bloku sdílené paměti sestaveném v testu podle rozložení irsdk; netestováno proti simulátoru

## Zdroj {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
