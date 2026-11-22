// The game's types and members the recorder reads, by the names the game uses
// (as public mods for the game refer to them), with the alternatives a game
// update might bring. Resolved once, when the mod starts.

using System;
using System.Collections.Generic;
using System.Reflection;
using Heat3D.Ghpc.Format;

namespace Heat3D.Ghpc.Game
{
    public static class Ghpc
    {
        public static Type Unit, Vehicle, LiveRound, AmmoType, ShotInfo, ShotStory, PlayerInput, AimablePlatform, Armor;

        // Unit
        public static Func<object, object> UnitAllegiance, UnitFriendlyName, UnitUniqueName, UnitCallsign;
        public static Func<object, bool> UnitNeutralized, UnitDestroyed;
        // LiveRound
        public static Func<object, object> RoundInfo, RoundShooter, RoundShotInfo, RoundStory, RoundParent, RoundPenLevel;
        public static Func<object, bool> RoundIsSpall;
        public static Func<object, double> RoundSpeed, RoundPenRating;
        // ShotInfo
        public static Func<object, object> ShotTypeInfo, ShotParent;
        public static Func<object, bool> ShotIsPlayer;
        public static Func<object, double> ShotDistance;
        // ShotStory
        public static Func<object, object> StoryText, StoryBuilder;
        public static Func<object, double> StoryNumber;
        // PlayerInput
        public static Func<object, object> PlayerInstance, PlayerUnit;

        public static readonly List<string> Missing = new List<string>();

        public static void Resolve()
        {
            Unit = Api.Find("Unit", "GHPC.Unit", "Unit");
            Vehicle = Api.Find("Vehicle", "GHPC.Vehicle.Vehicle", "Vehicle");
            LiveRound = Api.Find("LiveRound", "GHPC.Weapons.LiveRound", "LiveRound");
            AmmoType = Api.Find("AmmoType", "GHPC.Weapons.AmmoType", "AmmoType");
            ShotInfo = Api.Find("ShotInfo", "GHPC.Weapons.ShotInfo", "GHPC.ShotInfo", "ShotInfo");
            ShotStory = Api.Find("ShotStory", "GHPC.Weapons.ShotStory", "GHPC.ShotStory", "ShotStory");
            PlayerInput = Api.Find("PlayerInput", "GHPC.Player.PlayerInput", "PlayerInput");
            AimablePlatform = Api.Find("AimablePlatform", "GHPC.Equipment.AimablePlatform", "GHPC.AimablePlatform", "AimablePlatform");
            Armor = Api.Find("IArmor", "GHPC.IArmor", "IArmor");
            if (Unit == null) Unit = Vehicle;

            UnitAllegiance = Api.Getter(Api.Member(Unit, "Allegiance", "Allegiance", "_allegiance", "Faction"));
            UnitFriendlyName = Api.Getter(Api.Member(Unit, "FriendlyName", "FriendlyName", "_friendlyName"));
            UnitUniqueName = Api.Getter(Api.Member(Unit, "UniqueName", "UniqueName", "_uniqueName"));
            UnitCallsign = Api.Getter(Api.Member(Unit, "Callsign", "Callsign", "CallSign", "_callsign", "UnitCallsign"));
            UnitNeutralized = Api.BoolGetter(Api.Member(Unit, "Neutralized", "Neutralized", "IsNeutralized", "_neutralized"));
            UnitDestroyed = Api.BoolGetter(Api.Member(Unit, "Destroyed", "Destroyed", "IsDestroyed", "_destroyed", "Dead", "IsDead"));

            RoundInfo = Api.Getter(Api.Member(LiveRound, "Info", "Info"));
            RoundShooter = Api.Getter(Api.Member(LiveRound, "Shooter", "Shooter", "_shooter"));
            RoundShotInfo = Api.Getter(Api.Member(LiveRound, "ShotInfo", "ShotInfo"));
            RoundStory = Api.Getter(Api.Member(LiveRound, "Story", "Story"));
            RoundParent = Api.Getter(Api.Member(LiveRound, "ParentRound", "ParentRound", "_parentRound"));
            RoundPenLevel = Api.Getter(Api.Member(LiveRound, "_penetrationLevel", "_penetrationLevel", "PenetrationLevel"));
            RoundIsSpall = Api.BoolGetter(Api.Member(LiveRound, "IsSpall", "IsSpall"));
            RoundSpeed = Api.NumGetter(Api.Member(LiveRound, "CurrentSpeed", "CurrentSpeed", "_currentSpeed", "Speed"));
            RoundPenRating = Api.NumGetter(Api.Member(LiveRound, "CurrentPenRating", "CurrentPenRating"));

            ShotTypeInfo = Api.Getter(Api.Member(ShotInfo, "TypeInfo", "TypeInfo"));
            ShotParent = Api.Getter(Api.Member(ShotInfo, "ParentShot", "ParentShot"));
            ShotIsPlayer = Api.BoolGetter(Api.Member(ShotInfo, "IsPlayerShot", "IsPlayerShot"));
            ShotDistance = Api.NumGetter(Api.Member(ShotInfo, "Distance", "Distance"));

            StoryText = Api.Getter(Api.Member(ShotStory, "FinalString", "FinalString"));
            StoryBuilder = Api.Getter(Api.Member(ShotStory, "builder", "builder", "Builder"));
            StoryNumber = Api.NumGetter(Api.Member(ShotStory, "ShotNumber", "ShotNumber"));

            PlayerInstance = Api.Getter(Api.Static(PlayerInput, "Instance", "Instance", "_instance"));
            PlayerUnit = Api.Getter(Api.Member(PlayerInput, "CurrentPlayerUnit", "CurrentPlayerUnit", "_currentPlayerUnit"));

            foreach (var kv in Api.Lookups)
                if (kv.Value == "") Missing.Add(kv.Key);
        }

