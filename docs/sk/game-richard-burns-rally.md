---
title: "Richard Burns Rally (živé dáta)"
nav_order: 39
lang: "sk"
source: game-richard-burns-rally.md
source_hash: "1b9866f5a1f6"
nav_exclude: true
search_exclude: true
---
# Richard Burns Rally (živé dáta) {#richard-burns-rally-live-data}

Počas hry Richard Burns Rally watcher ukladá dáta, ktoré samotná hra posiela von, aby ste ich neskôr mohli pozrieť na mape v 3DHeat prehliadači.

*Technické údaje: adaptér `richard-burns-rally`, typ [`telemetry`](sources-and-rules.md); beží, kým beží `RichardBurnsRally_SSE.exe` alebo `RichardBurnsRally.exe`, a hľadá nové dáta každých 0,1 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- poloha vlastného auta (svetové XYZ, m) 10-krát za sekundu s rýchlosťou, rýchlostným stupňom, plynom, brzdou a vzdialenosťou na etape
- začiatok etapy (spustenie časomiery etapy), dojazd s časom etapy, reštarty
- teleporty (reset na cestu): `teleport`, kde auto bolo, `spawn`, kde je teraz
- etapy, najlepší čas etapy, vzdialenosť, najvyššia rýchlosť

## Odkiaľ to berie {#where-it-comes-from}

UDP telemetria pluginu NGP, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1)

## Ako to zapnúť {#how-to-switch-it-on}

RSF/NGP: v RichardBurnsRally.ini v sekcii [NGP] nastavte udpTelemetry=1 a koncový bod 127.0.0.1:6776

## Ako to funguje {#how-it-works}

Vlastná telemetria závodných hier: Forza, hry Assetto Corsa, rally hry a BeamNG, zaznamenané ako trasy, kolá a etapy.

Každá tu uvedená hra zverejňuje svoju telemetriu zámerne, pre palubné displeje a pohybové simulátory; nič sa do hry nevkladá a nič, čo hra nesprístupňuje, sa nečíta. Dekódovanie sa nerobí dvakrát: sú to záznamníky kôl z gamecapture v `heat3d_capture/telemetry` v 3DHeat GameCapture, skopírované do `heat3d_watch/decoders` (tam otestované proti paketom zostaveným z zverejnených popisov formátu). Tento modul ich rámce mení na riadky watchera: polohu auta niekoľkokrát za sekundu s rýchlosťou, plynom a brzdou, udalosť pri každom kole alebo etape a čísla, ktoré si vodič zapisuje: kolá, najlepšie kolo, vzdialenosť a najvyššiu rýchlosť.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

UDP „Data Out“, zapnuté v nastaveniach HUD a hrania hry, na 127.0.0.1 port 5300, formát Dash. Jeden paket na každý tik simulácie; posun bloku dashboardu sa zistí z paketov (`forza.detect_layout`). Svetové metre, os Y nahor; svet je ľavotočivý a kreslí sa tak, ako ho hra posiela, rovnako ako to robí záznamník kôl (dokumentácia „Data Out“ pre Forza Motorsport a Forza Horizon). Hra posiela na jeden port a FH Companion aj ďalšie aplikácie „Data Out“ počúvajú na tom istom porte. Dva programy naň nemôžu naraz: vo Windows soket viazaný na 127.0.0.1 dostáva pakety a soket viazaný na všetky adresy na tom istom porte nedostane žiadne, bez ohľadu na to, ktorý vznikol prvý. Watcher preto po spustení hry chvíľu počká, než port obsadí, nikdy ho neodoberie aplikácii, ktorá ho drží, a uvoľní ho hneď, ako si ho začne počúvať iná aplikácia. Kým port drží, každý paket bez zmeny posiela ďalej na 127.0.0.1:5301 – nastavte políčko portu v karte telemetrie FH Companion na 5301 a zaznamenávajú sa obe.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: `Documents/My Games/WRC/telemetry/config.json` pre WRC (paket `session_update` štruktúry `wrc`), `hardware_settings_config.xml` pre DiRT (`<udp enabled="true" extradata="3" port="20777">`), NGP plugin pre RBR (`udpTelemetry=1`, port 6776). Etapy podľa časomiery etapy hry (`rally.StageSplitter`). RBR nedokumentuje svoje osi: os nahor je tá, pozdĺž ktorej sa etapa mení najmenej, a rozhodne sa pri uzavretí relácie.

