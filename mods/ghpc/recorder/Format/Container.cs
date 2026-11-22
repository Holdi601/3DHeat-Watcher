// A finished mission: the spool read back into the Parquet table, the match
// document put together from the spool's entries, the game's log lines kept
// whole in a sidecar, all packed into one `.3dheat` file
// (docs/container.md in the viewer's repository).

using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;

namespace Heat3D.Ghpc.Format
{
    public static class Container
    {
        public const string Game = "ghpc";
        public const string ConverterName = "heat3d-ghpc-recorder";
        public const int GroupRows = 32768;

        /// Events that are the game's log, kept whole in the `raw` sidecar instead of the table.
        public const string LogEvent = "log";

        /// The table's reading instructions for the viewer (the `heat3d` footer key).
        public static string Hints()
        {
            var extra = new List<object>();
            foreach (var c in Col.All)
            {
                if (c.Name == "x" || c.Name == "y" || c.Name == "z" || c.Name == "time" || c.Name == "track" || c.Name == "team"
                    || c.Name == "match" || c.Name == "dirX" || c.Name == "dirY" || c.Name == "dirZ") continue;
                extra.Add(c.Name);
            }
            var hints = new Dictionary<string, object>
            {
                ["version"] = 1,
                ["kind"] = "ghpc-recorder",
                ["game"] = "Gunner, HEAT, PC!",
                // Unity's own axes: x east, y up, z north, a left-handed world; mirrored in z for the viewer.
                ["axes"] = new Dictionary<string, object> { ["up"] = "y", ["flipX"] = false, ["flipY"] = false, ["flipZ"] = true, ["scale"] = 1 },
                ["columns"] = new Dictionary<string, object>
                {
                    ["x"] = "x", ["y"] = "y", ["z"] = "z",
                    ["time"] = "time", ["timeUnit"] = "seconds", ["timeLabel"] = "since the mission began",
                    ["personId"] = "track", ["teamId"] = "team", ["sessionId"] = "match",
                    ["lookMode"] = "vector", ["dirX"] = "dirX", ["dirY"] = "dirY", ["dirZ"] = "dirZ",
                    ["extra"] = extra,
                },
            };
            return Json.Write(hints, false);
        }

        static readonly List<ColumnSpec> RawColumns = new List<ColumnSpec>
        {
            new ColumnSpec("time", PType.Double),
            new ColumnSpec("type", PType.String),
            new ColumnSpec("name", PType.String),
            new ColumnSpec("text", PType.String),
        };

        public sealed class Result
        {
            public string Path;
            public long Rows, RawRows;
            public bool Truncated;
            public Dictionary<string, long> Events = new Dictionary<string, long>();
        }

