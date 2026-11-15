"""Replays: the folder watch, and CS2 demos through the repository's own converter."""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

import pytest

from heat3d_watch.adapters.base import Context
from heat3d_watch.adapters.replays import SETTLE_SECONDS, ReplayAdapter, record_match
from heat3d_watch.config import Settings
from heat3d_watch.session import Session

#: A folder of real CS2 demos to check the conversion on, where one is at hand.
DEMOS = Path(os.environ.get("HEAT3D_CS2_DEMOS", "")) if os.environ.get("HEAT3D_CS2_DEMOS") else None


class _Counting(ReplayAdapter):
    def __init__(self, folder: Path):
        super().__init__(id="test-replays", game="Test", patterns=("*.rep",))
        self.folder = folder
        self.converted: list[str] = []

    def folders(self, ctx):
        return [self.folder]

    def convert(self, path, ctx):
        self.converted.append(path.name)


def test_old_replays_are_noted_and_new_ones_converted_once_written(tmp_path, monkeypatch):
    folder = tmp_path / "replays"
    folder.mkdir()
    (folder / "old.rep").write_bytes(b"x")
    a = _Counting(folder)
    ctx = Context(Settings(data=str(tmp_path / "data")), tmp_path / "data")
    clock = [1000.0]
    monkeypatch.setattr("heat3d_watch.adapters.replays.time.time", lambda: clock[0])
    a.start(ctx)
    try:
        new = folder / "new.rep"
        new.write_bytes(b"ab")
        a.poll(ctx)  # first sight: noted
        new.write_bytes(b"abc")  # still being written
        clock[0] += SETTLE_SECONDS + 1
        a.poll(ctx)  # the size changed: the clock starts again
        clock[0] += SETTLE_SECONDS + 1
        a.poll(ctx)  # unchanged long enough: queued
        deadline = time.time() + 5
        while not a.converted and time.time() < deadline:
            time.sleep(0.05)
        assert a.converted == ["new.rep"]
        a.poll(ctx)
        clock[0] += SETTLE_SECONDS + 1
        a.poll(ctx)
        time.sleep(0.3)
        assert a.converted == ["new.rep"]  # neither again nor the old one
    finally:
        a.stop(ctx)
    # A restart remembers what was converted.
    b = _Counting(folder)
    b.start(ctx)
    b.poll(ctx)
    b.stop(ctx)
    assert b.converted == []


def test_a_match_summary_gives_the_signed_in_player_s_line(tmp_path):
    s = Session.open(tmp_path, "Counter-Strike 2", "cs2-demos")
    match = {
        "match": "m1",
        "map": "a map",
        "teams": ["Blue", "Red"],
        "score": {"Blue": 13, "Red": 9},
        "rounds": [{}] * 22,
        "players": [
            {"name": "me", "steamid": "76561190000000001", "team": "Blue", "kills": 21, "deaths": 14, "adr": 88.5},
            {"name": "other", "steamid": "76561190000000002", "team": "Red", "kills": 30, "deaths": 10},
        ],
    }
    record_match(s, match, {"76561190000000001"})
    assert s.stats["kills"] == 21 and s.stats["deaths"] == 14 and s.stats["adr"] == 88.5
    assert s.stats["won"] == 1 and s.stats["rounds"] == 22 and s.stats["score.Red"] == 9
    s.close()


@pytest.mark.local
def test_a_real_demo_converts_into_a_session(tmp_path):
    demos = sorted(DEMOS.glob("*.dem")) if DEMOS and DEMOS.is_dir() else []
    if not demos:
        pytest.skip("set HEAT3D_CS2_DEMOS to a folder of CS2 demos")
    from heat3d_watch.adapters.replays import ADAPTERS

    a = next(x for x in ADAPTERS if x.id == "cs2-demos")
    if a.missing():
        pytest.skip(a.missing())
    # A whole match: parts of one ("-p2.dem") can hold no complete round of their own.
    whole = [d for d in demos if not re.search(r"[-_]p\d+$", d.stem)]
    demo = min(whole or demos, key=lambda p: p.stat().st_size)
    ctx = Context(Settings(data=str(tmp_path)), tmp_path)
    a.convert(demo, ctx)
    sessions = list((tmp_path / "sessions").rglob("meta.json"))
    assert len(sessions) == 1
    meta = json.loads(sessions[0].read_text(encoding="utf-8"))
    assert meta["stats"]["rounds"] > 0
    assert meta["events"].get("kill", 0) > 0 and meta["positions"] > 1000
    assert list(sessions[0].parent.glob("*/*.parquet"))


def test_the_replays_command_converts_what_is_already_on_disk_once(tmp_path, capsys, monkeypatch):
    from heat3d_watch import cli

    a = _Counting(tmp_path / "watched")
    counted = a.convert

    def convert(path, ctx):
        if path.name == "broken.rep":
            raise ValueError("not a replay")
        counted(path, ctx)

    a.convert = convert
    monkeypatch.setattr(cli, "load", lambda: {a.id: a})
    folder = tmp_path / "old replays"
    folder.mkdir()
    for name in ("first.rep", "second.rep", "broken.rep"):
        (folder / name).write_bytes(b"x")
    data = Path(os.environ["HEAT3D_WATCH_HOME"])  # the settings' default data folder in this test
    assert cli.main(["replays", a.id, str(folder)]) == 0
    assert "converted 2 replay(s)" in capsys.readouterr().out
    assert sorted(a.converted) == ["first.rep", "second.rep"]
    # Noted as seen: the folder watch does not convert them a second time; the broken one is tried again.
    seen = json.loads((data / "state" / f"replays-{a.id}.json").read_text(encoding="utf-8"))
    assert {Path(k).name for k in seen} == {"first.rep", "second.rep"}
    assert cli.main(["replays", "cs2-gsi"]) == 2  # not a replay adapter
    assert cli.main(["replays", a.id, str(tmp_path / "nowhere")]) == 2
    assert a.convert_existing(Context(Settings(data=str(data)), data), folder / "none") == 0
