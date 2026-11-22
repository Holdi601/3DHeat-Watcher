// A small JSON writer: dictionaries, lists, strings, numbers, booleans and null.
// The recorder writes its match document and manifest with it; nothing else is needed.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace Heat3D.Ghpc.Format
{
    public static class Json
    {
        public static string Write(object value, bool indent = true)
        {
            var sb = new StringBuilder();
            Emit(sb, value, indent ? 0 : -1);
            return sb.ToString();
        }

        static void Newline(StringBuilder sb, int depth)
        {
            if (depth < 0) return;
            sb.Append('\n');
            sb.Append(' ', depth);
        }

        static void Emit(StringBuilder sb, object v, int depth)
        {
            int inner = depth < 0 ? -1 : depth + 1;
            switch (v)
            {
                case null:
                    sb.Append("null");
                    return;
                case string s:
                    Str(sb, s);
                    return;
                case bool b:
                    sb.Append(b ? "true" : "false");
                    return;
                case float f:
                    Num(sb, f);
                    return;
                case double d:
                    Num(sb, d);
                    return;
                case int i:
                    sb.Append(i.ToString(CultureInfo.InvariantCulture));
                    return;
                case long l:
                    sb.Append(l.ToString(CultureInfo.InvariantCulture));
                    return;
                case IDictionary<string, object> map:
                {
                    sb.Append('{');
                    bool first = true;
                    foreach (var kv in map)
                    {
                        if (!first) sb.Append(',');
                        first = false;
                        Newline(sb, inner);
                        Str(sb, kv.Key);
                        sb.Append(depth < 0 ? ":" : ": ");
                        Emit(sb, kv.Value, inner);
                    }
                    if (!first) Newline(sb, depth);
                    sb.Append('}');
                    return;
                }
                case IEnumerable list:
                {
                    sb.Append('[');
                    bool first = true;
                    foreach (var item in list)
                    {
                        if (!first) sb.Append(',');
                        first = false;
                        Newline(sb, inner);
                        Emit(sb, item, inner);
                    }
                    if (!first) Newline(sb, depth);
                    sb.Append(']');
                    return;
                }
                default:
                    if (v is IConvertible c)
                    {
                        try
                        {
                            Num(sb, c.ToDouble(CultureInfo.InvariantCulture));
                            return;
                        }
                        catch (Exception)
                        {
                        }
                    }
                    Str(sb, v.ToString());
                    return;
            }
        }

        static void Num(StringBuilder sb, double d)
        {
            if (double.IsNaN(d) || double.IsInfinity(d)) sb.Append("null");
            else if (d == Math.Floor(d) && Math.Abs(d) < 1e15) sb.Append(((long)d).ToString(CultureInfo.InvariantCulture));
            else sb.Append(d.ToString("R", CultureInfo.InvariantCulture));
        }

        static void Str(StringBuilder sb, string s)
        {
            sb.Append('"');
            foreach (char ch in s)
            {
                switch (ch)
                {
                    case '"': sb.Append("\\\""); break;
                    case '\\': sb.Append("\\\\"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default:
                        if (ch < 0x20) sb.Append("\\u").Append(((int)ch).ToString("x4"));
                        else sb.Append(ch);
                        break;
                }
            }
            sb.Append('"');
        }
    }
}
