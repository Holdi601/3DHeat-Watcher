---
title: "Data"
nav_order: 5
lang: "cs"
source: the-data.md
source_hash: "6150cdc022fc"
nav_exclude: true
search_exclude: true
---
# Data {#the-data}

Všechny záznamy jsou prosté soubory v datové složce (`%LOCALAPPDATA%\3DHeat\Watcher`, pokud se nezmění, viz [Instalace a spuštění](installing-and-running.md#where-everything-is)). Můžete je číst, kopírovat nebo mazat bez Watcheru. Soubor `.jsonl` je prostý text, jeden záznam události na řádek (otevře ho Poznámkový blok); soubor `.parquet` je tabulka, kterou otevírá prohlížeč 3DHeat (Excel ne – `stats --csv` zapisuje soubory CSV pro tabulky).

## Složky záznamů {#session-folders}
![složka záznamu](../assets/img/session-folder.svg)


**Záznam** je jedna relace s jedním zdrojem: od chvíle, kdy hra poprvé něco řekne, do chvíle, kdy přestane (hra se zavře, zápas skončí, jízda nebo let se resetuje – stránka každého adaptéru říká, co záznamy začíná a končí). Každý záznam dostane složku:

```text
<data>\sessions\<game>\<YYYY-MM-DD_HH-MM-SS>_<adapter id>\
    events.jsonl
    heat.parquet
    meta.json
```

- `<game>` je název hry, kde každý znak jiný než písmena, číslice, `.`, `_` a `-` je nahrazen za `-` (nejvýš 60 znaků): `EA-SPORTS-F1-25`, `Counter-Strike-2`. Adaptéry, které pokrývají mnoho her (statistiky Steamu, Steam Timeline, zvýraznění NVIDIA), řadí každý záznam pod hru, ke které patří.
- Čas je začátek záznamu v místním čase. Záznamy popisující minulost (replay převedený po zápase, soubor statistik Steamu) používají čas, který uvede hra nebo soubor. Dva záznamy začínající ve stejné sekundě dostanou za název `_2`, `_3`, ...
- Id záznamu v databázi statistik je `<game folder>/<session folder>`.

Záznam, ve kterém se vůbec nic nezaznamenalo (hra seděla v menu, nebo spadla při startu), se při uzavření smaže, aby každé spuštění nezanechalo prázdnou složku.

Některé záznamy obsahují další soubory. Záznam dema Counter-Strike 2 obsahuje vlastní tabulku a souhrn převodníku (`<map>/<match>.parquet`, `<match>.match.json`). Záznam iRacingu uvádí jako události `telemetry_file` soubory `.ibt`, které simulátor během relace zapsal.

## events.jsonl {#eventsjsonl}

`events.jsonl` má jeden objekt JSON na řádek, jeden řádek na událost, zapsaný ve chvíli, kdy se událost stane. Soubor se zapisuje po řádcích, takže pád, výpadek proudu nebo ukončený proces neztratí nic, co už bylo zapsáno; řádek přerušený pádem se při čtení souboru přeskočí a každý řádek před ním platí.

Každý řádek má stejné základní sloupce:

| Sloupec | Typ | Co je to |
|---|---|---|
| `time` | číslo | sekundy od začátku záznamu (4 desetinná místa), nebo herní hodiny, pokud je adaptér předá |
| `ms` | celé číslo | čas podle hodin, Unixové milisekundy |
| `event` | text | co se stalo: `position`, `spawn`, `death`, `kill`, `lap`, `teleport`, `session_start`, ... |
| `x`, `y`, `z` | číslo | kde, v jednotkách a osách hry (viz `axes` v `meta.json`); je přítomno jen tehdy, když jsou všechny tři známé a konečné |
| `player` | text | kdo: jméno, id, nebo `me` pro hráče (viz [Vlastní řádky hráče](#the-players-own-rows)) |
| `team` | text | jeho strana, když ji hra uvádí |
| `session` | text | zápas, kolo, etapa, život nebo let, ke kterému řádek patří, když to hra uvádí |

Každé další pole, které hra nahlásí, následuje pod svým vlastním názvem (`speed_kmh`, `gear`, `lap_time`, `weapon`, `victim`, `hero`, ...). Pole bez hodnoty se vynechají, stejně jako čísla, která nejsou konečná. Dva syntetické řádky:

```json
{"time":12.3456,"ms":1777660501123,"event":"position","x":-412.5,"y":12.1,"z":233.0,"player":"me","session":"1","speed_kmh":187.4,"gear":5}
{"time":15.0,"ms":1777660503667,"event":"lap","x":-380.2,"y":12.0,"z":250.9,"player":"me","session":"1","lap_time":92.418,"lap":3}
```

Řádky bez pozice (řádek z killfeedu, zvýšení úrovně, změna statistiky) zůstávají v `events.jsonl` a počítají se do statistik. Do tabulky jdou jen řádky s pozicí.

### Vlastní řádky hráče {#the-players-own-rows}

Které řádky patří hráči, říká zdroj; nikdy se to neodhaduje. Řádek je hráčův vlastní, když

- jeho `player` je `me`: většina adaptérů, jejichž zdrojem je vlastní hra hráče (telemetrie vlastního auta nebo letadla, integrace stavu hry, deník);
- nese `own_car` 1: závodní hry, které zaznamenávají každé auto pod jménem jeho jezdce (EA SPORTS F1 podle indexu hráčova auta ve hře, RaceRoom podle jeho vlastního místa, Automobilista 2 a Project CARS 2 podle sledovaného účastníka) označí auto hráče tímto způsobem a jméno jezdce drží v `player`;
- jeho `player` je `player` záznamu v `meta.json`: jméno, které zdroj dává hráči – velitel z Elite Dangerous (deník je vždy hráčův), nebo řádek League of Legends replay s Riot ID z nastavení.

War Thunder a Rocket League jmenují každého hráče a neříkají, který jste vy; s vaším jménem v nastavení `player_names` (viz [Nastavení](installing-and-running.md#settings)) se vaše řádky stanou `me`. [Zvýraznění NVIDIA](nvidia-highlights.md) hledá okamžik přesně v těchto řádcích.

## heat.parquet {#heatparquet}

Když se záznam uzavře, řádky z `events.jsonl`, které mají `x`, `y` a `z`, se zapíšou do `heat.parquet`. To je tabulka, kterou otevírá prohlížeč 3DHeat. Pokud záznam nemá pozice, tabulka se nezapíše.

- Sloupce jsou `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session`, a za nimi každé další pole v pořadí, v jakém se poprvé objeví.
- `x`, `y`, `z` a `time` jsou 64bitová čísla s plovoucí desetinnou čárkou a `ms` je 64bitové celé číslo. Další sloupec, jehož hodnoty jsou všechna čísla, je 64bitové číslo s plovoucí desetinnou čárkou; každý jiný sloupec je text kódovaný slovníkem (chybějící hodnoty jsou prázdný text a seznamy nebo objekty se zapisují jako text JSON).
- Metadata souboru mají klíč `heat3d` s pokyny pro čtení, takže prohlížeč si sloupce a osy namapuje sám (příklad, se zkráceným seznamem `extra`):

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

`up` je svislá osa hry; `flipX`/`flipY`/`flipZ` zrcadlí osu, aby levotočivý svět nebyl vykreslen zrcadlově; `scale` je měřítko jednotek prohlížeče: prohlížeč při načtení tabulky vynásobí každou pozici tímto číslem (0.01 přemění centimetry na metry). Každý adaptér zapisuje 1 a zachovává vlastní jednotky hry – metry u většiny, jednotky Source (palce) u Counter-Strike 2, jednotky Unreal (centimetry) u Rocket League – protože úroveň exportovaná ze hry je v těchto stejných jednotkách, takže řádky na ni sednou; tabulky převodníku CS2 říkají totéž. `units` v `meta.json` říká, co je jedna jednotka. Stránka každé hry uvádí své hodnoty v části „Positions and axes“.

Létající simulátory (DCS World, Microsoft Flight Simulator, X-Plane, záznamy Tacview z IL-2) kladou své řádky na Zemi a jejich patička říká kde, takže prohlížeč může pod ně položit skutečný svět:

```json
"geo": {"lat0": 42.0, "lon0": 42.0, "projection": "tangent-plane", "east": "x", "north": "z", "up": "y"}
```

`lat0`/`lon0` (stupně) jsou počátek ploché mapy, ve které jsou řádky; `east`, `north` a `up` pojmenují sloupce obsahující metry na východ a na sever od něj a nadmořskou výšku. Počátek je u X-Plane a MSFS první poloha, u IL-2 referenční bod záznamu a u DCS pevný počátek bojiště (první poloha zaokrouhlená na celé stupně na bojiště, které Watcher nezná). Tabulka bez místa na Zemi nemá klíč `geo` a vše ostatní v patičce je stejné v obou případech.

`heat.parquet` lze vždy znovu sestavit z `events.jsonl` příkazem `python -m heat3d_watch table <session folder>` (viz [Příkazy](commands.md#table)). To se hodí, když při nahrávání záznamu chyběl `pyarrow`.

## meta.json {#metajson}

`meta.json` shrnuje záznam. Zapisuje se při otevření záznamu, nejvýš každých 30 sekund, když přicházejí události nebo statistiky, a při uzavření. Statistiky se drží jen v paměti mezi těmito zápisy, takže pád může ztratit nejvýš poslední půl minuty z nich.

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

Záznam, jehož zdroj jmenuje hráče (viz [Vlastní řádky hráče](#the-players-own-rows)), má také `"player"`: jméno, které nesou vlastní řádky hráče. Záznam na Zemi (létající simulátory) má také `"geo": {"lat0": .., "lon0": ..}`, jehož počátek opakuje `geo` v patičce tabulky.

- `started` / `ended`: místní čas na sekundu; `ended` je `null`, dokud záznam běží.
- `events`: kolikrát se každá událost stala, nejčastější první. `positions` je počet řádků s pozicí.
- `stats`: čísla záznamu. Adaptér každé nastaví, přičte k němu, nebo drží maximum či minimum.
- Cokoli dalšího, co adaptér o relace ví, je na nejvyšší úrovni: trať, mapa, mise, id zápasu, id aplikace Steam, soubor replaye, profil paměti a jeho verze. Záznam dokončený obnovou má `"recovered": true`.

## watcher.sqlite {#watchersqlite}

`watcher.sqlite` je databáze statistik. Řádek se přidá pro každý záznam, když se uzavře. Tři tabulky jsou prosté, takže je může číst jakýkoli nástroj SQL, notebook nebo tabulkový procesor bez Watcheru:

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
CREATE TABLE stats (            -- per session, every number the game reported or the Watcher counted
  session TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  key TEXT NOT NULL,
  value REAL,                   -- numbers
  text TEXT,                    -- everything else (a map name, a result, a hero)
  PRIMARY KEY (session, key)
);
```

Opětovné zaznamenání záznamu (obnova, znovu převedený replay) nahradí jeho řádky. `multiplayer` je příznak adaptéru (některé adaptéry ho nastavují pro každý záznam zvlášť, například DCS z mise), nikoli kontrola, zda jste byli online. Hodnota ano/ne v `stats` se ukládá jako text.

Příklad dotazu, nejlepší kolo podle hry přes všechny záznamy (nižší je lepší):

```sql
SELECT s.game, MIN(t.value) AS best_lap
FROM stats t JOIN sessions s ON s.id = t.session
WHERE t.key = 'best_lap'
GROUP BY s.game;
```

`python -m heat3d_watch stats` vypisuje součty z těchto tabulek (viz [Příkazy](commands.md#stats)); jeho sloupec `best` je nejnižší hodnota u časů uložených jako nejlepší a u umístění, nejvyšší u všeho ostatního.

## Obnova po pádu {#recovery-after-a-crash}

Když se `run` spustí, hledá záznamy, které předchozí Watcher nechal otevřené: `meta.json` bez `ended` a `events.jsonl` s alespoň jedním řádkem. Každý z nich dokončí:

- počty událostí a počet pozic se přepočítají z `events.jsonl`, přeskočí se řádek přerušený pádem;
- konec je čas podle hodin na posledním řádku (`ms`);
- statistiky jsou ty z posledního zápisu `meta.json` (nejvýš půl minuty staré);
- přidá se `"recovered": true`, zapíše se `heat.parquet` a záznam se dostane do `watcher.sqlite`.

Log hlásí „finished N session(s) left open by an earlier run“. Zamykací soubor brání tomu, aby jeden Watcher „obnovoval“ záznamy druhého, který ještě běží.

## Export do CSV {#csv-export}
![stats --csv a table](../assets/img/csv-and-table.svg)


```bash
python -m heat3d_watch stats --csv out
```

zapíše `out\sessions.csv`, `out\events.csv` a `out\stats.csv`. Každý soubor je jedna tabulka z `watcher.sqlite`, úplná, s řádkem záhlaví, v UTF-8. Časy jsou Unixové sekundy jako v databázi. `--game` export nezužuje; zapíšou se všechny záznamy.

## Otevření záznamu v prohlížeči 3DHeat {#opening-a-session-in-the-3dheat-viewer}

Prohlížeč: [github.com/Holdi601/3DHeat](https://github.com/Holdi601/3DHeat), dokumentace [holdi601.github.io/3DHeat](https://holdi601.github.io/3DHeat/) – jeho stránka [kontejneru `.3dheat`](https://holdi601.github.io/3DHeat/container.html) popisuje formát jednoho souboru na zápas, který mohou zapisovat převodníky replayů.

Otevřete `heat.parquet` záznamu v prohlížeči 3DHeat. Patička mu říká, který sloupec je pozice, čas, hráč, tým a relace a kterým směrem je nahoru, takže nic není nutné mapovat ručně. Pozice jsou ve světových souřadnicích hry. Když se vykreslí nad úrovní exportovanou jinými nástroji 3DHeat (například z [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles)), dopadnou tam, kde se staly.

- **Teplotní mapy** používají každý řádek s pozicí, filtrovaný podle `event`, `player`, `team` nebo `session` jako kterýkoli jiný sloupec.
- **Teplo z čar** (režim „Čáry“) kreslí čáru od každého řádku hráče k jeho dalšímu, a při přehrávání je každý hráč bodem pohybujícím se po trase s ocasem za sebou. Panel **Trasy** v prohlížeči podle sloupce `event` vybírá, které události trasu **začínají** a které ji **ukončují**. Watcher zapisuje ohraničující události jako řádky s pozicí, takže je lze tam vybrat:
  - začátky: `spawn`, `respawn`, `session_start`. Začátek uzavře trasu, která byla otevřená, aniž by kreslil čáru na nové místo.
  - konce: `death`, `finish`, `session_end` a `teleport`. Čára vede až k samotnému koncovému řádku, tam, kde hráč zemřel, zastavil se, nebo byl odvezen.

  Skok – místo dosažené bez cestování tam – jsou dva řádky: `teleport` na místě, které hráč **opustil**, a začátek na místě, kam **dorazil**, hned po něm. Závodní adaptéry zapisují skok, kdykoli auto ujelo víc, než mohlo ujet (přetočení nebo návrat na kontrolní bod, reset na silnici, návrat do boxů, rychlý přesun), se `spawn` na místě příjezdu (`respawn` u resetu BeamNG); řádek `teleport` nese příjezd jako `to_x`, `to_y`, `to_z` a vzdálenost jako `metres`, řádek začátku `after: "teleport"`. Nákladní adaptéry dělají totéž u trajektu, vlaku nebo načtené uložené hry, letové adaptéry u skoku, který žádné letadlo neuletí. Takže při `teleport` mezi konci a `spawn` mezi začátky – což prohlížeč sám navrhuje – trasa skončí tam, kde skok opustil, a další začíná tam, kde skok dorazil, a žádná čára nepřechází přes mapu. Trasa nikdy nepřekročí změnu sloupce `session`. Řádek pozice se zapisuje několikrát za sekundu (u většiny telemetrie 10 Hz), což dává plynulou čáru.
- Sloupec `session` rozděluje relaci na kola, etapy, životy nebo tělesa (Elite Dangerous takto drží řádky galaxie a řádky povrchu každé planety odděleně). Vyberte jedno v prohlížeči a podívejte se jen na tu část.

To, co prohlížeč s řádky dělá – filtry, barvy, přehrávání – popisuje dokumentace samotného prohlížeče. Záznamy dema Counter-Strike 2 se otevírají přes `<map>/<match>.parquet` a `<match>.match.json` převodníku v záložkách prohlížeče **Teplotní mapa** a **Zápas**. Pozice iRacingu pocházejí z souborů `.ibt` uvedených v záznamu, které prohlížeč čte sám.
