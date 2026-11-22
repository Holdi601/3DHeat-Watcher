// One mission being recorded: its units, sampled at the chosen rate (idle units
// at a lower one), the rounds in flight from launch to where they ended, what a
// hit did to the unit it struck, and the mission's states. Runs on the game's
// main thread and only reads; rows go to the writer thread.

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text.RegularExpressions;
using Heat3D.Ghpc.Format;
using UnityEngine;
using UnityEngine.SceneManagement;
using Pose = Heat3D.Ghpc.Format.Pose;

namespace Heat3D.Ghpc.Game
{
    public sealed class Session
    {
        public static Session Current;

        sealed class Flag
        {
            public string Event, Role, Module;
            public object Owner;
            public Func<object, bool> Get;
            public bool Invert, Last;
        }

        sealed class Tracked
        {
            public UnitInfo Info;
            public Component Comp;
            public Transform T, Turret, Gun;
            public Vector3 LastPos;
            public float LastTurret = float.NaN, LastGun = float.NaN;
            public double LastSampleT = double.NegativeInfinity, LastPosT = double.NaN;
            public float Speed;
            public List<Flag> Flags;
            public bool Neutralized, Destroyed;
            public int LastShooter = -1, LastShot;
            public double LastHitT = double.NegativeInfinity;
            public Ammo LastAmmo;
            public bool Gone;
        }

        sealed class Hit
        {
            public Tracked Victim;
            public double T;
            public Recording.Impact Impact;
        }

        sealed class RoundState
        {
            public object Round;
            public bool Pending;
            public Vector3 LaunchDir;
            public int ShotId;
            public Tracked Shooter;
            public Ammo Ammo;
            public double LaunchT;
            public Vector3 LaunchPos;
            public Hit First;
            public Recording.Impact Ground;
            public double GroundT;
            public readonly List<Hit> Plates = new List<Hit>();
            public int Spall;
            public double LastSpallT;
            public bool SpallWritten, Ended;
            public double PendingSpeed = double.NaN;
            public string Story;
        }

        public readonly Recording Rec;
        readonly MissionWriter _writer;
        readonly Settings _cfg;
        readonly double _t0;
        readonly Dictionary<object, Tracked> _units = new Dictionary<object, Tracked>(ReferenceComparer.Instance);
        readonly Dictionary<object, RoundState> _rounds = new Dictionary<object, RoundState>(ReferenceComparer.Instance);
        readonly List<RoundState> _ending = new List<RoundState>();
        readonly Dictionary<object, RoundState> _byShot = new Dictionary<object, RoundState>(ReferenceComparer.Instance);
        readonly Dictionary<string, int> _nameCount = new Dictionary<string, int>();
        readonly Dictionary<string, int> _logSeen = new Dictionary<string, int>();
        double _nextRefresh, _nextDamagePoll;
        int _nextUid = 1;
        string _lastState = "";
        public string MissionId { get; private set; }
        public string Map { get; private set; }
        public bool Ended { get; private set; }

        public double Now => Time.timeAsDouble - _t0;

        public Session(Settings cfg, string missionId, string map, List<string> scenes)
        {
            _cfg = cfg;
            _t0 = Time.timeAsDouble;
            MissionId = missionId;
            Map = map;
            var started = DateTime.UtcNow;
            var match = Container.Safe(missionId) + "_" + started.ToString("yyyyMMdd-HHmmss", CultureInfo.InvariantCulture);
            var spool = System.IO.Path.Combine(cfg.OutputFolder, ".spool", match + ".spool");
            _writer = new MissionWriter(spool, cfg.OutputFolder, Mod.Version, Mod.Log);
            Rec = new Recording(_writer, match, missionId, map, started, new Dictionary<string, object>
            {
                ["scenes"] = scenes,
                ["gameVersion"] = Application.version,
                ["unityVersion"] = Application.unityVersion,
                ["recorder"] = Mod.Version,
                ["rateHz"] = cfg.SampleHz,
                ["idleHz"] = cfg.IdleHz,
                ["axes"] = "metres; x east, y up, z north (Unity's own); hitLocal/hitDir in the struck unit's frame: x forward, y up, z right",
                ["missingNames"] = Ghpc.Missing,
            });
            Mod.Log($"recording {match} (map {map})");
        }

        // ------------------------------------------------------------------ units

        void Refresh()
        {
            if (Ghpc.Unit == null) return;
            UnityEngine.Object[] found;
            try
            {
                found = UnityEngine.Object.FindObjectsOfType(Ghpc.Unit);
            }
            catch (Exception)
            {
                return;
            }
            var player = Ghpc.PlayerUnitNow();
            foreach (var o in found)
            {
                var c = o as Component;
                if (c == null) continue;
                Tracked tr;
                if (!_units.TryGetValue(c, out tr))
                {
                    tr = Register(c);
                    _units[c] = tr;
                }
                bool isPlayer = player != null && ReferenceEquals(player, c);
                if (isPlayer != tr.Info.IsPlayer)
                {
                    tr.Info.IsPlayer = isPlayer;
                    tr.Info.Ai = !isPlayer;
                    Rec.AddUnit(tr.Info);
                }
            }
        }

