"""
Dota 2 replays (.dem): every hero's track, who played it, and what happened where.

Dota 2 keeps a replay of every public match on Valve's servers for a few weeks.
The client saves the ones a player downloads (Watch > Replays, or a match's
"Download replay") to `<Dota>/game/dota/replays/<match id>.dem`; anyone can
fetch one from Valve's replay CDN with the match's cluster and replay salt, which
OpenDota's API gives for a match id (`fetch_replay`). Replays are not encrypted;
OpenDota, Stratz and Dotabuff have read them for a decade.

Reading
-------
A .dem is a Source 2 demo: Snappy-compressed protobuf packets, 30 ticks a
second, with every networked entity's state as field deltas. Decoding that is a
parser's job; this module uses gem (github.com/whanyu1212/gem-dota, MIT, pure
Python, `pip install gem-dota`), and only asks it for facts:

* `gem.parse` for the match: players, heroes, teams, the score, the combat log
  (kills and deaths, with no position in the log itself), towers, barracks,
  Roshan, wards with where they were placed;
* a sampler of our own, hooked to the same parse, for the heroes' positions,
  height and health at `HZ` per second (gem's own track is once a second).

Coordinates
-----------
Dota's world is Source 2's: X east, Y north, Z up, in Hammer units (a hero is
about 48 across; the playable map runs about -8200..8200 on both axes). An
entity's position is sent as a 128-unit cell plus an offset in it; the cells
start 16384 units below the world origin, so `world = cell * 128 + offset - 16384`.
gem leaves out the 16384 (its positions are OpenDota's), so they are moved back
here. Game-state integration reports the same world X/Y, so a replay and a live
session land on the same map.

Events are placed where they happened: a death at the dying hero's last sampled
position, a kill where the killer stood (as in the CS2 tables), a tower or
barracks kill at the building, a Roshan kill where Roshan was, a Tormentor kill
where its killer stood, a ward where it was planted. Every row has a `life`:
a hero's lives counted from 1, so a track ends where the hero died instead of
running on to the fountain it respawned at.

Besides positions, each hero sample carries the hero's state - facing, mana,
experience, attributes, armour, speed, damage, the items it carries - and its
player's cursor. Every other unit (creeps, summons, illusions, couriers,
wards, buildings, Roshan) is sampled once a second into a table of its own,
`<match>.units.parquet`. The combat log's entries about a hero become rows
too (damage taken and dealt, heals, abilities, items, purchases, runes, gold,
experience, modifiers), and the whole log, every field, is in the summary,
as columns. So is everything else gem extracts: the draft, chat, runes,
couriers, smokes, neutral items, fights, visibility, per-player time series
and logs, the gold and experience advantage.

Not read: what gem does not extract (projectiles, the minimap's pings,
abilities' cooldowns over time beyond gem's snapshots), and units between
their once-a-second samples. A replay gem cannot read to the end is
converted as far as it goes and marked `incomplete` in the summary.
"""

from __future__ import annotations

import bz2
import json
import math
import threading
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

#: Ticks a second in a Dota 2 replay.
TICK_RATE = 30
#: Samples a second per hero: every fourth tick.
HZ = 7.5
#: Where the 128-unit cells start, below the world origin.
CELL_ORIGIN = 16384.0
CELL_SIZE = 128.0
#: A Source 2 demo's first eight bytes.
DEMO_MAGIC = b"PBDEMS2\0"
OPENDOTA = "https://api.opendota.com/api"
RADIANT, DIRE = 2, 3
TEAMS = {RADIANT: "Radiant", DIRE: "Dire"}
#: One parse at a time may swap gem's parser class (see `_parse_with_sampler`).
_PATCH = threading.Lock()


class FormatError(ValueError):
    """The file is not a Dota 2 replay this reader understands."""


class Missing(RuntimeError):
    """The parser this reader works through is not installed."""


# ------------------------------------------------------------------ downloading


def _get_json(url: str, timeout: float = 30.0) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "heat3d-watch"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def replay_url(match_id: int, *, api: str = OPENDOTA, get: Callable[[str], Any] = _get_json) -> str:
    """
    Where Valve keeps a match's replay: `http://replay<cluster>.valve.net/570/<id>_<salt>.dem.bz2`,
    with the cluster and salt from OpenDota's `/matches/<id>`.
    """
    data = get(f"{api}/matches/{int(match_id)}")
    if not isinstance(data, dict) or data.get("error"):
        raise LookupError(f"OpenDota does not know match {match_id}: {data.get('error') if isinstance(data, dict) else data}")
    if data.get("replay_url"):
        return str(data["replay_url"])
    cluster, salt = data.get("cluster"), data.get("replay_salt")
    if not cluster or not salt:
        raise LookupError(
            f"OpenDota has no replay salt for match {match_id} yet; ask it to fetch the match with "
            f"`curl -X POST {api}/request/{int(match_id)}` and try again in a few minutes"
        )
    return f"http://replay{int(cluster)}.valve.net/570/{int(match_id)}_{int(salt)}.dem.bz2"


class _Raw:
    """A replay served uncompressed: written as it comes."""

    eof = None

    @staticmethod
    def decompress(chunk: bytes) -> bytes:
        return chunk


def _decompressor(head: bytes, url: str) -> Any:
    """
    The replay's compression, from its first bytes rather than its name: the
    CDN's files are all called `.dem.bz2`, but newer ones are Zstandard.
    """
    if head.startswith(b"BZh"):
        return bz2.BZ2Decompressor()
    if head.startswith(b"\x28\xb5\x2f\xfd"):
        try:
            import zstandard
        except ImportError as e:
            raise Missing("this replay is Zstandard-compressed: pip install zstandard (gem-dota brings it)") from e
        return zstandard.ZstdDecompressor().decompressobj()
    if head.startswith(DEMO_MAGIC):
        return _Raw()
    raise FormatError(f"{url} is neither a demo nor a compressed one (starts {head[:8].hex()})")


