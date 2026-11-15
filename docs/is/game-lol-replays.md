---
title: "League of Legends (endursýningar)"
nav_order: 30
lang: "is"
source: game-lol-replays.md
source_hash: "ed26619fa904"
nav_exclude: true
search_exclude: true
---
# League of Legends (endursýningar) {#league-of-legends-replays}

Eftir leik í League of Legends breytir watcher endursýningunni sem leikurinn vistaði í skrár sem þú getur skoðað á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `lol-replays`, gerð [`replay`](sources-and-rules.md); það keyrir allan tímann (bíður ekki eftir að leikur ræsist) og leitar að nýjum gögnum á 5 s fresti.*

## Hvað er skráð {#what-is-recorded}

- meistari (champion), hlutverk, lið, dráp, dauðsföll, aðstoð, gull, skaði á meisturum og úrslit hvers spilara, og allar aðrar tölur úr stigatöflu leikloka
- þín eigin lína sem tölfræði, og raðirnar þínar nefndar sem þínar (meta.json `player`), með Riot ID þínu í stillingunum
- með þínum eigin Riot API-lykli: staða hvers spilara á hverri mínútu með tölfræði mínútunnar, og sérhver atburður tímalínunnar (dráp þar sem þau gerðust, byggingar, skrímsli, varðstöðvar (wards), hlutir, hæfileikar), á veggklukkutímanum sem tímalínan gefur
- sérhver hluti endursýningarskrárinnar geymdur heill í heat.raw.parquet; ekki afkóðað: leikurinn frá augnabliki til augnabliks, sem er dulkóðaður og gerður óskýr gegn svindli

## Hvaðan það kemur {#where-it-comes-from}

endursýningar sem League-forritið vistar: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (aðeins einföldu lýsigögnin í lok leiks); með þínum eigin Riot API-lykli, opinbera tímalína leiksins úr Match-V5 API Riot

## Hvernig kveikt er á því {#how-to-switch-it-on}

vistaðu endursýningu í League-forritinu (leikjasaga > sækja) og settu upp lesarann: github.com/Holdi601/3DHeat-Ext-Riot (`heat3d-riot-replays`); fyrir stöður stilltu riot_api_key og riot_platform með `config --set`

Stillingar úr umhverfisbreytum:

- `HEAT3D_RIOT_REPLAYS`: mappa lesarans (klón eða útpakkað útgáfusafn), þegar hann er ekki uppsettur eða við hlið watcher

## Hvernig það virkar {#how-it-works}

Endursýningar League of Legends og Valorant: það af þeim sem hægt er að lesa eins og það er.

Báðir leikirnir vista endursýningar á disk spilarans, og báðir verja það sem er inni í þeim:
leikjagögnin frá augnabliki til augnabliks eru gerð óskýr (obfuscated), og öðruvísi í hverri uppfærslu,
til að koma í veg fyrir að þau séu notuð til að svindla. Að komast í gegnum það þýðir að taka
eigin kóða leiksins í sundur, sem skilmálar Riot banna (Terms of Service 3.1 og 7.1)
- svo það er hvergi gert í 3DHeat. Það sem hver skrá ber opið
er lesið, og afgangurinn er geymdur eins og hann er: sérhver hluti skrárinnar, heill, í
`heat.raw.parquet` lotunnar (umbreytingarregla 3DHeat, docs/converters.md í
safni skoðarans), talinn í `selfCheck.completeness` í meta.json.

Watcher les skrárnar ekki sjálft: ytri lesari gerir það (3DHeat
Riot, github.com/Holdi601/3DHeat-Ext-Riot, `exporters/ext/riot-replays`,
skipunin `heat3d-riot-replays`), hafður sér svo að vandamál með skilmála Riot
snerti aðeins þann lesara. Finnist hann á PATH, uppsettur, eða við hlið watcher, les hann
hverja nýja endursýningu; vanti hann segir watcher einu sinni hvernig á að setja hann upp. Það sem
hann les skráir watcher í lotuna; Match-V5-tímalínan hér að neðan er
sótt af watcher sjálfu, þar sem hún er ekki í skránni.

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Báðar útgáfur
ílátsins bera stigatöflu leikloka sem einfaldan JSON (`statsJson`): fyrir hvern
af spilurunum tíu meistarann, dráp, dauðsföll, aðstoð, gull, skaða á
meisturum, hluti, lið, hlutverk, sigur, Riot ID þeirra, og allar aðrar tölur sem
leikurinn leggur saman (yfir hundrað á spilara); allar verða þær að `player_result`-röð
spilarans. ROFL1 (uppfærsla 14.9 og fyrr) hefur hana á eftir föstum haus
(`RIOT\0\0`, 256 bæta undirskrift, svo lengdirnar); ROFL2 (frá 14.11,
`RIOT\2\0`) í lok skrárinnar, lengd hennar í síðustu fjórum bætunum (sagt af
verkfræðingi hjá Riot, ReplayBook issue 299). Haus farmsins í ROFL1 (leikjaauðkenni,
lengd, fjöldi bita (chunks) og lykilramma, lengd lykils bitans) og tafla hans yfir
bita (auðkenni, gerð, lengd, næsti biti, frávik) eru opin og lesin; bitarnir
sjálfir eru dulkóðaðir og geymdir heilir ólesnir.

