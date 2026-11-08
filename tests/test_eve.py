"""EVE Online: synthetic gamelogs in the client's format, in UTF-8 and UTF-16."""

from __future__ import annotations

import json
import time
from dataclasses import replace
from datetime import datetime, timezone

from heat3d_watch.adapters import eve
from heat3d_watch.adapters.base import Context
from heat3d_watch.config import Settings
from heat3d_watch.session import read_rows


def stamp(ts: float) -> str:
    return "[ " + datetime.fromtimestamp(ts, timezone.utc).strftime("%Y.%m.%d %H:%M:%S") + " ]"


def gamelog(t0: float, listener: str) -> str:
    head = (
        "------------------------------------------------------------\n"
        "  Gamelog\n"
        f"  Listener: {listener}\n"
        f"  Session Started: {datetime.fromtimestamp(t0, timezone.utc).strftime('%Y.%m.%d %H:%M:%S')}\n"
        "------------------------------------------------------------\n"
    )
    body = [
        "(combat) <color=0xff00ffff><b>200</b> <color=0x77ffffff><font size=10>to</font> <b><color=0xffffffff>"
        "Test Pilot[TICK](Test Frigate)</b><font size=10><color=0x77ffffff> - Test Beam Laser - Penetrates",
        "(combat) <color=0xffcc0000><b>375</b> <color=0x77ffffff><font size=10>from</font> <b><color=0xffffffff>"
        "Other Pilot[CORP](Test Cruiser)</b><font size=10><color=0x77ffffff> - Test Smartbomb - Hits",
        "(combat) Test Rat misses you completely - Test Missile",
        "(combat) Your group of Test Autocannon misses Test Rat completely - Test Autocannon",
        "(bounty) <font size=12><b><color=0xff00aa00>15,000 ISK</b> added to next bounty payout",
        "(None) Jumping from Test System A to Test System B",
        "(notify) Something the client says",
    ]
    return head + "\n".join(f"{stamp(t0 + i)} {b}" for i, b in enumerate(body)) + "\n"


def test_two_clients_side_by_side_are_both_followed(tmp_path):
    folder = tmp_path / "Gamelogs"
    folder.mkdir()
    data = tmp_path / "data"
    ctx = Context(Settings(data=str(data)), data)
    a = replace(eve.ADAPTERS[0], folder=folder)
    a.start(ctx)
    t0 = time.time()
    (folder / "20260101_120000_1.txt").write_text(gamelog(t0, "Pilot One"), encoding="utf-8")
    (folder / "20260101_120001_2.txt").write_bytes(b"\xff\xfe" + gamelog(t0, "Pilot Two").encode("utf-16-le"))
    a.poll(ctx)
    a.poll(ctx)
    a.stop(ctx)

    [session] = list((data / "sessions").glob("*/*"))
    st = json.loads((session / "meta.json").read_text(encoding="utf-8"))["stats"]
    assert st["damage_dealt"] == 400 and st["damage_received"] == 750
    assert st["hits_dealt"] == 2 and st["misses_received"] == 2 and st["misses_dealt"] == 2
    assert st["bounty_kills"] == 2 and st["bounty_isk"] == 30000 and st["jumps"] == 2
    rows = read_rows(session)
    dealt = [r for r in rows if r["event"] == "damage_dealt"]
    assert {r["player"] for r in dealt} == {"Pilot One", "Pilot Two"}
    assert dealt[0]["target"] == "Test Pilot" and dealt[0]["target_ship"] == "Test Frigate"
    assert dealt[0]["weapon"] == "Test Beam Laser" and dealt[0]["quality"] == "Penetrates"
    assert dealt[0]["target_corp"] == "TICK"
    assert next(r for r in rows if r["event"] == "damage_received")["attacker_corp"] == "CORP"
    j = next(r for r in rows if r["event"] == "jump")
    assert (j["origin"], j["destination"]) == ("Test System A", "Test System B")


def chatlog(t0: float) -> str:
    head = (
        "﻿\n\n"
        "        ---------------------------------------------------------------\n"
        "          Channel ID:      local\n"
        "          Channel Name:    Local\n"
        "          Listener:        Pilot One\n"
        f"          Session started: {datetime.fromtimestamp(t0, timezone.utc).strftime('%Y.%m.%d %H:%M:%S')}\n"
        "        ---------------------------------------------------------------\n\n"
    )
    return head + f"{stamp(t0)} EVE System > Channel changed to Local : Test System B\n{stamp(t0 + 1)} Other > o7\n"


def test_every_gamelog_and_chat_line_is_kept_whole_in_the_raw_sidecar(tmp_path):
    import pyarrow.parquet as pq

    folder = tmp_path / "Gamelogs"
    folder.mkdir()
    (tmp_path / "Chatlogs").mkdir()
    data = tmp_path / "data"
    ctx = Context(Settings(data=str(data)), data)
    a = replace(eve.ADAPTERS[0], folder=folder)
    a.start(ctx)
    t0 = time.time()
    text = gamelog(t0, "Pilot One")
    (folder / "20260101_120000_1.txt").write_text(text, encoding="utf-8")
    (tmp_path / "Chatlogs" / "Local_20260101_120000_1.txt").write_bytes(chatlog(t0).encode("utf-16-le"))
    a.poll(ctx)
    a.stop(ctx)

    [session] = list((data / "sessions").glob("*/*"))
    raw = pq.read_table(session / "heat.raw.parquet").to_pydict()
    kept = list(zip(raw["type"], raw["used"], raw["text"], raw["channel"], raw["file"]))
    assert len([k for k in kept if k[4] == "20260101_120000_1.txt"]) == len(text.splitlines())  # every line
    notify = next(k for k in kept if k[0] == "notify")
    assert notify[1] is False and notify[2].endswith("(notify) Something the client says")
    combat = [k for k in kept if k[0] == "combat"]
    assert len(combat) == 4 and all(k[1] for k in combat) and "<color=0xff00ffff>" in combat[0][2]
    chat = [k for k in kept if k[0] == "chat"]
    assert [k[2][24:] for k in chat] == ["EVE System > Channel changed to Local : Test System B", "Other > o7"]
    assert all(k[3] == "Local" and not k[1] for k in chat)
    assert {k[0] for k in kept} >= {"gamelog header", "chatlog header", "bounty", "None"}
    check = json.loads((session / "meta.json").read_text(encoding="utf-8"))["selfCheck"]["completeness"]
    assert check["lost"] == 0 and check["types"]["chat"] == {"seen": 2, "decoded": 0, "partial": 0, "raw": 2, "lost": 0}


def test_old_gamelogs_are_left_alone(tmp_path):
    import os

    folder = tmp_path / "Gamelogs"
    folder.mkdir()
    old = folder / "20250101_120000_1.txt"
    old.write_text(gamelog(time.time() - 86400, "Pilot One"), encoding="utf-8")
    t = time.time() - 86400
    os.utime(old, (t, t))
    data = tmp_path / "data"
    ctx = Context(Settings(data=str(data)), data)
    a = replace(eve.ADAPTERS[0], folder=folder)
    a.start(ctx)
    a.poll(ctx)
    assert a._session is None and not a._files
    a.stop(ctx)
