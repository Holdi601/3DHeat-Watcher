# Licences and third-party components

Everything in this repository that was written for it is under the MIT licence in [`LICENSE`](LICENSE). Use it, change it,
ship it, commercially or not.

What the MIT licence cannot cover is what the tools are used with: the Python
packages they import, the models game capture runs, and the games they read.
Those carry their own terms, and they are listed here because the answer differs
by part, and the difference decides whether output may be used at work.

Every licence below was read off the package metadata or the model card in
September 2026, not recalled. Where a component's terms changed after that, the
source is what counts, not this file.

---

## Watcher - `watcher/`

### Software

| Package | Licence | Note |
|---|---|---|
| psutil | BSD-3-Clause | Which games are running |
| pyarrow | Apache-2.0 | Writing Parquet |
| numpy | BSD-3-Clause | |
| pytest | MIT | Development only |
| gem-dota | MIT | Optional: Dota 2 replays (`requirements-optional.txt`); github.com/whanyu1212/gem-dota |
| pandas, protobuf, protoc-wheel-0, python-snappy, zstandard | BSD-3-Clause | Optional: what gem-dota brings |
| cramjam, rich | MIT | Optional: what gem-dota brings |

Everything else is the standard library. Each game's interface was written from
its published description - Valve's game-state integration, Riot's Live Client
Data API, Psyonix's Stats API, Codemasters' F1 UDP specification, iRacing's SDK
header, Sector3's `r3e.h`, the SCS telemetry SDK and the RenCloud plugin's
header, SimConnect's documented structures, X-Plane's and IL-2's own UDP
documents, Tacview's ACMI format, Frontier's journal manual, the osu! wiki's
replay format, and the file layouts of Steam and the NVIDIA App as they are on
disk. No code was taken from GPL or unlicensed projects; where such a project
was consulted, only facts about a format were.

Dota 2 replays are decoded by gem-dota, used as a library and not copied; the
watcher's own part reads the entities gem rebuilds (positions, health, which hero
a player's controller is assigned) and writes the table. OpenDota's public API
is asked only for a match's replay server and salt.

The DCS hook (`heat3d-watch.lua`) and the CS2/Dota 2 game-state configuration
files the watcher writes on `setup --apply` are its own, MIT like the rest.

### What it reads

Only what the games hand out, and files on the player's own machine. Reading a
game's memory is limited to single-player games behind the checks in
`docs/watcher.md`, read only, off by default; no profiles ship.

---

## Sources

- [Depth Anything V2 model cards](https://huggingface.co/depth-anything) — licence per size
- [facebook/VGGT-1B](https://huggingface.co/facebook/VGGT-1B) — CC-BY-NC-4.0
- [ReShade — PCGamingWiki](https://www.pcgamingwiki.com/wiki/ReShade) — anti-cheat position
- [ReShade forum, depth buffer detection](https://reshade.me/forum/general-discussion/4083-depth-buffer-detection-modifications?start=1200) — multiplayer depth disabling
- [Reverse engineering and the law](https://ipwatchdog.com/2021/03/27/reverse-engineering-law-understand-restrictions-minimize-risks/) — EULA and DMCA position
- [DMCA §1201 anti-circumvention](https://copyrightalliance.org/education/copyright-law-explained/the-digital-millennium-copyright-act-dmca/section-1201-technology-protection/) — the tools provisions reach technologies, not only acts
- [FModel setup](https://modding.wiki/en/aewff/developers/fmodel) — established extractors require a user-supplied AES key rather than shipping one
- [facebook/VGGT-1B-Commercial](https://huggingface.co/facebook/VGGT-1B-Commercial) — gated; access is granted per account, so it cannot be a default
- [Oodle Data Compression](http://www.radgametools.com/oodle.htm) — proprietary, no redistributable build, hence found rather than bundled
- [Review of Feed-forward 3D Reconstruction: DUSt3R to VGGT](https://arxiv.org/abs/2507.08448)

This document is a record of what the licences say. It is not legal advice, and
the commercial question for any particular use is one for whoever is answerable
for that use.
