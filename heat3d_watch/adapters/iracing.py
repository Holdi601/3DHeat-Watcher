"""
iRacing, live: the iRacing SDK's shared memory, read natively.

iRacing publishes its telemetry for apps in a named file mapping,
`Local\\IRSDKMemMapFileName`, that the sim creates while it runs (and signals
`Local\\IRSDKDataValidEvent` on each update, which is not needed here: the
watcher looks ten times a second). The layout is the SDK's `irsdk_defines.h`,
also followed by pyirsdk (MIT) - written again here from those facts:

    irsdk_header (little-endian int32s)
        0 ver, 4 status (bit 0: connected), 8 tickRate,
        12 sessionInfoUpdate, 16 sessionInfoLen, 20 sessionInfoOffset,
        24 numVars, 28 varHeaderOffset, 32 numBuf, 36 bufLen, 40 pad[2],
        48 varBuf[4]: { tickCount, bufOffset, pad[2] } (16 bytes each)
    irsdk_varHeader (144 bytes, numVars of them at varHeaderOffset)
        0 type (0 char, 1 bool, 2 int, 3 bitfield, 4 float, 5 double),
        4 offset (into a line), 8 count, 12 countAsTime + 3 pad,
        16 name[32], 48 desc[64], 112 unit[32]
    session info: YAML text at sessionInfoOffset, rewritten when
        sessionInfoUpdate changes (track, sessions, drivers)

The sim writes `numBuf` lines round-robin; the newest is the one with the
highest tickCount, and a line is taken again if its tickCount moved while it
was being copied.

Live data has no world position - latitude, longitude and altitude are only in
the `.ibt` files iRacing logs to `Documents\\iRacing\\telemetry` (Alt+L in the
car, or `irsdkLog=1`), which the 3DHeat viewer reads itself. So this records
the driving as events without coordinates - speed, lap, the share of the lap
done, race position, incidents - plus laps, incidents, pit stops and the
chequered flag, and at the end the `.ibt` files written during the sitting as
`telemetry_file` events, for the viewer to open.

Beside the rows the whole memory map is kept, in the session's raw sidecar
(`heat.raw.parquet`): the header's fixed part (`header`, each time it
changes), the variable headers (`var_headers`, whole, and as JSON in `text`,
each time the layout changes), the session info YAML (`session_info`, its
text each time `sessionInfoUpdate` moves) and the newest telemetry line
(`telemetry`, every variable of it, each read that finds a new tick). The var
headers and a line are all a later decoder needs to read any variable.

Source: the iRacing SDK (irsdk_defines.h, "iRacing SDK" forum documentation);
kutu/pyirsdk (MIT) for confirmation of the offsets.
"""

from __future__ import annotations

import json
import logging
import math
import re
import struct
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..session import Axes
from .base import Adapter, Context
from .racing import KMH, Driving, Pages, documents

log = logging.getLogger("heat3d_watch")

MEMMAP = "Local\\IRSDKMemMapFileName"
HEADER = struct.Struct("<10i")
VAR_BUF = 48
MAX_BUFS = 4
VAR_HEADER = struct.Struct("<iii?3x32s64s32s")  # 144
STATUS_CONNECTED = 1
#: irsdk_VarType -> (struct code, bytes)
TYPES = {0: ("c", 1), 1: ("?", 1), 2: ("i", 4), 3: ("I", 4), 4: ("f", 4), 5: ("d", 8)}

#: irsdk_SessionState
STATE_CHECKERED = 5
STATES = {0: "invalid", 1: "get in car", 2: "warmup", 3: "parade laps", 4: "racing", 5: "checkered", 6: "cool down"}

