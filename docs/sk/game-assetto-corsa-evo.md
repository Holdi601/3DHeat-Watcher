---
title: "Assetto Corsa EVO (živé dáta)"
nav_order: 4
lang: "sk"
source: game-assetto-corsa-evo.md
source_hash: "b14d46c10e85"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa EVO (živé dáta) {#assetto-corsa-evo-live-data}

Počas hry Assetto Corsa EVO watcher ukladá dáta, ktoré samotná hra posiela von, aby ste ich neskôr mohli pozrieť na mape v 3DHeat prehliadači.

*Technické údaje: adaptér `assetto-corsa-evo`, typ [`telemetry`](sources-and-rules.md); beží, kým beží `AssettoCorsaEVO.exe`, a hľadá nové dáta každých 0,1 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- poloha vlastného auta (svetové XYZ, m: priemer bodov dotyku pneumatík) 10-krát za sekundu s rýchlosťou, rýchlostným stupňom, plynom a brzdou
- začiatok a koniec relácie s traťou a autom, ktoré hra uvádza
- kolá vtedy, keď auto prejde miestom, kde jazda začala, a ide tým istým smerom
- teleporty (späť do boxov, reštart): `teleport`, kde auto bolo, `spawn`, kde je teraz
- kolá, najlepšie kolo, vzdialenosť, najvyššia rýchlosť

## Odkiaľ to berie {#where-it-comes-from}

zdieľaná pamäť Local\acevo_pmf_physics, Local\acevo_pmf_static

## Ako to zapnúť {#how-to-switch-it-on}

Nič netreba zapínať: watcher číta zdroj tak, ako ho hra alebo platforma poskytuje.

## Ako to funguje {#how-it-works}

Vlastná telemetria závodných hier: Forza, hry Assetto Corsa, rally hry a BeamNG, zaznamenané ako trasy, kolá a etapy.

Každá tu uvedená hra zverejňuje svoju telemetriu zámerne, pre palubné displeje a pohybové simulátory; nič sa do hry nevkladá a nič, čo hra nesprístupňuje, sa nečíta. Dekódovanie sa nerobí dvakrát: sú to záznamníky kôl z gamecapture v `heat3d_capture/telemetry` v 3DHeat GameCapture, skopírované do `heat3d_watch/decoders` (tam otestované proti paketom zostaveným z zverejnených popisov formátu). Tento modul ich rámce mení na riadky watchera: polohu auta niekoľkokrát za sekundu s rýchlosťou, plynom a brzdou, udalosť pri každom kole alebo etape a čísla, ktoré si vodič zapisuje: kolá, najlepšie kolo, vzdialenosť a najvyššiu rýchlosť.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

UDP „Data Out“, zapnuté v nastaveniach HUD a hrania hry, na 127.0.0.1 port 5300, formát Dash. Jeden paket na každý tik simulácie; posun bloku dashboardu sa zistí z paketov (`forza.detect_layout`). Svetové metre, os Y nahor; svet je ľavotočivý a kreslí sa tak, ako ho hra posiela, rovnako ako to robí záznamník kôl (dokumentácia „Data Out“ pre Forza Motorsport a Forza Horizon). Hra posiela na jeden port a FH Companion aj ďalšie aplikácie „Data Out“ počúvajú na tom istom porte. Dva programy naň nemôžu naraz: vo Windows soket viazaný na 127.0.0.1 dostáva pakety a soket viazaný na všetky adresy na tom istom porte nedostane žiadne, bez ohľadu na to, ktorý vznikol prvý. Watcher preto po spustení hry chvíľu počká, než port obsadí, nikdy ho neodoberie aplikácii, ktorá ho drží, a uvoľní ho hneď, ako si ho začne počúvať iná aplikácia. Kým port drží, každý paket bez zmeny posiela ďalej na 127.0.0.1:5301 – nastavte políčko portu v karte telemetrie FH Companion na 5301 a zaznamenávajú sa obe.

#### Všetko, čo sa uchováva {#everything-kept}

Riadkov je niekoľko za sekundu; hry posielajú oveľa viac. Každý UDP paket, ktorý príde – v menu, medzi kolami, aj tie, ktoré žiadny dekodér nečíta –, sa uchová celý v `heat.raw.parquet` relácie pod svojím formátom (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), a každá stránka zdieľanej pamäte (celé mapovanie, nie len bajty, ktoré sa dekódujú) pri každej zmene pod názvom svojho mapovania (`acpmf_physics`, ...). `used` označuje to, čo sa stalo aj riadkami; `selfCheck.completeness` v `meta.json` počíta každý druh (pravidlo konvertorov 3DHeat).

Rovnaký modul slúži aj: [Assetto Corsa (živé dáta)](game-assetto-corsa.md), [Assetto Corsa Competizione (živé dáta)](game-assetto-corsa-competizione.md), [Assetto Corsa Rally (živé dáta)](game-assetto-corsa-rally.md), [BeamNG.drive (živé dáta)](game-beamng.md), [DiRT Rally 2.0 (živé dáta)](game-dirt-rally-2.md), [EA SPORTS WRC (živé dáta)](game-ea-wrc.md), [Forza Horizon 4 (živé dáta)](game-forza-horizon-4.md), [Forza Horizon 5 (živé dáta)](game-forza-horizon-5.md), [Forza Horizon 6 (živé dáta)](game-forza-horizon-6.md), [Forza Motorsport (živé dáta)](game-forza-motorsport.md), [Richard Burns Rally (živé dáta)](game-richard-burns-rally.md).

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | áno |
| Os nahor | `y` |
| Jednotky | metre |
| Zrkadlenie pre prehliadač | žiadne |
| Mierka jednotiek (`scale`: prehliadač polohy touto hodnotou násobí) | 1 |

Tieto údaje idú do `meta.json` každej relácie (`axes`) a, ak má relácia polohy, do päty súboru `heat.parquet`, takže 3DHeat prehliadač si riadky sám otočí a zmení ich mierku – pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)“.
- Typ `telemetry`: číta len to, čo hra alebo platforma vydáva (UDP port alebo zdieľaná pamäť, ktorú hra zverejňuje), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online – pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (štatistiky každej relácie `stats` v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč na tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z názvov štatistík hry, v tomto zozname nie sú; „Čo sa zaznamenáva“ vyššie ich pomenúva.

## Úplnosť {#completeness}

Watcher sa riadi [pravidlom konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, čo zdroj obsahuje, sa číta alebo uchováva, nikdy sa nezahadzuje. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia, ktoré sa uchovávajú podľa mena; `used` označuje to, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` – `lost` je 0.

**Čítané**

- riadky 10-krát za sekundu zo stránky fyziky: poloha (priemer bodov dotyku pneumatík), rýchlosť, rýchlostný stupeň, plyn, brzda, yaw/pitch/roll (rad), otáčky, riadenie (tak, ako ich stránka má); začiatok relácie s traťou a autom zo statickej stránky; kolá, pozícia v pretekoch

**Uchované surové**

- každá stránka celá – celá oblasť mapovania, nie len bajty, ktoré sa dekódujú – pri každej zmene jej bajtov, pri čítaní watchera 10-krát za sekundu: `acevo_pmf_physics`, `acevo_pmf_static`; opätovné čítanie, ktoré je bajt po bajte rovnaké ako posledné, sa počíta v `unchanged_reads` v meta.json a neukladá sa znova
- všetko, čo sa dekóduje len pre súbory kôl (`decoders/kunos.py`: šmyk, zaťaženie, tlak a teploty každého kolesa, uhol rázu, odpruženie, body dotyku, teploty bŕzd, pomer a uhol šmyku; svetová a lokálna rýchlosť, uhlová rýchlosť, pomôcky), je na týchto stránkach

**Nedostupné**

- polohy iných áut: stránky opisujú len auto hráča (grafická stránka ACC má v niektorých verziách ID áut a ich súradnice, sú uchované v surovej stránke, nedekódujú sa)
- fyzikálne tiky medzi čítaniami watchera: hra prepisuje stránku vo svojom fyzikálnom kroku (až 333 Hz) a watcher číta 10-krát za sekundu
- počítadlo kôl alebo čas kola hry: stránky AC EVO, ako sa čítajú, nemajú grafickú stránku; kolá sa delia podľa polohy

**Veľkosť**: približne 150 až 300 MB za hodinu pred kompresiou (stránka 4 KB na každú stránku, až 10 zmien za sekundu); stránky sú väčšinou nuly a zstd zachová malý zlomok

## Overené {#verified}

dekódovanie je z záznamníka kôl gamecapture (testované na syntetických stránkach); adaptér testovaný na zdieľanej pamäti zostavenej v teste podľa zdokumentovaného rozloženia; neotestované proti hre; názov spustiteľného súboru je z hlásení hráčov

## Zdroj {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generované z adaptéra nástrojom tools/gen_game_pages.py; zmeňte adaptér a spustite to znova, namiesto úpravy tejto stránky. -->
