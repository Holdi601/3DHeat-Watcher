// How the recorder finds its way into the game's own code: types and members
// looked up by name at run time (the game's assemblies are not shipped or
// referenced at build time), each with the names it may have, and read through
// getters compiled once. Everything here reads; nothing sets a field, calls a
// setter or a method with an effect.
//
// What was found and what was not goes into the probe (Probe.cs), so a game
// update that renames something shows up as a missing name, not as a crash.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using System.Reflection;

namespace Heat3D.Ghpc.Game
{
    public static class Api
    {
        public const BindingFlags All = BindingFlags.Instance | BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.FlattenHierarchy;
        public const BindingFlags Inst = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;

        /// What was looked for, and what it resolved to ("" when not found), for the probe.
        public static readonly SortedDictionary<string, string> Lookups = new SortedDictionary<string, string>(StringComparer.Ordinal);

        static Assembly[] _game;

        /// The game's own assemblies: Assembly-CSharp first, then the others that name GHPC types.
        public static Assembly[] GameAssemblies
        {
            get
            {
                if (_game != null) return _game;
                var list = new List<Assembly>();
                foreach (var a in AppDomain.CurrentDomain.GetAssemblies())
                {
                    var n = a.GetName().Name;
                    if (n == "Assembly-CSharp") list.Insert(0, a);
                    else if (n == "Assembly-CSharp-firstpass" || n.StartsWith("GHPC", StringComparison.Ordinal)) list.Add(a);
                }
                _game = list.ToArray();
                return _game;
            }
        }

        public static IEnumerable<Type> GameTypes()
        {
            foreach (var a in GameAssemblies)
            {
                Type[] types;
                try
                {
                    types = a.GetTypes();
                }
                catch (ReflectionTypeLoadException e)
                {
                    types = e.Types.Where(t => t != null).ToArray();
                }
                foreach (var t in types) yield return t;
            }
        }

        /// The first of `names` (full names, or short names matched anywhere) that exists.
        public static Type Find(string label, params string[] names)
        {
            foreach (var n in names)
            {
                foreach (var a in GameAssemblies)
                {
                    var t = a.GetType(n, false);
                    if (t != null) return Note(label, t);
                }
            }
            foreach (var n in names)
            {
                if (n.Contains(".")) continue;
                var t = GameTypes().FirstOrDefault(x => x.Name == n);
                if (t != null) return Note(label, t);
            }
            Lookups["type " + label] = "";
            return null;
        }

        static Type Note(string label, Type t)
        {
            Lookups["type " + label] = t.FullName;
            return t;
        }

        /// A field or property of `t` (or its bases) by the first name that exists.
        public static MemberInfo Member(Type t, string label, params string[] names)
        {
            if (t == null) return null;
            foreach (var n in names)
            {
                for (var b = t; b != null; b = b.BaseType)
                {
                    var f = b.GetField(n, Inst | BindingFlags.DeclaredOnly);
                    if (f != null) return NoteMember(t, label, f);
                    var p = b.GetProperty(n, Inst | BindingFlags.DeclaredOnly);
                    if (p != null && p.GetIndexParameters().Length == 0 && p.GetGetMethod(true) != null) return NoteMember(t, label, p);
                }
            }
            Lookups[t.Name + "." + label] = "";
            return null;
        }

        /// A static field or property (an `Instance`), by the first name that exists.
        public static MemberInfo Static(Type t, string label, params string[] names)
        {
            if (t == null) return null;
            const BindingFlags st = BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.FlattenHierarchy;
            foreach (var n in names)
            {
                var f = t.GetField(n, st);
                if (f != null) return NoteMember(t, label, f);
                var p = t.GetProperty(n, st);
                if (p != null && p.GetGetMethod(true) != null) return NoteMember(t, label, p);
            }
            Lookups[t.Name + "." + label] = "";
            return null;
        }

        static MemberInfo NoteMember(Type t, string label, MemberInfo m)
        {
            Lookups[t.Name + "." + label] = m.Name + ": " + TypeOf(m).Name;
            return m;
        }

        public static Type TypeOf(MemberInfo m) => m is FieldInfo f ? f.FieldType : ((PropertyInfo)m).PropertyType;

        /// Methods of `t` declared with one of `names` (every overload), for read-only hooks.
        public static List<MethodInfo> Methods(Type t, string label, params string[] names)
        {
            var found = new List<MethodInfo>();
            if (t == null) return found;
            foreach (var n in names)
            {
                foreach (var m in t.GetMethods(Inst | BindingFlags.DeclaredOnly))
                    if (m.Name == n && !m.IsAbstract && !m.IsGenericMethodDefinition) found.Add(m);
                if (found.Count > 0) break;
            }
            Lookups[t.Name + "." + label + "()"] = found.Count == 0 ? "" : string.Join("; ", found.Select(Signature).ToArray());
            return found;
        }

