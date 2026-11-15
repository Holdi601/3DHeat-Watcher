---
title: "X-Plane (lifandi gögn)"
nav_order: 49
lang: "is"
source: game-xplane.md
source_hash: "be1c5b21d2ef"
nav_exclude: true
search_exclude: true
---
# X-Plane (lifandi gögn) {#x-plane-live-data}

Meðan þú spilar X-Plane vistar watcher gögnin sem leikurinn sjálfur sendir út, svo þú getir skoðað þau síðar á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `xplane`, gerð [`telemetry`](sources-and-rules.md); það keyrir meðan `X-Plane.exe` er í gangi og leitar að nýjum gögnum á 0,1 s fresti.*

## Hvað er skráð {#what-is-recorded}

- eigin staða á 10 Hz (breiddargráða/lengdargráða/hæð sem metrar austur/upp/norður frá fyrstu staðsetningu; lat/lon/alt geymt sem dálkar)
- afstaða (attitude), sýndur og sannur flughraði, hraði yfir jörð, Mach, lóðréttur hraði, AoA, hliðarsvif, segulstefna, AGL, g (lóðrétt, ás, hlið), hraði og snúningshraði, vængbörð, loftbremsa, inngjöf, á jörðu
- þyngdir (heildar, eldsneyti, farmur), lendingarbúnaðarhandfang, sjálfstýring, snúningar hreyfils á mínútu og N1, tími og dagsetning hermis, bið, hraði hermis, endursýning, útihitastig og loftþrýstingur við sjávarmál (X-Plane 12) einu sinni á sekúndu
- flugtök, lendingar, brotlendingar, endurstilling flugs (session_start/session_end fyrir hvert flug)
- flugtími, tími í lofti, vegalengd, mesta hæð, mesta g, lendingar
- sérhvert svar sem X-Plane sendir geymt heilt í heat.raw.parquet

## Hvaðan það kemur {#where-it-comes-from}

UDP-viðmót X-Plane á 127.0.0.1:49000 (RREF-datarefs og RPOS-staða, svarað til watcher)

## Hvernig kveikt er á því {#how-to-switch-it-on}

X-Plane 12: Settings > Network > Accept incoming connections (X-Plane 11 svarar sjálfgefið)

## Hvernig það virkar {#how-it-works}

X-Plane 11 og 12: eigið UDP-viðmót hermisins á gátt 49000.