#### Všetko, čo sa uchováva {#everything-kept}

Riadkov je niekoľko za sekundu; hry posielajú oveľa viac. Každý UDP paket, ktorý príde – v menu, medzi kolami, aj tie, ktoré žiadny dekodér nečíta –, sa uchová celý v `heat.raw.parquet` relácie pod svojím formátom (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), a každá stránka zdieľanej pamäte (celé mapovanie, nie len bajty, ktoré sa dekódujú) pri každej zmene pod názvom svojho mapovania (`acpmf_physics`, ...). `used` označuje to, čo sa stalo aj riadkami; `selfCheck.completeness` v `meta.json` počíta každý druh (pravidlo konvertorov 3DHeat).

Rovnaký modul slúži aj: [Assetto Corsa (živé dáta)](game-assetto-corsa.md), [Assetto Corsa Competizione (živé dáta)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (živé dáta)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (živé dáta)](game-assetto-corsa-rally.md), [BeamNG.drive (živé dáta)](game-beamng.md), [DiRT Rally 2.0 (živé dáta)](game-dirt-rally-2.md), [EA SPORTS WRC (živé dáta)](game-ea-wrc.md), [Forza Horizon 4 (živé dáta)](game-forza-horizon-4.md), [Forza Horizon 5 (živé dáta)](game-forza-horizon-5.md), [Forza Horizon 6 (živé dáta)](game-forza-horizon-6.md), [Forza Motorsport (živé dáta)](game-forza-motorsport.md).

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | áno |
| Os nahor | `y` |
| Jednotky | metre; os nahor sa určí z jazdy (RBR nedokumentuje svoje osi) |
| Zrkadlenie pre prehliadač | žiadne |
| Mierka jednotiek (`scale`: prehliadač polohy touto hodnotou násobí) | 1 |

Tieto údaje idú do `meta.json` každej relácie (`axes`) a, ak má relácia polohy, do päty súboru `heat.parquet`, takže 3DHeat prehliadač si riadky sám otočí a zmení ich mierku – pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hrané online (`multiplayer`): **nie**. `games --markdown` to zobrazí ako „jeden hráč“.
- Typ `telemetry`: číta len to, čo hra alebo platforma vydáva (UDP port alebo zdieľaná pamäť, ktorú hra zverejňuje), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online – pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (štatistiky každej relácie `stats` v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč na tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z názvov štatistík hry, v tomto zozname nie sú; „Čo sa zaznamenáva“ vyššie ich pomenúva.

## Úplnosť {#completeness}

Watcher sa riadi [pravidlom konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, čo zdroj obsahuje, sa číta alebo uchováva, nikdy sa nezahadzuje. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia, ktoré sa uchovávajú podľa mena; `used` označuje to, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` – `lost` je 0.

**Čítané**

- riadky 10-krát za sekundu: poloha, rýchlosť, rýchlostný stupeň, plyn, brzda, vzdialenosť na etape, yaw, otáčky, riadenie; začiatok etapy, dojazd s časom etapy, reštarty

**Uchované surové**

- každý paket, ktorý dorazí na port, celý, rýchlosťou hry: `telemetry` (664-bajtová štruktúra TelemetryData z NGP), inak `rbr <n>-byte`
- v pakete okrem riadkov: postoj, vlastné rýchlosti a zrýchlenia auta, pre každé koleso výchylka a sila pružiny, postup etapy a vzdialenosť do cieľa; zvyšok 664 bajtov (motor, bloky pneumatík a bŕzd pre každé koleso) zatiaľ nikde nedekóduje

**Nedostupné**

- iné autá: hry posielajú len auto hráča
- jeho jednotka rýchlosti a osi: nie sú zdokumentované – rýchlosť sa berie z polôh, os nahor z jazdy

**Veľkosť**: približne 160 MB za hodinu pri 60 paketoch za sekundu (664 bajtov plus 70-bajtová hlavička položky); zstd zachová zlomok

## Overené {#verified}

dekódovanie je z záznamníka kôl gamecapture (testované na paketoch zostavených podľa zdokumentovaných rozložení); adaptér testovaný na paketoch zostavených v teste a poslaných cez UDP; neotestované proti hre

## Zdroj {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generované z adaptéra nástrojom tools/gen_game_pages.py; zmeňte adaptér a spustite to znova, namiesto úpravy tejto stránky. -->
