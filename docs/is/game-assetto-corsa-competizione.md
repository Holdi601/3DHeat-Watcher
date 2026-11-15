---
title: "Assetto Corsa Competizione (lifandi gögn)"
nav_order: 3
lang: "is"
source: game-assetto-corsa-competizione.md
source_hash: "08033208b212"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa Competizione (lifandi gögn) {#assetto-corsa-competizione-live-data}

Meðan þú spilar Assetto Corsa Competizione vistar watcher gögnin sem leikurinn sjálfur sendir út, svo þú getir skoðað þau síðar á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `assetto-corsa-competizione`, gerð [`telemetry`](sources-and-rules.md); það keyrir meðan `AC2-Win64-Shipping.exe` er í gangi og leitar að nýjum gögnum á 0,1 s fresti.*

## Hvað er skráð {#what-is-recorded}

- staða eigin bíls (heims-XYZ, m: meðaltal snertipunkta hjólbarða við jörð) á 10 Hz með hraða, gír, inngjöf, bremsu
- upphaf og endir lotu með brautinni og bílnum sem leikurinn nefnir
- hringir eftir hringateljara leiksins, með hringtíma hans; sæti í keppni
- færslur (aftur í viðgerðarsvæðið, endurræsing): `teleport` þar sem bíllinn var, `spawn` þar sem hann er núna
- hringir, besti hringur, vegalengd, hámarkshraði

## Hvaðan það kemur {#where-it-comes-from}

samnýtt minni Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static

## Hvernig kveikt er á því {#how-to-switch-it-on}

Ekki þarf að kveikja á neinu: watcher les heimildina eins og leikurinn eða vettvangurinn lætur hana í té.

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

#### Allt geymt {#everything-kept}

Raðirnar eru fáeinar á sekúndu; leikirnir senda miklu meira. Sérhver UDP-pakki sem
berst - í valmyndum, milli hringja, líka þeir sem enginn afkóðari les - er geymdur heill
í `heat.raw.parquet` lotunnar undir sniði sínu (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), og sérhver síða af samnýttu minni
(allt varpið, ekki aðeins bætin sem eru afkóðuð) í hvert sinn sem hún breytist, undir
heiti varpsins (`acpmf_physics`, ...). `used` merkir það sem varð líka að
röðum; `selfCheck.completeness` í `meta.json` telur hverja gerð (umbreytingarregla 3DHeat).

Sama eining þjónar líka: [Assetto Corsa (lifandi gögn)](game-assetto-corsa.md), [Assetto Corsa EVO (lifandi gögn)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (lifandi gögn)](game-assetto-corsa-rally.md), [BeamNG.drive (lifandi gögn)](game-beamng.md), [DiRT Rally 2.0 (lifandi gögn)](game-dirt-rally-2.md), [EA SPORTS WRC (lifandi gögn)](game-ea-wrc.md), [Forza Horizon 4 (lifandi gögn)](game-forza-horizon-4.md), [Forza Horizon 5 (lifandi gögn)](game-forza-horizon-5.md), [Forza Horizon 6 (lifandi gögn)](game-forza-horizon-6.md), [Forza Motorsport (lifandi gögn)](game-forza-motorsport.md), [Richard Burns Rally (lifandi gögn)](game-richard-burns-rally.md).

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

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Lykill innan slaufusviga er fylltur út á keyrslutíma (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; „Hvað er skráð“ hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [umbreytingarreglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er sérhver pakki, síða, lína eða svar sem millistykkið tekur við geymt heilt í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, og svo hver reitur sem er geymdur með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hverja `type` - `lost` er 0.

**Lesið**

- raðir á 10 Hz úr physics-síðunni: staða (meðaltal snertipunkta hjólbarða við jörð), hraði, gír, inngjöf, bremsa, yaw/pitch/roll (rad), snúningar á mínútu, stýri (eins og síðan hefur það); upphaf lotu með brautinni og bílnum úr static-síðunni; hringir, sæti í keppni

**Geymt hrátt**

- hver síða heil - allt minnisvarpið, ekki aðeins bætin sem eru afkóðuð - í hvert sinn sem bæti hennar breytast, við 10 Hz lestur watcher: `acpmf_physics`, `acpmf_graphics`, `acpmf_static`; endurlestur sem er bæti fyrir bæti eins og sá síðasti er talinn í `unchanged_reads` í meta.json, ekki geymdur aftur
- allt sem er aðeins afkóðað fyrir hringaskrár (`decoders/kunos.py`: skrið, álag, þrýstingur, hitastig, camber, fjöðrun, snertipunktar, bremsuhitastig, skriðhlutfall og skriðhorn á hvert hjól; hraði í heimi og staðbundinn, hornhraði, hjálpartæki) er í þessum síðum

**Ekki fáanlegt**

- staða annarra bíla: síðurnar lýsa bíl spilarans eingöngu (graphics-síða ACC hefur í sumum útgáfum bílanúmer og hnit annarra - geymt í hráu síðunni, ekki afkóðað)
- eðlisfræðitikk milli lestra watcher: leikurinn endurskrifar síðuna á eðlisfræðitíðni sinni (allt að 333 Hz) og watcher les 10 sinnum á sekúndu

**Stærð**: um 150-300 MB á klukkustund fyrir þjöppun (4 KB svæði á síðu með allt að 10 breytingum á sekúndu); síðurnar eru að mestu núll og zstd heldur aðeins litlum hluta

## Staðfest {#verified}

afkóðunin er hringupptökutæki gamecapture (prófað á tilbúnum síðum); millistykkið prófað á samnýttu minni sem er smíðað í prófinu eftir skjalaða útlitinu; óprófað á móti leiknum

## Heimild {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
