---
title: "NVIDIA highlights (vettvangur)"
nav_order: 34
lang: "is"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA highlights (vettvangur) {#nvidia-highlights-platform}

Watcher vistar það sem NVIDIA highlights geymir um leikina þína, svo þú getir skoðað söguna þína síðar á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `nvidia-highlights`, gerð [`platform`](sources-and-rules.md); það keyrir allan tímann (það bíður ekki eftir að leikur ræsist) og leitar að nýjum gögnum á 10 s fresti.*

## Hvað er skráð {#what-is-recorded}

- hvert nýtt myndskeið, highlight eða skjámynd: leikur, skrá, gerð, lengd og augnablikið (veggklukka, ms)
- auðkenni og heiti highlight þegar leikurinn skráði það hjá NVIDIA
- hvar spilarinn var á því augnabliki, þegar annað millistykki skráði sama leik þá
- highlight-beiðnir sem GfeSDK-leikir skrá í annál, jafnvel þegar ekkert myndskeið er geymt

## Hvaðan það kemur {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;game>\config.json; myndskeið í upptökumöppunni (%USERPROFILE%\Videos\NVIDIA\\&lt;Game>\\\*.mp4) og &lt;temp>\Highlights\\&lt;game>; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## Hvernig kveikt er á því {#how-to-switch-it-on}

NVIDIA App: kveikt á Instant Replay eða Highlights, myndskeið vistuð með flýtilykli eða af leiknum

## Hvernig það virkar {#how-it-works}

Það sem ræsiforritið og skjákortsreklarinn geyma um spilun: tölfræði Steam,
afrek, spilunartími og tímalínur, og highlights og myndskeið NVIDIA.

Engin þessara heimilda þarf að leikur vinni með eða sé í gangi, svo
þrjú millistykkin hér eru alltaf á og líta á nokkrar skrár á nokkurra sekúndna fresti.

#### NVIDIA highlights og myndskeið (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Það sem NVIDIA App / GeForce Experience geymir, allt undir
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
```text
UGCTracker.json      the gallery index: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, when the file was written), profileName, drsName
                     (the exe), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (where clips are saved),
                     settings.tempDirectory (highlights wait in
                     <temp>\Highlights\<game> until saved)
Highlights\<game>\config.json  the highlight kinds a game registered:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: text}}}, profileName, drsName, shortName}
```
og myndskeiðsskrárnar sjálfar, `<capture folder>\<Game>\<Game> yyyy.mm.dd -
hh.mm.ss.ff.DVR.mp4` (skjámyndir: `<Game> Screenshot yyyy.mm.dd - ...png`), þar sem
tíminn í heitinu er staðartíminn þegar myndskeiðið var vistað. GfeSDK-leikir skrá líka
highlight-köll sín í annál í `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

Hvað þetta getur og getur ekki skilað: leikur sem styður NVIDIA Highlights
(GfeSDK) skráir gerðir highlights einu sinni - auðkenni eins og „kill“,
vægi, merki, birtingarheiti - og segir síðar aðeins „highlight &lt;id>,
frá &lt;ms> fyrir núna til &lt;ms> eftir“. Engar staðsetningar eru til, enginn leikur eða
umferð, enginn andstæðingur, engin sérsniðin gögn: SDK hefur engan reit fyrir neitt af því. Vistað
myndskeið bætir við skrá, leikjaheiti, lengd og tíma. Það sem er
skráð er því „þessi gerð augnabliks, í þessum leik, á þessum tíma“ - og staður
aðeins með því að fletta upp tímanum í upptöku annars millistykkis af sama leik
(`position_at`), sem þetta millistykki gerir fyrir hvert myndskeið sem það skráir.
<https://developer.nvidia.com/highlights>

Hvert millistykki geymir það sem það hefur þegar séð í `<data>\state\<id>.json`, svo
endurræsing skráir ekkert tvisvar.

Hver lota geymir líka það sem raðir hennar komu úr, heilt (umbreytingarregla 3DHeat,
docs/converters.md í geymslu skoðarans), í `heat.raw.parquet`:
bæti tölfræðiskrárinnar og skema hennar og localconfig-blokk leiksins
(steam-stats; tölfræðiskrá sem afkóðarinn getur ekki lesið fær lotu sem geymir aðeins
bæti hennar), haus tímalínuskrárinnar og hver færsla sem JSON
(steam-timeline), færsla hvers myndskeiðs í myndasafnsskránni, skilgreiningar leiksins á highlights
og sérhver lína úr GfeSDK-annálnum, líka þær sem eru ekki highlight-
beiðnir (nvidia-highlights).

Sama eining þjónar líka: [Steam statistics (vettvangur)](game-steam-stats.md), [Steam Timeline (vettvangur)](game-steam-timeline.md).

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | aðeins fengnar að láni: staðurinn sem önnur upptaka af sama leik hefur fyrir það augnablik |
| Upp-ás | `y` |
| Einingar | metrar |
| Speglað fyrir skoðarann | ekkert |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` hverrar lotu (`axes`) og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **nei**. `games --markdown` sýnir þetta sem „single-player“.
- Gerð `platform`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (það sem Steam eða skjákortsreklarinn geymir), svo það skráir bæði í spilun á netinu og án nets; flaggið ræður aðeins því hvort minni megi nokkurn tíma vera lesið.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur sem spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`clip_seconds`, `clips`, `placed`, `screenshots`

Lykill innan slaufusviga er fylltur út á keyrslutíma (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; „Hvað er skráð“ hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [umbreytingarreglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er sérhver pakki, síða, lína eða svar sem millistykkið tekur við geymt heilt í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, og svo hver reitur sem er geymdur með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hverja `type` - `lost` er 0.

**Lesið**

- hvert nýtt myndskeið og skjámynd: leikur, skrá, gerð, miðill, lengd (úr skránni, annars MP4-haus), augnablikið úr skráarheitinu, auðkenni og heiti highlight þar sem leikurinn skráði þau, og staður spilarans þá úr upptöku annars millistykkis
- GfeSDK highlight-beiðnir (hver `Posted Request HL...` nema stillingarköll) með tíma sínum

**Geymt hrátt**

- `UGC`: heil færsla myndskeiðsins í myndasafnsskránni UGCTracker.json, hver reitur sem NVIDIA skrifar
- `clip_file`: fyrir myndskeið sem skráin telur ekki upp, slóð skrárinnar, stærð, tími og mappa
- `highlights_config`: `Highlights\<game>\config.json` leiksins eins og hún er skrifuð (vægi, merki, heiti á hverju tungumáli), einu sinni í hverri lotu
- `gfesdk_log`: sérhver lína úr GfeSDK-annálunum sem er lesin eftir fyrstu keyrslu, `used` satt fyrir highlight-beiðnirnar og ósatt fyrir hitt (stillingar, myndbandsstillingar, eigin skilaboð SDK)

**Ekki fáanlegt**

- myndskeiðin og skjámyndirnar sjálfar: myndband og myndir haldast þar sem NVIDIA vistaði þær; raðirnar nefna skrána
- það sem var til áður en millistykkið keyrði fyrst: talið þegar séð, svo ára gömul myndskeið verða ekki að lotum í einu (`baseline`; False skráir þau)
- `apps` og `info` í UGCTracker.json og GallerySettings.json: stillingar forritsins, ekki augnablik í spilun; upptökumappan sem þær nefna er notuð
- staðsetningar, umferðir, andstæðingar: GfeSDK hefur engan reit fyrir þau

**Stærð**: um 1 KB á myndskeið og nokkur KB af skilgreiningum og annállínum við hverja ræsingu leiks: vel undir 1 MB á klukkustund

## Staðfest {#verified}

prófað á raunverulegri myndasafnsskrá, stillingum, highlight-skilgreiningum og myndskeiðum úr staðbundinni uppsetningu; GfeSDK highlight-beiðnalínur og highlight-auðkenni í myndskeiðum eru óprófuð

## Heimild {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
