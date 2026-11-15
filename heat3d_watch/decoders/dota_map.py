"""
Dota 2's map as a level for the viewer: terrain, cliffs, water, trees and
buildings, in the frame the Dota replay tables are drawn in.

Everything comes from the user's own install, read offline by Source2Viewer's
command line (ValveResourceFormat, MIT licensed,
https://github.com/ValveResourceFormat/ValveResourceFormat), which decodes
Source 2's compiled resources; nothing here ships or downloads anything of the
game. Three things are taken from it:

- the map's collision mesh (`maps/<map>/world_physics`): the ground the heroes
  walk on, the cliff faces between its levels, and the water surfaces;
- the map's entity lumps (`maps/<map>/entities/*.vents_c`), decompiled to
  text: where each tree and building stands, turned and scaled how, with which
  model;
- those models, from the game's own archive (`pak01_dir.vpk`).

A building is its model's render mesh, thinned by vertex clustering. A tree is
a low turned solid that follows its model's outline - trunk, crown, true height
and width - because 2,000-odd trees at full detail would outweigh the rest of
the map many times over and say nothing more to a heatmap.

Source2Viewer writes glTF in metres with Y up: (Y, Z, X) of the game's units,
scaled by 0.0254. That is undone, and the result written the way the viewer
draws the Watcher's Dota tables (dota_replay.HINTS): game units, (X, Z, -Y).
"""

from __future__ import annotations

import math
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np

from . import glb

GAME_FOLDER = "dota 2 beta"
#: glTF metres of Source2Viewer's export -> game units.
INCH = 0.0254
#: A face whose normal is at least this far up is ground; the rest of the terrain is cliff and wall.
GROUND = 0.7
SOURCE2VIEWER_URL = "https://github.com/ValveResourceFormat/ValveResourceFormat/releases"

#: The buildings drawn, by entity class, and the part each goes to. Shops (a
#: shopkeeper is a character), the hall of fame and decoration are left out.
BUILDINGS = {
    "npc_dota_tower": "tower",
    "npc_dota_barracks": "barracks",
    "npc_dota_fort": "ancient",
    "npc_dota_building": "filler",
    "npc_dota_watch_tower": "outpost",
    "ent_dota_fountain": "fountain",
    "npc_dota_xp_fountain": "shrine",
    "npc_dota_lotus_pool": "lotus_pool",
    "npc_dota_unit_twin_gate": "twin_gate",
    "npc_dota_lantern": "watcher",
    "ent_dota_neutral_item_stash": "neutral_stash",
}
TREE = "ent_dota_tree"
#: A model's meshes that are another state of the same thing: a cut tree's
#: stump, the close-up shown in the inspector, a building's rubble.
OTHER_STATE = re.compile(r"stump|inspector|destruction|_dest_", re.I)
#: Physics surfaces that are water: the river and ponds (`water_slime`) and the
#: thin streams that run through the jungle, which Dota names `window`. Heroes
#: stand 10 to 16 units under the first and a few units under the second.
WATER = re.compile(r"water|slime|window", re.I)


# ------------------------------------------------------------------ finding things


def dota_folders() -> list[Path]:
    """`<library>/steamapps/common/dota 2 beta/game/dota` wherever Dota 2 is installed."""
    from ..adapters.replays import steam_libraries

    return [lib / GAME_FOLDER / "game" / "dota" for lib in steam_libraries() if (lib / GAME_FOLDER / "game" / "dota").is_dir()]


def game_folder(game: str | None = None) -> Path:
    """Dota's `game/dota` folder: `--game` (the install or that folder itself), else the first install found."""
    if game:
        given = Path(game)
        for candidate in (given, given / "game" / "dota", given / "dota"):
            if (candidate / "gameinfo.gi").exists():
                return candidate
        raise FileNotFoundError(f"{game} is not a Dota 2 folder (no game/dota/gameinfo.gi under it)")
    found = dota_folders()
    if not found:
        raise FileNotFoundError("Dota 2 not found in any Steam library - pass --game <Dota 2 folder>")
    return found[0]


