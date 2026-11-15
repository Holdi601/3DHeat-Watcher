---
title: "RaceRoom Racing Experience (lifandi gögn)"
nav_order: 37
lang: "is"
source: game-raceroom.md
source_hash: "f3879cd40a67"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (lifandi gögn) {#raceroom-racing-experience-live-data}

Meðan þú spilar RaceRoom Racing Experience vistar watcher gögnin sem leikurinn sjálfur sendir út, svo þú getir skoðað þau síðar á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `raceroom`, gerð [`telemetry`](sources-and-rules.md); það keyrir meðan `RRRE64.exe` eða `RRRE.exe` er í gangi og leitar að nýjum gögnum á 0,1 s fresti.*

## Hvað er skráð {#what-is-recorded}

- staða sérhvers bíls (heims-XYZ, m) á 10 Hz eftir nafni ökumanns, eigin bíll merktur, með hraða og sæti í keppni; eigin gír, inngjöf, bremsa
- upphaf lotu með brautinni sem leikurinn nefnir; hringir á hvern bíl með hringtíma; mark; eigin viðgerðarstopp
- teleports (aftur í viðgerðarsvæðið, endurræsing): `teleport` þar sem bíllinn var, `spawn` þar sem hann er núna
- eigin hringir, besti hringur, sæti í keppni, vegalengd, hámarkshraði
- allt samnýtt minnisblað leiksins í `heat.raw.parquet`, í hvert sinn sem það breytist
- eigin refsistig vegna atvika

## Hvaðan það kemur {#where-it-comes-from}

samnýtt minni $R3E (r3e.h frá Sector3, útgáfa 3)

## Hvernig kveikt er á því {#how-to-switch-it-on}

Ekki þarf að kveikja á neinu: watcher les heimildina eins og leikurinn eða vettvangurinn lætur hana í té.

## Hvernig það virkar {#how-it-works}

Samnýtt minni sem kappakstursleikir birta fyrir mælaborð, opnað skrifvarið - og
aldrei búið til.

Nokkrir hermar láta fjarmælingu sína í té sem nafngreint Windows-skráarvarp sem
leikurinn býr til og hver sem er má lesa: síður Kunos `Local\acpmf_*` (Assetto Corsa,
ACC, AC Rally, `Local\acevo_pmf_*` hjá AC EVO), `Local\IRSDKMemMapFileName` hjá iRacing,
`$R3E` hjá RaceRoom, `$pcars2$` hjá Automobilista 2 / Project CARS 2.

Hvers vegna ekki `mmap.mmap(-1, size, tagname=...)`, sem er venjulega leiðin í Python: þegar
varpið er ekki til enn *býr það til* eitt - hér skrifvarið. Leikur
sem er ræstur eftir það opnar varp watcher í stað þess að búa til sitt eigið og
getur þá ekki skrifað í það, svo fjarmæling hans er dauð þar til watcher sleppir.
Watcher ræsir millistykki um leið og ferli leiksins birtist, sem er
einmitt augnablikið þegar leikurinn hefur ekki enn búið til varp sitt. Þess vegna opnar þetta með
`OpenFileMappingW`, sem finnur aðeins varp sem er þegar til, varpar því með
`FILE_MAP_READ`, og tilkynnir „ekki til enn“ annars; millistykkin reyna aftur
augnabliki síðar.

Ekkert hér getur skrifað: sýnin er varpað skrifvarið og er aðeins afrituð
út með `ctypes.string_at`.

Tveir leikir eru líka lesnir hér; sérhver bíll á brautinni er í síðum þeirra.

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

`r3e.h` frá Sector3 (github.com/sector3studios/r3e-api, sample-c/src/r3e.h,
útgáfa 3.6), `#pragma pack(1)`. Hausinn segir hvar ökumennirnir byrja
og hversu stór einn er (`all_drivers_offset`, `driver_data_size`), svo
hluti hvers ökumanns - nafn, rauf, sæti, heimsstaða (float x y z, m),
hringir lokið, núverandi hringtími, lokastaða, viðgerðarbraut, hraði - er lesinn
eftir því. Eigin reitir spilarans (besti og fyrri hringur, sæti í keppni,
refsistig vegna atvika, gír, pedalar, heiti brautar og uppsetningar) eru lesnir á
3.6-staðsetningum sínum aðeins þegar `all_drivers_offset` er 2008, eins og þetta útlit
setur hann. Y er tekið sem upp; hausinn segir það ekki.

Sama eining þjónar líka: [Automobilista 2 (lifandi gögn)](game-automobilista-2.md), [Project CARS 2 (lifandi gögn)](game-project-cars-2.md).

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | já |
| Upp-ás | `y` |
| Einingar | metrar; Y upp gert ráð fyrir (r3e.h segir það ekki) |
| Speglað fyrir skoðarann | ekkert |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` hverrar lotu (`axes`) og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem „allowed (reads only what the game publishes)“.
- Gerð `telemetry`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (UDP-gátt eða samnýtt minni sem leikurinn birtir), svo það skráir bæði í spilun á netinu og án nets; flaggið ræður aðeins því hvort minni megi nokkurn tíma vera lesið.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur sem spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

Lykill innan slaufusviga er fylltur út á keyrslutíma (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; „Hvað er skráð“ hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [umbreytingarreglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er sérhver pakki, síða, lína eða svar sem millistykkið tekur við geymt heilt í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, og svo hver reitur sem er geymdur með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hverja `type` - `lost` er 0.

**Lesið**

- fyrir hverja ökumannsrauf (eftir eigin staðsetningu og stærð haussins): nafn, rauf, lokastaða, sæti, heimsstaða, hringir lokið, núverandi hringtími, viðgerðarbraut, hraði
- eigin reitir spilarans, aðeins þegar síðan er r3e.h 3.6-útlitið: heiti brautar og uppsetningar, tegund lotu, sæti í keppni, besti og fyrri hringur, refsistig vegna atvika, gír, inngjöf, bremsa, rauf spilarans
- staðsetningar unnar úr r3e.h 3.6 frá Sector3 og athugaðar á síðu sem er smíðuð úr því í prófunum; ekki enn á móti leiknum

**Geymt hrátt**

- `r3e`: allt $R3E-varpið, hver lestur þar sem bætin eru frábrugðin síðasta geymda afriti - sérhver reitur r3e.h: eðlisfræði spilarans (stefna, hraðar, hröðun, g-kraftar), vél, eldsneyti, hjólbarðar, bremsur, skemmdir, fánar, viðgerðarvalmynd, brautarhlutatímar, öll ökumannsgögn hverrar raufar (flokkur, gerð, lið, brautarhlutatímar, bil, refsingar, hjólbarðar)
- `used` er satt fyrir síðu sem er lesin í raðir; ósatt fyrir síðu í valmyndum, í hléi, í endursýningu, af öðru útliti, eða sem náðist í miðri ritun (`torn` 1); `unchanged_reads` í meta.json telur lestrana sem voru bæti fyrir bæti eins og afritið sem var geymt áður

**Ekki fáanlegt**

- inntak og eðlisfræði annarra ökumanna: síðan gefur aðeins spilarann sjálfan
- nákvæmir hringtímar annarra bíla: rauf hefur aðeins hringtímann sem er í gangi, svo hringur er síðasti tíminn sem sást (um það bil 0,1 s)
- eigin reitir spilarans á öðru útliti en 3.6: geymdir hráir, ekki lesnir, þar til þeir eru athugaðir

**Stærð**: síðan er 44 KB (r3e.h 3.6; varpið er rúnnað upp í heilar 4 KB síður), allt að 10 sinnum á sekúndu við akstur: um 1,6 GB á klukkustund fyrir þjöppun; tómar ökumannsrauf og óbreytilegir reitir þjappast mjög vel með zstd (ekki enn mælt í raunverulegri lotu)

## Staðfest {#verified}

prófað á síðu sem er smíðuð í prófinu úr r3e.h 3.6 (staðsetningar unnar úr opinbera hausnum); óprófað á móti leiknum; hringtímar annarra bíla eru síðasti hringtíminn í gangi sem sást (um það bil 0,1 s)

## Heimild {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
