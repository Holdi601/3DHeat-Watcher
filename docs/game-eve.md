---
title: "EVE Online (log)"
parent: Games
nav_order: 20
---

# EVE Online (log)

Adapter `eve` - kind [`log`](sources-and-rules.md) - runs while `exefile.exe` is running - looks for new data every 0.5 s.

## What is recorded

- damage dealt and received with the other ship, pilot, corporation ticker, weapon and hit quality
- misses dealt and received
- bounties paid (NPC kills) with ISK
- jumps between systems
- every gamelog and chat log line whole in heat.raw.parquet
- damage dealt and received, hits, misses, bounty kills and ISK, jumps

## Where it comes from

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt and the Chatlogs\\\*.txt beside them (every file written since the client started)

## How to switch it on

Nothing needs switching on: the watcher reads the source as the game or platform provides it.

## How it works

EVE Online: the client's game logs, `Documents\EVE\logs\Gamelogs\*.txt`.

The client writes one file per character per login,
`<yyyymmdd>_<hhmmss>[_<character id>].txt`; logging to file is on by default. Several clients running side by
side each write their own, so every file written since the game started is
followed. Header and lines (EVE time is UTC):

```text
------------------------------------------------------------
  Gamelog
  Listener: Character Name
  Session Started: 2024.07.02 19:41:40
------------------------------------------------------------
[ 2024.07.02 20:31:28 ] (combat) <color=0xff00ffff><b>200</b> <color=0x77ffffff><font size=10>to</font>
    <b><color=0xffffffff>Pilot[TICK](Ship)</b><font size=10><color=0x77ffffff> - Weapon - Penetrates
[ 2024.06.25 15:20:01 ] (combat) <color=0xffcc0000><b>375</b> ... from ... - Weapon - Hits
[ 2024.06.25 15:21:00 ] (bounty) <font size=12><b><color=0xff00aa00>15,000 ISK</b> added to next bounty payout
[ 2024.06.25 15:30:00 ] (None) Jumping from System A to System B
```

(the combat line is one line in the file). Formatting tags are stripped before
matching. The file has been UTF-8 and UTF-16 over the years; both are read.
The format is not documented by CCP; it is the client's plain-text log, read as
community combat-log tools read it (e.g. <https://docs.rs/crate/eve-log-parser>).
No positions.

Beside it, `Documents\EVE\logs\Chatlogs\<channel>_<yyyymmdd>_<hhmmss>[_<id>].txt`:
one file per chat channel per login (when chat logging is on, the client's
default), UTF-16, a header naming the channel and the listener, then
`[ yyyy.mm.dd hh:mm:ss ] Sender > message`.

Every line of both is kept whole in the session's raw sidecar (3DHeat's
converter rule): a gamelog line under its channel in brackets (`combat`,
`notify`, `bounty`, `None`, ...), a chat line as `chat` with its channel, the
header lines as `gamelog header` / `chatlog header`.

## Positions and axes

| | |
|---|---|
| Positions recorded | no |
| Up axis | `y` |
| Units | no positions recorded |
| Mirrored for the viewer | none |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `log`: it reads only what the game or platform hands out (files the game writes while it runs), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Completeness

The watcher follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the source holds is read or kept, never dropped. Besides the rows, every packet, page, line or reply the adapter receives is kept whole in the session's `heat.raw.parquet` (columns `time`, `ms`, `type`, `used`, `payload`, `text`, then any field kept by name; `used` marks what also became rows), and `meta.json`'s `selfCheck.completeness` counts each `type` - `lost` is 0.

**Read**

- gamelog `(combat)` hits dealt and received (amount, other pilot, corporation ticker, ship, weapon, hit quality) and misses both ways
- gamelog `(bounty)` payouts with ISK, and the `Jumping from A to B` lines
- the gamelog header's Listener: whose log it is

**Kept raw**

- every gamelog line whole, `type` = its channel in brackets (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), with `file` and `listener`; `used` where it became a row; the header lines as `gamelog header`
- every chat log line whole (Local, corporation, fleet, private channels, the `EVE System` notices such as a change of Local channel on a jump), `type` `chat`, with `channel`, `listener` and `file`; the header lines as `chatlog header`. Not made into rows yet
- the formatting tags (`<color>`, `<b>`, `<font>`) stay in the raw text; rows have them stripped

**Not available**

- positions: the client writes none to its logs
- other pilots' fights: a gamelog is the listener's own
- logs of earlier logins: each login writes new files; those older than this run of the client are not read again
- chat when the player has switched chat logging off in the client's settings
- the client's own cache and settings files: not logs, and not documented

**Size**: a gamelog is 0.1-2 MB per hour (most in combat); chat logs depend on the channels open - a busy Local or fleet channel 0.5-3 MB per hour; zstd in heat.raw.parquet makes it roughly a tenth

## Verified

tested on synthetic gamelog lines in the format published by community parsers; untested against the game

## Source

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