def find_vpk(name: str, folder: Path) -> Path:
    """The map's .vpk: a path as given, or `<name>.vpk` in the install's maps folder."""
    given = Path(name)
    if given.suffix.lower() == ".vpk" and given.exists():
        return given
    candidate = folder / "maps" / f"{given.stem}.vpk"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"no {given.stem}.vpk in {folder / 'maps'}")


def find_source2viewer(given: str | None = None) -> Path:
    for candidate in (given, os.environ.get("HEAT3D_SOURCE2VIEWER"), shutil.which("Source2Viewer-CLI"), shutil.which("Source2Viewer-CLI.exe")):
        if candidate and Path(candidate).exists():
            return Path(candidate)
    raise FileNotFoundError(
        "Source2Viewer-CLI not found: download the command line build for your system from "
        f"{SOURCE2VIEWER_URL}, then put it on PATH, set HEAT3D_SOURCE2VIEWER, or pass --source2viewer"
    )


# ------------------------------------------------------------------ frames


def to_game(gl: np.ndarray) -> np.ndarray:
    """Source2Viewer's glTF metres (Y up) -> the game's units (Z up)."""
    return np.stack([gl[:, 2], gl[:, 0], gl[:, 1]], axis=1) / INCH


def to_viewer(game: np.ndarray) -> np.ndarray:
    """The game's frame -> the frame the Dota tables are drawn in: (X, Z, -Y)."""
    return np.stack([game[:, 0], game[:, 2], -game[:, 1]], axis=1)


def rotation(pitch: float, yaw: float, roll: float) -> np.ndarray:
    """Source's angles in degrees (pitch about Y, yaw about Z, roll about X) as a matrix: columns forward, left, up."""
    p, y, r = (math.radians(a) for a in (pitch, yaw, roll))
    sp, cp, sy, cy, sr, cr = math.sin(p), math.cos(p), math.sin(y), math.cos(y), math.sin(r), math.cos(r)
    return np.array(
        [
            [cp * cy, sr * sp * cy - cr * sy, cr * sp * cy + sr * sy],
            [cp * sy, sr * sp * sy + cr * cy, cr * sp * sy - sr * cy],
            [-sp, sr * cp, cr * cp],
        ]
    )


# ------------------------------------------------------------------ entities


@dataclass
class Entity:
    classname: str
    model: str = ""
    origin: tuple[float, float, float] = (0.0, 0.0, 0.0)
    angles: tuple[float, float, float] = (0.0, 0.0, 0.0)
    scales: tuple[float, float, float] = (1.0, 1.0, 1.0)
    keys: dict[str, str] = field(default_factory=dict)

    def place(self, points: np.ndarray) -> np.ndarray:
        """Model-space points (game units) where this entity puts them in the world."""
        return (points * np.array(self.scales)) @ rotation(*self.angles).T + np.array(self.origin)


_VECTOR = re.compile(r"^\[\s*([-\d.eE+]+)\s*,\s*([-\d.eE+]+)\s*,\s*([-\d.eE+]+)\s*\]$")


def _text(value: str) -> str:
    """A key's value without its quotes or `resource_name:` tag."""
    value = value.strip()
    if value.startswith("resource_name:"):
        value = value[len("resource_name:"):]
    if len(value) >= 2 and value[0] == value[-1] == '"':
        value = value[1:-1]
    return value


def _vector(value: str | None, default: tuple[float, float, float]) -> tuple[float, float, float]:
    if value is None:
        return default
    m = _VECTOR.match(value.strip())
    if m:
        return (float(m.group(1)), float(m.group(2)), float(m.group(3)))
    parts = _text(value).split()  # older lumps write "x y z"
    try:
        return (float(parts[0]), float(parts[1]), float(parts[2])) if len(parts) == 3 else default
    except ValueError:
        return default


def read_entities(text: str) -> list[Entity]:
    """
    An entity lump as Source2Viewer decompiles it: blocks headed `====<n>====`,
    one `key value` per line. Lines starting with `@` are outputs and skipped.
    """
    out: list[Entity] = []
    for block in re.split(r"^====\d+====\s*$", text, flags=re.M):
        keys: dict[str, str] = {}
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("@"):
                continue
            head, _, rest = line.partition(" ")
            keys[head] = rest.strip()
        if "classname" not in keys:
            continue
        out.append(
            Entity(
                classname=_text(keys["classname"]),
                model=_text(keys.get("model", "")),
                origin=_vector(keys.get("origin"), (0.0, 0.0, 0.0)),
                angles=_vector(keys.get("angles"), (0.0, 0.0, 0.0)),
                scales=_vector(keys.get("scales"), (1.0, 1.0, 1.0)),
                keys=keys,
            )
        )
    return out


