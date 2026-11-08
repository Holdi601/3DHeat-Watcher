"""
Everything a Dota 2 replay holds that the table and the match document do not
hold whole, kept whole beside them, and the self-check of where each thing
went - the rule all 3DHeat converters follow:
https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md

A replay is a Source 2 demo: frames (a command, a tick, a size, the bytes),
most of them packets of network messages. `Keeper` rides on the same parse as
the hero sampler (`dota_replay._parse_with_sampler`) and sees every frame and
every message as gem reads them, in file order. Three sidecars, each with
`time` on the table's clock and the replay's `tick`:

- `<match>.packets.parquet`: every frame that is not a packet and every
  network message, whole (`payload`), with what its protobuf says
  (`decoded`, JSON; a bytes field is given as its length, the bytes being in
  `payload`). The protobuf class of each message is Valve's, from the
  definitions gem ships; each was checked by reading samples of the real
  replay and writing them back byte for byte. The entity stream
  (svc_PacketEntities) is here whole, with what a later decoder needs to read
  it alone: the send tables, the class list, the server info and the
  baselines (in the strings sidecar).
- `<match>.entities.parquet`: every entity's every property, decoded, each
  time it changed (one row per change: tick, entity, class, property, value),
  every entity's whole state when it was created, and every entity created,
  entering, leaving and deleted.
- `<match>.strings.parquet`: every entry of every string table, from each
  table update as the stream sends it and from each full snapshot, the
  value whole (`payload`) and, for the tables whose entries are protobufs
  (players, modifiers, cosmetic items), decoded.

Nothing is thinned in them. The self-check (`completeness`) counts, for each
kind of thing the replay holds, how many there were and where they went.
"""

from __future__ import annotations

import json
import math
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

RULE = "https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md"
#: The sidecars, by `<what>`.
SIDECARS = ("packets", "entities", "strings")

#: The protobuf modules (gem's, Valve's definitions) the message classes are looked up in.
PROTO_MODULES = (
    "networkbasetypes_pb2", "netmessages_pb2", "usermessages_pb2", "gameevents_pb2", "te_pb2", "dota_usermessages_pb2",
    "dota_commonmessages_pb2", "dota_shared_enums_pb2", "dota_match_metadata_pb2", "dota_gcmessages_common_pb2",
    "prediction_events_pb2", "demo_pb2", "dota_modifiers_pb2", "base_gcmessages_pb2",
)  # fmt: skip
#: The enums that number the messages a packet carries.
MESSAGE_ENUMS = (
    "NET_Messages", "SVC_Messages", "EBaseUserMessages", "EBaseEntityMessages", "EBaseGameEvents", "ETEProtobufIds",
    "EDotaUserMessages", "EDotaEntityMessages", "EBasePredictionEvents",
)  # fmt: skip
#: Messages whose class does not follow from their name.
SPECIAL = {
    "DOTA_UM_CombatLogDataHLTV": "CMsgDOTACombatLogEntry",
    "DOTA_UM_MatchMetadata": "CDOTAMatchMetadataFile",
    "DOTA_UM_MatchDetails": "CMsgDOTAMatch",
}
#: String tables whose values are protobufs: table -> class.
STRING_CLASSES = {"userinfo": "CMsgPlayerInfo", "ActiveModifiers": "CDOTAModifierBuffTableEntry", "EconItems": "CSOEconItem"}
#: String tables the conversion reads besides those: names of units and of the combat log's words, entity baselines.
STRINGS_READ = {"EntityNames", "CombatLogNames", "instancebaseline"}
#: Frames read whole into the match document.
FRAMES_IN_DOCUMENT = {"DEM_FileHeader", "DEM_FileInfo"}
#: Messages read whole into the match document.
MESSAGES_IN_DOCUMENT = {"DOTA_UM_MatchMetadata", "DOTA_UM_MatchDetails"}
#: Frames that hold network messages (their protobuf), split into them here; the full packet also holds a
#: string table snapshot.
PACKET_FRAMES = {7: "CDemoPacket", 8: "CDemoPacket", 13: "CDemoFullPacket"}
#: svc_CreateStringTable, svc_UpdateStringTable: the messages that set string table entries.
TABLE_MESSAGES = (44, 45)

