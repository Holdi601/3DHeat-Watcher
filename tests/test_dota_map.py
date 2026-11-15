"""Dota 2's map as a level: entity lumps, frames, terrain split, trees, buildings and the export - on made-up data."""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

import numpy as np
import pytest

from heat3d_watch import cli
from heat3d_watch.decoders import dota_map as m
from heat3d_watch.decoders import glb

LUMP = """====0====
classname                      "worldspawn"
origin                         [ 0.0, 0.0, 0.0 ]

====1====
model                          resource_name:"models/test/tree_a.vmdl"
classname                      "ent_dota_tree"
origin                         [ 100.0, 200.0, 128.0 ]
angles                         [ 0.0, 90.0, 0.0 ]
scales                         [ 0.5, 0.5, 0.5 ]

====2====
model                          resource_name:"models/test/tower_a.vmdl"
mapunitname                    "npc_test_tower"
classname                      "npc_dota_tower"
origin                         [ -1000.0, 500.0, 256.0 ]
angles                         [ 0.0, 0.0, 0.0 ]
scales                         [ 1.0, 1.0, 1.0 ]
@OnTowerKilled                 ReduceInvulnCount something

====3====
layername                      "world_layer_shown"
spawnflags                     1
classname                      "info_world_layer"

====4====
layername                      "world_layer_hidden"
spawnflags                     0
classname                      "info_world_layer"

====5====
model                          resource_name:"models/test/shopkeeper.vmdl"
classname                      "ent_dota_shop"
origin                         [ 0.0, 0.0, 0.0 ]
"""

LAYER = """====0====
model                          resource_name:"models/test/tree_a.vmdl"
classname                      "ent_dota_tree"
origin                         [ 300.0, 300.0, 0.0 ]
"""


def gl(game: np.ndarray) -> np.ndarray:
    """Game units (Z up) -> Source2Viewer's glTF metres (Y up), the inverse of to_game."""
    return np.stack([game[:, 1], game[:, 2], game[:, 0]], axis=1) * m.INCH


def quad(a, b, c, d) -> tuple[np.ndarray, np.ndarray]:
    return np.array([a, b, c, d], float), np.array([[0, 1, 2], [0, 2, 3]])


# ------------------------------------------------------------------ entities


def test_entity_lump_is_read_with_its_quotes_tags_and_vectors_undone():
    ents = m.read_entities(LUMP)
    assert [e.classname for e in ents] == ["worldspawn", "ent_dota_tree", "npc_dota_tower", "info_world_layer", "info_world_layer", "ent_dota_shop"]
    tree = ents[1]
    assert tree.model == "models/test/tree_a.vmdl"
    assert tree.origin == (100.0, 200.0, 128.0)
    assert tree.angles == (0.0, 90.0, 0.0)
    assert tree.scales == (0.5, 0.5, 0.5)
    assert ents[2].keys["mapunitname"] == '"npc_test_tower"'
    assert not any(k.startswith("@") for k in ents[2].keys)  # outputs are not keys
    assert ents[0].scales == (1.0, 1.0, 1.0)  # absent: the default


def test_only_layers_that_start_shown_are_added():
    lumps = {"default_ents": LUMP, "world_layer_shown": LAYER, "world_layer_hidden": LAYER.replace("300.0", "900.0")}
    assert m.shown_layers(m.read_entities(LUMP)) == {"world_layer_shown"}
    trees = [e.origin for e in m.entities_of(lumps) if e.classname == m.TREE]
    assert trees == [(100.0, 200.0, 128.0), (300.0, 300.0, 0.0)]


def test_older_lumps_write_vectors_as_text():
    assert m._vector('"1 2 3"', (0.0, 0.0, 0.0)) == (1.0, 2.0, 3.0)
    assert m._vector('"oops"', (0.0, 0.0, 9.0)) == (0.0, 0.0, 9.0)


# ------------------------------------------------------------------ frames