def fetch_replay(
    match_id: int,
    folder: str | Path,
    *,
    api: str = OPENDOTA,
    get: Callable[[str], Any] = _get_json,
    opener: Callable[[str], Any] | None = None,
    progress: Callable[[int], None] | None = None,
) -> Path:
    """
    A public match's replay into `folder` as `<match id>.dem`, decompressed as it
    downloads. An existing file is kept. Valve deletes replays after some weeks;
    a match older than that is gone (the CDN answers 404).
    """
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    out = folder / f"{int(match_id)}.dem"
    if out.is_file() and out.stat().st_size > 0:
        return out
    url = replay_url(match_id, api=api, get=get)
    part = out.with_suffix(".dem.part")
    open_url = opener or (lambda u: urllib.request.urlopen(
        urllib.request.Request(u, headers={"User-Agent": "heat3d-watch"}), timeout=60))
    try:
        r = open_url(url)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise LookupError(f"Valve no longer has the replay of match {match_id} ({url})") from e
        raise
    got = 0
    try:
        with r, part.open("wb") as f:
            chunk = r.read(1 << 20)
            unpack = _decompressor(chunk[:8], url)
            while chunk:
                got += len(chunk)
                f.write(unpack.decompress(chunk))
                if progress:
                    progress(got)
                chunk = r.read(1 << 20)
            if hasattr(unpack, "flush"):
                f.write(unpack.flush())
        if getattr(unpack, "eof", True) is False:
            raise OSError(f"the download of {url} stopped early")
        with part.open("rb") as f:
            if f.read(8) != DEMO_MAGIC:
                raise FormatError(f"{url} is not a Source 2 demo")
        part.replace(out)
    finally:
        if part.exists():
            part.unlink()
    return out


# ------------------------------------------------------------------ what a replay holds


@dataclass
class Sample:
    """One hero at one moment, alive."""

    tick: int
    time: float
    slot: int
    x: float
    y: float
    z: float
    health: int | None = None
    max_health: int | None = None
    level: int | None = None
    #: The rest of the hero's state, by column name (see `HERO_FIELDS`).
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Event:
    """
    Something that happened. `slot` is the player it belongs to (-1: none, as a
    creep's tower kill); without x/y it is placed at that player's position
    then (see `place`).
    """

    tick: int
    time: float
    event: str
    slot: int = -1
    x: float | None = None
    y: float | None = None
    z: float | None = None
    #: The other side of it: who a death was by, who a kill was of, the tower, the ward's type.
    other: str = ""
    #: A number and a text the event has: damage, gold, an ability's level; the ability, item or chat line.
    value: float | None = None
    text: str = ""


@dataclass
class Replay:
    """What the conversion keeps of one match. `players` are dicts; see `_player`."""

    match_id: int
    players: list[dict[str, Any]]
    samples: list[Sample]
    events: list[Event]
    info: dict[str, Any] = field(default_factory=dict)
    hz: float = HZ
    #: Every other unit once a second: see `_Sampler.units`.
    units: list[tuple] = field(default_factory=list)
    #: Everything else gem extracted, as JSON.
    more: dict[str, Any] = field(default_factory=dict)
    #: The whole combat log, as columns (see `combat_columns`).
    combat_log: dict[str, list[Any]] = field(default_factory=dict)


def world(cell: float, offset: float) -> float:
    """A position as sent - cell and offset - in world units."""
    return cell * CELL_SIZE + offset - CELL_ORIGIN


def hero_display(npc: str) -> str:
    """`npc_dota_hero_dragon_knight` as people say it: gem's table, else the name tidied."""
    try:
        from gem.constants import hero_display as display

        name = display(npc)
        if name and name != npc:
            return name
    except Exception:  # noqa: BLE001 - only the spelling is at stake
        pass
    return npc.removeprefix("npc_dota_hero_").replace("_", " ").title()


# ------------------------------------------------------------------ reading, through gem


#: A hero's state besides its place, health and level: the entity's field -> the table's column.
HERO_FIELDS = {
    "m_flMana": "mana",
    "m_flMaxMana": "maxMana",
    "m_iCurrentXP": "xp",
    "m_flStrengthTotal": "strength",
    "m_flAgilityTotal": "agility",
    "m_flIntellectTotal": "intellect",
    "m_flPhysicalArmorValue": "armor",
    "m_flMagicalResistanceValue": "magicResist",
    "m_iMoveSpeed": "moveSpeed",
    "m_iDamageMin": "damageMin",
    "m_iDamageMax": "damageMax",
    "m_iAttackRange": "attackRange",
    "m_flHealthThinkRegen": "healthRegen",
    "m_flManaThinkRegen": "manaRegen",
    "m_bIsMoving": "moving",
    "m_iAbilityPoints": "abilityPoints",
    "m_iRecentDamage": "recentDamage",
}
#: How many item slots a hero has: six, three in the backpack, the stash, the teleport and the neutral slot.
ITEM_SLOTS = 19
#: Units sampled once a second into their own table: every NPC class but the players' own heroes.
UNIT_PREFIXES = ("CDOTA_BaseNPC", "CDOTA_Unit_", "CDOTA_NPC_")


