---
title: "iRacing (lifandi gögn)"
nav_order: 28
lang: "is"
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (lifandi gögn) {#iracing-live-data}

Meðan þú spilar iRacing vistar watcher gögnin sem leikurinn sjálfur sendir út, svo þú getir skoðað þau síðar sem tölfræði og tímalínu.

*Tæknilegar upplýsingar: millistykki `iracing`, gerð [`telemetry`](sources-and-rules.md); það keyrir meðan `iRacingSim64DX11.exe` eða `iRacingSim64.exe` er í gangi og leitar að nýjum gögnum á 0,1 s fresti.*

## Hvað er skráð {#what-is-recorded}

- aksturinn á 5 Hz án stöðu (iRacing gefur enga í beinni): hraði, gír, inngjöf, bremsa, hringur, hlutfall hringsins, sæti í keppni og flokki, atvik
- upphaf lotu, að fara inn í og út úr bílnum, viðgerðarbraut inn og út, hringir með hringtíma, atvik með stigum þeirra, köflótti fáninn, lok
- .ibt-fjarmælingarskrárnar sem eru skrifaðar í setunni (breiddargráða, lengdargráða, hæð - skoðarinn les þær)
- hringir, besti hringur, atvik, sæti í keppni, viðgerðarstopp, vegalengd, hámarkshraði
- allt samnýtta minnið í `heat.raw.parquet`: haus, breytuhausar, upplýsingar um lotu, sérhver fjarmælingarlína sem er lesin

## Hvaðan það kemur {#where-it-comes-from}

samnýtt minni Local\IRSDKMemMapFileName (iRacing SDK); .ibt-skrár í %USERPROFILE%\Documents\iRacing\telemetry

## Hvernig kveikt er á því {#how-to-switch-it-on}

Ekkert fyrir lifandi gögnin. Fyrir stöður: skráðu fjarmælingu í bílnum (Alt+L) eða stilltu irsdkLog=1 í app.ini

## Hvernig það virkar {#how-it-works}

iRacing, í beinni: samnýtt minni iRacing SDK, lesið beint.

iRacing birtir fjarmælingu sína fyrir forrit í nafngreindu skráarvarpi,
`Local\IRSDKMemMapFileName`, sem herminn býr til meðan hann keyrir (og gefur merki með
`Local\IRSDKDataValidEvent` við hverja uppfærslu, sem þarf ekki hér:
watcher lítur tíu sinnum á sekúndu). Útlitið er `irsdk_defines.h` frá SDK,
sem pyirsdk (MIT) fylgir líka - skrifað aftur hér út frá þeim staðreyndum:

```text
irsdk_header (little-endian int32s)
    0 ver, 4 status (bit 0: connected), 8 tickRate,
    12 sessionInfoUpdate, 16 sessionInfoLen, 20 sessionInfoOffset,
    24 numVars, 28 varHeaderOffset, 32 numBuf, 36 bufLen, 40 pad[2],
    48 varBuf[4]: { tickCount, bufOffset, pad[2] } (16 bytes each)
irsdk_varHeader (144 bytes, numVars of them at varHeaderOffset)
    0 type (0 char, 1 bool, 2 int, 3 bitfield, 4 float, 5 double),
    4 offset (into a line), 8 count, 12 countAsTime + 3 pad,
    16 name[32], 48 desc[64], 112 unit[32]
session info: YAML text at sessionInfoOffset, rewritten when
    sessionInfoUpdate changes (track, sessions, drivers)
```

Herminn skrifar `numBuf` línur til skiptis; sú nýjasta er sú með
hæsta tickCount, og lína er tekin aftur ef tickCount hennar færðist meðan
verið var að afrita hana.

Lifandi gögn hafa enga heimsstöðu - breiddargráða, lengdargráða og hæð eru aðeins í
`.ibt`-skránum sem iRacing skráir í `Documents\iRacing\telemetry` (Alt+L í
bílnum, eða `irsdkLog=1`), sem 3DHeat-skoðarinn les sjálfur. Þetta skráir því
aksturinn sem atburði án hnita - hraða, hring, hlutfall hringsins sem er lokið, sæti í
keppni, atvik - auk hringja, atvika, viðgerðarstoppa og
köflótta fánans, og í lokin `.ibt`-skrárnar sem voru skrifaðar í setunni sem
`telemetry_file`-atburði, svo skoðarinn geti opnað þær.

Við hlið raðanna er allt minniskortið geymt, í hráu hliðarskrá lotunnar
(`heat.raw.parquet`): fasti hluti hausins (`header`, í hvert sinn sem hann
breytist), breytuhausarnir (`var_headers`, heilir, og sem JSON í `text`,
í hvert sinn sem útlitið breytist), YAML upplýsinga um lotu (`session_info`, texti þess í hvert sinn sem
`sessionInfoUpdate` hreyfist) og nýjasta fjarmælingarlínan
(`telemetry`, sérhver breyta hennar, í hverjum lestri sem finnur nýtt tikk). Breytuhausarnir
og ein lína eru allt sem síðari afkóðari þarf til að lesa hvaða breytu sem er.

Heimild: iRacing SDK (irsdk_defines.h, skjölun „iRacing SDK“ á spjallborðinu);
kutu/pyirsdk (MIT) til staðfestingar á frávikunum.

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | nei |
| Upp-ás | `y` |
| Einingar | engar stöður í beinni; .ibt-skrárnar bera breiddargráðu/lengdargráðu/hæð |
| Speglað fyrir skoðarann | ekkert |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` hverrar lotu (`axes`) og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem „allowed (reads only what the game publishes)“.
- Gerð `telemetry`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (UDP-gátt eða samnýtt minni sem leikurinn birtir), svo það skráir bæði í spilun á netinu og án nets; flaggið ræður aðeins því hvort minni megi nokkurn tíma vera lesið.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur sem spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

Lykill innan slaufusviga er fylltur út á keyrslutíma (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; „Hvað er skráð“ hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [umbreytingarreglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er sérhver pakki, síða, lína eða svar sem millistykkið tekur við geymt heilt í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, og svo hver reitur sem er geymdur með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hverja `type` - `lost` er 0.

**Lesið**

- úr nýjustu fjarmælingarlínunni: tími lotu, númer, ástand og auðkenni, á braut, endursýning, hringur, hringir lokið, hlutfall og metrar hringsins, síðasti og besti hringur, hraði, gír, inngjöf, bremsa, snúningar á mínútu, viðgerðarbraut, yfirborð brautar, sæti í keppni og flokki, eigin fjöldi atvika (`driving`-raðirnar á 5 Hz og atburðirnir)
- nú líka á `driving`-röðunum: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (gráður, úr radíönum hermisins - aðeins þegar breytuhausinn gefur eininguna sem rad), `fuel_l` (eining l), `lat_accel` og `lon_accel` (eining m/s^2)
- úr YAML upplýsinga um lotu: vísitala bíls spilarans, braut og uppsetning, gerðir lotna, nafn, bíll, lið og númer hvers ökumanns (session_start-raðir, meta.json)
- borið saman í prófunum við blokk sem er smíðuð úr irsdk_defines.h; ekki enn við herminn

**Geymt hrátt**

- `telemetry`: nýjasta línan heil, sérhver breyta sem herminn birtir (CarIdx-fylkin fyrir alla bíla, hjólbarðar, fjöðrun, hátíðni-`_ST`-fylkin þar sem herminn hefur þau ...), í hverjum lestri sem finnur nýtt tikk; `tick` er tikkteljari hermisins; `used` er ósatt meðan endursýning spilar
- `var_headers`: breytuhausarnir heilir (144 bæti hver) og, í `text`, sem JSON (name, type, offset, count, unit, description), í hvert sinn sem útlitið breytist - nóg til að lesa sérhverja breytu í sérhverri geymdri línu
- `session_info`: YAML-textinn heill í hvert sinn sem uppfærsluteljari hans hreyfist (helgi, lotur og úrslit, ökumenn, uppsetning bíls, talstöð, myndavélalistar), `update` er teljarinn
- `header`: 112 bæta irsdk-hausinn heill í hvert sinn sem hann breytist (útgáfa, ástand, tikktíðni, frávik, tikk línanna)

**Ekki fáanlegt**

- heimsstaða í beinni: samnýtta minnið hefur enga; breiddargráða, lengdargráða og hæð eru aðeins í .ibt-skránum (þegar skráning er á), sem skoðarinn les - watcher nefnir þær sem voru skrifaðar í setunni
- tikkin milli tveggja lestra: herminn skrifar 60 línur á sekúndu í 3 eða 4 hólf og watcher les 10 sinnum á sekúndu, svo flest tikk eru yfirskrifuð áður en hægt er að lesa þau; .ibt-skráin hefur hvert tikk þegar skráning er á

**Stærð**: fjarmælingarlína er nokkur KB (um 5 til 10 KB með fylkjum allra bíla), geymd allt að 10 sinnum á sekúndu, auk hauss (112 bæti) jafn oft og YAML upplýsinga um lotu (tugir KB) þegar það breytist: um 0,2 til 0,4 GB á klukkustund á braut fyrir þjöppun; zstd kemur því niður í brot (ekki enn mælt á raunverulegri lotu)

## Staðfest {#verified}

prófað á samnýttri minnisblokk sem er smíðuð í prófinu eftir irsdk-útlitinu; óprófað á móti hermininum

## Heimild {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