#: Entity operations (gem's flags).
CREATED, UPDATED, DELETED, ENTERED, LEFT = 0x01, 0x02, 0x04, 0x08, 0x10
#: Whole numbers a float64 holds exactly; larger ones (handles of 64 bits, steam ids) are kept as text.
EXACT = 2**53
#: Rows held before they are written.
FLUSH_ROWS = 400_000
FLUSH_BYTES = 48 << 20


class _Protos:
    """Message numbers -> Valve's names and protobuf classes, from gem's definitions; built once."""

    def __init__(self) -> None:
        import importlib

        self.classes: dict[str, Any] = {}
        self.names: dict[int, str] = {}
        self.frames: dict[int, str] = {}
        self.orders: dict[int, str] = {}
        for m in PROTO_MODULES:
            try:
                mod = importlib.import_module("gem.proto." + m)
            except Exception:  # noqa: BLE001 - a module a gem release lacks: its messages stay raw
                continue
            for n in mod.DESCRIPTOR.message_types_by_name:
                self.classes.setdefault(n, getattr(mod, n))
            for en, ed in mod.DESCRIPTOR.enum_types_by_name.items():
                if en in MESSAGE_ENUMS:
                    for v in ed.values:
                        self.names.setdefault(v.number, v.name)
                elif en == "EDemoCommands":
                    self.frames = {v.number: v.name for v in ed.values}
                elif en == "dotaunitorder_t":
                    # Unit orders by number: `move_to_position`, `cast_target`, ...
                    self.orders = {v.number: v.name.removeprefix("DOTA_UNIT_ORDER_").lower() for v in ed.values}
        self.by_id: dict[int, Any] = {}
        for number, name in self.names.items():
            cls = self.classes.get(SPECIAL.get(name, "")) or next((self.classes[c] for c in _candidates(name)
                                                                   if c in self.classes), None)
            if cls is not None:
                self.by_id[number] = cls

    def frame_class(self, name: str) -> Any:
        return self.classes.get("CDemo" + name.removeprefix("DEM_"))


def _candidates(name: str) -> Iterable[str]:
    """A message's class, by Valve's naming: `svc_ServerInfo` -> `CSVCMsg_ServerInfo`, ..."""
    for prefix, cls in (("net_", "CNETMsg_"), ("svc_", "CSVCMsg_"), ("UM_", "CUserMessage"), ("UM_", "CUserMsg_"),
                        ("EM_", "CEntityMessage"), ("GE_", "CMsg"), ("DOTA_UM_", "CDOTAUserMsg_")):
        if name.startswith(prefix):
            yield cls + name[len(prefix):]
    if name.startswith("TE_"):
        yield "CMsgTE" + name[3:].removesuffix("Id")


_PROTOS: _Protos | None = None


def protos() -> _Protos:
    global _PROTOS
    if _PROTOS is None:
        _PROTOS = _Protos()
    return _PROTOS


def to_json(msg: Any) -> dict[str, Any]:
    """
    A protobuf message as plain JSON values, by its own field names: the
    fields it has, enums by name, a bytes field as `{"bytes": length}` (the
    bytes are in the row's payload), non-finite floats as null.
    """
    out: dict[str, Any] = {}
    for f, v in msg.ListFields():
        # `label` is gone from newer protobuf releases, `is_repeated` missing from older ones.
        if f.is_repeated if hasattr(f, "is_repeated") else f.label == f.LABEL_REPEATED:
            if f.message_type is not None and f.message_type.GetOptions().map_entry:
                out[f.name] = {str(k): _value(f.message_type.fields_by_name["value"], x) for k, x in v.items()}
            else:
                out[f.name] = [_value(f, x) for x in v]
        else:
            out[f.name] = _value(f, v)
    return out


def _value(f: Any, v: Any) -> Any:
    t = f.type
    if t == f.TYPE_MESSAGE:
        return to_json(v)
    if t == f.TYPE_BYTES:
        return {"bytes": len(v)}
    if t == f.TYPE_ENUM:
        e = f.enum_type.values_by_number.get(v)
        return e.name if e is not None else v
    if isinstance(v, float) and not math.isfinite(v):
        return None
    return v


def _dumps(v: Any) -> str:
    return json.dumps(v, ensure_ascii=False, separators=(",", ":"), default=str)


# ---------------------------------------------------------------- entity property names


