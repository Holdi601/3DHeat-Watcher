---
title: "War Thunder (endursýningar)"
nav_order: 45
lang: "is"
source: game-warthunder-replays.md
source_hash: "4bf6e2f218cb"
nav_exclude: true
search_exclude: true
---
# War Thunder (endursýningar) {#war-thunder-replays}

Eftir leik í War Thunder breytir watcher endursýningunni sem leikurinn vistaði í skrár sem þú getur skoðað á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `warthunder-replays`, gerð [`replay`](sources-and-rules.md); það keyrir alltaf (það bíður ekki eftir að leikur ræsist) og leitar að nýjum gögnum á 5 s fresti.*

## Hvað er skráð {#what-is-recorded}

- staða og afstaða hverrar flugvélar um það bil 4 sinnum á sekúndu (eins oft og endursýningin geymir)
- staða landeininga úr jarðsamstillingu endursýningarinnar (í endursýningum frá 2026; ekki í þeim frá 2025)
- hver hver eining var (spilari, ökutækisauðkenni, lið) þar sem dráp eða skot nefnir hana; dráp, dauðsföll og skot þar sem þau gerðust; spjall; kortið
- dráp, dauðsföll, stig og yfirtökur höfundar endursýningarinnar sem tölfræði

## Hvaðan það kemur {#where-it-comes-from}

endursýningar sem War Thunder vistar: &lt;War Thunder>/Replays/\*.wrpl (þegar vistun endursýninga er á), umbreyttar af ytri umbreytinum `heat3d-wt-replay` (exporters/ext/warthunder-replay)

## Hvernig á að kveikja á því {#how-to-switch-it-on}

kveiktu á vistun endursýninga í valkostum War Thunder og settu upp umbreytinn: pip install -e &lt;3DHeat>/exporters/ext/warthunder-replay

Stillingar úr umhverfisbreytum:

- `HEAT3D_WT_REPLAY`: mappa umbreytisins (klón eða afpökkuð útgáfa), þegar hann er ekki uppsettur eða við hlið watcher

## Hvernig það virkar {#how-it-works}

Endursýningar og demó: það sem leikur vistar af viðureign, breytt þegar viðureigninni er lokið.

Endursýning geymir allt sem lifandi viðmót heldur eftir í fjölspilunarleikjum -
stöðu hvers spilara, hvert dráp þar sem það gerðist - og hún er skrá sem
leikurinn skrifar fyrir spilara sína, svo lestur hennar snertir ekkert í leiknum. Watcher
fylgist með möppunum sem leikir vista þær í, bíður þar til ný skrá hættir að
stækka (annars er leikurinn enn að skrifa hana), og breytir henni í
vinnuþræði, svo löng umbreyting haldi aldrei aftur af restinni af watcher.

Í fyrsta skipti sem mappa sést eru endursýningarnar sem þegar eru í henni aðeins skráðar,
ekki umbreyttar: spilari með ára gömul demó myndi annars sjá watcher upptekinn
í heilan dag. `python -m heat3d_watch replays <adapter> [folder]` umbreytir
þeim sem fyrir eru ef beðið er um það.

#### War Thunder {#war-thunder}

War Thunder vistar endursýningu af hverri orrustu í `<War Thunder>/Replays/*.wrpl`
þegar vistun endursýninga er kveikt í valkostum leiksins. Watcher les þær ekki
sjálfur: ytri umbreytir gerir það (3DHeat War Thunder replay converter,
`exporters/ext/warthunder-replay`, skipunin `heat3d-wt-replay`), sjálfstætt
verkefni. Þegar skipunin er á PATH, eða
pakkinn er uppsettur eða við hlið watcher, er hver ný endursýning keyrð í gegnum
hana inn í lotumöppuna sem `<map>/<match>.parquet` og `<match>.match.json`;
þegar hún er það ekki, segir watcher einu sinni hvernig á að setja hana upp og lætur möppuna
vera. Það sem umbreytirinn les, og það sem hann les ekki, stendur í README hans. Lína
höfundar endursýningarinnar í niðurstöðunum - dráp, dráp á jörðu, dauðsföll, aðstoð,
stig, yfirtökur - verður tölfræði lotunnar.

Sama eining þjónar líka: [Counter-Strike 2 (endursýningar)](game-cs2-demos.md), [Dota 2 (endursýningar)](game-dota-replays.md), [Squad (endursýningar)](game-squad-demos.md), [World of Tanks (endursýningar)](game-wot-replays.md), [World of Warships (endursýningar)](game-wows-replays.md).

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | já |
| Upp-ás | `y` |
| Einingar | metrar (x austur, y upp, z norður) |
| Speglað fyrir skoðarann | `z` |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` (`axes`) hverrar lotu og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem "allowed (reads only what the game publishes)".
- Gerð `replay`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (endursýningar og demó sem leikurinn vistar), svo það skráir bæði í netspilun og án nets; merkið ræður aðeins hvort minni megi nokkurn tíma lesa.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`map`

Lykill í slaufusvigum er fylltur út við keyrslu (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; "Hvað er skráð" hér að ofan nefnir þá.

## Heilleiki {#completeness}

Umbreytirinn sem þetta millistykki keyrir fylgir [breytireglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem endursýningin geymir er lesið eða varðveitt, aldrei sleppt - lesið inn í töfluna og skjal viðureignarinnar, allt annað varðveitt í heild í hliðarskrám við hlið þeirra, talið í `selfCheck.completeness` í skjali viðureignarinnar. Skjölun umbreytisins sjálfs telur upp hvað hann les, geymir óunnið og getur ekki lesið.

## Staðfest {#verified}

umbreytirinn er athugaður á opinberum endursýningum úr nokkrum leikjaútgáfum (dráp og nöfn passa við niðurstöðurnar) og með prófunum á tilbúnum endursýningum; þessi tenging með prófunum með staðgengilsskipun

## Heimild {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
