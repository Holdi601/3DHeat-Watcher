"""Dota 2 replays: the download and the adapter, which runs the external reader - on made-up data.

Reading a replay is heat3d-dota-replay's (exporters/ext/dota-replay), tested there."""

from __future__ import annotations

import bz2
import io
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pyarrow.parquet as pq
import pytest

from heat3d_watch.adapters.base import Context
from heat3d_watch.adapters import replays
from heat3d_watch.adapters.replays import DotaReplays, record_dota_match
from heat3d_watch.config import Settings
from heat3d_watch.decoders import dota_replay as d

DEMO = d.DEMO_MAGIC + b"\x00" * 64


# ------------------------------------------------------------------ download


def _match(**kw):
    return lambda url: {"match_id": 42, **kw}


def test_replay_url_from_cluster_and_salt():
    assert d.replay_url(42, get=_match(cluster=445, replay_salt=1577)) == "http://replay445.valve.net/570/42_1577.dem.bz2"
    assert d.replay_url(42, get=_match(replay_url="http://x/y.dem.bz2")) == "http://x/y.dem.bz2"
    with pytest.raises(LookupError, match="request"):
        d.replay_url(42, get=_match(cluster=445))
    with pytest.raises(LookupError):
        d.replay_url(42, get=lambda url: {"error": "Not Found"})


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


@pytest.mark.parametrize("pack", ["bz2", "zstd", "raw"])
def test_fetch_unpacks_whatever_the_cdn_sends(tmp_path, pack):
    if pack == "bz2":
        body = bz2.compress(DEMO)
    elif pack == "zstd":
        zstandard = pytest.importorskip("zstandard")
        body = zstandard.ZstdCompressor().compress(DEMO)
    else:
        body = DEMO
    asked = []
    out = d.fetch_replay(42, tmp_path, get=_match(cluster=1, replay_salt=2),
                         opener=lambda url: asked.append(url) or _Response(body))
    assert out == tmp_path / "42.dem" and out.read_bytes() == DEMO
    assert asked == ["http://replay1.valve.net/570/42_2.dem.bz2"]
    # Already there: kept, nothing asked.
    assert d.fetch_replay(42, tmp_path, get=lambda url: pytest.fail("asked again")) == out


def test_fetch_refuses_what_is_not_a_demo_and_leaves_nothing(tmp_path):
    with pytest.raises(d.FormatError):
        d.fetch_replay(42, tmp_path, get=_match(cluster=1, replay_salt=2),
                       opener=lambda url: _Response(bz2.compress(b"<html>gone</html>")))
    assert list(tmp_path.iterdir()) == []




# ------------------------------------------------------------------ the adapter


def _summary():
    return {
        "match": "42", "winner": "Dire", "score": {"Radiant": 5, "Dire": 28}, "duration": 1643,
        "players": [
            {"slot": 0, "name": "Ann", "steamid": "76561190000000001", "heroName": "Axe", "team": "Radiant", "kills": 1,
             "deaths": 7, "assists": 0, "lastHits": 150, "netWorth": 11781, "goldPerMin": 430, "won": False},
            {"slot": 5, "name": "Bob", "steamid": "76561190000000002", "heroName": "Lina", "team": "Dire", "kills": 6},
        ],
    }


def test_the_signed_in_players_line_becomes_the_statistics(tmp_path):
    stats, meta = {}, {}
    session = SimpleNamespace(meta=meta, stat=lambda k, v: stats.__setitem__(k, v))
    check = {"completeness": {"lost": 0, "types": {}}}
    record_dota_match(session, {**_summary(), "selfCheck": check}, {"76561190000000001"})
    assert stats["kills"] == 1 and stats["deaths"] == 7 and stats["net_worth"] == 11781 and stats["gpm"] == 430
    assert meta["selfCheck"] == check
    assert stats["hero"] == "Axe" and stats["won"] == 0 and stats["score.Dire"] == 28 and stats["duration"] == 1643
    assert meta["player"] == "Ann" and meta["match"]["winner"] == "Dire"


