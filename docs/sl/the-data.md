---
title: "Podatki"
nav_order: 5
lang: "sl"
source: the-data.md
source_hash: "6150cdc022fc"
nav_exclude: true
search_exclude: true
---
# Podatki {#the-data}

Vsi posnetki so navadne datoteke v mapi podatkov (`%LOCALAPPDATA%\3DHeat\Watcher`, razen če je spremenjena, glejte
[Namestitev in zagon](installing-and-running.md#where-everything-is)). Brez watcherja jih lahko berete, kopirate ali
brišete. Datoteka `.jsonl` je navadno besedilo, ena vrstica na dogodek (odpre se v Beležnici); datoteka `.parquet` je tabela,
ki jo odpre pregledovalnik 3DHeat (Excel je ne odpre - `stats --csv` zapiše datoteke CSV za preglednice).

## Mape sej {#session-folders}
![a session folder](../assets/img/session-folder.svg)


**Seja** je en sedež z enim virom: od trenutka, ko igra prvič kaj pove, do trenutka, ko se ustavi (igra se zapre, tekma
se konča, vožnja ali let se ponastavi - na strani vsakega vmesnika je povedano, kaj začne in konča seje). Vsaka seja dobi mapo:

```text
<data>\sessions\<game>\<YYYY-MM-DD_HH-MM-SS>_<adapter id>\
    events.jsonl
    heat.parquet
    meta.json
```

- `<game>` je ime igre, kjer je vsak znak razen črk, številk, `.`, `_` in `-` zamenjan z `-` (največ 60 znakov):
  `EA-SPORTS-F1-25`, `Counter-Strike-2`. Vmesniki, ki pokrivajo mnogo iger (statistike Steama, Steam Timeline, NVIDIA
  highlights), vsako sejo vpišejo pod igro, h kateri spada;
- čas je začetek seje po lokalni uri. Seje, ki opisujejo preteklost (ponovitev, pretvorjena po tekmi, datoteka statistik
  Steama), uporabijo čas, ki ga da igra ali datoteka. Dve seji, ki se začneta v isti sekundi, dobita pripono `_2`, `_3`, ...;
- id seje v bazi statistik je `<game folder>/<session folder>`.

Seja, v kateri ničesar ni bilo zapisanega (igra je ostala v svojih menijih ali se je ob zagonu zrušila), se ob zaprtju izbriše,
da se ob vsakem zagonu ne pusti prazna mapa.

Nekatere seje imajo več datotek. Seja demo posnetka Counter-Strike 2 ima tabelo in povzetek pretvornika
(`<map>/<match>.parquet`, `<match>.match.json`). Seja iRacing našteje datoteke `.ibt`, ki jih je simulator zapisal med sedežem,
kot dogodke `telemetry_file`.

## events.jsonl {#eventsjsonl}

`events.jsonl` ima en objekt JSON na vrstico, eno vrstico na dogodek, zapisano v trenutku, ko se dogodek zgodi. Datoteka je
vrstično medpomnjena, zato se ob zrušitvi, izpadu napajanja ali ubitem procesu ne izgubi nič, kar je bilo že zapisano; vrstica,
ki jo zruši prekinitev, se pri branju datoteke preskoči, vse vrstice pred njo pa ostanejo.

Vsaka vrstica ima enake osnovne stolpce:

| Stolpec | Tip | Kaj je |
|---|---|---|
| `time` | število | sekunde od začetka seje (4 decimalke), ali igrina lastna ura, kjer jo vmesnik poda |
| `ms` | celo število | stenski čas, Unix milisekunde |
| `event` | besedilo | kaj se je zgodilo: `position`, `spawn`, `death`, `kill`, `lap`, `teleport`, `session_start`, ... |
| `x`, `y`, `z` | število | kje, v lastnih enotah igre in osi (glejte `axes` v `meta.json`); prisotno samo, kadar so vse tri znane in končne |
| `player` | besedilo | kdo: ime, id, ali `me` za igralca ([Lastne vrstice igralca](#the-players-own-rows)) |
| `team` | besedilo | njihova stran, kadar jo igra pove |
| `session` | besedilo | tekma, runda, faza, življenje ali let, h kateremu vrstica spada, kadar igra to pove |

Vsako drugo polje, ki ga igra sporoči, sledi pod svojim imenom (`speed_kmh`, `gear`, `lap_time`, `weapon`, `victim`,
`hero`, ...). Polja brez vrednosti se izpustijo, prav tako števila, ki niso končna. Dve izmišljeni vrstici:

```json
{"time":12.3456,"ms":1777660501123,"event":"position","x":-412.5,"y":12.1,"z":233.0,"player":"me","session":"1","speed_kmh":187.4,"gear":5}
{"time":15.0,"ms":1777660503667,"event":"lap","x":-380.2,"y":12.0,"z":250.9,"player":"me","session":"1","lap_time":92.418,"lap":3}
```

Vrstice brez položaja (vrstica feeda ubijanj, dvig stopnje, sprememba statistike) ostanejo v `events.jsonl` in se štejejo v
statistikah. V tabelo gredo samo vrstice s položajem.

### Lastne vrstice igralca {#the-players-own-rows}

Kaj so vrstice igralca, pove vir, nikoli se ne ugiba. Vrstica je igralčeva lastna, kadar

- je njen `player` `me`: večina vmesnikov, katerih vir je igralčeva lastna igra (telemetrija lastnega avtomobila ali letala,
  vmesnik stanja igre, dnevnik);
- ima `own_car` 1: dirkalne igre, ki vsakega avtomobila zapišejo pod imenom njegovega voznika (EA SPORTS F1 po indeksu
  igralčevega avtomobila v igri, RaceRoom po njeni lastni reži, Automobilista 2 in Project CARS 2 po gledanem udeležencu)
  označijo igralčev avtomobil na ta način in ime voznika ohranijo v `player`;
- je njen `player` enak `player` seje v `meta.json`: ime, ki ga vir da igralcu - poveljnik Elite Dangerous (dnevnik je
  vedno igralčev), vrstica ponovitve League of Legends z Riot ID iz nastavitev.

War Thunder in Rocket League imenujeta vsakega igralca in ne povesta, kateri ste vi; z vašim imenom v nastavitvi
`player_names` (glejte [Nastavitve](installing-and-running.md#settings)) vaše vrstice postanejo `me`.
[NVIDIA highlights](nvidia-highlights.md) pogledajo trenutek ravno v teh vrsticah.

## heat.parquet {#heatparquet}

Ob zaprtju seje se vrstice `events.jsonl`, ki imajo `x`, `y` in `z`, zapišejo v `heat.parquet`. To je tabela, ki jo odpre
pregledovalnik 3DHeat. Če seja nima položajev, se tabela ne zapiše.

- Stolpci so `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session`, za njimi vsako drugo polje v vrstnem redu,
  v katerem se prvič pojavi;
- `x`, `y`, `z` in `time` so 64-bitna decimalna števila, `ms` je 64-bitno celo število. Dodatni stolpec, katerega vrednosti
  so vse številke, je 64-bitno decimalno število; vsak drug stolpec je besedilo s slovarskim kodiranjem (manjkajoče vrednosti
  so prazno besedilo, seznami in predmeti pa so zapisani kot besedilo JSON);
- v metapodatkih datoteke je ključ `heat3d` z navodili za branje, tako da pregledovalnik sam preslika stolpce in osi (primer,
  z okrajšanim seznamom `extra`):

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

`up` je navpična os igre, `flipX`/`flipY`/`flipZ` zrcalijo os, da levosučni svet ni narisan zrcaljeno, `scale` pa je merilo
enot pregledovalnika: pregledovalnik vsak položaj pomnoži z njim, ko nalaga tabelo (0.01 bi centimetre spremenil v metre).
Vsak vmesnik zapiše 1 in ohrani lastne enote igre - za večino metre, za Counter-Strike 2 enote Source (palce), za Rocket
League enote Unreal (centimetre) -, ker se nivo, izvožen iz igre, nahaja v istih enotah, zato vrstice pristanejo nanj;
tudi tabele pretvornika CS2 to povedo. `units` v `meta.json` pove, kaj je ena enota. Vsaka stran igre navaja svoje vrednosti
pod »Positions and axes«.

Simulatorji letenja (DCS World, Microsoft Flight Simulator, X-Plane, posnetki Tacview za IL-2) postavijo svoje vrstice na Zemljo,
noga pa pove kje, da lahko pregledovalnik pod njih položi pravi svet:

```json
"geo": {"lat0": 42.0, "lon0": 42.0, "projection": "tangent-plane", "east": "x", "north": "z", "up": "y"}
```

`lat0`/`lon0` (stopinje) sta izhodišče ravnega zemljevida, v katerem so vrstice; `east`, `north` in `up` imenujejo stolpce, ki
držijo metre vzhodno in severno od njega ter višino nad morjem. Izhodišče je prvi fiks za X-Plane in MSFS, referenčna točka
posnetka za IL-2 in fiksno izhodišče prizorišča za DCS (prvi fiks, zaokrožen na cele stopinje, na prizorišču, ki ga watcher ne
pozna). Tabela brez mesta na Zemlji nima ključa `geo`, vse ostalo v nogi pa je v obeh primerih enako.

`heat.parquet` se lahko vedno znova zgradi iz `events.jsonl` z
`python -m heat3d_watch table <session folder>` (glejte [Ukazi](commands.md#table)). To je uporabno, kadar `pyarrow`
ni bil nameščen, medtem ko se je seja zapisovala.

## meta.json {#metajson}

`meta.json` povzema sejo. Zapiše se, ko se seja odpre, največ vsakih 30 sekund, medtem ko prihajajo dogodki ali statistike, in
ob zaprtju seje. Statistike se med temi zapisi hranijo samo v pomnilniku, zato zrušitev lahko izgubi največ zadnjih pol minute.

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

Seja, katere vir imenuje igralca (glejte [Lastne vrstice igralca](#the-players-own-rows)), ima tudi `"player"`: ime, ki ga
nosijo igralčeve lastne vrstice. Seja na Zemlji (simulatorji letenja) ima tudi `"geo": {"lat0": .., "lon0": ..}`, ki ga ponovi
`geo` v nogi njene tabele.

- `started` / `ended`: lokalni čas do sekunde; `ended` je `null`, dokler seja teče;
- `events`: kolikokrat se je vsak dogodek zgodil, najpogostejši na vrhu. `positions` je število vrstic s položajem;
- `stats`: številke seje. Vmesnik vsako nastavi, prišteje ji, ali obdrži največjo ali najmanjšo vrednost;
- vse drugo, kar vmesnik ve o sedežu, sledi na najvišji ravni: proga, zemljevid, misija, id tekme, id aplikacije Steam,
  datoteka ponovitve, profil pomnilnika in različica. Seja, ki jo je dokončala obnovitev, ima `"recovered": true`.

## watcher.sqlite {#watchersqlite}

`watcher.sqlite` je baza statistik. Vrstica se doda za vsako sejo, ko se ta zapre. Tri tabele so preproste, zato jih lahko
vsak orodje za SQL, beležnica ali preglednica bere brez watcherja:

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

Ponovno zapisovanje seje (obnovitev, ponovno pretvorjena ponovitev) zamenja njene vrstice. `multiplayer` je zastavica
vmesnika (nekateri vmesniki jo nastavijo za vsako sejo posebej, na primer DCS iz misije), ni pa preverjanje, ali ste bili na
spletu. Vrednost da/ne v `stats` je shranjena kot besedilo.

Primer poizvedbe, najboljši krog vsake igre čez vse seje (nižje je boljše):

```sql
SELECT s.game, MIN(t.value) AS best_lap
FROM stats t JOIN sessions s ON s.id = t.session
WHERE t.key = 'best_lap'
GROUP BY s.game;
```

`python -m heat3d_watch stats` izpiše skupne vsote iz teh tabel (glejte [Ukazi](commands.md#stats)); njegov stolpec `best` je
najnižja vrednost za čase, shranjene kot najboljši, in za mesta, najvišja pa za vse ostalo.

## Obnovitev po zrušitvi {#recovery-after-a-crash}

Ko se `run` zažene, poišče seje, ki jih je prejšnji watcher pustil odprte: `meta.json` brez `ended` in `events.jsonl` z
vsaj eno vrstico. Vsako dokonča:

- števila dogodkov in število položajev se preštejeta znova iz `events.jsonl`, pri tem se preskoči prekinjena vrstica;
- konec je stenski čas zadnje vrstice (`ms`);
- statistike so tiste iz zadnjega zapisa `meta.json` (največ 30 sekund stare);
- doda se `"recovered": true`, zapiše se `heat.parquet` in seja gre v `watcher.sqlite`.

Dnevnik pravi »finished N session(s) left open by an earlier run«. Datoteka zaklepa preprečuje, da bi drugi watcher »obnovil«
seje tekočega.

## Izvoz v CSV {#csv-export}
![stats --csv and table](../assets/img/csv-and-table.svg)


```bash
python -m heat3d_watch stats --csv out
```

zapiše `out\sessions.csv`, `out\events.csv` in `out\stats.csv`. Vsaka datoteka je ena tabela `watcher.sqlite`, cela, z vrstico
glave, v UTF-8. Časi so Unix sekunde, kot v bazi. `--game` izvoza ne zoži; zapiše se vsaka seja.

## Odpiranje seje v pregledovalniku 3DHeat {#opening-a-session-in-the-3dheat-pregledovalnik}

Pregledovalnik: [github.com/Holdi601/3DHeat](https://github.com/Holdi601/3DHeat), dokumentacija
[holdi601.github.io/3DHeat](https://holdi601.github.io/3DHeat/) - njegova stran
[`.3dheat` container](https://holdi601.github.io/3DHeat/container.html) opisuje format ene datoteke na tekmo, ki ga lahko
pišejo pretvorniki ponovitev.

Odprite `heat.parquet` seje v pregledovalniku 3DHeat. Noga pove pregledovalniku, kateri stolpec je položaj, čas, igralec,
stran in seja ter katera je navpična os, zato ničesar ni treba preslikati ročno. Položaji so v lastnih svetovnih koordinatah
igre. Narisani čez nivo, izvožen z drugimi orodji 3DHeat (na primer iz [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles)),
pristanejo tam, kjer so se zgodili.

- **Toplotni zemljevidi** uporabijo vsako vrstico s položajem, filtrirano po `event`, `player`, `team` ali `session`, kot katerikoli
  drug stolpec.
- **Toplota črt** nariše črto od vsake vrstice igralca do njegove naslednje, pri predvajanju pa je vsak igralec točka, ki se
  premika po poti, z repom za seboj. Panel Trase v pregledovalniku iz stolpca `event` izbere, kateri dogodki **začnejo** pot in
  kateri jo **končajo**. Watcher zapiše mejne dogodke kot vrstice s položajem, zato jih je mogoče izbrati tam:
  - začetki: `spawn`, `respawn`, `session_start`. Začetek zapre pot, ki je bila odprta, ne da bi narisal črto do novega mesta;
  - konci: `death`, `finish`, `session_end` in `teleport`. Črta teče do same končne vrstice, to je tam, kjer je igralec umrl,
    se ustavil ali bil odpeljan.

  Skok - mesto, do katerega se pride, ne da bi tja potovali - sta dve vrstici: `teleport` na mestu, ki ga igralec **zapusti**, in
  začetek na mestu, do katerega **prispe**, takoj za njim. Vmesniki dirk zapišejo enega vsakič, ko je avtomobil prevozil več, kot bi
  lahko (previjanje ali flashback, ponastavitev na cesto, nazaj v bokse, hitro potovanje), s `spawn` na mestu prihoda (`respawn` za
  ponastavitev BeamNG); vrstica `teleport` nosi prihod kot `to_x`, `to_y`, `to_z` in razdaljo kot `metres`, vrstica začetka pa
  `after: "teleport"`. Vmesniki tovornjakov naredijo enako za trajekt, vlak ali naložen shranjen položaj, vmesniki letal pa za skok,
  ki ga nobeno letalo ne bi moglo preleteti. Tako z `teleport` med konci in `spawn` med začetki - kar pregledovalnik predlaga sam -
  pot konča tam, kjer je skok odšel, naslednja pa se začne tam, kamor je prišel, in nobena črta ne seka zemljevida. Pot nikoli ne teče
  čez spremembo stolpca `session`. Vrstica s položajem se zapiše nekajkrat na sekundo (10 Hz za večino telemetrije), kar da gladko črto.
- Stolpec `session` razdeli sedež na runde, faze, življenja ali telesa (Elite Dangerous tako loči vrstice galaktične zvezdne karte in
  vrstice površine vsakega planeta). Izberite enega v pregledovalniku, da si ogledate samo ta del.

Kaj pregledovalnik naredi z vrsticami - filtri, barve, predvajanje - je opisano v dokumentaciji pregledovalnika. Seje demo posnetkov
Counter-Strike 2 se odprejo prek tabele `<map>/<match>.parquet` in `<match>.match.json` pretvornika v zavihkih Toplotni zemljevid in
Tekma pregledovalnika. Položaje iRacinga dobimo iz datotek `.ibt`, naštetih v seji, ki jih pregledovalnik bere sam.