#: The live variables used; any the sim does not have are simply absent.
WANTED = (
    "SessionTime", "SessionNum", "SessionState", "SessionUniqueID", "IsOnTrack", "IsReplayPlaying",
    "Lap", "LapCompleted", "LapDistPct", "LapDist", "LapLastLapTime", "LapBestLapTime",
    "Speed", "Gear", "Throttle", "Brake", "RPM", "OnPitRoad", "PlayerTrackSurface",
    "PlayerCarPosition", "PlayerCarClassPosition", "PlayerCarMyIncidentCount",
    "SteeringWheelAngle", "Yaw", "YawNorth", "Pitch", "Roll", "FuelLevel", "LatAccel", "LongAccel",
)
#: Variables put on the driving rows under their own name, when the sim says the unit expected.
ANGLES = {"SteeringWheelAngle": "steering_angle", "Yaw": "yaw", "YawNorth": "yaw_north", "Pitch": "pitch",
          "Roll": "roll"}
MEASURES = {"FuelLevel": ("fuel_l", "l"), "LatAccel": ("lat_accel", "m/s^2"), "LongAccel": ("lon_accel", "m/s^2")}


@dataclass
class Var:
    name: str
    type: int
    offset: int
    count: int
    unit: str
    desc: str = ""
    count_as_time: bool = False


def parse_header(raw: bytes) -> dict:
    v = HEADER.unpack_from(raw, 0)
    head = dict(zip(("ver", "status", "tick_rate", "info_update", "info_len", "info_offset", "num_vars",
                     "var_header_offset", "num_buf", "buf_len"), v))
    head["bufs"] = [struct.unpack_from("<ii", raw, VAR_BUF + 16 * i) for i in range(MAX_BUFS)]
    return head


def parse_vars(raw: bytes, count: int) -> dict[str, Var]:
    out = {}
    for i in range(count):
        t, off, n, as_time, name, desc, unit = VAR_HEADER.unpack_from(raw, i * VAR_HEADER.size)
        key = name.split(b"\x00", 1)[0].decode("latin-1")
        out[key] = Var(key, t, off, n, unit.split(b"\x00", 1)[0].decode("latin-1"),
                       desc.split(b"\x00", 1)[0].decode("latin-1"), bool(as_time))
    return out


def vars_text(variables: dict[str, Var]) -> str:
    """The variable headers as JSON, one entry per variable in the sim's order: enough to read any line."""
    return json.dumps(
        [{"name": v.name, "type": v.type, "offset": v.offset, "count": v.count, "count_as_time": v.count_as_time,
          "unit": v.unit, "desc": v.desc} for v in variables.values()],
        ensure_ascii=False,
    )


def value(line: bytes, var: Var) -> Any:
    code, size = TYPES.get(var.type, ("", 0))
    if not code or var.offset + size * var.count > len(line):
        return None
    if var.type == 0:
        return line[var.offset : var.offset + var.count].split(b"\x00", 1)[0].decode("latin-1")
    values = struct.unpack_from(f"<{var.count}{code}", line, var.offset)
    return values[0] if var.count == 1 else list(values)


def session_yaml(text: str) -> dict:
    """
    The few things wanted from the session info, without a YAML library: the
    player's car index, the track, the session types, and each driver's name and car.
    """
    out: dict[str, Any] = {"drivers": {}, "sessions": {}}
    m = re.search(r"^\s*DriverCarIdx:\s*(-?\d+)", text, re.M)
    if m:
        out["car_idx"] = int(m.group(1))
    m = re.search(r"^\s*TrackDisplayName:\s*(.+?)\s*$", text, re.M)
    if m:
        out["track"] = m.group(1).strip()
    m = re.search(r"^\s*TrackConfigName:\s*(.+?)\s*$", text, re.M)
    if m and m.group(1).strip():
        out["track_config"] = m.group(1).strip()
    current: dict | None = None
    session: int | None = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("- CarIdx:"):
            current = {"idx": int(s.split(":", 1)[1])}
            out["drivers"][current["idx"]] = current
        elif current is not None and s.startswith(("UserName:", "CarScreenName:", "TeamName:", "CarNumber:")):
            k, v = s.split(":", 1)
            current[k] = v.strip().strip('"')
        if s.startswith("- SessionNum:"):
            session = int(s.split(":", 1)[1])
        elif session is not None and s.startswith("SessionType:"):
            out["sessions"][session] = s.split(":", 1)[1].strip()
            session = None
    return out


