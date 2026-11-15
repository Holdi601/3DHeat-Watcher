---
title: "Assetto Corsa (živé dáta)"
nav_order: 2
lang: "sk"
source: game-assetto-corsa.md
source_hash: "9132272cc104"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa (živé dáta) {#assetto-corsa-live-data}

Počas hry Assetto Corsa watcher ukladá dáta, ktoré samotná hra posiela von, aby ste ich neskôr mohli pozrieť na mape v 3DHeat prehliadači.

*Technické údaje: adaptér `assetto-corsa`, typ [`telemetry`](sources-and-rules.md); beží, kým beží `acs.exe` alebo `acs_x86.exe`, a hľadá nové dáta každých 0,1 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- poloha vlastného auta (svetové XYZ, m: priemer štyroch bodov dotyku pneumatík) 10-krát za sekundu s rýchlosťou, rýchlostným stupňom, plynom a brzdou
- začiatok a koniec relácie s traťou a autom, ktoré hra uvádza
- kolá podľa počítadla kôl hry, s časom kola
- teleporty (späť do boxov, reštart): `teleport`, kde auto bolo, `spawn`, kde je teraz
- kolá, najlepšie kolo, vzdialenosť, najvyššia rýchlosť

## Odkiaľ to berie {#where-it-comes-from}

zdieľaná pamäť Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static

## Ako to zapnúť {#how-to-switch-it-on}

Nič netreba zapínať: watcher číta zdroj tak, ako ho hra alebo platforma poskytuje.

## Ako to funguje {#how-it-works}

Vlastná telemetria závodných hier: Forza, hry Assetto Corsa, rally hry a BeamNG, zaznamenané ako trasy, kolá a etapy.

Každá tu uvedená hra zverejňuje svoju telemetriu zámerne, pre palubné displeje a pohybové simulátory; nič sa do hry nevkladá a nič, čo hra nesprístupňuje, sa nečíta. Dekódovanie sa nerobí dvakrát: sú to záznamníky kôl z 3DHeat GameCapture, `heat3d_capture/telemetry`, skopírované do `heat3d_watch/decoders` (tam otestované na paketoch zostavených podľa zverejnených rozložení). Tento modul ich rámce mení na riadky watchera: poloha auta niekoľkokrát za sekundu s rýchlosťou, rýchlostným stupňom a pedálmi, udalosť pri každom kole alebo etape a čísla, ktoré si vodič zapisuje: kolá, najlepšie kolo, vzdialenosť, najvyššia rýchlosť.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

„Data Out" UDP, zapína sa v hre v nastaveniach HUD a Gameplay, na 127.0.0.1 port 5300, formát Dash. Jeden paket na každý tik simulácie; posun bloku dash sa zistí z paketov (`forza.detect_layout`). Svetové metre, Y smerom nahor; svet je ľavotočivý a kreslí sa tak, ako sa posiela, ako to robí záznamník kôl (dokumentácia Forza Motorsport a Forza Horizon k „Data Out"). Hra posiela na jeden port a FH Companion aj ďalšie aplikácie Data Out počúvajú na tom istom porte. Dva programy naň nemôžu naraz: vo Windows soket viazaný na 127.0.0.1 dostáva pakety a soket viazaný na všetky adresy na tom istom porte nedostane nič, bez ohľadu na to, ktorý spustil prvý. Watcher preto po spustení hry chvíľu počká, než port obsadí, nikdy ho neodoberie aplikácii, ktorá ho drží, a hneď ho uvoľní, keď na ňom začne počúvať iná aplikácia. Kým port drží, každý paket bez zmeny preposiela na 127.0.0.1:5301 - nastavte políčko portu v karte telemetrie FH Companion na 5301 a zaznamenávajú sa obe.

#### Assetto Corsa, ACC, AC EVO, AC Rally {#assetto-corsa-acc-ac-evo-ac-rally}

Zdieľaná pamäť, ktorú hra zapisuje pre aplikácie: `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` (AC EVO: `Local\acevo_pmf_*`). Otvára sa len na čítanie a až keď ju hra vytvorí (`simracing_shm`). Poloha je priemer štyroch bodov dotyku pneumatík, svetové metre, Y smerom nahor. Kolá podľa počítadla hry (AC, ACC) alebo prechodom štartovacím bodom znova (AC EVO, AC Rally), ako to robí `kunos.py` pre záznamník kôl.

