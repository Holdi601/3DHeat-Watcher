---
title: "VALORANT (endursýningar)"
nav_order: 44
lang: "is"
source: game-valorant-replays.md
source_hash: "a2c4144797e9"
nav_exclude: true
search_exclude: true
---
# VALORANT (endursýningar) {#valorant-replays}

Eftir leik í VALORANT breytir watcher endursýningunni sem leikurinn vistaði í skrár sem þú getur skoðað sem tölfræði og tímalínu.

*Tæknilegar upplýsingar: millistykki `valorant-replays`, gerð [`replay`](sources-and-rules.md); það keyrir allan tímann (bíður ekki eftir að leikur ræsist) og leitar að nýjum gögnum á 5 s fresti.*

## Hvað er skráð {#what-is-recorded}

- kortið, auðkenni leiksins og umboðsmennirnir (agents) sem voru valdir; upplýsingablokk endursýningarinnar (lengd, útgáfur, nafn, upptökutími, fánar um þjöppun og dulkóðun)
- atburðatímalína þjónsins: dráp (drápari og fórnarlamb sem netauðkenni), lotur sem hefjast, gadda (spike) sem er komið fyrir, aftengdir og sprengdir, ofurhæfileikar (ultimates) notaðir, hliðaskipti - hvert með auðkenni sínu og lýsigögnum
- sérhver biti (chunk) skrárinnar geymdur heill í heat.raw.parquet; ekki afkóðað: stöður, nöfn eða stig - þau eru í óskýra straumnum

## Hvaðan það kemur {#where-it-comes-from}

endursýningar sem VALORANT vistar: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (aðeins hlutarnir sem eru ekki óskýrðir)

## Hvernig kveikt er á því {#how-to-switch-it-on}

vistaðu endursýningu í VALORANT (career > match > download replay) og settu upp lesarann: github.com/Holdi601/3DHeat-Ext-Riot (`heat3d-riot-replays`)

Stillingar úr umhverfisbreytum:

- `HEAT3D_RIOT_REPLAYS`: mappa lesarans (klón eða útpakkað útgáfusafn), þegar hann er ekki uppsettur eða við hlið watcher

## Hvernig það virkar {#how-it-works}

Endursýningar League of Legends og Valorant: það af þeim sem hægt er að lesa eins og það er.

Báðir leikirnir vista endursýningar á disk spilarans, og báðir verja það sem er inni í þeim:
leikjagögnin frá augnabliki til augnabliks eru gerð óskýr (obfuscated), og öðruvísi í hverri uppfærslu,
til að koma í veg fyrir að þau séu notuð til að svindla. Sá hluti er hvergi
afkóðaður í 3DHeat. Það sem hver skrá ber opið
er lesið, og afgangurinn er geymdur eins og hann er: sérhver hluti skrárinnar, heill, í
`heat.raw.parquet` lotunnar (umbreytingarregla 3DHeat, docs/converters.md í
safni skoðarans), talinn í `selfCheck.completeness` í meta.json.

Watcher les skrárnar ekki sjálft: ytri lesari gerir það (3DHeat
Riot, github.com/Holdi601/3DHeat-Ext-Riot, `exporters/ext/riot-replays`,
skipunin `heat3d-riot-replays`), sjálfstætt verkefni. Finnist hann á PATH, uppsettur, eða við hlið watcher, les hann
hverja nýja endursýningu; vanti hann segir watcher einu sinni hvernig á að setja hann upp. Það sem
hann les skráir watcher í lotuna; Match-V5-tímalínan hér að neðan er
sótt af watcher sjálfu, þar sem hún er ekki í skránni.

#### Valorant (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, staðbundin endursýning Unreal Engine. Opið:
upplýsingablokk endursýningarinnar (lengd, netútgáfa, changelist, nafn hennar, hvenær hún
var tekin upp, hvort hún er þjöppuð eða dulkóðuð), kortið, auðkenni leiksins og
umboðsmennirnir sem voru valdir (í hausnum), og eigin atburðatímalína þjónsins - dráp
(drápari og fórnarlamb sem netauðkenni, ekki nöfn), lotur sem hefjast, gaddar sem er komið fyrir,
aftengdir og sprengdir, ofurhæfileikar notaðir, hliðaskipti - hvert með tíma sínum,
auðkenni og lýsigögnum. Stöður, nöfn, stig og allt annað er í
óskýra straumnum (bitar endursýningargagna og eftirlitspunkta), sem er geymdur heill
og ekki lesinn.

Sama eining þjónar líka: [League of Legends (endursýningar)](game-lol-replays.md).

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | nei |
| Upp-ás | `z` |
| Einingar | heimseiningar VALORANT |
| Speglað fyrir skoðarann | ekkert |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` hverrar lotu (`axes`) og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem „allowed (reads only what the game publishes)“.
- Gerð `replay`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (endursýningar og demó sem leikurinn vistar), svo það skráir bæði í spilun á netinu og án nets; flaggið ræður aðeins því hvort minni megi nokkurn tíma vera lesið.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur sem spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

Lykill innan slaufusviga er fylltur út á keyrslutíma (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; „Hvað er skráð“ hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [umbreytingarreglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er sérhver pakki, síða, lína eða svar sem millistykkið tekur við geymt heilt í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, og svo hver reitur sem er geymdur með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hverja `type` - `lost` er 0.

**Lesið**

- upplýsingablokkin, sérhver reitur (meta.json `vrf`): skráarútgáfa, sérútgáfur, lengd, netútgáfa, changelist, nafn, fáni fyrir beina útsendingu, upptökutími, fánar um þjöppun og dulkóðun, lykillinn eins og hann er geymdur
- hausbitinn: kortið, auðkenni leiksins og umboðsmennirnir sem voru valdir (fundnir eftir lögun þeirra)
- sérhver atburðabiti: auðkenni, hópur, lýsigögn, upphafs- og lokatími, og af gögnum hans nafn atburðarins, tími hans í sekúndum og tölurnar á undan honum (netauðkenni drápara og fórnarlambs) - ein röð hver

**Geymt hrátt**

- sérhver biti heill, í skráarröð (`offset`), svo hlutarnir eru skráin: `info`, `header`, `event <group>`, `replay_data`, `checkpoint`, `chunk <n>` fyrir gerð sem útlitið nefnir ekki, `trailing` fyrir bæti á eftir síðasta heila bitanum

**Ekki fáanlegt**

- stöður, nöfn, stig, hæfileikar, sérhver rammi leiksins: bitar endursýningargagna og eftirlitspunkta eru óskýrðir. Geymt heilt, ekki lesið
- innihald dulkóðaðrar endursýningar: farið í gegnum og geymt heilt, ekkert lesið inni í því

**Stærð**: hrá hliðarskráin er um það bil jafn stór og endursýningin sjálf: óskýrði straumurinn þjappast ekki

## Staðfest {#verified}

lesarinn (heat3d-riot-replays) er smíðaður eftir ílátsútlitinu sem vrfkit skjalar (Apache-2.0); óprófaður á raunverulegri endursýningu, engin var tiltæk - athugar fyrir lestur og sleppir því sem passar ekki

## Heimild {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
