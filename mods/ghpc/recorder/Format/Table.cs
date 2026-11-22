// The recorder's table: its columns, a row as the game side fills it, and the
// spool the rows go into while a mission runs (so a crash loses at most the
// last second), read back into the Parquet table when the mission ends.

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace Heat3D.Ghpc.Format
{
    /// The table's columns, in order. Names and meanings follow the other 3DHeat
    /// converters (the War Thunder replay converter's table), so the viewer's
    /// replay, hit analysis and filters read them without a mapping.
    public static class Col
    {
        public static readonly List<ColumnSpec> All = new List<ColumnSpec>();
        static readonly Dictionary<string, int> ByName = new Dictionary<string, int>();

        static int Add(string name, PType t)
        {
            ByName[name] = All.Count;
            All.Add(new ColumnSpec(name, t));
            return All.Count - 1;
        }

        public static int Index(string name) => ByName.TryGetValue(name, out var i) ? i : -1;

        // when, what, which mission and unit
        public static readonly int Time = Add("time", PType.Double);
        public static readonly int Event = Add("event", PType.String);
        public static readonly int Match = Add("match", PType.String);
        public static readonly int Mission = Add("mission", PType.String);
        public static readonly int Map = Add("map", PType.String);
        public static readonly int Track = Add("track", PType.String);
        public static readonly int Life = Add("life", PType.String);
        public static readonly int Uid = Add("uid", PType.Int32);
        // who
        public static readonly int Player = Add("player", PType.String);
        public static readonly int Team = Add("team", PType.String);
        public static readonly int Ai = Add("ai", PType.Int32);
        public static readonly int IsPlayer = Add("isPlayer", PType.Int32);
        public static readonly int Kind = Add("kind", PType.String);
        public static readonly int Type = Add("type", PType.String);
        public static readonly int Vehicle = Add("Vehicle", PType.String);
        public static readonly int VehicleName = Add("VehicleName", PType.String);
        public static readonly int Crew = Add("crew", PType.String);
        // where, which way
        public static readonly int X = Add("x", PType.Float);
        public static readonly int Y = Add("y", PType.Float);
        public static readonly int Z = Add("z", PType.Float);
        public static readonly int DirX = Add("dirX", PType.Float);
        public static readonly int DirY = Add("dirY", PType.Float);
        public static readonly int DirZ = Add("dirZ", PType.Float);
        public static readonly int Heading = Add("heading", PType.Float);
        public static readonly int Pitch = Add("pitch", PType.Float);
        public static readonly int Roll = Add("roll", PType.Float);
        public static readonly int Speed = Add("speed", PType.Float);
        public static readonly int Alive = Add("alive", PType.Int32);
        public static readonly int TurretYaw = Add("turretYaw", PType.Float);
        public static readonly int GunPitch = Add("gunPitch", PType.Float);
        // shots
        public static readonly int Shot = Add("shotId", PType.Int32);
        public static readonly int Other = Add("other", PType.String);
        public static readonly int OtherVehicle = Add("otherVehicle", PType.String);
        public static readonly int OtherLife = Add("otherLife", PType.String);
        public static readonly int OtherTeam = Add("otherTeam", PType.String);
        public static readonly int Weapon = Add("weapon", PType.String);
        public static readonly int WeaponName = Add("weaponName", PType.String);
        public static readonly int Calibre = Add("calibre", PType.Float);
        public static readonly int AmmoType = Add("ammoType", PType.String);
        public static readonly int AmmoName = Add("ammoName", PType.String);
        public static readonly int MuzzleVelocity = Add("muzzleVelocity", PType.Float);
        public static readonly int PenetrationRha = Add("penetrationRha", PType.Float);
        // hits
        public static readonly int TargetX = Add("targetX", PType.Float);
        public static readonly int TargetY = Add("targetY", PType.Float);
        public static readonly int TargetZ = Add("targetZ", PType.Float);
        public static readonly int HitLocalX = Add("hitLocalX", PType.Float);
        public static readonly int HitLocalY = Add("hitLocalY", PType.Float);
        public static readonly int HitLocalZ = Add("hitLocalZ", PType.Float);
        public static readonly int HitDirX = Add("hitDirX", PType.Float);
        public static readonly int HitDirY = Add("hitDirY", PType.Float);
        public static readonly int HitDirZ = Add("hitDirZ", PType.Float);
        public static readonly int HitOutcome = Add("hitOutcome", PType.String);
        public static readonly int ImpactAngle = Add("impactAngle", PType.Float);
        public static readonly int ImpactSpeed = Add("impactSpeed", PType.Float);
        public static readonly int Plate = Add("plate", PType.String);
        public static readonly int Penetrated = Add("penetrated", PType.Int32);
        public static readonly int PenetrationLevel = Add("penetrationLevel", PType.Int32);
        public static readonly int Spall = Add("spall", PType.Int32);
        public static readonly int Distance = Add("distance", PType.Float);
        // what a hit did, and everything else
        public static readonly int CrewRole = Add("crewRole", PType.String);
        public static readonly int Module = Add("module", PType.String);
        public static readonly int Detail = Add("detail", PType.String);
        public static readonly int Text = Add("text", PType.String);
        public static readonly int State = Add("state", PType.String);
        // outcome columns (docs/data-formats.md, "Outcome columns")
        public static readonly int Won = Add("won", PType.Int32);
        public static readonly int MatchWon = Add("matchWon", PType.Int32);
        public static readonly int Round = Add("round", PType.Int32);
        public static readonly int RoundEndReason = Add("roundEndReason", PType.String);

        public static int Count => All.Count;
    }

    /// One row as the game side fills it: (column, value) pairs. Rows are pooled, so a
    /// recording at 20 Hz allocates nothing once it runs.
    public sealed class Row
    {
        public int N;
        public readonly int[] Cols = new int[128];
        public readonly double[] Nums = new double[128];
        public readonly string[] Strs = new string[128];

        public Row Set(int col, double v)
        {
            if (col < 0 || N >= Cols.Length || double.IsNaN(v) || double.IsInfinity(v)) return this;
            Cols[N] = col;
            Nums[N] = v;
            Strs[N] = null;
            N++;
            return this;
        }

        public Row Set(int col, string v)
        {
            if (col < 0 || N >= Cols.Length || v == null) return this;
            Cols[N] = col;
            Strs[N] = v;
            N++;
            return this;
        }

        public Row Set(int col, bool v) => Set(col, v ? 1.0 : 0.0);

        public void Reset()
        {
            for (int i = 0; i < N; i++) Strs[i] = null;
            N = 0;
        }
    }

    /// The spool: a header naming the columns, then string definitions, rows and
    /// match-document entries as they come. Append-only, so a cut-off spool reads to
    /// its last whole record.
    public sealed class SpoolWriter : IDisposable
    {
        public const string Magic = "H3DGHPC1";
        readonly BinaryWriter _w;
        readonly Dictionary<string, uint> _strings = new Dictionary<string, uint>(StringComparer.Ordinal);
        readonly uint[] _ids = new uint[128];
        uint _next;

        public SpoolWriter(string path)
        {
            var f = new FileStream(path, FileMode.Create, FileAccess.Write, FileShare.Read, 1 << 16);
            _w = new BinaryWriter(f, Encoding.UTF8);
            _w.Write(Encoding.ASCII.GetBytes(Magic));
            _w.Write((ushort)Col.Count);
            foreach (var c in Col.All)
            {
                _w.Write((byte)c.Type);
                Str(c.Name);
            }
        }

        void Str(string s)
        {
            var b = Encoding.UTF8.GetBytes(s ?? "");
            int n = Math.Min(b.Length, 1 << 20);
            _w.Write(n);
            _w.Write(b, 0, n);
        }

        uint Intern(string s)
        {
            uint id;
            if (_strings.TryGetValue(s, out id)) return id;
            id = _next++;
            // Strings that do not repeat (a shot's story, a log line) are not worth a table entry
            // forever; past 200k distinct ones the table stops growing and each is defined again.
            if (_strings.Count < 200000) _strings[s] = id;
            _w.Write((byte)'S');
            _w.Write(id);
            Str(s);
            return id;
        }

        public void Write(Row r)
        {
            // Strings first: a row's record then only refers to ids already defined.
            var ids = _ids;
            for (int i = 0; i < r.N; i++)
            {
                int c = r.Cols[i];
                if (c >= 0 && c < Col.Count && Col.All[c].Type == PType.String && r.Strs[i] != null) ids[i] = Intern(r.Strs[i]);
            }
            _w.Write((byte)'R');
            _w.Write((ushort)r.N);
            for (int i = 0; i < r.N; i++)
            {
                int c = r.Cols[i];
                _w.Write((ushort)c);
                switch (Col.All[c].Type)
                {
                    case PType.Double: _w.Write(r.Strs[i] != null ? double.NaN : r.Nums[i]); break;
                    case PType.Float: _w.Write(r.Strs[i] != null ? float.NaN : (float)r.Nums[i]); break;
                    case PType.Int32: _w.Write(r.Strs[i] != null ? int.MinValue : (int)Math.Round(r.Nums[i])); break;
                    default:
                        if (r.Strs[i] != null) _w.Write(ids[i]);
                        else _w.Write(Intern(r.Nums[i].ToString("R", System.Globalization.CultureInfo.InvariantCulture)));
                        break;
                }
            }
        }

        /// A match-document entry: the last one written under a key wins.
        public void Meta(string key, string json)
        {
            _w.Write((byte)'M');
            Str(key);
            Str(json);
        }

        public void Flush() => _w.Flush();

        public void Dispose()
        {
            _w.Flush();
            _w.Close();
        }
    }

    /// Reads a spool back: the columns it was written with, then each record.
    public sealed class SpoolReader : IDisposable
    {
        readonly BinaryReader _r;
        readonly Dictionary<uint, string> _strings = new Dictionary<uint, string>();
        public readonly List<ColumnSpec> Columns = new List<ColumnSpec>();
        public readonly Dictionary<string, string> Meta = new Dictionary<string, string>();
        /// Whether the spool ended in the middle of a record (the game stopped while it was written).
        public bool Truncated;

        public SpoolReader(string path)
        {
            _r = new BinaryReader(new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite, 1 << 16), Encoding.UTF8);
            var magic = Encoding.ASCII.GetString(_r.ReadBytes(8));
            if (magic != SpoolWriter.Magic) throw new InvalidDataException("not a recorder spool");
            int n = _r.ReadUInt16();
            for (int i = 0; i < n; i++)
            {
                var t = (PType)_r.ReadByte();
                Columns.Add(new ColumnSpec(Str(), t));
            }
        }

        string Str()
        {
            int n = _r.ReadInt32();
            if (n < 0 || n > (1 << 20)) throw new InvalidDataException("bad string");
            var b = _r.ReadBytes(n);
            if (b.Length != n) throw new EndOfStreamException();
            return Encoding.UTF8.GetString(b);
        }

        /// The next row into `buf` at `row`; false at the end. Meta entries and strings are taken on the way.
        public bool Next(ColumnBuffer[] buf, int row)
        {
            for (;;)
            {
                int kind;
                try
                {
                    kind = _r.BaseStream.ReadByte();
                    if (kind < 0) return false;
                    if (kind == 'S')
                    {
                        uint id = _r.ReadUInt32();
                        _strings[id] = Str();
                        continue;
                    }
                    if (kind == 'M')
                    {
                        var k = Str();
                        Meta[k] = Str();
                        continue;
                    }
                    if (kind != 'R') throw new InvalidDataException("bad record");
                    int n = _r.ReadUInt16();
                    for (int i = 0; i < n; i++)
                    {
                        int c = _r.ReadUInt16();
                        if (c >= Columns.Count) throw new InvalidDataException("bad column");
                        var b = buf[c];
                        switch (Columns[c].Type)
                        {
                            case PType.Double:
                            {
                                double v = _r.ReadDouble();
                                if (!double.IsNaN(v)) b.SetDouble(row, v);
                                break;
                            }
                            case PType.Float:
                            {
                                float v = _r.ReadSingle();
                                if (!float.IsNaN(v)) b.SetDouble(row, v);
                                break;
                            }
                            case PType.Int32:
                            {
                                int v = _r.ReadInt32();
                                if (v != int.MinValue) b.SetDouble(row, v);
                                break;
                            }
                            default:
                            {
                                uint id = _r.ReadUInt32();
                                string s;
                                if (_strings.TryGetValue(id, out s)) b.SetString(row, s);
                                break;
                            }
                        }
                    }
                    return true;
                }
                catch (EndOfStreamException)
                {
                    Truncated = true;
                    // The cut-off row is dropped whole.
                    foreach (var b in buf)
                    {
                        if (b.Present[row])
                        {
                            b.Present[row] = false;
                            b.NonNull--;
                        }
                    }
                    return false;
                }
                catch (InvalidDataException)
                {
                    Truncated = true;
                    foreach (var b in buf)
                    {
                        if (b.Present[row])
                        {
                            b.Present[row] = false;
                            b.NonNull--;
                        }
                    }
                    return false;
                }
            }
        }

        /// Only the match-document entries of a spool (rows are skipped): the finisher needs the
        /// mission's result before it writes the first row.
        public static Dictionary<string, string> ReadMeta(string path)
        {
            using (var sp = new SpoolReader(path))
            {
                var r = sp._r;
                try
                {
                    for (;;)
                    {
                        int kind = r.BaseStream.ReadByte();
                        if (kind < 0) break;
                        if (kind == 'S')
                        {
                            r.ReadUInt32();
                            sp.Str();
                        }
                        else if (kind == 'M')
                        {
                            var k = sp.Str();
                            sp.Meta[k] = sp.Str();
                        }
                        else if (kind == 'R')
                        {
                            int n = r.ReadUInt16();
                            for (int i = 0; i < n; i++)
                            {
                                int c = r.ReadUInt16();
                                if (c >= sp.Columns.Count) throw new InvalidDataException("bad column");
                                r.BaseStream.Seek(sp.Columns[c].Type == PType.Double ? 8 : 4, SeekOrigin.Current);
                            }
                        }
                        else break;
                    }
                }
                catch (EndOfStreamException)
                {
                }
                catch (InvalidDataException)
                {
                }
                return sp.Meta;
            }
        }

        public void Dispose() => _r.Close();
    }
}
