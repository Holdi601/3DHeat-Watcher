"""
Memory profiles: every read kept whole in the raw sidecar, each value by its
name - from a stand-in for the resolver, so no process is ever opened.
"""

from __future__ import annotations

import json

import pyarrow.parquet as pq

from heat3d_watch.adapters.base import Context
from heat3d_watch.adapters.memory_profiles import MemoryAdapter, completeness, raw_fields
from heat3d_watch.config import Settings
from heat3d_watch.memory import Profile, ReadError


class Values:
    """Stands in for `Resolver`: the values of one frame, and every name asked for."""

    def __init__(self, frames: list[dict]):
        self.frames = frames
        self.k = 0
        self.asked: list[str] = []

    def read(self, name: str):
        self.asked.append(name)
        v = self.frames[self.k].get(name)
        if v is None:
            raise ReadError("a null pointer on the way")
        return v


def profile() -> Profile:
    chain = {"base": "World", "chain": ["0x10"]}
    return Profile(
        id="test", game="Test Game", exe="game.exe", online=False, versions=[{"label": "1.0", "size": 1}],
        anchors={"World": {"module_offset": "0x1000"}},
        values={"pos": {"type": "vec3f", **chain}, "hp": {"type": "i32", **chain},
                "time": {"type": "f32", **chain}, "ammo": {"type": "i32", **chain}},
        events=[{"event": "death", "value": "hp", "when": "to_zero"}],
        rate=20,
    )


def test_every_read_is_kept_by_value_name_and_nothing_more_is_read(tmp_path):
    frames = [
        {"pos": (1.0, 2.0, 3.0), "hp": 100, "time": 5.5, "ammo": 30},
        {"time": 6.0, "ammo": 29},  # a menu: the chains to pos and hp are not there - no row, the read is kept
        {"pos": (1.5, 2.0, 3.0), "hp": 100, "time": 6.5, "ammo": 28},
        {"pos": (2.0, 2.0, 3.0), "hp": 0, "time": 7.0, "ammo": 28},  # a death
    ]
    p = profile()
    data = tmp_path / "data"
    ctx = Context(Settings(data=str(data)), data)
    a = MemoryAdapter(id="mem-test", game="Test Game", kind="memory", exes=("game.exe",), multiplayer=False,
                      profile=p)
    values = Values(frames)
    a._resolver = values
    a._session = ctx.open(a, meta={"profile": p.id})
    folder = a._session.folder
    for k in range(len(frames)):
        values.k = k
        a.poll(ctx)
    a.stop(ctx)

    # Read-only by the profile: exactly its values, each once per poll.
    assert values.asked == list(p.values) * len(frames)
    t = pq.read_table(folder / "heat.raw.parquet").to_pydict()
    assert t["type"] == ["values"] * 4
    assert t["used"] == [True, False, True, True]  # the menu's read became no row
    pos = [json.loads(v) if v else None for v in t["pos"]]
    assert pos == [[1.0, 2.0, 3.0], None, [1.5, 2.0, 3.0], [2.0, 2.0, 3.0]]
    assert t["hp"] == [100, None, 100, 0] and t["ammo"] == [30, 29, 28, 28]  # ammo: no event watches it
    assert t["value_time"] == [5.5, 6.0, 6.5, 7.0]  # a name the sidecar takes for itself, kept beside it
    assert t["unread"] == [None, "pos,hp", None, None]
    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    c = meta["selfCheck"]["completeness"]
    assert c["lost"] == 0 and c["types"]["values"] == {"seen": 4, "decoded": 0, "partial": 3, "raw": 1, "lost": 0}


def test_raw_fields_and_the_profile_s_account():
    assert raw_fields({"pos": (1, 2, 3), "type": 4, "unread": 5, "gone": None}) == {
        "pos": [1, 2, 3], "value_type": 4, "value_unread": 5, "unread": "gone",
    }
    c = completeness(profile())
    assert set(c) == {"read", "raw", "missing", "size"}
    assert "`values`" in c["raw"][0] and "20 reads a second" in c["size"]
