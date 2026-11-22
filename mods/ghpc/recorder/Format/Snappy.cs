// Raw Snappy compression (the block format Parquet's SNAPPY codec uses), written
// from Google's format_description.txt: a varint length, then literals and
// copies with 2-byte offsets. Greedy, a 14-bit hash of 4-byte sequences.

using System;
using System.IO;

namespace Heat3D.Ghpc.Format
{
    public static class Snappy
    {
        public static byte[] Compress(byte[] src, int n)
        {
            var o = new MemoryStream(n / 2 + 16);
            ulong len = (ulong)n;
            while (len >= 0x80)
            {
                o.WriteByte((byte)(len | 0x80));
                len >>= 7;
            }
            o.WriteByte((byte)len);
            var table = new int[1 << 14];
            for (int k = 0; k < table.Length; k++) table[k] = -1;
            int i = 0, lit = 0;
            while (i + 4 <= n)
            {
                uint v = Read32(src, i);
                int h = (int)((v * 0x1E35A7BDu) >> 18);
                int cand = table[h];
                table[h] = i;
                if (cand >= 0 && i - cand <= 65535 && Read32(src, cand) == v)
                {
                    Literal(o, src, lit, i - lit);
                    int m = 4;
                    while (i + m < n && src[cand + m] == src[i + m]) m++;
                    int off = i - cand;
                    int rest = m;
                    while (rest > 0)
                    {
                        int l = Math.Min(64, rest);
                        // A copy shorter than 4 left over is fine for the 2-byte-offset form (1..64).
                        o.WriteByte((byte)(((l - 1) << 2) | 2));
                        o.WriteByte((byte)off);
                        o.WriteByte((byte)(off >> 8));
                        rest -= l;
                    }
                    i += m;
                    lit = i;
                }
                else
                {
                    // Step faster through data that does not repeat, as Snappy's own compressor does.
                    i += 1 + ((i - lit) >> 5);
                }
            }
            Literal(o, src, lit, n - lit);
            return o.ToArray();
        }

        static uint Read32(byte[] b, int i) => (uint)(b[i] | (b[i + 1] << 8) | (b[i + 2] << 16) | (b[i + 3] << 24));

        static void Literal(Stream o, byte[] src, int at, int len)
        {
            if (len <= 0) return;
            int l = len - 1;
            if (l < 60) o.WriteByte((byte)(l << 2));
            else if (l < 256)
            {
                o.WriteByte(60 << 2);
                o.WriteByte((byte)l);
            }
            else if (l < 65536)
            {
                o.WriteByte(61 << 2);
                o.WriteByte((byte)l);
                o.WriteByte((byte)(l >> 8));
            }
            else if (l < (1 << 24))
            {
                o.WriteByte(62 << 2);
                o.WriteByte((byte)l);
                o.WriteByte((byte)(l >> 8));
                o.WriteByte((byte)(l >> 16));
            }
            else
            {
                o.WriteByte(63 << 2);
                o.WriteByte((byte)l);
                o.WriteByte((byte)(l >> 8));
                o.WriteByte((byte)(l >> 16));
                o.WriteByte((byte)(l >> 24));
            }
            o.Write(src, at, len);
        }
    }
}
