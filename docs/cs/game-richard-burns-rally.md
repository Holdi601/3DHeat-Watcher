---
title: "Richard Burns Rally (živá data)"
nav_order: 39
lang: "cs"
source: game-richard-burns-rally.md
source_hash: "1b9866f5a1f6"
nav_exclude: true
search_exclude: true
---
# Richard Burns Rally (živá data) {#richard-burns-rally-live-data}

Když hrajete Richard Burns Rally, Watcher uloží data, která hra sama posílá ven, abyste se na ně mohli později podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `richard-burns-rally`, druh [`telemetry`](sources-and-rules.md); běží, dokud běží `RichardBurnsRally_SSE.exe` nebo `RichardBurnsRally.exe`, a hledá nová data každých 0,1 s.*

## Co se zaznamenává {#what-is-recorded}

- pozice vlastního auta (světové XYZ, m) 10krát za sekundu s rychlostí, rychlostním stupněm, plynem, brzdou a vzdáleností na etapě
- začátek etapy (spuštění časomíry etapy), konec s časem etapy, restarty
- teleporty (návrat na silnici): `teleport`, kde auto bylo, `spawn`, kde je nyní
- etapy, nejlepší čas etapy, vzdálenost, nejvyšší rychlost

## Odkud to pochází {#where-it-comes-from}

UDP telemetrie z pluginu NGP, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1)

## Jak to zapnout {#how-to-switch-it-on}

RSF/NGP: v RichardBurnsRally.ini v sekci [NGP] nastavte udpTelemetry=1 a koncový bod na 127.0.0.1:6776

## Jak to funguje {#how-it-works}

Telemetrie závodních her: Forza, hry Assetto Corsa, rallye hry
a BeamNG, zaznamenané jako trasy, kola a etapy.

Každá hra zde zveřejňuje svou telemetrii záměrně, pro palubní desky
a pohybové simulátory; nic se do hry nevkládá a nic, co hra nevydává, se nečte. Dekódování
se nepíše dvakrát: jsou to záznamníky kol z gamecapture v
3DHeat GameCapture `heat3d_capture/telemetry`, zkopírované do `heat3d_watch/decoders` (tam otestované na paketech sestavených
podle zveřejněných layoutů). Tento modul jejich snímky převádí na řádky Watcheru -
pozici auta několikrát za sekundu s rychlostí, rychlostním stupněm a pedály,
událost na každé kolo nebo etapu a čísla, která řidič sleduje: kola, nejlepší kolo,
vzdálenost, nejvyšší rychlost.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

UDP „Data Out“, zapnuté v HUD a nastaveních hry (Gameplay), na
127.0.0.1 port 5300, formát Dash. Jeden paket na každý simulační tik; offset
bloku dashe se zjistí z paketů (`forza.detect_layout`). Světové metry,
osa Y nahoru; svět je levotočivý a kreslí se tak, jak přichází, jako to dělá záznamník kol
(dokumentace „Data Out“ od Forza Motorsport a Forza Horizon).
Hra posílá na jeden port a FH Companion a další aplikace Data Out na něm
naslouchají. Dva programy nemohou sdílet stejný port: ve Windows socket navázaný
na 127.0.0.1 dostane pakety a socket navázaný na všechny adresy na stejném
portu nedostane žádné, bez ohledu na to, který přišel první. Watcher proto počká chvíli po
spuštění hry, než port obsadí, nikdy ho nebere aplikaci, která ho drží,
a uvolní ho, jakmile na něm začne naslouchat jiná aplikace.
Dokud port drží, přeposílá každý paket beze změny na
127.0.0.1:5301 - nastavte políčko portu ve FH Companion (jeho záložka telemetrie) na 5301 a
nahrávají se obě.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: `Documents/My Games/WRC/telemetry/config.json` u WRC (paket `session_update`
struktury `wrc`), `hardware_settings_config.xml` u DiRT
(`<udp enabled="true" extradata="3" port="20777">`), plugin NGP u RBR
(`udpTelemetry=1`, port 6776). Etapy podle časomíry etapy hry
(`rally.StageSplitter`). RBR své osy nedokumentuje: osa nahoru je ta, podél které
se pozice mění nejméně, a rozhodne se, až když se relace uzavře.

