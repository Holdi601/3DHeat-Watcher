"""
DCS World: a small hook script of the watcher's own, sending UDP lines to 127.0.0.1:41993.

DCS runs Lua files in `Saved Games\\DCS*\\Scripts\\Hooks\\` at start; a hook can
read the export functions (`Export.Lo*`) and receive the simulation's callbacks
(`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - see
`<DCS>\\API\\DCS_ControlAPI.html` and https://wiki.hoggitworld.com/view/DCS_Export_Script.
`setup` writes `heat3d-watch.lua` there (its own file: Export.lua and other
tools' hooks are not touched), which sends ten lines a second, one more a
second, and one per game event or callback, never waiting for an answer. The
port is 41993 so JoyPro's hook (41992) and Tacview (42674) keep working beside
it. The lines (fields split by ';'):

    hello;v=2                                       the hook was loaded
    start;mission=..;map=..;me=<player id>;name=..;mp=0|1;file=..;server=0|1
    mis;t=..;date.Day=..;start_time=..;weather...   the mission's date, start time and weather, flattened
    p;t=<model s>;x=;y=;z=;lat=;lon=;alt=;hdg=;pitch=;bank=;ias=;agl=;g=;type=;tas=;mach=;vv=;aoa=;aos=;
      mhdg=;ralt=;gx=;gz=;vx=;vy=;vz=;wx=;wy=;wz=;air=;cx=;cy=;cz=;cfx=;cfy=;cfz=
    d;t=..;self.Name=..;eng.RPM.left=..;mech.gear.value=..;pay.Stations.1.count=..;...   once a second
    ev;t=..;name=<onGameEvent name>;args=a|b|c      every onGameEvent
    cb;t=..;name=<callback>;args=a|b                every other callback (pause, chat, players, loading)
    noexport;t=..                                   the server forbids ownship export
    stop;t=..                                       the mission ended

`p` is LoGetSelfData: Position x/y/z - DCS's own world metres, x north, y up,
z east - plus LatLongAlt (degrees, m), Heading/Pitch/Bank (radians), with
LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) and
LoGetAccelerationUnits() x/y/z (g); and, as `Scripts\\Export.lua` documents
them, LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s),
LoGetAngleOfAttack and LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad),
LoGetRadarAltimeter (m), LoGetVectorVelocity (world m/s), LoGetAngularVelocity
(rad/s), LoGetInAir, and LoGetCameraPosition's point and forward vector (world
metres). `d` is a once-a-second dump of whole tables, flattened to dotted keys:
LoGetSelfData (country, coalition, unit and group names, type levels, flags),
LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo,
LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute,
LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus and a few
numbers (pause, time acceleration, seat, pressure, deviations). The watcher
keeps every line whole in the raw sidecar; `p` also becomes the rows.

Positions go into the same flat map as the other flight sims' (`Tangent`: x
east, y altitude above sea level, z north, metres) from LatLongAlt, around the
theatre's fixed origin (`THEATRES`, from the `map` of the start line), so every
mission on one theatre shares one map, and one the viewer can lay the real
world under. A theatre not in the table takes the first fix's latitude and
longitude rounded to whole degrees. DCS's own x/y/z are kept as `dcs_x`,
`dcs_y`, `dcs_z`; a fix without LatLongAlt cannot be placed and is only
counted (`fixes_without_latlon`). The origin is the session's `geo`, in
meta.json and the table's footer.

onGameEvent's arguments, as DCS_ControlAPI
gives them: takeoff/landing (playerID, unit_missionID, airdromeName),
crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID,
killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide,
weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide),
mission_end (winner, msg).

A multiplayer server can forbid ownship export (LoIsOwnshipExportAllowed is
false); then there are no positions, only events, and the session says so.
"""

from __future__ import annotations

import logging
import math
import os
import re
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from ..session import Session
from .base import Adapter, Context
from .xplane import TANGENT_AXES, FlightLog, Tangent, drain, udp_socket

log = logging.getLogger("heat3d_watch")

PORT = 41993
HOOK_NAME = "heat3d-watch.lua"
MARK = "-- heat3d-watch hook"
BACKUP = ".heat3d-backup"

