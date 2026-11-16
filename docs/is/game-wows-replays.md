---
title: "World of Warships (endursýningar)"
nav_order: 48
lang: "is"
source: game-wows-replays.md
source_hash: "e7d24a56747e"
nav_exclude: true
search_exclude: true
---
# World of Warships (endursýningar) {#world-of-warships-replays}

Eftir leik í World of Warships breytir watcher endursýningunni sem leikurinn vistaði í skrár sem þú getur skoðað á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `wows-replays`, gerð [`replay`](sources-and-rules.md); það keyrir alltaf (það bíður ekki eftir að leikur ræsist) og leitar að nýjum gögnum á 5 s fresti.*

## Hvað er skráð {#what-is-recorded}

- staða og stefna hvers skips meðan upptökubiðlarinn sá það (um 6 til 7 sinnum á sekúndu á hreyfingu), skip spilarans sjálfs allan tímann
- spilari, bandamaður eða óvinur, og skip (skip spilarans sem tók upp með nafni, hin með skipanúmeri leiksins); sökkt skip þar sem þau sukku og drápsmenn þeirra þar sem þeir stóðu
- kortið; skip, dráp og afkoma spilarans sem tók upp sem tölfræði

## Hvaðan það kemur {#where-it-comes-from}

endursýningar sem World of Warships vistar: &lt;World of Warships>/replays/\*.wowsreplay (þegar endursýningar eru á), umbreyttar af ytri umbreytinum `heat3d-wows-replay` (exporters/ext/wows-replay)

## Hvernig á að kveikja á því {#how-to-switch-it-on}

kveiktu á upptöku endursýninga í World of Warships (`isReplayEnabled` í preferences.xml, eða eigin stilling leiksins þar sem hún er til) og settu upp umbreytinn: pip install -e &lt;3DHeat>/exporters/ext/wows-replay

Stillingar úr umhverfisbreytum:

- `HEAT3D_WOWS_REPLAY`: mappa umbreytisins (klón eða afpökkuð útgáfa), þegar hann er ekki uppsettur eða við hlið watcher

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

#### World of Tanks og World of Warships {#world-of-tanks-and-world-of-warships}

Báðir vista endursýningu af hverri orrustu í `<game>/replays/` þegar upptaka er kveikt
(`*.wotreplay`, `*.wowsreplay`); uppsetningarnar finnast í gegnum lista Wargaming
Game Center, `C:/Games/World_of_Tanks*` / `World_of_Warships*`, og
Steam. Eins og með War Thunder les watcher skrárnar ekki sjálfur: ytri
umbreytir fyrir hvorn leik gerir það (`exporters/ext/wot-replay`, skipunin
`heat3d-wot-replay`; `exporters/ext/wows-replay`, skipunin
`heat3d-wows-replay`), hvor um sig sjálfstætt verkefni.
Þegar hann finnst á PATH, er uppsettur, eða er við hlið watcher,
breytir hann hverri nýrri endursýningu í `<map>/<match>.parquet` og `<match>.match.json`
í lotumöppunni; vanti hann, segir watcher einu sinni hvernig á að setja hann upp. Lína
spilarans sem tók upp - ökutæki eða skip, dráp, skaði (World of Tanks),
hvort hann lifði af, og niðurstaðan (World of Tanks) - verður
tölfræði lotunnar. Það sem hver umbreytir les, og það sem hann les ekki, stendur í
README hans.

Sama eining þjónar líka: [Counter-Strike 2 (endursýningar)](game-cs2-demos.md), [Dota 2 (endursýningar)](game-dota-replays.md), [Squad (endursýningar)](game-squad-demos.md), [War Thunder (endursýningar)](game-warthunder-replays.md), [World of Tanks (endursýningar)](game-wot-replays.md).

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | já |
| Upp-ás | `y` |
| Einingar | heimseiningar World of Warships (x austur, y upp, z norður; ein er 15 m samkvæmt lögun skrokks, 30 m samkvæmt færi leiksins) |
| Speglað fyrir skoðarann | `z` |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` (`axes`) hverrar lotu og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem "allowed (reads only what the game publishes)".
- Gerð `replay`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (endursýningar og demó sem leikurinn vistar), svo það skráir bæði í netspilun og án nets; merkið ræður aðeins hvort minni megi nokkurn tíma lesa.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`map`, `survived`, `vehicle`, `won`

Lykill í slaufusvigum er fylltur út við keyrslu (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; "Hvað er skráð" hér að ofan nefnir þá.

## Heilleiki {#completeness}

Umbreytirinn sem þetta millistykki keyrir fylgir [breytireglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem endursýningin geymir er lesið eða varðveitt, aldrei sleppt - lesið inn í töfluna og skjal viðureignarinnar, allt annað varðveitt í heild í hliðarskrám við hlið þeirra, talið í `selfCheck.completeness` í skjali viðureignarinnar. Skjölun umbreytisins sjálfs telur upp hvað hann les, geymir óunnið og getur ekki lesið.

## Staðfest {#verified}

umbreytirinn er athugaður á opinberum endursýningum úr nokkrum leikjaútgáfum og með prófunum á tilbúnum endursýningum; þessi tenging með prófunum með staðgengilsskipun

## Heimild {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
