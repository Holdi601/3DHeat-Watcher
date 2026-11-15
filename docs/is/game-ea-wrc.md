---
title: "EA SPORTS WRC (lifandi gögn)"
nav_order: 17
lang: "is"
source: game-ea-wrc.md
source_hash: "c97300f65c43"
nav_exclude: true
search_exclude: true
---
# EA SPORTS WRC (lifandi gögn) {#ea-sports-wrc-live-data}

Meðan þú spilar EA SPORTS WRC vistar watcher gögnin sem leikurinn sjálfur sendir út, svo þú getir skoðað þau síðar á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `ea-wrc`, gerð [`telemetry`](sources-and-rules.md); það keyrir meðan `WRC.exe` er í gangi og leitar að nýjum gögnum á 0,1 s fresti.*

## Hvað er skráð {#what-is-recorded}

- staða eigin bíls (heims-XYZ, m) á 10 Hz með hraða, gír, inngjöf, bremsu, vegalengd leggsins
- upphaf leggs (legg-klukkan fer af stað), endir með tíma leggsins, endurræsingar
- færslur (endurstilling á veginn): `teleport` þar sem bíllinn var, `spawn` þar sem hann er núna
- leggir, besti legg-tími, vegalengd, hámarkshraði

## Hvaðan það kemur {#where-it-comes-from}

UDP 127.0.0.1:20777, session_update-pakki sjálfgefinnar `wrc`-gerðar (Documents\My Games\WRC\telemetry\config.json); meðan annað forrit heldur 20777 lætur watcher gáttina eftir því

## Hvernig kveikt er á því {#how-to-switch-it-on}

`python -m heat3d_watch setup ea-wrc --apply` kveikir á session_update-pakkanum í config.json (afrit tekið fyrst)

Sláðu skipunina inn í Terminal sem er opnaður í möppu watcher (sjá [Áður en þú byrjar](before-you-start.md)). Ef hún mistekst segir síðasta línan hvers vegna; [Uppsetning og keyrsla](installing-and-running.md) fjallar um algengustu ástæðurnar.

`python -m heat3d_watch setup ea-wrc` sýnir skrárnar sem hún myndi breyta; `python -m heat3d_watch setup ea-wrc --apply` breytir þeim og geymir upprunalegu skrána sem `<file>.heat3d-backup` (sjá [Skipanir](commands.md#setup)). Hún prentar `ea-wrc: changed: ...` fyrir hverja breytingu, eða `ea-wrc: nothing to change` þegar kveikt er þegar á þessu.

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

UDP: `Documents/My Games/WRC/telemetry/config.json` í WRC (`session_update`-pakki
`wrc`-gerðarinnar), `hardware_settings_config.xml` í DiRT
(`<udp enabled="true" extradata="3" port="20777">`), NGP-viðbót RBR
(`udpTelemetry=1`, gátt 6776). Leggir eftir legg-klukku leiksins
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

Sama eining þjónar líka: [Assetto Corsa (lifandi gögn)](game-assetto-corsa.md), [Assetto Corsa Competizione (lifandi gögn)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (lifandi gögn)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (lifandi gögn)](game-assetto-corsa-rally.md), [BeamNG.drive (lifandi gögn)](game-beamng.md), [DiRT Rally 2.0 (lifandi gögn)](game-dirt-rally-2.md), [Forza Horizon 4 (lifandi gögn)](game-forza-horizon-4.md), [Forza Horizon 5 (lifandi gögn)](game-forza-horizon-5.md), [Forza Horizon 6 (lifandi gögn)](game-forza-horizon-6.md), [Forza Motorsport (lifandi gögn)](game-forza-motorsport.md), [Richard Burns Rally (lifandi gögn)](game-richard-burns-rally.md).

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

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Lykill innan slaufusviga er fylltur út á keyrslutíma (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; „Hvað er skráð“ hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [umbreytingarreglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er sérhver pakki, síða, lína eða svar sem millistykkið tekur við geymt heilt í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, og svo hver reitur sem er geymdur með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hverja `type` - `lost` er 0.

**Lesið**

- raðir á 10 Hz: staða, hraði, gír, inngjöf, bremsa, vegalengd leggsins, yaw, snúningar á mínútu, stýri; upphaf leggs, endir með tíma leggsins, endurræsingar

**Geymt hrátt**

- sérhver pakki sem berst í gáttina, heill, á tíðni leiksins, undir sniði sínu: `session_update` (sjálfgefin `wrc`-gerð, 237 bæti), `wrc <n>-byte` fyrir alla aðra pakka sem stillingin sendir
- í pakkanum umfram raðirnar: heimshraði og hröðun, ásar bílsins, staða og hraði nafar á hvert hjól, hraði snertiflatar, bremsuhitastig, kúpling, handbremsa, klukka leiksins; 22 bæti (frávik 16-36 og 40) sem enginn birtur rásalisti nefnir

**Ekki fáanlegt**

- aðrir bílar: leikirnir senda bíl spilarans eingöngu
- hinar gerðirnar og pakkarnir sem fjarmælingastillingin getur skilgreint (session_start, session_end, pause): `setup` kveikir aðeins á `session_update`; sérhver annar pakki sem er sendur í gáttina er geymdur

**Stærð**: um 65 MB á klukkustund við 60 pakka á sekúndu (237 bæti auk 70 bæta hausa færslu; hraðinn -1 í stillingunni sendir einn á ramma, svo fleiri við hærri rammatíðni); zstd heldur broti af því

## Staðfest {#verified}

afkóðunin er hringupptökutæki gamecapture (prófað á pökkum sem eru smíðaðir eftir skjalaða útlitinu); millistykkið prófað á pökkum sem eru smíðaðir í prófinu og sendir yfir UDP; óprófað á móti leiknum

## Heimild {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
