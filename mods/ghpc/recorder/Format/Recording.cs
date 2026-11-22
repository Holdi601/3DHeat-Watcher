// What a mission's rows say, independent of the game: the game side reads the
// game and calls these; the synthetic mission in the tests calls the same ones.
//
// Rows (the `event` column):
//   (none)          a unit's sample: place, heading, speed, turret and gun
//   spawn           a unit first seen
//   launch          a round leaves the gun: shooter, weapon, ammunition, muzzle speed
//   shot            where a round ended: the shooter's row, `targetX/Y/Z` the impact;
//                   on a unit also `other`, `otherVehicle`, `hitLocal*`, `hitDir*`,
//                   `hitOutcome` (penetration, nonpenetration, ricochet)
//   plate_hit       each further armour plate the same round struck
//   spall           fragments a penetration threw (count, on the victim's row)
//   crew_ko         a crew member out (victim's row, `crewRole`, `other` the shooter)
//   module_destroyed a part of a unit destroyed (`module`)
//   fire_on / fire_off  a unit burning
//   ammo_detonation the ammunition went up
//   destroyed       a unit out of the fight (victim's row, `other` the killer, `state`)
//   mission_state   the mission's state changed (`state`)
//   finish          a unit's last row when the mission ends
//   story           the game's own account of a shot (`text`), as it shows it
//   log             a line of the game's log (kept in the raw sidecar)

using System;
using System.Collections.Generic;
using System.Globalization;

namespace Heat3D.Ghpc.Format
{
    public sealed class UnitInfo
    {
        public int Uid;
        public string Track = "", Name = "", Vehicle = "", VehicleName = "", Kind = "", Type = "", Team = "";
        public bool Ai = true, IsPlayer;
        public List<string> Crew = new List<string>();
        public List<string> Weapons = new List<string>();
        public bool Spawned, Out;
        public double FirstSeen = double.NaN, LastSeen = double.NaN;
        // The last place, for rows that have none of their own.
        public float X, Y, Z;
    }

    public struct Pose
    {
        public float X, Y, Z;
        /// The hull's forward vector (unit), in the world.
        public float FX, FY, FZ;
        public float Heading, Pitch, Roll, Speed;
        public bool Alive;
        /// Degrees, relative to the hull, + right; NaN when the unit has no turret.
        public float TurretYaw;
        /// Degrees, + up; NaN when not known.
        public float GunPitch;
    }

    public sealed class Ammo
    {
        public string Name = "", Type = "", Weapon = "", WeaponName = "";
        public float Calibre = float.NaN, MuzzleVelocity = float.NaN, PenetrationRha = float.NaN;
    }

    public sealed class Recording
    {
        public readonly MissionWriter Writer;
        public readonly string Match, Mission, Map;
        readonly Dictionary<int, UnitInfo> _units = new Dictionary<int, UnitInfo>();
        int _kills;
        public int Shots { get; private set; }

        public Recording(MissionWriter writer, string match, string mission, string map, DateTime startedUtc, IDictionary<string, object> extra)
        {
            Writer = writer;
            Match = match;
            Mission = mission;
            Map = map;
            Top("match", match);
            Top("mission", mission);
            Top("map", map);
            Top("mode", "mission");
            Top("started", startedUtc.ToString("yyyy-MM-ddTHH:mm:ssZ", CultureInfo.InvariantCulture));
            if (extra != null)
                foreach (var kv in extra) Writer.Meta("top/" + kv.Key, Json.Write(kv.Value, false));
        }

        public void Top(string key, object value) => Writer.Meta("top/" + key, Json.Write(value, false));

        public UnitInfo Unit(int uid) => _units.TryGetValue(uid, out var u) ? u : null;
        public IEnumerable<UnitInfo> Units => _units.Values;

        public void AddUnit(UnitInfo u)
        {
            if (string.IsNullOrEmpty(u.Track)) u.Track = "u" + u.Uid.ToString(CultureInfo.InvariantCulture);
            _units[u.Uid] = u;
            WriteUnit(u);
        }