        Tracked Register(Component c)
        {
            var info = new UnitInfo { Uid = _nextUid++ };
            var vehicle = Clean(Ghpc.Safe(Ghpc.UnitUniqueName, c) as string) ?? Clean(c.gameObject.name) ?? "unit";
            var friendly = Clean(Ghpc.Safe(Ghpc.UnitFriendlyName, c) as string) ?? vehicle;
            info.Vehicle = vehicle;
            info.VehicleName = friendly;
            info.Type = c.GetType().Name;
            info.Kind = KindOf(c.GetType().Name, vehicle + " " + friendly);
            var team = Ghpc.Safe(Ghpc.UnitAllegiance, c);
            info.Team = team != null ? team.ToString() : "";
            var call = Clean(Ghpc.Safe(Ghpc.UnitCallsign, c) as string);
            if (call != null) info.Name = call;
            else
            {
                var key = info.Team + "|" + friendly;
                int n;
                _nameCount.TryGetValue(key, out n);
                _nameCount[key] = ++n;
                info.Name = (info.Team != "" ? info.Team + " " : "") + friendly + " " + n.ToString(CultureInfo.InvariantCulture);
            }
            var tr = new Tracked { Info = info, Comp = c, T = c.transform };
            FindTurret(tr);
            info.Crew = CrewRoles(c);
            info.Weapons = WeaponNames(c);
            Rec.AddUnit(info);
            return tr;
        }

        static string Clean(string s)
        {
            if (string.IsNullOrEmpty(s)) return null;
            s = s.Replace("(Clone)", "").Trim();
            return s.Length == 0 ? null : s;
        }

        static readonly Regex Tank = new Regex(@"\b(M1|M1A1|M1IP|M60|T-?[5-9]\d|T-?80|T-?64|T-?62|T-?55|T-?54|LEO|LEOPARD|CHIEFTAIN|PT-?76|TANK|MBT)", RegexOptions.IgnoreCase);
        static readonly Regex Ifv = new Regex(@"\b(BMP|BMD|M2|M3|BRADLEY|MARDER|IFV)", RegexOptions.IgnoreCase);
        static readonly Regex Apc = new Regex(@"\b(BTR|M113|BRDM|MTLB|MT-LB|APC|FUCHS|TPZ)", RegexOptions.IgnoreCase);
        static readonly Regex Truck = new Regex(@"\b(URAL|UAZ|M923|M151|HMMWV|TRUCK|KAMAZ|GAZ|ZIL|JEEP|CAR)", RegexOptions.IgnoreCase);
        static readonly Regex Air = new Regex(@"\b(MI-?\d|AH-?\d|UH-?\d|OH-?\d|HELI|HIND)", RegexOptions.IgnoreCase);

        /// The unit's kind in the viewer's words (it picks a figure by it when the name is unknown).
        public static string KindOf(string typeName, string names)
        {
            var t = typeName ?? "";
            if (t.IndexOf("Infantry", StringComparison.OrdinalIgnoreCase) >= 0 || t.IndexOf("Soldier", StringComparison.OrdinalIgnoreCase) >= 0) return "infantry";
            if (t.IndexOf("Heli", StringComparison.OrdinalIgnoreCase) >= 0 || t.IndexOf("Aircraft", StringComparison.OrdinalIgnoreCase) >= 0 || Air.IsMatch(names)) return "helicopter";
            if (Ifv.IsMatch(names)) return "ifv";
            if (Tank.IsMatch(names)) return "tank";
            if (Apc.IsMatch(names)) return "apc";
            if (Truck.IsMatch(names)) return "truck";
            return "vehicle";
        }

        void FindTurret(Tracked tr)
        {
            var platforms = new List<Transform>();
            if (Ghpc.AimablePlatform != null)
            {
                try
                {
                    foreach (var p in tr.Comp.GetComponentsInChildren(Ghpc.AimablePlatform, true)) platforms.Add(p.transform);
                }
                catch (Exception)
                {
                }
            }
            foreach (var p in platforms)
            {
                var n = p.name.ToLowerInvariant();
                if (tr.Gun == null && (n.Contains("gun") || n.Contains("mantlet") || n.Contains("elev") || n.Contains("barrel"))) tr.Gun = p;
                else if (tr.Turret == null && (n.Contains("turret") || n.Contains("trav"))) tr.Turret = p;
            }
            foreach (var p in platforms)
            {
                if (tr.Turret == null && p != tr.Gun) tr.Turret = p;
                else if (tr.Gun == null && p != tr.Turret) tr.Gun = p;
            }
            if (tr.Turret == null || tr.Gun == null)
            {
                foreach (var t in tr.Comp.GetComponentsInChildren<Transform>(true))
                {
                    var n = t.name.ToLowerInvariant();
                    if (tr.Turret == null && n.Contains("turret") && !n.Contains("ring")) tr.Turret = t;
                    else if (tr.Gun == null && (n == "gun" || n.EndsWith("_gun") || n.Contains("mantlet") || n.Contains("barrel"))) tr.Gun = t;
                }
            }
        }