def path_name(serializer: Any, path: tuple[int, ...]) -> str:
    """
    A property's name from its field path, as gem's `Entity.get` takes it:
    levels joined by dots, array and table rows as four digits
    (`m_hItems.0003`, `m_vecPlayerTeamData.0004.m_iKills`).
    """
    from gem.schema.sendtable import (
        FIELD_MODEL_FIXED_ARRAY,
        FIELD_MODEL_FIXED_TABLE,
        FIELD_MODEL_VARIABLE_ARRAY,
        FIELD_MODEL_VARIABLE_TABLE,
    )

    parts: list[str] = []
    s, pos, n = serializer, 0, len(path)
    while pos < n:
        fields = getattr(s, "fields", None)
        if fields is None or not 0 <= path[pos] < len(fields):
            parts += [f"{i:04d}" for i in path[pos:]]
            break
        f = fields[path[pos]]
        parts.append(f.var_name)
        pos += 1
        if pos >= n:
            break
        model = f.model
        if model in (FIELD_MODEL_FIXED_ARRAY, FIELD_MODEL_VARIABLE_ARRAY):
            parts.append(f"{path[pos]:04d}")
            pos += 1
            if pos < n:
                parts += [f"{i:04d}" for i in path[pos:]]
            break
        if model == FIELD_MODEL_FIXED_TABLE:
            s = f.serializer
        elif model == FIELD_MODEL_VARIABLE_TABLE:
            parts.append(f"{path[pos]:04d}")
            pos += 1
            s = f.serializer
        else:
            parts += [f"{i:04d}" for i in path[pos:]]
            break
    return ".".join(parts)


# ---------------------------------------------------------------- the keeper


class _Part:
    """One sidecar while the parse runs: rows held as columns, written in batches to `<file>.part` (no time yet)."""

    def __init__(self, path: Path, schema: Any, dictionary: list[str]) -> None:
        import pyarrow.parquet as pq

        self.path = path
        self.schema = schema
        self.cols: dict[str, list] = {n: [] for n in schema.names}
        self.size = 0
        self.rows = 0
        self.writer = pq.ParquetWriter(path, schema, compression="zstd", use_dictionary=dictionary)

    def flush(self) -> None:
        import pyarrow as pa

        if not self.cols[self.schema.names[0]]:
            return
        self.writer.write_table(pa.table({n: pa.array(self.cols[n], self.schema.field(n).type) for n in self.schema.names},
                                         schema=self.schema))
        for v in self.cols.values():
            v.clear()
        self.size = 0

    def close(self) -> None:
        self.flush()
        self.writer.close()


def _schemas() -> dict[str, Any]:
    import pyarrow as pa

    return {
        "packets": pa.schema([
            ("tick", pa.int32()), ("seq", pa.int64()), ("frame", pa.int64()), ("type", pa.string()),
            ("name", pa.string()), ("id", pa.int32()), ("decoded", pa.string()), ("payload", pa.binary()),
        ]),
        "entities": pa.schema([
            ("tick", pa.int32()), ("type", pa.string()), ("name", pa.string()), ("entity", pa.int32()),
            ("value", pa.float64()), ("vector", pa.list_(pa.float32())), ("decoded", pa.string()),
        ]),
        "strings": pa.schema([
            ("tick", pa.int32()), ("seq", pa.int64()), ("source", pa.string()), ("type", pa.string()),
            ("name", pa.string()), ("entity", pa.int32()), ("flags", pa.int32()), ("decoded", pa.string()),
            ("payload", pa.binary()),
        ]),
    }  # fmt: skip


#: Dictionary-encoded columns of each sidecar.
DICTIONARY = {"packets": ["type", "name"], "entities": ["type", "name"], "strings": ["source", "type", "name"]}