        void WriteUnit(UnitInfo u)
        {
            var d = new Dictionary<string, object>
            {
                ["uid"] = u.Uid, ["track"] = u.Track, ["name"] = u.Name, ["vehicle"] = u.Vehicle, ["vehicleName"] = u.VehicleName,
                ["kind"] = u.Kind, ["type"] = u.Type, ["team"] = u.Team, ["ai"] = u.Ai, ["isPlayer"] = u.IsPlayer,
                ["crew"] = u.Crew, ["weapons"] = u.Weapons, ["firstSeen"] = Num(u.FirstSeen), ["lastSeen"] = Num(u.LastSeen), ["out"] = u.Out,
            };
            Writer.Meta("units/" + u.Uid.ToString("D6", CultureInfo.InvariantCulture), Json.Write(d, false));
        }

        static object Num(double v) => double.IsNaN(v) ? null : (object)Math.Round(v, 3);

        Row Base(double t, UnitInfo u, string ev)
        {
            var r = Writer.Rent();
            r.Set(Col.Time, t);
            if (ev != null) r.Set(Col.Event, ev);
            r.Set(Col.Match, Match).Set(Col.Mission, Mission).Set(Col.Map, Map).Set(Col.Round, 1);
            if (u != null)
            {
                r.Set(Col.Track, u.Track).Set(Col.Life, u.Track).Set(Col.Uid, u.Uid).Set(Col.Player, u.Name).Set(Col.Team, u.Team)
                    .Set(Col.Ai, u.Ai).Set(Col.IsPlayer, u.IsPlayer).Set(Col.Kind, u.Kind).Set(Col.Type, u.Type)
                    .Set(Col.Vehicle, u.Vehicle).Set(Col.VehicleName, u.VehicleName);
            }
            return r;
        }

        static void Place(Row r, float x, float y, float z) => r.Set(Col.X, x).Set(Col.Y, y).Set(Col.Z, z);

        void PlaceOf(Row r, UnitInfo u)
        {
            if (u != null) Place(r, u.X, u.Y, u.Z);
            else Place(r, 0, 0, 0);
        }

        static void PoseOf(Row r, in Pose p)
        {
            Place(r, p.X, p.Y, p.Z);
            r.Set(Col.DirX, p.FX).Set(Col.DirY, p.FY).Set(Col.DirZ, p.FZ)
                .Set(Col.Heading, p.Heading).Set(Col.Pitch, p.Pitch).Set(Col.Roll, p.Roll).Set(Col.Speed, p.Speed)
                .Set(Col.Alive, p.Alive).Set(Col.TurretYaw, p.TurretYaw).Set(Col.GunPitch, p.GunPitch);
        }

        public void Sample(double t, UnitInfo u, in Pose p)
        {
            u.X = p.X;
            u.Y = p.Y;
            u.Z = p.Z;
            if (double.IsNaN(u.FirstSeen)) u.FirstSeen = t;
            u.LastSeen = t;
            if (!u.Spawned)
            {
                u.Spawned = true;
                var s = Base(t, u, "spawn");
                PoseOf(s, p);
                s.Set(Col.Crew, string.Join(",", u.Crew.ToArray()));
                Writer.Commit(s);
            }
            var r = Base(t, u, null);
            PoseOf(r, p);
            Writer.Commit(r);
        }

        public int Launch(double t, UnitInfo shooter, Ammo a, float x, float y, float z, float dx, float dy, float dz)
        {
            int id = ++Shots;
            var r = Base(t, shooter, "launch");
            Place(r, x, y, z);
            r.Set(Col.DirX, dx).Set(Col.DirY, dy).Set(Col.DirZ, dz);
            r.Set(Col.Shot, id);
            AmmoOf(r, a);
            Writer.Commit(r);
            return id;
        }

        static void AmmoOf(Row r, Ammo a)
        {
            if (a == null) return;
            r.Set(Col.Weapon, a.Weapon).Set(Col.WeaponName, a.WeaponName).Set(Col.AmmoName, a.Name).Set(Col.AmmoType, a.Type)
                .Set(Col.Calibre, a.Calibre).Set(Col.MuzzleVelocity, a.MuzzleVelocity).Set(Col.PenetrationRha, a.PenetrationRha);
        }

