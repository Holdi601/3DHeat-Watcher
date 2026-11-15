---
title: "DiRT Rally 2.0 (živá data)"
nav_order: 11
lang: "cs"
source: game-dirt-rally-2.md
source_hash: "367131ff990b"
nav_exclude: true
search_exclude: true
---
# DiRT Rally 2.0 (živá data) {#dirt-rally-20-live-data}

Když hrajete DiRT Rally 2.0, Watcher ukládá data, která hra sama posílá ven, abyste se na ně mohli později podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `dirt-rally-2`, druh [`telemetry`](sources-and-rules.md); běží, když je spuštěný `dirtrally2.exe`, a hledá nová data každých 0,1 s.*

## Co se zaznamenává {#what-is-recorded}

- pozice vlastního auta (světové XYZ, m) každou 0,1 s spolu s rychlostí, rychlostním stupněm, plynem, brzdou a vzdáleností na etapě
- začátek etapy (rozběh časomíry etapy), konec s časem etapy, restarty
- teleporty (návrat na silnici): `teleport` tam, kde auto bylo, `spawn` tam, kde je teď
- etapy, nejlepší čas etapy, vzdálenost, nejvyšší rychlost

## Odkud to pochází {#where-it-comes-from}

UDP 127.0.0.1:20777, extradata=3 (Documents\My Games\DiRT Rally 2.0\hardwaresettings\hardware_settings_config.xml); dokud port 20777 drží jiná aplikace, Watcher ho jí nechá

## Jak to zapnout {#how-to-switch-it-on}

`python -m heat3d_watch setup dirt-rally-2 --apply` nastaví &lt;udp enabled="true" extradata="3"> (nejdřív se zazálohuje)

Příkaz napište do terminálu otevřeného ve složce Watcheru (viz [Než začnete](before-you-start.md)). Pokud selže, poslední řádek řekne proč; [Instalace a spuštění](installing-and-running.md) popisuje obvyklé příčiny.