class Keeper:
    """
    The sidecars of one replay, filled while gem parses it, and the counts
    behind `selfCheck.completeness`: per type [seen, decoded, partial, raw].

    `outer`, `inner` and `strings` are called by the parser subclass for each
    frame, each packet's messages and each string table change; `_entity` by
    gem for each entity created, changed or gone. `events` collects what goes
    into the table: map pings, map drawings and every player's orders.
    """

    def __init__(self, parser: Any, folder: str | Path, stem: str) -> None:
        self.p = parser
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.stem = stem
        self.pr = protos()
        schemas = _schemas()
        self.parts = {w: _Part(self.folder / f"{stem}.{w}.parquet.part", schemas[w], DICTIONARY[w]) for w in SIDECARS}
        self.types: dict[str, list[int]] = {}
        self.seq = 0
        self.frame = -1
        #: The rows of the packet's string table messages not yet applied by gem, in stream order, and the one it is
        #: applying: the entries it sets name the message they came in.
        self._table_messages: list[int] = []
        self._table_message = -1
        #: Decoded whole into the match document: frame or message name -> JSON.
        self.document: dict[str, Any] = {}
        #: Rows for the table: (tick, event, slot, x, y, other, value, text).
        self.events: list[tuple] = []
        self._full_entities = 0
        self._names: dict[int, dict[tuple, str]] = {}
        self._entity_types: dict[str, list[int]] = {}
        self.errors: dict[str, int] = {}
        parser.on_entity(self._entity)

    # ------------------------------------------------------------ counting

    def count(self, key: str, status: str) -> None:
        """One item of `key` met and put: `decoded`, `partial` or `raw`."""
        c = self.types.get(key)
        if c is None:
            c = self.types[key] = [0, 0, 0, 0]
        c[0] += 1
        c[{"decoded": 1, "partial": 2, "raw": 3}[status]] += 1

    def _row(self, what: str, **row: Any) -> None:
        part = self.parts[what]
        cols = part.cols
        for k in part.schema.names:
            cols[k].append(row.get(k))
        part.rows += 1
        payload = row.get("payload")
        part.size += len(payload) if payload else 0
        if len(cols["tick"]) >= FLUSH_ROWS or part.size >= FLUSH_BYTES:
            part.flush()

    # ------------------------------------------------------------ frames

    def outer(self, msg_type: int, data: bytes) -> None:
        """A frame of the demo, before gem reads it."""
        tick = int(self.p.tick)
        self.frame += 1
        name = self.pr.frames.get(msg_type, "")
        key = name or f"frame {msg_type}"
        if msg_type in PACKET_FRAMES:
            try:
                m = self.pr.classes[PACKET_FRAMES[msg_type]]()
                m.ParseFromString(data)
            except Exception:  # noqa: BLE001 - kept whole below, and gem stops on it
                m = None
            if m is None:
                self._frame_row(tick, msg_type, name, "", data)
                self.count(key, "raw")
                return
            known = {"data"} if msg_type != 13 else {"string_table", "packet"}
            other = [f.name for f, _ in m.ListFields() if f.name not in known]
            if msg_type == 13 and m.HasField("string_table"):
                self.snapshot(tick, m.string_table)
            if other:
                # More than its messages: the frame whole, besides.
                self._frame_row(tick, msg_type, name, _dumps(to_json(m)), data)
            # Its messages each get a row of their own (`inner`): the frame is read in part, kept in parts.
            self.count(key, "partial")
            return
        decoded = ""
        cls = self.pr.frame_class(name) if name else None
        if cls is not None:
            try:
                m = cls()
                m.ParseFromString(data)
                d = to_json(m)
                decoded = _dumps(d)
                if name in FRAMES_IN_DOCUMENT:
                    self.document[name] = d
                if name == "DEM_StringTables":
                    self.snapshot(tick, m)
            except Exception:  # noqa: BLE001 - kept whole, undecoded
                self.errors[key] = self.errors.get(key, 0) + 1
                decoded = ""
        self._frame_row(tick, msg_type, name, decoded, data)
        self.count(key, "decoded" if decoded and name in FRAMES_IN_DOCUMENT else "partial" if decoded else "raw")

    def _frame_row(self, tick: int, msg_type: int, name: str, decoded: str, data: bytes) -> None:
        self._row("packets", tick=tick, seq=self.seq, frame=self.frame, type=f"frame {msg_type}", name=name, id=msg_type,
                  decoded=decoded, payload=bytes(data))
        self.seq += 1

    # ------------------------------------------------------------ messages

    def inner(self, data: bytes) -> None:
        """A packet's messages, in the order the packet has them, before gem reads them."""
        from gem.binary.packet import read_inner_messages

        tick = int(self.p.tick)
        try:
            messages = read_inner_messages(data)
        except Exception:  # noqa: BLE001 - a packet that does not split: whole, as it is
            self._row("packets", tick=tick, seq=self.seq, frame=self.frame, type="packet", name="", id=-1, decoded="",
                      payload=bytes(data))
            self.seq += 1
            self.count("packet (does not split)", "raw")
            return
        self._table_messages.clear()
        for number, payload in messages:
            if number in TABLE_MESSAGES:
                self._table_messages.append(self.seq)
            self.message(tick, number, payload)

    def table_message(self) -> None:
        """gem is about to apply the packet's next string table message (they keep their order)."""
        self._table_message = self._table_messages.pop(0) if self._table_messages else -1

    def message(self, tick: int, number: int, payload: bytes) -> None:
        name = self.pr.names.get(number, "")
        key = name or f"message {number}"
        cls = self.pr.by_id.get(number)
        decoded: dict[str, Any] | None = None
        status = "raw"
        if cls is not None:
            try:
                m = cls()
                m.ParseFromString(payload)
                decoded = to_json(m)
                key, status = self._read(number, name, m, decoded, tick)
            except Exception:  # noqa: BLE001 - kept whole, undecoded
                self.errors[key] = self.errors.get(key, 0) + 1
                decoded, status = None, "raw"
        self._row("packets", tick=tick, seq=self.seq, frame=self.frame, type=f"message {number}", name=name, id=number,
                  decoded="" if decoded is None else _dumps(decoded), payload=bytes(payload))
        self.seq += 1
        self.count(key, status)

    def _read(self, number: int, name: str, m: Any, decoded: dict[str, Any], tick: int) -> tuple[str, str]:
        """What is made of a decoded message besides its row: the type it counts under, and how far it is read."""
        if name == "svc_PacketEntities":
            if not m.legacy_is_delta:
                self._full_entities += 1
                if self._full_entities > 1:
                    # A full snapshot after the first: gem rebuilds entities from the deltas, so its contents are
                    # kept whole here but not decoded into the entities sidecar.
                    return name, "raw"
            return name, "partial"
        if name == "GE_Source1LegacyGameEvent":
            from gem.state.game_events import GameEvent

            schema = self.p.game_event_manager.get_schema(m.eventid)
            if schema is None:
                return f"gameevent {m.eventid}", "partial"
            decoded["event"] = schema.name
            decoded["values"] = GameEvent(schema=schema, msg=m).to_dict()
            return f"gameevent {schema.name}", "partial"
        if name == "svc_UserMessage":
            inner = self.pr.by_id.get(m.msg_type)
            inner_name = self.pr.names.get(m.msg_type, f"message {m.msg_type}")
            if inner is not None:
                um = inner()
                um.ParseFromString(m.msg_data)
                decoded["msg"] = to_json(um)
            return f"svc_UserMessage {inner_name}", "partial"
        if name == "DOTA_UM_CombatLogDataHLTV":
            kind = str(decoded.get("type", "")).removeprefix("DOTA_COMBATLOG_")
            return f"combatlog {kind}", "partial"
        if name in MESSAGES_IN_DOCUMENT:
            self.document[name] = decoded
            return name, "decoded"
        if name == "DOTA_UM_LocationPing":
            ping = m.location_ping
            self.events.append((tick, "ping", m.player_id, float(ping.x), float(ping.y), decoded["location_ping"].get(
                "ping_source", ""), float(ping.type) if ping.HasField("type") else None, "direct" if ping.direct_ping else ""))
        elif name == "DOTA_UM_MapLine":
            self.events.append((tick, "map_line", m.player_id, float(m.mapline.x), float(m.mapline.y), "",
                                1.0 if m.mapline.initial else 0.0, ""))
        elif name == "DOTA_UM_SpectatorPlayerUnitOrders":
            self._order(tick, m, decoded)
        return name, "partial"

    def _order(self, tick: int, m: Any, decoded: dict[str, Any]) -> None:
        """A player's order: at the point it names, or (no point) where the player's hero then stands."""
        manager = getattr(self.p, "entity_manager", None)
        e = manager.find(m.entindex) if manager is not None else None
        slot = -1
        if e is not None:
            for k in ("m_nPlayerID", "m_iPlayerID", "m_nPlayerOwnerID"):
                v = e.get(k)
                if isinstance(v, int) and 0 <= v <= 23:
                    slot = v
                    break
        decoded["player"] = slot
        if slot < 0:
            return
        order = self.pr.orders.get(m.order_type) or str(m.order_type)
        decoded["order"] = order
        x = y = None
        if m.HasField("position") and (m.position.x or m.position.y):
            x, y = float(m.position.x), float(m.position.y)
        ability = float(m.ability_id) if m.HasField("ability_id") and m.ability_id > 0 else None
        self.events.append((tick, "order", slot, x, y, order, ability, _target(manager, m.target_index)))

    # ------------------------------------------------------------ string tables

    def snapshot(self, tick: int, tables: Any) -> None:
        """A full snapshot of the string tables (a CDemoStringTables), every entry whole."""
        seq = self.seq
        self.seq += 1
        for t in tables.tables:
            name = t.table_name
            # The table itself: its flags, and its fields beyond its entries, whole.
            rest = [f.name for f, _ in t.ListFields() if f.name not in ("table_name", "items", "items_clientside",
                                                                         "table_flags")]
            self._row("strings", tick=tick, seq=seq, source="snapshot", type=name, name=None, entity=-1,
                      flags=t.table_flags, decoded=_dumps({k: to_json(t)[k] for k in rest}) if rest else "",
                      payload=t.SerializeToString() if rest else None)
            for clientside, items in ((False, t.items), (True, t.items_clientside)):
                for i, item in enumerate(items):
                    self._entry(tick, seq, "snapshot clientside" if clientside else "snapshot", name, i, item.str,
                                item.data, t.table_flags)

    def strings(self, table: Any, items: list[Any]) -> None:
        """Entries a table update (or the table's creation) set, as the parser read them."""
        tick = int(self.p.tick)
        seq = self._table_message
        entries = table.items
        for item in items:
            current = entries.get(item.index)
            key = current[0] if current is not None else item.key
            self._entry(tick, seq, "message", table.name, item.index, key, item.value, table.flags)

    def _entry(self, tick: int, seq: int, source: str, table: str, index: int, key: str | None, value: bytes | None,
               flags: int) -> None:
        decoded = ""
        cls_name = STRING_CLASSES.get(table)
        if cls_name and value:
            cls = self.pr.classes.get(cls_name)
            if cls is not None:
                try:
                    m = cls()
                    m.ParseFromString(value)
                    decoded = _dumps(to_json(m))
                except Exception:  # noqa: BLE001 - kept whole, undecoded
                    decoded = ""
        self._row("strings", tick=tick, seq=seq, source=source, type=table, name=key, entity=index, flags=flags,
                  decoded=decoded, payload=bytes(value) if value is not None else None)
        # An entry that is only a name is read whole as its key; one with a value nothing decodes is kept raw.
        self.count(f"stringtable {table}", "partial" if decoded or table in STRINGS_READ or not value else "raw")

    # ------------------------------------------------------------ entities

    def _entity(self, e: Any, op: Any) -> None:
        op = int(op)
        cls = e.cls
        cname = cls.name
        index = e.index
        tick = int(self.p.tick)
        cols = self.parts["entities"].cols
        rows = 0
        if op != UPDATED:
            what = "|".join(n for bit, n in ((CREATED, "created"), (UPDATED, "updated"), (DELETED, "deleted"),
                                             (ENTERED, "entered"), (LEFT, "left")) if op & bit)
            self._prop(cols, tick, what, cname, index, None, _dumps({"serial": e.serial, "op": op,
                                                                     "handle": (e.serial << 14) | index}))
            rows += 1
        if op & CREATED:
            for k, v in e.to_map().items():
                self._prop(cols, tick, k, cname, index, v)
                rows += 1
        elif op & UPDATED:
            paths = e._field_state._updated_paths or ()
            serializer = cls.serializer
            names = self._names.get(id(serializer))
            if names is None:
                names = self._names[id(serializer)] = {}
            state = e._field_state
            for path in paths:
                n = names.get(path)
                if n is None:
                    n = names[path] = path_name(serializer, path)
                self._prop(cols, tick, n, cname, index, state._get_compact(path))
                rows += 1
            if not paths:
                self._prop(cols, tick, "updated", cname, index, None)
                rows += 1
        c = self._entity_types.get(cname)
        if c is None:
            c = self._entity_types[cname] = [0, 0]
        c[0] += 1
        c[1] += 1
        part = self.parts["entities"]
        part.rows += rows
        if len(cols["tick"]) >= FLUSH_ROWS:
            part.flush()

    @staticmethod
    def _prop(cols: dict[str, list], tick: int, name: str, cname: str, index: int, v: Any, decoded: str | None = None) -> None:
        value = vector = None
        t = type(v)
        if t is float:
            value = v if math.isfinite(v) else None
            if value is None:
                decoded = _dumps(str(v))
        elif t is bool:
            value = 1.0 if v else 0.0
        elif t is int:
            if -EXACT < v < EXACT:
                value = float(v)
            else:
                decoded = str(v)
        elif t is str:
            decoded = _dumps(v)
        elif t in (list, tuple):
            if all(type(x) in (float, int) for x in v):
                vector = [float(x) for x in v]
            else:
                decoded = _dumps(v)
        elif v is not None:
            decoded = _dumps(v.hex() if isinstance(v, (bytes, bytearray)) else str(v))
        cols["tick"].append(tick)
        cols["type"].append(name)
        cols["name"].append(cname)
        cols["entity"].append(index)
        cols["value"].append(value)
        cols["vector"].append(vector)
        cols["decoded"].append(decoded)

    # ------------------------------------------------------------ the end

    def abandon(self) -> None:
        """The parse failed: the half-written sidecars removed."""
        for part in self.parts.values():
            try:
                part.writer.close()
            except Exception:  # noqa: BLE001 - removed below either way
                pass
            part.path.unlink(missing_ok=True)

    def finish(self, at: Callable[[int], float], match: str) -> dict[str, Any]:
        """
        Closes the sidecars and names them `<match>.<what>.parquet`, with each
        row's time on the game clock; returns the `completeness` block (the
        caller adds the combat log's and the units' tables).
        """
        for part in self.parts.values():
            part.close()
        for cname, (seen, put) in sorted(self._entity_types.items()):
            self.types[f"entity {cname}"] = [seen, 0, put, 0]
        files = []
        for what, part in self.parts.items():
            out = self.folder / f"{match}.{what}.parquet"
            _with_time(part.path, out, at, DICTIONARY[what])
            files.append(out.name)
        return completeness(self.types, files, self.errors)


