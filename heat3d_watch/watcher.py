"""
The background loop: which games are running, and an adapter running for each.

Every few seconds the process list is read (names and paths only - nothing is
opened). An adapter whose game appeared is started in a thread of its own, one
whose game is gone is stopped, and its sessions are closed and counted. The
always-on adapters - platform statistics, highlights, replay folders - run the
whole time. A failing adapter is logged and retried later; it never takes the
others with it.

While no game is running the loop also looks for a newer release (with
`auto_update` on) and announces it once. It installs it and starts itself
again only when the user chose automatic updates (`--auto-update`, the
window's "Update automatically", `HEAT3D_AUTO_UPDATE=1`), so the watcher never
updates unasked and never interrupts a game to update. A `watcher.stop` file
in the data folder (`heat3d_watch stop`) ends the loop cleanly.
"""

from __future__ import annotations

import logging
import os
import sys
import threading
import time
from pathlib import Path

from .adapters import Adapter, Context, load
from .config import Settings

log = logging.getLogger("heat3d_watch")

#: Consecutive failing polls before an adapter is stopped until its game starts again.
MAX_FAILURES = 20
#: Left in the data folder by `heat3d_watch stop`: the running watcher ends cleanly at its next look.
STOP_FILE = "watcher.stop"


def running_processes() -> dict[str, tuple[int, Path | None]]:
    """Lower-case executable name -> (pid, full path). Names and paths only."""
    import psutil

    out: dict[str, tuple[int, Path | None]] = {}
    for p in psutil.process_iter(["pid", "name", "exe"]):
        name = (p.info.get("name") or "").lower()
        if not name:
            continue
        exe = p.info.get("exe")
        out.setdefault(name, (p.info["pid"], Path(exe) if exe else None))
    return out


class Runner(threading.Thread):
    """One adapter, polled in its own thread until told to stop."""

    def __init__(self, adapter: Adapter, ctx: Context):
        super().__init__(name=f"watch-{adapter.id}", daemon=True)
        self.adapter = adapter
        self.ctx = ctx
        self.halt = threading.Event()
        #: Set once the adapter has been started and polled once (or could not start).
        self.looked = threading.Event()
        self.failed = False

    def run(self) -> None:
        a = self.adapter
        try:
            a.start(self.ctx)
        except Exception:  # noqa: BLE001
            log.exception("%s: could not start", a.id)
            self.failed = True
            self.looked.set()
            return
        failures = 0
        while not self.halt.is_set():
            try:
                a.poll(self.ctx)
                failures = 0
            except Exception:  # noqa: BLE001
                failures += 1
                log.exception("%s: poll failed (%d)", a.id, failures)
                self.looked.set()
                if failures >= MAX_FAILURES:
                    self.failed = True
                    break
                self.halt.wait(min(5.0, a.interval * 10 + 0.5))
                continue
            self.looked.set()
            self.halt.wait(a.interval)
        try:
            a.stop(self.ctx)
        except Exception:  # noqa: BLE001
            log.exception("%s: could not stop cleanly", a.id)

    def stop(self, wait: float = 10.0) -> None:
        self.halt.set()
        self.join(wait)