class _Sampler:
    """
    Every hero's position, height, health and level every `step` ticks, read
    off the entities the parse rebuilds. A player's hero is the one their
    controller is assigned (`m_hAssignedHero`), so illusions and clones, which
    share the hero's class, are never taken for it. A dead hero is not sampled.

    Also keeps where each tower, barracks and ancient stands, and where Roshan
    is (he moves between two pits), for placing their deaths.
    """

    STRUCTURES = ("CDOTA_BaseNPC_Tower", "CDOTA_BaseNPC_Barracks", "CDOTA_BaseNPC_Fort", "CDOTA_Unit_Roshan")

    def __init__(self, parser: Any, step: int) -> None:
        self.p = parser
        self.step = step
        self.last = -(10**9)
        self.controllers: dict[int, Any] = {}
        self.raw: list[tuple] = []
        self.structures: dict[str, tuple[float, float, float]] = {}
        self.roshan: list[tuple[int, float, float, float]] = []
        self._roshan_entity: Any = None
        #: Each hero sample's further state, parallel to `raw`.
        self.extra: list[dict[str, Any]] = []
        #: Every other unit once a second: tick, entity index, class, name, team, x, y, z, health, max health,
        #: facing, the player that owns it (-1 none).
        self.units: list[tuple] = []
        self._live: dict[int, Any] = {}
        self._last_unit = -(10**9)
        self._item_names: dict[int, str] = {}
        names = ("CDOTAPlayerController", *self.STRUCTURES)
        hook = getattr(parser, "_on_entity_filtered", None)
        if callable(hook):
            hook(self._entity, class_names=names)
            hook(self._unit, class_prefixes=UNIT_PREFIXES)
        else:  # a gem without the filtered hook: every entity, filtered here
            parser.on_entity(lambda e, op: self._entity(e, op) if e.get_class_name() in names else None)
            parser.on_entity(lambda e, op: self._unit(e, op) if e.get_class_name().startswith(UNIT_PREFIXES) else None)
        parser.on_tick_start(self._tick)

    def _unit(self, e: Any, op: Any) -> None:
        if int(op) & 0x04:
            self._live.pop(e.get_index(), None)
        else:
            self._live[e.get_index()] = e

    def _items(self, hero: Any, manager: Any) -> str:
        """The items a hero carries, by slot, `|`-separated (an empty slot empty)."""
        out = []
        for i in range(ITEM_SLOTS):
            h = hero.get(f"m_hItems.{i:04d}")
            if h is None or h == 0xFFFFFF:
                out.append("")
                continue
            name = self._item_names.get(h)
            if name is None:
                item = manager.find_by_handle(h)
                name = (self._name(item) or item.get_class_name().removeprefix("CDOTA_Item_")) if item is not None else ""
                if name:
                    self._item_names[h] = name
            out.append(name or "")
        while out and not out[-1]:
            out.pop()
        return "|".join(out)

    def _state(self, hero: Any, controller: Any, manager: Any) -> dict[str, Any]:
        state = {column: hero.get(name) for name, column in HERO_FIELDS.items()}
        angles = hero.get("CBodyComponent.m_angRotation")
        state["yaw"] = float(angles[1]) if isinstance(angles, (list, tuple)) and len(angles) > 1 else None
        state["items"] = self._items(hero, manager)
        state["cursorX"] = controller.get("m_iCursor.0000")
        state["cursorY"] = controller.get("m_iCursor.0001")
        return state

    @staticmethod
    def _pos(e: Any) -> tuple[float, float, float] | None:
        cx, cy, cz = e.get("CBodyComponent.m_cellX"), e.get("CBodyComponent.m_cellY"), e.get("CBodyComponent.m_cellZ")
        vx, vy, vz = e.get("CBodyComponent.m_vecX"), e.get("CBodyComponent.m_vecY"), e.get("CBodyComponent.m_vecZ")
        if None in (cx, cy, vx, vy):
            return None
        return world(cx, vx), world(cy, vy), world(cz, vz) if cz is not None and vz is not None else 0.0

    def _name(self, e: Any) -> str | None:
        tables = getattr(self.p, "string_tables", None)
        table = tables.get_by_name("EntityNames") if tables is not None else None
        idx = e.get("m_pEntity.m_nameStringTableIndex")
        if table is None or idx is None or idx < 0:
            return None
        item = table.items.get(idx)
        return item[0] if item else None

    def _entity(self, e: Any, op: Any) -> None:
        cls = e.get_class_name()
        deleted = bool(int(op) & 0x04)
        if cls == "CDOTAPlayerController":
            if deleted:
                self.controllers.pop(e.get_index(), None)
            else:
                self.controllers[e.get_index()] = e
        elif cls == "CDOTA_Unit_Roshan":
            self._roshan_entity = None if deleted else e
        elif not deleted:
            name = _short(self._name(e) or "")
            if name and name not in self.structures:
                pos = self._pos(e)
                if pos:
                    self.structures[name] = pos

    def _tick(self, _net_tick: int) -> None:
        tick = self.p.tick
        if tick - self.last < self.step:
            return
        self.last = tick
        manager = getattr(self.p, "entity_manager", None)
        if manager is None:
            return
        for c in list(self.controllers.values()):
            slot, handle = c.get("m_nPlayerID"), c.get("m_hAssignedHero")
            if slot is None or not 0 <= slot <= 23 or handle is None or handle == 0xFFFFFF:
                continue
            hero = manager.find_by_handle(handle)
            if hero is None or hero.get("m_lifeState") not in (0, None):
                continue
            pos = self._pos(hero)
            if pos is None:
                continue
            self.raw.append((tick, slot, *pos, hero.get("m_iHealth"), hero.get("m_iMaxHealth"), hero.get("m_iCurrentLevel")))
            self.extra.append(self._state(hero, c, manager))
        if tick - self._last_unit >= 30:
            self._last_unit = tick
            heroes = {c.get("m_hAssignedHero") for c in self.controllers.values()}
            mine = {manager.find_by_handle(h) for h in heroes if h not in (None, 0xFFFFFF)}
            for index, u in list(self._live.items()):
                if u in mine or u.get("m_lifeState") not in (0, None):
                    continue
                pos = self._pos(u)
                if pos is None:
                    continue
                angles = u.get("CBodyComponent.m_angRotation")
                yaw = float(angles[1]) if isinstance(angles, (list, tuple)) and len(angles) > 1 else None
                owner = u.get("m_nPlayerOwnerID")
                self.units.append((tick, index, u.get_class_name(), self._name(u) or "", u.get("m_iTeamNum"), *pos,
                                   u.get("m_iHealth"), u.get("m_iMaxHealth"), yaw,
                                   owner if isinstance(owner, int) else -1))
        r = self._roshan_entity
        if r is not None and r.get("m_lifeState") in (0, None):
            pos = self._pos(r)
            if pos is not None:
                self.roshan.append((tick, *pos))


def _parse_with_sampler(path: Path, step: int) -> tuple[Any, _Sampler | None]:
    """
    `gem.parse`, with our sampler on the same pass: gem builds its parser from
    `gem.parser.ReplayParser`, so for the call that name is a subclass that
    attaches the sampler. Should a later gem build its parser elsewhere, the
    sampler simply sees nothing and `read` falls back to gem's own
    once-a-second track.
    """
    import gem
    import gem.parser as gp

    holder: list[_Sampler] = []
    base = gp.ReplayParser

    class Sampling(base):  # type: ignore[misc, valid-type]
        def __init__(self, source: Any) -> None:
            super().__init__(source)
            holder.append(_Sampler(self, step))

    with _PATCH:
        gp.ReplayParser = Sampling
        try:
            match = gem.parse(str(path))
        finally:
            gp.ReplayParser = base
    return match, holder[0] if holder else None


