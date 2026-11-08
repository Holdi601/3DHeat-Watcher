"""
One recording: what a game said during one sitting, written as it is said.

A session is a folder. `events.jsonl` gets one line per event the moment it
happens, so a crash, a power cut or a killed process loses nothing that was
already said. When the session ends, the lines with a position become
`heat.parquet` - the table the 3DHeat viewer opens, with the reading
instructions in its footer (which column is the player, the time, the event,
which way is up) - and a summary goes into `meta.json` and the statistics
database.

Rows carry the same columns in every game:

    time     seconds since the session began (or the game's own clock)
    ms       wall-clock time, Unix milliseconds
    event    what happened: "position", "death", "kill", "spawn", ...
    x y z    where, in the game's own units and axes (see `axes` in meta.json)
    player   who: a name, an id, "me" for the person playing (where every player
             goes by name, the player's own rows carry `own_car` 1, or the
             name is meta.json's `player`)
    team     their side, when the game says
    session  the match, round or life it belongs to, when the game says

plus whatever else a game reports, by name. Rows without a position - a kill
feed line, a level-up, a stat - stay in `events.jsonl` and count in the
statistics; the table holds the rows that can be drawn.

Beside the rows, `raw()` keeps what the source sent, whole: every packet,
line or memory read, including the fields no adapter uses yet, framed into
`raw.bin` as it arrives and written out as `heat.raw.parquet` when the session
ends (3DHeat's converter rule: everything the source holds is read or kept,
docs/converters.md in the viewer's repository). meta.json's
`selfCheck.completeness` counts them per type.
"""

from __future__ import annotations

import json
import math
import re
import struct
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

#: Columns every table has, in this order.
BASE_COLUMNS = ("time", "ms", "event", "x", "y", "z", "player", "team", "session")

#: The converter rule every 3DHeat tool follows, linked from the self-check.
RULE = "https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md"
#: The raw feed while the session runs, and the sidecar it becomes.
RAW_LOG = "raw.bin"
RAW_TABLE = "heat.raw.parquet"
#: Columns every raw sidecar has, in this order.
RAW_COLUMNS = ("time", "ms", "type", "used", "payload", "text")
_FRAME = struct.Struct("<II")


@dataclass
class Axes:
    """Which way the game's world is, for the viewer: the up axis, mirrored axes, units."""

    up: str = "y"
    flip_x: bool = False
    flip_y: bool = False
    flip_z: bool = False
    #: The viewer's unit scale: it multiplies every position by this when it loads
    #: the table (0.01 would turn centimetres into metres). 1 keeps the game's own
    #: units, which every adapter does: a level exported from the game is in the
    #: same units, so the rows land on it. `units` says what one unit is.
    scale: float = 1.0
    #: A short note on the units, said in meta.json ("metres", "inches", "light years").
    units: str = "metres"


def _slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-")[:60] or "game"