#### Všetko sa uchováva {#everything-kept}

Riadkov je niekoľko za sekundu; hry posielajú oveľa viac. Každý UDP paket, ktorý príde - v menu, medzi kolami, aj tie, ktoré žiadny dekodér nečíta - sa uchová celý v `heat.raw.parquet` relácie pod svojím formátom (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Každá stránka zdieľanej pamäte (celé mapovanie, nielen dekódované bajty) sa uchová pri každej zmene pod menom svojho mapovania (`acpmf_physics`, ...). `used` označuje, čo sa stalo aj riadkami; `selfCheck.completeness` v `meta.json` počíta každý druh (pravidlo konvertorov 3DHeat).

Ten istý modul slúži aj: [Assetto Corsa Competizione (živé dáta)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (živé dáta)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (živé dáta)](game-assetto-corsa-rally.md), [BeamNG.drive (živé dáta)](game-beamng.md), [DiRT Rally 2.0 (živé dáta)](game-dirt-rally-2.md), [EA SPORTS WRC (živé dáta)](game-ea-wrc.md), [Forza Horizon 4 (živé dáta)](game-forza-horizon-4.md), [Forza Horizon 5 (živé dáta)](game-forza-horizon-5.md), [Forza Horizon 6 (živé dáta)](game-forza-horizon-6.md), [Forza Motorsport (živé dáta)](game-forza-motorsport.md), [Richard Burns Rally (živé dáta)](game-richard-burns-rally.md).

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

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z jej vlastných názvov štatistík, v tomto zozname nie sú; čo sa zaznamenáva, uvádza vyššie časť „Čo sa zaznamenáva".

## Úplnosť {#completeness}

Watcher sa riadi pravidlom konvertorov 3DHeat ([pravidlo konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)): čo zdroj obsahuje, sa načíta alebo uchová, nikdy sa nezahodí. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia uchované podľa mena; `used` označuje, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` - `lost` je 0.

**Načítané**

- riadky 10-krát za sekundu zo stránky fyziky: poloha (priemer bodov dotyku pneumatík), rýchlosť, rýchlostný stupeň, plyn, brzda, natočenie okolo osí yaw/pitch/roll (rad), otáčky, riadenie (tak, ako ho stránka má); začiatok relácie s traťou a autom zo statickej stránky; kolá, poradie v pretekoch

**Uchované surové**

- každá stránka celá - celá oblasť mapovania, nielen dekódované bajty - pri každej zmene jej bajtov, pri čítaní watchera 10-krát za sekundu: `acpmf_physics`, `acpmf_graphics`, `acpmf_static`; čítanie, ktoré je bajt po bajte rovnaké ako predchádzajúce, sa počíta v `unchanged_reads` v meta.json a neukladá sa znova
- všetko dekódované len pre súbory kôl (`decoders/kunos.py`: pre každé koleso šmyk, zaťaženie, tlak, teploty, sklon, odpruženie, body dotyku, teploty bŕzd, pomer a uhol šmyku; svetová a lokálna rýchlosť, uhlová rýchlosť, asistencie) je na týchto stránkach

**Nie je k dispozícii**

- polohy iných áut: stránky opisujú len auto hráča (grafická stránka ACC má v niektorých verziách ID áut a súradnice ostatných - uchované v surovej stránke, nedekódované)
- fyzikálne ticky medzi čítaniami watchera: hra prepisuje stránku vo svojom fyzikálnom kroku (až 333 Hz) a watcher číta 10-krát za sekundu

**Veľkosť**: približne 150-300 MB za hodinu pred kompresiou (4 KB oblasť na stránku pri až 10 zmenách za sekundu); stránky sú väčšinou nuly a zstd si zachová malú časť

## Overené {#verified}

dekódovanie je z záznamníka kôl z GameCapture (overené na syntetických stránkach); adaptér overený na zdieľanej pamäti zostavenej v teste podľa zdokumentovaného rozloženia; nevyskúšané na skutočnej hre

## Zdroj {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