        public static object Safe(Func<object, object> g, object o)
        {
            if (g == null || o == null) return null;
            try
            {
                return g(o);
            }
            catch (Exception)
            {
                return null;
            }
        }

        public static bool Safe(Func<object, bool> g, object o, bool fallback = false)
        {
            if (g == null || o == null) return fallback;
            try
            {
                return g(o);
            }
            catch (Exception)
            {
                return fallback;
            }
        }

        public static double Safe(Func<object, double> g, object o)
        {
            if (g == null || o == null) return double.NaN;
            try
            {
                return g(o);
            }
            catch (Exception)
            {
                return double.NaN;
            }
        }

        static readonly object NoOwner = new object();

        /// The unit the player is in now, or null.
        public static object PlayerUnitNow()
        {
            // A static getter ignores its argument; any object will do.
            var pi = Safe(PlayerInstance, NoOwner);
            return Safe(PlayerUnit, pi);
        }

        // ------------------------------------------------------------- ammunition

        static readonly Dictionary<object, Ammo> AmmoCache = new Dictionary<object, Ammo>();

        /// What a round is, from its AmmoType (cached per AmmoType).
        public static Ammo AmmoOf(object ammoType, string weapon)
        {
            if (ammoType == null) return new Ammo { Weapon = weapon ?? "", WeaponName = weapon ?? "" };
            Ammo a;
            if (AmmoCache.TryGetValue(ammoType, out a)) return a;
            a = new Ammo
            {
                Name = Api.ReadString(ammoType, "Name", "_name", "FriendlyName") ?? "",
                Calibre = (float)Api.ReadNum(ammoType, "Caliber", "Calibre", "_caliber"),
                MuzzleVelocity = (float)Api.ReadNum(ammoType, "MuzzleVelocity", "_muzzleVelocity", "Velocity"),
                PenetrationRha = (float)Api.ReadNum(ammoType, "RhaPenetration", "_rhaPenetration", "Penetration"),
                Weapon = weapon ?? "",
                WeaponName = weapon ?? "",
            };
            a.Type = TypeOfAmmo(ammoType, a.Name);
            AmmoCache[ammoType] = a;
            return a;
        }

        /// The round's kind in the viewer's words (APFSDS, APDS, AP, HEAT, HE, HESH, ATGM, smoke...).
        static string TypeOfAmmo(object ammoType, string name)
        {
            var n = (name ?? "").ToUpperInvariant();
            var guidance = Api.ReadString(ammoType, "Guidance");
            if (guidance != null && guidance != "None" && guidance != "0") return "ATGM";
            foreach (var k in new[] { "APFSDS", "APDS", "APCBC", "APBC", "APHE", "APCR", "HEAT", "HESH", "HEP", "HE-FRAG", "HEFS", "HE", "SMOKE", "CANISTER", "AP" })
                if (n.Contains(k)) return k == "HEP" ? "HESH" : k == "HEFS" ? "HE" : k;
            var cat = Api.ReadString(ammoType, "Category");
            switch (cat)
            {
                case "Penetrator": return "kinetic";
                case "ShapedCharge": return "HEAT";
                case "Explosive": return "HE";
                case "Smoke": return "SMOKE";
                case "Flechette": return "canister";
            }
            return cat ?? "";
        }
    }
}