        /// A hit's numbers: where, which way, what the plate did.
        public sealed class Impact
        {
            public float WX, WY, WZ;
            /// The hit point in the struck unit's frame (m: x forward, y up, z right); NaN when no unit.
            public float LX = float.NaN, LY = float.NaN, LZ = float.NaN;
            /// The way the round travelled, in the struck unit's frame (unit vector).
            public float DX = float.NaN, DY = float.NaN, DZ = float.NaN;
            public float Angle = float.NaN, Speed = float.NaN, Distance = float.NaN, FlightSpeed = float.NaN;
            public string Plate, Outcome, Detail;
            public int Penetrated = -1, Level = int.MinValue;
        }

        /// Where a round ended or first struck a unit: the shooter's `shot` row.
        public void Shot(double t, int shotId, UnitInfo shooter, UnitInfo victim, Ammo a, Impact h)
        {
            var r = Base(t, shooter, "shot");
            if (shooter != null) PlaceOf(r, shooter);
            else Place(r, h.WX, h.WY, h.WZ);
            r.Set(Col.Shot, shotId);
            AmmoOf(r, a);
            r.Set(Col.TargetX, h.WX).Set(Col.TargetY, h.WY).Set(Col.TargetZ, h.WZ);
            // The tracer's speed: how fast the round came, on average, where known.
            if (!float.IsNaN(h.FlightSpeed)) r.Set(Col.Speed, h.FlightSpeed);
            ImpactOf(r, h);
            if (victim != null)
            {
                r.Set(Col.Other, victim.Name).Set(Col.OtherVehicle, victim.Vehicle).Set(Col.OtherLife, victim.Track).Set(Col.OtherTeam, victim.Team);
            }
            Writer.Commit(r);
        }

        static void ImpactOf(Row r, Impact h)
        {
            r.Set(Col.HitLocalX, h.LX).Set(Col.HitLocalY, h.LY).Set(Col.HitLocalZ, h.LZ)
                .Set(Col.HitDirX, h.DX).Set(Col.HitDirY, h.DY).Set(Col.HitDirZ, h.DZ)
                .Set(Col.HitOutcome, h.Outcome).Set(Col.ImpactAngle, h.Angle).Set(Col.ImpactSpeed, h.Speed)
                .Set(Col.Plate, h.Plate).Set(Col.Distance, h.Distance).Set(Col.Detail, h.Detail);
            if (h.Penetrated >= 0) r.Set(Col.Penetrated, h.Penetrated);
            if (h.Level != int.MinValue) r.Set(Col.PenetrationLevel, h.Level);
        }

        /// A further plate the same round struck (the victim's row).
        public void PlateHit(double t, int shotId, UnitInfo victim, UnitInfo shooter, Ammo a, Impact h)
        {
            var r = Base(t, victim, "plate_hit");
            Place(r, h.WX, h.WY, h.WZ);
            r.Set(Col.Shot, shotId);
            AmmoOf(r, a);
            ImpactOf(r, h);
            // The shooter by name only: `otherVehicle` beside a point on a unit means the unit hit (the shooter's
            // `shot` row), and this row is the struck unit's own. `shotId` ties it to that row.
            if (shooter != null) r.Set(Col.Other, shooter.Name).Set(Col.OtherLife, shooter.Track).Set(Col.OtherTeam, shooter.Team);
            Writer.Commit(r);
        }

        /// Something a hit did to a unit (crew_ko, module_destroyed, fire_on, fire_off, ammo_detonation, spall).
        public void Damage(double t, string ev, UnitInfo victim, UnitInfo by, int shotId, string crewRole, string module, string detail, int count = -1)
        {
            var r = Base(t, victim, ev);
            PlaceOf(r, victim);
            if (shotId > 0) r.Set(Col.Shot, shotId);
            if (by != null) r.Set(Col.Other, by.Name).Set(Col.OtherVehicle, by.Vehicle).Set(Col.OtherLife, by.Track).Set(Col.OtherTeam, by.Team);
            r.Set(Col.CrewRole, crewRole).Set(Col.Module, module).Set(Col.Detail, detail);
            // The viewer's module rows name the part in `weapon` (a War Thunder habit), so it goes there too.
            if (ev == "module_destroyed" && module != null) r.Set(Col.Weapon, module);
            if (count >= 0) r.Set(Col.Spall, count);
            Writer.Commit(r);
        }

