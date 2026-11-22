// The 3DHeat recorder for Gunner, HEAT, PC!: a MelonLoader mod that writes each
// mission into one `.3dheat` file for the 3DHeat viewer. It reads the game and
// changes nothing in it: no setting, no unit, no round, no input.
//
// Settings (UserData/MelonPreferences.cfg, section [Heat3DRecorder]):
//   Enabled       record missions (true)
//   SampleHz      samples a second of each moving unit, 1..20 (10)
//   IdleHz        samples a second of a unit that does not move (1)
//   OutputFolder  where the files go (%LOCALAPPDATA%\3DHeat\Watcher\recorders\ghpc)

using System;
using System.Collections.Generic;
using System.IO;
using System.Text.RegularExpressions;
using System.Threading;
using Heat3D.Ghpc.Format;
using MelonLoader;
using UnityEngine;
using UnityEngine.SceneManagement;

[assembly: MelonInfo(typeof(Heat3D.Ghpc.Game.Mod), "3DHeat Recorder", Heat3D.Ghpc.Game.Mod.Version, "3DHeat")]
[assembly: MelonGame("Radian Simulations LLC", "GHPC")]

namespace Heat3D.Ghpc.Game
{
    public sealed class Settings
    {
        public bool Enabled = true;
        public int SampleHz = 10;
        public float IdleHz = 1;
        public string OutputFolder;
    }

    public sealed class Mod : MelonMod
    {
        public const string Version = "0.1.0";

        static MelonLogger.Instance _logger;
        readonly Settings _cfg = new Settings();
        readonly List<KeyValuePair<string, LogType>> _early = new List<KeyValuePair<string, LogType>>();
        readonly List<string> _scenes = new List<string>();
        string _missionId;
        bool _inMission;
        float _nextLook;
        bool _probed;

        static readonly Regex MissionIdLine = new Regex(@"mission overrides detected for (\S+)", RegexOptions.IgnoreCase);

        public static void Log(string s)
        {
            try
            {
                _logger?.Msg(s);
            }
            catch (Exception)
            {
            }
        }

        public override void OnInitializeMelon()
        {
            _logger = LoggerInstance;
            Hooks.MainThread = Thread.CurrentThread.ManagedThreadId;
            var cat = MelonPreferences.CreateCategory("Heat3DRecorder", "3DHeat Recorder");
            var enabled = cat.CreateEntry("Enabled", true, "Record missions");
            var hz = cat.CreateEntry("SampleHz", 10, "Samples a second of each moving unit (1-20)");
            var idle = cat.CreateEntry("IdleHz", 1f, "Samples a second of a unit that does not move");
            var defaultOut = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "3DHeat", "Watcher", "recorders", "ghpc");
            var outDir = cat.CreateEntry("OutputFolder", defaultOut, "Where the mission files go");
            _cfg.Enabled = enabled.Value;
            _cfg.SampleHz = Math.Max(1, Math.Min(20, hz.Value));
            _cfg.IdleHz = Math.Max(0.2f, idle.Value);
            _cfg.OutputFolder = string.IsNullOrEmpty(outDir.Value) ? defaultOut : Environment.ExpandEnvironmentVariables(outDir.Value);
            if (!_cfg.Enabled)
            {
                Log("recording is off (Enabled = false)");
                return;
            }
            Ghpc.Resolve();
            Hooks.Install(HarmonyInstance);
            Log($"3DHeat Recorder {Version}: {Hooks.Installed.Count} hooks in, {Ghpc.Missing.Count} names not found; files go to {_cfg.OutputFolder}");
            foreach (var s in Hooks.Skipped) Log("  left out: " + s);
            Application.logMessageReceived += OnLog;
            // A mission the game did not finish (it closed or crashed): built now, off the main thread.
            var spools = Path.Combine(_cfg.OutputFolder, ".spool");
            var folder = _cfg.OutputFolder;
            new Thread(() => MissionWriter.Recover(spools, folder, Version, Log)) { IsBackground = true, Priority = System.Threading.ThreadPriority.BelowNormal }.Start();
        }