        static readonly Regex Role = new Regex(@"commander|gunner|loader|driver|radio|bow|operator", RegexOptions.IgnoreCase);

        static List<string> CrewRoles(Component c)
        {
            var roles = new List<string>();
            try
            {
                foreach (var comp in c.GetComponentsInChildren<Component>(true))
                {
                    if (comp == null) continue;
                    var tn = comp.GetType().Name;
                    if (tn.IndexOf("Crew", StringComparison.Ordinal) < 0 || tn.IndexOf("Manager", StringComparison.Ordinal) >= 0) continue;
                    var role = Api.ReadString(comp, "Position", "Role", "Seat", "CrewPosition", "Station") ?? comp.gameObject.name;
                    var m = Role.Match(role);
                    var r = m.Success ? m.Value.ToLowerInvariant() : role;
                    if (!roles.Contains(r)) roles.Add(r);
                    if (roles.Count >= 8) break;
                }
            }
            catch (Exception)
            {
            }
            return roles;
        }

        static List<string> WeaponNames(Component c)
        {
            var names = new List<string>();
            try
            {
                foreach (var comp in c.GetComponentsInChildren<Component>(true))
                {
                    if (comp == null || comp.GetType().Name != "WeaponSystem") continue;
                    var n = Api.ReadString(comp, "Name", "FriendlyName", "_name") ?? comp.gameObject.name;
                    if (!names.Contains(n)) names.Add(n);
                    if (names.Count >= 8) break;
                }
            }
            catch (Exception)
            {
            }
            return names;
        }

        // ---------------------------------------------------------------- samples

        public void Tick()
        {
            if (Ended) return;
            double t = Now;
            if (t >= _nextRefresh)
            {
                _nextRefresh = t + 2.0;
                Refresh();
            }
            double fast = 1.0 / Math.Max(1, Math.Min(20, _cfg.SampleHz));
            double slow = 1.0 / Math.Max(0.2, Math.Min(_cfg.SampleHz, _cfg.IdleHz));
            bool poll = t >= _nextDamagePoll;
            if (poll) _nextDamagePoll = t + 0.25;
            foreach (var tr in _units.Values)
            {
                if (tr.Gone) continue;
                if (tr.Comp == null)
                {
                    // Removed from the scene (despawned): its last row stays its end.
                    tr.Gone = true;
                    continue;
                }
                if (poll) PollState(tr, t);
                double since = t - tr.LastSampleT;
                if (since < fast) continue;
                var pose = PoseOf(tr, t);
                bool moved = (pose_pos - tr.LastPos).sqrMagnitude > 0.0025f
                    || Changed(tr.LastTurret, pose.TurretYaw, 0.5f) || Changed(tr.LastGun, pose.GunPitch, 0.3f);
                if (!moved && since < slow) continue;
                tr.LastPos = pose_pos;
                tr.LastTurret = pose.TurretYaw;
                tr.LastGun = pose.GunPitch;
                tr.LastSampleT = t;
                Rec.Sample(t, tr.Info, pose);
            }
            EndRounds(t, false);
        }

        static bool Changed(float a, float b, float d) => float.IsNaN(a) != float.IsNaN(b) || (!float.IsNaN(a) && Math.Abs(Mathf.DeltaAngle(a, b)) > d);

        Vector3 pose_pos;

