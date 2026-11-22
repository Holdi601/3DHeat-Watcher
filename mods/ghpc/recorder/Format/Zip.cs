// A ZIP writer as the .3dheat container wants it: members stored (method 0) or
// deflated (method 8), UTF-8 names, sizes and CRC in the local header (no data
// descriptors), no ZIP64 (a mission's table stays far below 4 GiB).
// Written from PKWARE's APPNOTE.TXT.

using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Text;

namespace Heat3D.Ghpc.Format
{
    public static class Crc32
    {
        static readonly uint[] Table = Build();

        static uint[] Build()
        {
            var t = new uint[256];
            for (uint n = 0; n < 256; n++)
            {
                uint c = n;
                for (int k = 0; k < 8; k++) c = (c & 1) != 0 ? 0xEDB88320u ^ (c >> 1) : c >> 1;
                t[n] = c;
            }
            return t;
        }

        public static uint Update(uint crc, byte[] b, int off, int len)
        {
            uint c = crc ^ 0xFFFFFFFFu;
            for (int i = off; i < off + len; i++) c = Table[(c ^ b[i]) & 0xFF] ^ (c >> 8);
            return c ^ 0xFFFFFFFFu;
        }
    }

    public sealed class ZipWriter : IDisposable
    {
        sealed class Entry
        {
            public string Name;
            public ushort Method;
            public uint Crc;
            public long CSize, USize, Offset;
        }

        readonly Stream _s;
        readonly List<Entry> _entries = new List<Entry>();
        readonly ushort _time, _date;

        public ZipWriter(Stream output, DateTime when)
        {
            _s = output;
            _time = (ushort)((when.Hour << 11) | (when.Minute << 5) | (when.Second / 2));
            _date = (ushort)(((Math.Max(1980, when.Year) - 1980) << 9) | (when.Month << 5) | when.Day);
        }

        /// A member from bytes: deflated when `deflate` and the runtime can (else stored).
        public void Add(string name, byte[] data, bool deflate)
        {
            uint crc = Crc32.Update(0, data, 0, data.Length);
            byte[] body = data;
            ushort method = 0;
            if (deflate)
            {
                try
                {
                    var m = new MemoryStream();
                    using (var z = new DeflateStream(m, CompressionMode.Compress, true)) z.Write(data, 0, data.Length);
                    body = m.ToArray();
                    method = 8;
                }
                catch (Exception)
                {
                    body = data; // a runtime without zlib: stored, which every reader takes as well
                    method = 0;
                }
            }
            var e = Header(name, method, crc, body.Length, data.Length);
            _s.Write(body, 0, body.Length);
            _entries.Add(e);
        }

        /// A stored member copied from a file, which is read twice: once for its CRC, once into the archive.
        public void AddFile(string name, string path)
        {
            uint crc = 0;
            long size = 0;
            var buf = new byte[1 << 16];
            using (var f = File.OpenRead(path))
            {
                int n;
                while ((n = f.Read(buf, 0, buf.Length)) > 0)
                {
                    crc = Crc32.Update(crc, buf, 0, n);
                    size += n;
                }
            }
            if (size >= 0xFFFFFFFFL) throw new IOException("member too large for this writer");
            var e = Header(name, 0, crc, size, size);
            using (var f = File.OpenRead(path)) f.CopyTo(_s);
            _entries.Add(e);
        }

        Entry Header(string name, ushort method, uint crc, long csize, long usize)
        {
            var e = new Entry { Name = name, Method = method, Crc = crc, CSize = csize, USize = usize, Offset = _s.Position };
            var n = Encoding.UTF8.GetBytes(name);
            var w = new BinaryWriter(_s, Encoding.UTF8, true);
            w.Write(0x04034b50u);
            w.Write((ushort)20);
            w.Write((ushort)0x0800);
            w.Write(method);
            w.Write(_time);
            w.Write(_date);
            w.Write(crc);
            w.Write((uint)csize);
            w.Write((uint)usize);
            w.Write((ushort)n.Length);
            w.Write((ushort)0);
            w.Write(n);
            w.Flush();
            return e;
        }

        public void Dispose()
        {
            long cdStart = _s.Position;
            var w = new BinaryWriter(_s, Encoding.UTF8, true);
            foreach (var e in _entries)
            {
                var n = Encoding.UTF8.GetBytes(e.Name);
                w.Write(0x02014b50u);
                w.Write((ushort)20);
                w.Write((ushort)20);
                w.Write((ushort)0x0800);
                w.Write(e.Method);
                w.Write(_time);
                w.Write(_date);
                w.Write(e.Crc);
                w.Write((uint)e.CSize);
                w.Write((uint)e.USize);
                w.Write((ushort)n.Length);
                w.Write((ushort)0);
                w.Write((ushort)0);
                w.Write((ushort)0);
                w.Write((ushort)0);
                w.Write(0u);
                w.Write((uint)e.Offset);
                w.Write(n);
            }
            long cdSize = _s.Position - cdStart;
            w.Write(0x06054b50u);
            w.Write((ushort)0);
            w.Write((ushort)0);
            w.Write((ushort)_entries.Count);
            w.Write((ushort)_entries.Count);
            w.Write((uint)cdSize);
            w.Write((uint)cdStart);
            w.Write((ushort)0);
            w.Flush();
            _s.Flush();
        }
    }
}