@dataclass
class Session:
    game: str
    adapter: str
    folder: Path
    axes: Axes = field(default_factory=Axes)
    #: Where the numbers came from, said in meta.json: "UDP telemetry", "Journal files", ...
    source: str = ""
    multiplayer: bool = False
    started: float = field(default_factory=time.time)
    ended: float | None = None
    stats: dict[str, float | str] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)
    positions: int = 0
    #: Where on the earth the rows are, for sessions that have a place there: {"lat0": .., "lon0": ..},
    #: the origin of the flat map x/y/z are in (x east, y altitude, z north, metres; see `Tangent`).
    #: Said in meta.json and in the table's footer, so the viewer can lay the real world under the rows.
    geo: dict[str, float] | None = None
    #: The raw feed per type: [items seen, items also turned into rows] (see `raw`).
    raw_counts: dict[str, list[int]] = field(default_factory=dict)
    _mono: float = field(default_factory=time.monotonic)
    _file: Any = None
    _raw: Any = None
    _lock: threading.Lock = field(default_factory=threading.Lock)
    #: When meta.json was last written; it is kept current while the session runs.
    _flushed: float = 0.0

    @classmethod
    def open(cls, root: Path, game: str, adapter: str, *, when: float | None = None, **kw: Any) -> "Session":
        stamp = datetime.fromtimestamp(when or time.time()).strftime("%Y-%m-%d_%H-%M-%S")
        folder = root / "sessions" / _slug(game) / f"{stamp}_{_slug(adapter)}"
        n = 1
        while folder.exists():
            n += 1
            folder = folder.with_name(f"{stamp}_{_slug(adapter)}_{n}")
        folder.mkdir(parents=True)
        s = cls(game=game, adapter=adapter, folder=folder, **kw)
        if when:
            s.started = when
        s._file = (folder / "events.jsonl").open("a", encoding="utf-8", buffering=1)
        s.write_meta()
        return s

    @property
    def id(self) -> str:
        """Unique across games: the game's folder and the session's, as on disk."""
        return f"{self.folder.parent.name}/{self.folder.name}"

    def now(self) -> float:
        """Seconds since the session began."""
        return time.monotonic() - self._mono

    # ------------------------------------------------------------------ record

    def event(
        self,
        event: str,
        *,
        t: float | None = None,
        ms: float | None = None,
        x: float | None = None,
        y: float | None = None,
        z: float | None = None,
        player: str | None = None,
        team: str | None = None,
        session: str | None = None,
        **attrs: Any,
    ) -> None:
        """Record one thing that happened. Coordinates are optional; so is everything but its name."""
        row: dict[str, Any] = {
            "time": round(self.now() if t is None else float(t), 4),
            "ms": int(ms if ms is not None else time.time() * 1000),
            "event": event,
        }
        has_position = x is not None and y is not None and z is not None
        if has_position:
            if not all(math.isfinite(float(v)) for v in (x, y, z)):
                has_position = False
            else:
                row["x"], row["y"], row["z"] = float(x), float(y), float(z)
        if player is not None:
            row["player"] = str(player)
        if team is not None:
            row["team"] = str(team)
        if session is not None:
            row["session"] = str(session)
        for k, v in attrs.items():
            if v is None:
                continue
            if isinstance(v, float) and not math.isfinite(v):
                continue
            row[k] = v
        line = json.dumps(row, ensure_ascii=False, separators=(",", ":"))
        with self._lock:
            if self._file is None:
                return
            self._file.write(line + "\n")
            self.counts[event] = self.counts.get(event, 0) + 1
            if has_position:
                self.positions += 1
        self._flush()

    def position(self, x: float, y: float, z: float, **kw: Any) -> None:
        """Where someone is now: an event named "position"."""
        self.event("position", x=x, y=y, z=z, **kw)

    def raw(
        self,
        type: str,
        payload: bytes | bytearray | memoryview | None = None,
        *,
        text: str | None = None,
        used: bool = False,
        t: float | None = None,
        ms: float | None = None,
        **fields: Any,
    ) -> None:
        """
        Keep one thing the source sent, whole: a packet's bytes (`payload`), a
        line or a JSON object as it came (`text`), or a read's fields by name
        (`fields`, each its own column). `type` is the source's own word for
        it (a packet id, a line's kind); `used` says the adapter also turned
        it into rows. Nothing is thinned: every item given is kept, so a later
        decoder needs only `heat.raw.parquet`.
        """
        head: dict[str, Any] = {
            "time": round(self.now() if t is None else float(t), 4),
            "ms": int(ms if ms is not None else time.time() * 1000),
            "type": str(type),
            "used": bool(used),
        }
        if text is not None:
            head["text"] = str(text)
        for k, v in fields.items():
            if v is None or k in RAW_COLUMNS:
                continue
            if isinstance(v, float) and not math.isfinite(v):
                v = str(v)
            elif isinstance(v, (bytes, bytearray, memoryview)):
                v = bytes(v).hex()
            head[k] = v
        h = json.dumps(head, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")
        body = bytes(payload) if payload is not None else b""
        with self._lock:
            if self._file is None:
                return
            if self._raw is None:
                self._raw = (self.folder / RAW_LOG).open("ab")
            self._raw.write(_FRAME.pack(len(h), len(body)))
            self._raw.write(h)
            self._raw.write(body)
            c = self.raw_counts.setdefault(head["type"], [0, 0])
            c[0] += 1
            c[1] += int(bool(used))
        self._flush()

    def stat(self, key: str, value: float | str, how: str = "set") -> None:
        """A number for the statistics: `set` it, `add` to it, keep the `max` or `min`."""
        with self._lock:
            old = self.stats.get(key)
            if how == "add" and isinstance(old, (int, float)) and isinstance(value, (int, float)):
                value = old + value
            elif how == "max" and isinstance(old, (int, float)) and isinstance(value, (int, float)):
                value = max(old, value)
            elif how == "min" and isinstance(old, (int, float)) and isinstance(value, (int, float)):
                value = min(old, value)
            self.stats[key] = value
        self._flush()

    def _flush(self, every: float = 30.0) -> None:
        """
        meta.json brought up to date now and then, not only at the end.

        The lines are safe the moment they are written; the statistics live in
        memory until the session closes. A watcher killed mid-game - a crash, a
        shutdown, a task manager - would lose them, so they are written out every
        half minute and `recover()` finishes such a session the next time.
        """
        now = time.monotonic()
        if now - self._flushed < every:
            return
        self._flushed = now
        try:
            with self._lock:
                if self._raw is not None:
                    self._raw.flush()
            self.write_meta()
        except OSError:
            pass

    # ------------------------------------------------------------------- close

    def write_meta(self) -> None:
        from . import __version__

        doc = {
            "format": "heat3d-watch-session",
            "version": 1,
            "watcher": __version__,
            "game": self.game,
            "adapter": self.adapter,
            "source": self.source,
            "multiplayer": self.multiplayer,
            "started": datetime.fromtimestamp(self.started).isoformat(timespec="seconds"),
            "ended": datetime.fromtimestamp(self.ended).isoformat(timespec="seconds") if self.ended else None,
            "seconds": round((self.ended or time.time()) - self.started, 1),
            "axes": self.axes.__dict__,
            "events": dict(sorted(self.counts.items(), key=lambda kv: -kv[1])),
            "positions": self.positions,
            "stats": self.stats,
            **self.meta,
        }
        if self.geo:
            doc["geo"] = self.geo
        if self.raw_counts:
            doc["selfCheck"] = {**(doc.get("selfCheck") or {}), "completeness": completeness(self.raw_counts)}
        (self.folder / "meta.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")

    def close(self) -> Path | None:
        """End the session: the table, the summary. Returns the table, or None when nothing was said."""
        with self._lock:
            if self._file is None:
                return None
            self._file.close()
            self._file = None
            if self._raw is not None:
                self._raw.close()
                self._raw = None
        self.ended = time.time()
        self.write_meta()
        if not self.counts and not self.raw_counts:
            return None
        try:
            write_raw_table(self.folder)
            return write_table(self.folder, self.axes, self.game, geo=self.geo) if self.counts else None
        except ImportError:
            # pyarrow missing: the lines and raw.bin are the record, the tables can be made later.
            return None


def completeness(raw_counts: dict[str, list[int]]) -> dict[str, Any]:
    """
    The self-check of docs/converters.md for a live feed: every item the
    source sent is kept whole in the raw sidecar, so none is lost; `partial`
    counts the ones an adapter also turned into rows, `raw` the ones kept only.
    """
    types = {
        k: {"seen": n, "decoded": 0, "partial": used, "raw": n - used, "lost": 0}
        for k, (n, used) in sorted(raw_counts.items())
    }
    return {"rule": RULE, "sidecars": [RAW_TABLE], "types": types, "lost": 0}


def read_raw(folder: Path):
    """The raw feed's items as (head, payload), in order; a frame cut short by a crash ends it."""
    path = folder / RAW_LOG
    if not path.exists():
        return
    with path.open("rb") as f:
        while True:
            frame = f.read(_FRAME.size)
            if len(frame) < _FRAME.size:
                return
            nh, nb = _FRAME.unpack(frame)
            h = f.read(nh)
            body = f.read(nb)
            if len(h) < nh or len(body) < nb:
                return
            try:
                head = json.loads(h)
            except ValueError:
                return
            yield head, body


def write_raw_table(folder: Path, batch: int = 50_000, batch_bytes: int = 64 << 20) -> Path | None:
    """
    `raw.bin` as `heat.raw.parquet` (zstd): `time`, `ms`, `type`, `used`,
    `payload` (the bytes), `text`, then every field an adapter gave by name,
    numbers as float64 and the rest as text. raw.bin is removed once the
    table is written. Two passes, so a long session's feed is never in
    memory at once: a row group is written every `batch` items or
    `batch_bytes` of payload and text, whichever comes first (a shared
    memory page of 40 KB at 10 Hz fills 64 MB in under three minutes).
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    if not (folder / RAW_LOG).exists():
        return None
    extra: dict[str, bool] = {}  # name -> every value numeric
    for head, _ in read_raw(folder):
        for k, v in head.items():
            if k in RAW_COLUMNS:
                continue
            num = isinstance(v, (int, float)) and not isinstance(v, bool)
            extra[k] = extra.get(k, True) and num
    dict_str = pa.dictionary(pa.int32(), pa.string())
    schema = pa.schema(
        [("time", pa.float64()), ("ms", pa.int64()), ("type", dict_str), ("used", pa.bool_()),
         ("payload", pa.binary()), ("text", pa.string())]
        + [(k, pa.float64() if num else dict_str) for k, num in extra.items()],
        metadata={b"heat3d": json.dumps({"version": 1, "kind": "heat3d-raw", "rule": RULE}).encode("utf-8")},
    )
    out = folder / RAW_TABLE
    tmp = folder / (RAW_TABLE + ".tmp")
    names = schema.names

    def arrays(cols: dict[str, list]) -> list:
        out = []
        for f in schema:
            vals = cols[f.name]
            if pa.types.is_dictionary(f.type):
                out.append(pa.array(vals, pa.string()).dictionary_encode().cast(f.type))
            elif pa.types.is_floating(f.type) and f.name not in ("time",):
                out.append(pa.array([None if v is None else float(v) for v in vals], f.type))
            else:
                out.append(pa.array(vals, f.type))
        return out

    with pq.ParquetWriter(tmp, schema, compression="zstd") as writer:
        cols: dict[str, list] = {k: [] for k in names}
        n = size = 0
        for head, body in read_raw(folder):
            for k in names:
                if k == "payload":
                    cols[k].append(body)
                elif k in ("time", "ms", "type", "used", "text"):
                    cols[k].append(head.get(k))
                else:
                    v = head.get(k)
                    if v is not None and not extra[k] and not isinstance(v, str):
                        v = json.dumps(v, ensure_ascii=False)
                    cols[k].append(v)
            n += 1
            size += len(body) + len(head.get("text") or "")
            if n >= batch or size >= batch_bytes:
                writer.write_table(pa.Table.from_arrays(arrays(cols), schema=schema))
                cols = {k: [] for k in names}
                n = size = 0
        if cols["time"]:
            writer.write_table(pa.Table.from_arrays(arrays(cols), schema=schema))
    tmp.replace(out)
    (folder / RAW_LOG).unlink(missing_ok=True)
    return out


def read_rows(folder: Path) -> list[dict[str, Any]]:
    rows = []
    path = folder / "events.jsonl"
    if not path.exists():
        return rows
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                # A line cut short by a crash: everything before it stands.
                continue
    return rows


def geo_hint(geo: dict[str, Any] | None) -> dict[str, Any] | None:
    """
    The footer's `geo` entry for a session placed on the earth, or None.

    `lat0`/`lon0` are the flat map's origin (degrees); `east`, `north` and `up`
    name the columns holding metres east and north of it and the altitude above
    sea level - x, z and y, as `Tangent.local` gives them.
    """
    if not geo:
        return None
    try:
        lat0, lon0 = float(geo["lat0"]), float(geo["lon0"])
    except (KeyError, TypeError, ValueError):
        return None
    if not (math.isfinite(lat0) and math.isfinite(lon0)):
        return None
    hint: dict[str, Any] = {"lat0": lat0, "lon0": lon0, "projection": "tangent-plane", "east": "x", "north": "z", "up": "y"}
    # DCS tables keep the sim's own metres too (x north, y up, z east in the
    # theatre's transverse Mercator projection): the viewer can place those
    # on the earth as well, by the theatre's name.
    dcs = geo.get("dcs")
    if isinstance(dcs, dict) and isinstance(dcs.get("theatre"), str) and dcs["theatre"]:
        hint["dcs"] = {"theatre": dcs["theatre"], "x": "dcs_x", "y": "dcs_y", "z": "dcs_z"}
    return hint


def write_table(folder: Path, axes: Axes, game: str, geo: dict[str, Any] | None = None) -> Path | None:
    """`events.jsonl` as `heat.parquet`, with the viewer's reading instructions in the footer."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    rows = [r for r in read_rows(folder) if "x" in r]
    if not rows:
        return None
    extra: list[str] = []
    for r in rows:
        for k in r:
            if k not in BASE_COLUMNS and k not in extra:
                extra.append(k)
    columns: dict[str, pa.Array] = {}
    for name in (*BASE_COLUMNS, *extra):
        values = [r.get(name) for r in rows]
        numeric = all(v is None or (isinstance(v, (int, float)) and not isinstance(v, bool)) for v in values)
        if name in ("x", "y", "z", "time"):
            columns[name] = pa.array([float(v) if v is not None else None for v in values], type=pa.float64())
        elif name == "ms":
            columns[name] = pa.array(values, type=pa.int64())
        elif numeric and any(v is not None for v in values):
            columns[name] = pa.array([float(v) if v is not None else None for v in values], type=pa.float64())
        else:
            text = ["" if v is None else (v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)) for v in values]
            columns[name] = pa.array(text, type=pa.string()).dictionary_encode()
    table = pa.table(columns)
    hints = {
        "version": 1,
        "kind": "heat3d-watch",
        "game": game,
        "axes": {"up": axes.up, "flipX": axes.flip_x, "flipY": axes.flip_y, "flipZ": axes.flip_z, "scale": axes.scale},
        "columns": {
            "x": "x",
            "y": "y",
            "z": "z",
            "time": "time",
            "timeUnit": "seconds",
            "personId": "player",
            "teamId": "team",
            "sessionId": "session",
            "extra": ["event", *[c for c in extra]],
        },
    }
    place = geo_hint(geo)
    if place:
        hints["geo"] = place
    meta = dict(table.schema.metadata or {})
    meta[b"heat3d"] = json.dumps(hints).encode("utf-8")
    table = table.replace_schema_metadata(meta)
    out = folder / "heat.parquet"
    pq.write_table(table, out)
    return out


