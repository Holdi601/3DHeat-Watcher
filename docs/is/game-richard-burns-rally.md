---
title: "Richard Burns Rally (lifandi gögn)"
nav_order: 38
lang: "is"
source: game-richard-burns-rally.md
source_hash: "4f2a2e46f8c8"
nav_exclude: true
search_exclude: true
---
# Richard Burns Rally (lifandi gögn) {#richard-burns-rally-live-data}

Meðan þú spilar Richard Burns Rally vistar watcher gögnin sem leikurinn sjálfur sendir út, svo þú getir skoðað þau síðar á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `richard-burns-rally`, gerð [`telemetry`](sources-and-rules.md); það keyrir meðan `RichardBurnsRally_SSE.exe` eða `RichardBurnsRally.exe` er í gangi og leitar að nýjum gögnum á 0,1 s fresti.*

## Hvað er skráð {#what-is-recorded}

- staða eigin bíls (heims-XYZ, m) á 10 Hz með hraða, gír, inngjöf, bremsu, vegalengd leggs
- upphaf leggs (leggklukkan byrjar), mark með legg-tíma, endurræsingar
- færslur (endurstilling á veginn): `teleport` þar sem bíllinn var, `spawn` þar sem hann er núna
- leggir, besti legg-tími, vegalengd, hámarkshraði

## Hvaðan það kemur {#where-it-comes-from}

NGP-viðbótin, UDP-fjarmæling, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1)

## Hvernig kveikt er á því {#how-to-switch-it-on}

RSF/NGP: í RichardBurnsRally.ini, í hlutanum [NGP], settu udpTelemetry=1 og endapunktinn á 127.0.0.1:6776

## Hvernig það virkar {#how-it-works}

Eigin fjarmæling kappakstursleikja: Forza, Assetto Corsa-leikirnir, rallíleikirnir og BeamNG, skráð sem leiðir, hringir og leggir.

Allir leikirnir hér birta fjarmælingu sína viljandi, fyrir mælaborð og hreyfipalla; engu er sprautað inn og ekkert er lesið sem leikurinn lætur ekki af hendi. Afkóðunin er ekki skrifuð tvisvar: hún er hringupptökutæki gamecapture í `heat3d_capture/telemetry` í 3DHeat GameCapture, afritað í `heat3d_watch/decoders` (prófað þar á pökkum sem eru smíðaðir eftir birtu útlitunum), og þessi eining breytir römmum þeirra í raðir watcher - staða bílsins nokkrum sinnum á sekúndu með hraða, gír og pedölum, atburður fyrir hvern hring eða legg, og tölurnar sem ökumaður heldur: hringir, besti hringur, vegalengd, hámarkshraði.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

„Data Out“ UDP, kveikt í HUD- og Gameplay-stillingum leiksins, til
127.0.0.1 gátt 5300, snið Dash. Einn pakki fyrir hvert hermitikk; staðsetning
dash-blokkarinnar er fundin út frá pökkunum (`forza.detect_layout`). Heimsmetrar,
Y upp; heimurinn er vinstrihandar og er teiknaður eins og hann er sendur, eins og
hringupptökutækið gerir (skjölun „Data Out“ í Forza Motorsport og Forza Horizon).
Leikurinn sendir í eina gátt, og FH Companion og önnur Data Out-forrit hlusta
á sömu gátt. Tvö forrit geta ekki deilt henni: á Windows fær sökkullinn sem er
bundinn við 127.0.0.1 pakkana, og sá sem er bundinn við öll vistföng á sömu
gátt fær enga, hvor sem kom á undan. Þess vegna bíður watcher dálitla stund eftir að
leikurinn ræsist áður en það tekur gáttina, tekur hana aldrei af forriti sem
heldur henni, og sleppir henni um leið og annað forrit byrjar að hlusta þar.
Meðan það heldur gáttinni sendir það hvern pakka óbreyttan áfram til
127.0.0.1:5301 - stilltu gáttarreit FH Companion (flipann fyrir fjarmælingu) á 5301 og
bæði skrá.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: `Documents/My Games/WRC/telemetry/config.json` hjá WRC (`session_update`-pakki
`wrc`-byggingarinnar), `hardware_settings_config.xml` hjá DiRT
(`<udp enabled="true" extradata="3" port="20777">`), NGP-viðbót RBR
(`udpTelemetry=1`, gátt 6776). Leggir eftir leggklukku leiksins
(`rally.StageSplitter`). RBR skjalar ekki ása sína: upp-ásinn er sá
sem leggurinn breytist minnst eftir, ákveðinn þegar lotunni lýkur.

