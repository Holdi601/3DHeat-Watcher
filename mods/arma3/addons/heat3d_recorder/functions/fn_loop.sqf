/*
 * heat3d_fnc_loop: one frame every captureDelay seconds, for as long as the
 * mission records. A frame holds every unit and vehicle once:
 *   unit:    [[x, y, z], dir, alive, inVehicle, name, isPlayer, role, group, side]
 *   vehicle: [[x, y, z], dir, alive, [crew ids]]
 * x east, y north, z above sea level (getPosASL), metres; dir a compass
 * bearing; alive 1, 0 dead, 2 unconscious. Getting in and out of vehicles is
 * found here too, from where each unit sat the frame before.
 */
private _tab = heat3d_tab;
private _json = heat3d_fnc_json;
private _p2 = { (str (100 + _this)) select [1] };
while { heat3d_recording } do {
    private _t0 = diag_tickTime;
    private _f = heat3d_frame;
    heat3d_buffer pushBack format ["N%1%2", _tab, _f];
    if (_f % 10 == 0) then {
        systemTimeUTC params ["_y", "_mo", "_d", "_h", "_mi", "_s", "_ms"];
        private _utc = format ["%1-%2-%3T%4:%5:%6", _y, _mo call _p2, _d call _p2, _h call _p2, _mi call _p2, _s call _p2] + "." + ((str (1000 + _ms)) select [1]);
        heat3d_buffer pushBack format ['T%1{"frameNum":%2,"time":%3,"systemTimeUTC":"%4","timeMultiplier":%5}', _tab, _f, time, _utc, timeMultiplier];
    };

    // Newcomers: units alive and dead, and vehicles (not the weapon holders and ruins `vehicles` also lists).
    { if (_x getVariable ["heat3d_id", -1] < 0) then { [_x] call heat3d_fnc_entity } } forEach (allUnits + allDeadMen);
    {
        if (_x getVariable ["heat3d_id", -1] < 0 && {_x isKindOf "AllVehicles"} && {!(_x isKindOf "CAManBase")}) then { [_x] call heat3d_fnc_entity };
    } forEach vehicles;
    // A deleted object's track ends.
    heat3d_tracked = heat3d_tracked select { !isNull _x };

    {
        private _o = _x;
        private _id = _o getVariable "heat3d_id";
        private _def = _o getVariable ["heat3d_def", ""];
        if (_def != "") then {
            heat3d_buffer pushBack format ['E%1%2%1%3,"startFrameNum":%4}', _tab, _id, _def, _f];
            _o setVariable ["heat3d_def", ""];
        };
        private _p = getPosASL _o;
        private _pos = format ["[%1,%2,%3]", _p#0 toFixed 1, _p#1 toFixed 1, _p#2 toFixed 1];
        private _alive = [0, 1] select alive _o;
        if (_o isKindOf "CAManBase") then {
            if (_alive == 1 && {lifeState _o == "INCAPACITATED"}) then { _alive = 2 };
            private _veh = objectParent _o;
            private _vid = if (isNull _veh) then { -1 } else { [_veh] call heat3d_fnc_entity };
            private _was = _o getVariable ["heat3d_in", -1];
            if (_vid != _was) then {
                if (_was >= 0) then { heat3d_buffer pushBack format ['V%1[%2,"getout",%3,%4]', _tab, _f, _id, _was] };
                if (_vid >= 0) then { heat3d_buffer pushBack format ['V%1[%2,"getin",%3,%4]', _tab, _f, _id, _vid] };
                _o setVariable ["heat3d_in", _vid];
            };
            // The name, escaped once for as long as it stays the same.
            private _name = name _o;
            if (_o getVariable ["heat3d_name", ""] != _name) then {
                _o setVariable ["heat3d_name", _name];
                _o setVariable ["heat3d_jname", [_name] call _json];
            };
            private _entry = format ["[%1,%2,%3,%4,%5,%6,%7", _pos, round getDir _o, _alive, [0, 1] select (_vid >= 0),
                _o getVariable "heat3d_jname", [0, 1] select isPlayer _o, _o getVariable ["heat3d_role", '""']];
            // A living unit's group and side, which change when a player switches; the dead have neither.
            if (_alive > 0) then {
                private _g = group _o;
                if (_g getVariable ["heat3d_gname", ""] != groupId _g) then {
                    _g setVariable ["heat3d_gname", groupId _g];
                    _g setVariable ["heat3d_jgroup", [groupId _g] call _json];
                };
                _entry = _entry + format [',%1,"%2"', _g getVariable "heat3d_jgroup", side _g];
            };
            heat3d_buffer pushBack format ["P%1%2%1%3]", _tab, _id, _entry];
        } else {
            private _crew = (crew _o) apply { [_x] call heat3d_fnc_entity };
            heat3d_buffer pushBack format ["P%1%2%1[%3,%4,%5,%6]", _tab, _id, _pos, round getDir _o, _alive, _crew];
        };
    } forEach heat3d_tracked;

    [] call heat3d_fnc_flush;
    heat3d_frame = _f + 1;
    sleep ((heat3d_delay - (diag_tickTime - _t0)) max 0.01);
};
