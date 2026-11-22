"""The standalone app's description of the watcher, and its loop's updates: announced, applied only when chosen."""

from __future__ import annotations

import json

import pytest

import heat3d_update as up
from heat3d_watch import standalone_spec, watcher
from heat3d_watch.app import entry, update
from heat3d_watch.config import Settings


@pytest.fixture(autouse=True)
def _appdata(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "appdata"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "appdata"))
    monkeypatch.setenv("HEAT3D_LEVELS", str(tmp_path / "levels"))
    monkeypatch.delenv("HEAT3D_AUTO_UPDATE", raising=False)
    update.AUTO_THIS_RUN = False


def test_tasks_and_checks(tmp_path, capsys):
    spec = standalone_spec.SPEC
    assert [t.argv({}, tmp_path) for t in spec.tasks][:3] == [
        ["heat3d-watch", "run"], ["heat3d-watch", "stop"], ["heat3d-watch", "open"]]
    assert entry.main(spec, ["--check", "--json"]) == 0
    assert [c["id"] for c in json.loads(capsys.readouterr().out)["checks"]] == ["data", "replays", "ghpc", "disk"]


def _loop(tmp_path, monkeypatch, *, auto: bool):
    monkeypatch.delenv("HEAT3D_NO_UPDATE", raising=False)
    release = update.Release("9.0.0", "v9.0.0", "- better", "https://example.invalid/r")
    monkeypatch.setattr(update, "latest", lambda target, use_cache=True: release)
    applied, notes = [], []
    monkeypatch.setattr(update, "apply", lambda target, r, **kw: applied.append(r.version) or "updated")
    monkeypatch.setattr(up, "restart", lambda: applied.append("restart"))
    monkeypatch.setattr("heat3d_watch.notify.notify", lambda title, text: notes.append(text))
    if auto:
        update.set_auto("heat3d-watcher", True)
    w = watcher.Watcher.__new__(watcher.Watcher)
    w.settings, w.active, w.adapters, w.last_update_check, w.announced = Settings(data=str(tmp_path / "w")), {}, {}, 0.0, None
    w.maybe_update()
    w.last_update_check = 0.0
    w.maybe_update()  # an hour later: the same release is not announced again
    return applied, notes


def test_the_loop_announces_and_does_not_update_unasked(tmp_path, monkeypatch):
    applied, notes = _loop(tmp_path, monkeypatch, auto=False)
    assert applied == [] and len(notes) == 1 and "9.0.0 is out" in notes[0]


def test_the_loop_updates_when_automatic_updates_were_chosen(tmp_path, monkeypatch):
    applied, notes = _loop(tmp_path, monkeypatch, auto=True)
    assert applied[:2] == ["9.0.0", "restart"]


def test_stop_asks_the_running_watcher_to_end(tmp_path):
    s = Settings(data=str(tmp_path / "w"))
    s.data_dir.mkdir(parents=True)
    (s.data_dir / "watcher.lock").write_text("1", encoding="utf-8")
    from heat3d_watch.cli import cmd_stop

    assert cmd_stop(None, s) == 0 and (s.data_dir / watcher.STOP_FILE).exists()
    w = watcher.Watcher.__new__(watcher.Watcher)
    w.settings = s
    assert w.stop_requested() and not (s.data_dir / watcher.STOP_FILE).exists()
