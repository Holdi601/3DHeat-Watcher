---
title: "Steam Timeline (platform)"
nav_order: 44
lang: "hu"
source: game-steam-timeline.md
source_hash: "3878efe0d7f1"
nav_exclude: true
search_exclude: true
---
# Steam Timeline (platform) {#steam-timeline-platform}

A watcher elmenti, amit a Steam Timeline a játékaidról megőriz, hogy később statisztikaként és idővonalon is megnézhesd a történetedet.

*Technikai részletek: adapter `steam-timeline`, típus [`platform`](sources-and-rules.md); folyamatosan fut (nem vár arra, hogy játék induljon), és 10 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- egy munkamenet idővonal-fájlonként: kezdete és vége (session_start, session_end)
- játék közben feloldott eredmények, idővel
- játékmód-változások (játék, előkészítés, menük, betöltőképernyő)
- játékok által az ISteamTimeline-on keresztül hozzáadott események, címmel és leírással, az ikonjuk nevén
- játékfázisok (meccs, küldetés) a címkéikkel; a bennük lévő események a fázis azonosítóját viselik `session` mezőként
- a játék által az idővonalon megjelenített állapotleírások ("3. kör")
- a Steam saját rögzítési hibái

## Honnan jön {#where-it-comes-from}

%STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json

## Hogyan kapcsolható be {#how-to-switch-it-on}

Steam > Beállítások > Játékfelvétel: rögzíts háttérben vagy kérésre (a Steam ekkor ír idővonalakat)

## Hogyan működik {#how-it-works}

Amit az indító és a grafikus illesztőprogram tart nyilván a játékról: a Steam statisztikái, eredményei, játékideje és idővonalai, valamint az NVIDIA kiemelései és klipjei.

Egyik forrásnak sem kell, hogy a játék együttműködjön vagy fusson, így az itt lévő három adapter mindig be van kapcsolva, és néhány másodpercenként néhány fájlt néz meg.

#### Steam Timeline (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`, amelyet a Steam Játékfelvétel bekapcsolt állapotában ír. A fájl JSON, a számok szövegként: "daterecorded" (Unix-másodperc), "starttime"/"endtime" (ms), és "entries", mindegyik {"id", "time" (ms a daterecorded óta), "type", ...}. Valódi fájlokon látott típusok:
```text
achievement        achievement_name - Steam adds these for every game
gamemode           mode, an ETimelineGameMode: 1 playing, 2 staging, 3 menus,
                   4 loading screen
error              description - Steam's own ("#GameRecording_RecordingFailed")
event              a game's AddInstantaneousTimelineEvent/AddRangeTimelineEvent:
                   title, description, icon, priority, duration (ms),
                   possible_clip - "You killed <name>" / "with the <weapon>"
state_description  title - SetTimelineTooltip ("Round 3")
phase              a StartGamePhase..EndGamePhase span: duration (ms), tags
                   [{name, icon, group, priority}] (mode, map ...)
```
A fájl elrendezése a Steamé, és nincs dokumentálva; a mezők az API paraméterei. Minden más típus a saját nevén, a mezőivel együtt kerül rögzítésre.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Ugyanez a modul szolgálja ki ezeket is: [NVIDIA highlights (platform)](game-nvidia-highlights.md), [Steam-statisztikák (platform)](game-steam-stats.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Pozíciók rögzítve | nem |
| Felfelé mutató tengely | `y` |
| Mértékegység | méter |
| Tükrözve a megtekintőnek | nincs |
| Mértékegység-szorzó (`scale`: a megtekintő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json`-jába (`axes`), és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe is, így a 3DHeat megtekintő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos {#multiplayer}

- Online játszottként jelölve (`multiplayer`): **nem**. A `games --markdown` ezt "single-player" jelöléssel mutatja.
- `platform` típus: csak azt olvassa, amit a játék vagy a platform kiad (amit a Steam vagy a grafikus illesztőprogram tart nyilván), így online játékban is rögzít, nemcsak offline; a jelző csak azt dönti el, szabad-e valaha memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amelyet online játszottként jelöltek meg – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Statisztikakulcsok, amelyeket ennek az adapternek a kódja név szerint állít be (minden munkamenet `stats`-ja a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

Kapcsos zárójelben lévő kulcsot futás közben egészítünk ki (`score.{team}` csapatonként egy kulcs). A kódnak a játék mezőinek táblázatából vagy a játék saját statisztikanevéből származó kulcsai nincsenek ebben a listában; a fenti "Mit rögzít" részben vannak megnevezve.

## Teljesség {#completeness}

A watcher követi a 3DHeat [átalakítási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassuk vagy megtartjuk, soha nem dobjuk el. A sorokon kívül minden csomagot, oldalt, sort vagy választ, amelyet az adapter kap, egészben megőrzünk a munkamenet `heat.raw.parquet` fájljában (oszlopok: `time`, `ms`, `type`, `used`, `payload`, `text`, és minden név szerint megtartott mező; a `used` jelöli, ami sorrá is lett), a `meta.json` `selfCheck.completeness` része pedig típusonként számolja – a `lost` értéke 0.

**Beolvasva**

- minden bejegyzés egyszer, sorként az idejénél: a típusa, minden egyszerű mező (title, description, icon, priority, duration, possible_clip, az eredmény neve, mode, ...), a fázis címkéi csoportonként, az eredmény megjelenítendő neve a statisztikasémából; a fájl kezdete és vége

**Nyersen megőrizve**

- minden bejegyzés egészben, JSON-ként, a Steam saját `type`-ja alatt (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, bármely más): a beágyazott mezők – egy címke ikonja és prioritása, és bármi, amit egy későbbi Steam hozzáad – csak itt vannak meg
- `timeline`: a fájl saját mezői (daterecorded, starttime, endtime, minden más), amikor a munkamenet megnyílik, és amikor megváltoznak

**Nem elérhető**

- maga a felvétel (videó): a Steam a saját mappáiban tartja; a munkamenet név szerint hivatkozik az idővonal-fájlra
- olyan fájl olvasása, amelyet a Steam ír, és amely a vége lezárásával sem értelmezhető: számolva (`bad` az adapter állapotában), és a következő változáskor újra olvassuk, ahol a bejegyzései beolvasásra kerülnek

**Méret**: játékban töltött óránként néhány száz, 100-300 bájtos bejegyzés: óránként jóval 1 MB alatt

## Ellenőrizve {#verified}

helyi telepítés valódi idővonal-fájlain tesztelve: eredmény, játékmód, hiba, valamint a játékok saját esemény-, állapotleírás- és fázisbejegyzései; a fájlformátum maga nincs dokumentálva

## Forrás {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- A heat3d_watch adapterből készült a tools/gen_game_pages.py által; az adaptert módosítsd, és futtasd újra, ne ezt az oldalt szerkeszd. -->
