// 3DHeat recorder: hits on characters, for the "hit" events.
// UNTESTED AND NOT COMPILED (see Heat3D_Recorder.c and README.md).
//
// The game mode has no hit event, so the character damage manager is modded
// instead. OnDamage is where the engine reports damage that was applied; the
// recorder only exists on the authority, so on clients this is one null check.

modded class SCR_CharacterDamageManagerComponent
{
	//------------------------------------------------------------------------------------------------
	protected override void OnDamage(notnull BaseDamageContext damageContext)
	{
		super.OnDamage(damageContext);

		Heat3D_Recorder recorder = Heat3D_Recorder.Get();
		if (recorder)
			recorder.OnCharacterHit(GetOwner(), damageContext);
	}
}