def read(path: str | Path, hz: float = HZ) -> Replay:
    """A replay file, read: heroes' tracks at `hz`, the match, and its events in place."""
    path = Path(path)
    with path.open("rb") as f:
        if f.read(8) != DEMO_MAGIC:
            raise FormatError(f"{path.name} is not a Source 2 demo (a .dem.bz2 must be unpacked first)")
    try:
        import gem  # noqa: F401
    except ImportError as e:
        raise Missing("pip install gem-dota (the Dota 2 replay parser, MIT)") from e
    step = max(1, round(TICK_RATE / hz))
    match, sampler = _parse_with_sampler(path, step)
    clock = getattr(match, "game_clock", None)

    def at(tick: int) -> float:
        t = clock.game_time_at(tick) if clock is not None else None
        return t if t is not None else (tick - (match.game_start_tick or 0)) / TICK_RATE

    end = getattr(match, "post_game_tick", None) or getattr(match, "game_end_tick", None)
    raw: list[tuple] = sampler.raw if sampler is not None else []
    if raw and sampler is not None and len(sampler.extra) == len(raw):
        raw = [(*r, x) for r, x in zip(raw, sampler.extra)]
    if raw:
        hz = TICK_RATE / step
    else:
        # gem's own track: once a second, no height or health.
        hz = 1.0
        raw = sorted(
            (tick, p.player_id, x - CELL_ORIGIN, y - CELL_ORIGIN, 0.0, None, None, None)
            for p in match.players for tick, x, y in p.position_log
        )
    samples = tracks(raw, at, end)
    players = [_player(p) for p in match.players]
    by_hero = {p.hero_name: p.player_id for p in match.players if p.hero_name}
    events = _events(match, by_hero, at, sampler)
    events += _more_events(match, by_hero, at)
    events.sort(key=lambda e: (e.tick, e.event))
    units = [(u[0], round(at(u[0]), 3), *u[1:]) for u in (sampler.units if sampler is not None else [])
             if end is None or u[0] <= end]
    replay = Replay(match_id=int(match.match_id or _id_from_name(path)), players=players, samples=samples,
                    events=events, info=_info(match, path), hz=hz, units=units, more=_more(match, at))
    replay.combat_log = combat_columns(list(getattr(match, "combat_log", [])), at)
    return replay


def tracks(raw: list[tuple], at: Callable[[int], float], end: int | None = None) -> list[Sample]:
    """
    The sampler's rows as samples on the game clock, up to `end` (the ancient's
    fall). While the game is paused the clock stands and so does everyone, so
    a row whose time is not past its hero's last is dropped.
    """
    out: list[Sample] = []
    last: dict[int, float] = {}
    for tick, slot, x, y, z, hp, mhp, lvl, *rest in raw:
        if end is not None and tick > end:
            break
        t = at(tick)
        if t <= last.get(slot, -math.inf):
            continue
        last[slot] = t
        out.append(Sample(tick, round(t, 3), slot, x, y, z, hp, mhp, lvl, rest[0] if rest else {}))
    return out


def _id_from_name(path: Path) -> int:
    head = path.stem.split("_", 1)[0]
    return int(head) if head.isdigit() else 0


def _player(p: Any) -> dict[str, Any]:
    def g(k: str, d: Any = 0) -> Any:  # a field gem may not have in every version
        return getattr(p, k, d)

    return {
        "slot": p.player_id,
        "name": p.player_name,
        "steamid": str(p.steam_id) if p.steam_id else "",
        "hero": p.hero_name,
        "heroName": hero_display(p.hero_name) if p.hero_name else "",
        "team": TEAMS.get(p.team, str(p.team)),
        "won": bool(g("win")),
        "kills": p.kills,
        "deaths": p.deaths,
        "assists": p.assists,
        "level": g("level"),
        "lastHits": g("last_hits"),
        "denies": g("denies"),
        "netWorth": g("net_worth"),
        "goldPerMin": g("gold_per_min"),
        "xpPerMin": g("xp_per_min"),
        "heroDamage": g("hero_damage"),
        "towerDamage": g("tower_damage"),
        "heroHealing": g("hero_healing"),
        "towerKills": g("tower_kills"),
        "roshanKills": g("roshan_kills"),
        "observersPlaced": g("obs_placed"),
        "sentriesPlaced": g("sen_placed"),
        "campsStacked": g("camps_stacked"),
        "runePickups": g("rune_pickups"),
        "buybacks": g("buyback_count"),
        "stuns": round(float(g("stuns_dealt", 0.0)), 2),
        "lane": {1: "bottom", 2: "middle", 3: "top", 4: "radiant jungle", 5: "dire jungle"}.get(g("lane"), ""),
    }


def _killer(by_hero: dict[str, int], source: str, attacker: str) -> int | None:
    """The player behind a kill: the damage's source first (a summon's or illusion's hero), else the attacker."""
    if source in by_hero:
        return by_hero[source]
    return by_hero.get(attacker)


