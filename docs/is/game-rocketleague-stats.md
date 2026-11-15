---
title: "Rocket League (leikjastaða)"
nav_order: 39
lang: "is"
source: game-rocketleague-stats.md
source_hash: "fd70d0540bb9"
nav_exclude: true
search_exclude: true
---
# Rocket League (leikjastaða) {#rocket-league-game-state}

Meðan þú spilar Rocket League vistar watcher það sem leikurinn segir forritum á þinni eigin tölvu, svo þú getir skoðað það síðar á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `rocketleague-stats`, gerð [`gsi`](sources-and-rules.md); það keyrir meðan `RocketLeague.exe` er í gangi og leitar að nýjum gögnum á 0,05 s fresti.*

## Hvað er skráð {#what-is-recorded}

- boltaspörk með stað boltans (XYZ, Unreal-einingar), hver sparkaði og hraðann
- mörk með höggstað, markaskorara, aðstoðarmanni og hraða; skot í þverslá með stað
- stat feed (eyðingar (demolitions), varsla, skot, stórvarsla, ...), upphafsspörk, endursýningar, upphaf og lok leiks, sigurvegari
- eigin mörk, aðstoð, varsla, skot, eyðingar, snertingar, stig og stig liðanna, úr UpdateState
- lokalína hvers spilara við leikslok
- þínar eigin raðir sem `me`: spilarinn sem er nefndur í stillingunum (`config --set player_names.rocketleague-stats=<name>`), annars sá sem myndavél leiksins fylgir utan endursýninga
- engar stöður bíla: API-ið hefur engar

## Hvaðan það kemur {#where-it-comes-from}

Stats API: TCP JSON-straumur frá 127.0.0.1:49123 (Port í &lt;RL>\TAGame\Config\TAStatsAPI.ini eða DefaultStatsAPI.ini)

## Hvernig kveikt er á því {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (stillir PacketSendRate=30), ræstu svo Rocket League

Sláðu skipunina inn í Terminal sem er opnaður í möppu watcher (sjá [Áður en þú byrjar](before-you-start.md)). Ef hún mistekst segir síðasta línan hvers vegna; [Uppsetning og keyrsla](installing-and-running.md) fjallar um algengustu ástæðurnar.

