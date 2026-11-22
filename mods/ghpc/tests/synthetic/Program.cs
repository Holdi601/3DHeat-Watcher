// A made-up mission written through the recorder's own writer: two units a side
// driving for a minute, shots, hits with points on the vehicle, a penetration
// that knocks out crew and a module, a fire and a kill, the mission's states and
// a few log lines. The tests read the file it writes with independent readers
// (pyarrow, the viewer's own) - nothing here comes from the game.
//
//   dotnet run --project mods/ghpc/tests/synthetic -- <out folder> [--crash]
//
// --crash stops the writer without finishing, then builds the file the way the
// mod does at its next start (from the spool left behind).

using System;
using System.Collections.Generic;
using System.IO;
using Heat3D.Ghpc.Format;

static class Program
{
    static int Main(string[] args)
    {
        if (args.Length < 1)
        {
            Console.Error.WriteLine("usage: synthetic <out folder> [--crash]");
            return 2;
        }
        string outDir = Path.GetFullPath(args[0]);
        bool crash = Array.IndexOf(args, "--crash") >= 0;
        string spool = Path.Combine(outDir, "spool", "synthetic.spool");
        var writer = new MissionWriter(spool, outDir, "0.0.0-test", s => Console.WriteLine(s));
        var started = new DateTime(2026, 1, 1, 12, 0, 0, DateTimeKind.Utc);
        var rec = new Recording(writer, "TEST01_synthetic_20260101-120000", "TEST01_synthetic", "test_terrain", started,
            new Dictionary<string, object> { ["missionTitle"] = "Synthetic test", ["gameVersion"] = "test", ["rateHz"] = 10 });

        var units = new[]
        {
            new UnitInfo { Uid = 1, Name = "Blue 1", Vehicle = "M1IP", VehicleName = "M1IP Abrams", Kind = "tank", Type = "Vehicle", Team = "Blue", Ai = false, IsPlayer = true,
                Crew = { "commander", "gunner", "loader", "driver" }, Weapons = { "M68A1 105mm" } },
            new UnitInfo { Uid = 2, Name = "Blue 2", Vehicle = "M2BRADLEY", VehicleName = "M2 Bradley", Kind = "ifv", Type = "Vehicle", Team = "Blue",
                Crew = { "commander", "gunner", "driver" }, Weapons = { "M242 25mm", "TOW" } },
            new UnitInfo { Uid = 3, Name = "Red 1", Vehicle = "T72M1", VehicleName = "T-72M1", Kind = "tank", Type = "Vehicle", Team = "Red",
                Crew = { "commander", "gunner", "driver" }, Weapons = { "2A46 125mm" } },
            new UnitInfo { Uid = 4, Name = "Red 2", Vehicle = "BMP1", VehicleName = "BMP-1", Kind = "ifv", Type = "Vehicle", Team = "Red",
                Crew = { "commander", "gunner", "driver" }, Weapons = { "2A28 73mm" } },
        };
        foreach (var u in units) rec.AddUnit(u);
        var sabot = new Ammo { Name = "M774 APFSDS-T", Type = "APFSDS", Weapon = "M68A1", WeaponName = "M68A1 105mm", Calibre = 105, MuzzleVelocity = 1508, PenetrationRha = 400 };
        var heat = new Ammo { Name = "3BK18M HEAT-FS", Type = "HEAT", Weapon = "2A46", WeaponName = "2A46 125mm", Calibre = 125, MuzzleVelocity = 905, PenetrationRha = 550 };

        rec.State(0, units[0], "Planning");
        rec.State(1, units[0], "Playing");
        rec.Log(0.5, "Log", "MissionState changed to Playing", null);
        bool redOneOut = false;
        for (int step = 0; step <= 600; step++)
        {
            double t = step / 10.0;
            for (int i = 0; i < units.Length; i++)
            {
                var u = units[i];
                bool blue = u.Team == "Blue";
                float lane = (i % 2) * 40f;
                float along = (float)(t * (u.Kind == "tank" ? 6 : 8));
                var p = new Pose
                {
                    X = blue ? -500 + along : 500 - along, Y = 100 + (float)Math.Sin(t / 10) * 2, Z = lane,
                    FX = blue ? 1 : -1, FY = 0, FZ = 0, Heading = blue ? 90 : 270, Pitch = 0, Roll = 0,
                    Speed = (u.Out || (u.Uid == 3 && redOneOut)) ? 0 : (u.Kind == "tank" ? 6 : 8),
                    Alive = !u.Out, TurretYaw = (float)(10 * Math.Sin(t / 5)), GunPitch = 1.5f,
                };
                rec.Sample(t, u, p);
            }
            if (step == 200)
            {
                // Blue 1 fires at Red 1: a ricochet off the upper glacis.
                int id = rec.Launch(t, units[0], sabot, units[0].X + 4, units[0].Y + 2, units[0].Z, 1, 0, 0);
                double hitT = t + 0.6;
                rec.Shot(hitT, id, units[0], units[2], sabot, new Recording.Impact
                {
                    WX = units[2].X - 3, WY = units[2].Y + 1.2f, WZ = units[2].Z, LX = 3, LY = 1.2f, LZ = 0.1f, DX = -1, DY = 0, DZ = 0,
                    Angle = 78, Speed = 1480, Distance = 880, FlightSpeed = 1490, Plate = "UFP", Outcome = "ricochet", Penetrated = 0, Level = 0,
                });
                rec.Story(hitT + 0.2, id, units[0], "Shot 1: M774 APFSDS-T ricocheted off the T-72M1 upper front plate");
            }
            if (step == 260)
            {
                // Second shot: a penetration through the turret front; gunner out, gun destroyed, a fire, then the tank is out.
                int id = rec.Launch(t, units[0], sabot, units[0].X + 4, units[0].Y + 2, units[0].Z, 1, 0, 0);
                double hitT = t + 0.5;
                rec.Shot(hitT, id, units[0], units[2], sabot, new Recording.Impact
                {
                    WX = units[2].X - 2, WY = units[2].Y + 1.9f, WZ = units[2].Z + 0.4f, LX = 2, LY = 1.9f, LZ = -0.4f, DX = -0.99f, DY = -0.05f, DZ = 0.1f,
                    Angle = 22, Speed = 1475, Distance = 760, FlightSpeed = 1490, Plate = "turret front", Outcome = "penetration", Penetrated = 1, Level = 2,
                });
                rec.PlateHit(hitT + 0.001, id, units[2], units[0], sabot, new Recording.Impact
                {
                    WX = units[2].X - 1, WY = units[2].Y + 1.8f, WZ = units[2].Z + 0.4f, LX = 1, LY = 1.8f, LZ = -0.4f, Plate = "turret ring", Outcome = "penetration", Penetrated = 1, Level = 2,
                });
                rec.Damage(hitT + 0.01, "spall", units[2], units[0], id, null, null, "behind-armour fragments", 14);
                rec.Damage(hitT + 0.02, "crew_ko", units[2], units[0], id, "gunner", null, "killed");
                rec.Damage(hitT + 0.02, "module_destroyed", units[2], units[0], id, null, "main gun breech", null);
                rec.Damage(hitT + 0.5, "fire_on", units[2], units[0], id, null, "fuel tank", "fire");
                rec.Destroyed(hitT + 1.0, units[2], units[0], "neutralized", sabot, id);
                redOneOut = true;
                rec.Story(hitT + 0.2, id, units[0], "Shot 2: M774 APFSDS-T penetrated the T-72M1 turret front\nGunner killed\nMain gun breech destroyed");
            }
            if (step == 320)
            {
                // Red 2's HEAT round misses, into the ground.
                int id = rec.Launch(t, units[3], heat, units[3].X - 3, units[3].Y + 2, units[3].Z, -1, 0, 0);
                rec.Shot(t + 1.0, id, units[3], null, heat, new Recording.Impact { WX = units[1].X + 20, WY = 99, WZ = units[1].Z + 5, FlightSpeed = 880, Outcome = "ground" });
            }
            if (step == 330) rec.Log(t, "Warning", "a warning line from the game's log", null);
        }
        rec.State(60, units[0], "Finished");
        rec.End(60, "Blue", "victory", "elimination", "Finished");

        if (crash)
        {
            writer.Abandon();
            writer.Join(10000);
            var got = MissionWriter.Recover(Path.GetDirectoryName(spool), outDir, "0.0.0-test", s => Console.WriteLine(s));
            if (got.Count != 1) return 1;
            Console.WriteLine(got[0]);
            return 0;
        }
        writer.Finish();
        if (!writer.Join(60000) || writer.Output == null)
        {
            Console.Error.WriteLine("writer failed: " + writer.Error);
            return 1;
        }
        Console.WriteLine(writer.Output);
        return 0;
    }
}
