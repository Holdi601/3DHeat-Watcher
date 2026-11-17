# Changelog

## 1.0.3

- osu! replays removed: out of scope (2D game).
- Dota 2, League of Legends and VALORANT replays are read by tools of their own, each its own
  project: [3DHeat-Ext-DotaReplay](https://github.com/Holdi601/3DHeat-Ext-DotaReplay)
  (`heat3d-dota-replay`, which brings gem-dota) and [3DHeat-Ext-Riot](https://github.com/Holdi601/3DHeat-Ext-Riot)
  (`heat3d-riot-replays`). The `dota-replays`, `lol-replays` and `valorant-replays` adapters,
  `replays <adapter>` and `dota-replay --convert` run them when they are on PATH, installed, or beside the
  watcher (`HEAT3D_DOTA_REPLAY`, `HEAT3D_RIOT_REPLAYS` name a source folder), and
  record the same sessions as before; without one they say where to get it. The `dota-replay` download and
  the League timeline from Riot's API stay in the watcher. gem-dota leaves the watcher's optional
  requirements ([Replays](docs/commands.md#replays)).
- `dota-map`: the Dota 2 map from your own install as a 3D level for the viewer - ground, cliffs,
  water, trees and buildings in the Dota replay tables' frame. The reader of the game's files lives in
  its own tool, [3DHeat-Ext-Dota](https://github.com/Holdi601/3DHeat-Ext-Dota) (`heat3d-dota-maps`);
  `dota-map` runs it when it is installed and says where to get it when not
  ([Dota 2 map](docs/dota-map.md)).
- Game pages open with a plain sentence, show only their own game's part of a shared module, and list
  the environment variables the adapter reads; `tools/gen_game_pages.py --check` finds stale pages and
  also refreshes the games table of `docs/watcher.md`.
- Documentation: a "Before you start" page for newcomers, a generated command and column reference
  (`tools/gen_docs_reference.py`), the release checklist (`docs/maintaining.md`).
- README: a quick start for new users.

## Docs

Where each feature is documented (<https://holdi601.github.io/3DHeat-Watcher/>):

| Feature | Page |
|---|---|
| Installing, first run | [Before you start](docs/before-you-start.md), [Installing and running](docs/installing-and-running.md) |
| Every game, what it records and how to switch it on | [Games](docs/games.md), a page per game, [All games in one table](docs/watcher.md) |
| Session folders, `events.jsonl`, `heat.parquet`, `meta.json`, `watcher.sqlite`, CSV | [The data](docs/the-data.md) |
| `run`, `games`, `setup`, `status`, `sessions`, `stats`, `table`, `replays`, `dota-replay`, `dota-map`, `update`, `config` | [Commands](docs/commands.md) |
| The Dota 2 map as a 3D level (made by 3DHeat-Ext-Dota) | [Dota 2 map](docs/dota-map.md) |
| Kinds of source, multiplayer rules, declined games | [Sources and rules](docs/sources-and-rules.md) |
| NVIDIA highlights and their positions | [NVIDIA Highlights](docs/nvidia-highlights.md) |
| Arma 3 and Arma Reforger server recorders | [Server recorder mods](docs/server-mods.md) |
| Single-player memory profiles | [Reading memory](docs/memory-reading.md) |
| Release check and self-update | [Updates](docs/updates.md) |
| Writing an adapter, regenerating pages | [Development](docs/development.md) |
| Every option and column, generated | [Reference](docs/cli-reference.md) |
| Release checks for the docs | [Maintaining](docs/maintaining.md) |
