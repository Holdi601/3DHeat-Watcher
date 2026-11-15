"""
Dota 2 replays: a public match's replay, downloaded by its match id.

Dota 2 keeps a replay of every public match on Valve's servers for a few weeks.
The client saves the ones a player downloads (Watch > Replays, or a match's
"Download replay") to `<Dota>/game/dota/replays/<match id>.dem`; anyone can
fetch one from Valve's replay CDN with the match's cluster and replay salt, which
OpenDota's API gives for a match id (`fetch_replay`). This is what
`python -m heat3d_watch dota-replay <match id>` does.

Reading a replay is not done here: the external reader does it (3DHeat Dota
Replay, github.com/Holdi601/3DHeat-Ext-DotaReplay, `heat3d-dota-replay`), run
by the `dota-replays` adapter (heat3d_watch/adapters/replays.py).
"""

from __future__ import annotations

import bz2
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

#: A Source 2 demo's first eight bytes.
DEMO_MAGIC = b"PBDEMS2\0"
OPENDOTA = "https://api.opendota.com/api"


class FormatError(ValueError):
    """The download is not a Dota 2 replay."""


class Missing(RuntimeError):
    """A package the download needs is not installed."""


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
