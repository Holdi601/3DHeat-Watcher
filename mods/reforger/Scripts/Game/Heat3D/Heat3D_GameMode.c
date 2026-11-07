// 3DHeat recorder: starts recording when any scenario starts.
// UNTESTED AND NOT COMPILED (see Heat3D_Recorder.c and README.md).
//
// A modded class instead of a game mode component: a component would have to
// be added to every scenario's GameMode prefab, while "modded class" changes
// SCR_BaseGameMode itself, so Conflict, Game Master, Combat Ops and community
// scenarios built on it all record without editing a prefab. No prefab and no
// replicated data is added, so clients that load the mod see the same world.

modded class SCR_BaseGameMode
{
	//------------------------------------------------------------------------------------------------
	//! Engine event: the world is initialised, before the first tick.
	//! Runs on every machine; only the authority (the dedicated server, or the
	//! host / single player game) records, so clients do nothing.
	protected override void OnGameStart()
	{
		super.OnGameStart();

		if (IsMaster())
			Heat3D_Recorder.Start(this);
	}
}
