---
title: De gegevens
nav_order: 5
lang: "nl"
source: the-data.md
source_hash: "6150cdc022fc"
nav_exclude: true
search_exclude: true
---
# De gegevens {#the-data}

Alle opnames zijn gewone bestanden in de datamap (`%LOCALAPPDATA%\3DHeat\Watcher`, tenzij anders ingesteld; zie
[Installeren en uitvoeren](installing-and-running.md#where-everything-is)). Je kunt ze lezen, kopiëren of verwijderen
zonder de watcher. Een `.jsonl`-bestand is platte tekst, één gebeurtenis per regel (Kladblok opent het); een
`.parquet`-bestand is een tabel die de 3DHeat-viewer opent (Excel niet - `stats --csv` schrijft CSV-bestanden voor
spreadsheets).

## Sessiemappen {#session-folders}
![een sessiemap](../assets/img/session-folder.svg)

Een **sessie** is één zitting met één bron: vanaf het moment dat het spel voor het eerst iets zegt tot het stopt (het
spel sluit, een wedstrijd eindigt, een rit of vlucht wordt gereset - op de pagina van elke adapter staat wat een
sessie begint en beëindigt). Elke sessie krijgt een map:

```text
<data>\sessions\<game>\<YYYY-MM-DD_HH-MM-SS>_<adapter id>\
    events.jsonl
    heat.parquet
    meta.json
```

- `<game>` is de naam van het spel, waarbij elk teken dat geen letter, cijfer, `.`, `_` of `-` is, wordt vervangen door
  `-` (hoogstens 60 tekens): `EA-SPORTS-F1-25`, `Counter-Strike-2`. Adapters die veel spellen dekken (Steam-statistieken,
  Steam Timeline, NVIDIA highlights) zetten elke sessie onder het spel waartoe ze behoort.
- De tijd is het begin van de sessie in lokale tijd. Sessies die het verleden beschrijven (een replay die na de wedstrijd
  wordt omgezet, een Steam-statistiekbestand) gebruiken de tijd die het spel of bestand geeft. Twee sessies die in
  dezelfde seconde beginnen, krijgen `_2`, `_3`, ... achter de naam.
- Het id van de sessie in de statistiekendatabase is `<spelmap>/<sessiemap>`.

Een sessie waarin helemaal niets is opgenomen (het spel stond in zijn menu's, of crashte bij het starten) wordt bij het
sluiten verwijderd, zodat elke start geen lege map achterlaat.

Sommige sessies bevatten meer bestanden. Een Counter-Strike 2-demosessie bevat de eigen tabel en samenvatting van de
converter (`<map>/<match>.parquet`, `<match>.match.json`). Een iRacing-sessie somt de `.ibt`-bestanden die de sim
tijdens de zitting schreef op als `telemetry_file`-gebeurtenissen.

## events.jsonl {#eventsjsonl}

`events.jsonl` heeft één JSON-object per regel, één regel per gebeurtenis, geschreven op het moment dat de gebeurtenis
plaatsvindt. Het bestand wordt per regel weggeschreven, dus een crash, een stroomstoring of een gedood proces verliest
niets wat al was geschreven; een regel die door een crash is afgebroken, wordt overgeslagen wanneer het bestand wordt
gelezen, en elke regel ervoor blijft staan.

Elke regel heeft dezelfde basiskolommen:

| Kolom | Type | Wat het is |
|---|---|---|
| `time` | getal | seconden sinds de sessie begon (4 decimalen), of de eigen klok van het spel waar de adapter die doorgeeft |
| `ms` | geheel getal | kloktijd, Unix-milliseconden |
| `event` | tekst | wat er gebeurde: `position`, `spawn`, `death`, `kill`, `lap`, `teleport`, `session_start`, ... |
| `x`, `y`, `z` | getal | waar, in de eigen eenheden en assen van het spel (zie `axes` in `meta.json`); alleen aanwezig als alle drie bekend en eindig zijn |
| `player` | tekst | wie: een naam, een id, of `me` voor de persoon die speelt (zie [De eigen rijen van de speler](#the-players-own-rows)) |
| `team` | tekst | hun kant, wanneer het spel die noemt |
| `session` | tekst | de wedstrijd, ronde, etappe, het leven of de vlucht waartoe de rij behoort, wanneer het spel die noemt |

Elk ander veld dat het spel meldt, volgt onder zijn eigen naam (`speed_kmh`, `gear`, `lap_time`, `weapon`, `victim`,
`hero`, ...). Velden zonder waarde worden weggelaten, en getallen die niet eindig zijn ook. Twee verzonnen regels:

```json
{"time":12.3456,"ms":1777660501123,"event":"position","x":-412.5,"y":12.1,"z":233.0,"player":"me","session":"1","speed_kmh":187.4,"gear":5}
{"time":15.0,"ms":1777660503667,"event":"lap","x":-380.2,"y":12.0,"z":250.9,"player":"me","session":"1","lap_time":92.418,"lap":3}
```

Rijen zonder positie (een regel uit de killfeed, een level-up, een statistiekwijziging) blijven in `events.jsonl` en
tellen mee in de statistieken. Alleen rijen met een positie gaan in de tabel.

### De eigen rijen van de speler {#the-players-own-rows}

Wat voor rijen de persoon is die speelt, zegt de bron, nooit een gok. Een rij is van de speler wanneer

- zijn `player` `me` is: de meeste adapters, waarvan de bron het eigen spel van de speler is (telemetrie van de eigen
  auto of het eigen vliegtuig, een game-state-integratie, een journaal);
- hij `own_car` 1 draagt: de racespellen die elke auto onder de naam van de bestuurder opnemen (EA SPORTS F1 op de
  spelersauto-index van het spel, RaceRoom op zijn eigen plek, Automobilista 2 en Project CARS 2 op de bekeken
  deelnemer) markeren de auto van de speler zo en bewaren de naam van de bestuurder in `player`;
- zijn `player` de `player` van de sessie in `meta.json` is: de naam die de bron aan de speler geeft - de commandant
  van Elite Dangerous (het journaal is altijd van de speler), of de regel van de Riot-ID in de instellingen bij een
  League of Legends-replay.

War Thunder en Rocket League noemen elke speler en zeggen niet welke jij bent; met je naam in de instelling
`player_names` (zie [Instellingen](installing-and-running.md#settings)) worden jouw rijen `me`.
[NVIDIA highlights](nvidia-highlights.md) kijken een moment alleen in deze rijen op.

## heat.parquet {#heatparquet}

Wanneer een sessie sluit, worden de rijen van `events.jsonl` die `x`, `y` en `z` hebben naar `heat.parquet`
geschreven. Dit is de tabel die de 3DHeat-viewer opent. Als de sessie geen posities heeft, wordt er geen tabel
geschreven.

- De kolommen zijn `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session`, gevolgd door elk ander veld in de
  volgorde waarin het voor het eerst voorkomt.
- `x`, `y`, `z` en `time` zijn 64-bit getallen met drijvende komma, en `ms` is een 64-bit geheel getal. Een verdere
  kolom waarvan alle waarden getallen zijn, is een 64-bit getal met drijvende komma; elke andere kolom is tekst met
  woordenboekcodering (ontbrekende waarden zijn lege tekst, en lijsten of objecten worden als JSON-tekst geschreven).
- De metadata van het bestand heeft een sleutel `heat3d` met de leesinstructies, zodat de viewer de kolommen en assen
  zelf koppelt (een voorbeeld, met de lijst `extra` ingekort):

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

`up` is de opwaartse as van het spel; `flipX`/`flipY`/`flipZ` spiegelen een as, zodat een linkshandige wereld niet
gespiegeld wordt getekend; `scale` is de eenheidsschaal van de viewer: de viewer vermenigvuldigt elke positie ermee
wanneer hij de tabel laadt (0.01 zou centimeters in meters veranderen). Elke adapter schrijft 1 en houdt de eigen
eenheden van het spel aan - meters voor de meeste, Source-eenheden (inches) voor Counter-Strike 2, Unreal-eenheden
(centimeters) voor Rocket League - omdat een level dat uit het spel is geëxporteerd in diezelfde eenheden is, zodat
de rijen erop vallen; de tabellen van de CS2-converter zeggen hetzelfde. `units` in `meta.json` zegt wat één eenheid
is. De pagina van elk spel somt zijn waarden op onder "Positions and axes".

De vluchtsimulators (DCS World, Microsoft Flight Simulator, X-Plane, de Tacview-opnames van IL-2) zetten hun rijen op de
aarde, en hun voettekst zegt waar, zodat de viewer de echte wereld eronder kan leggen:

```json
"geo": {"lat0": 42.0, "lon0": 42.0, "projection": "tangent-plane", "east": "x", "north": "z", "up": "y"}
```

`lat0`/`lon0` (graden) zijn de oorsprong van de platte kaart waarin de rijen staan; `east`, `north` en `up` noemen de
kolommen met de meters oost en noord van die oorsprong en de hoogte boven zeeniveau. De oorsprong is de eerste fix bij
X-Plane en MSFS, het referentiepunt van de opname bij IL-2, en de vaste oorsprong van het theater bij DCS (de eerste fix
afgerond op hele graden, bij een theater dat de watcher niet kent). Een tabel zonder plaats op de aarde heeft geen
`geo`-sleutel, en de rest van de voettekst is in beide gevallen hetzelfde.

`heat.parquet` kan altijd opnieuw worden gebouwd uit `events.jsonl` met
`python -m heat3d_watch table <session folder>` (zie [Commando's](commands.md#table)). Dat is handig wanneer `pyarrow`
ontbrak terwijl de sessie werd opgenomen.

## meta.json {#metajson}

`meta.json` vat de sessie samen. Het wordt geschreven wanneer de sessie opent, hoogstens elke 30 seconden terwijl er
gebeurtenissen of statistieken binnenkomen, en wanneer de sessie sluit. Statistieken worden alleen in het geheugen
tussen die schrijfacties bewaard, dus een crash kan hooguit het laatste halve minuutje ervan verliezen.

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

Een sessie waarvan de bron de speler noemt (zie [De eigen rijen van de speler](#the-players-own-rows)), heeft ook
`"player"`: de naam die de eigen rijen van de speler dragen. Een sessie op de aarde (de vluchtsimulators) heeft ook
`"geo": {"lat0": .., "lon0": ..}`, de oorsprong die de `geo` van de voettekst herhaalt.

- `started` / `ended`: lokale tijd tot op de seconde; `ended` is `null` terwijl de sessie loopt.
- `events`: hoe vaak elke gebeurtenis voorkwam, het vaakst eerst. `positions` is het aantal rijen met een positie.
- `stats`: de cijfers van de sessie. Een adapter zet elk ervan, telt erbij op, of houdt het maximum of minimum bij.
- Wat de adapter verder over de zitting weet, volgt op het hoogste niveau: de baan, kaart, missie, wedstrijd-id, de
  Steam-app-id, het replaybestand, het geheugenprofiel en de build. Een sessie die door herstel is afgemaakt, heeft
  `"recovered": true`.

## watcher.sqlite {#watchersqlite}

`watcher.sqlite` is de statistiekendatabase. Er wordt een regel toegevoegd voor elke sessie wanneer die sluit. De drie
tabellen zijn gewoon, dus elk SQL-hulpmiddel, notebook of spreadsheet kan ze lezen zonder de watcher:

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

Een sessie opnieuw opnemen (herstel, een replay die opnieuw wordt omgezet) vervangt de rijen ervan.
`multiplayer` is de vlag van de adapter (sommige adapters zetten die per sessie, bijvoorbeeld DCS uit de missie), geen
controle of je online was. Een waar/onwaar-waarde in `stats` wordt als tekst opgeslagen.

Een voorbeeldquery, de beste ronde per spel over alle sessies (lager is beter):

```sql
SELECT s.game, MIN(t.value) AS best_lap
FROM stats t JOIN sessions s ON s.id = t.session
WHERE t.key = 'best_lap'
GROUP BY s.game;
```

`python -m heat3d_watch stats` drukt totalen uit deze tabellen af (zie [Commando's](commands.md#stats)); de kolom `best`
is de laagste waarde voor tijden die als beste worden bewaard en voor plaatsen, de hoogste voor de rest.

## Herstel na een crash {#recovery-after-a-crash}

Wanneer `run` start, zoekt het naar sessies die een eerdere watcher open heeft gelaten: een `meta.json` zonder
`ended`, en een `events.jsonl` met minstens één regel. Het maakt elk ervan af:

- de aantallen gebeurtenissen en het aantal posities worden opnieuw geteld uit `events.jsonl`, waarbij een afgebroken
  regel wordt overgeslagen;
- het einde is de klokketijd van de laatste regel (`ms`);
- de statistieken zijn die van de laatste schrijfactie van `meta.json` (hoogstens 30 seconden oud);
- `"recovered": true` wordt toegevoegd, `heat.parquet` wordt geschreven, en de sessie gaat in `watcher.sqlite`.

Het logboek zegt "finished N session(s) left open by an earlier run". Het lockbestand zorgt ervoor dat een tweede
watcher de sessies van een watcher die nog draait niet "herstelt".

## CSV-export {#csv-export}
![stats --csv en table](../assets/img/csv-and-table.svg)

```bash
python -m heat3d_watch stats --csv out
```

schrijft `out\sessions.csv`, `out\events.csv` en `out\stats.csv`. Elk bestand is één tabel van `watcher.sqlite`,
compleet, met een kopregel, als UTF-8. Tijden zijn Unix-seconden zoals in de database. `--game` beperkt de export niet;
elke sessie wordt geschreven.

## Een sessie openen in de 3DHeat-viewer {#opening-a-session-in-the-3dheat-viewer}

De viewer: [github.com/Holdi601/3DHeat](https://github.com/Holdi601/3DHeat), documentatie
[holdi601.github.io/3DHeat](https://holdi601.github.io/3DHeat/) - de pagina over het
[`.3dheat`-containerformaat](https://holdi601.github.io/3DHeat/container.html) beschrijft het formaat met één bestand per
wedstrijd dat de replayconverters kunnen schrijven.

Open de `heat.parquet` van een sessie in de 3DHeat-viewer. De voettekst vertelt de viewer welke kolom de positie is,
de tijd, de speler, de kant en de sessie, en welke as boven is, zodat er niets met de hand moet worden gekoppeld.
Posities staan in de eigen wereldcoördinaten van het spel. Getekend over een level dat met de andere 3DHeat-tools is
geëxporteerd (bijvoorbeeld uit [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles)), vallen ze op de plek
waar ze gebeurden.

- **Heatmaps** gebruiken elke rij met een positie, gefilterd op `event`, `player`, `team` of `session` zoals elke andere
  kolom.
- **Routelijnen** trekken een lijn van elke rij van een speler naar diens volgende rij, en bij het afspelen is elke
  speler een punt dat langs de route beweegt met een staart erachter. Het Routes-paneel van de viewer kiest, uit de
  kolom `event`, welke gebeurtenissen een route **beginnen** en welke er een **beëindigen**. De watcher schrijft de
  begrenzende gebeurtenissen als rijen met een positie, zodat ze daar kunnen worden gekozen:
  - beginnen: `spawn`, `respawn`, `session_start`. Een begin sluit de route die open was zonder een lijn naar de nieuwe
    plek te trekken.
  - eindigen: `death`, `finish`, `session_end`, en `teleport`. De lijn loopt tot de eindrij zelf, waar de speler
    doodging, stopte of werd weggehaald.

  Een sprong - een plek die is bereikt zonder daarheen te reizen - is twee rijen: `teleport` op de plek die is
  **verlaten**, en een begin op de plek die is **bereikt**, direct erna. De racingadapters schrijven er een wanneer de
  auto verder is bewogen dan hij kon rijden (een terugspoelen of flashback, een reset naar de weg, terug naar de pits,
  een snelreis), met `spawn` bij de aankomst (`respawn` voor de reset van BeamNG); de `teleport`-rij draagt de aankomst
  als `to_x`, `to_y`, `to_z` en de afstand als `metres`, de startrij `after: "teleport"`. De truckadapters doen hetzelfde
  voor een veerboot, een trein of een geladen save, en de vluchtadapters voor een sprong die geen vliegtuig kan maken.
  Dus met `teleport` onder de eindes en `spawn` onder de beginnen - wat de viewer zelf voorstelt - eindigt een route waar
  de sprong begon en begint de volgende waar hij aankwam, en loopt er geen lijn over de kaart. Een route loopt nooit over
  een wisseling van de kolom `session` heen. Een positierij wordt enkele keren per seconde geschreven (10 Hz voor de
  meeste telemetrie), wat een vloeiende lijn geeft.
- De kolom `session` splitst een zitting in de eigen ronden, etappes, levens of lichamen (Elite Dangerous houdt
  galactische rijen en de rijen op het oppervlak van elke planeet op die manier uit elkaar). Kies er één in de viewer om
  dat deel alleen te bekijken.

Wat de viewer met de rijen doet - filters, kleuren, afspelen - staat beschreven in de eigen documentatie van de viewer.
Counter-Strike 2-demosessies worden geopend via het `<map>/<match>.parquet` en `<match>.match.json` van de converter, in
de tabbladen Heatmap en Match van de viewer. De posities van iRacing komen uit de `.ibt`-bestanden die in de sessie
staan, die de viewer zelf leest.