HOOK = r"""-- heat3d-watch hook 2: sends this flight's position, its aircraft's state and the game's events to the
-- 3DHeat Watcher (UDP 127.0.0.1:__PORT__). Written by `python -m heat3d_watch setup dcs --apply`; delete this
-- file to stop it. It only reads (Export.Lo*, DCS.*, net.*), never changes the simulation and never waits for
-- an answer. One line per datagram, fields split by ';':
--   hello;v=2                                    the hook was loaded
--   start;mission=..;map=..;me=..;name=..;mp=0|1;file=..;server=0|1   a mission began
--   mis;t=..;date.Day=..;...                     the mission's date, start time and weather, flattened
--   p;t=..;x=..;y=..;z=..;lat=..;lon=..;alt=..;hdg=..;pitch=..;bank=..;ias=..;agl=..;g=..;type=..;tas=..;...
--   d;t=..;self.Name=..;eng.RPM.left=..;...      whole export tables, flattened, once a second
--   ev;t=..;name=..;args=a|b|c                   a game event (onGameEvent)
--   cb;t=..;name=..;args=a|b                     any other callback: pause, chat, players, mission loading
--   noexport;t=..                                the server forbids ownship export
--   stop;t=..                                    the mission ended
local ok, err = pcall(function()
    package.path = package.path .. ';.\\LuaSocket\\?.lua'
    package.cpath = package.cpath .. ';.\\LuaSocket\\?.dll'
    local socket = require('socket')
    local udp = socket.udp()
    udp:settimeout(0)
    local SIM = DCS or Sim
    local PORT = __PORT__
    local RATE = 0.1
    local DUMP = 1.0
    local MAXKEYS = 800
    local last = -1
    local dumped = -100
    local quiet = -100
    local fmt = string.format

    local function send(text)
        pcall(udp.sendto, udp, text, '127.0.0.1', PORT)
    end

    local function call(f, ...)
        if type(f) ~= 'function' then return nil end
        local good, a, b, c = pcall(f, ...)
        if good then return a, b, c end
        return nil
    end

    local function lo(name, ...)
        return call(Export and Export[name], ...)
    end

    local function clean(v)
        if v == nil then return '' end
        return (string.gsub(tostring(v), '[;|\r\n]', ' '))
    end

    local function n(v, digits)
        if type(v) ~= 'number' or v ~= v or v == math.huge or v == -math.huge then return '' end
        return fmt('%.' .. digits .. 'f', v)
    end

    local function g10(v)
        if v ~= v or v == math.huge or v == -math.huge then return '' end
        return fmt('%.10g', v)
    end

    local function vec(v, key)
        if type(v) ~= 'table' then return nil end
        return v[key]
    end

    -- A table as dotted keys and values ("eng.RPM.left=85.1"), sorted, at most MAXKEYS of them.
    local function flat(prefix, v, out, depth)
        if #out >= MAXKEYS then return end
        local kind = type(v)
        if kind == 'table' then
            if depth >= 6 then return end
            local keys = {}
            for k in pairs(v) do keys[#keys + 1] = k end
            table.sort(keys, function(a, b) return tostring(a) < tostring(b) end)
            for _, k in ipairs(keys) do
                flat(prefix .. '.' .. string.gsub(tostring(k), '[;|=.\r\n]', '_'), v[k], out, depth + 1)
            end
        elseif kind == 'number' then
            out[#out + 1] = prefix .. '=' .. g10(v)
        elseif kind == 'boolean' then
            out[#out + 1] = prefix .. '=' .. (v and '1' or '0')
        elseif kind == 'string' then
            out[#out + 1] = prefix .. '=' .. clean(v)
        end
    end

    local function now()
        return call(SIM.getModelTime) or 0
    end

    local function dump(t)
        local out = {}
        local tables = {
            {'self', 'LoGetSelfData'}, {'eng', 'LoGetEngineInfo'}, {'mech', 'LoGetMechInfo'},
            {'pay', 'LoGetPayloadInfo'}, {'snares', 'LoGetSnares'}, {'wing', 'LoGetWingInfo'},
            {'wind', 'LoGetVectorWindVelocity'}, {'fm', 'LoGetFMData'}, {'nav', 'LoGetNavigationInfo'},
            {'route', 'LoGetRoute'}, {'mcp', 'LoGetMCPState'}, {'hsi', 'LoGetControlPanel_HSI'},
            {'beacons', 'LoGetRadioBeaconsStatus'},
        }
        for _, e in ipairs(tables) do flat(e[1], lo(e[2]), out, 0) end
        local numbers = {
            {'pause', 'LoSimulationOnPause'}, {'active_pause', 'LoSimulationOnActivePause'},
            {'accel', 'LoGetModelTimeAcceleration'}, {'seat', 'LoGetPlayerSeat'}, {'plane', 'LoGetPlayerPlaneId'},
            {'unit', 'LoGetPlayerUnitId'}, {'pilot', 'LoGetPilotName'}, {'press', 'LoGetBasicAtmospherePressure'},
            {'hobj', 'LoGetHeightWithObjects'}, {'shake', 'LoGetShakeAmplitude'}, {'glide', 'LoGetGlideDeviation'},
            {'side', 'LoGetSideDeviation'}, {'slip', 'LoGetSlipBallPosition'}, {'net', 'LoGetNetIsRunning'},
            {'track', 'LoGetTrackIsReading'}, {'start', 'LoGetMissionStartTime'},
        }
        for _, e in ipairs(numbers) do flat(e[1], lo(e[2]), out, 0) end
        local ap, ab, ay = lo('LoGetADIPitchBankYaw')
        flat('adi', {pitch = ap, bank = ab, yaw = ay}, out, 0)
        send('d;t=' .. n(t, 3) .. ';' .. table.concat(out, ';'))
    end

    local function frame()
        local t = now()
        if t < last then last = -1; dumped = -100 end
        if t - last < RATE then return end
        last = t
        if lo('LoIsOwnshipExportAllowed') == false then
            if t - quiet > 5 then
                quiet = t
                send('noexport;t=' .. n(t, 2))
            end
            return
        end
        local s = lo('LoGetSelfData')
        if type(s) ~= 'table' then return end
        local p = type(s.Position) == 'table' and s.Position or {}
        local g = type(s.LatLongAlt) == 'table' and s.LatLongAlt or {}
        local acc = lo('LoGetAccelerationUnits')
        local vel = lo('LoGetVectorVelocity')
        local rot = lo('LoGetAngularVelocity')
        local cam = lo('LoGetCameraPosition')
        local air = lo('LoGetInAir')
        send(table.concat({
            'p', 't=' .. n(t, 3), 'x=' .. n(p.x, 2), 'y=' .. n(p.y, 2), 'z=' .. n(p.z, 2),
            'lat=' .. n(g.Lat, 7), 'lon=' .. n(g.Long, 7), 'alt=' .. n(g.Alt, 2),
            'hdg=' .. n(s.Heading, 4), 'pitch=' .. n(s.Pitch, 4), 'bank=' .. n(s.Bank, 4),
            'ias=' .. n(lo('LoGetIndicatedAirSpeed'), 2), 'agl=' .. n(lo('LoGetAltitudeAboveGroundLevel'), 2),
            'g=' .. n(vec(acc, 'y'), 3), 'type=' .. clean(s.Name),
            'tas=' .. n(lo('LoGetTrueAirSpeed'), 2), 'mach=' .. n(lo('LoGetMachNumber'), 4),
            'vv=' .. n(lo('LoGetVerticalVelocity'), 2), 'aoa=' .. n(lo('LoGetAngleOfAttack'), 4),
            'aos=' .. n(lo('LoGetAngleOfSideSlip'), 4), 'mhdg=' .. n(lo('LoGetMagneticYaw'), 4),
            'ralt=' .. n(lo('LoGetRadarAltimeter'), 2), 'gx=' .. n(vec(acc, 'x'), 3), 'gz=' .. n(vec(acc, 'z'), 3),
            'vx=' .. n(vec(vel, 'x'), 2), 'vy=' .. n(vec(vel, 'y'), 2), 'vz=' .. n(vec(vel, 'z'), 2),
            'wx=' .. n(vec(rot, 'x'), 4), 'wy=' .. n(vec(rot, 'y'), 4), 'wz=' .. n(vec(rot, 'z'), 4),
            'air=' .. (air == nil and '' or (air and '1' or '0')),
            'cx=' .. n(vec(vec(cam, 'p'), 'x'), 2), 'cy=' .. n(vec(vec(cam, 'p'), 'y'), 2),
            'cz=' .. n(vec(vec(cam, 'p'), 'z'), 2), 'cfx=' .. n(vec(vec(cam, 'x'), 'x'), 4),
            'cfy=' .. n(vec(vec(cam, 'x'), 'y'), 4), 'cfz=' .. n(vec(vec(cam, 'x'), 'z'), 4),
        }, ';'))
        if t - dumped >= DUMP then
            dumped = t
            dump(t)
        end
    end

    local function callback(name, ...)
        local args = {}
        for i = 1, select('#', ...) do args[#args + 1] = clean((select(i, ...))) end
        send('cb;t=' .. n(now(), 3) .. ';name=' .. name .. ';args=' .. table.concat(args, '|'))
    end

    local callbacks = {}
    function callbacks.onSimulationStart()
        last = -1
        dumped = -100
        local theatre = ''
        local m = call(SIM.getCurrentMission)
        if type(m) == 'table' and type(m.mission) == 'table' then theatre = m.mission.theatre or '' end
        local me = net and call(net.get_my_player_id)
        local name = me and net and call(net.get_player_info, me, 'name')
        send(table.concat({
            'start', 'mission=' .. clean(call(SIM.getMissionName)), 'map=' .. clean(theatre),
            'me=' .. clean(me), 'name=' .. clean(name), 'mp=' .. (call(SIM.isMultiplayer) and '1' or '0'),
            'file=' .. clean(call(SIM.getMissionFilename)), 'server=' .. (call(SIM.isServer) and '1' or '0'),
        }, ';'))
        pcall(function()
            local mission = type(m) == 'table' and type(m.mission) == 'table' and m.mission or {}
            local out = {}
            for _, key in ipairs({'date', 'start_time', 'weather', 'sortie', 'theatre', 'version'}) do
                flat(key, mission[key], out, 0)
            end
            send('mis;t=' .. n(now(), 3) .. ';' .. table.concat(out, ';'))
        end)
    end
    function callbacks.onSimulationFrame()
        pcall(frame)
    end
    function callbacks.onSimulationStop()
        send('stop;t=' .. n(now(), 3))
    end
    function callbacks.onGameEvent(name, ...)
        pcall(function(...)
            local args = {}
            for i = 1, select('#', ...) do args[#args + 1] = clean((select(i, ...))) end
            send('ev;t=' .. n(now(), 3) .. ';name=' .. clean(name) .. ';args=' .. table.concat(args, '|'))
        end, ...)
    end
    -- Every other callback that only tells (none that answers: those would change what DCS does).
    for _, name in ipairs({
        'onMissionLoadBegin', 'onMissionLoadProgress', 'onMissionLoadEnd', 'onSimulationPause',
        'onSimulationResume', 'onNetConnect', 'onNetMissionChanged', 'onNetMissionEnd', 'onNetDisconnect',
        'onPlayerConnect', 'onPlayerDisconnect', 'onPlayerStart', 'onPlayerStop', 'onPlayerChangeSlot',
        'onChatMessage', 'onTriggerMessage', 'onRadioMessage', 'onRadioCommand', 'onShowMessage',
    }) do
        callbacks[name] = function(...) pcall(callback, name, ...) end
    end
    SIM.setUserCallbacks(callbacks)
    send('hello;v=2')
end)
if not ok and log and log.write then
    pcall(log.write, 'HEAT3D', log.WARNING, 'heat3d-watch hook not loaded: ' .. tostring(err))
end
"""


