"""Builds the Heat3D recorder mod for an Arma 3 server: @heat3d/, ready to copy.

    python mods/arma3/build.py [out folder]     (default: mods/arma3/@heat3d)

Packs addons/heat3d_recorder into @heat3d/addons/heat3d_recorder.pbo with
Python alone (no Arma 3 Tools needed: the config stays text, which Arma reads
as it is) and copies the extension beside it when it has been built
(extension/heat3d_x64.dll, extension/heat3d_x64.so; see extension/heat3d.c).

PBO layout: a property entry ("Vers") with prefix=<addon>, one header per
file (name, 0, 0, 0, time, size), a blank header, the files' bytes in header
order, then a zero byte and the SHA-1 of everything before it.
"""

from __future__ import annotations

import hashlib
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADDON = "heat3d_recorder"
VERS = 0x56657273


def pack(folder: Path, prefix: str) -> bytes:
    """A folder as a PBO: every file but the prefix file, paths with backslashes."""
    files = sorted(
        (p for p in folder.rglob("*") if p.is_file() and p.name != "$PBOPREFIX$"),
        key=lambda p: p.relative_to(folder).as_posix().lower(),
    )
    head = bytearray()
    head += b"\0" + struct.pack("<5I", VERS, 0, 0, 0, 0)
    head += b"prefix\0" + prefix.encode() + b"\0" + b"\0"
    blobs = []
    for p in files:
        data = p.read_bytes()
        name = str(p.relative_to(folder)).replace("/", "\\")
        head += name.encode() + b"\0" + struct.pack("<5I", 0, 0, 0, int(p.stat().st_mtime), len(data))
        blobs.append(data)
    head += b"\0" + struct.pack("<5I", 0, 0, 0, 0, 0)
    body = bytes(head) + b"".join(blobs)
    return body + b"\0" + hashlib.sha1(body).digest()


def unpack(pbo: bytes) -> tuple[dict[str, str], dict[str, bytes]]:
    """A PBO's properties and files; checks its SHA-1. The inverse of pack, for tests."""
    body, zero, digest = pbo[:-21], pbo[-21:-20], pbo[-20:]
    if zero != b"\0" or hashlib.sha1(body).digest() != digest:
        raise ValueError("bad PBO checksum")
    i = 0

    def cstr() -> str:
        nonlocal i
        j = body.index(b"\0", i)
        s = body[i:j].decode()
        i = j + 1
        return s

    props: dict[str, str] = {}
    headers: list[tuple[str, int]] = []
    while True:
        name = cstr()
        mime, _orig, _res, _time, size = struct.unpack_from("<5I", body, i)
        i += 20
        if mime == VERS:
            while (key := cstr()) != "":
                props[key] = cstr()
            continue
        if name == "" and size == 0:
            break
        headers.append((name, size))
    files = {}
    for name, size in headers:
        files[name] = body[i : i + size]
        i += size
    return props, files


def build(out: Path) -> Path:
    src = HERE / "addons" / ADDON
    prefix = (src / "$PBOPREFIX$").read_text(encoding="utf-8").strip() or ADDON
    (out / "addons").mkdir(parents=True, exist_ok=True)
    (out / "addons" / f"{ADDON}.pbo").write_bytes(pack(src, prefix))
    for lib in ("heat3d_x64.dll", "heat3d_x64.so"):
        if (HERE / "extension" / lib).is_file():
            shutil.copy2(HERE / "extension" / lib, out / lib)
    (out / "mod.cpp").write_text('name = "Heat3D recorder";\nauthor = "3DHeat";\n', encoding="utf-8")
    return out


if __name__ == "__main__":
    target = build(Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "@heat3d")
    print(f"built {target}")
    for p in sorted(target.rglob("*")):
        if p.is_file():
            print(f"  {p.relative_to(target)}  {p.stat().st_size} bytes")
    if not any((target / lib).exists() for lib in ("heat3d_x64.dll", "heat3d_x64.so")):
        print("  no extension yet: build extension/heat3d.c first (see the README)")