        public static string Signature(MethodInfo m) =>
            m.ReturnType.Name + " " + m.Name + "(" + string.Join(", ", m.GetParameters().Select(p => p.ParameterType.Name + " " + p.Name).ToArray()) + ")";

        // ------------------------------------------------------------- getters

        /// A compiled getter: object -> object (boxed); null when `m` is null.
        public static Func<object, object> Getter(MemberInfo m)
        {
            if (m == null) return null;
            try
            {
                var p = Expression.Parameter(typeof(object), "o");
                Expression owner = IsStatic(m) ? null : Expression.Convert(p, m.DeclaringType);
                Expression body = m is FieldInfo f ? Expression.Field(owner, f) : Expression.Property(owner, (PropertyInfo)m);
                return Expression.Lambda<Func<object, object>>(Expression.Convert(body, typeof(object)), p).Compile();
            }
            catch (Exception)
            {
                if (m is FieldInfo f2) return o => f2.GetValue(o);
                var g = ((PropertyInfo)m).GetGetMethod(true);
                return o => g.Invoke(o, null);
            }
        }

        static bool IsStatic(MemberInfo m) => m is FieldInfo f ? f.IsStatic : ((PropertyInfo)m).GetGetMethod(true).IsStatic;

        /// A compiled getter for a bool member (no boxing on the way): object -> bool.
        public static Func<object, bool> BoolGetter(MemberInfo m)
        {
            if (m == null) return null;
            var t = TypeOf(m);
            try
            {
                var p = Expression.Parameter(typeof(object), "o");
                Expression owner = IsStatic(m) ? null : Expression.Convert(p, m.DeclaringType);
                Expression body = m is FieldInfo f ? Expression.Field(owner, f) : Expression.Property(owner, (PropertyInfo)m);
                if (t == typeof(bool)) { }
                else if (t == typeof(float) || t == typeof(double) || t == typeof(int)) body = Expression.LessThanOrEqual(Expression.Convert(body, typeof(double)), Expression.Constant(0.0));
                else return null;
                return Expression.Lambda<Func<object, bool>>(body, p).Compile();
            }
            catch (Exception)
            {
                var g = Getter(m);
                return o =>
                {
                    var v = g(o);
                    return v is bool b ? b : v is IConvertible c && c.ToDouble(null) <= 0;
                };
            }
        }

        /// A compiled getter for a number: object -> double (NaN when it is not one).
        public static Func<object, double> NumGetter(MemberInfo m)
        {
            if (m == null) return null;
            var t = TypeOf(m);
            if (t != typeof(float) && t != typeof(double) && t != typeof(int) && t != typeof(long) && t != typeof(short) && !t.IsEnum) return null;
            try
            {
                var p = Expression.Parameter(typeof(object), "o");
                Expression owner = IsStatic(m) ? null : Expression.Convert(p, m.DeclaringType);
                Expression body = m is FieldInfo f ? Expression.Field(owner, f) : Expression.Property(owner, (PropertyInfo)m);
                if (t.IsEnum) body = Expression.Convert(body, Enum.GetUnderlyingType(t));
                return Expression.Lambda<Func<object, double>>(Expression.Convert(body, typeof(double)), p).Compile();
            }
            catch (Exception)
            {
                var g = Getter(m);
                return o => Convert.ToDouble(g(o));
            }
        }

        /// Reads `obj.<first name that exists>` once, without a compiled getter (rare reads).
        public static object Read(object obj, params string[] names)
        {
            if (obj == null) return null;
            var t = obj.GetType();
            foreach (var n in names)
            {
                for (var b = t; b != null; b = b.BaseType)
                {
                    try
                    {
                        var f = b.GetField(n, Inst | BindingFlags.DeclaredOnly);
                        if (f != null) return f.GetValue(obj);
                        var p = b.GetProperty(n, Inst | BindingFlags.DeclaredOnly);
                        if (p != null && p.GetIndexParameters().Length == 0 && p.GetGetMethod(true) != null) return p.GetValue(obj, null);
                    }
                    catch (Exception)
                    {
                        // A getter that throws is a value we do not have.
                    }
                }
            }
            return null;
        }

        public static string ReadString(object obj, params string[] names)
        {
            var v = Read(obj, names);
            if (v == null) return null;
            var s = v as string ?? v.ToString();
            return string.IsNullOrEmpty(s) ? null : s;
        }

        public static double ReadNum(object obj, params string[] names)
        {
            var v = Read(obj, names);
            if (v == null) return double.NaN;
            try
            {
                return v is Enum ? Convert.ToDouble(Convert.ChangeType(v, Enum.GetUnderlyingType(v.GetType()))) : Convert.ToDouble(v);
            }
            catch (Exception)
            {
                return double.NaN;
            }
        }
    }
}