def _events(match: Any, by_hero: dict[str, int], at: Callable[[int], float], sampler: _Sampler | None) -> list[Event]:
    """Kills and deaths from the combat log; objectives and wards from gem's extractors."""
    out: list[Event] = []
    for e in match.combat_log:
        if getattr(e.log_type, "value", e.log_type) != "DEATH" or not e.target_is_hero or e.target_is_illusion:
            continue
        victim = by_hero.get(e.target_name)
        if victim is None or getattr(e, "will_reincarnate", False):
            continue  # an aegis or Reincarnation brings the hero back where it fell: not a death
        killer = _killer(by_hero, e.damage_source_name, e.attacker_name)
        t = at(e.tick)
        out.append(Event(e.tick, t, "death", victim, other=_short(e.damage_source_name or e.attacker_name)))
        if killer is not None and killer != victim:
            out.append(Event(e.tick, t, "kill", killer, other=_short(e.target_name)))
    structures = sampler.structures if sampler is not None else {}
    for kind, items, name_of in (
        ("tower_kill", getattr(match, "towers", []), lambda k: k.tower_name),
        ("barracks_kill", getattr(match, "barracks", []), lambda k: k.barracks_name),
    ):
        for k in items:
            name = name_of(k)
            killer = _killer(by_hero, k.killer_source, k.killer)
            ev = Event(k.tick, at(k.tick), kind, -1 if killer is None else killer, other=_short(name))
            if _short(name) in structures:
                ev.x, ev.y, ev.z = structures[_short(name)]
            out.append(ev)
    roshan = sampler.roshan if sampler is not None else []
    for k in getattr(match, "roshans", []):
        killer = _killer(by_hero, k.killer_source, k.killer)
        ev = Event(k.tick, at(k.tick), "roshan_kill", -1 if killer is None else killer, other=f"roshan {k.kill_number}")
        seen = [r for r in roshan if r[0] <= k.tick]
        if seen:
            _, ev.x, ev.y, ev.z = seen[-1]
        out.append(ev)
    for k in getattr(match, "tormentors", []):
        slot = k.killer_player_id if isinstance(k.killer_player_id, int) and k.killer_player_id >= 0 else by_hero.get(k.killer, -1)
        out.append(Event(k.tick, at(k.tick), "tormentor_kill", slot, other=f"tormentor {k.kill_number}"))
    for w in getattr(match, "wards", []):
        if w.x is None or w.y is None:
            continue
        slot = w.player_id if w.player_id is not None and w.player_id >= 0 else by_hero.get(w.placer, -1)
        out.append(Event(w.tick, at(w.tick), f"{w.ward_type}_ward", slot, w.x - CELL_ORIGIN, w.y - CELL_ORIGIN,
                         other=w.ward_type))
    out.sort(key=lambda e: (e.tick, e.event))
    return out


#: Combat log entries about a hero, by the log's type -> the row's event (the target's row; `DAMAGE` and
#: `HEAL` also get a row at the attacker: "damage", "healed").
COMBAT_ROWS = {
    "DAMAGE": "hurt",
    "HEAL": "heal",
    "ABILITY": "ability",
    "ITEM": "item",
    "PURCHASE": "purchase",
    "PICKUP_RUNE": "rune",
    "GOLD": "gold",
    "XP": "xp",
    "MODIFIER_ADD": "modifier",
    "MODIFIER_REMOVE": "modifier_end",
    "KILLSTREAK": "killstreak",
    "MULTIKILL": "multikill",
    "BUYBACK": "buyback",
    "DEATH": "unit_kill",
}


def _more_events(match: Any, by_hero: dict[str, int], at: Callable[[int], float]) -> list[Event]:
    """
    The combat log's entries about a player's hero (not its illusions), the
    chat, smokes, runes, Aegis, neutral items found, wards taken out - each
    at the hero (or where the game says it happened).
    """
    out: list[Event] = []
    for e in getattr(match, "combat_log", []):
        kind = getattr(e.log_type, "value", e.log_type)
        event = COMBAT_ROWS.get(kind)
        if event is None:
            continue
        attacker = by_hero.get(e.attacker_name) if not e.attacker_is_illusion else None
        target = by_hero.get(e.target_name) if not e.target_is_illusion else None
        what = _short(e.inflictor_name or e.value_name or "")
        t = at(e.tick)
        x = e.location_x if e.location_x is not None else None
        y = e.location_y if e.location_y is not None else None
        if kind == "DEATH":
            # A hero's death is read elsewhere; here the units a player killed - with the hero, its illusions or
            # its summons (the damage's source names the hero behind them).
            killer = _killer(by_hero, e.damage_source_name, e.attacker_name)
            if e.target_is_hero or killer is None:
                continue
            out.append(Event(e.tick, t, event, killer, x, y, other=_short(e.target_name), value=e.value, text=what))
            continue
        if kind in ("ABILITY", "ITEM", "PURCHASE", "GOLD", "XP", "KILLSTREAK", "MULTIKILL", "BUYBACK"):
            who = attacker if kind in ("ABILITY", "ITEM") else target if target is not None else attacker
            if who is None:
                continue
            out.append(Event(e.tick, t, event, who, x, y, other=_short(e.target_name if who == attacker else e.attacker_name),
                             value=e.value or e.ability_level or e.gold_reason or e.xp_reason or None, text=what))
            continue
        if kind == "PICKUP_RUNE":
            who = target if target is not None else attacker
            if who is not None:
                out.append(Event(e.tick, t, event, who, x, y, value=e.rune_type, text=what))
            continue
        if target is not None:
            out.append(Event(e.tick, t, event, target, x, y, other=_short(e.attacker_name), value=e.value, text=what))
        if kind in ("DAMAGE", "HEAL") and attacker is not None and attacker != target:
            out.append(Event(e.tick, t, "damage" if kind == "DAMAGE" else "healed", attacker, x, y,
                             other=_short(e.target_name), value=e.value, text=what))
    for c in getattr(match, "chat", []):
        out.append(Event(c.tick, at(c.tick), "chat", c.player_slot, other=c.channel, text=c.text))
    for sm in getattr(match, "smoke_events", []):
        slot = by_hero.get(sm.activator, -1)
        x = sm.activation_x if sm.activation_x is not None else None
        y = sm.activation_y if sm.activation_y is not None else None
        out.append(Event(sm.tick, at(sm.tick), "smoke", slot, None if x is None else x - CELL_ORIGIN,
                         None if y is None else y - CELL_ORIGIN, other=",".join(_short(h) for h in sm.smoked)))
    for r in getattr(match, "runes", []):
        slot = r.player_id if isinstance(r.player_id, int) and r.player_id >= 0 else -1
        out.append(Event(r.spawn_tick, at(r.spawn_tick), "rune_spawn", slot, r.x - CELL_ORIGIN, r.y - CELL_ORIGIN,
                         other=str(r.outcome or ""), value=r.rune_type))
    for a in getattr(match, "aegis_events", []):
        out.append(Event(a.tick, at(a.tick), "aegis", a.player_id, text=str(a.event_type)))
    for n in getattr(match, "neutral_item_finds", []):
        out.append(Event(n.tick, at(n.tick), "neutral_item", n.player_id, value=n.item_tier, text=str(n.item_key)))
    for w in getattr(match, "wards", []):
        left = getattr(w, "left_tick", None) or getattr(w, "end_tick", None)
        if left and w.x is not None and w.y is not None:
            slot = w.player_id if w.player_id is not None and w.player_id >= 0 else by_hero.get(w.placer, -1)
            out.append(Event(left, at(left), f"{w.ward_type}_ward_end", slot, w.x - CELL_ORIGIN, w.y - CELL_ORIGIN,
                             other=w.ward_type))
    return out


