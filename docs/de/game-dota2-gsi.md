---
title: "Dota 2 (Spielstand)"
nav_order: 13
lang: de
source: game-dota2-gsi.md
source_hash: "100a0d704bbe"
nav_exclude: true
search_exclude: true
---
# Dota 2 (Spielstand) {#dota-2-game-state}

Während du Dota 2 spielst, speichert der Watcher, was das Spiel an Programme auf deinem eigenen Computer meldet, damit du es dir später auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `dota2-gsi`, Art [`gsi`](sources-and-rules.md); er läuft, solange `dota2.exe` läuft, und sucht alle 0,05 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- Position der eigenen Heldin bzw. des eigenen Helden (Welt-X/Y, Dota-Einheiten; keine Höhe), solange er lebt
- Spawn, Tode (mit Wiederbelebungszeit) und Wiederbelebungen des eigenen Helden
- Kills, aus dem wachsenden Killzähler
- zerstörte Gebäude, Roshan, Spielereignisse (roshan_killed, aegis_picked_up, ...), Spielzustände, Ergebnis
- Kills, Tode, Assists, letzte Treffer, Denies, Gold, GPM, XPM, Stufe, Held

## Woher es kommt {#where-it-comes-from}

Game State Integration: HTTP-POSTs an 127.0.0.1:3312, eingestellt in &lt;Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg

## So schaltest du es ein {#how-to-switch-it-on}

`python -m heat3d_watch setup dota2-gsi --apply`, dann Dota 2 starten (es liest die Datei beim Start)

Gib den Befehl in einem Terminal ein, das im Ordner des Watchers geöffnet ist (siehe [Vor dem Start](before-you-start.md)). Wenn er fehlschlägt, sagt die letzte Zeile, warum; [Installation und Start](installing-and-running.md) beschreibt die üblichen Ursachen.