def recover(data: Path) -> list[Session]:
    """
    Sessions a killed watcher left open, finished now: ended at their last event,
    their table written, their statistics as last saved. Returns them, for the
    statistics database.
    """
    out: list[Session] = []
    for meta_path in sorted((data / "sessions").glob("*/*/meta.json")):
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if meta.get("format") != "heat3d-watch-session" or meta.get("ended"):
            continue
        folder = meta_path.parent
        rows = read_rows(folder)
        if not rows and not (folder / RAW_LOG).exists():
            continue
        a = meta.get("axes") or {}
        axes = Axes(**{k: v for k, v in a.items() if k in Axes.__dataclass_fields__})
        try:
            started = datetime.fromisoformat(meta["started"]).timestamp()
        except (KeyError, ValueError):
            started = folder.stat().st_mtime
        known = {"format", "version", "watcher", "game", "adapter", "source", "multiplayer", "started", "ended",
                 "seconds", "axes", "events", "positions", "stats", "geo", "selfCheck"}
        s = Session(
            game=meta.get("game", folder.parent.name),
            adapter=meta.get("adapter", ""),
            folder=folder,
            axes=axes,
            source=meta.get("source", ""),
            multiplayer=bool(meta.get("multiplayer")),
            started=started,
            stats=dict(meta.get("stats") or {}),
            meta={k: v for k, v in meta.items() if k not in known},
            geo=meta.get("geo") if isinstance(meta.get("geo"), dict) else None,
        )
        for r in rows:
            e = str(r.get("event", ""))
            s.counts[e] = s.counts.get(e, 0) + 1
            if "x" in r:
                s.positions += 1
        last_ms = max((r.get("ms") or 0 for r in rows), default=0)
        for head, _ in read_raw(folder):
            c = s.raw_counts.setdefault(str(head.get("type", "")), [0, 0])
            c[0] += 1
            c[1] += int(bool(head.get("used")))
            last_ms = max(last_ms, head.get("ms") or 0)
        s.ended = last_ms / 1000.0 if last_ms else folder.stat().st_mtime
        s.meta["recovered"] = True
        s.write_meta()
        try:
            write_raw_table(folder)
            if rows:
                write_table(folder, axes, s.game, geo=s.geo)
        except (ImportError, OSError):
            pass
        if rows:
            # Only a session with rows has statistics; one with only a raw feed is finished, not counted.
            out.append(s)
    return out