def test_adapter_converts_in_a_process_of_its_own(tmp_path, monkeypatch):
    replay = tmp_path / "replays" / "42.dem"
    replay.parent.mkdir()
    replay.write_bytes(DEMO)
    calls = []

    def run(cmd, **kw):
        calls.append(cmd)
        out = Path(cmd[cmd.index("-o") + 1])
        out.mkdir(parents=True)
        (out / "42.match.json").write_text(json.dumps(_summary()), encoding="utf-8")
        import pyarrow as pa

        pq.write_table(pa.table({"event": ["position", "position", "death", "kill"]}), out / "42.parquet")
        # The side tables, which sort before the match's own: not counted.
        pq.write_table(pa.table({"tick": [1, 2, 3]}), out / "42.combatlog.parquet")
        pq.write_table(pa.table({"unit": ["a"]}), out / "42.units.parquet")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("heat3d_watch.adapters.replays.subprocess.run", run)
    monkeypatch.setattr("heat3d_watch.adapters.replays.signed_in_steam_ids", lambda: {"76561190000000002"})
    monkeypatch.setattr(replays.DOTA_REPLAY, "command_line", lambda: ["heat3d-dota-replay"])
    a = DotaReplays(id="dota-replays", game="Dota 2", patterns=("*.dem",))
    ctx = Context(Settings(data=str(tmp_path / "data")), tmp_path / "data")
    a.convert(replay, ctx)
    # The external reader, with absolute paths: the replay, and the session's dota folder.
    assert calls and calls[0][:2] == ["heat3d-dota-replay", "convert"]
    assert Path(calls[0][2]) == replay.resolve() and Path(calls[0][4]).is_absolute()
    folders = list((tmp_path / "data" / "sessions").glob("*/*"))
    assert len(folders) == 1
    meta = json.loads((folders[0] / "meta.json").read_text(encoding="utf-8"))
    assert meta["stats"]["kills"] == 6 and meta["stats"]["won"] == 1
    assert meta["events"]["death"] == 1 and meta["positions"] == 4


def test_adapter_looks_in_the_dota_install(tmp_path, monkeypatch):
    common = tmp_path / "steamapps" / "common"
    (common / "dota 2 beta" / "game" / "dota").mkdir(parents=True)
    monkeypatch.setattr("heat3d_watch.adapters.replays.steam_libraries", lambda: [common])
    a = DotaReplays(id="dota-replays", game="Dota 2", patterns=("*.dem",))
    ctx = Context(Settings(data=str(tmp_path / "data")), tmp_path / "data")
    assert a.folders(ctx) == [common / "dota 2 beta" / "game" / "dota" / "replays"]


def test_dota_replay_command_downloads_where_asked(tmp_path, monkeypatch, capsys):
    from heat3d_watch import cli

    got = []

    def fetch(match_id, folder):
        got.append((match_id, Path(folder)))
        return Path(folder) / f"{match_id}.dem"

    monkeypatch.setattr("heat3d_watch.decoders.dota_replay.fetch_replay", fetch)
    assert cli.main(["dota-replay", "42", "43", "-o", str(tmp_path)]) == 0
    assert got == [(42, tmp_path), (43, tmp_path)]
    assert "43.dem" in capsys.readouterr().out


def test_without_the_reader_it_says_where_to_get_it(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(replays.DOTA_REPLAY, "command_line", lambda: None)
    a = DotaReplays(id="dota-replays", game="Dota 2", patterns=("*.dem",))
    assert "3DHeat-Ext-DotaReplay" in a.missing() and "heat3d-dota-replay" in a.missing()
    replay = tmp_path / "42.dem"
    replay.write_bytes(DEMO)
    with pytest.raises(FileNotFoundError, match="pip install -e"):
        a.convert(replay, Context(Settings(data=str(tmp_path / "data")), tmp_path / "data"))
    assert not (tmp_path / "data" / "sessions").exists()
    # `dota-replay --convert` says what to install before downloading anything.
    from heat3d_watch import cli

    monkeypatch.setattr("heat3d_watch.decoders.dota_replay.fetch_replay", lambda *a: pytest.fail("downloaded"))
    monkeypatch.setattr(cli, "load", lambda: {"dota-replays": a})
    assert cli.main(["dota-replay", "42", "-o", str(tmp_path), "--convert"]) == 1
    assert "3DHeat-Ext-DotaReplay" in capsys.readouterr().err


def test_the_reader_is_run_from_its_folder_beside_the_watcher(tmp_path, monkeypatch):
    """Not installed: `python -m heat3d_ext_dota_replay` with its folder on PYTHONPATH, and gem-dota asked for."""
    folder = tmp_path / "ext" / "dota-replay"
    (folder / "heat3d_ext_dota_replay").mkdir(parents=True)
    (folder / "heat3d_ext_dota_replay" / "__init__.py").write_text("")
    monkeypatch.setattr(replays, "ROOT", tmp_path / "watcher")
    monkeypatch.setattr("shutil.which", lambda name: None)
    monkeypatch.delenv("HEAT3D_DOTA_REPLAY", raising=False)
    assert replays.DOTA_REPLAY.command_line() == [sys.executable, "-m", "heat3d_ext_dota_replay"]
    seen = {}
    monkeypatch.setattr(replays.subprocess, "run", lambda cmd, **kw: seen.update(cmd=cmd, **kw))
    replays.DOTA_REPLAY.run(["list"])
    assert seen["env"]["PYTHONPATH"].split(";" if sys.platform == "win32" else ":")[0] == str(folder)
    assert "cwd" not in seen and seen["env"]["HEAT3D_NO_UPDATE"] == "1"
    monkeypatch.setattr("importlib.util.find_spec", lambda name: None if name == "gem" else object())
    assert "gem-dota" in DotaReplays(id="dota-replays", game="Dota 2", patterns=("*.dem",)).missing()
