---
title: "DiRT Rally 2.0 (živé dáta)"
nav_order: 11
lang: "sk"
source: game-dirt-rally-2.md
source_hash: "367131ff990b"
nav_exclude: true
search_exclude: true
---
# DiRT Rally 2.0 (živé dáta) {#dirt-rally-20-live-data}

Počas hry DiRT Rally 2.0 watcher ukladá dáta, ktoré samotná hra posiela von, aby ste ich neskôr mohli pozrieť na mape v 3DHeat prehliadači.

*Technické údaje: adaptér `dirt-rally-2`, typ [`telemetry`](sources-and-rules.md); beží, kým beží `dirtrally2.exe`, a hľadá nové dáta každých 0,1 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- poloha vlastného auta (svetové XYZ, m) 10-krát za sekundu s rýchlosťou, rýchlostným stupňom, plynom, brzdou a vzdialenosťou v etape
- začiatok etapy (spustenie času etapy), koniec s časom etapy, reštarty
- teleporty (návrat na cestu): `teleport`, kde auto bolo, `spawn`, kde je teraz
- etapy, najlepší čas etapy, vzdialenosť, najvyššia rýchlosť

## Odkiaľ to berie {#where-it-comes-from}

UDP 127.0.0.1:20777, extradata=3 (Dokumenty\My Games\DiRT Rally 2.0\hardwaresettings\hardware_settings_config.xml); kým iná aplikácia drží port 20777, watcher ho nechá jej

## Ako to zapnúť {#how-to-switch-it-on}

`python -m heat3d_watch setup dirt-rally-2 --apply` nastaví &lt;udp enabled="true" extradata="3"> (najprv zálohuje)

Príkaz napíšte do terminálu otvoreného v priečinku watchera (pozrite [Pred začiatkom](before-you-start.md)). Ak zlyhá, posledný riadok povie prečo; [Inštalácia a spustenie](installing-and-running.md) popisuje obvyklé príčiny.