def test_frames_round_trip_and_the_viewer_frame_is_a_rotation():
    game = np.array([[1.0, 2.0, 3.0], [-5.0, 7.0, 11.0]])
    assert np.allclose(m.to_game(gl(game)), game)
    assert np.allclose(m.to_viewer(game), [[1.0, 3.0, -2.0], [-5.0, 11.0, -7.0]])
    # A rotation, not a mirror: the determinant of the axis change is +1.
    assert np.isclose(np.linalg.det(m.to_viewer(np.eye(3))), 1.0)


def test_source_angles():
    assert np.allclose(m.rotation(0, 90, 0) @ [1, 0, 0], [0, 1, 0])  # yaw turns east to north
    assert np.allclose(m.rotation(90, 0, 0) @ [1, 0, 0], [0, 0, -1])  # positive pitch looks down
    assert np.allclose(m.rotation(0, 0, 90) @ [0, 1, 0], [0, 0, 1])  # roll turns left to up
    r = m.rotation(10, 20, 30)
    assert np.allclose(r @ r.T, np.eye(3)) and np.isclose(np.linalg.det(r), 1.0)


def test_entity_places_scaled_turned_and_moved():
    e = m.Entity("ent_dota_tree", origin=(100.0, 200.0, 10.0), angles=(0.0, 90.0, 0.0), scales=(2.0, 2.0, 2.0))
    assert np.allclose(e.place(np.array([[1.0, 0.0, 5.0]])), [[100.0, 202.0, 20.0]])


# ------------------------------------------------------------------ terrain


def test_terrain_split_into_ground_cliffs_and_water_and_clips_dropped():
    flat = quad([0, 0, 0], [100, 0, 0], [100, 100, 0], [0, 100, 0])
    wall = quad([0, 0, 0], [0, 0, 100], [0, 100, 100], [0, 100, 0])
    water = quad([0, 0, 16], [100, 0, 16], [100, 100, 16], [0, 100, 16])
    meshes = [
        ("physics_group", gl(np.concatenate([flat[0], wall[0]])), np.concatenate([flat[1], wall[1] + 4])),
        ("physics_water_slime", gl(water[0]), np.concatenate([water[1], water[1][:, ::-1]])),  # up and down faces
        ("physics_npcclip_playerclip", gl(flat[0]), flat[1]),
    ]
    parts = m.terrain_parts(meshes)
    assert sorted(parts) == ["ground:terrain", "structure:terrain", "water:water_slime"]
    assert len(parts["ground:terrain"][0][1]) == 2
    assert len(parts["structure:terrain"][0][1]) == 2
    assert len(parts["water:water_slime"][0][1]) == 2  # only the faces looking up
    assert np.allclose(parts["ground:terrain"][0][0][:4], flat[0])  # back in game units
    assert m.surface_of("physics_window") == "window" and m.WATER.search("window")
    assert m.surface_of("physics_group") == "terrain"
    assert m.surface_of("physics_sky") is None


# ------------------------------------------------------------------ models


def grid(n: int, size: float) -> tuple[np.ndarray, np.ndarray]:
    xs = np.linspace(0, size, n + 1)
    pts = np.array([[x, y, 0.0] for y in xs for x in xs])
    tris = []
    for j in range(n):
        for i in range(n):
            a = j * (n + 1) + i
            tris += [(a, a + 1, a + n + 2), (a, a + n + 2, a + n + 1)]
    return pts, np.array(tris)


def test_clustering_thins_fine_detail_and_keeps_the_outline():
    pts, tris = grid(40, 400.0)
    p2, t2 = m.cluster(pts, tris, 50.0)
    assert len(t2) < len(tris) / 10
    assert p2.min(axis=0)[0] <= 25 and p2.max(axis=0)[0] >= 375  # still 400 wide, to half a cell
    assert t2.max() < len(p2)
    assert m.cluster(pts, tris, 0)[1] is tris  # 0: as it was


def closed(tris: np.ndarray) -> bool:
    edges: dict[tuple[int, int], int] = {}
    for t in tris:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            key = (min(a, b), max(a, b))
            edges[key] = edges.get(key, 0) + 1
    return all(v == 2 for v in edges.values())