Stöður koma ekki úr skránni. Með þróunarlykli frá Riot sem spilarinn á sjálfur
(`riot_api_key` í stillingunum; persónulegur lykill er ætlaður einmitt til þessa,
„showing (self) player stats“), er opinbera tímalína leiksins sótt úr
Match-V5 API Riot: staða hvers spilara einu sinni á mínútu með öllu sem
rammi mínútunnar segir um þá (gull, reynsla, stig, litlir óvinir (minions), tölfræði meistara og
skaða), og sérhver atburður tímalínunnar - dráp, byggingar, öflug
skrímsli, varðstöðvar, hlutir, hæfileikar, stig - hver ein röð, þar sem hann gerðist þegar
hann hefur stað. Án lykils er ekkert sótt og ekkert sent.

Sama eining þjónar líka: [VALORANT (endursýningar)](game-valorant-replays.md).

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | já |
| Upp-ás | `y` |
| Einingar | kortaeiningar Summoner's Rift (um 15000 þvert yfir) |
| Speglað fyrir skoðarann | ekkert |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` hverrar lotu (`axes`) og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem „allowed (reads only what the game publishes)“.
- Gerð `replay`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (endursýningar og demó sem leikurinn vistar), svo það skráir bæði í spilun á netinu og án nets; flaggið ræður aðeins því hvort minni megi nokkurn tíma vera lesið.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur sem spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`champion`, `game_seconds`, `won`

Lykill innan slaufusviga er fylltur út á keyrslutíma (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; „Hvað er skráð“ hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [umbreytingarreglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er sérhver pakki, síða, lína eða svar sem millistykkið tekur við geymt heilt í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, og svo hver reitur sem er geymdur með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hverja `type` - `lost` er 0.

**Lesið**

- lýsigagna-JSON: lengd leiks, útgáfa, auðkenni síðasta bita og lykilramma, og `statsJson` - sérhver reitur í stigatöflu hvers spilara á `player_result`-röð hans (tölur sem eru gefnar sem texti lesnar sem tölur)
- ROFL1: lengdablokkin, haus farmsins (leikjaauðkenni, lengd leiks, fjöldi lykilramma og bita, auðkenni upphafs- og leikbyrjunarbita, bil lykilramma, lykill bitans eins og hann er geymdur) og bitataflan (auðkenni, gerð, lengd, næsti biti, frávik) - í meta.json `rofl` og `text` hráu raðanna
- ROFL2: útgáfustrengurinn
- Match-V5-tímalínan (aðeins með eigin API-lykli): sérhver rammi þátttakanda á `position`-röð (eða `participant_frame` án staðar) með alla reiti sína flatta út (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...); sérhver atburður sem röð nefnd eftir gerð sinni, settur þar sem hann hefur `position`, CHAMPION_KILL sem dráp og dauðsfall

**Geymt hrátt**

- sérhver hluti .rofl-skrárinnar, heill, í skráarröð (`offset`), svo hlutarnir eru skráin: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); sérhver kafli sem enginn hluti nær yfir sem `unknown`
- tímalínan heil: `timeline <type>` fyrir hvern atburð, `timeline participantFrame` fyrir ramma hvers spilara (`participant` auðkenni hans), `timeline` fyrir afganginn

**Ekki fáanlegt**

- leikurinn sjálfur (stöður, hæfileikar, sérhver eining, frá augnabliki til augnabliks): bitar ROFL1 og meginmál ROFL2 eru dulkóðuð og pakkarnir inni í þeim gerðir óskýrir í hverri uppfærslu; að komast í gegn þýðir að taka forritið í sundur, sem skilmálar Riot banna (3.1, 7.1). Geymt heilt, ekki lesið
- stöður án þíns eigin Riot API-lykils: skráin hefur engar opnar

**Stærð**: hrá hliðarskráin er um það bil jafn stór og endursýningin sjálf: dulkóðuðu bitarnir þjappast ekki

## Staðfest {#verified}

lesarinn (heat3d-riot-replays) prófaður á skrám sem eru smíðaðar eftir útlitinu í roflxd.cs (MIT); tímalínan á skjalaða JSON-sniði Match-V5; engin raunveruleg endursýning var tiltæk til að prófa á

## Heimild {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