def shown_layers(entities: list[Entity]) -> set[str]:
    """The world layers shown when a match starts: an `info_world_layer` whose spawn flags have bit 1."""
    shown = set()
    for e in entities:
        if e.classname == "info_world_layer":
            try:
                flags = int(_text(e.keys.get("spawnflags", "0")))
            except ValueError:
                flags = 0
            if flags & 1:
                shown.add(_text(e.keys.get("layername", "")))
    return shown


def entities_of(lumps: dict[str, str]) -> list[Entity]:
    """
    The entities present when a match starts, from the lumps by name (without
    folder or extension): `default_ents`, and each world layer that starts shown.
    The layers that start hidden hold what appears when a base falls.
    """
    base = read_entities(lumps.get("default_ents", ""))
    shown = shown_layers(base)
    out = list(base)
    for name, text in sorted(lumps.items()):
        if name != "default_ents" and name in shown:
            out += read_entities(text)
    return out


# ------------------------------------------------------------------ geometry


def surface_of(node: str) -> str | None:
    """A physics group's surface, in lower case; None for clip brushes and the sky."""
    node = node.lower()
    if "clip" in node or "sky" in node:
        return None
    surface = re.sub(r"^physics(_group|_passbullets)?_?", "", node)
    return surface or "terrain"


def _up(points: np.ndarray, triangles: np.ndarray) -> np.ndarray:
    a, b, c = (points[triangles[:, k]] for k in range(3))
    normal = np.cross(b - a, c - a)
    length = np.linalg.norm(normal, axis=1)
    return np.divide(normal[:, 2], length, out=np.zeros(len(length)), where=length > 0)


def terrain_parts(meshes: list[tuple[str, np.ndarray, np.ndarray]]) -> dict[str, list[tuple[np.ndarray, np.ndarray]]]:
    """
    The collision mesh as parts, in the game's frame: water surfaces (their
    upward faces) as `water:<surface>`; everything else split by its faces'
    normals into `ground:<surface>` and `structure:<surface>`.
    """
    out: dict[str, list[tuple[np.ndarray, np.ndarray]]] = {}
    for node, gl, triangles in meshes:
        surface = surface_of(node)
        if surface is None or not len(triangles):
            continue
        game = to_game(gl)
        up = _up(game, triangles)
        if WATER.search(surface):
            keep = up > 0
            if keep.any():
                out.setdefault(f"water:{surface}", []).append((game, triangles[keep]))
            continue
        for kind, keep in (("ground", up >= GROUND), ("structure", up < GROUND)):
            if keep.any():
                out.setdefault(f"{kind}:{surface}", []).append((game, triangles[keep]))
    return out


