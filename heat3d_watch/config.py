"""
Where the watcher keeps what it records, and the few settings it has.

Everything lives under one folder - `%LOCALAPPDATA%\\3DHeat\\Watcher` unless
`HEAT3D_WATCH_HOME` or the settings say otherwise - so a player can see, copy
or delete all of it in one place. Nothing is sent anywhere.
"""

from __future__ import annotations

import json
import os
import typing
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


def home() -> Path:
    env = os.environ.get("HEAT3D_WATCH_HOME")
    if env:
        return Path(env)
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / ".local" / "share")
    return Path(base) / "3DHeat" / "Watcher"


@dataclass
class Settings:
    #: Where sessions and the statistics database go. Empty: `home()`.
    data: str = ""
    #: Adapters switched off by id. Everything else that finds its game runs.
    disabled: list[str] = field(default_factory=list)
    #: Update the tools from GitHub releases while no game is running.
    auto_update: bool = True
    #: Seconds between looks at which games are running.
    scan_seconds: float = 2.0
    #: Read single-player games' memory where a profile exists for the exact build.
    #: Off by default: it is the one source that is not the game's own output.
    memory: bool = False
    #: Watch the folders games save replays and demos to, and convert new ones.
    replays: bool = True
    #: Extra folders to look for replays in, by adapter id.
    replay_folders: dict[str, list[str]] = field(default_factory=dict)
    #: Your Riot ID ("Name#TAG"), so a League of Legends replay's line of yours
    #: becomes your statistics. Empty: every player's line is kept, none is yours.
    riot_id: str = ""
    #: A Riot developer API key of your own (developer.riotgames.com), to fetch
    #: each replayed match's official timeline - every player's position each
    #: minute and every kill where it happened. Empty: nothing is fetched.
    riot_api_key: str = ""
    #: Your League of Legends server's platform id: EUW1, EUN1, NA1, KR, ...
    riot_platform: str = "EUW1"
    #: Your name in games whose interface names every player but not which one is
    #: you, by adapter id: {"warthunder-webmap": "Name", "rocketleague-stats": "Name"}.
    #: Rows of that name become the player's own ("me"); empty: as the adapter says.
    player_names: dict[str, str] = field(default_factory=dict)

    @property
    def data_dir(self) -> Path:
        return Path(self.data) if self.data else home()


def settings_path() -> Path:
    return home() / "settings.json"


def kind(key: str) -> type:
    """A setting's type, as declared: str, bool, float, int, list or dict."""
    hint = typing.get_type_hints(Settings)[key]
    return typing.get_origin(hint) or hint


def parse(key: str, text: str) -> Any:
    """
    A setting's value from the text typed after `--set key=`, by the setting's
    type: `true`/`false` (also 1/0, yes/no, on/off), a number, a list as JSON or
    comma-separated, a dictionary as JSON. ValueError when the text is not one.
    """
    want = kind(key)
    text = text.strip()
    if want is bool:
        low = text.lower()
        if low in ("1", "true", "yes", "on", "ja"):
            return True
        if low in ("0", "false", "no", "off", "nein", ""):
            return False
        raise ValueError(f"{key} is true or false, not {text!r}")
    if want in (int, float):
        try:
            return want(text)
        except ValueError:
            raise ValueError(f"{key} is a number, not {text!r}") from None
    if want is list:
        if text.startswith("["):
            value = json.loads(text)
            if not isinstance(value, list):
                raise ValueError(f"{key} is a list")
            return [str(v) for v in value]
        return [v.strip() for v in text.split(",") if v.strip()]
    if want is dict:
        value = json.loads(text) if text else {}
        if not isinstance(value, dict):
            raise ValueError(f"{key} is a dictionary, as JSON: {{\"id\": ...}}")
        return {str(k): _item(key, v) for k, v in value.items()}
    return text


def parse_item(key: str, text: str) -> Any:
    """One entry of a dictionary setting, from `--set key.id=...`: a list comma-separated, else the text."""
    return _item(key, text.strip(), split=True)


def _item(key: str, value: Any, *, split: bool = False) -> Any:
    args = typing.get_args(typing.get_type_hints(Settings)[key])
    inner = typing.get_origin(args[1]) if len(args) == 2 else None
    if inner is list:
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()] if split else [value]
        if isinstance(value, list):
            return [str(v) for v in value]
        raise ValueError(f"{key}: each entry is a list of text")
    if not isinstance(value, str):
        raise ValueError(f"{key}: each entry is text")
    return value


def _fits(key: str, value: Any) -> bool:
    want = kind(key)
    if want is float:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if want is dict and isinstance(value, dict):
        try:
            return all(_item(key, v) == v for v in value.values())
        except ValueError:
            return False
    return isinstance(value, want)


def load() -> Settings:
    try:
        raw = json.loads(settings_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return Settings()
    known = {f for f in Settings.__dataclass_fields__}
    values = {}
    for k, v in raw.items() if isinstance(raw, dict) else ():
        if k not in known:
            continue
        if not _fits(k, v) and isinstance(v, str):
            # Written as text by hand (or by an older `config --set`): read it as typed.
            try:
                v = parse(k, v)
            except ValueError:
                continue
        if _fits(k, v):
            values[k] = v
    return Settings(**values)


def save(s: Settings) -> Path:
    p = settings_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(asdict(s), indent=2), encoding="utf-8")
    return p
