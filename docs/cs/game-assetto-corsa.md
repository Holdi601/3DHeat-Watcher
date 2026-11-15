---
title: "Assetto Corsa (živá data)"
nav_order: 2
lang: "cs"
source: game-assetto-corsa.md
source_hash: "9132272cc104"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa (živá data) {#assetto-corsa-live-data}

Když hrajete Assetto Corsa, Watcher ukládá data, která hra sama posílá ven, abyste se na ně mohli později podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `assetto-corsa`, druh [`telemetry`](sources-and-rules.md); běží, když je spuštěný `acs.exe` nebo `acs_x86.exe`, a hledá nová data každých 0,1 s.*

## Co se zaznamenává {#what-is-recorded}

- pozice vlastního auta (světové XYZ, m: průměr bodů dotyku pneumatik) každou 0,1 s spolu s rychlostí, rychlostním stupněm, plynem a brzdou
- začátek a konec relace s tratí a autem, jak je hra pojmenuje
- kola podle počítadla kol hry, s jeho časem kola
- teleporty (návrat do boxů, restart): `teleport` tam, kde auto bylo, `spawn` tam, kde je teď
- kola, nejlepší kolo, vzdálenost, nejvyšší rychlost

## Odkud to pochází {#where-it-comes-from}

sdílená paměť Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static

## Jak to zapnout {#how-to-switch-it-on}

Nic se nemusí zapínat: Watcher čte zdroj tak, jak ho hra nebo platforma poskytuje.

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

#### Assetto Corsa, ACC, AC EVO, AC Rally {#assetto-corsa-acc-ac-evo-ac-rally}

Sdílená paměť, kterou hra zapisuje pro aplikace: `Local\acpmf_physics`,
`Local\acpmf_graphics`, `Local\acpmf_static` (AC EVO: `Local\acevo_pmf_*`).
Otevírá se jen pro čtení a až ve chvíli, kdy ji hra vytvoří (`simracing_shm`). Pozice je
průměr čtyř bodů dotyku pneumatik, světové metry, osa Y nahoru.
Kola podle počítadla hry (AC, ACC), nebo přejezdem startovní čáry
znovu (AC EVO, AC Rally), jak to dělá `kunos.py` pro záznamník kol.

#### Vše se ukládá {#everything-kept}

Řádků je několik za sekundu; hry posílají mnohem víc. Každý UDP paket, který
přijde – v menu, mezi koly, i ty, které žádný dekodér nečte – se uloží celý
do `heat.raw.parquet` relace pod svým formátem (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...). Každá stránka sdílené paměti
(celé mapování, ne jen dekódované bajty) se uloží pokaždé, když se změní, pod
názvem svého mapování (`acpmf_physics`, ...). `used` označuje, co se také stalo
řádky; `selfCheck.completeness` v `meta.json` počítá každý druh (pravidlo
převaděče 3DHeat).

Stejný modul slouží také: [Assetto Corsa Competizione (živá data)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (živá data)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (živá data)](game-assetto-corsa-rally.md), [BeamNG.drive (živá data)](game-beamng.md), [DiRT Rally 2.0 (živá data)](game-dirt-rally-2.md), [EA SPORTS WRC (živá data)](game-ea-wrc.md), [Forza Horizon 4 (živá data)](game-forza-horizon-4.md), [Forza Horizon 5 (živá data)](game-forza-horizon-5.md), [Forza Horizon 6 (živá data)](game-forza-horizon-6.md), [Forza Motorsport (živá data)](game-forza-motorsport.md), [Richard Burns Rally (živá data)](game-richard-burns-rally.md).

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

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v části „Co se zaznamenává“ jsou pojmenovány.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převaděče](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, které adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky) a `selfCheck.completeness` v `meta.json` počítá každý `type` – `lost` je 0.

**Načteno**

- řádky po 0,1 s z fyzikální stránky: pozice (průměr bodů dotyku pneumatik), rychlost, rychlostní stupeň, plyn, brzda, natočení, sklon a náklon (rad), otáčky, řízení (tak, jak je na stránce); začátek relace s tratí a autem ze statické stránky; kola, pořadí v závodě

**Uchováno surové**

- každá stránka celá – celá oblast mapování, ne jen dekódované bajty – pokaždé, když se změní její bajty, při čtení Watcheru každých 0,1 s: `acpmf_physics`, `acpmf_graphics`, `acpmf_static`; opětovné čtení, které je bajt po bajtu stejné jako to předchozí, se počítá v `unchanged_reads` v meta.json a neukládá se znovu
- vše dekódované jen pro soubory kol (`decoders/kunos.py`: skluz, zatížení, tlak, teploty, rozbíhání, zavěšení a body dotyku každého kola, teploty brzd, poměr a úhel skluzu; rychlost a úhlová rychlost ve světě i lokálně, pomůcky) je na těchto stránkách

**Nedostupné**

- pozice jiných aut: stránky popisují jen auto hráče (stránka grafiky ACC má u některých verzí id aut a souřadnice ostatních – uloženo v surové stránce, nedekódováno)
- fyzikální takty mezi čteními Watcheru: hra přepisuje stránku rychlostí své fyziky (až 333 Hz) a Watcher čte desetkrát za sekundu

**Velikost**: asi 150–300 MB za hodinu před komprimací (stránka 4 KB na každou stránku, až 10 změn za sekundu); stránky jsou většinou nuly a zstd z nich nechá malou část

## Ověřeno {#verified}

dekódování je z záznamníku kol gamecapture (testováno na syntetických stránkách); adaptér testován na sdílené paměti vytvořené v testu podle zdokumentovaného rozložení; netestováno proti hře

## Zdroj {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