        /// Builds `<folder>/<match>.3dheat` from a spool. The spool is left in place; the caller deletes it.
        public static Result Build(string spoolPath, string folder, string version)
        {
            Directory.CreateDirectory(folder);
            string tableTmp = spoolPath + ".table.tmp", rawTmp = spoolPath + ".raw.tmp";
            var res = new Result();
            Dictionary<string, string> meta;
            double tMin = double.PositiveInfinity, tMax = double.NegativeInfinity;
            // Who won, for the outcome columns of every row with a side (docs/data-formats.md).
            var pre = SpoolReader.ReadMeta(spoolPath);
            string winner = null, endReason = null;
            if (pre.TryGetValue("top/winner", out var wj)) winner = Unquote(wj);
            if (pre.TryGetValue("top/roundEndReason", out var rj)) endReason = Unquote(rj);
            using (var spool = new SpoolReader(spoolPath))
            {
                var cols = spool.Columns.Select(c => new ColumnBuffer(c, GroupRows)).ToArray();
                var raw = RawColumns.Select(c => new ColumnBuffer(c, GroupRows)).ToArray();
                int iTime = spool.Columns.FindIndex(c => c.Name == "time");
                int iEvent = spool.Columns.FindIndex(c => c.Name == "event");
                int iDetail = spool.Columns.FindIndex(c => c.Name == "detail");
                int iText = spool.Columns.FindIndex(c => c.Name == "text");
                int iState = spool.Columns.FindIndex(c => c.Name == "state");
                int iTeam = spool.Columns.FindIndex(c => c.Name == "team");
                int iWon = spool.Columns.FindIndex(c => c.Name == "won");
                int iMatchWon = spool.Columns.FindIndex(c => c.Name == "matchWon");
                int iReason = spool.Columns.FindIndex(c => c.Name == "roundEndReason");
                using (var tf = new FileStream(tableTmp, FileMode.Create, FileAccess.Write, FileShare.None, 1 << 16))
                using (var rf = new FileStream(rawTmp, FileMode.Create, FileAccess.Write, FileShare.None, 1 << 16))
                {
                    var table = new ParquetWriter(tf, spool.Columns);
                    var rawTable = new ParquetWriter(rf, RawColumns);
                    int rows = 0, rawRows = 0;
                    while (spool.Next(cols, rows))
                    {
                        string ev = iEvent >= 0 && cols[iEvent].Present[rows] ? cols[iEvent].S[rows] : null;
                        double t = iTime >= 0 && cols[iTime].Present[rows] ? cols[iTime].D[rows] : double.NaN;
                        if (ev != null)
                        {
                            long n;
                            res.Events.TryGetValue(ev, out n);
                            res.Events[ev] = n + 1;
                        }
                        if (ev == LogEvent)
                        {
                            if (!double.IsNaN(t)) raw[0].SetDouble(rawRows, t);
                            raw[1].SetString(rawRows, iState >= 0 && cols[iState].Present[rows] ? cols[iState].S[rows] : "log");
                            raw[2].SetString(rawRows, iDetail >= 0 && cols[iDetail].Present[rows] ? cols[iDetail].S[rows] : "");
                            raw[3].SetString(rawRows, iText >= 0 && cols[iText].Present[rows] ? cols[iText].S[rows] : "");
                            foreach (var b in cols)
                            {
                                if (b.Present[rows])
                                {
                                    b.Present[rows] = false;
                                    b.NonNull--;
                                    if (b.S != null) b.S[rows] = null;
                                }
                            }
                            if (++rawRows == GroupRows)
                            {
                                rawTable.WriteRowGroup(raw, rawRows);
                                foreach (var b in raw) b.Clear(rawRows);
                                rawRows = 0;
                            }
                            continue;
                        }
                        if (!string.IsNullOrEmpty(winner) && iTeam >= 0 && cols[iTeam].Present[rows] && cols[iTeam].S[rows] != "")
                        {
                            int w = cols[iTeam].S[rows] == winner ? 1 : 0;
                            if (iWon >= 0 && !cols[iWon].Present[rows]) cols[iWon].SetDouble(rows, w);
                            if (iMatchWon >= 0 && !cols[iMatchWon].Present[rows]) cols[iMatchWon].SetDouble(rows, w);
                            if (endReason != null && iReason >= 0 && !cols[iReason].Present[rows]) cols[iReason].SetString(rows, endReason);
                        }
                        if (!double.IsNaN(t))
                        {
                            tMin = Math.Min(tMin, t);
                            tMax = Math.Max(tMax, t);
                        }
                        if (++rows == GroupRows)
                        {
                            table.WriteRowGroup(cols, rows);
                            foreach (var b in cols) b.Clear(rows);
                            rows = 0;
                        }
                    }
                    table.WriteRowGroup(cols, rows);
                    rawTable.WriteRowGroup(raw, rawRows);
                    table.Finish(new List<KeyValuePair<string, string>> { new KeyValuePair<string, string>("heat3d", Hints()) }, ConverterName + " " + version);
                    rawTable.Finish(null, ConverterName + " " + version);
                    res.Rows = table.Rows;
                    res.RawRows = rawTable.Rows;
                }
                meta = spool.Meta;
                res.Truncated = spool.Truncated;
            }

            string Top(string k, string fallback)
            {
                string v;
                return meta.TryGetValue("top/" + k, out v) ? v : fallback;
            }

            string match = Unquote(Top("match", null)) ?? Path.GetFileNameWithoutExtension(spoolPath);
            match = Safe(match);
            var stem = match;
            var tableName = stem + ".parquet";
            var docName = stem + ".match.json";
            var rawName = stem + ".raw.parquet";
            var probeName = stem + ".probe.json";

            double duration = tMax >= tMin ? tMax - tMin : 0;
            var doc = MatchDocument(meta, res, duration, rawName, version);
            var docBytes = Encoding.UTF8.GetBytes(doc);
            string probe;
            meta.TryGetValue("probe", out probe);
            byte[] probeBytes = probe != null ? Encoding.UTF8.GetBytes(probe) : null;

            var members = new List<object>
            {
                Member(tableName, "table", "application/vnd.apache.parquet", "stored", tableTmp, res.Rows, "heat3d-table"),
                Member(docName, "match", "application/json", "deflated", docBytes, -1, null),
                Member(rawName, "raw", "application/vnd.apache.parquet", "stored", rawTmp, res.RawRows, null),
            };
            var roles = new Dictionary<string, object> { ["table"] = tableName, ["match"] = docName, ["raw"] = rawName };
            if (probeBytes != null)
            {
                members.Add(Member(probeName, "probe", "application/json", "deflated", probeBytes, -1, null));
                roles["probe"] = probeName;
            }
            var manifest = new Dictionary<string, object>
            {
                ["format"] = "3dheat",
                ["format_version"] = "1.0",
                ["game"] = Game,
                ["source"] = "recorder mod",
                ["converter"] = new Dictionary<string, object> { ["name"] = ConverterName, ["version"] = version },
                ["match"] = match,
                ["map"] = Unquote(Top("map", "\"\"")),
                ["mode"] = Unquote(Top("mode", "\"mission\"")),
                ["started"] = Unquote(Top("started", "\"\"")),
                ["created"] = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffZ", CultureInfo.InvariantCulture),
                ["roles"] = roles,
                ["members"] = members,
            };

            var outPath = Path.Combine(folder, stem + ".3dheat");
            var tmpOut = outPath + ".part";
            using (var f = new FileStream(tmpOut, FileMode.Create, FileAccess.Write, FileShare.None, 1 << 16))
            using (var zip = new ZipWriter(f, DateTime.Now))
            {
                zip.Add("manifest.json", Encoding.UTF8.GetBytes(Json.Write(manifest)), true);
                zip.AddFile(tableName, tableTmp);
                zip.Add(docName, docBytes, true);
                zip.AddFile(rawName, rawTmp);
                if (probeBytes != null) zip.Add(probeName, probeBytes, true);
            }
            if (File.Exists(outPath)) File.Delete(outPath);
            File.Move(tmpOut, outPath);
            File.Delete(tableTmp);
            File.Delete(rawTmp);
            res.Path = outPath;
            return res;
        }