X-Plane svarar hverjum sem spyr á 127.0.0.1:49000, á tíðninni sem er beðið um, til
vistfangsins og gáttarinnar sem beiðnin kom frá (skjalið „Exchanging Data with
X-Plane“ frá X-Plane, sem fylgir í `<X-Plane>\Instructions\`):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

RPOS gefur breiddargráðu og lengdargráðu sem tvöfaldar tölur (RREF aðeins sem fleytitölur, hálfum metra
frá hvor annarri), svo hún ræður stöðunni; RREF færir restina og hleypur í skarðið þegar
RPOS kemur ekki. Datarefs (nöfn eins og í `Resources\plugins\DataRefs.txt` í X-Plane 12,
<https://developer.x-plane.com/datarefs/>):

```text
sim/flightmodel/position/latitude, longitude, elevation  deg, deg, m MSL
sim/flightmodel/position/true_theta, true_phi, true_psi  pitch, roll, true heading (deg)
sim/flightmodel/position/indicated_airspeed              knots
sim/flightmodel/position/groundspeed                     m/s
sim/flightmodel/position/y_agl                           m above ground
sim/flightmodel/forces/g_nrml                            g, normal to the wings
sim/flightmodel/failures/onground_any                    1 on the ground
sim/flightmodel2/misc/has_crashed                        1 crashed
sim/time/total_flight_time_sec                           since the flight was reset
```

og restin af fluginu á sömu tíðni (sannur flughraði, lóðréttur hraði, AoA,
hliðarsvif, segulstefna, Mach, g eftir ás og hlið, snúningshraði, vængbörð,
loftbremsa, inngjöf: `DATAREFS`), með hægara ástandi flugvélarinnar einu sinni á
sekúndu (þyngdir, lendingarbúnaðarhandfang, sjálfstýring, hreyflar, tími hermis, bið og
hraði, veður: `SLOW_DATAREFS`). Sérhver gagnapakki er líka geymdur heill í
hráu hliðarskrá lotunnar, og meta.json nefnir datarefið á bak við hverja RREF-vísitölu.

X-Plane 12 tekur við þessu aðeins með Settings > Network > „Accept incoming
connections“ á. Stöður fara í flatt kort umhverfis fyrstu staðsetningu setunnar
(`Tangent`): x austur, z norður í metrum, y hæðin yfir sjávarmáli - svo
láréttur flugferill helst láréttur hversu langt sem hann fer, sem sannur snertiflötur myndi
beygja niður með jörðinni. Upphafspunktur kortsins er `geo` lotunnar: meta.json
og fótur töflunnar bera hann, svo skoðarinn geti lagt raunverulegan heim undir
flugið.

Þessi eining geymir líka það sem hinir flughermarnir deila: flata kortið,
bókhald flugsins (flugtök, lendingar, brotlendingar, vegalengd), UDP-tengið og
lista Steam-bókasafnsins.

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | já |
| Upp-ás | `y` |
| Einingar | metrar (austur, hæð, norður frá fyrstu staðsetningu) |
| Speglað fyrir skoðarann | `z` |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` hverrar lotu (`axes`) og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **nei**. `games --markdown` sýnir þetta sem „single-player“.
- Gerð `telemetry`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (UDP-gátt eða samnýtt minni sem leikurinn birtir), svo það skráir bæði í spilun á netinu og án nets; flaggið ræður aðeins því hvort minni megi nokkurn tíma vera lesið.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur sem spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Lykill innan slaufusviga er fylltur út á keyrslutíma (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; „Hvað er skráð“ hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [umbreytingarreglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er sérhver pakki, síða, lína eða svar sem millistykkið tekur við geymt heilt í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, og svo hver reitur sem er geymdur með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hverja `type` - `lost` er 0.

**Lesið**

- RPOS (10 Hz): lengdargráða, breiddargráða, hæð, AGL, pitch, sönn stefna, roll, hraði (austur, upp, suður) og snúningshraði P/Q/R - allt á röðunum
- RREF (10 Hz): 27 datarefs `DATAREFS` - staða, afstaða, IAS, hraði yfir jörð, TAS, lóðréttur hraði, AoA, hliðarsvif, segulstefna, Mach, g lóðrétt/ás/hlið, snúningshraði, vængbörð, loftbremsa, inngjöf, AGL, brotlent, á jörðu, flugtími - á röðunum
- RREF (1 Hz): 20 datarefs `SLOW_DATAREFS` - þyngdir, lendingarbúnaðarhandfang, sjálfstýringarservó, tími og dagsetning hermis, bið, hraði hermis, endursýning, fjöldi hreyfla, snúningar á mínútu hreyfla 1-4, N1 hreyfla 1-2, hitastig útilofts, loftþrýstingur við sjávarmál - á röðunum eins og síðast var móttekið

**Geymt hrátt**

- sérhver gagnapakki heill sem `payload`, undir fjögurra stafa hausnum: `RREF` og `RPOS` (`used` þegar könnunin bjó til röð; í valmyndum, án staðsetningar, búa þeir til enga), allt annað sem X-Plane sendir í gátt watcher undir eigin haus eða `unknown`; `requests` í meta.json segir hvaða dataref hver RREF-vísitala er, svo hægt sé að lesa farmana án þessarar einingar

**Ekki fáanlegt**

- sérhvert annað dataref (X-Plane hefur þúsundir): RREF sendir aðeins það sem er beðið um, ein áskrift hvert; listinn biður um flugið, ástand flugvélarinnar og tíma hermisins - meiri smáatriði í stjórnklefa (talstöðvar, ljós, mælar hvers hreyfils, bilanir) myndu margfalda beiðnirnar
- nafn flugvélarinnar og ICAO-gerð: bætafylkis-datarefs, sem RREF sendir eina fleytitölu fyrir hvern staf
- aðrar flugvélar (gervigreind og fjölspilun): sim/multiplayer/position-datarefs ekki beðin um
- DATA-úttakið (Settings > Data Output): það sendir á fast vistfang sem er valið í hermininum, ekki til þess sem spyr; RREF og RPOS ná yfir það sem watcher les

**Stærð**: um 17 MB á klukkustund fyrir zstd (RREF og RPOS á 10 Hz, um 220 og 70 bæti auk ramma hvort, hægari RREF einu sinni á sekúndu), ef X-Plane sendir gildi hverrar könnunar í einum pakka eins og það gerir; zstd minnkar fleytitölurnar nokkrum sinnum

## Staðfest {#verified}

prófað á fölskum X-Plane sem svarar RREF/RPOS samkvæmt „Exchanging Data with X-Plane“ í X-Plane 12; nöfn datarefs athuguð gegn DataRefs.txt í X-Plane 12; óprófað á móti hermininum í gangi

## Heimild {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
