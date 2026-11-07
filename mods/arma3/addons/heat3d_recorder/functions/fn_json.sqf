/*
 * heat3d_fnc_json: a string as a JSON string, quotes included.
 *
 * SQF's own `str` doubles quotes instead of escaping them, which is not JSON,
 * so quotes and backslashes are escaped here and control characters dropped.
 */
params [["_s", "", [""]]];
if (_s find """" < 0 && {_s find "\" < 0} && {count (toArray _s select {_x < 32}) == 0}) exitWith { """" + _s + """" };
private _out = [];
{
    if (_x == 34 || {_x == 92}) then { _out pushBack 92; _out pushBack _x } else { if (_x >= 32) then { _out pushBack _x } };
} forEach toArray _s;
"""" + toString _out + """"