        static bool IsMenu(string scene) => scene.IndexOf("Menu", StringComparison.OrdinalIgnoreCase) >= 0 || scene.IndexOf("Loading", StringComparison.OrdinalIgnoreCase) >= 0;

        public override void OnSceneWasInitialized(int buildIndex, string sceneName)
        {
            if (!_cfg.Enabled) return;
            if (IsMenu(sceneName))
            {
                EndSession("back to the menu");
                _inMission = false;
                _scenes.Clear();
                _missionId = null;
                return;
            }
            var s = Session.Current;
            // The same scene again while recording: the mission was restarted.
            if (s != null && !s.Ended && _scenes.Contains(sceneName))
            {
                EndSession("mission restarted");
                _scenes.Clear();
            }
            if (!_scenes.Contains(sceneName)) _scenes.Add(sceneName);
            _inMission = true;
        }

        public override void OnSceneWasUnloaded(int buildIndex, string sceneName)
        {
            if (!_cfg.Enabled) return;
            var s = Session.Current;
            if (s != null && !s.Ended && _scenes.Contains(sceneName)) EndSession("scene unloaded");
        }

        void OnLog(string text, string stack, LogType type)
        {
            if (text == null) return;
            var m = MissionIdLine.Match(text);
            if (m.Success) _missionId = m.Groups[1].Value;
            var s = Session.Current;
            if (s != null && !s.Ended)
            {
                s.LogLine(text, stack, type);
                return;
            }
            if (_early.Count < 500) _early.Add(new KeyValuePair<string, LogType>(text, type));
        }

        public override void OnUpdate()
        {
            if (!_cfg.Enabled) return;
            var s = Session.Current;
            if (s != null && !s.Ended)
            {
                try
                {
                    s.Tick();
                    if (!_probed && (s.Now > 10 || Ghpc.PlayerUnitNow() != null))
                    {
                        _probed = true;
                        var session = s;
                        Probe.WriteInBackground(Path.Combine(MelonLoader.Utils.MelonEnvironment.UserDataDirectory, "Heat3DRecorder"), Ghpc.PlayerUnitNow() as Component, json => session.Probe(json));
                    }
                }
                catch (Exception e)
                {
                    Log("recording stopped after an error: " + e);
                    try
                    {
                        s.End("recorder error");
                    }
                    catch (Exception)
                    {
                    }
                }
                return;
            }
            if (!_inMission || Ghpc.Unit == null || Time.unscaledTime < _nextLook) return;
            _nextLook = Time.unscaledTime + 1f;
            // A mission begins when its units are there.
            UnityEngine.Object[] units;
            try
            {
                units = UnityEngine.Object.FindObjectsOfType(Ghpc.Unit);
            }
            catch (Exception)
            {
                return;
            }
            if (units.Length == 0) return;
            Begin();
        }

        void Begin()
        {
            var scenes = new List<string>();
            for (int i = 0; i < SceneManager.sceneCount; i++)
            {
                var n = SceneManager.GetSceneAt(i).name;
                if (!string.IsNullOrEmpty(n) && !scenes.Contains(n)) scenes.Add(n);
            }
            var mission = _missionId;
            string map = null;
            foreach (var n in scenes)
            {
                if (IsMenu(n) || n == mission) continue;
                if (map == null) map = n;
            }
            if (mission == null) mission = scenes.Count > 0 ? scenes[scenes.Count - 1] : "mission";
            if (map == null) map = mission;
            _probed = false;
            var s = new Session(_cfg, mission, map, scenes);
            Session.Current = s;
            foreach (var kv in _early) s.LogLine(kv.Key, null, kv.Value);
            _early.Clear();
        }

        void EndSession(string why)
        {
            _inMission = false;
            var s = Session.Current;
            if (s == null || s.Ended) return;
            try
            {
                s.End(why);
            }
            catch (Exception e)
            {
                Log("ending the mission failed: " + e.Message);
            }
        }

        public override void OnApplicationQuit()
        {
            var s = Session.Current;
            EndSession("game closed");
            // The file is written on the writer's thread; the game waits for it a few seconds at most
            // (a longer mission left unwritten is built from its spool at the next start).
            s?.WaitWriter(8000);
        }
    }
}