        Pose PoseOf(Tracked tr, double t)
        {
            var T = tr.T;
            var pos = T.position;
            pose_pos = pos;
            if (!double.IsNaN(tr.LastPosT) && t > tr.LastPosT)
            {
                float d = (pos - tr.LastPos).magnitude;
                tr.Speed = (float)(d / (t - tr.LastPosT));
            }
            tr.LastPosT = t;
            var f = T.forward;
            var p = new Pose
            {
                X = pos.x, Y = pos.y, Z = pos.z, FX = f.x, FY = f.y, FZ = f.z,
                Heading = Wrap360(Mathf.Atan2(f.x, f.z) * Mathf.Rad2Deg),
                Pitch = Mathf.Asin(Mathf.Clamp(f.y, -1, 1)) * Mathf.Rad2Deg,
                Roll = -Mathf.DeltaAngle(0, T.eulerAngles.z),
                Speed = tr.Speed,
                Alive = !tr.Info.Out,
                TurretYaw = float.NaN,
                GunPitch = float.NaN,
            };
            if (tr.Turret != null)
            {
                var d = T.InverseTransformDirection(tr.Turret.forward);
                p.TurretYaw = Mathf.Atan2(d.x, d.z) * Mathf.Rad2Deg;
            }
            if (tr.Gun != null)
            {
                var d = T.InverseTransformDirection(tr.Gun.forward);
                p.GunPitch = Mathf.Asin(Mathf.Clamp(d.y, -1, 1)) * Mathf.Rad2Deg;
                if (tr.Turret == null) p.TurretYaw = Mathf.Atan2(d.x, d.z) * Mathf.Rad2Deg;
            }
            return p;
        }

        static float Wrap360(float a)
        {
            a %= 360f;
            return a < 0 ? a + 360f : a;
        }

        // ------------------------------------------------------- what a hit did

        void PollState(Tracked tr, double t)
        {
            bool neut = Ghpc.Safe(Ghpc.UnitNeutralized, tr.Comp);
            bool dead = Ghpc.Safe(Ghpc.UnitDestroyed, tr.Comp);
            if ((neut && !tr.Neutralized) || (dead && !tr.Destroyed))
            {
                var killer = tr.LastShooter >= 0 && t - tr.LastHitT < 30 ? ByUid(tr.LastShooter) : null;
                if (!tr.Info.Out) Rec.Destroyed(t, tr.Info, killer?.Info, dead ? "destroyed" : "neutralized", killer != null ? tr.LastAmmo : null, killer != null ? tr.LastShot : 0);
                else if (dead && !tr.Destroyed) Rec.Damage(t, "wrecked", tr.Info, killer?.Info, killer != null ? tr.LastShot : 0, null, null, "destroyed after it was out of the fight");
            }
            tr.Neutralized |= neut;
            tr.Destroyed |= dead;
            // The parts are watched for half a minute after each hit.
            if (t - tr.LastHitT > 30) return;
            if (tr.Flags == null) tr.Flags = DiscoverFlags(tr.Comp);
            foreach (var f in tr.Flags)
            {
                bool v;
                try
                {
                    v = f.Get(f.Owner) != f.Invert;
                }
                catch (Exception)
                {
                    continue;
                }
                if (v && !f.Last)
                {
                    var by = ByUid(tr.LastShooter);
                    Rec.Damage(t, f.Event, tr.Info, by?.Info, tr.LastShot, f.Role, f.Module, "watched");
                    Noted(tr.Info.Uid, f.Event, f.Role ?? f.Module, t);
                }
                else if (!v && f.Last && f.Event == "fire_on")
                {
                    Rec.Damage(t, "fire_off", tr.Info, null, 0, null, f.Module, "watched");
                }
                f.Last = v;
            }
        }

        static readonly string[] CrewOut = { "Dead", "IsDead", "Killed", "IsKilled", "Incapacitated", "IsIncapacitated", "KnockedOut", "IsKnockedOut", "Unconscious" };
        static readonly string[] CrewIn = { "Alive", "IsAlive", "Conscious", "IsConscious" };
        static readonly string[] PartOut = { "Destroyed", "IsDestroyed", "_destroyed", "Broken", "IsBroken", "Disabled", "IsDisabled", "IsDead", "Dead" };
        static readonly string[] Health = { "Health", "_health", "HitPoints", "_hitPoints", "CurrentHealth", "_currentHealth" };
        static readonly string[] Burning = { "IsBurning", "Burning", "_burning", "OnFire", "IsOnFire", "Ignited", "IsIgnited" };
        static readonly string[] Cooked = { "Detonated", "IsDetonated", "CookedOff", "IsCookedOff", "CookingOff", "IsCookingOff", "Exploded", "HasExploded" };
        static readonly Regex PartType = new Regex("Destructible|Damageable|Module|Subsystem|Engine|Transmission|Track|Breech|Barrel|Optic|Sight|Radiator|FuelTank|Turret", RegexOptions.IgnoreCase);
        static readonly Regex FireType = new Regex("Fire|Flamm|Burn", RegexOptions.IgnoreCase);
        static readonly Regex AmmoType = new Regex("AmmoRack|AmmoStorage|Ammunition|AmmoBox|CookOff|Cookoff|Magazine", RegexOptions.IgnoreCase);