#: Each theatre's fixed origin (lat0, lon0 in whole degrees), by DCS's own name for it
#: (mission.theatre, the `map` of the start line). The names are DCS's theatre names as
#: best known; a name not here falls back to the first fix rounded to whole degrees.
#: The table mirrors the viewer's theatre origins (src/world/theatres.ts), so a DCS
#: table and a theatre backdrop share one tangent plane: change both together.
THEATRES: dict[str, tuple[float, float]] = {
    "Caucasus": (42.0, 42.0),
    "Nevada": (36.0, -115.0),
    "Normandy": (49.0, 0.0),
    "TheChannel": (51.0, 2.0),
    "Syria": (34.0, 36.0),
    "PersianGulf": (26.0, 56.0),
    "MarianaIslands": (13.0, 145.0),
    "MarianaIslandsWWII": (13.0, 145.0),
    "Falklands": (-52.0, -58.0),
    "SinaiMap": (30.0, 33.0),
    "Afghanistan": (35.0, 69.0),
    "Kola": (69.0, 33.0),
    "GermanyCW": (51.0, 10.0),
    "Iraq": (33.0, 44.0),
}


def theatre_origin(theatre: str, lat: float, lon: float) -> tuple[float, float]:
    """The flat map's origin: the theatre's own, else the fix rounded to whole degrees (halves up, like the viewer)."""
    known = THEATRES.get(theatre or "")
    if known is not None:
        return known
    return float(math.floor(lat + 0.5)), float(math.floor(lon + 0.5))


