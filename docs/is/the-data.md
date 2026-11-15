---
title: "Gögnin"
nav_order: 5
lang: "is"
source: the-data.md
source_hash: "6150cdc022fc"
nav_exclude: true
search_exclude: true
---
# Gögnin {#the-data}

Allar upptökur eru venjulegar skrár í gagnamöppunni (`%LOCALAPPDATA%\3DHeat\Watcher` nema henni sé breytt,
sjá [Uppsetning og keyrsla](installing-and-running.md#where-everything-is)). Þú getur lesið þær, afritað eða
eytt þeim án watcher. `.jsonl` skrá er venjulegur texti, einn atburður í línu (Notepad opnar hana);
`.parquet` skrá er tafla sem 3DHeat-skoðarinn opnar (Excel gerir það ekki - `stats --csv` skrifar CSV-
skrár fyrir töflureikna).

## Lotumöppur {#session-folders}
![lotumappa](../assets/img/session-folder.svg)


**Lota** (session) er ein seta með einni heimild: frá þeirri stundu sem leikurinn segir fyrst eitthvað þar til hún
endar (leikurinn lokast, leik lýkur, akstur eða flug er endurstillt - síða hvers millistykkis segir hvað
byrjar og endar loturnar). Hver lota fær möppu:

```text
<data>\sessions\<game>\<YYYY-MM-DD_HH-MM-SS>_<adapter id>\
    events.jsonl
    heat.parquet
    meta.json
```

- `<game>` er nafn leiksins þar sem hver stafur annar en bókstafir, tölustafir, `.`, `_` og `-`
  er settur í stað `-` (í mesta lagi 60 stafir): `EA-SPORTS-F1-25`, `Counter-Strike-2`. Millistykki sem ná yfir
  marga leiki (Steam-tölfræði, Steam Timeline, NVIDIA hápunktar) skrá hverja lotu undir leiknum sem hún
  tilheyrir.
- Tíminn er upphaf lotunnar í staðartíma. Lotur sem lýsa fortíðinni (endursýning umbreytt
  eftir leikinn, Steam-tölfræðiskrá) nota tímann sem leikurinn eða skráin gefur. Tvær lotur sem byrja á
  sömu sekúndu fá `_2`, `_3`, ... aftan við.
- Auðkenni lotunnar, í tölfræðigagnagrunninum, er `<game folder>/<session folder>`.

Lota þar sem ekkert var skráð (leikurinn sat í valmyndum, eða hrundi við ræsingu) er
eytt þegar henni lýkur, svo hver ræsing skilur ekki eftir tóma möppu.

Sumar lotur geyma fleiri skrár. Counter-Strike 2 demólota geymir eigin töflu og samantekt breytisins
(`<map>/<match>.parquet`, `<match>.match.json`). iRacing lota telur upp `.ibt` skrárnar sem
hermirinn skrifaði á meðan setunni stóð sem `telemetry_file` atburði.

## events.jsonl {#eventsjsonl}

`events.jsonl` hefur eitt JSON-hlut í línu, eina línu fyrir hvern atburð, skrifaða um leið og atburðurinn
gerist. Skráin er línubuffruð, svo hrun, rafmagnsleysi eða drepið ferli tapar engu sem var
þegar skrifað; lína sem hrun styttir er sleppt þegar skráin er lesin, og hver lína á undan
stendur.

Hver lína hefur sömu grunndálka:

| Dálkur | Gerð | Hvað það er |
|---|---|---|
| `time` | tala | sekúndur síðan lotan hófst (4 aukastafir), eða eigin klukka leiksins þar sem millistykkið gefur hana |
| `ms` | heiltala | veggklukkutími, Unix millisekúndur |
| `event` | texti | hvað gerðist: `position`, `spawn`, `death`, `kill`, `lap`, `teleport`, `session_start`, ... |
| `x`, `y`, `z` | tala | hvar, í eigin einingum og ásum leiksins (sjá `axes` í `meta.json`); aðeins til staðar þegar allir þrír eru þekktir og endanlegir |
| `player` | texti | hver: nafn, auðkenni, eða `me` fyrir þann sem spilar (sjá [Eigin raðir spilarans](#the-players-own-rows)) |
| `team` | texti | lið þeirra, þegar leikurinn segir það |
| `session` | texti | leikurinn, umferðin, leiðin, lífið eða flugið sem röðin tilheyrir, þegar leikurinn segir það |

Hvert annað svið sem leikurinn tilkynnir kemur á eftir undir eigin nafni (`speed_kmh`, `gear`, `lap_time`, `weapon`,
`victim`, `hero`, ...). Svið án gildis eru sleppt, og tölur sem eru ekki endanlegar líka.
Tvær gervilínur:

```json
{"time":12.3456,"ms":1777660501123,"event":"position","x":-412.5,"y":12.1,"z":233.0,"player":"me","session":"1","speed_kmh":187.4,"gear":5}
{"time":15.0,"ms":1777660503667,"event":"lap","x":-380.2,"y":12.0,"z":250.9,"player":"me","session":"1","lap_time":92.418,"lap":3}
```

Raðir án staðsetningar (lína í dráparunu, stigahækkun, tölfræðibreyting) haldast í `events.jsonl` og teljast
í tölfræðinni. Aðeins raðir með staðsetningu fara í töfluna.

### Eigin raðir spilarans {#the-players-own-rows}

Heimildin segir hvaða raðir eru þess sem spilar, aldrei giskað. Röð er spilarans sjálfs þegar

- `player` hennar er `me`: flest millistykki, þar sem heimildin er eigin leikur spilarans (fjarmæling eigin
  bíls eða flugvélar, game-state integration, dagbók);
- hún ber `own_car` 1: kappakstursleikirnir sem skrá hvern bíl undir nafni ökumanns síns (EA SPORTS F1
  eftir bílvísi spilarabílsins í leiknum, RaceRoom eftir eigin raufu, Automobilista 2 og Project CARS 2 eftir
  þátttakandanum sem er skoðaður) merkja bíl spilarans þannig og halda nafni ökumannsins í `player`;
- `player` hennar er `player` lotunnar í `meta.json`: nafnið sem heimildin gefur spilaranum - foringi Elite
  Dangerous (dagbókin er alltaf spilarans), lína Riot ID úr stillingunum í League of Legends endursýningu.

War Thunder og Rocket League nefna hvern leikmann og segja ekki hver þú ert; með nafninu þínu í
stillingunni `player_names` (sjá [Stillingar](installing-and-running.md#settings)) verða raðirnar þínar `me`.
[NVIDIA hápunktar](nvidia-highlights.md) fletta stund upp í nákvæmlega þessum röðum.

## heat.parquet {#heatparquet}

Þegar lota lokast eru raðir `events.jsonl` sem hafa `x`, `y` og `z` skrifaðar í
`heat.parquet`. Þetta er taflan sem 3DHeat-skoðarinn opnar. Ef lotan hefur engar staðsetningar er engin tafla
skrifuð.

- Dálkarnir eru `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session`, og svo hvert
  annað svið í þeirri röð sem það birtist fyrst.
- `x`, `y`, `z` og `time` eru 64 bita fleytitölur og `ms` er 64 bita heiltala. Annar dálkur þar sem öll
  gildin eru tölur er 64 bita fleytitala; hver annar dálkur er orðabókarkóðaður texti (vantandi gildi
  eru tómur texti, og listar eða hlutir eru skrifaðir sem JSON-texti).
- Lýsigögn skrárinnar hafa lykilinn `heat3d` með leiðbeiningum um lestur, svo skoðarinn varpar dálkum
  og ásum sjálfur (dæmi, með `extra` listann styttan):

```json
{
  "version": 1,
  "kind": "heat3d-watch",
  "game": "EA SPORTS F1 25",
  "axes": {"up": "y", "flipX": false, "flipY": false, "flipZ": false, "scale": 1.0},
  "columns": {
    "x": "x", "y": "y", "z": "z",
    "time": "time", "timeUnit": "seconds",
    "personId": "player", "teamId": "team", "sessionId": "session",
    "extra": ["event", "speed_kmh", "gear", "lap_time", "lap"]
  }
}
```

`up` er upp-ás leiksins, `flipX`/`flipY`/`flipZ` spegla ás svo vinstrihandar heimur er ekki teiknaður
spegilmyndaður, og `scale` er einingakvarði skoðarans: skoðarinn margfaldar hverja staðsetningu með honum þegar hann
hleður töfluna (0.01 myndi breyta sentímetrum í metra). Hvert millistykki skrifar 1 og heldur eigin
einingum leiksins - metrar í flestum, Source-einingar (tommur) í Counter-Strike 2, Unreal-einingar (sentímetrar) í
Rocket League - því borð sem er flutt út úr leiknum er í sömu einingum, svo raðirnar lenda á því;
eigin töflur CS2 breytisins segja það sama. `units` í `meta.json` segir hvað ein eining er. Síða hvers leiks
telur upp gildi hans undir „Positions and axes“.

Flugherma (DCS World, Microsoft Flight Simulator, X-Plane, Tacview upptökur IL-2) setja raðir sínar
á jörðina, og fótur þeirra segir hvar, svo skoðarinn geti lagt raunverulega heiminn undir þær:

```json
"geo": {"lat0": 42.0, "lon0": 42.0, "projection": "tangent-plane", "east": "x", "north": "z", "up": "y"}
```

`lat0`/`lon0` (gráður) eru upphaf flata kortsins sem raðirnar eru á; `east`, `north` og `up` nefna
dálkana sem geyma metra austur og norður af því og hæð yfir sjávarmáli. Upphafið er
fyrsta mæling fyrir X-Plane og MSFS, viðmiðunarpunktur upptökunnar fyrir IL-2, og fast upphaf sviðsins
fyrir DCS (fyrsta mælingin námunduð í heilar gráður á sviði sem watcher þekkir ekki). Tafla án
staðar á jörðinni hefur engan `geo` lykil, og allt annað í fætinum er eins í báðum tilvikum.

Alltaf er hægt að endurbyggja `heat.parquet` úr `events.jsonl` með
`python -m heat3d_watch table <session folder>` (sjá [Skipanir](commands.md#table)). Þetta er gagnlegt þegar
`pyarrow` vantaði meðan lotan var skráð.

## meta.json {#metajson}

`meta.json` tekur lotuna saman. Hún er skrifuð þegar lotan opnast, í mesta lagi á 30 sekúndna fresti meðan
atburðir eða tölfræði berast, og þegar lotan lokast. Tölfræði er aðeins geymd í minni milli
þessara skrifta, svo hrun getur í mesta lagi tapað síðustu hálfu mínútunni af henni.

```json
{
  "format": "heat3d-watch-session",
  "version": 1,
  "watcher": "1.0.2",
  "game": "EA SPORTS F1 25",
  "adapter": "f1-25",
  "source": "UDP telemetry 127.0.0.1:20777 (...)",
  "multiplayer": true,
  "started": "2026-05-01T20:15:03",
  "ended": "2026-05-01T21:02:11",
  "seconds": 2828.0,
  "axes": {"up": "y", "flip_x": false, "flip_y": false, "flip_z": false, "scale": 1.0, "units": "metres"},
  "events": {"position": 52110, "lap": 412, "teleport": 3},
  "positions": 52530,
  "stats": {"laps": 20, "best_lap": 91.874, "distance_km": 106.3, "race_position": 4},
  "track": "..."
}
```

Lota þar sem heimildin nefnir spilarann (sjá [Eigin raðir spilarans](#the-players-own-rows)) hefur líka
`"player"`: nafnið sem eigin raðir spilarans bera. Lota á jörðinni (fluglhermarnir) hefur líka
`"geo": {"lat0": .., "lon0": ..}`, upphafið sem `geo` í fæti hennar endurtekur.

- `started` / `ended`: staðartími upp á sekúndu; `ended` er `null` meðan lotan er í gangi.
- `events`: hversu oft hver atburður gerðist, algengastur fyrst. `positions` er fjöldi raða
  með staðsetningu.
- `stats`: tölur lotunnar. Millistykki stillir hverja, leggur við hana, eða heldur hámarkinu eða lágmarkinu.
- Allt annað sem millistykkið veit um setuna kemur á efsta stigi: brautin, kortið, verkefnið,
  leikjaauðkennið, Steam app-auðkennið, endursýningarskráin, minnissniðið og útgáfan. Lota sem var kláruð með
  endurheimt hefur `"recovered": true`.

## watcher.sqlite {#watchersqlite}

`watcher.sqlite` er tölfræðigagnagrunnurinn. Röð er bætt við fyrir hverja lotu þegar henni lýkur. Töflurnar
þrjár eru einfaldar, svo hvaða SQL-tól, minnisbók eða töflureiknir sem er getur lesið þær án watcher:

```sql
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,          -- <game folder>/<session folder>
  game TEXT NOT NULL,
  adapter TEXT NOT NULL,
  started REAL NOT NULL,        -- Unix seconds
  ended REAL,                   -- Unix seconds
  seconds REAL,
  folder TEXT NOT NULL,         -- the session folder's full path
  events INTEGER NOT NULL DEFAULT 0,
  positions INTEGER NOT NULL DEFAULT 0,
  multiplayer INTEGER NOT NULL DEFAULT 0,
  source TEXT
);
CREATE TABLE events (           -- per session, how many times each event happened
  session TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  event TEXT NOT NULL,
  count INTEGER NOT NULL,
  PRIMARY KEY (session, event)
);
CREATE TABLE stats (            -- per session, every number the game reported or the watcher counted
  session TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  key TEXT NOT NULL,
  value REAL,                   -- numbers
  text TEXT,                    -- everything else (a map name, a result, a hero)
  PRIMARY KEY (session, key)
);
```

Að skrá lotu aftur (endurheimt, endursýning umbreytt aftur) kemur í stað raða hennar. `multiplayer` er
fáni millistykkisins (sum millistykki stilla hann fyrir hverja lotu, til dæmis DCS út frá verkefninu), ekki athugun á
því hvort þú varst á netinu. Satt/ósatt gildi í `stats` er geymt sem texti.

Dæmi um fyrirspurn, besti hringur fyrir hvern leik yfir allar lotur (lægra er betra):

```sql
SELECT s.game, MIN(t.value) AS best_lap
FROM stats t JOIN sessions s ON s.id = t.session
WHERE t.key = 'best_lap'
GROUP BY s.game;
```

`python -m heat3d_watch stats` prentar samtölur úr þessum töflum (sjá [Skipanir](commands.md#stats)); dálkurinn
`best` er lægsta gildið fyrir tíma sem eru geymdir sem met og fyrir sæti, hæsta fyrir restina.

## Endurheimt eftir hrun {#recovery-after-a-crash}

Þegar `run` ræsist leitar það að lotum sem fyrri watcher skildi eftir opnar: `meta.json` án
`ended`, og `events.jsonl` með að minnsta kosti eina línu. Það lýkur hverri:

- atburðafjöldinn og fjöldi staðsetninga er talinn aftur úr `events.jsonl`, og lína sem var
  stytt er sleppt;
- endirinn er veggklukkutími síðustu línunnar (`ms`);
- tölfræðin er sú úr síðustu skrift `meta.json` (í mesta lagi 30 sekúndna gömul);
- `"recovered": true` er bætt við, `heat.parquet` er skrifuð og lotan fer í `watcher.sqlite`.

Loggurinn segir „finished N session(s) left open by an earlier run“. Læsingarskráin kemur í veg fyrir að annar
watcher „endurheimti“ loturnar hjá öðrum sem er enn í gangi.

## CSV-útflutningur {#csv-export}
![stats --csv og table](../assets/img/csv-and-table.svg)


```bash
python -m heat3d_watch stats --csv out
```

skrifar `out\sessions.csv`, `out\events.csv` og `out\stats.csv`. Hver skrá er ein tafla úr
`watcher.sqlite`, heil, með hausröð, sem UTF-8. Tímar eru Unix sekúndur eins og í gagnagrunninum.
`--game` þrengir ekki útflutninginn; hver lota er skrifuð.

## Að opna lotu í 3DHeat-skoðaranum {#opening-a-session-in-the-3dheat-viewer}

Skoðarinn: [github.com/Holdi601/3DHeat](https://github.com/Holdi601/3DHeat), skjölun
[holdi601.github.io/3DHeat](https://holdi601.github.io/3DHeat/) - síðan um
[`.3dheat` ílátið](https://holdi601.github.io/3DHeat/container.html) lýsir eins-skrár-fyrir-leik
sniðinu sem endursýningarbreytarnir geta skrifað.

Opnaðu `heat.parquet` lotu í 3DHeat-skoðaranum. Fóturinn segir skoðaranum hvaða dálkur er
staðsetningin, tíminn, leikmaðurinn, liðið og lotan, og hvaða átt er upp, svo ekkert þarf að
varpa í höndunum. Staðsetningar eru í eigin heimshnitum leiksins. Teiknaðar yfir borð sem er flutt út með
hinum 3DHeat verkfærunum (til dæmis úr [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles)),
lenda þær þar sem þær gerðust.

- **Hitakort** nota hverja röð með staðsetningu, síuð eftir `event`, `player`, `team` eða `session` eins og hvern
  annan dálk.
- **Línuhiti** teiknar línu frá hverri röð leikmanns til næstu raðar hans, og í afspilun er hver
  leikmaður punktur sem hreyfist eftir leiðinni með hala á eftir sér. Leiðaspjald skoðarans velur,
  út frá `event` dálkinum, hvaða atburðir **hefja** leið og hvaða atburðir **enda** hana. Watcher skrifar
  atburðina sem afmarka sem raðir með staðsetningu, svo hægt er að velja þá þar:
  - upphaf: `spawn`, `respawn`, `session_start`. Upphaf lokar leiðinni sem var opin án
    þess að teikna línu á nýja staðinn.
  - endir: `death`, `finish`, `session_end` og `teleport`. Línan nær að endaröðinni sjálfri,
    sem er þar sem leikmaðurinn dó, stoppaði eða var fluttur burt.

  Stökk - staður sem er náð án þess að ferðast þangað - eru tvær raðir: `teleport` á staðnum sem var
  **yfirgefinn**, og upphaf á staðnum sem var **komið á**, rétt á eftir. Kappakstursmillistykkin skrifa eitt hvenær sem
  bíllinn færðist lengra en hann hefði getað ekið (afturspólun eða flashback, endurstilling á veginn, aftur á
  viðgerðarsvæðið, hraðferð), með `spawn` við komuna (`respawn` fyrir endurstillingu BeamNG); `teleport` röðin
  ber komustaðinn sem `to_x`, `to_y`, `to_z` og vegalengdina sem `metres`, upphafsröðin
  `after: "teleport"`. Flutningabílamillistykkin gera það sama fyrir ferju, lest eða hlaðna vistun, og
  flugmillistykkin fyrir stökk sem engin flugvél gæti flogið. Svo með `teleport` meðal endanna og `spawn`
  meðal upphafanna - sem er það sem skoðarinn stingur sjálfur upp á - endar leið þar sem stökkið yfirgaf
  og næsta byrjar þar sem komið var, og engin lína þverar kortið. Leið liggur aldrei yfir
  breytingu á `session` dálkinum. Staðsetningarröð er skrifuð nokkrum sinnum á sekúndu
  (10 Hz fyrir flesta fjarmælingu), sem gefur mjúka línu.
- Dálkurinn `session` skiptir setu í umferðir, leiðir, líf eða líkama (Elite Dangerous
  heldur vetrarbrautarröðum og yfirborðsröðum hverrar plánetu aðskildum þannig). Veldu eitt í skoðaranum til að skoða
  þann hluta einan.

Hvað skoðarinn gerir við raðirnar - síur, litir, afspilun - er lýst í eigin skjölun skoðarans. Counter-Strike 2
demólotur eru opnaðar í gegnum `<map>/<match>.parquet` breytisins og
`<match>.match.json` í hita- og leikjaflipum skoðarans. Staðsetningar iRacing koma úr
`.ibt` skránum sem eru taldar upp í lotunni, sem skoðarinn les sjálfur.