        static List<Flag> DiscoverFlags(Component unit)
        {
            var flags = new List<Flag>();
            Component[] comps;
            try
            {
                comps = unit.GetComponentsInChildren<Component>(true);
            }
            catch (Exception)
            {
                return flags;
            }
            foreach (var c in comps)
            {
                if (c == null || flags.Count >= 64) continue;
                var type = c.GetType();
                var ns = type.Namespace ?? "";
                if (ns.StartsWith("UnityEngine", StringComparison.Ordinal) || ns.StartsWith("TMPro", StringComparison.Ordinal)) continue;
                var tn = type.Name;
                string ev = null;
                string[] outNames = null, inNames = null;
                if (tn.IndexOf("Crew", StringComparison.Ordinal) >= 0 && tn.IndexOf("Manager", StringComparison.Ordinal) < 0)
                {
                    ev = "crew_ko";
                    outNames = CrewOut;
                    inNames = CrewIn;
                }
                else if (AmmoType.IsMatch(tn))
                {
                    ev = "ammo_detonation";
                    outNames = Cooked;
                }
                else if (FireType.IsMatch(tn))
                {
                    ev = "fire_on";
                    outNames = Burning;
                }
                else if (PartType.IsMatch(tn))
                {
                    ev = "module_destroyed";
                    outNames = PartOut;
                }
                if (ev == null) continue;
                var getter = Api.BoolGetter(Api.Member(type, ev + ":" + tn, outNames));
                bool invert = false;
                if (getter == null && inNames != null)
                {
                    getter = Api.BoolGetter(Api.Member(type, ev + "-alive:" + tn, inNames));
                    invert = getter != null;
                }
                if (getter == null && ev != "fire_on" && ev != "ammo_detonation") getter = Api.BoolGetter(Api.Member(type, ev + "-health:" + tn, Health));
                if (getter == null) continue;
                var f = new Flag { Event = ev, Owner = c, Get = getter, Invert = invert };
                if (ev == "crew_ko")
                {
                    var role = Api.ReadString(c, "Position", "Role", "Seat", "CrewPosition", "Station") ?? c.gameObject.name;
                    var m = Role.Match(role);
                    f.Role = m.Success ? m.Value.ToLowerInvariant() : role;
                }
                else f.Module = Api.ReadString(c, "Name", "FriendlyName", "_name", "ComponentName") ?? c.gameObject.name;
                try
                {
                    f.Last = getter(c) != invert;
                }
                catch (Exception)
                {
                    continue;
                }
                flags.Add(f);
            }
            return flags;
        }

        /// What was seen happen to a unit lately, so the shot story does not say it twice.
        readonly Dictionary<string, double> _noted = new Dictionary<string, double>();

        void Noted(int uid, string ev, string what, double t) => _noted[uid + "|" + ev + "|" + (what ?? "")] = t;

        bool WasNoted(int uid, string ev, string what, double t)
        {
            double at;
            return _noted.TryGetValue(uid + "|" + ev + "|" + (what ?? ""), out at) && Math.Abs(at - t) < 3;
        }

        Tracked ByUid(int uid)
        {
            if (uid < 0) return null;
            foreach (var tr in _units.Values)
                if (tr.Info.Uid == uid) return tr;
            return null;
        }

        Tracked UnitOf(object unit)
        {
            if (unit == null) return null;
            Tracked tr;
            if (_units.TryGetValue(unit, out tr)) return tr;
            var c = unit as Component;
            if (c == null) return null;
            tr = Register(c);
            _units[c] = tr;
            return tr;
        }

        // ------------------------------------------------------------------ rounds

        RoundState StateOf(object round, bool create)
        {
            RoundState s;
            if (_rounds.TryGetValue(round, out s) && (!s.Ended || !create))
            {
                if (s.Pending) Complete(s);
                return s;
            }
            if (!create) return null;
            s = Launch(round);
            Complete(s);
            return s;
        }

        /// A round leaves the gun (or is first seen): its place now, the `launch` row once the game has
        /// set its shooter and ammunition (the next frame, or the round's first contact if sooner).
        RoundState Launch(object round)
        {
            RoundState old;
            if (_rounds.TryGetValue(round, out old) && !old.Ended) EndRound(old, Now);
            var s = new RoundState { Round = round, Pending = true, LaunchT = Now };
            var rc = round as Component;
            if (rc != null)
            {
                s.LaunchPos = rc.transform.position;
                s.LaunchDir = rc.transform.forward;
            }
            _rounds[round] = s;
            return s;
        }

