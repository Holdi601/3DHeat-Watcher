---
title: "iRacing (živé dáta)"
nav_order: 28
lang: "sk"
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (živé dáta) {#iracing-live-data}

Počas hry iRacing watcher ukladá dáta, ktoré samotná hra posiela von, aby ste ich neskôr mohli pozrieť ako štatistiky a časovú os.

*Technické údaje: adaptér `iracing`, typ [`telemetry`](sources-and-rules.md); beží, kým beží `iRacingSim64DX11.exe` alebo `iRacingSim64.exe`, a hľadá nové dáta každých 0,1 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- jazda 5-krát za sekundu bez polohy (iRacing ju živo neposkytuje): rýchlosť, rýchlostný stupeň, plyn, brzda, kolo, podiel kola, poradie v pretekoch a v triede, incidenty
- začiatok relácie, nastupovanie a vystupovanie z auta, vjazd a výjazd z boxovej uličky, kolá s časom kola, incidenty s ich bodmi, šachovnicová vlajka, cieľ
- súbory telemetrie .ibt zapísané počas sedenia (zemepisná šírka, dĺžka, výška - prehliadač ich číta)
- kolá, najlepšie kolo, incidenty, poradie v pretekoch, zastávky v boxoch, vzdialenosť, najvyššia rýchlosť
- celá zdieľaná pamäť v `heat.raw.parquet`: hlavička, hlavičky premenných, informácie o relácii, každý riadok telemetrie, ktorý sa načítal

## Odkiaľ to berie {#where-it-comes-from}

zdieľaná pamäť Local\IRSDKMemMapFileName (iRacing SDK); súbory .ibt v %USERPROFILE%\Documents\iRacing\telemetry

## Ako to zapnúť {#how-to-switch-it-on}

Pre živé dáta netreba nič. Pre polohy: zapnite logovanie telemetrie v aute (Alt+L) alebo nastavte irsdkLog=1 v app.ini

## Ako to funguje {#how-it-works}

iRacing, živo: pamäť zdieľaná SDK iRacingu, čítaná natívne.

iRacing zverejňuje svoju telemetriu pre aplikácie v pomenovanom mapovaní súboru, `Local\IRSDKMemMapFileName`, ktoré simulátor vytvorí počas behu (a signalizuje `Local\IRSDKDataValidEvent` pri každej aktualizácii, čo tu nie je potrebné: watcher číta desaťkrát za sekundu). Rozloženie je podľa `irsdk_defines.h` z SDK, tiež podľa pyirsdk (MIT) - tu znova napísané z týchto faktov:

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

Simulátor zapisuje `numBuf` riadkov v kruhu; najnovší je ten s najvyšším tickCount, a riadok sa načíta znova, ak sa jeho tickCount pohol počas kopírovania.

Živé dáta nemajú svetovú polohu - zemepisná šírka, dĺžka a výška sú len v súboroch `.ibt`, ktoré iRacing loguje do `Documents\iRacing\telemetry` (Alt+L v aute alebo `irsdkLog=1`), a tie číta 3DHeat prehliadač sám. Watcher preto zaznamenáva jazdu ako udalosti bez súradníc - rýchlosť, kolo, podiel prejdeného kola, poradie v pretekoch, incidenty - plus kolá, incidenty, zastávky v boxoch a šachovnicovú vlajku, a na konci súbory `.ibt` zapísané počas sedenia ako udalosti `telemetry_file`, aby ich prehliadač mohol otvoriť.

Popri riadkoch sa celá mapa pamäte uchováva v surovom sprievodnom súbore relácie (`heat.raw.parquet`): pevná časť hlavičky (`header`, zakaždým, keď sa zmení), hlavičky premenných (`var_headers`, celé a v `text` ako JSON, keď sa zmení rozloženie), textový YAML informácií o relácii (`session_info`, jeho text vždy, keď sa pohne počítadlo `sessionInfoUpdate`) a najnovší riadok telemetrie (`telemetry`, každá premenná z neho, pri každom čítaní, ktoré nájde nový tick). Hlavičky premenných a jeden riadok sú všetko, čo neskorší dekodér potrebuje na čítanie ľubovoľnej premennej.

Zdroj: iRacing SDK (irsdk_defines.h, dokumentácia „iRacing SDK" na fórach); kutu/pyirsdk (MIT) na potvrdenie posunov.

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | nie |
| Osa nahor | `y` |
| Jednotky | živé polohy nie sú; súbory .ibt nesú zemepisnú šírku/dĺžku/výšku |
| Zrkadlenie pre prehliadač | žiadne |
| Mierka jednotiek (`scale`: prehliadač ňou násobí polohy) | 1 |

Tieto hodnoty idú do `meta.json` každej relácie (`axes`) a, keď relácia obsahuje polohy, do päty `heat.parquet`, takže 3DHeat prehliadač ich otáča a škáluje sám - pozrite [Dáta](the-data.md).

## Multiplayer {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)".
- Druh `telemetry`: číta len to, čo hra alebo platforma sprístupňuje (UDP port alebo zdieľaná pamäť, ktorú hra zverejňuje), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie vôbec čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online - pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z jej vlastných názvov štatistík, v tomto zozname nie sú; čo sa zaznamenáva, uvádza vyššie časť „Čo sa zaznamenáva".

## Úplnosť {#completeness}

Watcher sa riadi pravidlom konvertorov 3DHeat ([pravidlo konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)): čo zdroj obsahuje, sa načíta alebo uchová, nikdy sa nezahodí. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia uchované podľa mena; `used` označuje, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` - `lost` je 0.

**Načítané**

- z najnovšieho riadku telemetrie: čas relácie, číslo, stav a ID, na trati, replay, kolo, dokončené kolá, podiel a metre kola, posledné a najlepšie kolo, rýchlosť, rýchlostný stupeň, plyn, brzda, otáčky, boxová ulička, povrch trate, poradie v pretekoch a v triede, vlastný počet incidentov (riadky `driving` 5-krát za sekundu a udalosti)
- teraz aj na riadkoch `driving`: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (stupne, z radiánov simulátora - len keď hlavička premennej uvádza jednotku rad), `fuel_l` (jednotka l), `lat_accel` a `lon_accel` (jednotka m/s^2)
- z YAML informácií o relácii: index auta hráča, trať a konfigurácia, typy relácií, meno každého jazdca, auto, tím a číslo (riadky session_start, meta.json)
- overené na bloku zostavenom z irsdk_defines.h v testoch; zatiaľ nie na samotnom simulátore

**Uchované surové**

- `telemetry`: najnovší riadok celý, každá premenná, ktorú simulátor zverejňuje (polia CarIdx každého auta, pneumatiky, odpruženie, polia `_ST` s vysokou frekvenciou, kde ich simulátor má ...), pri každom čítaní, ktoré nájde nový tick; `tick` je počet ticků simulátora; `used` je false, kým beží replay
- `var_headers`: hlavičky premenných celé (144 bajtov každá) a v `text` ako JSON (názov, typ, posun, počet, jednotka, popis), vždy, keď sa zmení rozloženie - dosť na čítanie každej premennej každého uchovaného riadku
- `session_info`: YAML text celý vždy, keď sa pohne jeho počítadlo aktualizácie (víkend, relácie a výsledky, jazdci, nastavenie auta, rádio, zoznamy kamier), `update` je počítadlo
- `header`: 112-bajtová hlavička irsdk celá vždy, keď sa zmení (verzia, stav, frekvencia ticků, posuny, ticky riadkov)

**Nie je k dispozícii**

- živá svetová poloha: zdieľaná pamäť ju nemá; zemepisná šírka, dĺžka a výška sú len v súboroch .ibt (keď je logovanie zapnuté), ktoré prehliadač číta - watcher pomenúva tie, ktoré boli zapísané počas sedenia
- ticky medzi dvoma čítaniami: simulátor zapisuje 60 riadkov za sekundu do 3 alebo 4 slotov a watcher číta 10-krát za sekundu, takže väčšina ticků sa prepíše skôr, než by sa dali prečítať; súbor .ibt má každý tick, keď je logovanie zapnuté

**Veľkosť**: riadok telemetrie má niekoľko KB (okolo 5 až 10 KB so všetkými poliami každého auta), uchováva sa až 10-krát za sekundu, plus hlavička (112 bajtov) rovnako často a YAML informácií o relácii (desiatky KB), keď sa zmení: okolo 0,2 až 0,4 GB za hodinu na trati pred kompresiou; zstd to zmenší na zlomok (na skutočnej relácii ešte nezmerané)

## Overené {#verified}

overené na bloku zostavenom v teste z rozloženia irsdk; nevyskúšané na simulátore

## Zdroj {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
