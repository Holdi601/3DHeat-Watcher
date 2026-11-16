---
title: "Dota 2 (endursýningar)"
nav_order: 12
lang: "is"
source: game-dota-replays.md
source_hash: "88539ee6dc65"
nav_exclude: true
search_exclude: true
---
# Dota 2 (endursýningar) {#dota-2-replays}

Eftir leik í Dota 2 breytir watcher endursýningunni sem leikurinn vistaði í skrár sem þú getur skoðað á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `dota-replays`, gerð [`replay`](sources-and-rules.md); það keyrir alltaf (það bíður ekki eftir að leikur ræsist) og leitar að nýjum gögnum á 5 s fresti.*

## Hvað er skráð {#what-is-recorded}

- staða, hæð, heilsa og level hverrar hetju, 7,5 sinnum á sekúndu meðan hún er á lífi
- dráp og dauðsföll þar sem þau gerðust; turnar, barracks, Roshan og Tormentors þar sem þau féllu; wards þar sem þau voru sett
- kortamerkingar (pings), kortateikningar og skipanir (hreyfa, ráðast, galdra, kaupa, ...) hvers spilara þar sem bent var
- stigin og lína hvers spilara; lína innskráða spilarans sem tölfræði
- allt annað sem endursýningin geymir, varðveitt í heild við hlið töflunnar: hver rammi og netskilaboð, hver breyting á eiginleika einingar, hver færsla í strengjatöflu

## Hvaðan það kemur {#where-it-comes-from}

endursýningar sem Dota 2 vistar: &lt;Dota>/game/dota/replays/&lt;match id>.dem (sóttar í biðlaranum, eða með `dota-replay <match id>`)

## Hvernig á að kveikja á því {#how-to-switch-it-on}

sæktu endursýningu leiks í Dota 2, eða náðu í opinbera: `python -m heat3d_watch dota-replay <match id>`; settu upp lesarann: github.com/Holdi601/3DHeat-Ext-DotaReplay (`heat3d-dota-replay`, kemur með gem-dota)

Sláðu skipunina inn í terminal sem er opnaður í möppu watcher (sjá [Áður en þú byrjar](before-you-start.md)). Ef hún mistekst segir síðasta línan hvers vegna; [Uppsetning og keyrsla](installing-and-running.md) fer yfir algengustu orsakirnar.

Stillingar úr umhverfisbreytum:

- `HEAT3D_DOTA_REPLAY`: mappa lesarans (klón eða útpakkað útgáfusafn), þegar hann er ekki uppsettur eða við hlið watcher

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

#### Dota 2 {#dota-2}

Dota 2 vistar endursýningarnar sem spilari sækir (upplýsingar viðureignar, eða Watch >
Replays) í `<Dota>/game/dota/replays/<match id>.dem`; Valve geymir endursýningu hverrar
opinberrar viðureignar á þjónum sínum í nokkrar vikur, og `python -m heat3d_watch
dota-replay <match id>` sækir eina eftir auðkenni hennar í gegnum OpenDota. Watcher
les þær ekki sjálft: ytri lesari gerir það (3DHeat Dota Replay,
github.com/Holdi601/3DHeat-Ext-DotaReplay, `exporters/ext/dota-replay`, skipun
`heat3d-dota-replay`, les í gegnum gem-dota, MIT), sjálfstætt verkefni,
keyrður í eigin ferli á hverri
nýrri endursýningu þegar hann er á PATH, uppsettur eða við hlið watcher; vanti hann,
segir watcher einu sinni hvernig á að setja hann upp. Hann skrifar staðsetningu, hæð,
heilsu, level, stefnu, mana, reynslu, eigindir og hluti hverrar hetju 7,5
sinnum á sekúndu meðan hún er á lífi, dráp og dauðsföll þar sem þau gerðust, turna,
barracks, Roshan og Tormentors þar sem þau féllu, hvert ward þar sem það var
sett og þar sem það endaði, færslur combat log um hetjurnar
(skaða, lækningu, hæfileika, hluti, kaup, rúnir, gull, reynslu,
modifiers), og kortamerkingar, kortateikningar og skipanir hvers spilara - í
`dota/<match>.parquet`; hverja aðra einingu (creeps, summons, illusions,
couriers, byggingar) einu sinni á sekúndu í `<match>.units.parquet`; allt
combat log í `<match>.combatlog.parquet`; og viðureignina, spjallið, draft,
allt annað sem þáttarinn dregur út og eigin lokaskrá leiksins um viðureignina
í `<match>.match.json`, í lotumöppunni. Allt annað sem endursýningin
geymir er varðveitt í heild við hlið þeirra (breytiregla 3DHeat):
hver rammi og netskilaboð í `<match>.packets.parquet`, hver breyting á eiginleika
einingar í `<match>.entities.parquet`, hver færsla í strengjatöflu í
`<match>.strings.parquet`, talið í `selfCheck.completeness` í skjali viðureignarinnar.
Staðsetningar eru heimseiningar Dota,
þær sömu og game-state integration tilkynnir. Lína innskráða spilarans á
stigatöflunni verður að tölfræði lotunnar: dráp, dauðsföll, aðstoð,
last hits, denies, net worth, GPM, XPM, skaði á hetjur, wards, og hvort
viðureignin vannst. Ný Dota-uppfærsla getur breytt einingum endursýningarinnar áður en gem
fylgir á eftir; endursýning sem gem getur ekki lesið til enda er umbreytt eins
langt og hún nær og merkt `incomplete` í samantekt sinni.