        static string Unquote(string json) => json != null && json.Length >= 2 && json[0] == '"' ? json.Substring(1, json.Length - 2) : json;

        static Dictionary<string, object> Member(string name, string role, string media, string compression, object data, long rows, string schema)
        {
            long bytes;
            string sha;
            using (var h = SHA256.Create())
            {
                if (data is string path)
                {
                    using (var f = File.OpenRead(path)) sha = Hex(h.ComputeHash(f));
                    bytes = new FileInfo(path).Length;
                }
                else
                {
                    var b = (byte[])data;
                    sha = Hex(h.ComputeHash(b));
                    bytes = b.Length;
                }
            }
            var m = new Dictionary<string, object>
            {
                ["name"] = name,
                ["role"] = role,
                ["media_type"] = media,
                ["compression"] = compression,
                ["bytes"] = bytes,
            };
            if (rows >= 0) m["rows"] = rows;
            m["sha256"] = sha;
            if (schema != null) m["schema"] = new Dictionary<string, object> { ["id"] = schema, ["version"] = "1" };
            return m;
        }

        static string Hex(byte[] b)
        {
            var sb = new StringBuilder(b.Length * 2);
            foreach (var x in b) sb.Append(x.ToString("x2"));
            return sb.ToString();
        }

        /// A file name from a mission name: letters, digits, `-`, `_` and `.` only.
        public static string Safe(string s)
        {
            var sb = new StringBuilder();
            foreach (var ch in s ?? "")
                sb.Append(char.IsLetterOrDigit(ch) || ch == '-' || ch == '_' || ch == '.' ? ch : '_');
            var r = sb.ToString().Trim('.', '_');
            return r.Length == 0 ? "mission" : r.Length > 120 ? r.Substring(0, 120) : r;
        }