#: onGameEvent names whose first argument is the player they happened to.
PLAYER_EVENTS = ("takeoff", "landing", "crash", "eject", "pilot_death", "self_kill", "change_slot", "friendly_fire",
                 "connect", "disconnect")


#: A line's kind as the raw sidecar's `type`: the hook's own words; anything else is "unknown".
KIND = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,23}")


def hook_lua(port: int = PORT) -> str:
    return HOOK.replace("__PORT__", str(int(port)))


def parse_line(line: str) -> tuple[str, dict[str, str]]:
    """`kind;k=v;k=v` -> (kind, {k: v}). Values keep everything after the first '='."""
    parts = line.strip().split(";")
    fields: dict[str, str] = {}
    for p in parts[1:]:
        k, sep, v = p.partition("=")
        if sep:
            fields[k.strip()] = v
    return parts[0].strip(), fields


def number(fields: dict[str, str], key: str) -> float | None:
    try:
        v = float(fields.get(key, ""))
    except ValueError:
        return None
    return v if math.isfinite(v) else None


def saved_games() -> Path:
    return Path(os.environ.get("USERPROFILE") or Path.home()) / "Saved Games"


@dataclass
class DcsAdapter(Adapter):
    port: int = PORT
    #: Where DCS's `Saved Games\DCS*` folders are; empty: the player's Saved Games.
    saved_games: str = ""
    #: Seconds without a position after which a dead pilot's next position is a new life.
    respawn_gap: float = 3.0
    _sock: Any = None
    _session: Session | None = None
    _log: FlightLog | None = None
    _tangent: Tangent | None = None
    #: The theatre the start line named, for the session's origin.
    _map: str = ""
    _me: str = ""
    _mp: bool = False
    _dead: bool = False
    _seen: float = 0.0
    _blocked: bool = False

    # -- setup ---------------------------------------------------------------------------

    def folders(self) -> list[Path]:
        root = Path(self.saved_games) if self.saved_games else saved_games()
        try:
            return sorted(d for d in root.glob("DCS*") if d.is_dir())
        except OSError:
            return []

    def setup(self, ctx: Context, *, apply: bool) -> list[str]:
        folders = self.folders()
        if not folders:
            return ["no Saved Games\\DCS* folder found: start DCS once, then run setup again"]
        text = hook_lua(self.port)
        out: list[str] = []
        for d in folders:
            target = d / "Scripts" / "Hooks" / HOOK_NAME
            if target.exists():
                try:
                    old = target.read_text(encoding="utf-8", errors="replace")
                except OSError as e:
                    out.append(f"leave {target}: cannot read it ({e})")
                    continue
                if old == text:
                    continue
                if not old.startswith(MARK):
                    out.append(f"leave {target}: a file of that name that the watcher did not write")
                    continue
                out.append(f"update {target} (restart DCS)")
                if apply:
                    backup = target.with_name(target.name + BACKUP)
                    if not backup.exists():
                        backup.write_text(old, encoding="utf-8")
                    target.write_text(text, encoding="utf-8")
            else:
                out.append(f"add {target}: sends position and game events to 127.0.0.1:{self.port} (restart DCS)")
                if apply:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(text, encoding="utf-8")
        return out

    # -- running -------------------------------------------------------------------------

    def start(self, ctx: Context) -> None:
        self.stop(ctx)
        self._sock = udp_socket(self.port)

    def poll(self, ctx: Context) -> None:
        for packet, _ in drain(self._sock):
            try:
                text = packet.decode("utf-8", errors="replace")
            except Exception:  # noqa: BLE001 - decode with replace does not fail, but a datagram never stops us
                continue
            for line in text.splitlines():
                if not line.strip():
                    continue
                try:
                    self.line(ctx, line)
                except (ValueError, KeyError, TypeError):
                    if self._session is not None:
                        self._session.stat("bad_packets", 1, "add")

    def _open(self, ctx: Context, **meta: Any) -> Session:
        mp = meta.pop("mp", self._mp)
        s = self._session
        if s is not None and not s.counts:
            # Only lines from before the mission so far (the hook's hello, menu callbacks): the mission
            # joins them instead of leaving them in a folder of their own.
            s.multiplayer = bool(mp)
            s.meta.update({k: v for k, v in meta.items() if v})
        else:
            self._close(ctx)
            s = self._session = ctx.open(self, multiplayer=bool(mp), meta={k: v for k, v in meta.items() if v})
        self._log = FlightLog(s, word="life", plural="lives")
        self._tangent = None
        self._map = ""
        self._dead = False
        self._blocked = False
        return self._session

    def _close(self, ctx: Context) -> None:
        if self._log is not None:
            self._log.end()
        ctx.close(self._session)
        self._session, self._log, self._tangent = None, None, None

    def _keep(self, ctx: Context, kind: str, line: str, used: bool) -> None:
        """Every line whole in the raw sidecar, the ones that made no row too; a line before any mission opens the session."""
        s = self._session or self._open(ctx)
        s.raw(kind if KIND.fullmatch(kind) else "unknown", text=line, used=used)

    def line(self, ctx: Context, line: str) -> None:
        kind, f = parse_line(line)
        try:
            used = self._line(ctx, kind, f, line)
        except (ValueError, KeyError, TypeError):
            # Kept before it is refused: a line nobody can read yet is still the record.
            self._keep(ctx, kind, line, False)
            raise
        if used is not None:
            self._keep(ctx, kind, line, used)

    def _line(self, ctx: Context, kind: str, f: dict[str, str], line: str) -> bool | None:
        """Act on one line; whether it made rows (None: already kept)."""
        used = False
        if kind == "p":
            used = self._position(ctx, f)
        elif kind == "ev":
            used = self._event(ctx, f)
        elif kind == "start":
            self._me = f.get("me", "")
            self._mp = f.get("mp") == "1"
            s = self._open(ctx, map=f.get("map"), mission=f.get("mission"), pilot=f.get("name"), mp=self._mp,
                           mission_file=f.get("file"), server=f.get("server") == "1" or None)
            self._map = f.get("map", "")
            s.event("mission_start", player="me", mission=f.get("mission") or None, map=f.get("map") or None)
            used = True
        elif kind == "stop":
            if self._session is not None:
                self._session.event("mission_stop", player="me", model_time=number(f, "t"))
                used = True
            self._keep(ctx, kind, line, used)
            self._close(ctx)
            return None
        elif kind == "noexport":
            s = self._session or self._open(ctx)
            if not self._blocked:
                # A server rule, not a fault: the session says why it has no track.
                self._blocked = True
                s.event("no_export", player="me", model_time=number(f, "t"))
                s.stat("export_blocked", 1)
                s.meta["no_export"] = "the server forbids ownship export: events only, no positions"
                used = True
        elif kind == "mis":
            # The mission's own date and start time (seconds after midnight) go into meta.json; the weather stays raw.
            s = self._session or self._open(ctx)
            y, m, d = number(f, "date.Year"), number(f, "date.Month"), number(f, "date.Day")
            if y is not None and m is not None and d is not None:
                s.meta["mission_date"] = f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
                used = True
            if number(f, "start_time") is not None:
                s.meta["mission_start_time"] = number(f, "start_time")
                used = True
        elif kind not in ("hello", "d", "cb"):
            raise ValueError(f"unknown line {kind!r}")
        return used

    def _place(self, s: Session, lat: float, lon: float) -> Tangent:
        """The session's flat map, decided at its first fix: the theatre's origin, else the fix rounded."""
        if self._tangent is None:
            self._tangent = Tangent(*theatre_origin(self._map, lat, lon))
            s.geo = self._tangent.geo()
            if self._map:
                # The sim's own metres are in this theatre's projection: said
                # so the viewer can place the dcs_x/dcs_z columns as well.
                s.geo["dcs"] = {"theatre": self._map}
            s.meta["origin"] = self._tangent.meta()
            try:
                s.write_meta()  # said at once: a watcher killed mid-mission still leaves it for recover()
            except OSError:
                pass
        return self._tangent

    def _position(self, ctx: Context, f: dict[str, str]) -> bool:
        """A `p` line as a row; False when it made none (no LatLongAlt, the wreck after a death)."""
        if self._session is None:
            self._open(ctx)
        assert self._session is not None and self._log is not None
        lat, lon, alt = number(f, "lat"), number(f, "lon"), number(f, "alt")
        if lat is None or lon is None or alt is None or not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
            # Without LatLongAlt there is no place on the map for it: counted, not drawn.
            self._session.stat("fixes_without_latlon", 1, "add")
            return False
        now = time.monotonic()
        gap = now - self._seen
        self._seen = now
        if self._dead:
            if gap < self.respawn_gap:
                return False  # the wreck, or the view after death: not a new life yet
            self._dead = False
        air = f.get("air")
        x, y, z = self._place(self._session, lat, lon).local(lat, lon, alt)
        if not self._log.live:
            self._log.begin((x, y, z), event="spawn", aircraft=f.get("type") or None)
        self._log.fix(
            x,
            y,
            z,
            g=number(f, "g"),
            dcs_x=number(f, "x"),
            dcs_y=number(f, "y"),
            dcs_z=number(f, "z"),
            lat=lat,
            lon=lon,
            alt=alt,
            heading=number(f, "hdg"),
            pitch=number(f, "pitch"),
            bank=number(f, "bank"),
            ias=number(f, "ias"),
            agl=number(f, "agl"),
            model_time=number(f, "t"),
            aircraft=f.get("type") or None,
            # Hook 2's numbers, in Export.lua's units: m/s, radians, rad/s, g, DCS's world metres.
            tas=number(f, "tas"),
            mach=number(f, "mach"),
            vertical_speed=number(f, "vv"),
            aoa=number(f, "aoa"),
            sideslip=number(f, "aos"),
            magnetic_heading=number(f, "mhdg"),
            radar_alt=number(f, "ralt"),
            gx=number(f, "gx"),
            gz=number(f, "gz"),
            dcs_vx=number(f, "vx"),
            dcs_vy=number(f, "vy"),
            dcs_vz=number(f, "vz"),
            rate_x=number(f, "wx"),
            rate_y=number(f, "wy"),
            rate_z=number(f, "wz"),
            in_air=int(air == "1") if air in ("0", "1") else None,
            camera_x=number(f, "cx"),
            camera_y=number(f, "cy"),
            camera_z=number(f, "cz"),
            camera_fx=number(f, "cfx"),
            camera_fy=number(f, "cfy"),
            camera_fz=number(f, "cfz"),
        )
        return True

    def _mine(self, pid: str) -> bool:
        if self._me:
            return pid == self._me
        return not self._mp  # alone in the mission, every player event is the player's

    def _end_life(self, event: str, **attrs: Any) -> None:
        assert self._log is not None
        if self._log.live:
            self._log.mark(event, **attrs)
            self._log.end()
        self._dead = True

    def _event(self, ctx: Context, f: dict[str, str]) -> bool:
        """An onGameEvent as a row (every one with a name makes one)."""
        name = f.get("name", "")
        args = f.get("args", "").split("|") if f.get("args") else []
        if self._session is None:
            self._open(ctx)
        s, fl = self._session, self._log
        assert s is not None and fl is not None
        t = number(f, "t")
        arg = lambda i: args[i] if len(args) > i else ""  # noqa: E731
        if name in ("takeoff", "landing") and self._mine(arg(0)):
            fl.mark(name, airfield=arg(2) or None, model_time=t)
        elif name == "crash" and self._mine(arg(0)):
            self._end_life("crash", model_time=t)
        elif name == "eject" and self._mine(arg(0)):
            s.stat("ejections", 1, "add")
            self._end_life("eject", model_time=t)
        elif name in ("pilot_death", "self_kill") and self._mine(arg(0)):
            s.stat("deaths", 1, "add")
            if fl.live:
                fl.end("death", model_time=t, how=name)
            else:
                s.event("death", player="me", model_time=t, how=name)
            self._dead = True
        elif name == "kill":
            killer, victim = arg(0), arg(3)
            detail = dict(killer_type=arg(1) or None, victim_type=arg(4) or None, weapon=arg(6) or None, model_time=t)
            if self._mine(killer) and killer != victim:
                s.stat("kills", 1, "add")
                fl.mark("kill", **detail)
            elif self._mine(victim):
                s.stat("shot_down", 1, "add")
                fl.mark("killed", **detail)
            else:
                s.event("kill", killer_id=killer or None, victim_id=victim or None, **detail)
        elif name == "change_slot" and self._mine(arg(0)):
            if fl.live:
                fl.end()
            self._dead = False
            s.event("change_slot", player="me", slot=arg(1) or None, model_time=t)
        elif name in PLAYER_EVENTS and arg(0) not in ("", "-1"):
            # Someone else's: kept under their id, out of the player's own numbers.
            who = "me" if self._mine(arg(0)) else f"player-{arg(0)}"
            s.event(name, player=who, args=args[1:] or None, model_time=t)
        elif name:
            s.event(name, args=args or None, model_time=t)
        return bool(name)

    def stop(self, ctx: Context) -> None:
        self._close(ctx)
        if self._sock is not None:
            self._sock.close()
            self._sock = None


