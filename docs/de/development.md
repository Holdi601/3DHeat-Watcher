---
title: "Entwicklung"
nav_order: 12
lang: de
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Entwicklung {#development}

Diese Seite ist für das Hinzufügen eines Spiels gedacht: wie ein Adapter gebaut wird, wie er geprüft wird und
wie seine Dokumentation entsteht.

## Das Repository {#the-repository}

| Pfad | Was er enthält |
|---|---|
| `heat3d_watch/cli.py` | die Befehle ([Befehle](commands.md)) |
| `heat3d_watch/watcher.py` | die Hintergrundschleife: Prozessliste, ein Thread je Adapter, Updates |
| `heat3d_watch/session.py` | eine Aufnahme: `events.jsonl`, `heat.parquet`, `meta.json`, Wiederherstellung |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | die Einstellungen und der Datenordner |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | die Speicherprüfungen und der nur lesende Leser ([Speicher lesen](memory-reading.md)) |
| `heat3d_watch/notify.py` | Windows-Benachrichtigungen |
| `heat3d_watch/adapters/` | ein Modul je Spiel oder Spielfamilie; Module, die mit `_` beginnen, sind gemeinsame Helfer |
| `heat3d_watch/decoders/` | die Decoder für Renn-Telemetrie, kopiert aus den Rundenrekordern von 3DHeat GameCapture |
| `heat3d_update/` | der Updater ([Updates](updates.md)) |
| `mods/beamng/heat3d/` | der BeamNG-Protokoll-Mod, den `setup beamng` installiert |
| `tests/` | die Tests |
| `tools/gen_game_pages.py` | schreibt die Spielseiten dieser Dokumentation |

## Ein Adapter {#an-adapter}

Ein Adapter ist eine Dataclass, die von `heat3d_watch.adapters.base.Adapter` abgeleitet ist. Ihre Felder sagen,
was er ist; seine Methoden erledigen die Arbeit.

| Feld | Standard | Was es ist |
|---|---|---|
| `id` | `""` | kurz und stabil: Sitzungsordner, `disabled`, `replay_folders` und `player_names` beziehen sich darauf |
| `game` | `""` | der Name des Spiels, so wie Menschen ihn schreiben; Sitzungen werden unter ihm abgelegt |
| `kind` | `"telemetry"` | eines von `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Quellen und Regeln](sources-and-rules.md)) |
| `exes` | `()` | Namen der Programmdateien (egal welche Schreibweise), die bedeuten, dass das Spiel läuft. Leer: Der Adapter ist immer aktiv (`always` ist wahr) |
| `multiplayer` | `True` | das Spiel wird online gespielt: sein Speicher wird nie gelesen |
| `source` | `""` | woher die Zahlen kommen, einmal gesagt |
| `records` | `()` | was aufgezeichnet wird, ein Eintrag je Art von Ding |
| `enable` | `""` | wie die Quelle eingeschaltet wird; leer, wenn nichts nötig ist |
| `interval` | `0.1` | Sekunden zwischen den Abfragen |
| `axes` | `Axes()` | die Hochachse der Welt, gespiegelte Achsen, der Maßstab der Einheiten für den Viewer (bei 1 belassen) und eine Notiz zu den Einheiten |
| `verified` | `""` | was geprüft wurde, ehrlich gesagt (siehe unten) |
| `completeness` | `{}` | die Darstellung der Quelle nach der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: `read` (was zu Zeilen wird), `raw` (was ganz aufbewahrt wird, unter welchem `type`), `missing` (was die Quelle nicht liefert, und warum), `size` (wie groß der rohe Strom in einer Stunde wird). Der Abschnitt „Completeness“ der Spielseite wird daraus geschrieben |

`source`, `records`, `enable`, `verified` und `completeness` sind Dokumentation, keine Zierde. `games` gibt sie
aus, `games --markdown` erzeugt die Tabelle in [Alle Spiele in einer Tabelle](watcher.md), und die Spielseiten
werden aus ihnen erzeugt. Schreib sie so, dass sie genau sagen, was der Code tut.

Die Methoden, alle optional:

| Methode | Aufgerufen | Was sie tun soll |
|---|---|---|
| `missing(self) -> str \| None` | von `games`, `status` und vor dem Start | sagen, warum der Adapter hier nicht laufen kann (eine DLL nicht gefunden, ein Ordner fehlt), oder `None` |
| `setup(self, ctx, *, apply) -> list[str]` | von `setup` | die eigene Ausgabe des Spiels einschalten; eine Zeile je Änderung zurückgeben, und Dateien nur ändern, wenn `apply` wahr ist. Eine Datei als `<file>.heat3d-backup` sichern, bevor sie zum ersten Mal geändert wird, und diese Sicherung nie überschreiben. Nur überschreiben, wenn es etwas zum Einschalten gibt: `can_setup` (wahr, wenn `setup` überschrieben ist) entscheidet, ob `setup` es ausführt oder sagt, dass es nichts zu ändern gibt; eine Klasse, die mehrere Spiele bedient, überschreibt `can_setup` für die, die sie nicht einrichten kann (`RallyAdapter` für Richard Burns Rally). |
| `start(self, ctx)` | wenn der Prozess des Spiels erscheint (immer aktive Adapter: wenn `run` startet) | Sockets öffnen, Dateien finden, sich merken, wo man beginnt |
| `poll(self, ctx)` | alle `interval` Sekunden, im eigenen Thread des Adapters | nehmen, was das Spiel seit der letzten Abfrage gesagt hat, und es aufzeichnen |
| `stop(self, ctx)` | wenn das Spiel weg ist oder der Watcher stoppt | Sitzungen und Sockets schließen |

Jeder Adapter läuft in seinem eigenen Thread (`Runner`). Eine Ausnahme in `poll` wird protokolliert, und der
Adapter wartet `min(5, interval × 10 + 0.5)` Sekunden bis zur nächsten Abfrage. Nach 20 Fehlern hintereinander
oder einem Fehler in `start` wird der Adapter gestoppt und erst wieder gestartet, wenn sich die Prozess-ID des
Spiels ändert. `missing()` wird bei jedem Scan geprüft, also halte es billig.

Ein Adapterobjekt wird wiederverwendet, wenn das Spiel erneut startet, daher muss `start` alles zurücksetzen,
was ein früherer Lauf hinterlassen hat.

### Anmelden {#registering-it}

Lege das Modul in `heat3d_watch/adapters/` ab und trage die Adapter am Ende des Moduls ein:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` importiert jedes Modul im Paket (außer `base` und Namen, die mit `_` beginnen) und sammelt
deren `ADAPTERS`. Zwei Adapter mit derselben ID stoppen das Laden mit einem `ValueError`. Ein Modul, das sich
nicht importieren lässt (eine fehlende Abhängigkeit), lässt seine Spiele weg und wird von `games` mit dem Fehler
genannt, so stört das Problem eines Spiels die anderen nicht.

## Context und Session {#context-and-session}

`start`, `poll`, `stop` und `setup` bekommen einen `Context`:

| Mitglied | Was es ist |
|---|---|
| `settings` | die `Settings` ([Installieren und Starten](installing-and-running.md#settings)) |
| `data` | der Datenordner |
| `pid`, `exe` | die Prozess-ID und der Pfad der Programmdatei des Spiels, wenn der Adapter für ein laufendes Spiel gestartet wurde; der Installationsordner liegt neben `exe` |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | eine neue `Session`. `game` überschreibt den Spielnamen des Adapters (für Adapter, die viele Spiele abdecken); `when` setzt den Beginn für Sitzungen, die die Vergangenheit beschreiben; `axes`, `source` und `multiplayer` nehmen die des Adapters als Standard; `meta` ist ein Wörterbuch, das in `meta.json` geschrieben wird; `geo` (`{"lat0": .., "lon0": ..}`, oder später `session.geo` setzen) setzt eine Flachkarten-Sitzung auf die Erde, in `meta.json` und in die Fußzeile der Tabelle |
| `close(session)` | beendet eine Sitzung: die Tabelle, `heat.raw.parquet`, `meta.json`, ihre Zeile in `watcher.sqlite`. Eine Sitzung ohne Ereignisse und ohne rohe Einträge wird gelöscht; eine mit nur rohen Einträgen bleibt erhalten (keine Tabelle, keine Zeile in der Datenbank). Nimmt `None` an. Gibt den Pfad der Tabelle oder `None` zurück. |

Eine `Session` nimmt auf:

| Mitglied | Was es tut |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | eine Zeile. `t` ist standardmäßig die Sekunden seit Beginn der Sitzung, `ms` die jetzige Zeit. Eine Position zählt nur, wenn `x`, `y` und `z` alle angegeben und endlich sind. `None`-Attribute werden weggelassen. |
| `position(x, y, z, **kw)` | ein Ereignis namens `position` |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | eine Sache behalten, die die Quelle gesendet hat, ganz: die Bytes eines Pakets oder einer Seite (`payload`), eine Zeile oder eine JSON-Antwort, so wie sie kam (`text`), oder die Werte eines Lesevorgangs nach Namen (`fields`, jeder als eigene Spalte). `type` ist das eigene Wort der Quelle dafür (eine Paket-ID, der Name einer Abbildung, ein Journal-Ereignis, ein Endpunkt); `used` sagt, dass es auch zu Zeilen wurde. Wird beim Aufruf sofort in `raw.bin` gerahmt, beim Schließen oder Wiederherstellen der Sitzung als `heat.raw.parquet` (zstd) geschrieben und je `type` in `meta.json` unter `selfCheck.completeness` gezählt |
| `stat(key, value, how="set")` | eine Statistik: `set` setzt sie, `add` addiert dazu, `max` oder `min` behält den höchsten bzw. niedrigsten Wert |
| `now()` | Sekunden seit Beginn der Sitzung |
| `meta` | ein Wörterbuch, das in `meta.json` geschrieben wird |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | wann, wo und was bisher aufgenommen wurde |

`event`, `stat` und `raw` sind threadsicher und können aus einem Worker-Thread aufgerufen werden.

**Jeder Adapter behält alles, was seine Quelle sendet.** Die Zeilen sind das, was der Viewer zeichnet; sie sind
nicht die Aufnahme. Jedes Paket, das an einem Port ankommt, jede gelesene Speicherseite (die ganze Abbildung,
jedes Mal, wenn sie sich ändert), jede Zeile eines Logs oder Export-Skripts (auch die, die der Adapter
ignoriert), jede JSON-Antwort oder jedes gesendete Dokument geht bei Ankunft an `session.raw(...)` – ob es zu
einer Zeile wird oder nicht – und nichts wird unter die Rate gedrosselt, mit der der Adapter liest. Ein Eintrag,
der ankommt, bevor eine Sitzung offen ist, öffnet eine (eine Sitzung mit nur rohen Einträgen bleibt erhalten),
oder wird gehalten, bis eine offen ist; er geht nie verloren. Felder, die billig zu dekodieren und sicher in
ihrer Bedeutung sind, kommen zusätzlich in die Zeilen. Das ist die
[Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Ein Live-Strom ist
in dem Moment verloren, in dem er gesendet wird, also ist, was ein Adapter nicht behält, endgültig weg, und was
er ganz behält, kann dekodiert werden, an dem Tag, an dem jemand es versteht. Die Größe ist der Preis; zstd und
Wörterbuch-Kodierung halten sie klein, indem nichts weggelassen wird. Der Test jedes Adapters sendet etwas, das
er nicht nutzt, und prüft, dass es unverändert aus `heat.raw.parquet` zurückkommt und dass
`selfCheck.completeness.lost` 0 ist. `racing.Driving.raw` tut dasselbe für die Renn-Adapter (und öffnet die
Sitzung), und `racing.Pages` behält Speicherseiten, wann immer sich ihre Bytes ändern, und zählt die erneuten
Lesevorgänge, die nichts Neues fanden, in `meta.json` unter `unchanged_reads`.

Konventionen, auf die sich der Rest des Systems verlässt:

- **Die eigenen Zeilen des Spielers werden markiert, nach dem, was die Quelle sagt.** `player="me"`, wo die Quelle
  die des Spielers selbst ist; wo jeder Spieler unter einem Namen aufgezeichnet wird, `own_car=1` an den Zeilen
  des Autos des Spielers (nach dem Spielerindex des Spiels oder dem betrachteten Teilnehmer), oder der Name des
  Spielers als `session.meta["player"]` (sofort in `meta.json` geschrieben), wenn die Quelle den Spieler nennt.
  Nie raten: Wo die Quelle es nicht sagt, nimm den Namen aus einer Einstellung (`player_names`, `riot_id`) oder
  markiere nichts.
  [NVIDIA-Highlights](nvidia-highlights.md) übernehmen Positionen nur aus solchen Zeilen (`platform.own_row`).
  Andere Spieler werden über Name oder ID geführt.
- **Routen werden durch Ereignisse mit Positionen begrenzt**: `spawn`, `respawn` und `session_start` beginnen eine;
  `death`, `finish`, `session_end` und `teleport` beenden eine. Wann immer sich der Spieler bewegt hat, ohne zu
  reisen (ein Reset, ein Zurückspulen, eine Schnellreise, ein geladener Spielstand), schreibe `teleport` an den Ort,
  den er verlassen hat, und dann einen Start (`spawn`, oder `respawn` bei einem Reset, den das Spiel nennt) an den
  Ort, den er erreicht hat, damit die Linienheat des Viewers eine Route beendet und die nächste beginnt, statt
  quer über die Karte zu zeichnen. `Driving.jumped` macht das für Fahrzeuge.
- **Positionen bleiben in den eigenen Weltkoordinaten und Einheiten des Spiels**, beschrieben durch `axes`.
  Rechne sie nicht in ein anderes Koordinatensystem um, es sei denn, das Spiel gibt keinen brauchbaren Weltrahmen
  (die Flugsimulatoren legen Breite und Länge in eine flache Karte, `Tangent`, um den ersten Fix – DCS um den
  festen Ursprung seines Schauplatzes – und übergeben `geo=tangent.geo()` an `open`, damit die Fußzeile sagt, wo
  auf der Erde die Karte liegt). `axes.scale` ist der Maßstab der Einheiten für den Viewer – er multipliziert jede
  Position damit – und bleibt 1, damit die Zeilen zu einem Level passen, das aus demselben Spiel in denselben
  Einheiten exportiert wurde; nenne die Einheit in `axes.units`.
- **Statistik-Schlüssel** sind klein geschrieben mit Unterstrichen und tragen ihre Einheit, wo eine zutrifft
  (`distance_km`, `top_speed_kmh`, `max_altitude_m`, `duration_s`). Eine Zeit, die als Bestwert gehalten wird,
  beginnt mit `best_` (mit `min` behalten), eine Platzierung endet auf `_position`: `stats` zeigt davon den
  niedrigsten als Bestwert, und bei allen anderen Schlüsseln den höchsten (`db.lower_is_better`).

## Helfer {#helpers}

| Helfer | Modul | Wofür |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | das Verfolgen eines Logs, das das Spiel schreibt: geteilte Lesevorgänge, nur die Zeilen dieser Sitzung, neue und ersetzte Dateien, nur ganze Zeilen |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` mit `try_open(who)`, `receive()`, `close()` | `racing` | ein UDP-Telemetrie-Port auf 127.0.0.1, nur übernommen, wenn frei, an ein anderes Programm abgegeben, optional weitergeleitet |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` mit `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | Fahrzeug-Sitzungen: Positionen mit fester Rate, Strecke, Höchstgeschwindigkeit, Runden; bei einem Sprung `teleport` dort, wo das Auto war, und `spawn` dort, wo es jetzt ist (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | der benannte gemeinsame Speicher eines Spiels, nur lesend, nie angelegt |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | ein beobachteter Replay-Ordner: Dateien werden einmal umgewandelt, wenn sie nicht mehr wachsen, in einem Worker-Thread; beim ersten Blick wird nur notiert, was da ist, und `convert_existing(ctx, folder=None)` – der Befehl [`replays`](commands.md#replays) – wandelt jene auf Anfrage um |
| `load_state`, `save_state` | `platform` | sich merken, was ein immer aktiver Adapter gesehen hat, in `<data>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | Flugbuchhaltung (Starts, Landungen, Abstürze, Strecke) und die flache Karte um den ersten Fix (`Tangent.geo()` ist das `geo` der Sitzung) |
| `backup_once(path)` | `gsi`, `racing` | die Regel `<file>.heat3d-backup` |
| die Dateien von Steam | `_steam` | binäre und Textdateien im KeyValues-Format, der Steam-Ordner aus der Registry |

Ein minimaler Log-Adapter, als Beispiel (ein erfundenes Spiel):

```python
from dataclasses import dataclass, field
from pathlib import Path

from ..session import Axes, Session
from ._logfollow import Follower, game_started, newest
from .base import Adapter, Context


@dataclass
class ExampleAdapter(Adapter):
    _session: Session | None = field(default=None, repr=False)
    _follow: Follower | None = field(default=None, repr=False)

    def start(self, ctx: Context) -> None:
        log = (ctx.exe.parent if ctx.exe else Path(".")) / "logs" / "game.log"
        self._session = None
        self._follow = Follower(lambda: newest(p for p in [log] if p.exists()), game_started(ctx.pid))

    def poll(self, ctx: Context) -> None:
        for line in self._follow.lines() if self._follow else []:
            if line.startswith("DIED "):
                if self._session is None:
                    self._session = ctx.open(self)
                self._session.event("death", player="me")
                self._session.stat("deaths", 1, "add")

    def stop(self, ctx: Context) -> None:
        self.poll(ctx)
        ctx.close(self._session)
        self._session = None


ADAPTERS = [
    ExampleAdapter(
        id="example",
        game="Example Game",
        kind="log",
        exes=("ExampleGame.exe",),
        source=r"<install>\logs\game.log (followed)",
        records=("deaths",),
        interval=0.5,
        axes=Axes(units="no positions recorded"),
        verified="tested on synthetic log lines in the game's format; untested against the game",
    )
]
```

Öffne die Sitzung mit dem ersten Ereignis, das es wert ist, aufgezeichnet zu werden, nicht in `start`, damit ein
Spiel, das in seinen Menüs bleibt, nichts zurücklässt (eine leere Sitzung wird ohnehin gelöscht).

## Tests {#tests}

```bash
python -m pytest
```

`tests/conftest.py` gibt jedem Test einen Wegwerf-Datenordner (`HEAT3D_WATCH_HOME`) und schaltet
Update-Prüfungen und Benachrichtigungen ab (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). Ein Adaptertest baut die
Ausgabe des Spiels aus seinem veröffentlichten Format – Pakete aus der Spezifikation, Logzeilen im Format des
Spiels, Dateien im dokumentierten Aufbau – und steuert den Adapter direkt (gekürzt aus `tests/test_poe.py`;
`data` und `install` sind temporäre Ordner):

```python
from dataclasses import replace
from heat3d_watch.adapters import poe
from heat3d_watch.adapters.base import Context
from heat3d_watch.config import Settings
from heat3d_watch.session import read_rows

ctx = Context(Settings(data=str(data)), data, exe=install / "PathOfExileSteam.exe")
a = replace(poe.ADAPTERS[0])   # a fresh copy of the adapter
a.start(ctx); a.poll(ctx); a.stop(ctx)
[session] = list((data / "sessions").glob("*/*"))
rows = read_rows(session)      # then check the rows and meta.json's stats
```

Netzwerk-Adapter werden gegen einen gefälschten lokalen Server geprüft oder mit Paketen, die per UDP an den
Adapter gesendet werden. Tests, die gegen echte Spieldaten auf dem Rechner der Entwicklerin bzw. des
Entwicklers prüfen, sind mit `@pytest.mark.local` markiert und werden übersprungen, wo diese Daten fehlen. Diese
Daten gehen nie ins Repository. `test_core.py` enthält außerdem den Test, der fehlschlägt, wenn Code, der in
einen anderen Prozess schreiben könnte, im Paket auftaucht (`test_memory_reading_cannot_write`).

## Ein ehrliches `verified` {#an-honest-verified}

`verified` sagt, was geprüft wurde und wie, und was nicht. Es wird von `games` und auf jeder Spielseite
angezeigt, und Spieler verlassen sich darauf. Beispiele aus dem Code:

- „tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent
  over UDP; untested against the game“
- „tested on documents in the published GSI format posted to the running adapter; untested against the
  running game“
- „tested on real stats files and schemas from a local install; change detection tested on files built
  in the binary KeyValues format“

Schreib „untested against the game“, bis der Adapter das laufende Spiel aufgezeichnet hat. Nenne nur die
Methode und die Toleranz: nie eine Karte, eine Match-ID, einen Spielernamen, ein Datum, eine Korpusgröße oder
eine genaue Anzahl aus echten Dateien, und nie „this machine“ (die Leser kennen den Rechner nicht). Nenne die
Quelle jedes Offsets und Aufbaus, und sag, wo zwei Quellen verglichen wurden. Behaupte nie mehr, als getan
wurde. Ein Format, das geraten oder aus Community-Werkzeugen übernommen wurde, wird genau so benannt.

## Die Spielseiten {#the-game-pages}

Jede Seite unter [Spiele](games.md) wird aus den Adaptern erzeugt, daher passt sie immer zum Code. Nach dem
Hinzufügen oder Ändern eines Adapters erzeugst du sie aus dem Repository-Ordner neu:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(In PowerShell: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Mit `--check` wird nur verglichen:
Es wird nichts geschrieben, und es endet mit 1, wenn eine Seite veraltet ist (auch die Spieletabelle in
`docs/watcher.md`).

Das Skript:

- lädt die Adapter mit `heat3d_watch.adapters.load()` gegen einen leeren temporären Datenordner, damit kein
  Speicherprofil oder keine Einstellung auf deinem Rechner in die Seiten gerät. Speicher-Adapter werden
  weggelassen, da sie aus den eigenen Profilen der Spieler kommen;
- schreibt nichts, wenn ein Adaptermodul sich nicht importieren lässt (die Seiten würden diese Spiele verlieren);
- schreibt `docs/game-<adapter id>.md` für jeden Adapter und `docs/games.md` mit der Übersichtstabelle, und
  löscht die Seiten von Adaptern, die es nicht mehr gibt;
- übernimmt „What is recorded“, „Where it comes from“, „How to switch it on“, die Achsen, das Mehrspieler-Flag und
  „Verified“ aus den Feldern des Adapters;
- macht aus dem Docstring des Moduls „How it works“. Schreib Docstrings im einfachen Textstil, den die Module schon
  verwenden und den das Skript umwandelt: Absätze; Listen mit `*`, `-` oder `1.`; Aufbauten und Beispiele, die
  unter der Zeile eingerückt sind, die sie einleitet (sie werden zu Code-Abschnitten); ein Titel, der mit
  Bindestrichen unterstrichen ist, oder eine kurze Titelzeile, deren Text direkt darunter eingerückt steht (sie
  werden zu Überschriften);
- listet die Statistik-Schlüssel, die der Code des Adapters namentlich setzt – `.stat("key", ...)`, beide Seiten
  eines `if`-Ausdrucks und f-String-Muster wie `score.{team}` – in den Klassen des Adapters und in den Helfern, die
  sie nutzen. Schlüssel, die aus einer Variablen kommen (eine Tabelle der Felder des Spiels), werden nicht
  aufgeführt;
- entscheidet „Positions“ anhand von `axes.units` (eine Notiz, die mit „no“ oder „none“ beginnt, heißt keine
  Positionen) und anhand dessen, was sein Code schreibt.

Bearbeite die erzeugten Seiten nie von Hand: Ändere den Adapter und führe das Skript erneut aus. Die Tabelle
unter [Alle Spiele in einer Tabelle](watcher.md) ist die Ausgabe von `python -m heat3d_watch games --markdown`.