class Irsdk:
    """The sim's shared memory, read: the header, the variables, the newest line."""

    def __init__(self, view: Any):
        self.view = view
        self.vars: dict[str, Var] = {}
        self._layout: tuple[int, int] | None = None
        self.info_update = -1
        self.info: dict = {}
        #: The bytes last read, for the raw sidecar: the header, the newest line.
        self.head_raw = b""
        self.line = b""
        #: Set when they were read again (the layout or the session info changed); the adapter keeps and clears them.
        self.new_vars: bytes | None = None
        self.new_info: bytes | None = None

    def header(self) -> dict:
        self.head_raw = self.view.read(0, VAR_BUF + 16 * MAX_BUFS)
        return parse_header(self.head_raw)

    def connected(self, head: dict) -> bool:
        return bool(head["status"] & STATUS_CONNECTED) and head["num_buf"] > 0 and head["buf_len"] > 0

    def read(self, head: dict) -> tuple[int, dict[str, Any]] | None:
        """(tick, the wanted values) from the newest complete line; the whole line stays in `line`."""
        layout = (head["num_vars"], head["var_header_offset"])
        if layout != self._layout:
            block = self.view.read(head["var_header_offset"], head["num_vars"] * VAR_HEADER.size)
            self.vars = parse_vars(block, head["num_vars"])
            self._layout = layout
            self.new_vars = block
        if head["info_update"] != self.info_update and head["info_len"] > 0:
            text = self.view.read(head["info_offset"], head["info_len"]).split(b"\x00", 1)[0]
            self.info = session_yaml(text.decode("cp1252", errors="replace"))
            self.info_update = head["info_update"]
            self.new_info = text
        n = max(1, min(head["num_buf"], MAX_BUFS))
        for _ in range(3):
            tick, offset = max(head["bufs"][:n])
            line = self.view.read(offset, head["buf_len"])
            again = parse_header(self.view.read(0, VAR_BUF + 16 * MAX_BUFS))
            if (tick, offset) in again["bufs"][:n]:
                self.line = line
                return tick, {name: value(line, self.vars[name]) for name in WANTED if name in self.vars}
            head = again  # the sim wrote over it while it was copied
        return None


