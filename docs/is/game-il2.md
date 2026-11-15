---
title: "IL-2 Sturmovik: Great Battles (lifandi gögn)"
nav_order: 26
lang: "is"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (lifandi gögn) {#il-2-sturmovik-great-battles-live-data}

Meðan þú spilar IL-2 Sturmovik: Great Battles vistar watcher gögnin sem leikurinn sjálfur sendir út, svo þú getir skoðað þau síðar sem tölfræði og tímalínu.

*Tæknilegar upplýsingar: millistykki `il2`, gerð [`telemetry`](sources-and-rules.md); það keyrir meðan `Il-2.exe` eða `IL2Series.exe` er í gangi og leitar að nýjum gögnum á 0,1 s fresti.*

## Hvað er skráð {#what-is-recorded}

- ferðir (sorties): flugvélin sem er valin (spawn) og þegar úttakið stöðvast (session_end) - engin heimsstaða: leikurinn sendir enga
- sprengjur og eldflaugar sem er sleppt (massi), högg og skaði sem er orðið fyrir, sprengingar, skotlotur - stöður staðbundnar miðað við flugvélina
- jafngildur flughraði, AGL, lóðréttur hraði, g, snúningar hreyfils á mínútu einu sinni á sekúndu, með öllum öðrum vísum sem pakkinn ber (inntaksþrýstingur, titringur hreyfils, ástand og þrýstingur lendingarbúnaðar, AoA, hliðarsvif, hröðun x/y/z, titringur stjórnklefa, vængbörð, loftbremsur)
- ferðir, skotin skot, sprengjur, eldflaugar, högg sem tekin eru, mesti hraði, mesta g, flugtími; titill þjóns og nafn flugmanns á netinu
- sérhver fjarmælingarpakki geymdur heill í heat.raw.parquet

## Hvaðan það kemur {#where-it-comes-from}

UDP-fjarmælingarúttak leiksins til 127.0.0.1:41995 ([KEY = telemetrydevice] í &lt;game>\data\startup.cfg)

## Hvernig kveikt er á því {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (bætir við addrN = "127.0.0.1:41995", enable = true), endurræstu IL-2

Sláðu skipunina inn í Terminal sem er opnaður í möppu watcher (sjá [Áður en þú byrjar](before-you-start.md)). Ef hún mistekst segir síðasta línan hvers vegna; [Uppsetning og keyrsla](installing-and-running.md) fjallar um algengustu ástæðurnar.

`python -m heat3d_watch setup il2` sýnir skrárnar sem hún myndi breyta; `python -m heat3d_watch setup il2 --apply` breytir þeim og geymir upprunalegu skrána sem `<file>.heat3d-backup` (sjá [Skipanir](commands.md#setup)). Hún prentar `il2: changed: ...` fyrir hverja breytingu, eða `il2: nothing to change` þegar kveikt er þegar á þessu.

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

Sama eining þjónar líka: [IL-2 Sturmovik: Great Battles (endursýningar)](game-il2-tacview.md).

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | nei |
| Upp-ás | `y` |
| Einingar | engar: fjarmælingin hefur engar heimsstöður |
| Speglað fyrir skoðarann | ekkert |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` hverrar lotu (`axes`) og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem „allowed (reads only what the game publishes)“.
- Gerð `telemetry`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (UDP-gátt eða samnýtt minni sem leikurinn birtir), svo það skráir bæði í spilun á netinu og án nets; flaggið ræður aðeins því hvort minni megi nokkurn tíma vera lesið.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur sem spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

Lykill innan slaufusviga er fylltur út á keyrslutíma (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; „Hvað er skráð“ hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [umbreytingarreglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er sérhver pakki, síða, lína eða svar sem millistykkið tekur við geymt heilt í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, og svo hver reitur sem er geymdur með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hverja `type` - `lost` er 0.

**Lesið**

- SET_FOCUS (flugvélin sem er valin: ferð), DROP_BOMB og ROCKET_LAUNCH (massi, staðbundin staða), HIT og DAMAGE (staðbundin staða, kraftur), EXPLOSION (staðbundin staða, radíus), GUN_FIRE (skot í hverri könnun) sem raðir
- SETUP_ENG (index, id, staðbundin staða, hámarks snúningar á mínútu), SETUP_GUN (index, staðbundin staða, massi skotfæris, munnhraði) og SETUP_LGEAR (index, id, staðbundin staða) sem raðir: hreyflar, byssur og lendingarbúnaður flugvélarinnar þegar ferðin hefst
- SRV_TITLE, SRV_ADDR, SRS_ADDR og CLIENT_DAT (nafn flugmanns) í meta.json; coalition úr CTRL_DAT sem lið ferðarinnar
- allir fimmtán vísar forskriftarinnar á `state`-röðinni sem kemur einu sinni á sekúndu (eitt gildi sem tala, eitt fyrir hvern hreyfil, lendingarfót eða ás sem listi); mesti hraði, g og AGL úr hverjum pakka

**Geymt hrátt**

- sérhver gagnapakki (datagram) heill sem `payload`, undir Packet_ID sínu: `0x54000101` fyrir fjarmælingu (`used` þegar hann bjó til röð eða færslu í meta.json), sérhvert annað auðkenni sem sjálft sig, gagnapakki of stuttur fyrir eitt sem `short`
- það sem aðeins hráa hliðarskráin geymir: vísarnir milli raðanna sem koma einu sinni á sekúndu (leikurinn sendir þá á 50 Hz / decimation), SETUP-atburður styttri en útlit forskriftarinnar, atburðaauðkenni sem forskriftin telur ekki upp

**Ekki fáanlegt**

- heimsstaða: fjarmælingarúttakið hefur enga (staða atburða er staðbundin miðað við flugvélina); il2-tacview-millistykkið les stöður úr eigin Tacview-upptökum leiksins
- aðrar flugvélar og spilarar: úttakið lýsir aðeins eigin flugvél spilarans

**Stærð**: um 8 MB á klukkustund við 10 Hz sem `setup` stillir (decimation 5; pakki er um 160 bæti auk ramma hans), 40 MB við fulla 50 Hz leiksins, fyrir zstd; zstd minnkar endurteknu fleytitölurnar í brot

## Staðfest {#verified}

prófað á pökkum sem eru smíðaðir eftir eigin forskrift leiksins Il2_TeleOutput (útg. 1.2); breytingar á startup.cfg prófaðar á afriti af skránni; óprófað á móti leiknum í gangi

## Heimild {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
