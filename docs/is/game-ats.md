---
title: "American Truck Simulator (lifandi gögn)"
nav_order: 1
lang: "is"
source: game-ats.md
source_hash: "974252b355da"
nav_exclude: true
search_exclude: true
---
# American Truck Simulator (lifandi gögn) {#american-truck-simulator-live-data}

Meðan þú spilar American Truck Simulator vistar watcher gögnin sem leikurinn sjálfur sendir út, svo þú getir skoðað þau síðar á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `ats`, gerð [`telemetry`](sources-and-rules.md); það keyrir meðan `amtrucks.exe` er í gangi og leitar að nýjum gögnum á 0,1 s fresti.*

## Hvað er skráð {#what-is-recorded}

- heimsstaða vörubílsins (x austur, y upp, z suður, m) á 10 Hz meðan hann hreyfist, á 5 s fresti meðan hann stendur kyrr; stefna, hraði, kílómetramælir
- verk hafin (farmur, frá, til), afhent (tekjur, XP, km), afturkölluð; sektir, vegatollar, ferjur, lestir, áfylling eldsneytis
- ferjur, lestir og hlaðnar vistanir rjúfa leiðina (teleport, spawn)
- vegalengd, hámarkshraði, afhendingar, tekjur, XP, sektir
- allt samnýtta minni viðbótarinnar í `heat.raw.parquet`, í hvert sinn sem það breytist

## Hvaðan það kemur {#where-it-comes-from}

samnýtt minni Local\SCSTelemetry sem RenCloud scs-sdk-plugin (útgáfa 12) skrifar í &lt;game>\bin\win_x64\plugins

## Hvernig kveikt er á því {#how-to-switch-it-on}

settu scs-telemetry.dll (útgáfa 12) frá github.com/RenCloud/scs-sdk-plugin í &lt;game>\bin\win_x64\plugins; leikurinn spyr einu sinni við hverja ræsingu hvort leyfa eigi SDK

## Hvernig það virkar {#how-it-works}

Euro Truck Simulator 2 og American Truck Simulator: fjarmælinga-SDK SCS, í gegnum RenCloud-viðbótina.

SCS birtir fjarmælinga-SDK (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>)
fyrir viðbætur sem spilarinn setur í `<game>\bin\win_x64\plugins\`. Leikurinn sjálfur
birtir ekkert; mikið notaða viðbótin frá <https://github.com/RenCloud/scs-sdk-plugin>
(MIT) afritar rásir SDK í samnýtt minni `Local\SCSTelemetry`
(32 KiB), sem er sett upp í `scs-telemetry/inc/scs-telemetry-common.hpp`. Þetta les
útgáfu 12 af þessu útliti (PLUGIN_REVID 12) og ekkert annað: viðbótin
skrifar útgáfu sína á stað 40, og öll önnur útgáfa er látin ólesin frekar en að
vera misskilin. Staðsetningar sem eru notaðar (svæði eins og hausinn merkir þau; náttúruleg jöfnun):

```text
   0  bool sdkActive          4  bool paused
  40  u32  telemetry_plugin_revision, version_major, version_minor, game (1 ETS2, 2 ATS)
  64  u32  common_ui.time_abs (in-game minutes)
 504  i32  truck_i.gear
 640  i32  gameplay_i.jobDeliveredEarnedXp
 948  f32  truck_f.speed (m/s); 952 engineRpm; 1056 truckOdometer (km)
1460  f32  gameplay_f.jobDeliveredDistanceKm
2200  f64  truck_dp.coordinateX/Y/Z (m), rotationX/Y/Z (heading, pitch, roll in turns, 0..1)
2300  char[64] config_s: truckBrand +64, truckName +192, cargo +320, cityDst +448, compDst +576,
      citySrc +704, compSrc +832; 3436 gameplay_s.fineOffence[32]
4200  i64  gameplay_ll: jobCancelledPenalty, jobDeliveredRevenue, fineAmount, tollgatePayAmount,
      ferryPayAmount, trainPayAmount
4300  bool special_b: onJob, jobFinished, jobCancelled, jobDelivered, fined, tollgate, ferry,
      train, refuel, refuelPayed