        void Complete(RoundState s)
        {
            if (!s.Pending) return;
            s.Pending = false;
            var round = s.Round;
            var shooter = UnitOf(Ghpc.Safe(Ghpc.RoundShooter, round));
            var shot = Ghpc.Safe(Ghpc.RoundShotInfo, round);
            var ammo = Ghpc.Safe(Ghpc.RoundInfo, round) ?? Ghpc.Safe(Ghpc.ShotTypeInfo, shot);
            s.Shooter = shooter;
            s.Ammo = Ghpc.AmmoOf(ammo, shooter != null && shooter.Info.Weapons.Count > 0 ? shooter.Info.Weapons[0] : null);
            if (shot != null) _byShot[shot] = s;
            var pos = s.LaunchPos;
            if (pos == Vector3.zero && shooter != null) pos = s.LaunchPos = shooter.T.position;
            var dir = s.LaunchDir == Vector3.zero ? Vector3.forward : s.LaunchDir;
            s.ShotId = Rec.Launch(s.LaunchT, shooter?.Info, s.Ammo, pos.x, pos.y, pos.z, dir.x, dir.y, dir.z);
        }

        /// A fragment or a sub-round of a round in flight: counted on the round it came from.
        public void SpallOf(object spallRound)
        {
            RoundState s = null;
            var parent = Ghpc.Safe(Ghpc.RoundParent, spallRound);
            if (parent != null) s = StateOf(parent, false);
            if (s == null)
            {
                var ps = Ghpc.Safe(Ghpc.ShotParent, Ghpc.Safe(Ghpc.RoundShotInfo, spallRound));
                if (ps != null) _byShot.TryGetValue(ps, out s);
            }
            if (s == null) return;
            s.Spall++;
            s.LastSpallT = Now;
        }

        /// A new round: a spall fragment counts on its parent, anything else is a launch.
        public void RoundStarted(object round)
        {
            if (Ghpc.Safe(Ghpc.RoundIsSpall, round) || Ghpc.Safe(Ghpc.RoundParent, round) != null) SpallOf(round);
            else Launch(round);
        }

        public void BeforePlate(object round)
        {
            if (Ghpc.Safe(Ghpc.RoundIsSpall, round) || Ghpc.Safe(Ghpc.RoundParent, round) != null) return;
            var s = StateOf(round, true);
            s.PendingSpeed = Ghpc.Safe(Ghpc.RoundSpeed, round);
        }

        /// A round met a surface (penCheck): the first unit it struck is the hit, further plates are kept too.
        public void Plate(object round, Component collider, Vector3 normal, Vector3 path, Vector3 impact, bool result)
        {
            if (Ghpc.Safe(Ghpc.RoundIsSpall, round) || Ghpc.Safe(Ghpc.RoundParent, round) != null) return;
            var s = StateOf(round, true);
            double t = Now;
            Component unitComp = null;
            if (collider != null && Ghpc.Unit != null)
            {
                try
                {
                    unitComp = collider.GetComponentInParent(Ghpc.Unit);
                }
                catch (Exception)
                {
                }
            }
            var levelObj = Ghpc.Safe(Ghpc.RoundPenLevel, round);
            int level = levelObj is IConvertible ? Convert.ToInt32(levelObj, CultureInfo.InvariantCulture) : int.MinValue;
            var h = new Recording.Impact
            {
                WX = impact.x, WY = impact.y, WZ = impact.z,
                Speed = (float)s.PendingSpeed,
                Plate = collider != null ? Clean(collider.gameObject.name) : null,
                Level = level,
                Detail = "penCheck " + (result ? "true" : "false"),
            };
            var dirN = path.sqrMagnitude > 1e-9f ? path.normalized : Vector3.zero;
            if (normal.sqrMagnitude > 1e-9f && dirN != Vector3.zero) h.Angle = Vector3.Angle(-dirN, normal.normalized);
            if (unitComp == null)
            {
                if (s.First == null && s.Ground == null)
                {
                    h.Outcome = "ground";
                    s.Ground = h;
                    s.GroundT = t;
                }
                return;
            }
            var victim = UnitOf(unitComp);
            if (victim == null || victim == s.Shooter) return;
            var vt = victim.T;
            var local = vt.InverseTransformPoint(impact);
            var ldir = vt.InverseTransformDirection(dirN);
            // The figure frame: x forward, y up, z right (Unity's local is x right, y up, z forward).
            h.LX = local.z; h.LY = local.y; h.LZ = local.x;
            if (dirN != Vector3.zero)
            {
                h.DX = ldir.z; h.DY = ldir.y; h.DZ = ldir.x;
            }
            bool pen = level != int.MinValue ? level >= 2 : result;
            h.Penetrated = pen ? 1 : 0;
            h.Outcome = pen ? "penetration" : "nonpenetration";
            if (s.Shooter != null) h.Distance = (s.Shooter.T.position - impact).magnitude;
            var hit = new Hit { Victim = victim, T = t, Impact = h };
            if (s.First == null) s.First = hit;
            else if (s.Plates.Count < 32) s.Plates.Add(hit);
            victim.LastShooter = s.Shooter != null ? s.Shooter.Info.Uid : -1;
            victim.LastShot = s.ShotId;
            victim.LastAmmo = s.Ammo;
            victim.LastHitT = t;
        }