def cluster(points: np.ndarray, triangles: np.ndarray, cell: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Fewer triangles by vertex clustering: every point snaps to the mean of the
    points in its `cell`-sized cube, and triangles that collapse, or repeat
    another, go. Shapes larger than a cell keep their outline, to within half
    a cell; detail smaller than one goes. `cell` <= 0 leaves the mesh as it is.
    """
    if cell <= 0 or not len(triangles):
        return points, triangles
    keys = np.floor(points / cell).astype(np.int64)
    _, group, counts = np.unique(keys, axis=0, return_inverse=True, return_counts=True)
    group = group.reshape(-1)
    merged = np.zeros((len(counts), 3))
    np.add.at(merged, group, points)
    merged /= counts[:, None]
    tris = group[triangles]
    alive = (tris[:, 0] != tris[:, 1]) & (tris[:, 1] != tris[:, 2]) & (tris[:, 0] != tris[:, 2])
    tris = tris[alive]
    if len(tris):
        _, first = np.unique(np.sort(tris, axis=1), axis=0, return_index=True)
        tris = tris[np.sort(first)]
    used = np.unique(tris)
    remap = np.full(len(merged), -1, dtype=np.int64)
    remap[used] = np.arange(len(used))
    return merged[used], remap[tris]


def lathe(points: np.ndarray, sides: int = 6, bands: int = 5) -> tuple[np.ndarray, np.ndarray]:
    """
    A tree's outline as a closed turned solid about its model's vertical axis:
    the height split into `bands`, each a ring as wide as most of the model's
    points at that height (the 90th percentile of their distance from the
    axis), a point on top. True height and width, `2 * sides * bands`
    triangles.
    """
    z = points[:, 2]
    r = np.hypot(points[:, 0], points[:, 1])
    lo, hi = float(z.min()), float(z.max())
    if hi - lo < 1e-6:
        hi = lo + 1.0
    edges = np.linspace(lo, hi, bands + 1)
    radii = []
    for k in range(bands):
        inside = (z >= edges[k]) & (z <= edges[k + 1])
        radii.append(float(np.percentile(r[inside], 90)) if inside.any() else 0.0)
    # Empty bands (a bare trunk between crown layers) take the next band below's width.
    for k in range(1, bands):
        if radii[k] == 0.0:
            radii[k] = radii[k - 1]
    radii = [max(v, 1.0) for v in radii]
    heights = [lo] + [float((edges[k] + edges[k + 1]) / 2) for k in range(1, bands)]
    ring_r = [radii[0]] + radii[1:]
    angle = np.arange(sides) * (2 * math.pi / sides)
    verts = [np.array([0.0, 0.0, lo])]
    for h, rad in zip(heights, ring_r):
        verts += [np.array([rad * math.cos(a), rad * math.sin(a), h]) for a in angle]
    verts.append(np.array([0.0, 0.0, hi]))
    verts = np.array(verts)
    top = len(verts) - 1
    tris = []
    ring = lambda i, j: 1 + i * sides + (j % sides)  # noqa: E731
    for j in range(sides):  # bottom cap, facing down
        tris.append((0, ring(0, j + 1), ring(0, j)))
    for i in range(len(heights) - 1):
        for j in range(sides):
            a, b, c, d = ring(i, j), ring(i, j + 1), ring(i + 1, j), ring(i + 1, j + 1)
            tris += [(a, b, d), (a, d, c)]
    last = len(heights) - 1
    for j in range(sides):  # to the top
        tris.append((ring(last, j), ring(last, j + 1), top))
    return verts, np.array(tris, dtype=np.int64)


def model_mesh(meshes: list[tuple[str, np.ndarray, np.ndarray]]) -> tuple[np.ndarray, np.ndarray] | None:
    """A model's export as one mesh in model space (game units), its other states left out."""
    points, tris, offset = [], [], 0
    keep = [m for m in meshes if not OTHER_STATE.search(m[0].rsplit(".", 1)[-1])] or meshes
    for _, gl, t in keep:
        if not len(t):
            continue
        points.append(to_game(gl))
        tris.append(t + offset)
        offset += len(gl)
    if not points:
        return None
    return np.concatenate(points), np.concatenate(tris)


@dataclass
class Level:
    parts: list[tuple[str, np.ndarray, np.ndarray]]
    trees: int = 0
    buildings: int = 0
    missing: list[str] = field(default_factory=list)


def build(
    terrain: list[tuple[str, np.ndarray, np.ndarray]],
    entities: list[Entity],
    models: dict[str, tuple[np.ndarray, np.ndarray] | None],
    detail: float = 8.0,
    sides: int = 6,
    bands: int = 5,
) -> Level:
    """
    The level from Source2Viewer's physics export (glTF meshes), the map's
    entities, and each model in model space by its `.vmdl` path. Parts in the
    viewer's frame, sorted by name.
    """
    grouped = terrain_parts(terrain)
    proxies: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    thinned: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    trees = buildings = 0
    missing: set[str] = set()
    for e in entities:
        if e.classname == TREE:
            part = "structure:tree"
        elif e.classname in BUILDINGS:
            part = f"structure:{BUILDINGS[e.classname]}"
        else:
            continue
        mesh = models.get(e.model)
        if mesh is None:
            missing.add(e.model or e.classname)
            continue
        if e.classname == TREE:
            if e.model not in proxies:
                proxies[e.model] = lathe(mesh[0], sides, bands)
            points, tris = proxies[e.model]
            trees += 1
        else:
            if e.model not in thinned:
                thinned[e.model] = cluster(mesh[0], mesh[1], detail)
            points, tris = thinned[e.model]
            buildings += 1
        grouped.setdefault(part, []).append((e.place(points), tris))
    parts = []
    for name, pieces in sorted(grouped.items()):
        offset, points, tris = 0, [], []
        for p, t in pieces:
            points.append(to_viewer(p))
            tris.append(t + offset)
            offset += len(p)
        parts.append((name, np.concatenate(points), np.concatenate(tris)))
    return Level(parts, trees, buildings, sorted(missing))


# ------------------------------------------------------------------ Source2Viewer


def _run(tool: Path, vpk: Path, files: list[str], out: Path, extensions: str | None = None) -> subprocess.CompletedProcess:
    """Source2Viewer decompiling `files` (paths or folders in the archive) to `out`; models as .glb."""
    args = [str(tool), "-i", str(vpk), "-d", "-f", ",".join(files), "-o", str(out)]
    # With a glTF format given, it exports models and leaves other resources undecompiled.
    args += ["-e", extensions] if extensions else ["--gltf_export_format", "glb"]
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")


def _vmdl_c(model: str) -> str:
    return model[:-5] + ".vmdl_c" if model.endswith(".vmdl") else model + "_c"


def export_map(
    name: str,
    out: str | Path,
    game: str | None = None,
    source2viewer: str | None = None,
    detail: float = 8.0,
    say: Callable[[str], None] = lambda _: None,
) -> str:
    """Writes the map's level to `out`; returns a line saying what it holds."""
    folder = game_folder(game)
    vpk = find_vpk(name, folder)
    tool = find_source2viewer(source2viewer)
    stem = vpk.stem
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        say(f"reading {vpk.name}: collision mesh and entities")
        # One file asked for: the output is that file's name, not a folder. It writes the model
        # (empty: the world has no render mesh of its own) and its physics beside it.
        (tmp / "map").mkdir()
        run = _run(tool, vpk, [f"maps/{stem}/world_physics.vmdl_c"], tmp / "map" / "world_physics.glb")
        found = sorted((tmp / "map").rglob("*.glb"), key=lambda f: f.stat().st_size, reverse=True)
        if run.returncode != 0 or not found:
            raise RuntimeError(f"Source2Viewer did not export {stem}'s collision mesh:\n{run.stdout[-800:]}{run.stderr[-800:]}")
        doc, blob = glb.read(found[0])
        terrain = glb.meshes(doc, blob)
        _run(tool, vpk, [f"maps/{stem}/entities/"], tmp / "entities", extensions="vents_c")
        lumps = {f.stem: f.read_text(encoding="utf-8", errors="replace") for f in (tmp / "entities").rglob("*.vents")}
        if "default_ents" not in lumps:
            say(f"{stem} has no entity lump Source2Viewer could read: terrain and water only")
        entities = entities_of(lumps)
        wanted = sorted({e.model for e in entities if e.model and (e.classname == TREE or e.classname in BUILDINGS)})
        models: dict[str, tuple[np.ndarray, np.ndarray] | None] = {}
        if wanted:
            say(f"reading {len(wanted)} models from pak01_dir.vpk")
            pak = folder / "pak01_dir.vpk"
            run = _run(tool, pak, [_vmdl_c(m) for m in wanted], tmp / "models")
            for m in wanted:
                stem_path = tmp / "models" / Path(m).with_suffix(".glb")
                if stem_path.exists():
                    models[m] = model_mesh(glb.meshes(*glb.read(stem_path)))
    level = build(terrain, entities, models, detail=detail)
    if not level.parts:
        raise RuntimeError(f"{stem}'s collision mesh has nothing but clip brushes")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    glb.write(out, level.parts)
    triangles = sum(len(t) for _, _, t in level.parts)
    ground = sum(len(t) for n, _, t in level.parts if n.startswith("ground:"))
    line = (
        f"{out}: {stem}, {triangles:,} triangles ({ground:,} ground) in {len(level.parts)} parts; "
        f"{level.trees:,} trees, {level.buildings:,} buildings"
    )
    if level.missing:
        line += f"; {len(level.missing)} model(s) not found, left out: {', '.join(level.missing[:5])}"
    return line
