---
title: "IL-2 Sturmovik: Great Battles (endursýningar)"
nav_order: 27
lang: "is"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (endursýningar) {#il-2-sturmovik-great-battles-replays}

Eftir leik í IL-2 Sturmovik: Great Battles breytir watcher endursýningunni sem leikurinn vistaði í skrár sem þú getur skoðað á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `il2-tacview`, gerð [`replay`](sources-and-rules.md); það keyrir allan tímann (bíður ekki eftir að leikur ræsist) og leitar að nýjum gögnum á 5 s fresti.*

## Hvað er skráð {#what-is-recorded}

- sérhver flugvél, farartæki og skip upptökunnar: stöður einu sinni á sekúndu (metrar austur/upp/norður frá viðmiðunarpunkti upptökunnar; lat/lon/alt sem dálkar)
- spawn, eyðingar (death) og brottfarir (left), flugtök og lendingar þegar þau eru skráð
- hlutir, eyðingar, flugtök, lendingar og lengd fyrir hverja upptöku
- sérhver lína upptökunnar geymd heil í heat.raw.parquet, á klukku raðanna

## Hvaðan það kemur {#where-it-comes-from}

eigin Tacview-upptökur leiksins &lt;game>\data\Tracks\\\*.acmi (ACMI 2.x texti, óþjappaður eða zip)

## Hvernig kveikt er á því {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 í [KEY = track_record])

Sláðu skipunina inn í Terminal sem er opnaður í möppu watcher (sjá [Áður en þú byrjar](before-you-start.md)). Ef hún mistekst segir síðasta línan hvers vegna; [Uppsetning og keyrsla](installing-and-running.md) fjallar um algengustu ástæðurnar.

`python -m heat3d_watch setup il2-tacview` sýnir skrárnar sem hún myndi breyta; `python -m heat3d_watch setup il2-tacview --apply` breytir þeim og geymir upprunalegu skrána sem `<file>.heat3d-backup` (sjá [Skipanir](commands.md#setup)). Hún prentar `il2-tacview: changed: ...` fyrir hverja breytingu, eða `il2-tacview: nothing to change` þegar kveikt er þegar á þessu.

## Hvernig það virkar {#how-it-works}

IL-2 Sturmovik: Great Battles - UDP-fjarmælingarúttak leiksins, og eigin Tacview-upptökur hans.

1. Fjarmæling („Telemetry output of IL2 v4.003“, útgáfa 1.2, fylgir sem
   `<game>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Kveikt í
   `<game>\data\startup.cfg`, kafli `[KEY = telemetrydevice]`: `addr`,
   `addr1`, ... = „IP[:port]“ (mörg skotmörk í einu), `decimation` (50 Hz /
   n), `enable`, `port`. `setup` bætir við einu skotmarki, 127.0.0.1:41995 (JoyPro notar
   41994, sjálfgefið í leiknum er 4322), og kveikir á úttakinu. Pakkar,
   little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Vísar: 0 ENG_RPM, 1 ENG_MP, 2/3 titringur hreyfils, 4 LGEARS_STATE, 5
   LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz að þyngdarafli meðtöldu),
   9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14
   VERTICAL_SPEED (m/s). Atburðir (2-bæta pakkaðir): 0 SET_FOCUS (STRING: lengdarbæti
   + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float
   max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass,
   float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float
   pos[3]}, 4 DROP_BOMB og 5 ROCKET_LAUNCH
   {float pos[3], float mass, WORD flags}, 6 HIT og 7 DAMAGE {float pos[3],
   float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE
   gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long
   client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short
   coalition}. Staðsetningar atburða eru staðbundnar miðað við flugvél spilarans; straumurinn
   hefur enga heimsstöðu - þetta eru því atburðir og tölur, ekki ferill.

2. Tacview-upptaka: `tacviewrecord = 1` í `[KEY = track_record]` lætur
   leikinn skrifa `<game>\data\Tracks\*.acmi` (í fjölspilun ræður þjónninn).
   Lokið skrá er umbreytt: sérhver flugvél, farartæki og skip með
   stöðum sínum, spawn og brottnámi (eytt eða farið), flugtökum og lendingum þegar
   upptakan hefur þau. ACMI 2.x textasnið, óþjappað eða zip, samkvæmt
   <https://www.tacview.net/documentation/acmi/en/> - „#t“-línur færa klukkuna,
   „id,Key=Value,...“-línur setja eiginleika (sextándakerfis-auðkenni, kommur varðar með „\\,“, aftari
   „\\“ heldur línunni áfram), „-id“ fjarlægir hlut, hlutur 0 ber
   altæku gildin (ReferenceLongitude/Latitude, RecordingTime, ...) og atburðina
   („Event=Destroyed\|id\|text“). T = Lon\|Lat\|Alt[\|U\|V] eða
   Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], lengdar- og breiddargráða miðað við
   viðmiðið, tómir reitir óbreyttir. Stöður fara í flatt kort umhverfis
   viðmiðunarpunktinn: x austur, y hæð, z norður, metrar. Viðmiðunarpunkturinn
   er `geo` lotunnar, borið í meta.json og fót töflunnar,
   svo skoðarinn geti lagt raunverulegan heim undir ferlana.

Sama eining þjónar líka: [IL-2 Sturmovik: Great Battles (lifandi gögn)](game-il2.md).

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

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem „allowed (reads only what the game publishes)“.
- Gerð `replay`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (endursýningar og demó sem leikurinn vistar), svo það skráir bæði í spilun á netinu og án nets; flaggið ræður aðeins því hvort minni megi nokkurn tíma vera lesið.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur sem spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

Lykill innan slaufusviga er fylltur út á keyrslutíma (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; „Hvað er skráð“ hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [umbreytingarreglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er sérhver pakki, síða, lína eða svar sem millistykkið tekur við geymt heilt í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, og svo hver reitur sem er geymdur með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hverja `type` - `lost` er 0.

**Lesið**

- T sérhvers hlutar (lengdargráða, breiddargráða, hæð, roll, pitch, yaw, U, V, heading) sem stöður einu sinni á sekúndu fyrir hvern hlut, með Name, Type, Pilot, Coalition/Color, Country, Group og Parent
- spawn, brottnám (death þegar Destroyed-atburður kom fyrst, annars left), TakenOff- og Landed-atburðir, Message- og Bookmark-atburðir sem raðir
- altæku gildin ReferenceLongitude/Latitude (upphafspunktur kortsins), RecordingTime/ReferenceTime (hvenær), DataSource, DataRecorder og Title í meta.json

**Geymt hrátt**

- sérhver lína sem er ekki tóm, rökleg lína, heil sem `text` (lína sem heldur áfram með aftari skástrik er sameinuð, eins og ACMI les hana), undir gerð sinni: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` og `event` (hlutur 0), `object` (id,Key=Value,...)
- það sem aðeins hráa hliðarskráin geymir: stöðurnar milli raðanna sem koma einu sinni á sekúndu, vopn, skeljar, blys, tinsnifsi og aðrir hlutir sem eru ekki teiknaðir sem ferlar, sérhver annar eiginleiki (fjarmæling eins og IAS, AOA, inngjöf, eldsneyti þar sem upptakan hefur hana), önnur altæk gildi (Comments, Briefing, Author, Category), atburðir aðrir en þeir sem eru lesnir (Timeout, LeftArea, ...)

**Ekki fáanlegt**

- ekkert sem upptakan geymir; það sem leikurinn skrifar ekki í upptökur sínar er ekki í þeim

**Stærð**: um texti upptökunnar sjálfrar auk um 70 bæta á línu, fyrir zstd: 100 MB upptaka verður um 150-250 MB hrá, sem zstd kemur nálægt stærð zip-upptökunnar

## Staðfest {#verified}

prófað á tilbúnum ACMI 2.2 skrám (texti og zip); óprófað á upptöku úr leiknum

## Heimild {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