        /// The game reported the round's story: its account of the shot, and the round's end.
        public void StoryOf(object round)
        {
            if (Ghpc.Safe(Ghpc.RoundIsSpall, round) || Ghpc.Safe(Ghpc.RoundParent, round) != null) return;
            var s = StateOf(round, true);
            var story = Ghpc.Safe(Ghpc.RoundStory, round);
            var text = Ghpc.Safe(Ghpc.StoryText, story) as string;
            if (string.IsNullOrEmpty(text))
            {
                var b = Ghpc.Safe(Ghpc.StoryBuilder, story);
                text = b?.ToString();
            }
            s.Story = text;
            EndRound(s, Now);
        }

        void EndRounds(double t, bool all)
        {
            _ending.Clear();
            foreach (var s in _rounds.Values)
            {
                if (s.Pending) Complete(s);
                if (s.Ended)
                {
                    if (!s.SpallWritten && s.Spall > 0 && t - s.LastSpallT > 0.5) WriteSpall(s);
                    continue;
                }
                // A round no story ended: closed ten seconds after it was fired.
                if (all || t - s.LaunchT > 10) _ending.Add(s);
            }
            foreach (var s in _ending) EndRound(s, t);
            if (_rounds.Count > 512)
            {
                var drop = new List<object>();
                foreach (var kv in _rounds)
                    if (kv.Value.Ended && (kv.Value.SpallWritten || kv.Value.Spall == 0) && t - kv.Value.LaunchT > 30) drop.Add(kv.Key);
                foreach (var k in drop) _rounds.Remove(k);
                var dropShots = new List<object>();
                foreach (var kv in _byShot)
                    if (kv.Value.Ended && t - kv.Value.LaunchT > 30) dropShots.Add(kv.Key);
                foreach (var k in dropShots) _byShot.Remove(k);
            }
        }

        void EndRound(RoundState s, double t)
        {
            if (s.Ended) return;
            if (s.Pending) Complete(s);
            s.Ended = true;
            var shooter = s.Shooter?.Info;
            var story = s.Story ?? "";
            if (s.First != null)
            {
                var h = s.First.Impact;
                if (h.Outcome == "nonpenetration" && Regex.IsMatch(story, "ricochet", RegexOptions.IgnoreCase)) h.Outcome = "ricochet";
                double flight = s.First.T - s.LaunchT;
                if (flight > 0.01) h.FlightSpeed = (float)((new Vector3(h.WX, h.WY, h.WZ) - s.LaunchPos).magnitude / flight);
                Rec.Shot(s.First.T, s.ShotId, shooter, s.First.Victim.Info, s.Ammo, h);
                foreach (var p in s.Plates) Rec.PlateHit(p.T, s.ShotId, p.Victim.Info, shooter, s.Ammo, p.Impact);
                if (story.Length > 0) StoryDamage(s, story, t);
            }
            else if (s.Ground != null)
            {
                double flight = s.GroundT - s.LaunchT;
                if (flight > 0.01) s.Ground.FlightSpeed = (float)((new Vector3(s.Ground.WX, s.Ground.WY, s.Ground.WZ) - s.LaunchPos).magnitude / flight);
                Rec.Shot(s.GroundT, s.ShotId, shooter, null, s.Ammo, s.Ground);
            }
            if (story.Length > 0) Rec.Story(t, s.ShotId, shooter, story);
        }

        void WriteSpall(RoundState s)
        {
            s.SpallWritten = true;
            var victim = s.First?.Victim;
            if (victim == null) return;
            Rec.Damage(s.LastSpallT, "spall", victim.Info, s.Shooter?.Info, s.ShotId, null, null, "fragments", s.Spall);
        }

        static readonly Regex StoryCrew = new Regex(@"\b(commander|gunner|loader|driver)\b[^\n]*?\b(killed|incapacitated|wounded|dead|knocked out|injured)\b", RegexOptions.IgnoreCase);
        static readonly Regex StoryPart = new Regex(@"^\s*(?:the\s+)?([A-Za-z][\w \-/]{1,40}?)\s+(?:was\s+|is\s+)?(destroyed|disabled|knocked out)\b", RegexOptions.IgnoreCase | RegexOptions.Multiline);
        static readonly Regex StoryFire = new Regex(@"\b(fire|burning|ignited|caught fire)\b", RegexOptions.IgnoreCase);
        static readonly Regex StoryAmmo = new Regex(@"cook[- ]?off|(ammunition|ammo)[^\n]*(detonat|explod)", RegexOptions.IgnoreCase);