`python -m heat3d_watch setup rocketleague-stats` sýnir skrárnar sem hún myndi breyta; `python -m heat3d_watch setup rocketleague-stats --apply` breytir þeim og geymir upprunalegu skrána sem `<file>.heat3d-backup` (sjá [Skipanir](commands.md#setup)). Hún prentar `rocketleague-stats: changed: ...` fyrir hverja breytingu, eða `rocketleague-stats: nothing to change` þegar kveikt er þegar á þessu.

## Hvernig það virkar {#how-it-works}

Rocket League: opinbera Stats API, staðbundin tengi (socket) sem leikurinn skrifar leikgögn í.

Kveikt í `<RL>\TAGame\Config\TAStatsAPI.ini` - eða `DefaultStatsAPI.ini`
þegar hin er ekki til, sem leikurinn les aðeins þá - undir
`[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   UpdateState messages per second; 0 (the default) switches the API off, at most 120
Port             the TCP port the game listens on, default 49123 (WebPort 49124 is a WebSocket copy)
```

Leikurinn er þjónninn: biðlari tengist 127.0.0.1:49123 og les straum
JSON-hluta `{"Event": name, "Data": {...}}` (sumar útgáfur senda Data sem
JSON-streng), hvern á eftir öðrum án skiljutákna. Atburðir eru sendir á
tikkinu sem þeir gerast, óháð tíðninni:

```text
UpdateState   MatchGuid, Players[] (Name, PrimaryId, Shortcut, TeamNum 0 blue / 1 orange,
              Score, Goals, Shots, Assists, Saves, Touches, CarTouches, Demos; car state
              only for spectators), Game (Teams[], TimeSeconds, bOvertime, Ball {Speed,
              TeamNum}, bReplay, bHasWinner, Winner, Arena, bHasTarget, Target)
BallHit       Players[] (Name, Shortcut, TeamNum), Ball {PreHitSpeed, PostHitSpeed, Location {X,Y,Z}}
GoalScored    GoalSpeed, GoalTime, ImpactLocation {X,Y,Z}, Scorer, Assister, BallLastTouch
CrossbarHit   BallLocation {X,Y,Z}, BallSpeed, ImpactForce, BallLastTouch
StatfeedEvent EventName, Type, MainTarget, SecondaryTarget
MatchEnded    WinnerTeamNum
MatchCreated, MatchInitialized, CountdownBegin, RoundStarted, GoalReplayStart/WillEnd/End,
MatchPaused/Unpaused, PodiumStart, ReplayCreated, MatchDestroyed, ClockUpdatedSeconds
```

Staðir eru Unreal-einingar (sentimetrar), Z upp; völlurinn er um 8200 x 10240
með mörkin við Y = +-5120. Stöður bíla eru ekki hluti af API-inu: það sem hefur
stað er boltinn þar sem honum var sparkað, hann skoraði eða hitti þverslána.

Sérhver skilaboð eru líka geymd heil (umbreytingarregla 3DHeat, docs/converters.md
í safni skoðarans): `heat.raw.parquet`, `type` er Event-nafn skilaboðanna,
`text` er hluturinn eins og hann kom úr straumnum. UpdateState sem er bæti fyrir bæti
eins og sá á undan (leikur í bið, valmynd) er geymdur einu sinni og talinn í `unchanged_replies`
í meta.json. Skilaboð milli leikja bíða í biðröð eftir lotu næsta
leiks; það sem er eftir þegar leikurinn lokast fær sína eigin lotu.
Stafir milli hluta sem eru ekki JSON eru geymdir sem „junk“.

Heimildir: <https://www.rocketleague.com/en/developer/stats-api> (opinbera síðan);
há- og lágstafir reita og TCP-rammasniðið staðfest gegn rlstatsapi-biðlaranum
(<https://docs.rs/crate/rlstatsapi>, MIT; lesinn aðeins fyrir staðreyndir).

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | já |
| Upp-ás | `z` |
| Einingar | Unreal-einingar (sentimetrar) |
| Speglað fyrir skoðarann | ekkert |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` hverrar lotu (`axes`) og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem „allowed (reads only what the game publishes)“.
- Gerð `gsi`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (game-state integration eða staðbundið API sem leikurinn þjónar), svo það skráir bæði í spilun á netinu og án nets; flaggið ræður aðeins því hvort minni megi nokkurn tíma vera lesið.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur sem spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

Lykill innan slaufusviga er fylltur út á keyrslutíma (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; „Hvað er skráð“ hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [umbreytingarreglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er sérhver pakki, síða, lína eða svar sem millistykkið tekur við geymt heilt í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, og svo hver reitur sem er geymdur með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hverja `type` - `lost` er 0.

**Lesið**

- BallHit (staður, hver, lið, hraði fyrir og eftir), GoalScored (höggstaður, skorari, aðstoðarmaður, hraði, markatími), CrossbarHit (staður, síðasta snerting, hraði, kraftur), StatfeedEvent (atburður, gerð, aðal- og aukamarkmið), MatchEnded (sigurvegari, úrslit), nafn sérhvers annars atburðar sem röð
- úr UpdateState: völlurinn, skotmark myndavélarinnar utan endursýninga (hver `me` er), stig liða, mörk, aðstoð, varsla, skot, eyðingar, snertingar, bílsnertingar og stig hvers spilara (eigin sem tölfræði, allra sem `player_result` við leikslok); framlenging úr ClockUpdatedSeconds

**Geymt hrátt**

- sérhver skilaboð heil eins og þau komu úr straumnum (`text`), undir eigin Event-nafni: `UpdateState` (PrimaryId og Shortcut hvers spilara, klukkan, hraði og lið boltans, nöfn og litir liða, fánar um endursýningu og sigurvegara, og bílástand þar sem leikurinn sendir það), `BallHit`, `GoalScored` (með síðustu snertingu boltans), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` og sérhver atburður sem síðari útgáfa bætir við
- UpdateState sem er bæti fyrir bæti eins og sá á undan (bið, valmyndir) er geymdur einu sinni og talinn (`unchanged_replies` í meta.json)
- skilaboð milli leikja: á sínum eigin tíma fyrir upphaf næsta leiks; eftir síðasta leik, í lotu út af fyrir sig (`raw_only` í meta.json)
- `unreadable`: hlutur sem er ekki Stats API-skilaboð; `junk`: stafir milli hluta

**Ekki fáanlegt**

- stöður bíla og bílástand meðan spilað er: leikurinn sendir þær aðeins til áhorfenda
- UpdateState milli tveggja sendinga: leikurinn sendir PacketSendRate á sekúndu (`setup` stillir 30, leikurinn leyfir allt að 120); atburðirnir eru sendir á tikkinu sem þeir gerast
- WebSocket-afritið á WebPort (49124): sömu skilaboð og á TCP-gáttinni, ekki lesin tvisvar

**Stærð**: UpdateState er 1-3 KB fyrir sex spilara, 30 á sekúndu: um 100-300 MB á klukkustund í `raw.bin` meðan leikur stendur yfir, tíundi hluti eða minna í zstd `heat.raw.parquet` (áætlað út frá skjalaða sniðinu, ekki mælt í leiknum)

## Staðfest {#verified}

prófað á skilaboðum á skjalaða sniðinu sem falskur staðbundinn þjónn sendi; óprófað á móti leiknum

## Heimild {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