#: Combat log fields kept as columns in the summary, in this order.
COMBAT_FIELDS = (
    "tick", "log_type", "attacker_name", "damage_source_name", "target_name", "inflictor_name", "value",
    "attacker_is_hero", "target_is_hero", "attacker_is_illusion", "target_is_illusion", "ability_level",
    "gold_reason", "xp_reason", "value_name", "damage_type", "stun_duration", "neutral_camp_type",
    "neutral_camp_team", "location_x", "location_y", "timestamp_s", "game_time_s", "will_reincarnate",
    "visible_radiant", "visible_dire", "modifier_duration_s", "modifier_elapsed_duration_s", "attacker_team",
    "target_team", "source", "aura_modifier", "modifier_purged", "modifier_purged_duration_s", "rune_type",
)


def _jsonable(v: Any) -> Any:
    v = getattr(v, "value", v)  # an Enum
    if isinstance(v, float) and not math.isfinite(v):
        return None
    return v if v is None or isinstance(v, (bool, int, float, str)) else str(v)


def combat_columns(entries: list[Any], at: Callable[[int], float]) -> dict[str, list[Any]]:
    """
    The whole combat log as columns, every field gem reads, with the game
    clock's time added: written as `<match>.combatlog.parquet` (a long
    match's log is tens of thousands of entries).
    """
    columns: dict[str, list[Any]] = {k: [] for k in ("time", *COMBAT_FIELDS)}
    for e in entries:
        columns["time"].append(round(at(e.tick), 3))
        for k in COMBAT_FIELDS:
            columns[k].append(_jsonable(getattr(e, k, None)))
    return columns


def _columnar(items: list[Any]) -> dict[str, list[Any]] | list[Any]:
    """A list of like dicts as one list per key: the same data, a fraction of the text."""
    if not items or not all(isinstance(x, dict) for x in items):
        return items
    keys = list(dict.fromkeys(k for x in items for k in x))
    return {k: [x.get(k) for x in items] for k in keys}


def _more(match: Any, at: Callable[[int], float]) -> dict[str, Any]:
    """
    Everything else gem extracted, as JSON: per-player time series and logs,
    the draft, runes, couriers, smokes, fights, visibility, advantages. The
    combat log goes in as columns (`combat_columns`); gem's once-a-second
    position log, which the samples supersede, is left out.
    """
    try:
        from gem.results.serialization import to_dict
    except Exception:  # noqa: BLE001 - a gem without it: the summary keeps what it has
        return {}
    try:
        data = to_dict(match)
    except Exception:  # noqa: BLE001
        return {}
    data.pop("combat_log", None)
    for p in data.get("players") or []:
        if isinstance(p, dict):
            p.pop("position_log", None)
            # The combat log entries gem keeps per player are in the log already: their ticks are enough.
            for k, v in list(p.items()):
                if isinstance(v, list) and v and isinstance(v[0], dict) and "log_type" in v[0]:
                    p[k] = [{"tick": x.get("tick"), "value": x.get("value"), "name": x.get("value_name") or x.get("target_name")}
                            for x in v]
    data = json.loads(json.dumps(data, default=_jsonable))
    # The long lists of like records, as columns.
    for k in ("entity_visibility_events", "hero_visibility_events", "courier_snapshots", "neutral_creeps"):
        if isinstance(data.get(k), list):
            data[k] = _columnar(data[k])
    return data


def _short(npc: str) -> str:
    """
    A unit's name without its prefix: `hero_axe`, `goodguys_tower1_top`. The
    combat log says `npc_dota_goodguys_tower1_top`, the entity's own name is
    `dota_goodguys_tower1_top`; both come out the same.
    """
    return npc.removeprefix("npc_").removeprefix("dota_") if npc else ""


def _info(match: Any, path: Path) -> dict[str, Any]:
    def g(k: str, d: Any = None) -> Any:
        return getattr(match, k, d)

    radiant_win = g("radiant_win")
    return {
        "replay": path.name,
        "duration": g("duration"),
        "winner": None if radiant_win is None else ("Radiant" if radiant_win else "Dire"),
        "score": {"Radiant": g("radiant_score", 0), "Dire": g("dire_score", 0)},
        "teams": {
            "Radiant": {"name": g("radiant_team_name") or "", "tag": g("radiant_team_tag") or ""},
            "Dire": {"name": g("dire_team_name") or "", "tag": g("dire_team_tag") or ""},
        },
        "gameMode": g("game_mode"),
        "league": g("leagueid"),
        "firstBlood": g("first_blood_time"),
        # The parse stopped early: a replay cut short, or one gem cannot read to the end.
        "incomplete": g("parse_error") is not None,
    }


# ------------------------------------------------------------------ writing


def place(replay: Replay) -> None:
    """
    Gives each event without a position the position of its player then: the
    last sample at or before it (a hero's last steps before dying), else the
    first after. An event with neither - no player, as a creep's tower kill
    with the tower not seen - stays without one: in the summary, not the table.
    A ward gets its planter's height.
    """
    import bisect

    by_slot: dict[int, list[Sample]] = {}
    for s in replay.samples:
        by_slot.setdefault(s.slot, []).append(s)
    ticks = {slot: [s.tick for s in track] for slot, track in by_slot.items()}
    for e in replay.events:
        track = by_slot.get(e.slot)
        if not track:
            continue
        i = bisect.bisect_right(ticks[e.slot], e.tick)
        s = track[i - 1] if i > 0 else track[0]
        if e.x is None or e.y is None:
            e.x, e.y, e.z = s.x, s.y, s.z
        elif e.z is None:
            e.z = s.z