```

Heimsstaða vörubílsins er heimsrammi SCS: x austur, y upp, z suður, metrar
(hægrihandar, y upp - skoðarinn teiknar það eins og það er). Ferjur, lestir og hleðsla
á vistun færa vörubílinn án þess að ekið sé: leiðin er rofin þar.

Allt varpið (32 KiB viðbótarinnar: öll svæðin hér að ofan og þau sem eru ekki
lesin - uppsetning vörubílsins, hjól, slit, aðrar rásir vörubílsins, og
það sem útgáfan leggur út eftir bæti 4400, tengivagnarnir) er geymt í hráu hliðarskrá lotunnar í hvert sinn sem það breytist,
`type` `SCSTelemetry` með `revision` við hliðina - líka síða af annarri
útgáfu, sem er geymd heil frekar en að vera misskilin.

Sama eining þjónar líka: [Euro Truck Simulator 2 (lifandi gögn)](game-ets2.md).

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | já |
| Upp-ás | `y` |
| Einingar | metrar (heimur SCS: x austur, y upp, z suður) |
| Speglað fyrir skoðarann | ekkert |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` hverrar lotu (`axes`) og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem „allowed (reads only what the game publishes)“.
- Gerð `telemetry`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (UDP-gátt eða samnýtt minni sem leikurinn birtir), svo það skráir bæði í spilun á netinu og án nets; flaggið ræður aðeins því hvort minni megi nokkurn tíma vera lesið.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur sem spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

Lykill innan slaufusviga er fylltur út á keyrslutíma (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; „Hvað er skráð“ hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [umbreytingarreglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er sérhver pakki, síða, lína eða svar sem millistykkið tekur við geymt heilt í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, og svo hver reitur sem er geymdur með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hverja `type` - `lost` er 0.

**Lesið**

- SDK- og hléstaða, útgáfa viðbótar, leikur og útgáfa, tími í leiknum, heimsstaða og stefna vörubílsins, hraði, kílómetramælir, tegund og heiti vörubíls, farmur, borg og fyrirtæki upphafs og áfangastaðar, tekjur verks, XP og vegalengd, afturköllunarsekt, sektir og brot þeirra, vegatollar, ferjur, lestir, sérstöku atburðafánarnir (raðir, atburðir og tölfræði)
- nú líka á stöðuröðunum: `pitch` og `roll` (gráður, úr snúningum SDK), `gear` og `rpm`
- staðsetningar athugaðar á móti afritun, reit fyrir reit, á haus útgáfu 12 af viðbótinni þar sem upphaf svæða er staðfest í prófunum; ekki enn á móti leiknum

**Geymt hrátt**

- `SCSTelemetry`: allt 32 KiB varp viðbótarinnar, hver lestur þar sem bætin eru frábrugðin síðasta geymda afriti (`unchanged_reads` í meta.json telur hina), `revision` við hliðina: öll svæði - uppsetning vörubíls og tengivagns, rásir vörubílsins (pedalar, stýri, eldsneyti, AdBlue, þrýstingur, hitastig, slit, ljós, hjól), staðsetningar- og hröðunarvigrar, strengir verks og spilunar, og allt sem útgáfan leggur út eftir bæti 4400 (tengivagnarnir); `used` er satt meðan SDK er virkt og útgáfan er 12
- síða af annarri útgáfu viðbótarinnar er geymd heil með `used` ósatt í stað þess að vera misskilin

**Ekki fáanlegt**

- allt sem viðbótin afritar ekki úr SDK, og allt meðan viðbótin er ekki uppsett: leikurinn birtir enga fjarmælingu sjálfur
- vörubílar annarra spilara í TruckersMP eða lestum vörubíla: SDK gefur aðeins vörubíl spilarans sjálfs

**Stærð**: 32 KiB allt að 10 sinnum á sekúndu við akstur (hver lestur er þá frábrugðinn): um 1,2 GB á klukkustund fyrir þjöppun, eitt afrit meðan hlé er; mest af síðunni eru núll og uppsetning sem breytist ekki, svo zstd minnkar hana mörgum sinnum (ekki enn mælt í raunverulegri lotu)

## Staðfest {#verified}

prófað á samnýttu minni sem er smíðað eftir haus útgáfu 12 af viðbótinni; óprófað á móti leiknum

## Heimild {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
