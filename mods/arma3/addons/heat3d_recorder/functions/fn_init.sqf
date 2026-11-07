/*
 * heat3d_fnc_init (postInit): starts the recorder when a mission starts.
 *
 * Runs on the server only. The addon is loaded with -serverMod, so no client
 * has it; the isServer check keeps it quiet in a single-player editor preview
 * that is not hosting.
 */
if (!isServer) exitWith {};

heat3d_tab = toString [9];
heat3d_recording = false;
heat3d_frame = 0;
heat3d_nextId = 0;
heat3d_tracked = [];
heat3d_buffer = [];

// Players coming and going, where they are (placed by the viewer at their unit).
addMissionEventHandler ["PlayerConnected", {
    params ["_id", "_uid", "_name"];
    if (!heat3d_recording || {_name == "__SERVER__"}) exitWith {};
    heat3d_buffer pushBack format ['V%1[%2,"connected",%3]', heat3d_tab, heat3d_frame, [_name] call heat3d_fnc_json];
}];
addMissionEventHandler ["PlayerDisconnected", {
    params ["_id", "_uid", "_name"];
    if (!heat3d_recording || {_name == "__SERVER__"}) exitWith {};
    heat3d_buffer pushBack format ['V%1[%2,"disconnected",%3]', heat3d_tab, heat3d_frame, [_name] call heat3d_fnc_json];
}];

// Kills of anything: units and vehicles, on whatever machine they were local.
addMissionEventHandler ["EntityKilled", {
    params ["_victim", "_killer", "_instigator"];
    if (!heat3d_recording) exitWith {};
    // A drone's kill belongs to whoever flies it.
    if (isNull _instigator) then { _instigator = (UAVControl vehicle _killer) param [0, objNull] };
    if (isNull _instigator) then { _instigator = _killer };
    [_victim, _instigator, "killed"] call heat3d_fnc_event;
}];

// The mission's end; a server shut down or a mission changed without one
// leaves the journal behind, and the extension finishes it at the next start.
addMissionEventHandler ["Ended", { params ["_end"]; [_end] call heat3d_fnc_finish }];
addMissionEventHandler ["MPEnded", { [""] call heat3d_fnc_finish }];

[] spawn {
    // Settings once the mission runs, so that its init.sqf can still set
    // heat3d_captureDelay, heat3d_recordHits, heat3d_recordShots or heat3d_minPlayers.
    waitUntil { sleep 1; time > 0 };
    private _setting = {
        params ["_name", "_default"];
        missionNamespace getVariable [
            "heat3d_" + _name,
            [_default, getNumber (configFile >> "Heat3D" >> _name)] select isNumber (configFile >> "Heat3D" >> _name)
        ]
    };
    heat3d_delay = (["captureDelay", 1] call _setting) max 0.1;
    heat3d_recordHits = (["recordHits", 1] call _setting) > 0;
    heat3d_recordShots = (["recordShots", 1] call _setting) > 0;
    heat3d_minPlayers = ["minPlayers", 0] call _setting;
    // Players, when the server wants some before it records.
    waitUntil { sleep 1; count (allPlayers - entities "HeadlessClient_F") >= heat3d_minPlayers };
    private _json = heat3d_fnc_json;
    private _version = "heat3d" callExtension "version";
    private _result = ("heat3d" callExtension ["open", [missionName]]) select 0;
    if (_result == "" || {_result find "error" == 0}) exitWith {
        diag_log format ["Heat3D recorder: not recording, the heat3d extension answered '%1' (is heat3d_x64.dll/.so in the mod folder?)", _result];
    };
    diag_log format ["Heat3D recorder %1: recording %2 every %3 s", _version, _result, heat3d_delay];
    heat3d_recording = true;
    private _name = [briefingName, missionName] select (briefingName == "");
    heat3d_buffer pushBack format [
        'H%1{"missionName":%2,"worldName":%3,"missionAuthor":%4,"captureDelay":%5,"addonVersion":"heat3d","extensionVersion":%6,"tags":""}',
        heat3d_tab, [_name] call _json, [worldName] call _json, [getMissionConfigValue ["author", ""]] call _json, heat3d_delay, [_version] call _json
    ];
    heat3d_buffer pushBack format ['V%1[0,"generalEvent","Recording started."]', heat3d_tab];
    [] call heat3d_fnc_loop;
};