#: How the viewer should read the table (the `heat3d` key in the Parquet footer).
HINTS = {
    "version": 1,
    "kind": "dota2-replay",
    # Source 2's world, as CS2's: Z up, and drawn with Y negated so the map is not mirrored.
    "axes": {"up": "z", "flipX": False, "flipY": True, "flipZ": False, "scale": 1},
    # A hero's hull is 24 units in radius.
    "entity": {"size": 48},
    "columns": {
        "x": "x",
        "y": "y",
        "z": "z",
        "time": "time",
        "timeUnit": "seconds",
        "personId": "player",
        "teamId": "team",
        "sessionId": "life",
        "lookMode": "vector",
        "dirX": "dirX",
        "dirY": "dirY",
        "dirZ": "dirZ",
        "extra": ["event", "hero", "other", "health", "level", "match", "value", "text", "mana", "items"],
    },
}

#: The hero state's columns in the table, after the fixed ones; `items` is text, the rest numbers.
STATE_COLUMNS = (*HERO_FIELDS.values(), "items", "cursorX", "cursorY")

COLUMNS = ("time", "tick", "event", "slot", "player", "hero", "team", "life", "x", "y", "z", "health", "maxHealth",
           "level", "other", "value", "text", "dirX", "dirY", "dirZ", *STATE_COLUMNS)


def table(replay: Replay) -> Any:
    """
    Positions and events as one table, in time order, with the hints in its
    footer. `life` counts a hero's lives from 1, so a track ends where the hero
    died rather than running on to the fountain it respawned at.
    """
    import bisect

    import numpy as np
    import pyarrow as pa

    place(replay)
    by_slot = {p["slot"]: p for p in replay.players}
    deaths: dict[int, list[int]] = {}
    for e in replay.events:
        if e.event == "death":
            deaths.setdefault(e.slot, []).append(e.tick)

    rows: dict[str, list[Any]] = {k: [] for k in COLUMNS}

    def add(tick: int, t: float, event: str, slot: int, x: float, y: float, z: float,
            hp: int | None, mhp: int | None, lvl: int | None, other: str, life: int, value: float | None = None,
            text: str = "", state: dict[str, Any] | None = None) -> None:
        p = by_slot.get(slot, {})
        state = state or {}
        yaw = state.get("yaw")
        look = (math.cos(math.radians(yaw)), math.sin(math.radians(yaw)), 0.0) if isinstance(yaw, (int, float)) else (None,) * 3
        for k, v in (("time", t), ("tick", tick), ("event", event), ("slot", slot), ("player", p.get("name", "")),
                     ("hero", p.get("heroName", "")), ("team", p.get("team", "")), ("life", life), ("x", x),
                     ("y", y), ("z", z), ("health", hp), ("maxHealth", mhp), ("level", lvl), ("other", other),
                     ("value", value), ("text", text), ("dirX", look[0]), ("dirY", look[1]), ("dirZ", look[2])):
            rows[k].append(v)
        for k in STATE_COLUMNS:
            v = state.get(k)
            rows[k].append(("" if v is None else str(v)) if k == "items" else (None if v is None else float(v)))

    for s in replay.samples:
        life = 1 + bisect.bisect_left(deaths.get(s.slot, []), s.tick)
        add(s.tick, s.time, "position", s.slot, s.x, s.y, s.z, s.health, s.max_health, s.level, "", life, state=s.extra)
    for e in replay.events:
        if e.x is None or e.y is None:
            continue
        # A death ends the life it happened in; anything else belongs to the life it happened in.
        life = 1 + bisect.bisect_left(deaths.get(e.slot, []), e.tick)
        add(e.tick, e.time, e.event, e.slot, e.x, e.y, 0.0 if e.z is None else e.z, None, None, None, e.other, life,
            e.value, e.text)

    n = len(rows["time"])
    order = np.lexsort((np.array(rows["slot"], dtype=np.int64),
                        np.array([0 if ev == "position" else 1 for ev in rows["event"]], dtype=np.int64),
                        np.array(rows["tick"], dtype=np.int64))) if n else np.zeros(0, dtype=np.int64)

    def ints(name: str, kind: Any) -> Any:
        values = [rows[name][i] for i in order]
        mask = np.array([v is None for v in values], dtype=bool)
        data = np.array([0 if v is None else v for v in values], dtype=np.int64)
        return pa.array(data, type=kind, mask=mask if mask.any() else None)

    def floats(name: str, kind: Any) -> Any:
        values = np.array([np.nan if rows[name][i] is None else rows[name][i] for i in order], dtype=np.float64)
        return pa.array(values, type=kind, from_pandas=True)

    def text(name: str) -> Any:
        return pa.array([rows[name][i] for i in order], type=pa.string()).dictionary_encode()

    columns = {
        "match": pa.array([str(replay.match_id)] * n, type=pa.string()).dictionary_encode(),
        "time": floats("time", pa.float64()),
        "tick": ints("tick", pa.int32()),
        "event": text("event"),
        "slot": ints("slot", pa.int8()),
        "player": text("player"),
        "hero": text("hero"),
        "team": text("team"),
        "life": ints("life", pa.int16()),
        "x": floats("x", pa.float32()),
        "y": floats("y", pa.float32()),
        "z": floats("z", pa.float32()),
        "health": ints("health", pa.int32()),
        "maxHealth": ints("maxHealth", pa.int32()),
        "level": ints("level", pa.int8()),
        "other": text("other"),
        "value": floats("value", pa.float32()),
        "text": text("text"),
        "dirX": floats("dirX", pa.float32()),
        "dirY": floats("dirY", pa.float32()),
        "dirZ": floats("dirZ", pa.float32()),
        **{k: (text(k) if k == "items" else floats(k, pa.float32())) for k in STATE_COLUMNS},
    }
    hints = dict(HINTS, hz=replay.hz)
    return pa.table(columns).replace_schema_metadata({"heat3d": json.dumps(hints)})


#: How the viewer should read the units' table: one track per unit, `unit` naming it.
UNIT_HINTS = {
    **HINTS,
    "kind": "dota2-replay-units",
    "columns": {**HINTS["columns"], "personId": "unit", "sessionId": "match",
                "extra": ["name", "class", "team", "health", "owner", "match"]},
}


