---
title: "Az adatok"
nav_order: 5
lang: "hu"
source: the-data.md
source_hash: "6150cdc022fc"
nav_exclude: true
search_exclude: true
---
# Az adatok {#the-data}

Minden felvétel sima fájl az adatmappában (`%LOCALAPPDATA%\3DHeat\Watcher`, hacsak nem módosítottad, lásd
[Telepítés és futtatás](installing-and-running.md#where-everything-is)). A figyelő nélkül is olvashatod, másolhatod vagy
törölheted őket. Egy `.jsonl` fájl sima szöveg, soronként egy esemény (a Jegyzettömb megnyitja); a `.parquet` fájl egy
tábla, amelyet a 3DHeat nézegető megnyit (az Excel nem - a `stats --csv` CSV-fájlokat ír táblázatkezelőhöz).

## Munkamenet-mappák {#session-folders}
![a session folder](../assets/img/session-folder.svg)


Egy **munkamenet** egyetlen forrás egyetlen ülése: attól a pillanattól kezdve, hogy a játék először mond valamit, addig,
amíg meg nem áll (a játék bezárul, egy mérkőzés véget ér, egy út vagy repülés visszaáll - minden adapter oldala leírja, mi
kezdi és zárja le a munkameneteit). Minden munkamenet kap egy mappát:

```text
<data>\sessions\<game>\<YYYY-MM-DD_HH-MM-SS>_<adapter id>\
    events.jsonl
    heat.parquet
    meta.json
```

- A `<game>` a játék neve, ahol a betűkön, számokon, `.`, `_` és `-` jeleken kívüli karakterek mind `-`-re cserélődnek
  (legfeljebb 60 karakter): `EA-SPORTS-F1-25`, `Counter-Strike-2`. Azok az adapterek, amelyek sok játékot fednek le (Steam-
  statisztika, Steam Timeline, NVIDIA-kiemelések), minden munkamenetet abba a játékba sorolnak, amelyhez tartozik.
- Az idő a munkamenet kezdete helyi időben. A múltat leíró munkamenetek (a mérkőzés után konvertált visszajátszás, egy Steam
  statisztikai fájl) azt az időt használják, amelyet a játék vagy a fájl ad meg. Ha két munkamenet ugyanabban a
  másodpercben kezdődik, a végére `_2`, `_3`, ... kerül.
- A munkamenet azonosítója a statisztikai adatbázisban `<game folder>/<session folder>`.

Az a munkamenet, amelyben semmi sem rögzült (a játék a menüiben állt, vagy indításkor összeomlott), lezáráskor törlődik,
hogy minden indítás ne hagyjon maga után üres mappát.

Egyes munkamenetekben több fájl van. Egy Counter-Strike 2 demó-munkamenet tartalmazza a konverter saját tábláját és
összefoglalóját (`<map>/<match>.parquet`, `<match>.match.json`). Egy iRacing-munkamenet felsorolja a szimulátor által az ülés
alatt írt `.ibt` fájlokat `telemetry_file` eseményekként.

## events.jsonl {#eventsjsonl}

Az `events.jsonl`-ben soronként egy JSON-objektum van, soronként egy esemény, abban a pillanatban írva, amikor az esemény
megtörténik. A fájl soronkénti pufferelésű, így egy összeomlás, áramszünet vagy megölt folyamat nem veszít el semmit, ami már
ki volt írva; az összeomlástól csonkolt sor olvasáskor kimarad, és a fölötte lévő sorok megmaradnak.

Minden sornak ugyanazok az alaposzlopai vannak:

| Oszlop | Típus | Mit jelent |
|---|---|---|
| `time` | szám | másodpercek a munkamenet kezdete óta (4 tizedesjegy), vagy a játék saját órája, ahol az adapter ezt átadja |
| `ms` | egész | falióra-idő, Unix-milliszekundum |
| `event` | szöveg | mi történt: `position`, `spawn`, `death`, `kill`, `lap`, `teleport`, `session_start`, ... |
| `x`, `y`, `z` | szám | hol, a játék saját egységeiben és tengelyeiben (lásd a `meta.json` `axes` részét); csak akkor van jelen, ha mindhárom ismert és véges |
| `player` | szöveg | ki: név, azonosító, vagy `me` a játékost jelölő személy esetén (lásd [A játékos saját sorai](#the-players-own-rows)) |
| `team` | szöveg | az oldaluk, ha a játék megmondja |
| `session` | szöveg | a mérkőzés, forduló, szakasz, élet vagy repülés, amelyhez a sor tartozik, ha a játék megmondja |

Minden más mezőt, amelyet a játék jelent, a saját nevén követ (`speed_kmh`, `gear`, `lap_time`, `weapon`, `victim`, `hero`, ...).
Az érték nélküli mezők kimaradnak, ahogy a véges értékek nélküli számok is. Két kitalált sor:

```json
{"time":12.3456,"ms":1777660501123,"event":"position","x":-412.5,"y":12.1,"z":233.0,"player":"me","session":"1","speed_kmh":187.4,"gear":5}
{"time":15.0,"ms":1777660503667,"event":"lap","x":-380.2,"y":12.0,"z":250.9,"player":"me","session":"1","lap_time":92.418,"lap":3}
```

A pozíció nélküli sorok (egy killfeed-sor, egy szintlépés, egy statisztika-változás) az `events.jsonl`-ben maradnak, és
beleszámítanak a statisztikába. Csak a pozícióval rendelkező sorok kerülnek a táblába.

### A játékos saját sorai {#the-players-own-rows}

Hogy mely sorok a játékost jelölik, azt a forrás mondja meg, soha nem találgatják. Egy sor akkor a játékos saját sora, ha

- a `player` értéke `me`: a legtöbb adapter, amelynek a forrása a játékos saját játéka (a saját autó vagy repülőgép
  telemetriája, egy játékállapot-integráció, egy napló);
- rajta van az `own_car` 1: a versenyjátékok, amelyek minden autót a pilótája nevén rögzítenek (az EA SPORTS F1 a játék
  játékos-autó indexe alapján, a RaceRoom a saját helye alapján, az Automobilista 2 és a Project CARS 2 a megtekintett
  résztvevő alapján), így jelölik a játékos autóját, és a pilóta nevét a `player`-ben tartják meg;
- a `player` értéke megegyezik a munkamenet `player` értékével a `meta.json`-ban: az a név, amelyet a forrás a játékosnak
  ad - az Elite Dangerous parancsnoka (a napló mindig a játékosé), vagy egy League of Legends visszajátszás sora a
  beállításokban megadott Riot-azonosítóval.

A War Thunder és a Rocket League minden játékost névvel említ, és nem mondja meg, melyik vagy te; ha a neved a
`player_names` beállításban szerepel (lásd [Beállítások](installing-and-running.md#settings)), a sorok `me`-vé válnak.
Az [NVIDIA-kiemelések](nvidia-highlights.md) pontosan ezekben a sorokban keresnek egy pillanatot.

## heat.parquet {#heatparquet}

Amikor egy munkamenet lezárul, az `events.jsonl` azon sorai, amelyeknek van `x`, `y` és `z` értéke, a `heat.parquet`-be
íródnak. Ez az a tábla, amelyet a 3DHeat nézegető megnyit. Ha a munkamenetnek nincsenek pozíciói, nem íródik tábla.

- Az oszlopok: `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session`, utána minden más mező abban a sorrendben,
  ahogy először megjelenik.
- Az `x`, `y`, `z` és `time` 64 bites lebegőpontos számok, az `ms` 64 bites egész. Minden további oszlop, amelynek értékei
  mind számok, 64 bites lebegőpontos szám; minden más oszlop szótár-kódolt szöveg (a hiányzó értékek üres szövegek, a listák
  és objektumok JSON-szövegként íródnak).
- A fájl metaadatai között van egy `heat3d` kulcs az olvasási utasításokkal, így a nézegető magától leképezi az oszlopokat és
  a tengelyeket (egy példa, az `extra` lista rövidítve):

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

Az `up` a játék felfelé mutató tengelye; a `flipX`/`flipY`/`flipZ` tükröz egy tengelyt, hogy egy balkezes világ ne tükrözve
jelenjen meg; a `scale` a nézegető mértékegység-skálája: a nézegető a tábla betöltésekor minden pozíciót megszoroz vele (0,01
centimétert méterré alakítana). Minden adapter 1-et ír, és megtartja a játék saját egységeit - a legtöbbnél méter, a Counter-
Strike 2-nél Source-egység (hüvelyk), a Rocket League-nél Unreal-egység (centiméter) -, mert a játékból exportált szint ugyanebben
az egységben van, így a sorok ráesnek; a CS2-konverter saját táblái is ezt mondják. A `meta.json` `units` mezője mondja meg, mit
jelent egy egység. Minden játék oldala felsorolja az értékeit a „Positions and axes” (Pozíciók és tengelyek) részben.

A repülési szimulátorok (DCS World, Microsoft Flight Simulator, X-Plane, az IL-2 Tacview-felvételei) a sorokat a Földre teszik,
és a láblécük megmondja, hol, így a nézegető alá teheti a valódi világot:

```json
"geo": {"lat0": 42.0, "lon0": 42.0, "projection": "tangent-plane", "east": "x", "north": "z", "up": "y"}
```

A `lat0`/`lon0` (fok) annak a lapos térképnek az origója, amelyben a sorok vannak; az `east`, `north` és `up` megnevezi azokat az
oszlopokat, amelyek a keletre és északra mért métereket, valamint a tengerszint feletti magasságot tartalmazzák. Az origó az
X-Plane-nél és az MSFS-nél az első pozíció, az IL-2-nél a felvétel referenciapontja, a DCS-nél pedig a hadszíntér rögzített
origója (az első pozíció egész fokra kerekítve egy olyan hadszíntéren, amelyet a figyelő nem ismer). Egy olyan táblának, amelynek
nincs helye a Földön, nincs `geo` kulcsa; a lábléc többi része mindkét esetben ugyanaz.

A `heat.parquet` mindig újraépíthető az `events.jsonl`-ből a `python -m heat3d_watch table <session folder>` paranccsal (lásd
[Parancsok](commands.md#table)). Ez akkor hasznos, ha a `pyarrow` hiányzott a munkamenet rögzítésekor.

## meta.json {#metajson}

A `meta.json` összefoglalja a munkamenetet. Akkor íródik, amikor a munkamenet megnyílik, legfeljebb 30 másodpercenként,
miközben események vagy statisztikák érkeznek, és amikor a munkamenet lezárul. A statisztikák csak a memóriában vannak meg
ezek az írások között, így egy összeomlás legfeljebb az utolsó fél perc statisztikáját veheti el.

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

Az a munkamenet, amelyben a forrás megnevezi a játékost (lásd [A játékos saját sorai](#the-players-own-rows)), a `"player"`
mezőt is tartalmazza: azt a nevet, amelyet a játékos saját sorai hordoznak. A Földön lévő munkamenet (a repülési szimulátorok)
a `"geo": {"lat0": .., "lon0": ..}` mezőt is tartalmazza, amelyet a lábléc `geo` része ismételten megad.

- `started` / `ended`: helyi idő másodpercre pontosan; az `ended` `null`, amíg a munkamenet fut.
- `events`: hányszor történt meg minden esemény, a leggyakoribb először. A `positions` a pozícióval rendelkező sorok száma.
- `stats`: a munkamenet számai. Egy adapter mindegyiket beállítja, hozzáadja hozzá, vagy megtartja a maximumot vagy a minimumot.
- Minden más, amit az adapter az ülésről tud, a legfelső szinten követi: a pálya, a térkép, a küldetés, a mérkőzés-azonosító,
  a Steam-alkalmazásazonosító, a visszajátszás-fájl, a memória-profil és a build. A helyreállítással befejezett munkamenet
  `"recovered": true` jelölést kap.

## watcher.sqlite {#watchersqlite}

A `watcher.sqlite` a statisztikai adatbázis. Minden munkamenethez egy sor íródik, amikor lezárul. A három tábla egyszerű, így
bármely SQL-eszköz, jegyzetfüzet vagy táblázatkezelő a figyelő nélkül olvashatja őket:

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

Egy munkamenet újrarögzítése (helyreállítás, egy újra konvertált visszajátszás) lecseréli a sorait. A `multiplayer` az adapter
jelzője (egyes adapterek munkamenetenként állítják, például a DCS a küldetésből), nem annak ellenőrzése, hogy online voltál-e.
Az igaz/hamis érték a `stats`-ban szövegként tárolódik.

Példa lekérdezés: játékonként a legjobb köridő az összes munkamenetben (az alacsonyabb a jobb):

```sql
SELECT s.game, MIN(t.value) AS best_lap
FROM stats t JOIN sessions s ON s.id = t.session
WHERE t.key = 'best_lap'
GROUP BY s.game;
```

A `python -m heat3d_watch stats` ezekből a táblákból ír ki összesítéseket (lásd [Parancsok](commands.md#stats)); a `best`
oszlopa a legjobbként megtartott időknél és a helyezéseknél a legkisebb érték, a többinél a legnagyobb.

## Helyreállítás összeomlás után {#recovery-after-a-crash}

Amikor a `run` elindul, olyan munkameneteket keres, amelyeket egy korábbi figyelő nyitva hagyott: egy `meta.json`, amelyben nincs
`ended`, és egy `events.jsonl`, amelyben legalább egy sor van. Mindegyiket befejezi:

- az eseményszámokat és a pozíciók számát újraszámolja az `events.jsonl`-ből, a csonkolt sort kihagyva;
- a vége az utolsó sor falióra-ideje (`ms`);
- a statisztikák az utolsó `meta.json` írásából valók (legfeljebb 30 másodpercesek);
- hozzáadódik a `"recovered": true`, íródik a `heat.parquet`, és a munkamenet bekerül a `watcher.sqlite`-ba.

A napló ezt írja: „finished N session(s) left open by an earlier run”. A zárfájl megakadályozza, hogy egy második figyelő
„helyreállítsa” egy még futó figyelő munkameneteit.

## CSV-export {#csv-export}
![stats --csv and table](../assets/img/csv-and-table.svg)


```bash
python -m heat3d_watch stats --csv out
```

Ez az `out\sessions.csv`, `out\events.csv` és `out\stats.csv` fájlt írja. Mindegyik fájl a `watcher.sqlite` egy-egy teljes
táblája, fejléc-sorral, UTF-8 kódolásban. Az idők Unix-másodpercek, ahogy az adatbázisban is. A `--game` nem szűkíti az
exportot; minden munkamenet kiíródik.

## Munkamenet megnyitása a 3DHeat nézegetőben {#opening-a-session-in-the-3dheat-viewer}

A nézegető: [github.com/Holdi601/3DHeat](https://github.com/Holdi601/3DHeat), a dokumentáció:
[holdi601.github.io/3DHeat](https://holdi601.github.io/3DHeat/) - a
[`.3dheat` konténer](https://holdi601.github.io/3DHeat/container.html) oldala írja le azt a fájlonkénti-mérkőzés formátumot,
amelyet a visszajátszás-konverterek írhatnak.

Nyisd meg egy munkamenet `heat.parquet`-jét a 3DHeat nézegetőben. A lábléc megmondja a nézegetőnek, melyik oszlop a pozíció, az
idő, a játékos, az oldal és a munkamenet, és hogy melyik irány a felfelé, így semmit sem kell kézzel leképezni. A pozíciók a játék
saját világkoordinátáiban vannak. A többi 3DHeat-eszközzel exportált szint fölé rajzolva (például a
[3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles) eszközzel) oda kerülnek, ahol történtek.

- A **hőtérképek** minden pozícióval rendelkező sort használnak, és az `event`, `player`, `team` vagy `session` szerint szűrhetők,
  mint minden más oszlop.
- A **vonalhő** egy vonalat húz a játékos minden sorától a következőig, lejátszáskor pedig minden játékos egy pontként mozog
  az útvonalon, mögötte farokkal. A nézegető Útvonalak panelje az `event` oszlop alapján választja ki, mely események **kezdenek**
  és melyek **zárnak le** egy útvonalat. A figyelő a határoló eseményeket pozícióval rendelkező sorként írja, így ott
  kiválaszthatók:
  - kezdetek: `spawn`, `respawn`, `session_start`. Egy kezdet lezárja a nyitva lévő útvonalat anélkül, hogy vonalat húzna az új
    helyre.
  - végek: `death`, `finish`, `session_end` és `teleport`. A vonal magáig a vég sorig fut, ahol a játékos meghalt, megállt vagy
    elvitték.

  Az ugrás - olyan hely, amelyet nem utazással értek el - két sor: egy `teleport` a **elhagyott** helynél, és egy kezdet az
  **megérkezett** helynél, közvetlenül utána. A versenyzési adapterek mindig írnak egyet, amikor az autó az elvárhatónál tovább
  mozdult (visszatekerés vagy flashback, visszaállítás az útra, vissza a boxba, gyorsutazás), a `spawn`-nal az érkezésnél
  (a BeamNG visszaállításához a `respawn`); a `teleport` sor az érkezést `to_x`, `to_y`, `to_z` mezőkben, a távolságot
  `metres`-ben viszi, a kezdő sor pedig `after: "teleport"`. A teherautó-adapterek ugyanezt teszik komppal, vonattal vagy
  betöltött mentéssel, a repülési adapterek pedig olyan ugrásoknál, amelyet egyetlen repülőgép sem tudott volna megtenni. Így ha
  a `teleport` a végek, a `spawn` pedig a kezdetek között van - amit a nézegető magától ajánl -, az útvonal ott ér véget, ahol az
  ugrás elindult, a következő pedig ott kezdődik, ahová megérkezett, és nincs vonal, amely átmetszené a térképet. Egy útvonal soha
  nem fut át a `session` oszlop változásán. Egy pozíciósor másodpercenként néhányszor íródik (a legtöbb telemetriánál 10 Hz), ez
  adja a sima vonalat.
- A `session` oszlop a munkamenetet a fordulóira, szakaszaira, életeire vagy testeire bontja (az Elite Dangerous így tartja külön a
  galaktikus sorokat és az egyes bolygók felszíni soraikat). Válassz egyet a nézegetőben, hogy csak azt a részt nézd.

Azt, hogy a nézegető mit csinál a sorokkal - szűrők, színek, lejátszás -, a nézegető saját dokumentációja írja le. A Counter-Strike
2 demó-munkamenetek a konverter `<map>/<match>.parquet` és `<match>.match.json` fájljain keresztül nyílnak meg a nézegető hő- és
mérkőzés-füleiben. Az iRacing pozíciói a munkamenetben felsorolt `.ibt` fájlokból jönnek, amelyeket a nézegető maga olvas be.
