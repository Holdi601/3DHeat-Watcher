// Heat3D recorder: records an Arma 3 mission on the server, for 3DHeat.
// Loaded with -serverMod only; players install nothing. MIT licence.

class CfgPatches {
    class heat3d_recorder {
        name = "Heat3D recorder";
        author = "3DHeat";
        units[] = {};
        weapons[] = {};
        requiredVersion = 2.10;
        requiredAddons[] = {"A3_Functions_F"};
    };
};

class CfgFunctions {
    class heat3d {
        tag = "heat3d";
        class recorder {
            file = "\heat3d_recorder\functions";
            class init { postInit = 1; };
            class json {};
            class entity {};
            class event {};
            class flush {};
            class loop {};
            class finish {};
        };
    };
};

// Settings. A mission or the server's own scripts can override each one by
// setting missionNamespace variable heat3d_<name> before the first frame.
class Heat3D {
    captureDelay = 1;   // seconds between two samples of every unit and vehicle
    recordHits = 1;     // 1: a "hit" event for every hit on a unit (an MPHit handler per unit)
    recordShots = 1;    // 1: shots fired (a FiredMan handler per unit)
    minPlayers = 0;     // start recording only once this many players are connected
};
