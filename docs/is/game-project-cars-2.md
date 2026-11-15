---
title: "Project CARS 2 (lifandi gögn)"
nav_order: 36
lang: "is"
source: game-project-cars-2.md
source_hash: "278eb9594615"
nav_exclude: true
search_exclude: true
---
# Project CARS 2 (lifandi gögn) {#project-cars-2-live-data}

Meðan þú spilar Project CARS 2 vistar watcher gögnin sem leikurinn sjálfur sendir út, svo þú getir skoðað þau síðar á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `project-cars-2`, gerð [`telemetry`](sources-and-rules.md); það keyrir meðan `pCARS2AVX.exe` eða `pCARS2.exe` er í gangi og leitar að nýjum gögnum á 0,1 s fresti.*

## Hvað er skráð {#what-is-recorded}

- staða sérhvers bíls (heims-XYZ, m) á 10 Hz eftir nafni ökumanns, eigin bíll merktur, með hraða og sæti í keppni; eigin gír, inngjöf, bremsa
- upphaf lotu með brautinni sem leikurinn nefnir; hringir á hvern bíl með hringtíma; mark; eigin viðgerðarstopp
- teleports (aftur í viðgerðarsvæðið, endurræsing): `teleport` þar sem bíllinn var, `spawn` þar sem hann er núna
- eigin hringir, besti hringur, sæti í keppni, vegalengd, hámarkshraði
- allt samnýtt minnisblað leiksins í `heat.raw.parquet`, í hvert sinn sem það breytist

## Hvaðan það kemur {#where-it-comes-from}

samnýtt minni $pcars2$ (SMS SharedMemory.h)

## Hvernig kveikt er á því {#how-to-switch-it-on}

Í leiknum: Options > System > Shared Memory: „Project CARS 2“

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

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

`SharedMemory.h` frá SMS (fylgir í möppunni Support\SharedMemory í leiknum;
AMS2: Options > System > Shared Memory „Project CARS 2“), `#pragma pack(4)`.
`mParticipantInfo[64]` frá bæti 28, 100 bæti hver: mIsActive, mName[64],
mWorldPosition[3] (m, Y upp), mCurrentLapDistance, mRacePosition,
mLapsCompleted, mCurrentLap, mCurrentSector; mViewedParticipantIndex (20)
er bíll spilarans; fyrir hvern þátttakanda mLastLapTimes (9200), mRaceStates
(9520), mSpeeds (10800); hjá spilaranum mBestLapTime (6716), mLastLapTime
(6720), mSpeed (6848), mBrake, mThrottle, mGear; mSequenceNumber (7320) er
oddatala meðan leikurinn skrifar. Staðsetningarnar voru unnar út frá tveimur
óháðum afritum af hausnum (eigið afrit leiksins er ekki uppsett
hér), sem stemma.

Báðar síðurnar eru auk þess geymdar heilar (docs/converters.md, „Live sources“): allt
varpið, hver lestur þar sem bætin eru frábrugðin síðasta geymda afriti, í
hráu hliðarskrá lotunnar undir `type` `r3e` eða `pcars2` - sérhver ökumannsrauf og
sérhver reitur byggingarinnar (struct), líka þeir sem eru ekki lesnir hér, svo síðari afkóðari
þarf aðeins hliðarskrána.

Sama eining þjónar líka: [Automobilista 2 (lifandi gögn)](game-automobilista-2.md), [RaceRoom Racing Experience (lifandi gögn)](game-raceroom.md).

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | já |
| Upp-ás | `y` |
| Einingar | metrar |
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

- fyrir hvern þátttakanda (allt að 64): virkur, nafn, heimsstaða, sæti í keppni, hringir lokið; síðasti hringtími hans, keppnisstaða og hraði
- bíll spilarans (mViewedParticipantIndex), leikja- og lotustaða, staðsetning og afbrigði brautar, besti og síðasti hringur, hraði, bremsa, inngjöf, gír; mSequenceNumber til að sleppa afriti sem náðist í miðri ritun
- staðsetningar úr tveimur óháðum afritum af SharedMemory.h frá SMS sem stemma, athugaðar á síðu sem er smíðuð úr þeim í prófunum; ekki enn á móti leiknum

**Geymt hrátt**

- `pcars2`: allt $pcars2$-varpið - byggingin (struct) nær langt umfram 11.312 bætin sem eru lesin hér - hver lestur þar sem bætin eru frábrugðin síðasta geymda afriti: stefna hvers þátttakanda, brautarhlutatímar, heiti bíla og flokka, viðgerðarhamir og fánar, eðlisfræði spilarans, hjólbarðar, fjöðrun, skemmdir, veður og allt sem síðari útgáfur Project CARS 2 bættu við
- `used` er satt fyrir síðu sem er lesin í raðir; ósatt fyrir síðu í valmyndum, í hléi, í endursýningu, af öðru útliti, eða sem náðist í miðri ritun (`torn` 1); `unchanged_reads` í meta.json telur lestrana sem voru bæti fyrir bæti eins og afritið sem var geymt áður

**Ekki fáanlegt**

- inntak og eðlisfræði annarra þátttakenda: síðan gefur aðeins bílinn sem er horft á
- allt meðan valkostur leiksins fyrir samnýtt minni er slökktur (Project CARS 2 skrifar þá ekkert)

**Stærð**: varpið er um 20 til 30 KB (eftir útgáfu leiksins), allt að 10 sinnum á sekúndu við akstur: nálægt 0,7 til 1,1 GB á klukkustund fyrir þjöppun; zstd minnkar tómar þátttakendarauf og óbreytileg nöfn í brot (ekki enn mælt í raunverulegri lotu)

## Staðfest {#verified}

prófað á síðu sem er smíðuð í prófinu; staðsetningar úr tveimur óháðum afritum af SharedMemory.h sem stemma, ekki úr afritinu sem leikurinn fylgir með; óprófað á móti leiknum

## Heimild {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
