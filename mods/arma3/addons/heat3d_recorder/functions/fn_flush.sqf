/*
 * heat3d_fnc_flush: hands the waiting lines to the extension, a few kB per
 * call (how much one callExtension argument may hold is not documented, so
 * this stays well under the 10 kB older servers were said to allow).
 */
private _lines = heat3d_buffer;
heat3d_buffer = [];
private _chunk = [];
private _size = 0;
private _nl = toString [10];
{
    if (_size + count _x > 8000 && {_size > 0}) then {
        "heat3d" callExtension ["write", [_chunk joinString _nl]];
        _chunk = [];
        _size = 0;
    };
    _chunk pushBack _x;
    _size = _size + count _x + 1;
} forEach _lines;
if (_size > 0) then { "heat3d" callExtension ["write", [_chunk joinString _nl]] };
