---
title: "Counter-Strike 2 (endursýningar)"
nav_order: 8
lang: "is"
source: game-cs2-demos.md
source_hash: "82fe00f0f2f0"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (endursýningar) {#counter-strike-2-replays}

Eftir leik í Counter-Strike 2 breytir watcher endursýningunni sem leikurinn vistaði í skrár sem þú getur skoðað á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `cs2-demos`, gerð [`replay`](sources-and-rules.md); það keyrir alltaf (það bíður ekki eftir að leikur ræsist) og leitar að nýjum gögnum á 5 s fresti.*

## Hvað er skráð {#what-is-recorded}

- staða, sjónstefna, heilsa og peningar hvers spilara (á hverju 8. ticki)
- dráp, dauðsföll, skaði, handsprengjur, sprengja sett og aftengd þar sem það gerðist
- lotur, stig, hagkerfi; lína innskráða spilarans á stigatöflunni sem tölfræði

## Hvaðan það kemur {#where-it-comes-from}

demó sem CS2 vistar: &lt;CS2>/game/csgo/replays/\*.dem (sótt úr leikjasögunni) og &lt;CS2>/game/csgo/\*.dem (tekin upp)

## Hvernig á að kveikja á því {#how-to-switch-it-on}

sæktu demó viðureignar í CS2 (Watch > Your Matches), eða taktu eitt upp með `record` í stjórnborði leiksins

Stillingar úr umhverfisbreytum:

- `HEAT3D_CS2`: mappa 3DHeat CS2, þegar hún er ekki við hlið watcher eða uppsett

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

#### Counter-Strike 2 {#counter-strike-2}

CS2 vistar demóin sem spilari sækir úr leikjasögunni (flipinn Watch) í
`<CS2>/game/csgo/replays/` og þau sem eru tekin upp með `record` skipuninni í stjórnborðinu
í `<CS2>/game/csgo/`. Hvert þeirra er umbreytt með eigin CS2-umbreyti þessarar geymslu
(3DHeat CS2, github.com/Holdi601/3DHeat-CS2: staða, sjónstefna, heilsa og
peningar hvers spilara á hverju áttunda ticki; dráp, dauðsföll, skaði, handsprengjur, sprengja sett og aftengd
þar sem það gerðist; lotur, stig, hagkerfi) inn í lotumöppuna, sem taflan
`<map>/<match>.parquet` og yfirlitið `<match>.match.json` sem hita- og
viðureignarflipar skoðarans lesa. Stigatafla viðureignarinnar verður tölfræði lotunnar:
fyrir spilarann sem er skráður inn á Steam-reikning á þessari tölvu (úr `loginusers.vdf` frá Steam) undir einföldum nöfnum - kills, deaths, assists, ADR, KAST,
hlutfall höfuðskota, fyrstu dráp, clutches - ásamt stigum og lotum.

Sama eining þjónar líka: [Dota 2 (endursýningar)](game-dota-replays.md), [Squad (endursýningar)](game-squad-demos.md), [War Thunder (endursýningar)](game-warthunder-replays.md), [World of Tanks (endursýningar)](game-wot-replays.md), [World of Warships (endursýningar)](game-wows-replays.md).

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | já |
| Upp-ás | `z` |
| Einingar | tommur (Source-einingar) |
| Speglað fyrir skoðarann | `y` |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` (`axes`) hverrar lotu og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem "allowed (reads only what the game publishes)".
- Gerð `replay`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (endursýningar og demó sem leikurinn vistar), svo það skráir bæði í netspilun og án nets; merkið ræður aðeins hvort minni megi nokkurn tíma lesa.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`map`, `rounds`, `score.{team}`, `won`

Lykill í slaufusvigum er fylltur út við keyrslu (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; "Hvað er skráð" hér að ofan nefnir þá.

## Heilleiki {#completeness}

Umbreytirinn sem þetta millistykki keyrir fylgir [breytireglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem endursýningin geymir er lesið eða varðveitt, aldrei sleppt - lesið inn í töfluna og skjal viðureignarinnar, allt annað varðveitt í heild í hliðarskrám við hlið þeirra, talið í `selfCheck.completeness` í skjali viðureignarinnar. Skjölun umbreytisins sjálfs telur upp hvað hann les, geymir óunnið og getur ekki lesið.

## Staðfest {#verified}

umbreytirinn er prófaður á raunverulegum demóum úr mótum; möppuvöktunin og tölfræðin með prófunum

## Heimild {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