#### Allt geymt {#everything-kept}

Raðirnar eru fáeinar á sekúndu; leikirnir senda miklu meira. Sérhver UDP-pakki sem
berst - í valmyndum, milli hringja, líka þeir sem enginn afkóðari les - er geymdur heill
í `heat.raw.parquet` lotunnar undir sniði sínu (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), og sérhver síða af samnýttu minni
(allt varpið, ekki aðeins bætin sem eru afkóðuð) í hvert sinn sem hún breytist, undir
heiti varpsins (`acpmf_physics`, ...). `used` merkir það sem varð líka að
röðum; `selfCheck.completeness` í `meta.json` telur hverja gerð (umbreytingarregla 3DHeat).

Sama eining þjónar líka: [Assetto Corsa (lifandi gögn)](game-assetto-corsa.md), [Assetto Corsa Competizione (lifandi gögn)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (lifandi gögn)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (lifandi gögn)](game-assetto-corsa-rally.md), [BeamNG.drive (lifandi gögn)](game-beamng.md), [DiRT Rally 2.0 (lifandi gögn)](game-dirt-rally-2.md), [EA SPORTS WRC (lifandi gögn)](game-ea-wrc.md), [Forza Horizon 4 (lifandi gögn)](game-forza-horizon-4.md), [Forza Horizon 5 (lifandi gögn)](game-forza-horizon-5.md), [Forza Horizon 6 (lifandi gögn)](game-forza-horizon-6.md), [Forza Motorsport (lifandi gögn)](game-forza-motorsport.md).

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | já |
| Upp-ás | `y` |
| Einingar | metrar; upp-ás ákveðinn út frá akstrinum (RBR skjalar ekki ása sína) |
| Speglað fyrir skoðarann | ekkert |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` hverrar lotu (`axes`) og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **nei**. `games --markdown` sýnir þetta sem „single-player“.
- Gerð `telemetry`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (UDP-gátt eða samnýtt minni sem leikurinn birtir), svo það skráir bæði í spilun á netinu og án nets; flaggið ræður aðeins því hvort minni megi nokkurn tíma vera lesið.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur sem spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Lykill innan slaufusviga er fylltur út á keyrslutíma (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; „Hvað er skráð“ hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [umbreytingarreglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er sérhver pakki, síða, lína eða svar sem millistykkið tekur við geymt heilt í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, og svo hver reitur sem er geymdur með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hverja `type` - `lost` er 0.

**Lesið**

- raðir á 10 Hz: staða, hraði, gír, inngjöf, bremsa, vegalengd leggs, yaw, snúningar á mínútu, stýri; upphaf leggs, mark með legg-tíma, endurræsingar

**Geymt hrátt**

- sérhver pakki sem berst í gáttina, heill, á tíðni leiksins, undir sniði sínu: `telemetry` (664 bæta TelemetryData frá NGP), annars `rbr <n>-byte`
- í pakkanum umfram raðirnar: afstaða, eigin hraðar og hröðun bílsins, fjöðrunarútslag og kraftur á hvert hjól, framvinda leggsins og vegalengd að endamarki; afgangur 664 bætanna (vél, hjólbarða- og bremsublokkir á hvert hjól) er enn afkóðaður hvergi

**Ekki fáanlegt**

- aðrir bílar: leikirnir senda aðeins bíl spilarans
- hraðaeining hans og ásar: ekki skjalað - hraði er tekinn úr stöðunum, upp úr akstrinum

**Stærð**: um 160 MB á klukkustund við 60 pakka á sekúndu (664 bæti auk 70 bæta færsluhauss); zstd heldur broti

## Staðfest {#verified}

afkóðunin er hringupptökutæki gamecapture (prófað á pökkum sem eru smíðaðir eftir skjöluðu útlitunum); millistykkið prófað á pökkum sem eru smíðaðir í prófinu, sendir yfir UDP; óprófað á móti leiknum

## Heimild {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
