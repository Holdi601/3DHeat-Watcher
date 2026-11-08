"""X-Plane: the RREF/RPOS packets as documented, a fake X-Plane on localhost, the flat map."""

from __future__ import annotations

import json
import math
import socket
import struct
import time
from dataclasses import replace

import pyarrow.parquet as pq
import pytest

from heat3d_watch.adapters.base import Context
from heat3d_watch.adapters.xplane import (
    ADAPTERS,
    DATAREFS,
    RPOS_FORMAT,
    SLOW_DATAREFS,
    Tangent,
    decode_rpos,
    decode_rref,
    ground_distance,
    rpos_request,
    rref_request,
    steam_libraries,
)
from heat3d_watch.config import Settings
from heat3d_watch.session import read_rows

#: What the adapter sends X-Plane: an RREF per dataref, fast and slow, and one RPOS.
REQUESTS = len(DATAREFS) + len(SLOW_DATAREFS) + 1


def test_requests_are_laid_out_as_documented():
    p = rref_request(10, 7, "sim/flightmodel/position/latitude")
    assert len(p) == 413 and p[:5] == b"RREF\0"
    assert struct.unpack_from("<ii", p, 5) == (10, 7)
    assert p[13:].rstrip(b"\0") == b"sim/flightmodel/position/latitude" and p[-1] == 0
    assert rpos_request(10) == b"RPOS\x0010\x00"


def test_answers_decode():
    raw = b"RREF\0" + struct.pack("<if", 3, 1234.5) + struct.pack("<if", 9, 1.25)
    assert decode_rref(raw) == {3: 1234.5, 9: 1.25}
    rpos = b"RPOS\0" + struct.pack(RPOS_FORMAT, 8.5, 47.25, 500.0, 2.0, 1.0, 90.0, -3.0, 0, 0, 0, 0, 0, 0)
    d = decode_rpos(rpos)
    assert (d["lon"], d["lat"], d["alt"], d["heading"], d["roll"]) == (8.5, 47.25, 500.0, 90.0, -3.0)
    for bad in (b"RREF\0\1\2\3", b"DATA\0", b"RPOS\0" + b"\0" * 10):
        with pytest.raises(ValueError):
            (decode_rpos if bad.startswith(b"RPOS") else decode_rref)(bad)


def test_the_flat_map_is_metres_east_and_north():
    t = Tangent(47.0, 8.0)
    x, y, z = t.local(47.0, 8.0, 1000.0)
    assert abs(x) < 1e-6 and abs(z) < 1e-6 and y == 1000.0
    # One minute of latitude is about 1853 m there; one of longitude cos(47) of that.
    x, _, z = t.local(47.0 + 1 / 60, 8.0, 0)
    assert abs(x) < 1 and abs(z - 1853.4) < 3
    x, _, z = t.local(47.0, 8.0 + 1 / 60, 0)
    assert abs(x - 1855.3 * math.cos(math.radians(47))) < 3 and abs(z) < 1
    assert abs(ground_distance((47, 8), (47 + 1 / 60, 8)) - 1853) < 5


class FakeXPlane:
    """Answers RREF and RPOS subscriptions the way the document says X-Plane does."""

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", 0))
        self.sock.settimeout(2.0)
        self.port = self.sock.getsockname()[1]
        self.subs: dict[int, tuple[int, str]] = {}
        self.rpos_hz: int | None = None
        self.client = None

    def take_requests(self, count: int) -> None:
        for _ in range(count):
            data, addr = self.sock.recvfrom(1000)
            self.client = addr
            if data[:5] == b"RREF\0":
                freq, index = struct.unpack_from("<ii", data, 5)
                path = data[13:].split(b"\0", 1)[0].decode()
                if freq == 0:
                    self.subs.pop(index, None)
                else:
                    self.subs[index] = (freq, path)
            elif data[:5] == b"RPOS\0":
                self.rpos_hz = int(data[5:].split(b"\0", 1)[0])

    def send(self, values: dict[str, float], *, rpos: bool = True) -> None:
        by_path = {path: v for path, v in values.items()}
        pairs = b"".join(struct.pack("<if", i, by_path[p]) for i, (_, p) in self.subs.items() if p in by_path)
        self.sock.sendto(b"RREF\0" + pairs, self.client)
        if rpos and self.rpos_hz:
            v = values
            body = struct.pack(
                RPOS_FORMAT,
                v["sim/flightmodel/position/longitude"],
                v["sim/flightmodel/position/latitude"],
                v["sim/flightmodel/position/elevation"],
                v.get("sim/flightmodel/position/y_agl", 0.0),
                1.0, 90.0, 0.0, 0, 0, 0, 0, 0, 0,
            )
            self.sock.sendto(b"RPOS\0" + body, self.client)