`python -m heat3d_watch setup dirt-rally-2` vypíše soubory, které by změnil; `python -m heat3d_watch setup dirt-rally-2 --apply` je opravdu změní a původní soubor uloží jako `<file>.heat3d-backup` (viz [Příkazy](commands.md#setup)). Pro každou změnu vypíše `dirt-rally-2: changed: ...`, nebo `dirt-rally-2: nothing to change`, když je už zapnuto.

## Jak to funguje {#how-it-works}

Telemetrie vlastních závodních her: Forza, hry Assetto Corsa, rallye hry
a BeamNG, zaznamenaná jako trasy, kola a etapy.

Každá zde uvedená hra zveřejňuje svou telemetrii záměrně, pro palubní desky
a pohybová zařízení; nic se do hry nevkládá a nic, co hra nevydává, se nečte. Dekódování
se nepíše dvakrát: použijí se záznamníky kol z 3DHeat GameCapture, konkrétně
`heat3d_capture/telemetry`, zkopírované do `heat3d_watch/decoders` (tam otestované
na paketech sestavených podle zveřejněných popisů formátu). Tento modul pak jejich snímky
převádí na řádky Watcheru: pozice auta několikrát za sekundu s rychlostí, rychlostním stupněm
a pedály, událost na každé kolo nebo etapu a čísla, která řidič sleduje: kola, nejlepší
kolo, vzdálenost, nejvyšší rychlost.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

„Data Out“ UDP, zapnuté v nastavení hry v HUD a Gameplay, na
127.0.0.1, port 5300, formát Dash. Jeden paket na každý tik simulace; offset
bloku dash se najde z paketů (`forza.detect_layout`). Světové metry, osa Y nahoru; svět je
levoruký a kreslí se tak, jak přichází, stejně jako to dělá záznamník kol
(dokumentace Forza Motorsport a Forza Horizon k „Data Out“).
Hra posílá na jeden port a FH Companion i další aplikace „Data Out“ na něm
naslouchají také. Dva programy ho nemohou sdílet: ve Windows socket navázaný
na 127.0.0.1 dostává pakety a socket navázaný na všechny adresy na stejném
portu nedostane žádný, bez ohledu na to, který se spustil první. Proto Watcher chvíli počká,
než po spuštění hry port obsadí, nikdy ho neodebere aplikaci, která ho drží,
a uvolní ho, jakmile na něm začne poslouchat jiná aplikace.
Dokud port drží, přeposílá každý paket beze změny
na 127.0.0.1:5301. Nastavte pole portu v FH Companion (na kartě telemetrie) na 5301
a nahrávají se obě.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: `Documents/My Games/WRC/telemetry/config.json` ve hře WRC (paket `session_update`
struktury `wrc`), `hardware_settings_config.xml` u DiRTu
(`<udp enabled="true" extradata="3" port="20777">`), NGP plugin RBR
(`udpTelemetry=1`, port 6776). Etapy podle časomíry etapy hry
(`rally.StageSplitter`). RBR nedokumentuje své osy: osa nahoru je ta, podél které
se etapa mění nejméně; určí se při uzavření relace.

#### Vše se ukládá {#everything-kept}

Řádků je několik za sekundu; hry posílají mnohem víc. Každý UDP paket, který
přijde – v menu, mezi koly, i ty, které žádný dekodér nečte – se uloží celý
do `heat.raw.parquet` relace pod svým formátem (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...). Každá stránka sdílené paměti
(celé mapování, ne jen dekódované bajty) se uloží pokaždé, když se změní, pod
názvem svého mapování (`acpmf_physics`, ...). `used` označuje, co se také stalo
řádky; `selfCheck.completeness` v `meta.json` počítá každý druh (pravidlo
převaděče 3DHeat).

Stejný modul slouží také: [Assetto Corsa (živá data)](game-assetto-corsa.md), [Assetto Corsa Competizione (živá data)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (živá data)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (živá data)](game-assetto-corsa-rally.md), [BeamNG.drive (živá data)](game-beamng.md), [EA SPORTS WRC (živá data)](game-ea-wrc.md), [Forza Horizon 4 (živá data)](game-forza-horizon-4.md), [Forza Horizon 5 (živá data)](game-forza-horizon-5.md), [Forza Horizon 6 (živá data)](game-forza-horizon-6.md), [Forza Motorsport (živá data)](game-forza-motorsport.md), [Richard Burns Rally (živá data)](game-richard-burns-rally.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `y` |
| Jednotky | metry |
| Zrcadleno pro prohlížeč | žádné |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto údaje se zapíšou do `meta.json` každé relace (`axes`) a, pokud má relace pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítko řádků nastavuje sám – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukazuje jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `telemetry`: čte jen to, co hra nebo platforma vydává (UDP port nebo sdílená paměť, kterou hra zveřejňuje), takže zaznamenává i v online hře, nejen offline; příznak rozhoduje jen o tom, zda se paměť smí vůbec číst.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry typu `memory` a nikdy u hry označené jako hraná online – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (u každé relace `stats` v `meta.json` a v tabulce `stats` souboru `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v části „Co se zaznamenává“ jsou pojmenovány.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převaděče](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, které adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky) a `selfCheck.completeness` v `meta.json` počítá každý `type` – `lost` je 0.

**Načteno**

- řádky po 0,1 s: pozice, rychlost, rychlostní stupeň, plyn, brzda, vzdálenost na etapě, natočení, otáčky, řízení; začátek etapy, konec s časem etapy, restarty

**Uchováno surové**

- každý paket, který dorazí na port, celý, rychlostí hry, pod svým formátem: `extradata3` (66 floatů, 264 bajtů), `extradata3-64` (64 u DiRT Rally), jinak `<n>-byte`
- v paketu navíc, mimo řádky: všech 66 floatů – rychlost vozu ve světě, boční a přední vektory, poloha zavěšení a rychlost každého kola, rychlost stopy pneumatiky a teplota brzdy, g-síly, kola, délka etapy; floaty bez ustáleného názvu jsou v souborech kol jako `float<i>`

**Nedostupné**

- jiná auta: hry posílají jen auto hráče
- kanál ruční brzdy: paket ho nemá

**Velikost**: asi 70 MB za hodinu při 60 paketech za sekundu (264 bajtů plus 70bajtová hlavička položky); zstd z toho nechá zlomek

## Ověřeno {#verified}

dekódování je z záznamníku kol gamecapture (testováno na paketech sestavených podle zdokumentovaných rozložení); adaptér testován na paketech sestavených v testu a odeslaných přes UDP; netestováno proti hře

## Zdroj {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