        /// The match document: `top/<key>` entries become its keys, `<list>/<id>` entries the
        /// items of its lists (in key order), any other entry a key of its own; then the counts.
        static string MatchDocument(Dictionary<string, string> meta, Result res, double duration, string rawName, string version)
        {
            var sb = new StringBuilder();
            sb.Append("{\n \"format\": \"heat3d-ghpc-match\",\n \"version\": 1,\n \"game\": \"ghpc\"");
            var lists = new SortedDictionary<string, List<KeyValuePair<string, string>>>(StringComparer.Ordinal);
            bool timePlayed = false;
            foreach (var kv in meta)
            {
                if (kv.Key == "probe") continue;
                int slash = kv.Key.IndexOf('/');
                if (slash < 0)
                {
                    sb.Append(",\n ").Append(Json.Write(kv.Key)).Append(": ").Append(kv.Value);
                    continue;
                }
                var head = kv.Key.Substring(0, slash);
                if (head == "top")
                {
                    var k = kv.Key.Substring(slash + 1);
                    if (k == "timePlayed") timePlayed = true;
                    sb.Append(",\n ").Append(Json.Write(k)).Append(": ").Append(kv.Value);
                    continue;
                }
                List<KeyValuePair<string, string>> l;
                if (!lists.TryGetValue(head, out l)) lists[head] = l = new List<KeyValuePair<string, string>>();
                l.Add(new KeyValuePair<string, string>(kv.Key, kv.Value));
            }
            if (!timePlayed) sb.Append(",\n \"timePlayed\": ").Append(Json.Write(Math.Round(duration, 3)));
            foreach (var kv in lists)
            {
                sb.Append(",\n ").Append(Json.Write(kv.Key)).Append(": [");
                var items = kv.Value.OrderBy(x => x.Key, StringComparer.Ordinal).ToList();
                for (int i = 0; i < items.Count; i++) sb.Append(i == 0 ? "\n  " : ",\n  ").Append(items[i].Value);
                sb.Append(items.Count > 0 ? "\n ]" : "]");
            }
            // The converter rule's self-check (docs/converters.md): every event the mod wrote is decoded
            // into the table; the game's log lines are kept whole in the raw sidecar.
            var types = new Dictionary<string, object>();
            foreach (var kv in res.Events.OrderBy(x => x.Key, StringComparer.Ordinal))
            {
                bool log = kv.Key == LogEvent;
                types[kv.Key] = new Dictionary<string, object>
                {
                    ["seen"] = kv.Value, ["decoded"] = log ? 0L : kv.Value, ["partial"] = 0, ["raw"] = log ? kv.Value : 0L, ["lost"] = 0,
                };
            }
            var self = new Dictionary<string, object>
            {
                ["completeness"] = new Dictionary<string, object>
                {
                    ["rule"] = "https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md",
                    ["sidecars"] = new List<object> { rawName },
                    ["types"] = types,
                    ["lost"] = 0,
                },
                ["rows"] = res.Rows,
                ["rawRows"] = res.RawRows,
                ["spoolCutOff"] = res.Truncated,
                ["writer"] = ConverterName + " " + version,
            };
            sb.Append(",\n \"selfCheck\": ").Append(Json.Write(self));
            sb.Append("\n}\n");
            return sb.ToString();
        }
    }
}
