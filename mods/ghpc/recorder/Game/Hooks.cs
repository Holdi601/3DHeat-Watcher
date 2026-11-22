// The recorder's hooks into the game's rounds. Each is a Harmony prefix or
// postfix that only reads: it returns nothing (the game's method always runs,
// unchanged), sets nothing, and swallows its own errors so the game never sees
// one. Hooked by name, so a game update that renames a method leaves that part
// of the record empty (the probe says which) instead of breaking anything.
//
//   LiveRound.Init / Initialize   a round fired (or a fragment of one)
//   LiveRound.penCheck            a round met a surface: collider, normal, path, impact point
//   LiveRound.ReportShotStory     the game's account of the shot; the round's end

using System;
using System.Collections.Generic;
using System.Reflection;
using System.Threading;
using HarmonyLib;
using UnityEngine;

namespace Heat3D.Ghpc.Game
{
    public static class Hooks
    {
        public static int MainThread;
        public static readonly List<string> Installed = new List<string>();
        public static readonly List<string> Skipped = new List<string>();
        static int _errors;

        public static void Install(HarmonyLib.Harmony h)
        {
            var lr = Ghpc.LiveRound;
            if (lr == null)
            {
                Skipped.Add("LiveRound not found: no shots or hits are recorded");
                return;
            }
            foreach (var m in Api.Methods(lr, "Init", "Init", "Initialize", "Setup"))
                Patch(h, m, null, nameof(AfterInit));
            foreach (var m in Api.Methods(lr, "penCheck", "penCheck", "PenCheck"))
            {
                var ps = m.GetParameters();
                bool fits = ps.Length >= 4 && typeof(Component).IsAssignableFrom(ps[0].ParameterType)
                    && ps[1].ParameterType == typeof(Vector3) && ps[2].ParameterType == typeof(Vector3) && ps[3].ParameterType == typeof(Vector3);
                if (!fits)
                {
                    Skipped.Add("penCheck with an unexpected signature: " + Api.Signature(m));
                    continue;
                }
                Patch(h, m, nameof(BeforePen), m.ReturnType == typeof(bool) ? nameof(AfterPenBool) : nameof(AfterPen));
            }
            foreach (var m in Api.Methods(lr, "ReportShotStory", "ReportShotStory"))
                Patch(h, m, null, nameof(AfterStory));
        }

        static void Patch(HarmonyLib.Harmony h, MethodInfo m, string prefix, string postfix)
        {
            try
            {
                h.Patch(m,
                    prefix: prefix != null ? new HarmonyMethod(typeof(Hooks).GetMethod(prefix, BindingFlags.Static | BindingFlags.NonPublic)) : null,
                    postfix: postfix != null ? new HarmonyMethod(typeof(Hooks).GetMethod(postfix, BindingFlags.Static | BindingFlags.NonPublic)) : null);
                Installed.Add(Api.Signature(m));
            }
            catch (Exception e)
            {
                Skipped.Add(Api.Signature(m) + ": " + e.GetType().Name + ": " + e.Message);
            }
        }

        static Session Live()
        {
            var s = Session.Current;
            if (s == null || s.Ended || Thread.CurrentThread.ManagedThreadId != MainThread) return null;
            return s;
        }

        static void Failed(Exception e)
        {
            if (++_errors <= 10) Mod.Log("hook error (ignored): " + e.GetType().Name + ": " + e.Message);
        }

        static void AfterInit(object __instance)
        {
            try
            {
                Live()?.RoundStarted(__instance);
            }
            catch (Exception e)
            {
                Failed(e);
            }
        }

        static void BeforePen(object __instance)
        {
            try
            {
                Live()?.BeforePlate(__instance);
            }
            catch (Exception e)
            {
                Failed(e);
            }
        }

        static void Pen(object round, object[] args, bool result)
        {
            var s = Live();
            if (s == null || args == null || args.Length < 4) return;
            s.Plate(round, args[0] as Component, (Vector3)args[1], (Vector3)args[2], (Vector3)args[3], result);
        }

        static void AfterPenBool(object __instance, object[] __args, bool __result)
        {
            try
            {
                Pen(__instance, __args, __result);
            }
            catch (Exception e)
            {
                Failed(e);
            }
        }

        static void AfterPen(object __instance, object[] __args)
        {
            try
            {
                Pen(__instance, __args, false);
            }
            catch (Exception e)
            {
                Failed(e);
            }
        }

        static void AfterStory(object __instance)
        {
            try
            {
                Live()?.StoryOf(__instance);
            }
            catch (Exception e)
            {
                Failed(e);
            }
        }
    }
}
