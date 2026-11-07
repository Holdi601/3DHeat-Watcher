/*
 * heat3d_fnc_finish: the mission's end. Writes the end, then has the
 * extension turn the journal into the recording (OCAP's JSON layout).
 */
params [["_end", "", [""]]];
if (!heat3d_recording) exitWith {};
heat3d_recording = false;
heat3d_buffer pushBack format ['V%1[%2,"endMission",["",%3]]', heat3d_tab, heat3d_frame, [_end] call heat3d_fnc_json];
[] call heat3d_fnc_flush;
private _result = ("heat3d" callExtension ["close", []]) select 0;
diag_log format ["Heat3D recorder: %1", _result];
