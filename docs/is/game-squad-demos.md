---
title: "Squad (endursýningar)"
nav_order: 40
lang: "is"
source: game-squad-demos.md
source_hash: "a908f7e6d9c3"
nav_exclude: true
search_exclude: true
---
# Squad (endursýningar) {#squad-replays}

Eftir leik í Squad breytir watcher endursýningunni sem leikurinn vistaði í skrár sem þú getur skoðað á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `squad-demos`, gerð [`replay`](sources-and-rules.md); það keyrir alltaf (það bíður ekki eftir að leikur ræsist) og leitar að nýjum gögnum á 5 s fresti.*

## Hvað er skráð {#what-is-recorded}

- staða, stefna líkamans og hraði hvers spilara í hvert sinn sem þjónninn afritar það (allt að 8 sinnum á sekúndu), fótgangandi og í ökutækjum á jörðu
- nafn, lið, fylking og sveit hvers spilara, með liðaskiptum
- ekki: hreyfing þyrlna, dráp og deployables - sjá README lesarans

## Hvaðan það kemur {#where-it-comes-from}

þjónademó sem Squad tekur upp með stjórnandaskipuninni AdminDemoRec: &lt;server>/SquadGame/Saved/Demos/\*.replay, lesin af ytri lesaranum `heat3d-squad-demo` (exporters/ext/squad-demo)

## Hvernig á að kveikja á því {#how-to-switch-it-on}

taktu upp á þjóninum: gefðu stjórnandanum `demos` heimildina í Admins.cfg, síðan AdminDemoRec &lt;name> og AdminDemoStop í stjórnborði leiksins; afritaðu demóið hingað og settu upp lesarann: pip install -e &lt;3DHeat>/exporters/ext/squad-demo

Stillingar úr umhverfisbreytum:

- `HEAT3D_SQUAD_DEMO`: mappa umbreytisins (klón eða afpökkuð útgáfa), þegar hann er ekki uppsettur eða við hlið watcher

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

#### Squad {#squad}

Sérþjónar Squad taka upp demó af viðureign þegar stjórnandi með
`demos` heimildina keyrir AdminDemoRec &lt;name> (og AdminDemoStop), í
`<server>/SquadGame/Saved/Demos/<name>.replay` - netendursýning í Unreal Engine
sem geymir það sem þjónninn afritaði, þar á meðal hreyfingu hvers spilara.
Watcher les þau ekki sjálfur: ytri lesari gerir það (3DHeat Squad
demo reader, `exporters/ext/squad-demo`, skipunin `heat3d-squad-demo`), hafður
sér svo vandamál í honum snerti ekkert annað. Hann er keyrður á hvert nýtt
demó í möppunum sem staðbundinn þjónn skrifar í, eða í möppu sem stillingarnar bæta við
fyrir demó afrituð af leigðum þjóni, inn í lotumöppuna sem
`<map>/<match>.parquet` og `<match>.match.json`. Lagið (layer), kortið, fjöldi
spilara og lengd viðureignar verða tölfræði lotunnar.

Sama eining þjónar líka: [Counter-Strike 2 (endursýningar)](game-cs2-demos.md), [Dota 2 (endursýningar)](game-dota-replays.md), [War Thunder (endursýningar)](game-warthunder-replays.md), [World of Tanks (endursýningar)](game-wot-replays.md), [World of Warships (endursýningar)](game-wows-replays.md).

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | já |
| Upp-ás | `z` |
| Einingar | Unreal-einingar (sentímetrar) |
| Speglað fyrir skoðarann | engin |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` (`axes`) hverrar lotu og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem "allowed (reads only what the game publishes)".
- Gerð `replay`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (endursýningar og demó sem leikurinn vistar), svo það skráir bæði í netspilun og án nets; merkið ræður aðeins hvort minni megi nokkurn tíma lesa.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`layer`, `map`, `match_seconds`, `players`

Lykill í slaufusvigum er fylltur út við keyrslu (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; "Hvað er skráð" hér að ofan nefnir þá.

## Heilleiki {#completeness}

Umbreytirinn sem þetta millistykki keyrir fylgir [breytireglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem endursýningin geymir er lesið eða varðveitt, aldrei sleppt - lesið inn í töfluna og skjal viðureignarinnar, allt annað varðveitt í heild í hliðarskrám við hlið þeirra, talið í `selfCheck.completeness` í skjali viðureignarinnar. Skjölun umbreytisins sjálfs telur upp hvað hann les, geymir óunnið og getur ekki lesið.

## Staðfest {#verified}

lesarinn er athugaður á opinberum þjónademóum (hreyfingin passar við hraðann sem hún ber; lið hverrar raðar passar við fylkingu hermannsins) og með prófunum á tilbúnum demóum; þessi tenging með prófunum með staðgengilsskipun

## Heimild {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