@dataclass
class IRacingAdapter(Adapter):
    """iRacing's live telemetry: the driving as events, laps, incidents; the .ibt files named."""

    #: The mapping's name; tests use their own.
    tagname: str = MEMMAP
    #: Rows per second of driving data (they carry no position).
    hz: float = 5.0
    #: Where iRacing writes .ibt files; empty: Documents\iRacing\telemetry.
    telemetry_folder: str = ""

    def missing(self) -> str | None:
        if sys.platform != "win32":
            return "iRacing's shared memory is Windows only"
        return None

    def start(self, ctx: Context) -> None:
        self._drive = Driving(self, ctx)
        self._pages = Pages()
        self._sdk: Irsdk | None = None
        self._tried = 0.0
        self._last_tick: int | None = None
        self._prev: dict[str, Any] = {}
        self._session: tuple | None = None
        self._last_row = -1e9
        self._last_time: float | None = None
        self._metres = 0.0
        self._folder = Path(self.telemetry_folder) if self.telemetry_folder else documents() / "iRacing" / "telemetry"
        self._ibt_before = self._ibt_files()
        self._started = time.time()

    def _ibt_files(self) -> dict[Path, tuple[int, float]]:
        try:
            return {p: (p.stat().st_size, p.stat().st_mtime) for p in self._folder.glob("*.ibt")}
        except OSError:
            return {}

    def _open(self) -> bool:
        if self._sdk is not None:
            return True
        now = time.monotonic()
        if now - self._tried < 2.0:
            return False
        self._tried = now
        from .simracing_shm import SharedView

        view = SharedView.open(self.tagname)
        if view is None:
            return False
        self._sdk = Irsdk(view)
        return True

    def poll(self, ctx: Context) -> None:
        if not self._open():
            return
        d, sdk = self._drive, self._sdk
        try:
            head = sdk.header()
            # The header whole each time it changes: status, session info update, layout, the lines' ticks.
            self._pages.keep(d, "header", sdk.head_raw)
            if not sdk.connected(head):
                self._prev = {}
                return
            got = sdk.read(head)
        except Exception:  # noqa: BLE001
            d.count("bad_reads")
            return
        self._keep_context()
        if got is None:
            d.count("torn_reads")
            return
        tick, v = got
        if tick == self._last_tick:
            return
        self._last_tick = tick
        # The whole line, every variable in it - the rows below take a few.
        d.raw("telemetry", sdk.line, used=not v.get("IsReplayPlaying"), tick=tick)
        try:
            self.step(v)
        except Exception:  # noqa: BLE001
            d.count("bad_reads")

    def _keep_context(self) -> None:
        """What a later decoder needs to read the lines: the variable headers, and the session info."""
        d, sdk = self._drive, self._sdk
        if sdk.new_vars is not None:
            d.raw("var_headers", sdk.new_vars, text=vars_text(sdk.vars), num_vars=len(sdk.vars))
            sdk.new_vars = None
        if sdk.new_info is not None:
            text = sdk.new_info.decode("cp1252", errors="replace")
            # The bytes as well only where cp1252 could not say them all.
            d.raw("session_info", sdk.new_info if "�" in text else None, text=text, used=True,
                  update=sdk.info_update)
            sdk.new_info = None

    def _extra(self, v: dict[str, Any]) -> dict[str, Any]:
        """Orientation, steering, fuel and accelerations, each only when the sim's unit is the one expected."""
        out: dict[str, Any] = {}
        known = self._sdk.vars if self._sdk else {}
        for name, col in ANGLES.items():
            x, var = v.get(name), known.get(name)
            if isinstance(x, float) and math.isfinite(x) and var is not None and var.unit == "rad":
                out[col] = round(math.degrees(x), 2)
        for name, (col, unit) in MEASURES.items():
            x, var = v.get(name), known.get(name)
            if isinstance(x, float) and math.isfinite(x) and var is not None and var.unit == unit:
                out[col] = round(x, 3)
        return out

    def step(self, v: dict[str, Any]) -> None:
        """One new line of live data."""
        if v.get("IsReplayPlaying"):
            return
        d = self._drive
        info = self._sdk.info if self._sdk else {}
        me = info.get("drivers", {}).get(info.get("car_idx"), {})
        player = me.get("UserName") or "me"
        p = self._prev
        session_id = f"{v.get('SessionUniqueID', 0)}/{v.get('SessionNum', 0)}"
        key = (v.get("SessionUniqueID"), v.get("SessionNum"))
        if key != self._session:
            self._session = key
            p = self._prev = {}
            s = d.open(track=info.get("track"), track_config=info.get("track_config"), car=me.get("CarScreenName"))
            kind = info.get("sessions", {}).get(v.get("SessionNum"))
            d.event("session_start", player=player, where=False, session=session_id, session_type=kind,
                    track=info.get("track"), car=me.get("CarScreenName"))
            s.stat("sessions", 1, "add")
        s = d.open()

        # Distance and top speed from the speed over the sim's own clock.
        speed = v.get("Speed")
        t = v.get("SessionTime")
        if isinstance(speed, (int, float)) and isinstance(t, (int, float)):
            if self._last_time is not None and 0 < t - self._last_time < 1.0 and v.get("IsOnTrack"):
                self._metres += speed * (t - self._last_time)
                s.stat("distance_km", round(self._metres / 1000.0, 3))
            self._last_time = t
            if v.get("IsOnTrack"):
                s.stat("top_speed_kmh", round(speed * KMH, 1), "max")

        on = bool(v.get("IsOnTrack"))
        if "IsOnTrack" in p and on != p["IsOnTrack"]:
            d.event("spawn" if on else "despawn", player=player, where=False, session=session_id,
                    lap=v.get("Lap"), lap_dist_pct=_r(v.get("LapDistPct")))
        pit = v.get("OnPitRoad")
        if "OnPitRoad" in p and pit is not None and pit != p["OnPitRoad"]:
            d.event("pit_in" if pit else "pit_out", player=player, where=False, session=session_id, lap=v.get("Lap"))
            if pit:
                s.stat("pit_stops", 1, "add")
        state = v.get("SessionState")
        if "SessionState" in p and state == STATE_CHECKERED and p["SessionState"] != STATE_CHECKERED:
            d.event("chequered_flag", player=player, where=False, session=session_id)

        done = v.get("LapCompleted")
        if isinstance(done, int) and isinstance(p.get("LapCompleted"), int) and done == p["LapCompleted"] + 1 and done > 0:
            last = v.get("LapLastLapTime")
            d.lap(last if isinstance(last, (int, float)) and last > 0 else None, player=player, where=False,
                  session=session_id, lap=done, race_position=v.get("PlayerCarPosition") or None)
            if state is not None and state >= STATE_CHECKERED:
                d.event("finish", player=player, where=False, session=session_id,
                        race_position=v.get("PlayerCarPosition") or None, class_position=v.get("PlayerCarClassPosition") or None)
                s.stat("finishes", 1, "add")
        best = v.get("LapBestLapTime")
        if isinstance(best, (int, float)) and best > 0:
            s.stat("best_lap", round(best, 3), "min")

        incidents = v.get("PlayerCarMyIncidentCount")
        if isinstance(incidents, int):
            before = p.get("PlayerCarMyIncidentCount")
            if isinstance(before, int) and incidents > before:
                d.event("incident", player=player, where=False, session=session_id, points=incidents - before,
                        incidents=incidents, lap=v.get("Lap"), lap_dist_pct=_r(v.get("LapDistPct")))
            s.stat("incidents", incidents)
        position = v.get("PlayerCarPosition")
        if isinstance(position, int) and position > 0:
            s.stat("race_position", position)

        now = time.monotonic()
        if on and now - self._last_row >= 1.0 / self.hz:
            self._last_row = now
            d.event(
                "driving", player=player, where=False, session=session_id,
                speed_kmh=round(speed * KMH, 1) if isinstance(speed, (int, float)) else None,
                gear=v.get("Gear"), throttle=_r(v.get("Throttle")), brake=_r(v.get("Brake")), rpm=_r(v.get("RPM"), 0),
                lap=v.get("Lap"), lap_dist_pct=_r(v.get("LapDistPct"), 4), lap_dist=_r(v.get("LapDist"), 1),
                race_position=position or None, class_position=v.get("PlayerCarClassPosition") or None,
                incidents=incidents, track_surface=v.get("PlayerTrackSurface"), on_pit_road=1 if pit else 0,
                game_time=_r(t), **self._extra(v),
            )
        self._prev = dict(v)

    def stop(self, ctx: Context) -> None:
        # The .ibt files written while the game ran: the viewer reads them, positions and all.
        for path, (size, mtime) in sorted(self._ibt_files().items()):
            old = self._ibt_before.get(path)
            if (old is None or old != (size, mtime)) and mtime >= self._started - 5:
                self._drive.event("telemetry_file", where=False, path=str(path), bytes=size)
        if self._sdk is not None:
            self._sdk.view.close()
            self._sdk = None
        self._pages.close(self._drive)
        self._drive.close()