def _state(lat, lon, alt, *, ground, ft, crashed=0.0, g=1.0):
    return {
        "sim/flightmodel/position/latitude": lat,
        "sim/flightmodel/position/longitude": lon,
        "sim/flightmodel/position/elevation": alt,
        "sim/flightmodel/position/indicated_airspeed": 120.0,
        "sim/flightmodel/forces/g_nrml": g,
        "sim/flightmodel/position/y_agl": 0.0 if ground else alt - 400,
        "sim/flightmodel/failures/onground_any": 1.0 if ground else 0.0,
        "sim/flightmodel2/misc/has_crashed": crashed,
        "sim/time/total_flight_time_sec": ft,
    }


def _poll_until(adapter, ctx, cond, seconds=2.0):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        adapter.poll(ctx)
        if cond():
            return
        time.sleep(0.005)
    raise AssertionError("adapter never got there")


def test_a_flight_against_a_fake_xplane(tmp_path):
    xp = FakeXPlane()
    a = replace(ADAPTERS[0], port=xp.port)
    ctx = Context(Settings(data=str(tmp_path)), tmp_path)
    a.start(ctx)
    xp.take_requests(REQUESTS)
    assert {p for _, p in xp.subs.values()} == {p for _, p, _ in (*DATAREFS, *SLOW_DATAREFS)}
    assert {f for f, p in xp.subs.values() if p in {q for _, q, _ in DATAREFS}} == {10} and xp.rpos_hz == 10
    assert {f for f, p in xp.subs.values() if p in {q for _, q, _ in SLOW_DATAREFS}} == {1}

    lat, lon = 47.0, 8.0
    step = 0.0001  # about 11 m of latitude per fix: a takeoff run
    track = []
    for i in range(6):
        track.append(_state(lat + i * step, lon, 400.0, ground=True, ft=10 + i))
    for i in range(6, 12):
        track.append(_state(lat + i * step, lon, 400.0 + (i - 5) * 5, ground=False, ft=10 + i, g=1.0 + i / 10))
    track.append(_state(lat + 12 * step, lon, 400.0, ground=True, ft=22))
    track.append(_state(lat + 13 * step, lon, 400.0, ground=True, ft=23, crashed=1.0))
    for n, st in enumerate(track, 1):
        xp.send(st)
        _poll_until(a, ctx, lambda: a._session is not None and a._session.counts.get("position", 0) >= n)
    # A reset: flight time starts again, somewhere close by.
    xp.send(_state(lat, lon, 400.0, ground=True, ft=0.5))
    _poll_until(a, ctx, lambda: a._session.counts.get("session_start", 0) == 2)
    folder = a._session.folder
    a.stop(ctx)
    xp.take_requests(REQUESTS)
    assert xp.subs == {} and xp.rpos_hz == 0  # unsubscribed on stop

    rows = read_rows(folder)
    events = [r["event"] for r in rows if r["event"] != "position"]
    assert events == ["session_start", "takeoff", "landing", "crash", "session_end", "session_start", "session_end"]
    pos = [r for r in rows if r["event"] == "position"]
    assert pos[0]["x"] == pytest.approx(0, abs=1e-6) and pos[0]["z"] == pytest.approx(0, abs=1e-6)
    assert pos[5]["z"] == pytest.approx(5 * 11.12, abs=0.5)  # metres north of the first fix
    assert pos[7]["y"] == pytest.approx(410.0) and pos[7]["lat"] == pytest.approx(lat + 7 * step)
    assert {r["session"] for r in pos} == {"flight-1", "flight-2"}
    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    assert meta["origin"] == {"lat": 47.0, "lon": 8.0}
    assert meta["axes"]["up"] == "y" and meta["axes"]["flip_z"] is True
    st = meta["stats"]
    assert st["landings"] == 1 and st["takeoffs"] == 1 and st["crashes"] == 1 and st["flights"] == 2
    assert st["max_altitude_m"] == pytest.approx(430.0)
    assert st["max_g"] == pytest.approx(2.1, abs=0.01)
    assert st["distance_km"] == pytest.approx(0.15, abs=0.03)
    assert meta["geo"] == {"lat0": 47.0, "lon0": 8.0}
    t = pq.read_table(folder / "heat.parquet")
    assert "lat" in t.column_names and set(t.column("player").to_pylist()) == {"me"}
    hints = json.loads(t.schema.metadata[b"heat3d"])
    assert hints["geo"] == {"lat0": 47.0, "lon0": 8.0, "projection": "tangent-plane", "east": "x", "north": "z",
                            "up": "y"}


