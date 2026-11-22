// A Parquet writer for flat tables: optional columns of double, float, int32 and
// UTF-8 strings, written row group by row group so only one group is ever in
// memory. Numbers are PLAIN, strings dictionary-encoded (a dictionary page and
// RLE_DICTIONARY indices), definition levels RLE; pages Snappy-compressed.
// Written from the Apache Parquet format specification (parquet.thrift).

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace Heat3D.Ghpc.Format
{
    public enum PType
    {
        Double,
        Float,
        Int32,
        String,
    }

    public sealed class ColumnSpec
    {
        public readonly string Name;
        public readonly PType Type;

        public ColumnSpec(string name, PType type)
        {
            Name = name;
            Type = type;
        }
    }

    /// One column's values for one row group: a value per row where `Present`.
    public sealed class ColumnBuffer
    {
        public readonly ColumnSpec Spec;
        public readonly bool[] Present;
        public readonly double[] D;
        public readonly float[] F;
        public readonly int[] I;
        public readonly string[] S;
        public int NonNull;

        public ColumnBuffer(ColumnSpec spec, int capacity)
        {
            Spec = spec;
            Present = new bool[capacity];
            switch (spec.Type)
            {
                case PType.Double: D = new double[capacity]; break;
                case PType.Float: F = new float[capacity]; break;
                case PType.Int32: I = new int[capacity]; break;
                default: S = new string[capacity]; break;
            }
        }

        public void Clear(int rows)
        {
            Array.Clear(Present, 0, rows);
            if (S != null) Array.Clear(S, 0, rows);
            NonNull = 0;
        }

        public void SetDouble(int row, double v)
        {
            if (D != null) D[row] = v;
            else if (F != null) F[row] = (float)v;
            else if (I != null) I[row] = (int)Math.Round(v);
            else S[row] = v.ToString("R", System.Globalization.CultureInfo.InvariantCulture);
            Mark(row);
        }

        public void SetString(int row, string v)
        {
            if (v == null) return;
            if (S != null) S[row] = v;
            else
            {
                double d;
                if (!double.TryParse(v, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out d)) return;
                SetDouble(row, d);
                return;
            }
            Mark(row);
        }

        void Mark(int row)
        {
            if (!Present[row])
            {
                Present[row] = true;
                NonNull++;
            }
        }
    }

    public sealed class ParquetWriter
    {
        const int PLAIN = 0, PLAIN_DICTIONARY = 2, RLE = 3, RLE_DICTIONARY = 8;
        const int DATA_PAGE = 0, DICTIONARY_PAGE = 2;

        sealed class ChunkMeta
        {
            public PType Type;
            public string Name;
            public bool Dict;
            public long DataOffset, DictOffset = -1, Size, USize;
            public long Values;
        }

        readonly Stream _s;
        readonly IList<ColumnSpec> _schema;
        readonly List<List<ChunkMeta>> _groups = new List<List<ChunkMeta>>();
        readonly List<long> _groupRows = new List<long>();
        long _pos;
        long _rows;

        public long Rows => _rows;

        public ParquetWriter(Stream output, IList<ColumnSpec> schema)
        {
            _s = output;
            _schema = schema;
            Raw(Encoding.ASCII.GetBytes("PAR1"));
        }

        void Raw(byte[] b)
        {
            _s.Write(b, 0, b.Length);
            _pos += b.Length;
        }

        void Raw(MemoryStream m)
        {
            m.Position = 0;
            m.CopyTo(_s);
            _pos += m.Length;
        }

        public void WriteRowGroup(ColumnBuffer[] cols, int rows)
        {
            if (rows <= 0) return;
            var metas = new List<ChunkMeta>();
            foreach (var c in cols) metas.Add(WriteChunk(c, rows));
            _groups.Add(metas);
            _groupRows.Add(rows);
            _rows += rows;
        }

        ChunkMeta WriteChunk(ColumnBuffer c, int rows)
        {
            var meta = new ChunkMeta { Type = c.Spec.Type, Name = c.Spec.Name, Values = rows };
            long start = _pos;
            _usize = 0;
            var levels = DefinitionLevels(c.Present, rows);
            var values = new MemoryStream();
            int encoding = PLAIN;
            if (c.Spec.Type == PType.String && c.NonNull > 0)
            {
                var dict = new Dictionary<string, int>(StringComparer.Ordinal);
                var order = new List<string>();
                var idx = new int[c.NonNull];
                int k = 0;
                for (int r = 0; r < rows; r++)
                {
                    if (!c.Present[r]) continue;
                    var s = c.S[r] ?? "";
                    int id;
                    if (!dict.TryGetValue(s, out id))
                    {
                        id = order.Count;
                        dict[s] = id;
                        order.Add(s);
                    }
                    idx[k++] = id;
                }
                var dpage = new MemoryStream();
                foreach (var s in order) PlainString(dpage, s);
                meta.Dict = true;
                meta.DictOffset = _pos;
                Page(DICTIONARY_PAGE, dpage, 0, order.Count);
                int width = BitWidth(order.Count - 1);
                values.WriteByte((byte)width);
                RleRuns(values, idx, idx.Length, width);
                encoding = RLE_DICTIONARY;
            }
            else
            {
                var bw = new BinaryWriter(values);
                for (int r = 0; r < rows; r++)
                {
                    if (!c.Present[r]) continue;
                    switch (c.Spec.Type)
                    {
                        case PType.Double: bw.Write(c.D[r]); break;
                        case PType.Float: bw.Write(c.F[r]); break;
                        case PType.Int32: bw.Write(c.I[r]); break;
                        default: PlainString(values, c.S[r] ?? ""); break;
                    }
                }
                bw.Flush();
            }
            var page = new MemoryStream();
            var lw = new BinaryWriter(page);
            lw.Write((int)levels.Length);
            lw.Write(levels.ToArray());
            values.Position = 0;
            values.CopyTo(page);
            meta.DataOffset = _pos;
            Page(DATA_PAGE, page, encoding, rows);
            meta.Size = _pos - start;
            meta.USize = _usize;
            return meta;
        }

        long _usize;

        void Page(int type, MemoryStream body, int encoding, int count)
        {
            var packed = Snappy.Compress(body.GetBuffer(), (int)body.Length);
            var head = new MemoryStream();
            var t = new ThriftWriter(head);
            t.BeginStruct();
            t.I32(1, type);
            t.I32(2, (int)body.Length);
            t.I32(3, packed.Length);
            if (type == DATA_PAGE)
            {
                t.Struct(5);
                t.I32(1, count);
                t.I32(2, encoding);
                t.I32(3, RLE);
                t.I32(4, RLE);
                t.EndStruct();
            }
            else
            {
                t.Struct(7);
                t.I32(1, count);
                t.I32(2, PLAIN);
                t.EndStruct();
            }
            t.EndStruct();
            Raw(head);
            Raw(packed);
            _usize += head.Length + body.Length;
        }

        static void PlainString(Stream s, string v)
        {
            var b = Encoding.UTF8.GetBytes(v);
            var len = BitConverter.GetBytes(b.Length);
            s.Write(len, 0, 4);
            s.Write(b, 0, b.Length);
        }

        static int BitWidth(int max)
        {
            int w = 0;
            while (max > 0)
            {
                w++;
                max >>= 1;
            }
            return Math.Max(1, w);
        }

        /// RLE/bit-packing hybrid, RLE runs only: each run of equal values is (count << 1) and the value.
        static void RleRuns(Stream s, int[] v, int n, int width)
        {
            int bytes = (width + 7) / 8;
            int i = 0;
            while (i < n)
            {
                int j = i + 1;
                while (j < n && v[j] == v[i]) j++;
                VarInt(s, (ulong)(j - i) << 1);
                int x = v[i];
                for (int b = 0; b < bytes; b++) s.WriteByte((byte)(x >> (8 * b)));
                i = j;
            }
        }

        static MemoryStream DefinitionLevels(bool[] present, int rows)
        {
            var m = new MemoryStream();
            int i = 0;
            while (i < rows)
            {
                int j = i + 1;
                while (j < rows && present[j] == present[i]) j++;
                VarInt(m, (ulong)(j - i) << 1);
                m.WriteByte(present[i] ? (byte)1 : (byte)0);
                i = j;
            }
            return m;
        }

        static void VarInt(Stream s, ulong v)
        {
            while (v >= 0x80)
            {
                s.WriteByte((byte)(v | 0x80));
                v >>= 7;
            }
            s.WriteByte((byte)v);
        }

        static int Physical(PType t)
        {
            switch (t)
            {
                case PType.Double: return 5;
                case PType.Float: return 4;
                case PType.Int32: return 1;
                default: return 6;
            }
        }

        /// The footer: the schema, the row groups and the key/value metadata, then the closing magic.
        public void Finish(IList<KeyValuePair<string, string>> metadata, string createdBy)
        {
            var m = new MemoryStream();
            var t = new ThriftWriter(m);
            t.BeginStruct();
            t.I32(1, 1);
            t.List(2, ThriftWriter.TStruct, _schema.Count + 1);
            t.BeginStruct();
            t.String(4, "schema");
            t.I32(5, _schema.Count);
            t.EndStruct();
            foreach (var c in _schema)
            {
                t.BeginStruct();
                t.I32(1, Physical(c.Type));
                t.I32(3, 1); // OPTIONAL
                t.String(4, c.Name);
                if (c.Type == PType.String)
                {
                    t.I32(6, 0); // UTF8
                    t.Struct(10); // LogicalType
                    t.Struct(1); // STRING
                    t.EndStruct();
                    t.EndStruct();
                }
                t.EndStruct();
            }
            t.I64(3, _rows);
            t.List(4, ThriftWriter.TStruct, _groups.Count);
            for (int g = 0; g < _groups.Count; g++)
            {
                t.BeginStruct();
                var metas = _groups[g];
                t.List(1, ThriftWriter.TStruct, metas.Count);
                long total = 0;
                foreach (var c in metas)
                {
                    total += c.USize;
                    t.BeginStruct();
                    t.I64(2, c.Dict ? c.DictOffset : c.DataOffset);
                    t.Struct(3);
                    t.I32(1, Physical(c.Type));
                    if (c.Dict)
                    {
                        t.List(2, ThriftWriter.TI32, 3);
                        t.ElemI32(PLAIN);
                        t.ElemI32(RLE);
                        t.ElemI32(RLE_DICTIONARY);
                    }
                    else
                    {
                        t.List(2, ThriftWriter.TI32, 2);
                        t.ElemI32(PLAIN);
                        t.ElemI32(RLE);
                    }
                    t.List(3, ThriftWriter.TBinary, 1);
                    t.ElemString(c.Name);
                    t.I32(4, 1); // SNAPPY
                    t.I64(5, c.Values);
                    t.I64(6, c.USize);
                    t.I64(7, c.Size);
                    t.I64(9, c.DataOffset);
                    if (c.Dict) t.I64(11, c.DictOffset);
                    t.EndStruct();
                    t.EndStruct();
                }
                t.I64(2, total);
                t.I64(3, _groupRows[g]);
                t.EndStruct();
            }
            if (metadata != null && metadata.Count > 0)
            {
                t.List(5, ThriftWriter.TStruct, metadata.Count);
                foreach (var kv in metadata)
                {
                    t.BeginStruct();
                    t.String(1, kv.Key);
                    t.String(2, kv.Value);
                    t.EndStruct();
                }
            }
            t.String(6, createdBy);
            t.EndStruct();
            Raw(m);
            Raw(BitConverter.GetBytes((int)m.Length));
            Raw(Encoding.ASCII.GetBytes("PAR1"));
            _s.Flush();
        }
    }
}
