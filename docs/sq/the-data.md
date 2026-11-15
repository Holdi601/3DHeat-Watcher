---
title: "Të dhënat"
nav_order: 5
lang: "sq"
source: the-data.md
source_hash: "6150cdc022fc"
nav_exclude: true
search_exclude: true
---
# Të dhënat {#the-data}

Të gjitha regjistrimet janë skedarë të thjeshtë në dosjen e të dhënave (`%LOCALAPPDATA%\3DHeat\Watcher` përveç nëse ndryshohet,
shih [Instalimi dhe ekzekutimi](installing-and-running.md#where-everything-is)). Mund t'i lexosh, kopjosh ose
fshish pa watcher-in. Një skedar `.jsonl` është tekst i thjeshtë, një ngjarje në rresht (Notepad e hap);
një skedar `.parquet` është një tabelë që e hap shikuesi 3DHeat (Excel nuk e hap - `stats --csv` shkruan skedarë
CSV për fletë llogaritjeje).

## Dosjet e seancave {#session-folders}
![a session folder](../assets/img/session-folder.svg)


Një **seancë** është një ulje me një burim: nga çasti kur loja thotë diçka për herë të parë deri sa
ndalon (loja mbyllet, një ndeshje mbaron, një vozitje ose një fluturim rivendoset - faqja e secilit adapter thotë se çfarë
fillon dhe mbaron seancat e tij). Çdo seancë merr një dosje:

```text
<data>\sessions\<game>\<YYYY-MM-DD_HH-MM-SS>_<adapter id>\
    events.jsonl
    heat.parquet
    meta.json
```

- `<game>` është emri i lojës me çdo karakter përveç shkronjave, shifrave, `.`, `_` dhe `-`
  zëvendësuar me `-` (më së shumti 60 karaktere): `EA-SPORTS-F1-25`, `Counter-Strike-2`. Adapterat që mbulojnë
  shumë lojëra (statistikat e Steam, Steam Timeline, NVIDIA highlights) e arkivojnë çdo seancë nën lojën së cilës
  i përket.
- Koha është fillimi i seancës në orën lokale. Seancat që përshkruajnë të shkuarën (një riluajtje e konvertuar
  pas ndeshjes, një skedar statistikash Steam) përdorin kohën që jep loja ose skedari. Dy seanca që fillojnë në të
  njëjtën sekondë marrin `_2`, `_3`, ... në fund.
- Id-ja e seancës, në bazën e të dhënave të statistikave, është `<game folder>/<session folder>`.

Një seancë në të cilën nuk u regjistrua fare asgjë (loja qëndroi në menutë e saj, ose u prish në fillim)
fshihet kur mbyllet, që çdo nisje të mos lërë një dosje bosh.

Disa seanca mbajnë më shumë skedarë. Një seancë demoje Counter-Strike 2 mban tabelën dhe përmbledhjen e
vetë konvertuesit (`<map>/<match>.parquet`, `<match>.match.json`). Një seancë iRacing liston skedarët `.ibt` që
simulatori shkroi gjatë uljes si ngjarje `telemetry_file`.

## events.jsonl {#eventsjsonl}

`events.jsonl` ka një objekt JSON për rresht, një rresht për ngjarje, i shkruar në çastin kur ngjarja
ndodh. Skedari është me buferim sipas rreshtit, ndaj një prishje, një ndërprerje rryme ose një proces i vrarë nuk humb asgjë që
ishte shkruar tashmë; një rresht i ndërprerë nga një prishje kapërcehet kur lexohet skedari, dhe çdo rresht para tij
mbetet.

Çdo rresht ka të njëjtat kolona bazë:

| Kolona | Lloji | Çfarë është |
|---|---|---|
| `time` | numër | sekonda që nga fillimi i seancës (4 dhjetore), ose ora e vetë lojës aty ku adapteri e kalon |
| `ms` | numër i plotë | koha e murit, milisekonda Unix |
| `event` | tekst | çfarë ndodhi: `position`, `spawn`, `death`, `kill`, `lap`, `teleport`, `session_start`, ... |
| `x`, `y`, `z` | numër | ku, në njësitë dhe boshtet e vetë lojës (shih `axes` te `meta.json`); janë vetëm kur të tria dihen dhe janë të fundme |
| `player` | tekst | kush: një emër, një id, ose `me` për personin që luan (shih [Rreshtat e vetë lojtarit](#the-players-own-rows)) |
| `team` | tekst | ana e tij, kur loja e thotë |
| `session` | tekst | ndeshja, raundi, etapa, jeta ose fluturimi të cilit i përket rreshti, kur loja e thotë |

Çdo fushë tjetër që raporton loja vjen pas me emrin e vet (`speed_kmh`, `gear`, `lap_time`, `weapon`,
`victim`, `hero`, ...). Fushat pa vlerë lihen jashtë, dhe po ashtu numrat që nuk janë të fundëm.
Dy rreshta sintetikë:

```json
{"time":12.3456,"ms":1777660501123,"event":"position","x":-412.5,"y":12.1,"z":233.0,"player":"me","session":"1","speed_kmh":187.4,"gear":5}
{"time":15.0,"ms":1777660503667,"event":"lap","x":-380.2,"y":12.0,"z":250.9,"player":"me","session":"1","lap_time":92.418,"lap":3}
```

Rreshtat pa pozicion (një rresht kill feed, një rritje niveli, një ndryshim statistike) mbeten te `events.jsonl` dhe numërohen
në statistika. Vetëm rreshtat me pozicion shkojnë në tabelë.

### Rreshtat e vetë lojtarit {#the-players-own-rows}

Cilët rreshta janë të personit që luan e thotë burimi, kurrë nuk merret me mend. Një rresht është i vetë lojtarit kur

- `player` i tij është `me`: shumica e adapterave, burimi i të cilëve është loja e vetë lojtarit (telemetria e
  makinës ose avionit të vet, një integrim gjendjeje loje, një ditar);
- mban `own_car` 1: lojërat e garave që regjistrojnë çdo makinë nën emrin e shoferit të saj (EA SPORTS F1
  sipas indeksit të makinës së lojtarit në lojë, RaceRoom sipas vendit të vet, Automobilista 2 dhe Project CARS 2 sipas
  pjesëmarrësit të shikuar) e shënojnë makinën e lojtarit kështu dhe e mbajnë emrin e shoferit te `player`;
- `player` i tij është `player` i seancës te `meta.json`: emri që burimi i jep lojtarit - komandanti i Elite
  Dangerous (ditari është gjithmonë i lojtarit), rreshti i një riluajtjeje League of Legends për Riot ID-në
  te cilësimet.

War Thunder dhe Rocket League emërtojnë çdo lojtar dhe nuk thonë cili je ti; me emrin tënd te cilësimi
`player_names` (shih [Cilësimet](installing-and-running.md#settings)) rreshtat e tu bëhen `me`.
[NVIDIA highlights](nvidia-highlights.md) kërkojnë një moment pikërisht në këto rreshta.

## heat.parquet {#heatparquet}

Kur një seancë mbyllet, rreshtat e `events.jsonl` që kanë `x`, `y` dhe `z` shkruhen te
`heat.parquet`. Kjo është tabela që hap shikuesi 3DHeat. Nëse seanca nuk ka pozicione, nuk shkruhet
tabelë.

- Kolonat janë `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session`, të ndjekura nga çdo
  fushë tjetër sipas radhës së shfaqjes së parë.
- `x`, `y`, `z` dhe `time` janë float 64-bit dhe `ms` është numër i plotë 64-bit. Një kolonë tjetër vlerat e së cilës
  janë të gjitha numra është float 64-bit; çdo kolonë tjetër është tekst i koduar me fjalor (vlerat që mungojnë
  janë tekst i zbrazët, dhe listat ose objektet shkruhen si tekst JSON).
- Metadata e skedarit ka një çelës `heat3d` me udhëzimet e leximit, ndaj shikuesi i lidh kolonat
  dhe boshtet vetë (një shembull, me listën `extra` të shkurtuar):

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

`up` është boshti lart i lojës, `flipX`/`flipY`/`flipZ` pasqyrojnë një bosht që një botë me dorë të majtë të mos vizatohet
e pasqyruar, dhe `scale` është shkalla e njësisë së shikuesit: shikuesi e shumëzon çdo pozicion me të kur
e ngarkon tabelën (0.01 do t'i kthente centimetrat në metra). Çdo adapter shkruan 1 dhe i mban njësitë e vetë
lojës - metra për shumicën, njësi Source (inç) për Counter-Strike 2, njësi Unreal (centimetra) për
Rocket League - sepse një nivel i eksportuar nga loja është në po ato njësi, ndaj rreshtat bien mbi të;
tabelat e vetë konvertuesit CS2 thonë të njëjtën gjë. `units` te `meta.json` thotë sa është një njësi. Faqja e secilës lojë
liston vlerat e saj nën "Positions and axes".

Simulatorët e fluturimit (DCS World, Microsoft Flight Simulator, X-Plane, regjistrimet Tacview të IL-2) i vendosin
rreshtat e tyre në tokë, dhe fundi i tyre thotë ku, që shikuesi të mund të shtrojë botën e vërtetë poshtë tyre:

```json
"geo": {"lat0": 42.0, "lon0": 42.0, "projection": "tangent-plane", "east": "x", "north": "z", "up": "y"}
```

`lat0`/`lon0` (gradë) janë origjina e hartës së sheshtë ku ndodhen rreshtat; `east`, `north` dhe `up` emërtojnë
kolonat që mbajnë metra në lindje dhe veri prej saj dhe lartësinë mbi nivelin e detit. Origjina është
pika e parë për X-Plane dhe MSFS, pika e referencës së regjistrimit për IL-2, dhe origjina fikse e teatrit
për DCS (pika e parë e rrumbullakosur në gradë të plota në një teatër që watcher-i nuk e njeh). Një tabelë pa
vend në tokë nuk ka çelës `geo`, dhe gjithçka tjetër në fund është e njëjtë në të dyja rastet.

`heat.parquet` mund të rindërtohet gjithmonë nga `events.jsonl` me
`python -m heat3d_watch table <session folder>` (shih [Komandat](commands.md#table)). Kjo ndihmon kur
`pyarrow` mungonte ndërsa seanca regjistrohej.

## meta.json {#metajson}

`meta.json` përmbledh seancën. Shkruhet kur seanca hapet, më së shumti çdo 30 sekonda ndërsa
vijnë ngjarje ose statistika, dhe kur seanca mbyllet. Statistikat mbahen vetëm në memorie mes
atyre shkrimeve, ndaj një prishje mund të humbasë më së shumti gjysmë minutën e fundit të tyre.

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

Një seancë burimi i së cilës emërton lojtarin (shih [Rreshtat e vetë lojtarit](#the-players-own-rows)) ka edhe
`"player"`: emrin që mbajnë rreshtat e vetë lojtarit. Një seancë në tokë (simulatorët e fluturimit) ka edhe
`"geo": {"lat0": .., "lon0": ..}`, origjinën që e përsërit `geo` i fundit të saj.

- `started` / `ended`: ora lokale deri në sekondë; `ended` është `null` ndërsa seanca ekzekutohet.
- `events`: sa herë ndodhi çdo ngjarje, më e shpeshta e para. `positions` është numri i rreshtave
  me pozicion.
- `stats`: numrat e seancës. Një adapter e vendos secilin, i shton, ose mban maksimumin ose minimumin.
- Çdo gjë tjetër që adapteri di për uljen vjen në nivelin e sipërm: pista, harta, misioni,
  id-ja e ndeshjes, id-ja e aplikacionit Steam, skedari i riluajtjes, profili i memories dhe versioni. Një seancë e përfunduar
  nga rikuperimi ka `"recovered": true`.

## watcher.sqlite {#watchersqlite}

`watcher.sqlite` është baza e të dhënave të statistikave. Një rresht shtohet për çdo seancë kur mbyllet. Tri
tabelat janë të thjeshta, ndaj çdo mjet SQL, notebook ose fletë llogaritjeje mund t'i lexojë pa watcher-in:

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

Regjistrimi i një seance përsëri (rikuperim, një riluajtje e konvertuar përsëri) zëvendëson rreshtat e saj. `multiplayer` është
flamuri i adapterit (disa adaptera e vendosin sipas seancës, për shembull DCS nga misioni), jo një kontroll nëse
ishe online. Një vlerë e/jo te `stats` ruhet si tekst.

Një pyetje shembull, xhiroja më e mirë për lojë nga të gjitha seancat (më e ulët është më mirë):

```sql
SELECT s.game, MIN(t.value) AS best_lap
FROM stats t JOIN sessions s ON s.id = t.session
WHERE t.key = 'best_lap'
GROUP BY s.game;
```

`python -m heat3d_watch stats` printon totalet nga këto tabela (shih [Komandat](commands.md#stats)); kolona e tij
`best` është vlera më e ulët për kohët e mbajtura si më të mira dhe për vendet, më e larta për pjesën tjetër.

## Rikuperimi pas një prishjeje {#recovery-after-a-crash}

Kur `run` niset, kërkon seanca që një watcher i mëparshëm i la të hapura: një `meta.json` pa
`ended`, dhe një `events.jsonl` me të paktën një rresht. I përfundon secilën:

- numrat e ngjarjeve dhe numri i pozicioneve numërohen përsëri nga `events.jsonl`, duke kapërcyer një rresht
  të ndërprerë;
- fundi është koha e murit e rreshtit të fundit (`ms`);
- statistikat janë ato të shkrimit të fundit të `meta.json` (më së shumti 30 sekonda i vjetër);
- shtohet `"recovered": true`, shkruhet `heat.parquet`, dhe seanca hyn te `watcher.sqlite`.

Logu thotë "finished N session(s) left open by an earlier run". Skedari i kyçjes e ndalon një watcher të dytë
të "rikuperojë" seancat e një tjetri që ende ekzekutohet.

## Eksporti CSV {#csv-export}
![stats --csv and table](../assets/img/csv-and-table.svg)


```bash
python -m heat3d_watch stats --csv out
```

shkruan `out\sessions.csv`, `out\events.csv` dhe `out\stats.csv`. Çdo skedar është një tabelë e
`watcher.sqlite`, e plotë, me një rresht titujsh, si UTF-8. Kohët janë sekonda Unix si në bazën e të dhënave.
`--game` nuk e ngushton eksportin; çdo seancë shkruhet.

## Hapja e një seance në shikuesin 3DHeat {#opening-a-session-in-the-3dheat-viewer}

Shikuesi: [github.com/Holdi601/3DHeat](https://github.com/Holdi601/3DHeat), dokumentacioni
[holdi601.github.io/3DHeat](https://holdi601.github.io/3DHeat/) - faqja e tij për
[kontejnerin `.3dheat`](https://holdi601.github.io/3DHeat/container.html) përshkruan formatin një-skedar-për-ndeshje
që konvertuesit e riluajtjeve mund ta shkruajnë.

Hap `heat.parquet` të një seance në shikuesin 3DHeat. Fundi i tregon shikuesit cila kolonë është
pozicioni, koha, lojtari, ekipi dhe seanca, dhe cila anë është lart, ndaj asgjë nuk duhet lidhur me
dorë. Pozicionet janë në koordinatat e botës së vetë lojës. Të vizatuara mbi një nivel të eksportuar me
mjetet e tjera 3DHeat (për shembull nga [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles)),
ato bien aty ku ndodhën.

- **Hartat e nxehtësisë** përdorin çdo rresht me pozicion, të filtruar sipas `event`, `player`, `team` ose `session` si çdo
  kolonë tjetër.
- **Nxehtësia e vijës** vizaton një vijë nga çdo rresht i një lojtari te rreshti tjetër i tij, dhe në riprodhim çdo
  lojtar është një pikë që lëviz përgjatë rrugës me një bisht pas. Paneli Rrugët i shikuesit zgjedh,
  nga kolona `event`, cilat ngjarje **fillojnë** një rrugë dhe cilat e **mbarojnë**. Watcher-i shkruan
  ngjarjet kufizuese si rreshta me pozicion, ndaj mund të zgjidhen aty:
  - fillimet: `spawn`, `respawn`, `session_start`. Një fillim mbyll rrugën që ishte e hapur pa
    vizatuar vijë drejt vendit të ri.
  - mbarimet: `death`, `finish`, `session_end` dhe `teleport`. Vija arrin deri te vetë rreshti i mbarimit,
    që është aty ku lojtari vdiq, ndaloi ose u mor tutje.

  Një kërcim - një vend i arritur pa udhëtuar atje - janë dy rreshta: `teleport` te vendi i **lënë**,
  dhe një fillim te vendi ku **mbërriti**, menjëherë pas tij. Adapterat e garave shkruajnë një sa herë që
  makina lëvizi më larg se sa mund të kishte vozitur (një rikthim ose flashback, një rivendosje në rrugë, kthim te
  pit-et, një udhëtim i shpejtë), me `spawn` te mbërritja (`respawn` për rivendosjen e BeamNG); rreshti `teleport`
  mban mbërritjen si `to_x`, `to_y`, `to_z` dhe largësinë si `metres`, rreshti i fillimit
  `after: "teleport"`. Adapterat e kamionëve bëjnë të njëjtën për një traget, një tren ose një ruajtje të ngarkuar,
  dhe adapterat e fluturimit për një kërcim që asnjë avion nuk mund ta fluturonte. Pra me `teleport` mes mbarimeve
  dhe `spawn` mes fillimeve - që është ajo që sugjeron vetë shikuesi - një rrugë mbaron aty ku e la kërcimi
  dhe tjetra fillon aty ku mbërriti, dhe asnjë vijë nuk e kalon hartën. Një rrugë nuk shkon kurrë përtej
  ndryshimit të kolonës `session`. Një rresht pozicioni shkruhet disa herë në sekondë
  (10 Hz për shumicën e telemetrisë), që jep një vijë të lëmuar.
- Kolona `session` e ndan një ulje në raundet, etapat, jetët ose trupat e saj (Elite Dangerous
  i mban rreshtat e galaktikës dhe rreshtat e sipërfaqes së çdo planeti të ndarë kështu). Zgjidh një në shikues për të parë
  vetëm atë pjesë.

Çfarë bën shikuesi me rreshtat - filtrat, ngjyrat, riprodhimi - përshkruhet në dokumentacionin e vetë shikuesit.
Seancat e demove Counter-Strike 2 hapen përmes `<map>/<match>.parquet` dhe `<match>.match.json` të konvertuesit
në skedat heat dhe match të shikuesit. Pozicionet e iRacing vijnë nga skedarët `.ibt` të listuar në seancë, që
shikuesi i lexon vetë.
