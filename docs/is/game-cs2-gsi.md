---
title: "Counter-Strike 2 (leikjastaða)"
nav_order: 9
lang: "is"
source: game-cs2-gsi.md
source_hash: "2eda1106e11f"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (leikjastaða) {#counter-strike-2-game-state}

Meðan þú spilar Counter-Strike 2 vistar watcher það sem leikurinn tilkynnir til forrita á þinni eigin tölvu, svo þú getir skoðað það síðar á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `cs2-gsi`, gerð [`gsi`](sources-and-rules.md); það keyrir meðan `cs2.exe` er í gangi og leitar að nýjum gögnum á 0,05 s fresti.*

## Hvað er skráð {#what-is-recorded}

- eigin staða (heimshnit XYZ, tommur) og sjónstefna allt að 10 Hz meðan þú ert á lífi
- endurfæðingar (fyrsta sjáanlega staða í hverri lotu, endurlífgun) og dauðsföll (heilsa niður í 0, eða dauðatalan)
- dráp með virka vopninu, úr leiktölfræðinni
- lotur (upphaf, endir, sigurvegari), sprengja sett/aftengd/sprungin, leikfasar og niðurstaðan
- dráp, aðstoð, dauðsföll, MVP, stig, peningar, skaði, höfuðskotsdráp, unnar og tapaðar lotur

## Hvaðan það kemur {#where-it-comes-from}

Game State Integration: HTTP POST á 127.0.0.1:3311, stillt með &lt;CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg

## Hvernig á að kveikja á því {#how-to-switch-it-on}

`python -m heat3d_watch setup cs2-gsi --apply`, ræstu síðan CS2 (það les skrána við ræsingu)

Sláðu skipunina inn í terminal sem er opnaður í möppu watcher (sjá [Áður en þú byrjar](before-you-start.md)). Ef hún mistekst segir síðasta línan hvers vegna; [Uppsetning og keyrsla](installing-and-running.md) fer yfir algengustu orsakirnar.

`python -m heat3d_watch setup cs2-gsi` sýnir þær skrár sem það myndi breyta; `python -m heat3d_watch setup cs2-gsi --apply` breytir þeim og geymir frumritið sem `<file>.heat3d-backup` (sjá [Skipanir](commands.md#setup)). Það skrifar `cs2-gsi: changed: ...` fyrir hverja breytingu, eða `cs2-gsi: nothing to change` þegar kveikt er nú þegar.

Stillingar úr umhverfisbreytum:

- `HEAT3D_CS2_GSI_PORT`: gáttin sem leikurinn sendir á (sjálfgefið 3311); cfg-skrá leiksins verður að nefna sömu gátt

## Hvernig það virkar {#how-it-works}

Valve Game State Integration: Counter-Strike 2 og Dota 2 segja staðbundnum vefþjóni hvað gerist.

Báðir leikirnir lesa hverja `gamestate_integration_*.cfg` í cfg-möppunni sinni þegar
þeir ræsast, og senda eftir það JSON-skjal með POST á `uri` hverrar skrár þegar
staðan breytist (í mesta lagi á `throttle` sekúndna fresti, og á `heartbeat` sekúndna fresti
þegar ekkert breytist). Watcher er þessi vefþjónn: hann hlustar aðeins á 127.0.0.1,
svarar hverju POST strax með 200 og vinnur verkið í sínum eigin könnunarþræði.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

Það sem spilara er sent - og þar með það sem hægt er að skrá - er það sem leikurinn
ákveður að spilari megi sjá:

- CS2: `provider` (eigið steamid), `map` (heiti, hamur, fasi warmup/live/
  intermission/gameover, lota, stig team_ct/team_t), `round` (fasi
  freezetime/live/over, sprengja planted/exploded/defused, win_team), `player` (sá
  spilari sem er *fylgst með*: maður sjálfur meðan á lífi, liðsfélagi eftir dauða) með
  `state` (health, armor, money, round_kills, round_killhs, round_totaldmg),
  `match_stats` (kills, assists, deaths, mvps, score), `position` og `forward`
  sem strengir "x, y, z" í heimseiningum (tommur, Z upp), `weapons`; `bomb` aðeins fyrir
  áhorfendur. Staða annarra spilara (`allplayers_*`) er aðeins send til
  áhorfenda og GOTV, svo þeirra er ekki beðið.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player`
  (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero`
  (xpos/ypos í heimseiningum, level, alive, respawn_seconds), `buildings`
  (heilsa hvers turns/barracks/ancient), `roshan`, `events` (roshan_killed,
  aegis_picked_up, ...). Engin hæð er til: z er 0. Einnig beðið um, og geymt
  í heild: `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`,
  `neutralitems`, `league` (leikurinn sendir það sem biðlari spilarans sjálfs hefur;
  óprófað er hver þeirra innihalda eitthvað þegar spilað er í stað þess að horfa á).

Hvert skjal er líka geymt í heild (breytireglan í 3DHeat,
docs/converters.md í geymslu skoðarans): `heat.raw.parquet`, `type`
"gsi", `text` er JSON eins og það var sent - aðeins token cfg-skrárinnar er afmáð, það er
leyndarmál watcher sjálfs, ekki leikjagögn. Skjöl sem berast meðan engin viðureign er opin
(valmyndir, hleðsla, milli viðureigna) bíða í `Backlog` og fara í lotu
næstu viðureignar, á undan upphafi hennar; það sem er eftir þegar leikurinn lokast fær
sína eigin lotu sem geymir aðeins þau. Ólæsileg POST og POST með rangt
token eru einnig geymd ("gsi-unreadable", "gsi-bad-auth").

Heimildir: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration>
(sniðið sem CS2 hélt), <https://github.com/antonpup/CounterStrike2GSI> og
<https://github.com/antonpup/Dota2GSI> (reitalistar; MIT, lesið aðeins fyrir staðreyndir).

Sama eining þjónar líka: [Dota 2 (leikjastaða)](game-dota2-gsi.md).

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | já |
| Upp-ás | `z` |
| Einingar | tommur (Hammer-einingar) |
| Speglað fyrir skoðarann | `y` |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` (`axes`) hverrar lotu og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem "allowed (reads only what the game publishes)".
- Gerð `gsi`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (game-state integration eða staðbundið API sem leikurinn þjónar), svo það skráir bæði í netspilun og án nets; merkið ræður aðeins hvort minni megi nokkurn tíma lesa.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `money`, `result`, `score_other`, `score_own`

Lykill í slaufusvigum er fylltur út við keyrslu (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; "Hvað er skráð" hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [breytireglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er hver pakki, síða, lína eða svar sem millistykkið fær geymt í heild í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, svo hver reitur sem geymdur er með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hvert `type` - `lost` er 0.

**Lesið**

- staða, sjónstefna, heilsa, skjöldur, peningar, virkt vopn, hjálmur, afvopnunarsett, magn blindunar/reyks/elds og verðmæti búnaðar þess spilara sem fylgst er með, á hverri stöðuröð meðan það er spilarinn sjálfur (steamid provider = steamid player)
- endurfæðingar, dauðsföll (heilsa niður í 0, eða dauðatala leiktölfræðinnar), dráp (drápatalan hækkar)
- leikfasar, lotur (freeze time, live, over, sigurvegari), sprengja sett/aftengd/sprungin, niðurstaðan
- dráp, aðstoð, dauðsföll, MVP, stig, peningar, skaði, höfuðskotsdráp, unnar og tapaðar lotur sem tölfræði

**Geymt óunnið**

- `gsi`: hvert skjal sem leikurinn sendir, í heild, eins og það var sent (`text`), `used` er satt þegar það var lesið í viðureign - provider (útgáfa, tímastimpill), map (hamur, liðaheiti, samfelld lotutöp, leikhlé, seríusigrar, `round_wins` með sigurskilyrði hverrar lotu), round, spilarinn sem fylgst er með (klan, áhorfendarauf, virkni, hvert vopn með skinni, skotfærum og varaskotfærum), bomb, niðurtalning fasa, og eigin `previously`/`added` mismunur leiksins miðað við póstinn á undan
- skjöl úr valmyndum, hleðslu og milli viðureigna: geymd á sama hátt, á sínum eigin tíma fyrir upphaf næstu viðureignar; eftir síðustu viðureign, í lotu út af fyrir sig (`raw_only` í meta.json)
- `gsi-unreadable`: POST sem er ekki JSON-hlutur, bætin hans sem `payload` og `length`
- `gsi-bad-auth`: POST með annað token en cfg-skráin

**Ekki tiltækt**

- aðrir spilarar (`allplayers_*`) og handsprengjur (`allgrenades`): leikurinn sendir þær aðeins til áhorfenda og GOTV, og watcher biður ekki um þær (Heimildir og reglur); demó hefur alla spilara - sjá [Counter-Strike 2 (endursýningar)](game-cs2-demos.md)
- ástand milli pósta: leikurinn sendir í mesta lagi á 0,1 s fresti (`throttle`) og aðeins við breytingu, annars á 10 s fresti (`heartbeat`)
- token cfg-skrárinnar, afmáð í hverju geymdu skjali: leyndarmál watcher sjálfs, ekki leikjagögn
- póstar umfram 10.000 í bið (watcher stöðvaðist) eru taldir sem `dropped_packets`, ekki geymdir; póstur yfir 4 MB er geymdur sem `gsi-unreadable` með lengdinni en án bætanna

**Stærð**: skjal spilara er 2-4 KB og er sent allt að 10 sinnum á sekúndu meðan eitthvað breytist: um 30-150 MB á klukkustund í `raw.bin` meðan viðureignin stendur, tíunda hluta af því eða minna í zstd-þjappaða `heat.raw.parquet` (áætlað út frá útgefnu sniði, ekki mælt í leiknum)

## Staðfest {#verified}

prófað á skjölum á útgefnu GSI-sniði sem send voru til millistykkisins í keyrslu; uppsetning og leit að cfg-möppu prófuð á staðbundinni uppsetningu; óprófað gegn leiknum í keyrslu

## Heimild {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