def _target(manager: Any, index: int) -> str:
    """What an order targets, by its entity's name where it has one."""
    if manager is None or not index or index < 0:
        return ""
    e = manager.find(index)
    return e.get_class_name() if e is not None else ""


def _with_time(part: Path, out: Path, at: Callable[[int], float], dictionary: list[str]) -> None:
    """A `.part` sidecar rewritten with `time` first, batch by batch; the part removed."""
    import numpy as np
    import pyarrow as pa
    import pyarrow.parquet as pq

    cache: dict[int, float] = {}
    with pq.ParquetFile(part) as src:
        schema = pa.schema([("time", pa.float64()), *src.schema_arrow])
        with pq.ParquetWriter(out, schema, compression="zstd", use_dictionary=dictionary) as w:
            for batch in src.iter_batches(batch_size=200_000):
                ticks = batch.column(0).to_numpy(zero_copy_only=False)
                uniq, inverse = np.unique(ticks, return_inverse=True)
                times = np.array([cache[t] if t in cache else cache.setdefault(t, round(at(int(t)), 4))
                                  for t in uniq.tolist()], dtype=np.float64)
                t = pa.array(times[inverse], pa.float64())
                w.write_table(pa.Table.from_batches([batch]).add_column(0, "time", t).cast(schema))
    part.unlink()


def entry(seen: int, decoded: int = 0, partial: int = 0, raw: int = 0) -> dict[str, int]:
    return {"seen": seen, "decoded": decoded, "partial": partial, "raw": raw, "lost": seen - decoded - partial - raw}


def completeness(types: dict[str, list[int]], files: list[str], errors: dict[str, int] | None = None) -> dict[str, Any]:
    """The `completeness` block of docs/converters.md from counts per type: [seen, decoded, partial, raw]."""
    out_types = {k: entry(*v) for k, v in sorted(types.items())}
    out: dict[str, Any] = {
        "rule": RULE,
        "sidecars": files,
        "types": out_types,
        "lost": sum(t["lost"] for t in out_types.values()),
    }
    if errors:
        # Items whose protobuf did not read: kept whole, counted raw.
        out["undecoded"] = dict(sorted(errors.items()))
    return out