def test_a_jump_is_cut_and_a_far_new_flight_gets_its_own_map(tmp_path):
    xp = FakeXPlane()
    a = replace(ADAPTERS[0], port=xp.port)
    ctx = Context(Settings(data=str(tmp_path)), tmp_path)
    a.start(ctx)
    xp.take_requests(REQUESTS)
    xp.send(_state(47.0, 8.0, 400, ground=True, ft=5))
    _poll_until(a, ctx, lambda: a._session is not None and a._session.positions >= 2)
    xp.send(_state(47.5, 8.0, 400, ground=True, ft=6))  # 55 km in a blink
    _poll_until(a, ctx, lambda: a._session.counts.get("teleport", 0) == 1)
    first = a._session.folder
    xp.send(_state(-33.9, 151.2, 10, ground=True, ft=0.1))  # reset on the other side of the world
    _poll_until(a, ctx, lambda: a._session.folder != first and a._session.positions >= 1)
    second = a._session
    a.stop(ctx)
    assert [r["event"] for r in read_rows(first)][-3:] == ["spawn", "position", "session_end"]
    meta = json.loads((second.folder / "meta.json").read_text(encoding="utf-8"))
    assert meta["origin"] == {"lat": pytest.approx(-33.9), "lon": pytest.approx(151.2)}


def test_bad_packets_are_counted_not_fatal(tmp_path):
    xp = FakeXPlane()
    a = replace(ADAPTERS[0], port=xp.port)
    ctx = Context(Settings(data=str(tmp_path)), tmp_path)
    a.start(ctx)
    xp.take_requests(REQUESTS)
    xp.send(_state(47.0, 8.0, 400, ground=True, ft=5))
    _poll_until(a, ctx, lambda: a._session is not None)
    xp.sock.sendto(b"RREF\0\1\2", xp.client)
    xp.sock.sendto(b"RPOS\0short", xp.client)
    _poll_until(a, ctx, lambda: a._session.stats.get("bad_packets") == 2)
    a.stop(ctx)


@pytest.mark.local
def test_the_datarefs_exist_in_the_installed_xplane():
    refs = [lib / "steamapps" / "common" / "X-Plane 12" / "Resources" / "plugins" / "DataRefs.txt" for lib in steam_libraries()]
    found = [p for p in refs if p.is_file()]
    if not found:
        pytest.skip("no X-Plane 12 installed through Steam here")
    names = {line.split("\t", 1)[0] for line in found[0].read_text(encoding="utf-8", errors="replace").splitlines()}
    missing = [p for _, p, _ in (*DATAREFS, *SLOW_DATAREFS) if p.split("[", 1)[0] not in names]
    assert not missing


def test_every_answer_is_kept_in_the_raw_sidecar(tmp_path):
    """Answers that made rows, answers that could not (no fix yet) and packets nobody reads all reach heat.raw.parquet."""
    xp = FakeXPlane()
    a = replace(ADAPTERS[0], port=xp.port)
    ctx = Context(Settings(data=str(tmp_path)), tmp_path)
    a.start(ctx)
    xp.take_requests(REQUESTS)
    # The menus: an answer at 0/0 is no place on the earth, but the session opens to keep it.
    xp.send(_state(0.0, 0.0, 0.0, ground=True, ft=0), rpos=False)
    _poll_until(a, ctx, lambda: a._session is not None)
    xp.sock.sendto(b"XYZW" + b"\x01\x02\x03", xp.client)
    _poll_until(a, ctx, lambda: a._session.raw_counts.get("XYZW") is not None)
    slow = {p: v for p, v in (("sim/flightmodel/weight/m_fuel_total", 850.0),
                              ("sim/cockpit2/engine/indicators/engine_speed_rpm[0]", 2400.0))}
    xp.send({**_state(47.0, 8.0, 400.0, ground=True, ft=5), "sim/flightmodel/position/true_airspeed": 60.0, **slow})
    _poll_until(a, ctx, lambda: a._session.positions >= 1)
    folder = a._session.folder
    a.stop(ctx)
    t = pq.read_table(folder / "heat.raw.parquet").to_pylist()
    kinds = [(r["type"], r["used"]) for r in t]
    assert kinds[:2] == [("RREF", False), ("XYZW", False)] and ("RREF", True) in kinds and ("RPOS", True) in kinds
    assert t[1]["payload"] == b"XYZW\x01\x02\x03"
    pos = next(r for r in read_rows(folder) if r["event"] == "position")
    assert pos["tas"] == 60.0 and pos["fuel_kg"] == 850.0 and pos["rpm_1"] == 2400.0 and pos["vel_east"] == 0
    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    assert meta["geo"] == {"lat0": 47.0, "lon0": 8.0}  # placed at the first fix, not at the menus' 0/0
    assert meta["requests"]["rref"]["101"]["dataref"] == "sim/flightmodel/weight/m_total"
    check = meta["selfCheck"]["completeness"]
    assert check["lost"] == 0 and check["types"]["XYZW"] == {"seen": 1, "decoded": 0, "partial": 0, "raw": 1, "lost": 0}