ADAPTERS = [
    DcsAdapter(
        id="dcs",
        game="DCS World",
        kind="telemetry",
        exes=("DCS.exe",),
        multiplayer=True,
        source=(
            f"the watcher's hook %USERPROFILE%\\Saved Games\\DCS*\\Scripts\\Hooks\\{HOOK_NAME}, "
            f"UDP lines to 127.0.0.1:{PORT}"
        ),
        records=(
            "own position at 10 Hz as metres east/up/north of the theatre's origin (from latitude/longitude/"
            "altitude); lat/lon/alt and DCS's own world metres (dcs_x north, dcs_y up, dcs_z east) as columns",
            "attitude, indicated and true airspeed, Mach, vertical speed, angle of attack and sideslip, magnetic "
            "heading, AGL and radar altitude, g on three axes, velocity and rotation rates, in the air, the camera's "
            "position and forward vector, aircraft type",
            "takeoffs and landings with the airfield; crashes, ejections, pilot deaths",
            "kills and being shot down with both unit types and the weapon; other game events as given",
            "lives per mission (spawn ... session_end), kills, deaths, distance, highest altitude, highest g",
            "every line the hook sends kept whole in heat.raw.parquet, with a once-a-second dump of the aircraft's "
            "export tables (engines, gear and flaps, payload, countermeasures, route, navigation) and every other "
            "callback (pause, chat, players joining, mission loading)",
        ),
        enable=f"python -m heat3d_watch setup dcs --apply (adds Scripts\\Hooks\\{HOOK_NAME}), then restart DCS",
        interval=0.1,
        axes=replace(TANGENT_AXES, units="metres (east, altitude, north from the theatre's origin)"),
        verified=(
            "line format tested with synthetic datagrams; the Lua hook is untested inside DCS "
            "(written from the DCS hook/export API and Scripts\\Export.lua's list of Lo* functions, not run)"
        ),
        completeness={
            "read": (
                "`p` (10 Hz): position, LatLongAlt, attitude, IAS, AGL, g (x/y/z), aircraft type, and hook 2's TAS, "
                "Mach, vertical speed, AoA, sideslip, magnetic heading, radar altitude, world velocity, rotation "
                "rates, in-air and camera point/forward vector - all as row columns (units as Export.lua gives them)",
                "`start`: mission, theatre, own player id and name, multiplayer, mission file, server; `mis`: the "
                "mission's date and start time into meta.json",
                "`ev`: every onGameEvent as a row (takeoff, landing, crash, eject, pilot_death, kill, self_kill, "
                "change_slot, connect, disconnect, friendly_fire, mission_end, any other name as given)",
                "`noexport` and `stop` as rows and meta.json",
            ),
            "raw": (
                "every line the hook sends, whole, as `text` under its kind: `hello`, `start`, `mis`, `p`, `d`, "
                "`ev`, `cb`, `noexport`, `stop`; a line of any other kind under `unknown`",
                "`d` (1 Hz, raw only): LoGetSelfData whole (country, coalition, unit and group name, type levels, "
                "flags), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, wind vector, "
                "LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, radio beacons, pause, time "
                "acceleration, seat, pressure, deviations - flattened to dotted keys",
                "`mis`: the mission's weather table, flattened; `cb`: onSimulationPause/Resume, onMissionLoad*, "
                "onNet*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, "
                "onRadioMessage, onRadioCommand, onShowMessage with their arguments",
            ),
            "missing": (
                "other units (LoGetWorldObjects, LoGetObjectById) and sensor data (LoGetTargetInformation, "
                "LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): not "
                "requested - every object of a mission at 10 Hz is costly inside DCS's own frame, and a server "
                "gates them (allow_object_export, allow_sensor_export); Tacview records them",
                "the whole mission table (DCS.getCurrentMission holds every unit and trigger, megabytes): only its "
                "date, start time, weather, sortie, theatre and version are sent",
                "the onPlayerTry* callbacks: they answer DCS (allow or refuse), so the hook leaves them alone",
                "other players' addresses and UCIDs: net.get_player_info gives them only to a server, and they are "
                "not the player's to keep",
                "a table's entries past 800 keys or 6 levels deep in one `d` line are cut, so one line stays one "
                "datagram",
            ),
            "size": (
                "about 20 MB an hour of `p` lines (10 a second, about 500 bytes each with its frame) and 15-40 MB "
                "of `d` dumps (one a second, 4-10 KB depending on the aircraft's payload and route), before zstd; "
                "the repeated keys compress about tenfold"
            ),
        },
    )
]
