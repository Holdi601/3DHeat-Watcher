---
title: "Forza Horizon 4 (živá data)"
nav_order: 21
lang: "cs"
source: game-forza-horizon-4.md
source_hash: "ac1890f4d62c"
nav_exclude: true
search_exclude: true
---
# Forza Horizon 4 (živá data) {#forza-horizon-4-live-data}

Když hrajete Forza Horizon 4, Watcher ukládá data, která hra sama posílá ven, abyste se na ně mohli později podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `forza-horizon-4`, druh [`telemetry`](sources-and-rules.md); běží, když je spuštěný `ForzaHorizon4.exe`, a hledá nová data každých 0,1 s.*

## Co se zaznamenává {#what-is-recorded}

- pozice vlastního auta (světové XYZ, m) každou 0,1 s spolu s rychlostí, rychlostním stupněm, plynem, brzdou a kolem
- začátek a konec relace (session_start/session_end), kola s časem kola z hry
- začátek a konec závodu s pořadím v závodě
- teleporty (přetáčení, rychlá cesta): `teleport` tam, kde auto bylo, `spawn` tam, kde je teď
- kola, nejlepší kolo, vzdálenost, nejvyšší rychlost, závody

## Odkud to pochází {#where-it-comes-from}

Forza Data Out, UDP 127.0.0.1:5300 (formát Dash); každý paket přeposlán beze změny na 127.0.0.1:5301

## Jak to zapnout {#how-to-switch-it-on}

Ve hře: Settings > HUD and Gameplay > Data Out On, IP 127.0.0.1, port 5300 (Motorsport: formát Dash). FH Companion nebo jiná aplikace Data Out: nastavte její port na 5301 – Watcher přepošle každý paket; dokud jiná aplikace poslouchá na 5300, Watcher jí port nechá a nic nezaznamená

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

#### Vše se ukládá {#everything-kept}

Řádků je několik za sekundu; hry posílají mnohem víc. Každý UDP paket, který
přijde – v menu, mezi koly, i ty, které žádný dekodér nečte – se uloží celý
do `heat.raw.parquet` relace pod svým formátem (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...). Každá stránka sdílené paměti
(celé mapování, ne jen dekódované bajty) se uloží pokaždé, když se změní, pod
názvem svého mapování (`acpmf_physics`, ...). `used` označuje, co se také stalo
řádky; `selfCheck.completeness` v `meta.json` počítá každý druh (pravidlo
převaděče 3DHeat).

Stejný modul slouží také: [Assetto Corsa (živá data)](game-assetto-corsa.md), [Assetto Corsa Competizione (živá data)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (živá data)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (živá data)](game-assetto-corsa-rally.md), [BeamNG.drive (živá data)](game-beamng.md), [DiRT Rally 2.0 (živá data)](game-dirt-rally-2.md), [EA SPORTS WRC (živá data)](game-ea-wrc.md), [Forza Horizon 5 (živá data)](game-forza-horizon-5.md), [Forza Horizon 6 (živá data)](game-forza-horizon-6.md), [Forza Motorsport (živá data)](game-forza-motorsport.md), [Richard Burns Rally (živá data)](game-richard-burns-rally.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `y` |
| Jednotky | metry; světový rámec Forzy je levoruký, kreslí se tak, jak přichází, jako to dělá záznamník kol |
| Zrcadleno pro prohlížeč | žádné |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto údaje se zapíšou do `meta.json` každé relace (`axes`) a, pokud má relace pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítko řádků nastavuje sám – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukazuje jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `telemetry`: čte jen to, co hra nebo platforma vydává (UDP port nebo sdílená paměť, kterou hra zveřejňuje), takže zaznamenává i v online hře, nejen offline; příznak rozhoduje jen o tom, zda se paměť smí vůbec číst.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry typu `memory` a nikdy u hry označené jako hraná online – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (u každé relace `stats` v `meta.json` a v tabulce `stats` souboru `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `races`, `top_speed_kmh`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v části „Co se zaznamenává“ jsou pojmenovány.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převaděče](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, které adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky) a `selfCheck.completeness` v `meta.json` počítá každý `type` – `lost` je 0.

**Načteno**

- řádky po 0,1 s: pozice, rychlost, rychlostní stupeň, plyn, brzda, kolo, natočení, sklon a náklon (rad), otáčky, řízení (-1 až 1); začátek relace s pořadovým číslem auta, třídou, PI a pohonem; kola s časem kola z hry; pořadí v závodě

**Uchováno surové**

- každý paket, který dorazí na port, celý, rychlostí hry (jeden na každý tik simulace), pod svým formátem: `dash-horizon` (324 bajtů, Forza Horizon), `dash` (311, Motorsport 7), `dash-fm2023` (331, Forza Motorsport 2023: opotřebení pneumatik a id tratě), `sled` (232, bez pozice), `<n>-byte` pro cokoli jiného – včetně paketů z menu (isRaceOn 0), paketů držených, dokud se nepotvrdí rozložení dash, a ~13 bajtů paketu Horizon, které žádný zveřejněný popis nepojmenovává
- každý kanál kola bloku Sled (poměr skluzu, úhel skluzu, kombinovaný skluz, zavěšení, rychlost kola, rumble, louže), zrychlení, úhlová rychlost, výkon, točivý moment, boost, palivo, teploty pneumatik, spojka, ruční brzda, jízdní linie, rozdíl brzdění AI: vše je v paketech, dekódováno `decoders/fulllap.decode_full` z nich

**Nedostupné**

- jiná auta: Data Out popisuje jen auto hráče
- název tratě nebo trasy: Forza Horizon ho nikdy neposílá; Motorsport 2023 posílá jen číslo tratě
- pakety, zatímco jiná aplikace (FH Companion) drží UDP 5300: Watcher port nechá jí

**Velikost**: asi 85 MB za hodinu před komprimací (60 paketů za sekundu po 324 bajtech plus 70bajtová hlavička položky); po sobě jdoucí pakety se příliš neliší, takže zstd z toho nechá zlomek

## Ověřeno {#verified}

dekódování je z záznamníku kol gamecapture (testováno na paketech sestavených z rozložení Data Out); adaptér testován na syntetických paketech a na zaznamenaných trajektoriích kol přehrávaných jako pakety; netestováno proti samotné hře

## Zdroj {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