`python -m heat3d_watch setup dota2-gsi` listet die Dateien auf, die er ändern würde; `python -m heat3d_watch setup dota2-gsi --apply` ändert sie und hebt das Original als `<file>.heat3d-backup` auf (siehe [Befehle](commands.md#setup)). Er gibt für jede Änderung `dota2-gsi: changed: ...` aus oder `dota2-gsi: nothing to change`, wenn er schon eingeschaltet ist.

Einstellungen über Umgebungsvariablen:

- `HEAT3D_DOTA_GSI_PORT`: der Port, an den das Spiel sendet (Standard 3312); die cfg-Datei des Spiels muss denselben Port nennen

## Wie es funktioniert {#how-it-works}

Valve Game State Integration: Counter-Strike 2 und Dota 2 melden einem lokalen Webserver, was passiert.

Beide Spiele lesen beim Start jede `gamestate_integration_*.cfg` in ihrem cfg-Ordner und schicken danach bei jeder Änderung des Zustands ein JSON-Dokument per POST an die `uri` jeder Datei (höchstens alle `throttle` Sekunden und alle `heartbeat` Sekunden, wenn sich nichts ändert). Der Watcher ist dieser Webserver: Er hört nur auf 127.0.0.1, antwortet auf jeden POST sofort mit 200 und erledigt die Arbeit in seinem eigenen Abfrage-Thread.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

Was ein Spieler gesendet bekommt - und damit was aufgezeichnet werden kann - entscheidet das Spiel, das einem Spieler zeigen darf:

- CS2: `provider` (die eigene steamid), `map` (Name, Modus, Phase warmup/live/intermission/gameover, Runde, Punktestand team_ct/team_t), `round` (Phase freezetime/live/over, Bombe planted/exploded/defused, win_team), `player` (der Spieler, der *beobachtet* wird: man selbst, solange man lebt, nach dem Tod ein Teamkamerad) mit `state` (Leben, Rüstung, Geld, round_kills, round_killhs, round_totaldmg), `match_stats` (Kills, Assists, Tode, MVPs, Punktestand), `position` und `forward` als Zeichenketten "x, y, z" in Welteinheiten (Zoll, Z nach oben), `weapons`; `bomb` nur für Zuschauer. Positionen anderer Spieler (`allplayers_*`) werden nur an Zuschauer und GOTV gesendet, deshalb werden sie nicht angefragt.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player` (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero` (xpos/ypos in Welteinheiten, level, alive, respawn_seconds), `buildings` (Leben pro Turm, Kaserne, Ancient), `roshan`, `events` (roshan_killed, aegis_picked_up, ...). Es gibt keine Höhe: z ist 0. Außerdem angefragt und ganz behalten: `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`, `neutralitems`, `league` (das Spiel sendet, was der eigene Client des Spielers hat; welche davon beim Spielen statt beim Zuschauen etwas enthalten, ist ungetestet).

Jedes Dokument wird außerdem vollständig behalten (Konverterregel von 3DHeat, docs/converters.md im Repository des Viewers): `heat.raw.parquet`, `type` "gsi", `text` das JSON, wie gesendet - nur das Token der cfg-Datei ist geschwärzt, denn es ist das eigene Geheimnis des Watchers, keine Spieldaten. Dokumente, die gesendet werden, während kein Match offen ist (Menüs, Laden, zwischen den Matches), warten in einem `Backlog` und gehen in die Session des nächsten Matches, vor dessen Start; was übrig bleibt, wenn das Spiel schließt, bekommt eine eigene Session, die nur diese enthält. Nicht lesbare Posts und Posts mit falschem Token werden ebenfalls behalten ("gsi-unreadable", "gsi-bad-auth").

Quellen: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration> (das Format, das CS2 übernommen hat), <https://github.com/antonpup/CounterStrike2GSI> und <https://github.com/antonpup/Dota2GSI> (Feldlisten; MIT, nur für Fakten gelesen).

Dasselbe Modul bedient außerdem: [Counter-Strike 2 (Spielstand)](game-cs2-gsi.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | ja |
| Oben-Achse | `z` |
| Einheiten | Dota-Welteinheiten (z immer 0) |
| Für den Viewer gespiegelt | `y` |
| Einheitenfaktor (`scale`: der Viewer multipliziert Positionen damit) | 1 |

Diese landen in der `meta.json` jeder Session (`axes`) und, wenn die Session Positionen hat, im Footer von `heat.parquet`, damit der 3DHeat-Viewer die Zeilen selbst dreht und skaliert - siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt das als "erlaubt (liest nur, was das Spiel veröffentlicht)".
- Art `gsi`: Er liest nur, was das Spiel oder die Plattform herausgibt (eine Game-State-Integration oder lokale API, die das Spiel bereitstellt), deshalb zeichnet er auch im Online-Spiel auf wie offline; die Markierung entscheidet nur, ob Speicher jemals gelesen werden darf.
- Speicher: **nie** von diesem Adapter gelesen. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist - siehe [Quellen und Regeln](sources-and-rules.md).

## Erfasste Statistiken {#statistics-recorded}

Statistik-Schlüssel, die der Code dieses Adapters namentlich setzt (das `stats` jeder Session in `meta.json` und die Tabelle `stats` in `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `hero`, `level`, `result`, `roshan_kills_seen`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; "Was aufgezeichnet wird" oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder behalten, nie weggelassen. Neben den Zeilen wird jedes Paket, jede Seite, jede Zeile oder Antwort, die der Adapter erhält, vollständig in der `heat.raw.parquet` der Session behalten (Spalten `time`, `ms`, `type`, `used`, `payload`, `text`, dann jedes nach Namen behaltene Feld; `used` markiert, was auch zu Zeilen wurde), und `selfCheck.completeness` in der `meta.json` zählt jeden `type` - `lost` ist 0.

**Gelesen**

- Position (x/y) der eigenen Heldin bzw. des eigenen Helden, lebend, Stufe, Leben, maximales Leben, Mana, maximales Mana; Spawn, Tode mit Wiederbelebungszeit, Wiederbelebungen
- Kills (der Killzähler steigt); Kills, Tode, Assists, letzte Treffer, Denies, Gold, GPM, XPM, Nettowert, Stufe und Held als Statistiken
- zerstörte Gebäude, Roshan unten und wieder da, jeder Eintrag von `events` einmal, Spielzustände, der Gewinner

**Roh behalten**

- `gsi`: jedes Dokument, das das Spiel sendet, vollständig, wie gesendet (`text`); `used` ist wahr, wenn es in einem Match gelesen wurde - alle fünfzehn Komponenten, die die cfg-Datei anfragt: provider, map (Tag/Nacht, pausiert, Ward-Abklingzeiten, Punktestände), player (verlässliches und unverlässliches Gold, Serien, Killliste, ausgegebene Befehle, ...), hero (Buffs, Talente, Aghanim's, Attribute), abilities, items, buildings, roshan, events, draft, wearables, minimap, couriers, neutralitems, league und das eigene `previously`/`added`-Diff des Spiels
- Dokumente aus Menüs, Ladebildschirm und zwischen den Matches: genauso behalten, zu ihrer eigenen Zeit vor dem Start des nächsten Matches; nach dem letzten Match in einer eigenen Session (`raw_only` in meta.json)
- `gsi-unreadable`: ein Post, der kein JSON-Objekt ist, mit seinen Bytes als `payload` und `length`
- `gsi-bad-auth`: ein Post mit einem anderen Token als dem der cfg-Datei

**Nicht verfügbar**

- Höhe: das Spiel sendet nur x und y
- die anderen Helden während des Spielens: das Spiel sendet den eigenen Helden, und jeden Spieler nur an Zuschauer (dann roh behalten, nicht gezeichnet); mehrere Komponenten (draft, minimap, couriers) enthalten nur, was der eigene Client des Spielers hat - was beim Spielen ungetestet ist
- Zustände zwischen den Posts: höchstens einer alle 0,1 s (`throttle`), alle 10 s, wenn sich nichts ändert
- das Token der cfg-Datei, in jedem behaltenen Dokument geschwärzt: das eigene Geheimnis des Watchers, keine Spieldaten
- Posts über 10.000 Wartende (der Watcher war hängen geblieben) werden als `dropped_packets` gezählt, nicht behalten; ein Post über 4 MB wird als `gsi-unreadable` mit seiner Länge, aber ohne seine Bytes behalten

**Größe**: mit allen Komponenten ist das Dokument eines Spielers etwa 5-15 KB groß und wird bis zu 10 Mal pro Sekunde gepostet (die Uhr ändert sich bei jedem Post): etwa 100-500 MB pro Stunde in `raw.bin`, während das Match läuft, etwa ein Zehntel davon in der zstd-komprimierten `heat.raw.parquet`; das eines Zuschauers, mit jedem Spieler und der Minimap, ein Mehrfaches davon (aus dem veröffentlichten Format geschätzt, nicht am Spiel gemessen)

## Geprüft {#verified}

mit Dokumenten im veröffentlichten GSI-Format getestet, an den laufenden Adapter gesendet; am laufenden Spiel ungetestet

## Quelle {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