def test_tree_outline_is_a_closed_turned_solid_of_the_models_size():
    rng = np.random.default_rng(1)
    # A cone-shaped made-up tree: 300 high, 100 wide at the bottom, narrowing to the top.
    z = rng.uniform(0, 300, 4000)
    r = (1 - z / 300) * 100 * np.sqrt(rng.uniform(0, 1, 4000))
    a = rng.uniform(0, 2 * math.pi, 4000)
    pts = np.stack([r * np.cos(a), r * np.sin(a), z], axis=1)
    v, t = m.lathe(pts, sides=6, bands=5)
    assert len(t) == 2 * 6 * 5
    assert closed(t)
    assert np.isclose(v[:, 2].min(), pts[:, 2].min()) and np.isclose(v[:, 2].max(), pts[:, 2].max())
    widths = np.hypot(v[1:-1, 0], v[1:-1, 1]).reshape(5, 6)[:, 0]
    assert 70 < widths[0] <= 100 and all(np.diff(widths) < 0)  # narrows upwards like the model
    # Outward: the signed volume of a closed mesh with outward faces is positive.
    vol = sum(np.dot(v[i], np.cross(v[j], v[k])) for i, j, k in t) / 6
    assert vol > 0


def test_model_mesh_leaves_out_other_states():
    a = (gl(np.array([[0, 0, 0], [10, 0, 0], [0, 10, 0]], float)), np.array([[0, 1, 2]]))
    b = (gl(np.array([[0, 0, 50], [10, 0, 50], [0, 10, 50]], float)), np.array([[0, 1, 2]]))
    meshes = [("x.vmdl_c.tree_model", *a), ("x.vmdl_c.tree_stump_model", *b), ("x.vmdl_c.tree_inspector", *b), ("x.vmdl_c.tree_model", *b)]
    pts, tris = m.model_mesh(meshes)
    assert len(tris) == 2 and tris.max() == 5
    assert m.model_mesh([]) is None


# ------------------------------------------------------------------ level


def test_level_places_trees_and_buildings_in_the_viewer_frame():
    flat = quad([-2000, -2000, 0], [2000, -2000, 0], [2000, 2000, 0], [-2000, 2000, 0])
    terrain = [("physics_group", gl(flat[0]), flat[1])]
    cube = np.array([[x, y, z] for z in (0, 100) for y in (-50, 50) for x in (-50, 50)], float)
    cube_tris = np.array([[0, 1, 3], [0, 3, 2], [4, 6, 7], [4, 7, 5], [0, 4, 5], [0, 5, 1], [2, 3, 7], [2, 7, 6], [0, 2, 6], [0, 6, 4], [1, 5, 7], [1, 7, 3]])
    tree_pts = np.array([[0, 0, 0], [40, 0, 50], [-40, 0, 100], [0, 40, 150], [0, -40, 200]], float)
    models = {"models/test/tree_a.vmdl": (tree_pts, np.array([[0, 1, 2]])), "models/test/tower_a.vmdl": (cube, cube_tris)}
    level = m.build(terrain, m.entities_of({"default_ents": LUMP}), models, detail=0)
    names = [n for n, _, _ in level.parts]
    assert names == ["ground:terrain", "structure:tower", "structure:tree"]
    assert (level.trees, level.buildings, level.missing) == (1, 1, [])  # the shop is not drawn
    tower = dict((n, p) for n, p, _ in level.parts)["structure:tower"]
    # Game (-1000, 500, 256..356) -> viewer (X, Z, -Y).
    assert np.allclose(tower.min(axis=0), [-1050, 256, -550]) and np.allclose(tower.max(axis=0), [-950, 356, -450])
    tree = dict((n, p) for n, p, _ in level.parts)["structure:tree"]
    assert np.isclose(tree[:, 1].min(), 128) and np.isclose(tree[:, 1].max(), 128 + 0.5 * 200)
    assert np.allclose(tree[:, [0, 2]].mean(axis=0), [100, -200], atol=15)


def test_a_model_not_found_is_named_and_left_out():
    level = m.build([], m.entities_of({"default_ents": LUMP}), {})
    assert level.parts == [] and level.missing == ["models/test/tower_a.vmdl", "models/test/tree_a.vmdl"]


