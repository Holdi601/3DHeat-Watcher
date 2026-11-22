// The probe: what the recorder found of the game, written once per game version
// to `UserData/Heat3DRecorder/probe-<version>.json` and into each mission's
// file. It lists each name looked up and what it resolved to, the hooks put in
// and those left out, and the fields, properties and methods of the game's
// types the recorder reads (or might read next), so a renamed member shows up
// as data rather than as a guess. It only reflects over loaded types; nothing in
// the game is called.

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.RegularExpressions;
using Heat3D.Ghpc.Format;
using UnityEngine;

namespace Heat3D.Ghpc.Game
{
    public static class Probe
    {
        static readonly Regex Interesting = new Regex(
            @"^(Unit|Vehicle|LiveRound|AmmoType|ShotInfo|ShotStory|PlayerInput|AimablePlatform|WeaponSystem|WeaponsManager|IArmor|UniformArmor|VariableArmor|Faction)$" +
            @"|Crew|Destruct|Damage|Mission|Flamm|Fire|Spall|Armor|Ammo|Penetrat|Scenario|Objective|Platoon|Debrief|Aar|SceneController",
            RegexOptions.IgnoreCase);

        /// The part that needs the game's main thread (Unity objects): the player's vehicle's build.
        public static List<object> PlayerHierarchy(Component playerUnit) => playerUnit != null ? Hierarchy(playerUnit) : null;

        /// The rest: reflection over loaded types only, safe on any thread.
        public static Dictionary<string, object> Build(List<object> playerUnit, string gameVersion, string unityVersion)
        {
            var types = new Dictionary<string, object>();
            int n = 0;
            foreach (var t in Api.GameTypes())
            {
                if (t.FullName == null || !(t.FullName.StartsWith("GHPC", StringComparison.Ordinal) || Interesting.IsMatch(t.Name))) continue;
                if (!Interesting.IsMatch(t.Name) || t.Name.Contains("<")) continue;
                if (++n > 400) break;
                types[t.FullName] = Describe(t);
            }
            var doc = new Dictionary<string, object>
            {
                ["format"] = "heat3d-ghpc-probe",
                ["recorder"] = Mod.Version,
                ["gameVersion"] = gameVersion,
                ["unityVersion"] = unityVersion,
                ["lookups"] = Api.Lookups.ToDictionary(kv => kv.Key, kv => (object)kv.Value),
                ["hooks"] = new Dictionary<string, object> { ["installed"] = Hooks.Installed, ["skipped"] = Hooks.Skipped },
                ["types"] = types,
            };
            if (playerUnit != null) doc["playerUnit"] = playerUnit;
            return doc;
        }

        static Dictionary<string, object> Describe(Type t)
        {
            const BindingFlags f = BindingFlags.Instance | BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly;
            var d = new Dictionary<string, object> { ["base"] = t.BaseType?.FullName ?? "" };
            try
            {
                if (t.IsEnum)
                {
                    d["enum"] = Enum.GetNames(t).ToList();
                    return d;
                }
                d["fields"] = t.GetFields(f).Where(x => !x.Name.Contains("<")).Select(x => x.FieldType.Name + " " + x.Name).Take(200).ToList();
                d["properties"] = t.GetProperties(f).Select(x => x.PropertyType.Name + " " + x.Name).Take(200).ToList();
                d["methods"] = t.GetMethods(f).Where(x => !x.IsSpecialName && !x.Name.Contains("<")).Select(Api.Signature).Take(200).ToList();
            }
            catch (Exception e)
            {
                d["error"] = e.GetType().Name;
            }
            return d;
        }

        /// The player's vehicle as the game builds it: each object's path and its components' types.
        static List<object> Hierarchy(Component unit)
        {
            var list = new List<object>();
            try
            {
                foreach (var tr in unit.GetComponentsInChildren<Transform>(true))
                {
                    if (list.Count >= 600) break;
                    var comps = tr.GetComponents<Component>().Where(c => c != null && !(c is Transform)).Select(c => c.GetType().Name).ToList();
                    if (comps.Count == 0) continue;
                    list.Add(new Dictionary<string, object> { ["path"] = PathOf(tr, unit.transform), ["components"] = comps });
                }
            }
            catch (Exception)
            {
            }
            return list;
        }

        static string PathOf(Transform t, Transform root)
        {
            var parts = new List<string>();
            for (var x = t; x != null && x != root.parent; x = x.parent) parts.Add(x.name);
            parts.Reverse();
            return string.Join("/", parts.ToArray());
        }

        /// Builds the probe off the main thread, writes it beside the mod's settings (one per game
        /// version) and hands it to the mission's file.
        public static void WriteInBackground(string folder, Component playerUnit, Action<string> done)
        {
            var hierarchy = PlayerHierarchy(playerUnit);
            string gv = Application.version, uv = Application.unityVersion;
            var th = new System.Threading.Thread(() =>
            {
                try
                {
                    var json = Json.Write(Build(hierarchy, gv, uv));
                    Directory.CreateDirectory(folder);
                    File.WriteAllText(Path.Combine(folder, "probe-" + Container.Safe(gv) + ".json"), json);
                    done?.Invoke(json);
                }
                catch (Exception e)
                {
                    Mod.Log("probe not written: " + e.GetType().Name + ": " + e.Message);
                }
            }) { IsBackground = true, Priority = System.Threading.ThreadPriority.BelowNormal, Name = "3DHeat GHPC probe" };
            th.Start();
        }
    }
}
