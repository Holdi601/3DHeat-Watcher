
# Updates

The watcher keeps itself current from the releases of
[Holdi601/3DHeat-Watcher](https://github.com/Holdi601/3DHeat-Watcher/releases). The updater is the
`heat3d_update` package next to `heat3d_watch` in the repository.

## The check

- **When**: every command except `update` checks when it starts. `run` also checks while it is running,
  at most once an hour and only while no game is running.
- **How**: one HTTPS request to `https://api.github.com/repos/Holdi601/3DHeat-Watcher/releases/latest`,
  with a timeout of 5 seconds. The answer is cached for six hours in
  `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-Watcher.json`, so most starts ask nothing. "No release
  yet" (HTTP 404) is cached like an answer. Offline, rate-limited or behind a proxy, the check fails
  quietly and the command carries on with the version it has.
- **Versions**: the installed version is the `VERSION` file in the repository folder (`1.0.1` at the
  time of writing). A release's tag (`v1.2.0` or `1.2.0`) is compared as numbers, part by part; anything
  after a `-` or `+` is ignored.
- **Off**: `HEAT3D_NO_UPDATE=1` (any value but empty, `0`, `false` or `no`) switches off both the
  check and the automatic update. Each 3DHeat tool keeps its own cache file, so one tool's answer never
  stands in for another's.

## What happens when a newer release is out

- **`run`** prints a notice when it starts, and keeps running:
  `[heat3d_watch] 3DHeat Watcher 1.2.0 is out (this is 1.0.1). <release page>`. While it runs, with
  `auto_update` on (the default) and no game running, it then updates itself: the log line
  `3DHeat Watcher 1.2.0 is out (this is 1.0.1); updating`, a Windows notification "Updating to 1.2.0",
  the update, every adapter stopped and its sessions closed, and the same command started again on the
  new code. The watcher never updates in the middle of a game. If the update
  cannot be applied, the notification says so ("1.2.0 is out; not updated: ...") and the watcher keeps
  running the old version. With `auto_update` off there is only the notice.
- **Other commands** ask `Update now? [Y/n]` when they run in a terminal. Enter, `y`, `yes`, `j` or
  `ja` updates and then runs the same command again on the new version. Without a terminal (a
  scheduled run, a pipe), they print how to update and carry on.
- **On request**: `python -m heat3d_watch update` (or `python -m heat3d_update`) asks GitHub without
  the cache and updates. `--check` only says whether a newer release is out. This works even with
  `HEAT3D_NO_UPDATE` set.

## How an update is applied

It depends on how the copy was installed:

- **A git clone** (the folder has `.git` and `git` is on the PATH): `git pull --ff-only`. This is refused
  while the clone has changes to tracked files (`git status --porcelain --untracked-files=no` is not
  empty): those changes are someone's work, and an update does not decide what happens to them. Commit
  or stash them, then pull.
- **A downloaded copy**: the release's source archive is downloaded and unpacked into a temporary
  folder. Entries that would land outside it are skipped. The archive's `VERSION` must be the version
  the release claims, or nothing is copied. Then its files are copied over the repository folder.
  Files that are not part of a release - recordings, settings, virtual environments, exports, anything
  you made - are not touched. A Python module that an older release had and the new one dropped is
  removed from the release's own packages (`heat3d_watch`, `heat3d_update`), so no stale adapter
  module is loaded after the update; nothing outside those packages is removed.

Recordings and settings normally live outside the repository folder anyway
(`%LOCALAPPDATA%\3DHeat\Watcher`), so an update never comes near them.

After an update, the same command is started again. On Windows, the watcher starts the new process,
waits for it and passes its exit code on, so the console behaves as if the first process had done the
work.
