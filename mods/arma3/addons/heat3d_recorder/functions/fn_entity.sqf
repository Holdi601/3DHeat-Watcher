/*
 * heat3d_fnc_entity: the recording's id of a unit or vehicle, giving it one
 * the first time it is seen.
 *
 * What it is gets written with its first sample (heat3d_fnc_loop), so its
 * start frame is the frame of that sample: an object met in the middle of a
 * frame (a killer, a vehicle found through its crew) starts in the next one.
 * The id is kept on the object with a local setVariable: nothing is sent to
 * the clients.
 */
params ["_obj"];
private _id = _obj getVariable ["heat3d_id", -1];
if (_id >= 0 || {isNull _obj}) exitWith { _id };
_id = heat3d_nextId;
heat3d_nextId = heat3d_nextId + 1;
_obj setVariable ["heat3d_id", _id];
heat3d_tracked pushBack _obj;

private _json = heat3d_fnc_json;
private _line = if (_obj isKindOf "CAManBase") then {
    private _role = roleDescription _obj;
    if (_role == "") then { _role = getText (configOf _obj >> "displayName") };
    _obj setVariable ["heat3d_role", [_role] call _json];
    format [
        '{"id":%1,"type":"unit","name":%2,"side":"%3","group":%4,"role":%5,"isPlayer":%6,"class":%7',
        _id, [name _obj] call _json, side group _obj, [groupId group _obj] call _json, _obj getVariable "heat3d_role",
        [0, 1] select isPlayer _obj, [typeOf _obj] call _json
    ]
} else {
    // OCAP's vehicle classes, which the viewer turns into Car, Tank, Helicopter...
    private _class = switch (true) do {
        case (_obj isKindOf "ParachuteBase"): { "parachute" };
        case (_obj isKindOf "Helicopter"): { "heli" };
        case (_obj isKindOf "Plane"): { "plane" };
        case (_obj isKindOf "Ship"): { "sea" };
        case (_obj isKindOf "StaticMortar"): { "static-mortar" };
        case (_obj isKindOf "StaticWeapon"): { "static-weapon" };
        case (_obj isKindOf "Wheeled_APC_F"): { "apc" };
        case ({ _obj isKindOf _x } count ["APC_Tracked_01_base_F", "APC_Tracked_02_base_F", "APC_Tracked_03_base_F"] > 0): { "apc" };
        case (_obj isKindOf "Tank"): { "tank" };
        case (_obj isKindOf "Truck_F"): { "truck" };
        case (_obj isKindOf "Car"): { "car" };
        default { "unknown" };
    };
    format [
        '{"id":%1,"type":"vehicle","name":%2,"class":"%3","vehicleClass":%4',
        _id, [getText (configOf _obj >> "displayName")] call _json, _class, [typeOf _obj] call _json
    ]
};
// Without its closing brace: the loop adds the start frame.
_obj setVariable ["heat3d_def", _line];

if (_obj isKindOf "CAManBase") then {
    if (heat3d_recordShots) then {
        // Untested on remote (player) units: whether FiredMan added on the
        // server fires there for shots of a unit local to a client.
        _obj addEventHandler ["FiredMan", {
            params ["_unit"];
            if (!heat3d_recording) exitWith {};
            private _p = getPosASL _unit;
            heat3d_buffer pushBack format ["F%1%2%1[%3,[%4,%5,%6]]", heat3d_tab, _unit getVariable ["heat3d_id", -1], heat3d_frame, _p#0 toFixed 1, _p#1 toFixed 1, _p#2 toFixed 1];
        }];
    };
    if (heat3d_recordHits) then {
        // MPHit fires on every machine, so the engine sends this handler to the
        // clients too; there it stops at the first check.
        _obj addMPEventHandler ["MPHit", {
            params ["_unit", "_causedBy", "_damage", "_instigator"];
            if (!isServer || {!(missionNamespace getVariable ["heat3d_recording", false])}) exitWith {};
            [_unit, [_instigator, _causedBy] select (isNull _instigator), "hit"] call heat3d_fnc_event;
        }];
    };
};
_id