        /// A unit out of the fight: the victim's `destroyed` row, the killer in `other`.
        public void Destroyed(double t, UnitInfo victim, UnitInfo killer, string state, Ammo a, int shotId)
        {
            if (victim.Out) return;
            victim.Out = true;
            var r = Base(t, victim, "destroyed");
            PlaceOf(r, victim);
            r.Set(Col.State, state);
            if (shotId > 0) r.Set(Col.Shot, shotId);
            AmmoOf(r, a);
            if (killer != null)
            {
                r.Set(Col.Other, killer.Name).Set(Col.OtherVehicle, killer.Vehicle).Set(Col.OtherLife, killer.Track).Set(Col.OtherTeam, killer.Team);
                r.Set(Col.Distance, Dist(victim, killer));
            }
            Writer.Commit(r);
            var k = new Dictionary<string, object>
            {
                ["time"] = Math.Round(t, 3),
                ["killer"] = killer?.Name ?? "", ["killerVehicle"] = killer?.Vehicle ?? "", ["killerTeam"] = killer?.Team ?? "",
                ["victim"] = victim.Name, ["victimVehicle"] = victim.Vehicle, ["victimTeam"] = victim.Team, ["victimUid"] = victim.Uid,
                ["weapon"] = a?.Weapon ?? "", ["weaponName"] = a?.WeaponName ?? "", ["ammoName"] = a?.Name ?? "", ["state"] = state,
            };
            Writer.Meta("kills/" + (++_kills).ToString("D6", CultureInfo.InvariantCulture), Json.Write(k, false));
            WriteUnit(victim);
        }

        static float Dist(UnitInfo a, UnitInfo b)
        {
            float dx = a.X - b.X, dy = a.Y - b.Y, dz = a.Z - b.Z;
            return (float)Math.Sqrt(dx * dx + dy * dy + dz * dz);
        }

        public void Story(double t, int shotId, UnitInfo shooter, string text)
        {
            var r = Base(t, shooter, "story");
            PlaceOf(r, shooter);
            if (shotId > 0) r.Set(Col.Shot, shotId);
            r.Set(Col.Text, text);
            Writer.Commit(r);
        }

        public void State(double t, UnitInfo at, string state)
        {
            var r = Base(t, null, "mission_state");
            PlaceOf(r, at);
            r.Set(Col.State, state);
            Writer.Commit(r);
        }

        public void Log(double t, string type, string text, string detail)
        {
            var r = Writer.Rent();
            r.Set(Col.Time, t).Set(Col.Event, Container.LogEvent).Set(Col.State, type).Set(Col.Text, text).Set(Col.Detail, detail);
            Writer.Commit(r);
        }

        /// The end: a `finish` row per unit with what the mission came to, and the document's result.
        public void End(double t, string winner, string outcome, string reason, string state)
        {
            foreach (var u in _units.Values)
            {
                if (!u.Spawned) continue;
                var r = Base(t, u, "finish");
                PlaceOf(r, u);
                if (!string.IsNullOrEmpty(winner) && !string.IsNullOrEmpty(u.Team))
                {
                    int w = u.Team == winner ? 1 : 0;
                    r.Set(Col.Won, w).Set(Col.MatchWon, w);
                }
                if (reason != null) r.Set(Col.RoundEndReason, reason);
                Writer.Commit(r);
                WriteUnit(u);
            }
            Writer.Meta("result", Json.Write(new Dictionary<string, object>
            {
                ["winner"] = winner, ["outcome"] = outcome, ["reason"] = reason, ["state"] = state, ["ended"] = Math.Round(t, 3),
            }, false));
            Top("timePlayed", Math.Round(t, 3));
            if (winner != null) Top("winner", winner);
            if (reason != null) Top("roundEndReason", reason);
        }
    }
}