class Watcher:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.adapters = load()
        self.active: dict[str, Runner] = {}
        #: Adapters that gave up, by id -> the pid they gave up on, so they are not restarted at once.
        self.benched: dict[str, int | None] = {}
        self.last_update_check = 0.0
        #: The release last announced, so a newer one is announced once, not every hour.
        self.announced: str | None = None

    def wanted(self, procs: dict[str, tuple[int, Path | None]]) -> dict[str, Context]:
        """Adapters that should be running now, with the context each is started with."""
        from .safety import memory_allowed

        s = self.settings
        out: dict[str, Context] = {}
        for a in self.adapters.values():
            if a.id in s.disabled or a.missing():
                continue
            if a.kind == "replay" and not s.replays:
                continue
            if a.kind == "memory" and not s.memory:
                continue
            if a.always:
                out[a.id] = Context(s, s.data_dir)
                continue
            hit = next((procs[e.lower()] for e in a.exes if e.lower() in procs), None)
            if hit is None:
                continue
            pid, exe = hit
            if a.kind == "memory":
                verdict = memory_allowed(a, pid, exe)
                if verdict:
                    log.info("%s: not reading memory: %s", a.id, verdict)
                    continue
            out[a.id] = Context(s, s.data_dir, pid=pid, exe=exe)
        return out

    def step(self) -> None:
        procs = running_processes()
        want = self.wanted(procs)
        for aid, runner in list(self.active.items()):
            if aid not in want or not runner.is_alive():
                if runner.is_alive():
                    log.info("%s: stopping", aid)
                runner.stop()
                if runner.failed:
                    self.benched[aid] = runner.ctx.pid
                del self.active[aid]
        for aid, ctx in want.items():
            if aid in self.active:
                continue
            if aid in self.benched and self.benched[aid] == ctx.pid:
                continue
            self.benched.pop(aid, None)
            log.info("%s: starting (%s)", aid, self.adapters[aid].game)
            r = Runner(self.adapters[aid], ctx)
            self.active[aid] = r
            r.start()

    def games_running(self) -> bool:
        return any(not self.adapters[a].always for a in self.active)

    def maybe_update(self) -> None:
        """
        A newer release, while no game is running: announced once; installed
        (and the watcher started again) only when automatic updates were chosen.
        """
        if not self.settings.auto_update or self.games_running():
            return
        if time.time() - self.last_update_check < 3600:
            return
        self.last_update_check = time.time()
        try:
            import heat3d_update as up

            from .app import update as app_update
        except ImportError:
            return
        target = up.target()
        try:
            release = app_update.available(target)
        except Exception:  # noqa: BLE001 - an update check never stops the watcher
            return
        if release is None:
            return
        from .notify import notify

        if not app_update.auto_enabled(target.tool_id) or (app_update.managed() and app_update.frozen()):
            if self.announced != release.version:
                self.announced = release.version
                log.info("%s", app_update.notice(target, release))
                log.info("update with `heat3d_watch update` or from the window; automatic updates are off")
                notify("3DHeat Watcher", f"{release.version} is out (this is {target.version}); "
                                         "update it from its window or with `update`")
            return
        log.info("3DHeat Watcher %s is out (this is %s); updating (automatic updates are on)",
                 release.version, target.version)
        notify("3DHeat Watcher", f"Updating to {release.version}")
        windows_frozen = app_update.frozen() and os.name == "nt"
        try:
            # A frozen copy on Windows is swapped by a script once this process has ended.
            log.info(app_update.apply(target, release, restart_args=sys.argv[1:] if windows_frozen else None,
                                      log=log.info))
        except RuntimeError as e:
            log.warning("update not applied: %s", e)
            notify("3DHeat Watcher", f"{release.version} is out; not updated: {e}")
            return
        self.shutdown()
        if windows_frozen:
            os._exit(0)
        if app_update.frozen():
            os.execv(sys.executable, [sys.executable, *sys.argv[1:]])
        up.restart()

    def stop_requested(self) -> bool:
        """`heat3d_watch stop` left a stop file: take it away and end the loop."""
        f = self.settings.data_dir / STOP_FILE
        if not f.exists():
            return False
        try:
            f.unlink()
        except OSError:
            pass
        log.info("asked to stop")
        return True

    def run(self, *, once: bool = False, look: float = 10.0) -> None:
        """
        Watch until stopped. `once`: start the adapters for the games running
        now, let each take one look (at most `look` seconds), then stop them
        the way a game ending would - their sessions closed and counted.
        """
        log.info("watching; data in %s", self.settings.data_dir)
        self.recover()
        try:
            while True:
                self.step()
                if once:
                    deadline = time.monotonic() + look
                    for runner in list(self.active.values()):
                        runner.looked.wait(max(0.0, deadline - time.monotonic()))
                    break
                if self.stop_requested():
                    break
                self.maybe_update()
                time.sleep(self.settings.scan_seconds)
        finally:
            self.shutdown()

    def recover(self) -> None:
        """Finish the sessions a watcher that was killed left open."""
        from . import db
        from .session import recover

        finished = recover(self.settings.data_dir)
        if not finished:
            return
        con = db.connect(self.settings.data_dir)
        try:
            for s in finished:
                db.record(con, s)
        finally:
            con.close()
        log.info("finished %d session(s) left open by an earlier run", len(finished))

    def shutdown(self) -> None:
        for runner in self.active.values():
            runner.stop()
        self.active.clear()