`python -m heat3d_watch setup dirt-rally-2` vypíše súbory, ktoré by zmenil; `python -m heat3d_watch setup dirt-rally-2 --apply` ich zmení a pôvodný súbor nechá ako `<file>.heat3d-backup` (pozrite [Príkazy](commands.md#setup)). Pri každej zmene vypíše `dirt-rally-2: changed: ...`, alebo `dirt-rally-2: nothing to change`, ak je už zapnuté.

## Ako to funguje {#how-it-works}

Vlastná telemetria závodných hier: Forza, hry Assetto Corsa, rally hry a BeamNG, zaznamenané ako trasy, kolá a etapy.

Každá tu uvedená hra zverejňuje svoju telemetriu zámerne, pre palubné displeje a pohybové simulátory; nič sa do hry nevkladá a nič, čo hra nesprístupňuje, sa nečíta. Dekódovanie sa nerobí dvakrát: sú to záznamníky kôl z 3DHeat GameCapture, `heat3d_capture/telemetry`, skopírované do `heat3d_watch/decoders` (tam otestované na paketoch zostavených podľa zverejnených rozložení). Tento modul ich rámce mení na riadky watchera: poloha auta niekoľkokrát za sekundu s rýchlosťou, rýchlostným stupňom a pedálmi, udalosť pri každom kole alebo etape a čísla, ktoré si vodič zapisuje: kolá, najlepšie kolo, vzdialenosť, najvyššia rýchlosť.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

„Data Out" UDP, zapína sa v hre v nastaveniach HUD a Gameplay, na 127.0.0.1 port 5300, formát Dash. Jeden paket na každý tik simulácie; posun bloku dash sa zistí z paketov (`forza.detect_layout`). Svetové metre, Y smerom nahor; svet je ľavotočivý a kreslí sa tak, ako sa posiela, ako to robí záznamník kôl (dokumentácia Forza Motorsport a Forza Horizon k „Data Out"). Hra posiela na jeden port a FH Companion aj ďalšie aplikácie Data Out počúvajú na tom istom porte. Dva programy naň nemôžu naraz: vo Windows soket viazaný na 127.0.0.1 dostáva pakety a soket viazaný na všetky adresy na tom istom porte nedostane nič, bez ohľadu na to, ktorý spustil prvý. Watcher preto po spustení hry chvíľu počká, než port obsadí, nikdy ho neodoberie aplikácii, ktorá ho drží, a hneď ho uvoľní, keď na ňom začne počúvať iná aplikácia. Kým port drží, každý paket bez zmeny preposiela na 127.0.0.1:5301 - nastavte políčko portu v karte telemetrie FH Companion na 5301 a zaznamenávajú sa obe.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: `Dokumenty/My Games/WRC/telemetry/config.json` hry WRC (paket `session_update` štruktúry `wrc`), `hardware_settings_config.xml` hry DiRT (`<udp enabled="true" extradata="3" port="20777">`), NGP plugin hry RBR (`udpTelemetry=1`, port 6776). Etapy podľa času etapy hry (`rally.StageSplitter`). RBR nedokumentuje svoje osi: osa nahor je tá, pozdĺž ktorej sa etapa mení najmenej; určí sa pri zatvorení relácie.

#### Všetko sa uchováva {#everything-kept}

Riadkov je niekoľko za sekundu; hry posielajú oveľa viac. Každý UDP paket, ktorý príde - v menu, medzi kolami, aj tie, ktoré žiadny dekodér nečíta - sa uchová celý v `heat.raw.parquet` relácie pod svojím formátom (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Každá stránka zdieľanej pamäte (celé mapovanie, nielen dekódované bajty) sa uchová pri každej zmene pod menom svojho mapovania (`acpmf_physics`, ...). `used` označuje, čo sa stalo aj riadkami; `selfCheck.completeness` v `meta.json` počíta každý druh (pravidlo konvertorov 3DHeat).

Ten istý modul slúži aj: [Assetto Corsa (živé dáta)](game-assetto-corsa.md), [Assetto Corsa Competizione (živé dáta)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (živé dáta)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (živé dáta)](game-assetto-corsa-rally.md), [BeamNG.drive (živé dáta)](game-beamng.md), [EA SPORTS WRC (živé dáta)](game-ea-wrc.md), [Forza Horizon 4 (živé dáta)](game-forza-horizon-4.md), [Forza Horizon 5 (živé dáta)](game-forza-horizon-5.md), [Forza Horizon 6 (živé dáta)](game-forza-horizon-6.md), [Forza Motorsport (živé dáta)](game-forza-motorsport.md), [Richard Burns Rally (živé dáta)](game-richard-burns-rally.md).

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | áno |
| Osa nahor | `y` |
| Jednotky | metre |
| Zrkadlenie pre prehliadač | žiadne |
| Mierka jednotiek (`scale`: prehliadač ňou násobí polohy) | 1 |

Tieto hodnoty idú do `meta.json` každej relácie (`axes`) a, keď relácia obsahuje polohy, do päty `heat.parquet`, takže 3DHeat prehliadač ich otáča a škáluje sám - pozrite [Dáta](the-data.md).

## Multiplayer {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)".
- Druh `telemetry`: číta len to, čo hra alebo platforma sprístupňuje (UDP port alebo zdieľaná pamäť, ktorú hra zverejňuje), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie vôbec čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online - pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z jej vlastných názvov štatistík, v tomto zozname nie sú; čo sa zaznamenáva, uvádza vyššie časť „Čo sa zaznamenáva".

## Úplnosť {#completeness}

Watcher sa riadi pravidlom konvertorov 3DHeat ([pravidlo konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)): čo zdroj obsahuje, sa načíta alebo uchová, nikdy sa nezahodí. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia uchované podľa mena; `used` označuje, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` - `lost` je 0.

**Načítané**

- riadky 10-krát za sekundu: poloha, rýchlosť, rýchlostný stupeň, plyn, brzda, vzdialenosť v etape, yaw, otáčky, riadenie; začiatok etapy, koniec s časom etapy, reštarty

**Uchované surové**

- každý paket, ktorý dorazí na port, celý, rýchlosťou hry (jeden na každý tik simulácie), pod svojím formátom: `extradata3` (66 floatov, 264 bajtov), `extradata3-64` (64 u DiRT Rally), inak `<n>-byte`
- v pakete za riadkami: všetkých 66 floatov - svetová rýchlosť, vektory strán a smeru, poloha odpruženia a rýchlosť každého kolesa, rýchlosť stopy pneumatiky a teplota bŕzd, G sily, kolá, dĺžka etapy; floaty bez ustáleného názvu sú v súboroch kôl ako `float<i>`

**Nie je k dispozícii**

- iné autá: hry posielajú len auto hráča
- kanál ručnej brzdy: paket ho nemá

**Veľkosť**: približne 70 MB za hodinu pri 60 paketoch za sekundu (264 bajtov plus 70-bajtová hlavička položky); zstd si zachová malú časť

## Overené {#verified}

dekódovanie je z záznamníka kôl z GameCapture (overené na paketoch zostavených podľa zdokumentovaných rozložení); adaptér overený na paketoch zostavených v teste a odoslaných cez UDP; nevyskúšané na skutočnej hre

## Zdroj {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
