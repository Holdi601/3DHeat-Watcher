// The Thrift compact protocol, the part a Parquet footer and page headers need:
// structs of integers, strings, lists and nested structs. Written from the
// Thrift compact protocol specification.

using System.Collections.Generic;
using System.IO;
using System.Text;

namespace Heat3D.Ghpc.Format
{
    public sealed class ThriftWriter
    {
        public const byte TBool = 1, TByte = 3, TI16 = 4, TI32 = 5, TI64 = 6, TDouble = 7, TBinary = 8, TList = 9, TStruct = 12;

        readonly Stream _out;
        readonly Stack<short> _last = new Stack<short>();
        short _field;

        public ThriftWriter(Stream output)
        {
            _out = output;
        }

        public void BeginStruct()
        {
            _last.Push(_field);
            _field = 0;
        }

        public void EndStruct()
        {
            _out.WriteByte(0); // stop
            _field = _last.Pop();
        }

        void FieldHeader(short id, byte type)
        {
            int delta = id - _field;
            if (delta > 0 && delta <= 15) _out.WriteByte((byte)((delta << 4) | type));
            else
            {
                _out.WriteByte(type);
                VarInt(ZigZag(id));
            }
            _field = id;
        }

        public void I32(short id, int v)
        {
            FieldHeader(id, TI32);
            VarInt(ZigZag(v));
        }

        public void I64(short id, long v)
        {
            FieldHeader(id, TI64);
            VarInt(ZigZag(v));
        }

        public void Bool(short id, bool v)
        {
            // Compact protocol: the value is the field type (1 true, 2 false).
            FieldHeader(id, (byte)(v ? 1 : 2));
        }

        public void String(short id, string v)
        {
            FieldHeader(id, TBinary);
            RawString(v);
        }

        public void Struct(short id)
        {
            FieldHeader(id, TStruct);
            BeginStruct();
        }

        public void List(short id, byte elemType, int count)
        {
            FieldHeader(id, TList);
            ListHeader(elemType, count);
        }

        public void ListHeader(byte elemType, int count)
        {
            if (count < 15) _out.WriteByte((byte)((count << 4) | elemType));
            else
            {
                _out.WriteByte((byte)(0xF0 | elemType));
                VarInt((ulong)count);
            }
        }

        /// A list element of type i32.
        public void ElemI32(int v) => VarInt(ZigZag(v));

        /// A list element of type binary/string.
        public void ElemString(string v) => RawString(v);

        void RawString(string v)
        {
            var b = Encoding.UTF8.GetBytes(v ?? "");
            VarInt((ulong)b.Length);
            _out.Write(b, 0, b.Length);
        }

        static ulong ZigZag(long v) => (ulong)((v << 1) ^ (v >> 63));

        void VarInt(ulong v)
        {
            while (v >= 0x80)
            {
                _out.WriteByte((byte)(v | 0x80));
                v >>= 7;
            }
            _out.WriteByte((byte)v);
        }
    }
}