def units_table(replay: Replay) -> Any:
    """Every unit but the players' heroes, once a second: creeps, summons, illusions, couriers, wards, buildings."""
    import numpy as np
    import pyarrow as pa

    u = replay.units
    teams = {RADIANT: "Radiant", DIRE: "Dire"}

    def col(i: int) -> list[Any]:
        return [r[i] for r in u]

    def floats(values: list[Any], kind: Any = pa.float32()) -> Any:
        return pa.array(np.array([np.nan if v is None else v for v in values], dtype=np.float64), type=kind, from_pandas=True)

    yaw = np.array([np.nan if v is None else v for v in col(11)], dtype=np.float64) if u else np.zeros(0)
    columns = {
        "match": pa.array([str(replay.match_id)] * len(u), type=pa.string()).dictionary_encode(),
        "time": floats(col(1), pa.float64()),
        "tick": pa.array(col(0), type=pa.int32()),
        "unit": pa.array([f"{name or cls} #{index}" for index, cls, name in zip(col(2), col(3), col(4))],
                         type=pa.string()).dictionary_encode(),
        "class": pa.array(col(3), type=pa.string()).dictionary_encode(),
        "name": pa.array(col(4), type=pa.string()).dictionary_encode(),
        "team": pa.array([teams.get(t, str(t if t is not None else "")) for t in col(5)], type=pa.string()).dictionary_encode(),
        "x": floats(col(6)),
        "y": floats(col(7)),
        "z": floats(col(8)),
        "health": floats(col(9)),
        "maxHealth": floats(col(10)),
        "dirX": pa.array(np.cos(np.radians(yaw)), type=pa.float32(), from_pandas=True),
        "dirY": pa.array(np.sin(np.radians(yaw)), type=pa.float32(), from_pandas=True),
        "dirZ": pa.array(np.where(np.isfinite(yaw), 0.0, np.nan), type=pa.float32(), from_pandas=True),
        "owner": pa.array(col(12), type=pa.int16()),
    }
    return pa.table(columns).replace_schema_metadata({"heat3d": json.dumps(dict(UNIT_HINTS, hz=1.0))})


def summary(replay: Replay) -> dict[str, Any]:
    """The match as one document: teams, score, every player's line, deaths, objectives and wards."""
    place(replay)

    def at(e: Event) -> dict[str, Any]:
        return {"time": round(e.time, 1), "slot": e.slot, "x": _r(e.x), "y": _r(e.y)}

    span = (replay.samples[-1].time - replay.samples[0].time) if replay.samples else 0.0
    return {
        "format": "heat3d-dota-match",
        "version": 2,
        "match": str(replay.match_id),
        "map": "dota",
        **replay.info,
        "players": replay.players,
        "deaths": [{**at(e), "by": e.other} for e in replay.events if e.event == "death"],
        "objectives": [{**at(e), "event": e.event, "what": e.other} for e in replay.events
                       if e.event in ("tower_kill", "barracks_kill", "roshan_kill", "tormentor_kill")],
        "wards": [{**at(e), "type": e.other} for e in replay.events if e.event.endswith("_ward")],
        "samples": {"hz": replay.hz, "rows": len(replay.samples), "seconds": round(span, 1)},
        "units": {"hz": 1.0, "rows": len(replay.units), "count": len({u[2] for u in replay.units})},
        "events": dict(sorted(_count(e.event for e in replay.events).items())),
        # Everything else the parser extracted, as it has it (see `_more`); the combat log in a table of its own.
        "gem": replay.more,
        "combatLog": {"file": f"{replay.match_id}.combatlog.parquet", "rows": len(replay.combat_log.get("tick", []))},
        "conventions": {
            "coordinates": "Dota world units: x east, y north, z up; the playable map runs about -8200..8200",
            "time": "the game clock in seconds: negative before the horn, standing while paused",
            "deaths": "real deaths only: one an aegis or Reincarnation undoes is left out",
            "places": "a death where the hero fell, a kill where the killer stood, a tower or Roshan where it stood, "
                      "a ward where it was planted",
        },
    }


def _count(items: Any) -> dict[str, int]:
    out: dict[str, int] = {}
    for x in items:
        out[x] = out.get(x, 0) + 1
    return out


def _r(v: float | None) -> float | None:
    return None if v is None else round(v, 1)


def write(replay: Replay, folder: str | Path) -> tuple[Path, Path]:
    """`<match>.parquet` and `<match>.match.json` in `folder`."""
    import pyarrow.parquet as pq

    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    name = str(replay.match_id)
    data = folder / f"{name}.parquet"
    doc = folder / f"{name}.match.json"
    pq.write_table(table(replay), data, compression="snappy", row_group_size=256_000)
    if replay.units:
        pq.write_table(units_table(replay), folder / f"{name}.units.parquet", compression="snappy",
                       row_group_size=256_000)
    if replay.combat_log.get("tick"):
        import pyarrow as pa

        pq.write_table(pa.table(replay.combat_log), folder / f"{name}.combatlog.parquet", compression="snappy")
    # Compact: the parser's data runs to megabytes.
    doc.write_text(json.dumps(summary(replay), ensure_ascii=False, default=str, separators=(",", ":")), encoding="utf-8")
    return data, doc


def convert(path: str | Path, folder: str | Path, hz: float = HZ) -> tuple[Path, Path]:
    """One replay into `folder`: read, then written."""
    return write(read(path, hz), folder)


def main(argv: list[str] | None = None) -> int:
    """
    `python -m heat3d_watch.decoders.dota_replay <replay.dem> -o <folder>`: one
    replay converted in a process of its own. The watcher runs it so, which
    keeps the parse's memory (about a gigabyte for a long match) out of its own.
    """
    import argparse
    import sys

    ap = argparse.ArgumentParser(prog="heat3d_watch.decoders.dota_replay")
    ap.add_argument("replay")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--hz", type=float, default=HZ)
    args = ap.parse_args(argv)
    try:
        data, doc = convert(args.replay, args.out, args.hz)
    except (FormatError, Missing) as e:
        print(f"{args.replay}: {e}", file=sys.stderr)
        return 2
    print(data)
    print(doc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
