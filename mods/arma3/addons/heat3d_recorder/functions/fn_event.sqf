/*
 * heat3d_fnc_event: a kill or a hit, in OCAP's layout:
 *   [frame, "killed" | "hit", victim id, [killer id, weapon] or ["null"], metres]
 * The weapon is the killer's weapon in hand, or the vehicle they were in.
 */
params ["_victim", "_by", "_kind"];
if (isNull _victim) exitWith {};
private _vid = [_victim] call heat3d_fnc_entity;
private _cause = '["null"]';
private _distance = -1;
if (!isNull _by && {_by != _victim}) then {
    private _bid = [_by] call heat3d_fnc_entity;
    private _weapon = switch (true) do {
        case (!(_by isKindOf "CAManBase")): { getText (configOf _by >> "displayName") };
        case (!isNull objectParent _by): { getText (configOf objectParent _by >> "displayName") };
        default { getText (configFile >> "CfgWeapons" >> currentWeapon _by >> "displayName") };
    };
    _cause = format ["[%1,%2]", _bid, [_weapon] call heat3d_fnc_json];
    _distance = round (_victim distance _by);
};
heat3d_buffer pushBack format ['V%1[%2,"%3",%4,%5,%6]', heat3d_tab, heat3d_frame, _kind, _vid, _cause, _distance];