        /// What the game's account of a shot says it did, where the watched parts did not show it.
        void StoryDamage(RoundState s, string story, double t)
        {
            var v = s.First.Victim;
            var by = s.Shooter?.Info;
            foreach (Match m in StoryCrew.Matches(story))
            {
                var role = m.Groups[1].Value.ToLowerInvariant();
                if (WasNoted(v.Info.Uid, "crew_ko", role, s.First.T)) continue;
                Rec.Damage(s.First.T, "crew_ko", v.Info, by, s.ShotId, role, null, "shot story: " + m.Groups[2].Value.ToLowerInvariant());
            }
            foreach (Match m in StoryPart.Matches(story))
            {
                var part = m.Groups[1].Value.Trim();
                if (Role.IsMatch(part) || WasNoted(v.Info.Uid, "module_destroyed", part, s.First.T)) continue;
                Rec.Damage(s.First.T, "module_destroyed", v.Info, by, s.ShotId, null, part, "shot story");
            }
            if (StoryAmmo.IsMatch(story)) Rec.Damage(s.First.T, "ammo_detonation", v.Info, by, s.ShotId, null, null, "shot story");
            else if (StoryFire.IsMatch(story)) Rec.Damage(s.First.T, "fire_on", v.Info, by, s.ShotId, null, null, "shot story");
        }

        // ------------------------------------------------------- mission and log

        static readonly Regex MissionState = new Regex(@"MissionState changed to (\w+)");

        public void LogLine(string text, string stack, LogType type)
        {
            if (Ended || text == null) return;
            double t = Now;
            var m = MissionState.Match(text);
            if (m.Success)
            {
                _lastState = m.Groups[1].Value;
                Rec.State(t, PlayerTracked()?.Info, _lastState);
            }
            // The converter rule keeps every line; a line said thousands of times (an exception in a
            // loop) is kept 20 times, the rest counted in the match document.
            int n;
            _logSeen.TryGetValue(text, out n);
            _logSeen[text] = n + 1;
            if (n < 20) Rec.Log(t, type.ToString(), text, n == 0 && type != LogType.Log ? stack : null);
        }

        Tracked PlayerTracked()
        {
            foreach (var tr in _units.Values)
                if (tr.Info.IsPlayer) return tr;
            return null;
        }

        /// The mission ends: rounds closed, `finish` rows, the result, and the file written on the writer's thread.
        public void End(string why)
        {
            if (Ended) return;
            double t = Now;
            EndRounds(t, true);
            foreach (var s in _rounds.Values)
                if (!s.SpallWritten && s.Spall > 0) WriteSpall(s);
            var player = PlayerTracked();
            string outcome = null, winner = null, reason = null;
            var st = _lastState.ToLowerInvariant();
            string own = player?.Info.Team ?? "";
            string enemy = null;
            foreach (var tr in _units.Values)
                if (tr.Info.Team != "" && tr.Info.Team != own && tr.Info.Team != "Neutral") enemy = tr.Info.Team;
            if (Regex.IsMatch(st, "victory|win|won|success|complete")) { outcome = "victory"; winner = own != "" ? own : null; reason = "objective"; }
            else if (Regex.IsMatch(st, "defeat|lose|lost|fail")) { outcome = "defeat"; winner = enemy; reason = "objective"; }
            // Who is left, as a second opinion where the state says nothing.
            var left = new Dictionary<string, int>();
            foreach (var tr in _units.Values)
            {
                if (tr.Info.Out || tr.Info.Team == "" || tr.Info.Team == "Neutral") continue;
                int k;
                left.TryGetValue(tr.Info.Team, out k);
                left[tr.Info.Team] = k + 1;
            }
            var unitsLeft = new Dictionary<string, object>();
            foreach (var kv in left) unitsLeft[kv.Key] = kv.Value;
            Rec.Top("unitsLeft", unitsLeft);
            Rec.Top("endedBy", why);
            Rec.Top("lastState", _lastState);
            var repeats = new Dictionary<string, object>();
            foreach (var kv in _logSeen)
                if (kv.Value > 20 && repeats.Count < 200) repeats[kv.Key.Length > 300 ? kv.Key.Substring(0, 300) : kv.Key] = kv.Value;
            Rec.Top("logRepeats", repeats);
            Rec.End(t, winner, outcome ?? "unknown", reason, _lastState);
            Ended = true;
            _writer.Finish();
            Mod.Log($"mission ended ({why}); writing the file");
        }

        public void Probe(string json) => _writer.Meta("probe", json);

        public bool WaitWriter(int ms) => _writer.Join(ms);
    }

    sealed class ReferenceComparer : IEqualityComparer<object>
    {
        public static readonly ReferenceComparer Instance = new ReferenceComparer();
        public new bool Equals(object a, object b) => ReferenceEquals(a, b);
        public int GetHashCode(object o) => System.Runtime.CompilerServices.RuntimeHelpers.GetHashCode(o);
    }
}