#### Vše se ukládá {#everything-kept}

Řádků je několik za sekundu; hry posílají mnohem víc. Každý paket UDP, který
přijde - v menu, mezi koly, i ty, které žádný dekodér nečte -, se uloží celý
do `heat.raw.parquet` jejich relace pod svým formátem (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), a každá stránka sdílené paměti
(celé mapování, ne jen dekódované bajty) při každé změně pod názvem svého
mapování (`acpmf_physics`, ...). `used` označuje, co se také stalo
řádky; `selfCheck.completeness` v `meta.json` počítá každý druh (pravidlo
převodníků 3DHeat).

Stejný modul slouží také: [Assetto Corsa (živá data)](game-assetto-corsa.md), [Assetto Corsa Competizione (živá data)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (živá data)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (živá data)](game-assetto-corsa-rally.md), [BeamNG.drive (živá data)](game-beamng.md), [DiRT Rally 2.0 (živá data)](game-dirt-rally-2.md), [EA SPORTS WRC (živá data)](game-ea-wrc.md), [Forza Horizon 4 (živá data)](game-forza-horizon-4.md), [Forza Horizon 5 (živá data)](game-forza-horizon-5.md), [Forza Horizon 6 (živá data)](game-forza-horizon-6.md), [Forza Motorsport (živá data)](game-forza-motorsport.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `y` |
| Jednotky | metry; osa nahoru určena z jízdy (RBR své osy nedokumentuje) |
| Zrcadleno pro prohlížeč | žádné |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto hodnoty se zapíší do `meta.json` (`axes`) každé relace a, pokud relace obsahuje pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítko řádků upravuje sám - viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ne**. `games --markdown` to ukazuje jako „single-player“.
- Druh `telemetry`: čte jen to, co hra nebo platforma vydává (UDP port nebo sdílená paměť, kterou hra zveřejňuje), takže zaznamenává i v online hře i offline; příznak rozhoduje jen o tom, zda se paměť smí vůbec číst.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry `memory`, a nikdy u hry označené jako hraná online - viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (`stats` každé relace v `meta.json` a tabulka `stats` v `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedeny.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, kterou adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky), a `selfCheck.completeness` v `meta.json` počítá každý `type` - `lost` je 0.

**Načteno**

- řádky 10krát za sekundu: pozice, rychlost, rychlostní stupeň, plyn, brzda, vzdálenost na etapě, yaw, otáčky, řízení; začátek etapy, konec s časem etapy, restarty

**Uchováno surové**

- každý paket, který dorazí na port, celý, v tempu hry, pod svým formátem: `telemetry` (TelemetryData pluginu NGP o 664 bajtech), jinak `rbr <n>-byte`
- v paketu nad rámec řádků: postoj, vlastní rychlosti a zrychlení auta, průhyb pružiny a síla každého kola, průběh etapy a vzdálenost do konce; zbytek 664 bajtů (motor, a bloky pneumatik a brzd pro každé kolo) zatím nikde nedekódován

**Nedostupné**

- ostatní auta: hry posílají jen auto hráče
- jednotka rychlosti a osy: nejsou zdokumentované - rychlost se bere z pozic, osa nahoru z jízdy

**Velikost**: asi 160 MB za hodinu při 60 paketech za sekundu (664 bajtů plus 70bajtová hlavička položky); zstd zachová zlomek

## Ověřeno {#verified}

dekódování je ze záznamníku kol gamecapture (testováno na paketech sestavených podle zdokumentovaných layoutů); adaptér testován na paketech sestavených v testu a poslaných přes UDP; zatím neotestováno ve hře

## Zdroj {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte generování znovu, místo úpravy této stránky. -->