Sama eining þjónar líka: [Counter-Strike 2 (endursýningar)](game-cs2-demos.md), [Squad (endursýningar)](game-squad-demos.md), [War Thunder (endursýningar)](game-warthunder-replays.md), [World of Tanks (endursýningar)](game-wot-replays.md), [World of Warships (endursýningar)](game-wows-replays.md).

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | já |
| Upp-ás | `z` |
| Einingar | Dota-heimseiningar (Hammer-einingar; kortið er um 16400 á breidd) |
| Speglað fyrir skoðarann | `y` |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` (`axes`) hverrar lotu og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem "allowed (reads only what the game publishes)".
- Gerð `replay`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (endursýningar og demó sem leikurinn vistar), svo það skráir bæði í netspilun og án nets; merkið ræður aðeins hvort minni megi nokkurn tíma lesa.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`duration`, `hero`, `score.{team}`, `team`, `won`

Lykill í slaufusvigum er fylltur út við keyrslu (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; "Hvað er skráð" hér að ofan nefnir þá.

## Heilleiki {#completeness}

Umbreytirinn fylgir [breytireglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem endursýningin geymir er lesið eða varðveitt, aldrei sleppt. Auk töflunnar er allt annað sem endursýningin geymir varðveitt í heild í hliðarskrám við hlið hennar í `dota/`-möppu lotunnar - `<match>.packets.parquet`, `<match>.entities.parquet`, `<match>.strings.parquet` (dálkarnir `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, eftir því sem við á) - og `selfCheck.completeness` í skjali viðureignarinnar (`<match>.match.json`) telur hvert `type` - `lost` er 0.

**Lesið**

- taflan (`dota/<match>.parquet`): staða, hæð, heilsa, level, stefna, mana, reynsla, eigindir, brynja, hraði, skaði, hlutir hverrar hetju og bendill spilarans 7,5 sinnum á sekúndu; dráp, dauðsföll, markmið, wards, færslur combat log um hetjur; kortamerkingar (`ping`, DOTA_UM_LocationPing), kortateikningar (`map_line`, DOTA_UM_MapLine) og hver einingarskipun (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` gerð skipunar, `value` auðkenni hæfileika eða hlutar, `text` flokkur skotmarksins; á punktinum sem skipað var á, annars á hetjunni)
- `<match>.units.parquet`: hver önnur eining einu sinni á sekúndu; `<match>.combatlog.parquet`: allt combat log eins og gem les það, hver reitur
- skjal viðureignarinnar: allt sem gem dregur út, og eigin færslur endursýningarinnar í heild - `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: lengd spilunar, nafn, hetja, Steam-auðkenni og lið hvers spilara), `matchDetails` (DOTA_UM_MatchDetails: lokastigatafla leikjasamhæfingarinnar, tölur hvers spilara, hlutir, skaði eftir gerð, picks og bans) og `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: dráp, dauðsföll, aðstoð, level, last hits og denies eins og lesið úr straumnum borið saman við `matchDetails`, fyrir hvern spilara

**Geymt óunnið**

- `<match>.packets.parquet`: hver rammi sem er ekki pakki (`type` `frame <n>`) og hver netskilaboð (`message <n>`, `name` frá Valve), í heild í `payload`, í röð skrárinnar (`seq`, `frame`), með `decoded` sem protobuf sem JSON (bætareitur gefinn sem lengd hans), hver skilaboðagerð afkóðuð: svc_PacketEntities (einingastraumurinn), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, combat log skilaboðin, GE_SosStartSoundEvent, DOTA_UM_TE_\* (skot, hreyfimyndir, blóð), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; send tables, flokkalisti og server info sem síðari einingaafkóðari þarf eru þar á meðal
- `<match>.entities.parquet`: hver eiginleiki hverrar einingar í hvert sinn sem hann breyttist (`type` eiginleikinn, `name` flokkurinn, `entity` vísir hennar; `value`, `vector` eða `decoded`), allt ástand hennar við sköpun, og hver sköpun, innkoma, brottför og eyðing - milljónir raða fyrir heila viðureign
- `<match>.strings.parquet`: hver færsla strengjatöflu úr hverri uppfærslu og hverri heildarmynd, gildið í heild; `userinfo`, `ActiveModifiers` og `EconItems` afkóðuð úr protobuf sínu
- `selfCheck.completeness` í skjali viðureignarinnar telur ramma og skilaboð eftir nafni Valve, færslur combat log (`combatlog <type>`), leikatburði (`gameevent <name>`), færslur strengjatöflu (`stringtable <name>`) og uppfærslur eininga (`entity <class>`); fáeinar eru aðeins geymdar óunnar (fullar einingamyndir sem gem sleppir því það endurbyggir úr breytingunum, og færslur taflna sem enginn les gildin úr), lost 0

**Ekki tiltækt**

- rödd: endursýningin hefur raddstillinguna en engin raddgögn
- nöfn á bak við hash og auðkenni: hljóð og agnir eru nefnd með hash af skrám leiksins, hæfileikar með auðkennum; endursýningin ber ekki nöfnin (hlutir eru nefndir í gegnum skrá gem þar sem hún hefur þá)
- allt sem aðeins biðlarar spilaranna sjálfra vissu (myndavél þeirra, skjár þeirra) umfram það sem þjónninn útvarpaði; bendillinn og hver skipun eru með

**Stærð**: hliðarskrárnar til samans eru nokkru stærri en endursýningin sjálf, packets og entities stærstar; heil viðureign tekur mínútu eða tvær í einu ferli

## Staðfest {#verified}

athugað á endursýningu opinberrar viðureignar: dráp, dauðsföll, aðstoð, level, last hits og denies passa við eigin lokaskrá leiksins fyrir alla tíu spilarana; hver skilaboð í packets-hliðarskránni raðast aftur bæti fyrir bæti; taflan og tölfræðin með prófunum á tilbúnum gögnum

## Heimild {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
