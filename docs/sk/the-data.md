---
title: "Údaje"
nav_order: 5
lang: "sk"
source: the-data.md
source_hash: "6150cdc022fc"
nav_exclude: true
search_exclude: true
---
# Údaje {#the-data}

Všetky záznamy sú obyčajné súbory v dátovom priečinku (`%LOCALAPPDATA%\3DHeat\Watcher`, pokiaľ sa nezmenil,
pozrite [Inštalácia a spustenie](installing-and-running.md#where-everything-is)). Môžete ich čítať, kopírovať alebo mazať
bez watchera. Súbor `.jsonl` je obyčajný text, jeden riadok na udalosť (otvorí ho Poznámkový blok); súbor `.parquet`
je tabuľka, ktorú otvára prehliadač 3DHeat (Excel nie – `stats --csv` zapíše CSV súbory pre tabuľkové procesory).

## Priečinky relácií {#session-folders}
![priečinok relácie](../assets/img/session-folder.svg)

**Relácia** je jedno sedenie s jedným zdrojom: od chvíle, keď hra prvýkrát niečo povie, až kým sa zastaví (hra sa zavrie,
zápas skončí, jazda alebo let sa resetuje – stránka každého adaptéra hovorí, čo relácie začína a končí). Každá relácia
dostane priečinok:

```text
<data>\sessions\<game>\<YYYY-MM-DD_HH-MM-SS>_<adapter id>\
    events.jsonl
    heat.parquet
    meta.json
```

- `<game>` je názov hry, v ktorom každý znak okrem písmen, číslic, `.`, `_` a `-` je nahradený za `-` (najviac 60 znakov):
  `EA-SPORTS-F1-25`, `Counter-Strike-2`. Adaptéry, ktoré pokrývajú veľa hier (štatistiky Steamu, Steam Timeline,
  NVIDIA highlights), zaraďujú každú reláciu pod hru, ku ktorej patrí.
- Čas je začiatok relácie v miestnom čase. Relácie, ktoré opisujú minulosť (replay prevedený po zápase, súbor štatistík
  Steamu), používajú čas, ktorý im dá hra alebo súbor. Dve relácie, ktoré začnú v tej istej sekunde, dostanú pripojené
  `_2`, `_3`, ...
- Id relácie v databáze štatistík je `<game folder>/<session folder>`.

Relácia, v ktorej sa vôbec nič nezaznamenalo (hra sedela v menu, alebo spadla pri štarte), sa pri uzavretí zmaže, aby každé
spustenie nezanechalo prázdny priečinok.

Niektoré relácie majú ďalšie súbory. Relácia dem Counter-Strike 2 obsahuje vlastnú tabuľku a súhrn konvertora
(`<map>/<match>.parquet`, `<match>.match.json`). Relácia iRacing uvádza súbory `.ibt`, ktoré simulátor počas sedenia
zapísal, ako udalosti `telemetry_file`.

## events.jsonl {#eventsjsonl}

`events.jsonl` má jeden objekt JSON na riadok, jeden riadok na udalosť, zapísaný v okamihu, keď sa udalosť stane. Súbor
sa zapisuje po riadkoch, takže pád, výpadok prúdu alebo zabitý proces nestratia nič, čo už bolo zapísané; riadok skrátený
pádom sa pri čítaní preskočí a každý riadok pred ním platí.

Každý riadok má rovnaké základné stĺpce:

| Stĺpec | Typ | Čo je |
|---|---|---|
| `time` | číslo | sekundy od začiatku relácie (4 desatinné miesta), alebo herné hodiny, ak ich adaptér preberá |
| `ms` | celé číslo | čas na stene, Unix milisekundy |
| `event` | text | čo sa stalo: `position`, `spawn`, `death`, `kill`, `lap`, `teleport`, `session_start`, ... |
| `x`, `y`, `z` | číslo | kde, v jednotkách a osiach samotnej hry (pozrite `axes` v `meta.json`); len keď sú všetky tri známe a konečné |
| `player` | text | kto: meno, id, alebo `me` pre hráča, ktorý hrá (pozrite [Riadky hráča](#the-players-own-rows)) |
| `team` | text | ich strana, ak to hra uvádza |
| `session` | text | zápas, kolo, etapa, život alebo let, ku ktorým riadok patrí, ak to hra uvádza |

Každé ďalšie pole, ktoré hra hlási, nasleduje pod vlastným menom (`speed_kmh`, `gear`, `lap_time`, `weapon`,
`victim`, `hero`, ...). Polia bez hodnoty sa vynechajú, rovnako aj čísla, ktoré nie sú konečné. Dva syntetické riadky:

```json
{"time":12.3456,"ms":1777660501123,"event":"position","x":-412.5,"y":12.1,"z":233.0,"player":"me","session":"1","speed_kmh":187.4,"gear":5}
{"time":15.0,"ms":1777660503667,"event":"lap","x":-380.2,"y":12.0,"z":250.9,"player":"me","session":"1","lap_time":92.418,"lap":3}
```

Riadky bez pozície (riadok zo zoznamu zabití, postup na vyššiu úroveň, zmena štatistiky) zostanú v `events.jsonl` a
započítajú sa do štatistík. Do tabuľky idú len riadky s pozíciou.

### Riadky hráča {#the-players-own-rows}

Ktoré riadky patria hrajúcemu človeku, o tom hovorí zdroj, nikdy sa to neodhaduje. Riadok patrí hráčovi, keď

- jeho `player` je `me`: väčšina adaptérov, ktorých zdroj je vlastná hra hráča (telemetria vlastného auta alebo lietadla,
  integrácia stavu hry, žurnál);
- nesie `own_car` 1: závodné hry, ktoré zaznamenávajú každé auto pod menom jeho jazdca (EA SPORTS F1 podľa indexu
  hráčovho auta v hre, RaceRoom podľa jeho vlastného miesta, Automobilista 2 a Project CARS 2 podľa sledovaného účastníka)
  označujú auto hráča takto a meno jazdca nechávajú v `player`;
- jeho `player` je `player` relácie v `meta.json`: meno, ktoré zdroj dáva hráčovi – veliteľ Elite Dangerous (žurnál je
  vždy hráčov), a riadok League of Legends replaya s Riot ID z nastavení.

War Thunder a Rocket League pomenúvajú každého hráča a nehovoria, ktorý ste vy; s vaším menom v nastavení `player_names`
(pozrite [Nastavenia](installing-and-running.md#settings)) sa vaše riadky stanú `me`.
[NVIDIA highlights](nvidia-highlights.md) hľadajú moment práve v týchto riadkoch.

## heat.parquet {#heatparquet}

Keď sa relácia zatvorí, riadky `events.jsonl`, ktoré majú `x`, `y` a `z`, sa zapíšu do `heat.parquet`. Je to tabuľka, ktorú
otvára prehliadač 3DHeat. Ak relácia nemá pozície, tabuľka sa nezapíše.

- Stĺpce sú `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session`, za nimi každé ďalšie pole v poradí, v akom sa
  prvýkrát objaví.
- `x`, `y`, `z` a `time` sú 64-bitové desatinné čísla a `ms` je 64-bitové celé číslo. Ďalší stĺpec, ktorého všetky hodnoty sú
  čísla, je 64-bitové desatinné číslo; každý iný stĺpec je text s kódovaním slovníkom (chýbajúce hodnoty sú prázdny text
  a zoznamy alebo objekty sa zapisujú ako text JSON).
- Metadáta súboru majú kľúč `heat3d` s pokynmi na čítanie, takže prehliadač si mapuje stĺpce a osi sám (príklad, so
  skráteným zoznamom `extra`):

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

`up` je hore-os hry, `flipX`/`flipY`/`flipZ` zrkadlia os, aby ľavostranný svet nevyzeral zrkadlovo prevrátený, a `scale`
je mierka jednotiek prehliadača: prehliadač pri načítaní tabuľky vynásobí každú pozíciu týmto číslom (0.01 by premenilo
centimetre na metre). Každý adaptér zapisuje 1 a ponecháva jednotky hry – metre pre väčšinu, Source jednotky (palce) pre
Counter-Strike 2, Unreal jednotky (centimetre) pre Rocket League – pretože úroveň exportovaná z hry je v tých istých
jednotkách, takže riadky na nej sedia; tabuľky konvertora CS2 hovoria to isté. `units` v `meta.json` hovorí, čo je jedna
jednotka. Každá stránka hry uvádza svoje hodnoty v sekcii „Positions and axes“.

Letecké simulátory (DCS World, Microsoft Flight Simulator, X-Plane, záznamy Tacview z IL-2) kladú svoje riadky na zem a ich
pätička hovorí kde, takže prehliadač môže pod ne položiť skutočný svet:

```json
"geo": {"lat0": 42.0, "lon0": 42.0, "projection": "tangent-plane", "east": "x", "north": "z", "up": "y"}
```

`lat0`/`lon0` (stupne) sú začiatok plochej mapy, v ktorej sú riadky; `east`, `north` a `up` pomenúvajú stĺpce, ktoré držia
metre na východ a sever od neho a výšku nad morom. Začiatok je prvé zachytenie pre X-Plane a MSFS, referenčný bod záznamu
pre IL-2 a pevný začiatok divadla pre DCS (prvé zachytenie zaokrúhlené na celé stupne na divadle, ktoré watcher nepozná).
Tabuľka bez miesta na zemi nemá kľúč `geo` a všetko ostatné v pätičke je v oboch prípadoch rovnaké.

`heat.parquet` sa dá vždy znova vytvoriť z `events.jsonl` príkazom `python -m heat3d_watch table <session folder>`
(pozrite [Príkazy](commands.md#table)). Hodí sa to, keď pri zázname chýbal `pyarrow`.

## meta.json {#metajson}

`meta.json` zhrnie reláciu. Zapisuje sa pri otvorení relácie, najviac každých 30 sekúnd, kým prichádzajú udalosti alebo
štatistiky, a pri zatvorení relácie. Štatistiky sa medzi zápismi držia len v pamäti, takže pád môže stratiť najviac
posledných pol minúty z nich.

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

Relácia, ktorej zdroj pomenúva hráča (pozrite [Riadky hráča](#the-players-own-rows)), má aj `"player"`: meno, ktoré nesú riadky
hráča. Relácia na zemi (letecké simulátory) má aj `"geo": {"lat0": .., "lon0": ..}`, ktorý opakuje pätička jej `geo`.

- `started` / `ended`: miestny čas na sekundu; `ended` je `null`, kým relácia beží.
- `events`: koľkokrát sa každá udalosť stala, najčastejšie ako prvé. `positions` je počet riadkov s pozíciou.
- `stats`: čísla relácie. Adaptér každé nastaví, pripočíta k nemu, alebo podrží najvyššiu či najnižšiu hodnotu.
- Všetko ostatné, čo adaptér o sedení vie, sa objaví na najvyššej úrovni: trať, mapa, misia, id zápasu, id aplikácie Steam,
  súbor replaya, profil pamäte a build. Relácia dokončená obnovou má `"recovered": true`.

## watcher.sqlite {#watchersqlite}

`watcher.sqlite` je databáza štatistík. Riadok sa pridá pre každú reláciu pri jej zatvorení. Tri tabuľky sú obyčajné, takže
ich prečíta ktorýkoľvek nástroj SQL, notebook alebo tabuľkový procesor bez watchera:

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

Opätovné zaznamenanie relácie (obnova, replay prevedený znova) nahradí jej riadky. `multiplayer` je príznak adaptéra
(niektoré adaptéry ho nastavujú pre každú reláciu, napríklad DCS podľa misie), nie kontrola, či ste boli online. Hodnota
pravda/nepravda v `stats` je uložená ako text.

Príklad dotazu, najlepšie kolo podľa hry zo všetkých relácií (nižšie je lepšie):

```sql
SELECT s.game, MIN(t.value) AS best_lap
FROM stats t JOIN sessions s ON s.id = t.session
WHERE t.key = 'best_lap'
GROUP BY s.game;
```

`python -m heat3d_watch stats` vypíše súčty z týchto tabuliek (pozrite [Príkazy](commands.md#stats)); jeho stĺpec `best` je
najnižšia hodnota pri časoch uložených ako najlepšie a pri umiestneniach, najvyššia pri ostatných.

## Obnova po páde {#recovery-after-a-crash}

Keď sa `run` spustí, hľadá relácie, ktoré predchádzajúci watcher nechal otvorené: `meta.json` bez `ended` a `events.jsonl`
s aspoň jedným riadkom. Každú z nich dokončí:

- počty udalostí a počet pozícií sa znova spočítajú z `events.jsonl`, pričom sa preskočí riadok skrátený pádom;
- koniec je čas na stene posledného riadku (`ms`);
- štatistiky sú tie z posledného zápisu `meta.json` (najviac 30 sekúnd staré);
- pridá sa `"recovered": true`, zapíše sa `heat.parquet` a relácia sa dostane do `watcher.sqlite`.

Log hovorí „finished N session(s) left open by an earlier run“. Zámkový súbor bráni tomu, aby druhý watcher „obnovoval“
relácie jedného, ktorý ešte beží.

## Export do CSV {#csv-export}
![stats --csv a table](../assets/img/csv-and-table.svg)

```bash
python -m heat3d_watch stats --csv out
```

zapíše `out\sessions.csv`, `out\events.csv` a `out\stats.csv`. Každý súbor je jedna tabuľka `watcher.sqlite`, úplná,
s hlavičkovým riadkom, v kódovaní UTF-8. Časy sú Unix sekundy ako v databáze. `--game` export nezužuje; zapíšu sa všetky
relácie.

## Otvorenie relácie v prehliadači 3DHeat {#opening-a-session-in-the-3dheat-viewer}

Prehliadač: [github.com/Holdi601/3DHeat](https://github.com/Holdi601/3DHeat), dokumentácia
[holdi601.github.io/3DHeat](https://holdi601.github.io/3DHeat/) – jeho stránka
[kontajnera `.3dheat`](https://holdi601.github.io/3DHeat/container.html) opisuje formát jeden zápas v jednom súbore, ktorý
môžu zapisovať konvertory replayov.

Otvorte `heat.parquet` relácie v prehliadači 3DHeat. Pätička mu povie, ktorý stĺpec je pozícia, čas, hráč, tím a relácia
a ktorým smerom je hore, takže sa nič nemusí mapovať ručne. Pozície sú v súradniciach sveta hry. Nad úrovňou exportovanou
inými nástrojmi 3DHeat (napríklad z [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles)) sedia tam, kde sa to
stalo.

- **Heatmapy** používajú každý riadok s pozíciou; filtrujú sa podľa `event`, `player`, `team` alebo `session` ako ktorýkoľvek
  iný stĺpec.
- **Čiary** (line heat) kreslia čiaru od každého riadku hráča k jeho ďalšiemu, a pri prehrávaní je každý hráč bod, ktorý sa
  pohybuje po trase s chvostom za sebou. Panel Cesty v prehliadači vyberá zo stĺpca `event`, ktoré udalosti **začínajú**
  trasu a ktoré ju **ukončujú**. Watcher zapisuje ohraničujúce udalosti ako riadky s pozíciou, aby sa dali vybrať aj tam:
  - štarty: `spawn`, `respawn`, `session_start`. Štart zatvorí trasu, ktorá bola otvorená, bez kreslenia čiary k novému miestu.
  - konce: `death`, `finish`, `session_end` a `teleport`. Čiara vedie až k samotnému koncovému riadku, teda tam, kde hráč
    zomrel, zastavil sa alebo bol odvedený.

  Skok – miesto, ku ktorému sa dostanete bez cestovania – sú dva riadky: `teleport` na mieste, ktoré ste **opustili**, a štart
  na mieste, ktoré ste **dosiahli**, hneď za ním. Závodné adaptéry zapíšu jeden vždy, keď auto prešlo ďalej, než by mohlo
  prejsť (pretočenie alebo flashback, reset na cestu, späť do boxov, rýchly presun), so `spawn` na mieste príchodu (`respawn`
  pri resete BeamNG); riadok `teleport` nesie miesto príchodu ako `to_x`, `to_y`, `to_z` a vzdialenosť ako `metres`, riadok
  štartu nesie `after: "teleport"`. Nákladné adaptéry robia to isté pre trajekt, vlak alebo načítaný save a letecké adaptéry
  pre skok, ktorým by žiadne lietadlo nepreletelo. Takže keď sú medzi koncami `teleport` a medzi štartmi `spawn` – čo navrhuje
  prehliadač sám – trasa skončí tam, kde skok odviedol, a ďalšia začne tam, kde prišiel, a žiadna čiara nepreťína mapu.
  Trasa nikdy nepresahuje cez zmenu stĺpca `session`. Riadok pozície sa zapíše niekoľkokrát za sekundu (pri väčšine telemetrie
  10 Hz), čo dá plynulú čiaru.
- Stĺpec `session` rozdelí sedenie na kolá, etapy, životy alebo telá (Elite Dangerous takto drží riadky galaxie a riadky
  povrchu každej planéty oddelene). Vyberte jednu v prehliadači a pozrite sa len na túto časť.

Čo prehliadač s riadkami robí – filtre, farby, prehrávanie – je opísané v jeho vlastnej dokumentácii. Relácie dem
Counter-Strike 2 sa otvárajú cez `<map>/<match>.parquet` a `<match>.match.json` konvertora v kartách prehliadača
Heatmapa a Zápas. Pozície iRacing pochádzajú zo súborov `.ibt` uvedených v relácii, ktoré ich číta prehliadač sám.
