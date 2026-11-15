---
title: "League of Legends (leikjastaða)"
nav_order: 29
lang: "is"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (leikjastaða) {#league-of-legends-game-state}

Meðan þú spilar League of Legends vistar watcher það sem leikurinn tilkynnir til forrita á þinni eigin tölvu, svo þú getir skoðað það síðar sem tölfræði og tímalínu.

*Tæknilegar upplýsingar: millistykki `lol-live`, gerð [`gsi`](sources-and-rules.md); það keyrir meðan `League of Legends.exe` er í gangi og leitar að nýjum gögnum á 0,5 s fresti.*

## Hvað er skráð {#what-is-recorded}

- engar staðsetningar: API hefur engar
- dráparás (kill feed): dráp, dauðsföll og stoðsendingar spilarans, dráp annarra hetja með banamanni, fórnarlambi og aðstoðarmönnum
- drekar, heraldar, barónar, turnar, hemlar (inhibitors), fjöldadráp (multikills), ace, fyrsta blóð, upphaf og endir leiks
- eigin dráp, dauðsföll, stoðsendingar, creep score, ward score, stig (level), gull, hetja, leiktími, niðurstaða
- markmið sem lið spilarans tók

## Hvaðan það kemur {#where-it-comes-from}

Live Client Data API leikjabiðlarans, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), meðan á leik stendur

## Hvernig kveikt er á því {#how-to-switch-it-on}

Ekki þarf að kveikja á neinu: watcher les heimildina eins og leikurinn eða vettvangurinn lætur hana í té.

## Hvernig það virkar {#how-it-works}

League of Legends: Live Client Data API sem leikjabiðlarinn þjónar meðan á leik stendur.

Meðan leikur stendur yfir (líka í æfingaverkfærinu og áhorfendaham) svarar `League of
Legends.exe` á <https://127.0.0.1:2999> með því sem spilarinn getur séð í
viðmóti leiksins sjálfs:

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} from EventID N on: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

Engar staðsetningar eru til: API hefur engar, svo League-lota er atburðir og
tölfræði, án hitatöflu. Vottorðið er sjálfundirritað, af eigin
rótarvottorði Riot (`riotgames.pem`, birt á
<https://static.developer.riotgames.com/docs/lol/riotgames.pem>). Notkunarskilmálar þess
eru ekki tilgreindir, svo það fylgir ekki með: settu það í `<data>\riotgames.pem` og
tengingin er staðfest með því; án þess er staðfesting slökkt - og aðeins
fyrir 127.0.0.1, einu vistfangið sem þetta millistykki talar við.

Stefna Riot leyfir verkfærum að sýna það sem spilarinn gæti vitað úr leiknum
sjálfum, og ekkert reiknað umfram það (engar tímamælingar óvina): þetta skráir dráparásina
og stigatöfluna sem spilarinn sér, og eigin tölur spilarans.

Sérhvert svar er líka geymt heilt (umbreytingarregla 3DHeat, docs/converters.md í
geymslu skoðarans): `heat.raw.parquet`, `type` endapunkturinn
(„allgamedata“, „eventdata“), `text` JSON eins og biðlarinn sendi það, `status`
þegar það var ekki 200. Svar sem er bæti fyrir bæti hið sama og það fyrra frá sama endapunkti (atburðalistinn
meðan ekkert gerist) er geymt einu sinni og talið í `unchanged_replies` í meta.json.
allgamedata hefur allt sem hinir endapunktarnir þjóna
(activeplayer\*, playerlist, playerscores, playeritems, playersummonerspells,
playermainrunes, gamestats), svo þeir eru ekki spurðir sérstaklega. Svör áður en
leikur hefst (hleðsluskjárinn) bíða í biðröð og fara í lotu leiksins;
eftir GameEnd er lotan opin þar til biðlarinn fer, svo svör
lokaskjásins eru geymd með henni.

Heimild: <https://developer.riotgames.com/docs/lol#game-client-api>

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | nei |
| Upp-ás | `z` |
| Einingar | engar (engar staðsetningar) |
| Speglað fyrir skoðarann | ekkert |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` hverrar lotu (`axes`) og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem „allowed (reads only what the game publishes)“.
- Gerð `gsi`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (game-state integration eða staðbundið API sem leikurinn þjónar), svo það skráir bæði í netspilun og án nets; flaggið ræður aðeins því hvort minni megi nokkurn tíma vera lesið.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur sem spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

Lykill innan slaufusviga er fylltur út á keyrslutíma (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; „Hvað er skráð“ hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [umbreytingarreglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er sérhver pakki, síða, lína eða svar sem millistykkið tekur við geymt heilt í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, og svo hver reitur sem er geymdur með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hverja `type` - `lost` er 0.

**Lesið**

- dráparásin úr eventdata: hver atburður einu sinni, nefndir reitir hans afkóðaðir (banamaður, fórnarlamb og aðstoðarmenn með hetju og liði, byggingar og hlið þeirra, tegund dreka, þjófnaðir, fjöldadráp, ace, fyrsta blóð, niðurstaðan) og sérhver annar reitur atburðar á röð hans undir eigin nafni
- úr allgamedata: eigin dráp, dauðsföll, stoðsendingar, creep score, ward score, stig, gull, hetja, leiktíminn, leikjahamur og kort

**Geymt hrátt**

- `allgamedata`: hvert svar heilt (`text`), á 2 s fresti - activePlayer (hæfileikar, öll hetjutölfræði, fullar rúnir, gull, stig), allPlayers (hlutir með raufum og verði, rúnir, galdrar kallarans (summoner spells), stig, stig (level), dauður og endurfæðingartími, skinn, braut (lane), bot), atburðirnir, gameData (hamur, tími, kort, landslag); `used` satt meðan leikur stendur yfir, ósatt á lokaskjánum
- `eventdata`: hvert svar heilt, spurt á 0,5 s fresti frá næsta atburðarnúmeri; `used` satt þegar það kom með nýja atburði
- svar sem er bæti fyrir bæti hið sama og það fyrra frá sama endapunkti er geymt einu sinni og talið (`unchanged_replies` í meta.json); villusvör (RESOURCE_NOT_FOUND á hleðsluskjánum) eru geymd með `status` sínu, áður en leikur hefst

**Ekki fáanlegt**

- staðsetningar: API hefur engar (ekkert smákort, engin hnit)
- hinir endapunktarnir (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): hver þjónar hluta af allgamedata, svo þeir eru ekki spurðir
- Replay API (`/replay/*` á sömu gátt): það spilar endursýningar og leiki sem horft er á þegar kveikt er á því í game.cfg, það er ekki hluti af leik sem er spilaður
- lockfile-endapunktar League-biðlarans: ekki birt API (Heimildir og reglur)
- gildi milli tveggja lestra: API svarar þegar spurt er og ýtir ekki; stigataflan er spurð á 2 s fresti, atburðirnir á 0,5 s fresti

**Stærð**: allgamedata er 15-40 KB (það ber allan atburðalistann, sem vex) á 2 s fresti: um 30-70 MB á klukkustund í `raw.bin`; eventdata bætir litlu við, þar sem óbreytt svör eru talin, ekki geymd; zstd minnkar endurtekið JSON í `heat.raw.parquet` í nokkur MB á klukkustund (áætlað út frá skjalaða sniðinu)

## Staðfest {#verified}

prófað á móti gervi-staðbundnum þjóni sem þjónar svörum á skjalaða sniðinu; óprófað á móti leiknum

## Heimild {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