def test_glb_round_trip(tmp_path):
    pts, tris = quad([0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0])
    glb.write(tmp_path / "a.glb", [("ground:a", pts, tris), ("water:b", pts + 1, tris)])
    doc, blob = glb.read(tmp_path / "a.glb")
    assert doc["asset"]["generator"] == "heat3d_watch"
    meshes = glb.meshes(doc, blob)
    assert [n for n, _, _ in meshes] == ["ground:a", "water:b"]
    assert np.allclose(meshes[1][1][meshes[1][2]].reshape(-1, 3), (pts + 1)[tris].reshape(-1, 3))


# ------------------------------------------------------------------ export, with Source2Viewer played by a stand-in


@pytest.fixture
def install(tmp_path):
    game = tmp_path / "dota 2 beta" / "game" / "dota"
    (game / "maps").mkdir(parents=True)
    (game / "gameinfo.gi").write_text("x")
    (game / "maps" / "dota.vpk").write_bytes(b"")
    (game / "pak01_dir.vpk").write_bytes(b"")
    tool = tmp_path / "Source2Viewer-CLI.exe"
    tool.write_bytes(b"")
    return tmp_path / "dota 2 beta", tool


def fake_source2viewer(calls):
    flat = quad([-2000, -2000, 0], [2000, -2000, 0], [2000, 2000, 0], [-2000, 2000, 0])
    tree = np.array([[0, 0, 0], [40, 0, 50], [0, 40, 100]], float)

    def run(tool, vpk, files, out, extensions=None):
        calls.append((vpk.name, files, extensions))
        out = Path(out)
        if files == ["maps/dota/world_physics.vmdl_c"]:
            glb.write(out.parent / "world_physics_physics.glb", [("physics_group", gl(flat[0]), flat[1])])
            glb.write(out, [])
        elif extensions == "vents_c":
            (out / "maps" / "dota" / "entities").mkdir(parents=True)
            (out / "maps" / "dota" / "entities" / "default_ents.vents").write_text(LUMP, encoding="utf-8")
        else:
            (out / "models" / "test").mkdir(parents=True)
            glb.write(out / "models" / "test" / "tree_a.glb", [("tree_a.vmdl_c.tree_a_model", gl(tree), np.array([[0, 1, 2]]))])
        return subprocess.CompletedProcess([], 0, "", "")

    return run


def test_export_writes_the_level(install, tmp_path, monkeypatch):
    folder, tool = install
    calls = []
    monkeypatch.setattr(m, "_run", fake_source2viewer(calls))
    out = tmp_path / "out" / "dota.glb"
    line = m.export_map("dota", out, game=str(folder), source2viewer=str(tool))
    assert "1 trees, 0 buildings" in line and "1 model(s) not found" in line and "tower_a" in line
    assert [c[0] for c in calls] == ["dota.vpk", "dota.vpk", "pak01_dir.vpk"]
    assert calls[2][1] == ["models/test/tower_a.vmdl_c", "models/test/tree_a.vmdl_c"]
    names = [n for n, _, _ in glb.meshes(*glb.read(out))]
    assert names == ["ground:terrain", "structure:tree"]


def test_cli_says_what_is_missing(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(m, "dota_folders", lambda: [])
    assert cli.main(["dota-map", "-o", str(tmp_path / "x.glb")]) == 1
    assert "Dota 2 not found" in capsys.readouterr().err
    assert cli.main(["dota-map", "-o", str(tmp_path / "x.glb"), "--game", str(tmp_path)]) == 1
    assert "not a Dota 2 folder" in capsys.readouterr().err


def test_install_and_tool_are_found(install, monkeypatch):
    folder, tool = install
    assert m.game_folder(str(folder)) == folder / "game" / "dota"
    assert m.find_vpk("dota", folder / "game" / "dota").name == "dota.vpk"
    with pytest.raises(FileNotFoundError):
        m.find_vpk("nope", folder / "game" / "dota")
    monkeypatch.setenv("HEAT3D_SOURCE2VIEWER", str(tool))
    assert m.find_source2viewer() == tool