def _r(v: Any, digits: int = 3) -> Any:
    return round(v, digits) if isinstance(v, float) else v


ADAPTERS = [
    IRacingAdapter(
        id="iracing",
        game="iRacing",
        exes=("iRacingSim64DX11.exe", "iRacingSim64.exe"),
        kind="telemetry",
        multiplayer=True,
        source="shared memory Local\\IRSDKMemMapFileName (the iRacing SDK); .ibt files in %USERPROFILE%\\Documents\\iRacing\\telemetry",
        records=(
            "the driving at 5 Hz without a position (iRacing gives none live): speed, gear, throttle, brake, lap, "
            "share of the lap, race and class position, incidents",
            "session start, getting in and out of the car, pit lane in and out, laps with lap time, incidents with "
            "their points, chequered flag, finish",
            "the .ibt telemetry files written during the sitting (latitude, longitude, altitude - the viewer reads them)",
            "laps, best lap, incidents, race position, pit stops, distance, top speed",
            "the whole shared memory in `heat.raw.parquet`: header, variable headers, session info, every telemetry "
            "line read",
        ),
        enable="Nothing for the live data. For positions: log telemetry in the car (Alt+L) or set irsdkLog=1 in app.ini",
        axes=Axes(up="y", units="no positions live; the .ibt files carry latitude/longitude/altitude"),
        verified="tested on a shared-memory block built in the test from the irsdk layout; untested against the sim",
        completeness={
            "read": (
                "from the newest telemetry line: session time, number, state and id, on track, replay, lap, laps "
                "completed, share and metres of the lap, last and best lap, speed, gear, throttle, brake, RPM, pit "
                "road, track surface, race and class position, own incident count (the `driving` rows at 5 Hz and "
                "the events)",
                "now also on the `driving` rows: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (degrees, "
                "from the sim's radians - only when the variable header gives the unit as rad), `fuel_l` (unit l), "
                "`lat_accel` and `lon_accel` (unit m/s^2)",
                "from the session info YAML: the player's car index, track and configuration, session types, each "
                "driver's name, car, team and number (session_start rows, meta.json)",
                "checked against a block built from irsdk_defines.h in the tests; not yet against the sim",
            ),
            "raw": (
                "`telemetry`: the newest line whole, every variable the sim publishes (the CarIdx arrays of every "
                "car, tyres, suspension, the high-rate `_ST` arrays where the sim has them ...), each read that "
                "finds a new tick; `tick` the sim's tick count; `used` is false while a replay plays",
                "`var_headers`: the variable headers whole (144 bytes each) and, in `text`, as JSON (name, type, "
                "offset, count, unit, description), each time the layout changes - enough to read every variable "
                "of every kept line",
                "`session_info`: the YAML text whole each time its update counter moves (weekend, sessions and "
                "results, drivers, car setup, radio, camera lists), `update` the counter",
                "`header`: the 112-byte irsdk header whole each time it changes (version, status, tick rate, "
                "offsets, the lines' ticks)",
            ),
            "missing": (
                "a world position live: the shared memory has none; latitude, longitude and altitude are only in "
                "the .ibt files (logging on), which the viewer reads - the watcher names those written during the "
                "sitting",
                "the ticks between two reads: the sim writes 60 lines a second into 3 or 4 slots and the watcher "
                "reads 10 times a second, so most ticks are overwritten before they could be read; the .ibt file "
                "has every tick when logging is on",
            ),
            "size": (
                "a telemetry line is a few KB (about 5 to 10 KB with every car's arrays), kept up to 10 times a "
                "second, plus the header (112 bytes) as often and the session info YAML (tens of KB) when it "
                "changes: about 0.2 to 0.4 GB per hour on track before compression; zstd brings it to a fraction "
                "(not yet measured on a real session)"
            ),
        },
    )
]
