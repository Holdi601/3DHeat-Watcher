// 3DHeat recorder for Arma Reforger.
//
// UNTESTED AND NOT COMPILED. Written from the game's published script API
// (BohemiaInteractive/Arma-Reforger-Script-Diff, game version 1.9.0.37) without
// Workbench. Expect compile errors to fix on the first Workbench build; see
// README.md for what is still unverified.
//
// What it does: on the machine that owns the game mode (the dedicated server,
// or the host / single player), it samples every character and vehicle once a
// second and logs kills, hits, vehicle get in / get out, player connect /
// disconnect and the end of the mission. Everything goes into one JSON Lines
// file per session under $profile:heat3d/. Players install nothing by hand:
// the server's mod list makes their game download it, and the code does
// nothing on their machines.
//
// Coordinates are written as the engine gives them: Enfusion is Y-up, x east,
// y height above sea level, z north. dir is a compass bearing in degrees
// (0 north, 90 east). 3DHeat's importer maps this to OCAP2's [x, y(north), z].

class Heat3D_Recorder : Managed
{
	// Seconds between samples. OCAP2 records at 1 s by default.
	static const int CAPTURE_DELAY_MS = 1000;
	// Pending lines are appended to the file every this many frames, so a
	// crash loses at most this much, and the server never holds a whole
	// session in memory. FileHandle has no flush, hence open-append-close.
	static const int FLUSH_EVERY_FRAMES = 10;
	// How often the whole world is searched for characters and vehicles that
	// neither the player list nor the AI list reports (parked vehicles, AI out
	// of simulation). Cost on a full map is unmeasured: tune after a test.
	static const int SWEEP_EVERY_FRAMES = 30;

	protected static ref Heat3D_Recorder s_Instance;

	protected SCR_BaseGameMode m_GameMode;
	protected string m_sPath;
	protected bool m_bFileStarted;
	protected ref array<string> m_aPending = {};
	protected int m_iFrame;
	protected int m_iNextId;

	// Tracked entities with our ids, in parallel arrays. Entity references are
	// weak, so a deleted entity turns into null and is dropped on the next tick.
	protected ref array<IEntity> m_aUnits = {};
	protected ref array<int> m_aUnitIds = {};
	protected ref array<IEntity> m_aVehicles = {};
	protected ref array<int> m_aVehicleIds = {};
	protected ref map<IEntity, int> m_mIds = new map<IEntity, int>();
	protected bool m_bIdsDirty;

	protected ref map<IEntity, int> m_mGroupIds = new map<IEntity, int>();
	protected int m_iNextGroupId;
	// Last vehicle per unit id, to log get in / get out when it changes.
	protected ref map<int, int> m_mLastVehicle = new map<int, int>();
	// Names per player id: the name can be gone when the disconnect arrives.
	protected ref map<int, string> m_mPlayerNames = new map<int, string>();
	// One hit per victim and shooter per frame is enough for a heat map;
	// the engine reports a hit for every hit zone a bullet touches.
	protected ref set<string> m_HitsThisFrame = new set<string>();

	//------------------------------------------------------------------------------------------------
	static Heat3D_Recorder Get()
	{
		return s_Instance;
	}

	//------------------------------------------------------------------------------------------------
	//! Called from the modded SCR_BaseGameMode.OnGameStart, on the authority only.
	static void Start(SCR_BaseGameMode gameMode)
	{
		if (s_Instance)
			s_Instance.Stop("restart");

		s_Instance = new Heat3D_Recorder();
		s_Instance.Begin(gameMode);
	}

	//------------------------------------------------------------------------------------------------
	protected void Begin(SCR_BaseGameMode gameMode)
	{
		m_GameMode = gameMode;

		string worldFile = GetGame().GetWorldFile();
		string world = FilePath.StripExtension(FilePath.StripPath(worldFile));

		int y, mo, d, h, mi, s;
		System.GetYearMonthDayUTC(y, mo, d);
		System.GetHourMinuteSecondUTC(h, mi, s);
		string date = y.ToString() + "-" + mo.ToString(2) + "-" + d.ToString(2);
		string time = h.ToString(2) + "-" + mi.ToString(2) + "-" + s.ToString(2);

		// $profile: is the server's -profile folder (see README for the exact place).
		FileIO.MakeDirectory("$profile:heat3d");
		m_sPath = "$profile:heat3d/" + date + "_" + time + "_" + world + ".jsonl";

		string header = "{\"type\":\"header\",\"format\":\"heat3d-reforger\",\"version\":1";
		header += ",\"world\":\"" + Esc(world) + "\"";
		header += ",\"worldFile\":\"" + Esc(worldFile) + "\"";
		// Mission name as the scenario header gives it (may be a "#AR-..." string key).
		string mission;
		SCR_MissionHeader missionHeader = SCR_MissionHeader.Cast(GetGame().GetMissionHeader());
		if (missionHeader)
			mission = missionHeader.m_sName;
		float captureDelay = CAPTURE_DELAY_MS / 1000.0;

		header += ",\"mission\":\"" + Esc(mission) + "\"";
		header += ",\"captureDelay\":" + captureDelay.ToString(-1, 2);
		header += ",\"startedUtc\":\"" + date + "T" + h.ToString(2) + ":" + mi.ToString(2) + ":" + s.ToString(2) + "Z\"";
		header += ",\"axes\":\"x east, y up, z north; dir compass degrees\"}";
		m_aPending.Insert(header);

		// The game mode's own events. Invokers are the documented extension
		// points and also fire for game modes derived from SCR_BaseGameMode.
		m_GameMode.GetOnPlayerRegistered().Insert(OnPlayerRegistered);
		m_GameMode.GetOnPlayerDisconnected().Insert(OnPlayerDisconnected);
		m_GameMode.GetOnControllableSpawned().Insert(OnControllableSpawned);
		m_GameMode.GetOnControllableDestroyed().Insert(OnControllableDestroyed);
		m_GameMode.GetOnGameModeEnd().Insert(OnGameModeEnd);
		m_GameMode.GetOnGameEnd().Insert(OnGameEnd);

		Sweep();
		GetGame().GetCallqueue().CallLater(Tick, CAPTURE_DELAY_MS, true);
		Print("[Heat3D] recording to " + m_sPath);
	}

	//------------------------------------------------------------------------------------------------
	void Stop(string reason)
	{
		GetGame().GetCallqueue().Remove(Tick);
		if (m_GameMode)
		{
			m_GameMode.GetOnPlayerRegistered().Remove(OnPlayerRegistered);
			m_GameMode.GetOnPlayerDisconnected().Remove(OnPlayerDisconnected);
			m_GameMode.GetOnControllableSpawned().Remove(OnControllableSpawned);
			m_GameMode.GetOnControllableDestroyed().Remove(OnControllableDestroyed);
			m_GameMode.GetOnGameModeEnd().Remove(OnGameModeEnd);
			m_GameMode.GetOnGameEnd().Remove(OnGameEnd);
		}

		m_aPending.Insert("{\"type\":\"end\",\"frame\":" + m_iFrame + ",\"reason\":\"" + Esc(reason) + "\"}");
		Flush();
		Print("[Heat3D] stopped (" + reason + "), " + m_iFrame + " frames in " + m_sPath);

		// Last statement on purpose: dropping the static ref may free this object.
		if (s_Instance == this)
			s_Instance = null;
	}

	//------------------------------------------------------------------------------------------------
	// Sampling
	//------------------------------------------------------------------------------------------------

	protected void Tick()
	{
		m_HitsThisFrame.Clear();
		DiscoverUnits();
		if (m_iFrame % SWEEP_EVERY_FRAMES == 0)
			Sweep();

		PlayerManager players = GetGame().GetPlayerManager();
		// Crew lists per vehicle id, filled from the units' side so no
		// compartment walking is needed.
		map<int, string> crew = new map<int, string>();

		string units = "";
		for (int i = m_aUnits.Count() - 1; i >= 0; i--)
		{
			IEntity e = m_aUnits[i];
			if (!e)
			{
				// Remove() moves the last element into slot i; going backwards that
				// element is already done, and both arrays move the same way.
				m_aUnits.Remove(i);
				m_aUnitIds.Remove(i);
				m_bIdsDirty = true;
				continue;
			}

			int id = m_aUnitIds[i];
			int vehicleId = -1;
			IEntity vehicle = CompartmentAccessComponent.GetVehicleIn(e);
			if (vehicle)
			{
				vehicleId = TrackVehicle(vehicle);
				string list;
				if (crew.Find(vehicleId, list))
					list += "," + id;
				else
					list = id.ToString();
				crew.Set(vehicleId, list);
			}

			// Find() fills the out value with 0 when the key is missing, and 0 is
			// a valid id, so the default has to be set after the lookup.
			int lastVehicle;
			if (!m_mLastVehicle.Find(id, lastVehicle))
				lastVehicle = -1;
			if (lastVehicle != vehicleId)
			{
				if (lastVehicle >= 0)
					AddEvent("\"getout\"," + id + "," + lastVehicle);
				if (vehicleId >= 0)
					AddEvent("\"getin\"," + id + "," + vehicleId);
				m_mLastVehicle.Set(id, vehicleId);
			}

			int playerId = players.GetPlayerIdFromControlledEntity(e);
			if (units != "")
				units += ",";
			units += "[" + id + "," + Pos(e) + "," + Heading(e) + "," + UnitAlive(e) + "," + vehicleId + "," + playerId + "]";
		}

		// Enforce Script does not allow the same local name twice in one
		// function, even in separate loops, hence j / vid / crewList.
		string vehicles = "";
		for (int j = m_aVehicles.Count() - 1; j >= 0; j--)
		{
			IEntity v = m_aVehicles[j];
			if (!v)
			{
				m_aVehicles.Remove(j);
				m_aVehicleIds.Remove(j);
				m_bIdsDirty = true;
				continue;
			}

			int vid = m_aVehicleIds[j];
			string crewList;
			crew.Find(vid, crewList);
			if (vehicles != "")
				vehicles += ",";
			vehicles += "[" + vid + "," + Pos(v) + "," + Heading(v) + "," + VehicleAlive(v) + ",[" + crewList + "]]";
		}

		float ms = GetGame().GetWorld().GetWorldTime();
		m_aPending.Insert("{\"type\":\"frame\",\"frame\":" + m_iFrame + ",\"ms\":" + ms.ToString(-1, 0) + ",\"units\":[" + units + "],\"vehicles\":[" + vehicles + "]}");

		if (m_bIdsDirty)
			RebuildIds();

		m_iFrame++;
		if (m_iFrame % FLUSH_EVERY_FRAMES == 0)
			Flush();
	}

	//------------------------------------------------------------------------------------------------
	//! Players and AI, every tick: cheap lists the game keeps anyway.
	protected void DiscoverUnits()
	{
		array<int> playerIds = {};
		PlayerManager players = GetGame().GetPlayerManager();
		players.GetPlayers(playerIds);
		foreach (int playerId : playerIds)
		{
			IEntity e = players.GetPlayerControlledEntity(playerId);
			if (ChimeraCharacter.Cast(e))
				TrackUnit(e);
		}

		AIWorld aiWorld = GetGame().GetAIWorld();
		if (!aiWorld)
			return;

		array<AIAgent> agents = {};
		aiWorld.GetAIAgents(agents);
		foreach (AIAgent agent : agents)
		{
			// Groups are agents too; only their members control characters.
			IEntity controlled = agent.GetControlledEntity();
			if (ChimeraCharacter.Cast(controlled))
				TrackUnit(controlled);
		}
	}

	//------------------------------------------------------------------------------------------------
	//! Whole-world search for anything the lists above miss.
	protected void Sweep()
	{
		BaseWorld world = GetGame().GetWorld();
		vector mins, maxs;
		world.GetBoundBox(mins, maxs);
		world.QueryEntitiesByAABB(mins, maxs, SweepAdd, SweepFilter, EQueryEntitiesFlags.DYNAMIC);
	}

	protected bool SweepFilter(IEntity e)
	{
		return ChimeraCharacter.Cast(e) != null || Vehicle.Cast(e) != null;
	}

	protected bool SweepAdd(IEntity e)
	{
		if (ChimeraCharacter.Cast(e))
			TrackUnit(e);
		else if (Vehicle.Cast(e))
			TrackVehicle(e);
		return true; // keep searching
	}

	//------------------------------------------------------------------------------------------------
	// Entity registry
	//------------------------------------------------------------------------------------------------

	//! Our id for a character, registering it (one "entity" line) on first sight.
	protected int TrackUnit(IEntity e)
	{
		int id;
		if (m_mIds.Find(e, id))
			return id;

		id = m_iNextId++;
		m_mIds.Set(e, id);
		m_aUnits.Insert(e);
		m_aUnitIds.Insert(id);

		int playerId = GetGame().GetPlayerManager().GetPlayerIdFromControlledEntity(e);
		string name = PrefabBase(e);
		if (playerId > 0)
			name = GetGame().GetPlayerManager().GetPlayerName(playerId);

		string faction;
		int group = -1;
		SCR_ChimeraCharacter ch = SCR_ChimeraCharacter.Cast(e);
		if (ch)
		{
			faction = ch.GetFactionKey();
			SCR_AIGroup g = ch.GetCharacterGroup();
			if (g)
				group = GroupId(g);
		}

		string line = "{\"type\":\"entity\",\"id\":" + id + ",\"kind\":\"unit\",\"frame\":" + m_iFrame;
		line += ",\"name\":\"" + Esc(name) + "\",\"playerId\":" + playerId;
		line += ",\"faction\":\"" + Esc(faction) + "\",\"group\":" + group;
		line += ",\"prefab\":\"" + Esc(PrefabBase(e)) + "\"}";
		m_aPending.Insert(line);
		return id;
	}

	//------------------------------------------------------------------------------------------------
	//! Our id for a vehicle (or a static weapon: anything a character sits in).
	protected int TrackVehicle(IEntity e)
	{
		int id;
		if (m_mIds.Find(e, id))
			return id;

		id = m_iNextId++;
		m_mIds.Set(e, id);
		m_aVehicles.Insert(e);
		m_aVehicleIds.Insert(id);

		string faction;
		Vehicle v = Vehicle.Cast(e);
		if (v)
		{
			Faction f = v.GetFaction();
			if (f)
				faction = f.GetFactionKey();
		}

		string line = "{\"type\":\"entity\",\"id\":" + id + ",\"kind\":\"vehicle\",\"frame\":" + m_iFrame;
		line += ",\"name\":\"" + Esc(PrefabBase(e)) + "\",\"class\":\"" + VehicleClass(e) + "\"";
		line += ",\"faction\":\"" + Esc(faction) + "\",\"prefab\":\"" + Esc(PrefabBase(e)) + "\"}";
		m_aPending.Insert(line);
		return id;
	}

	//------------------------------------------------------------------------------------------------
	//! Id for anything an event names: a tracked unit or vehicle, else registers it.
	protected int IdOf(IEntity e)
	{
		if (!e)
			return -1;
		int id;
		if (m_mIds.Find(e, id))
			return id;
		if (ChimeraCharacter.Cast(e))
			return TrackUnit(e);
		if (Vehicle.Cast(e))
			return TrackVehicle(e);
		return -1;
	}

	protected int GroupId(IEntity group)
	{
		int id;
		if (!m_mGroupIds.Find(group, id))
		{
			id = m_iNextGroupId++;
			m_mGroupIds.Set(group, id);
		}
		return id;
	}

	protected void RebuildIds()
	{
		m_mIds.Clear();
		foreach (int i, IEntity unit : m_aUnits)
			m_mIds.Set(unit, m_aUnitIds[i]);
		foreach (int j, IEntity vehicle : m_aVehicles)
			m_mIds.Set(vehicle, m_aVehicleIds[j]);
		m_bIdsDirty = false;
	}

	//------------------------------------------------------------------------------------------------
	// Events. Each line carries an OCAP2-shaped event array, so the importer
	// can pass most of them through unchanged.
	//------------------------------------------------------------------------------------------------

	protected void AddEvent(string body)
	{
		m_aPending.Insert("{\"type\":\"event\",\"event\":[" + m_iFrame + "," + body + "]}");
	}

	protected void OnPlayerRegistered(int playerId)
	{
		// Registered, not connected: the docs say the name is known from here.
		string name = GetGame().GetPlayerManager().GetPlayerName(playerId);
		m_mPlayerNames.Set(playerId, name);
		AddEvent("\"connected\",\"" + Esc(name) + "\"," + playerId);
	}

	protected void OnPlayerDisconnected(int playerId, KickCauseCode cause, int timeout)
	{
		string name;
		if (!m_mPlayerNames.Find(playerId, name))
			name = GetGame().GetPlayerManager().GetPlayerName(playerId);
		AddEvent("\"disconnected\",\"" + Esc(name) + "\"," + playerId);
	}

	protected void OnControllableSpawned(IEntity entity)
	{
		IdOf(entity);
	}

	//! Raised for any controllable entity (players, AI, possibly vehicles).
	protected void OnControllableDestroyed(notnull SCR_InstigatorContextData data)
	{
		IEntity victim = data.GetVictimEntity();
		IEntity killer = data.GetKillerEntity();
		if (!killer && data.GetInstigator())
			killer = data.GetInstigator().GetInstigatorEntity();

		int victimId = IdOf(victim);
		if (victimId < 0)
			return;

		float distance = -1;
		if (victim && killer)
			distance = vector.Distance(victim.GetOrigin(), killer.GetOrigin());

		AddEvent("\"killed\"," + victimId + ",[" + IdOf(killer) + ",\"" + Esc(WeaponOf(killer)) + "\"]," + distance.ToString(-1, 1));
	}

	//! From the modded SCR_CharacterDamageManagerComponent.OnDamage.
	void OnCharacterHit(IEntity victim, notnull BaseDamageContext context)
	{
		if (context.damageValue <= 0)
			return;
		// Bleeding, healing and regeneration are not hits.
		EDamageType type = context.damageType;
		if (type == EDamageType.BLEEDING || type == EDamageType.HEALING || type == EDamageType.REGENERATION)
			return;

		IEntity shooter;
		if (context.instigator)
			shooter = context.instigator.GetInstigatorEntity();

		int victimId = IdOf(victim);
		int shooterId = IdOf(shooter);
		string key = victimId.ToString() + ":" + shooterId;
		if (victimId < 0 || m_HitsThisFrame.Contains(key))
			return;
		m_HitsThisFrame.Insert(key);

		float distance = -1;
		if (shooter)
			distance = vector.Distance(victim.GetOrigin(), shooter.GetOrigin());

		AddEvent("\"hit\"," + victimId + ",[" + shooterId + ",\"" + Esc(WeaponOf(shooter)) + "\"]," + distance.ToString(-1, 1));
	}

	protected void OnGameModeEnd(SCR_GameModeEndData endData)
	{
		string winner;
		string reason;
		if (endData)
		{
			reason = typename.EnumToString(EGameOverTypes, endData.GetEndReason());
			FactionManager factions = GetGame().GetFactionManager();
			int winnerFaction = endData.GetWinnerFactionId();
			if (factions && winnerFaction >= 0)
			{
				Faction f = factions.GetFactionByIndex(winnerFaction);
				if (f)
					winner = f.GetFactionKey();
			}
		}
		// OCAP2 shape: [frame, "endMission", [side, message]]; side is the
		// faction key here and gets mapped by the importer.
		AddEvent("\"endMission\",[\"" + Esc(winner) + "\",\"" + Esc(reason) + "\"]");
		Flush();
	}

	//! The world is being torn down (session end, restart, shutdown).
	protected void OnGameEnd()
	{
		Stop("game end");
	}

	//------------------------------------------------------------------------------------------------
	// Values
	//------------------------------------------------------------------------------------------------

	protected static string Pos(IEntity e)
	{
		vector p = e.GetOrigin();
		return p[0].ToString(-1, 2) + "," + p[1].ToString(-1, 2) + "," + p[2].ToString(-1, 2);
	}

	//! Compass bearing of the entity's forward (+Z) axis. vector.ToYaw measures
	//! in the XZ plane with +X = 90, so with z north this is 0 north, 90 east.
	protected static int Heading(IEntity e)
	{
		float yaw = e.GetWorldTransformAxis(2).ToYaw();
		if (yaw < 0)
			yaw += 360;
		int dir = Math.Round(yaw);
		return dir % 360;
	}

	//! OCAP2 life state: 0 dead, 1 alive, 2 unconscious.
	protected static int UnitAlive(IEntity e)
	{
		ChimeraCharacter ch = ChimeraCharacter.Cast(e);
		if (!ch || !ch.GetCharacterController())
			return 1;
		ECharacterLifeState state = ch.GetCharacterController().GetLifeState();
		if (state == ECharacterLifeState.DEAD)
			return 0;
		if (state == ECharacterLifeState.INCAPACITATED)
			return 2;
		return 1;
	}

	protected static int VehicleAlive(IEntity e)
	{
		BaseVehicle v = BaseVehicle.Cast(e);
		if (v && v.GetDamageManager() && v.GetDamageManager().IsDestroyed())
			return 0;
		return 1;
	}

	//! Coarse OCAP2 vehicle class from the controller the vehicle carries.
	protected static string VehicleClass(IEntity e)
	{
		if (!Vehicle.Cast(e))
			return "static-weapon";
		if (e.FindComponent(HelicopterControllerComponent))
			return "heli";
		if (e.FindComponent(CarControllerComponent))
			return "car";
		return "vehicle";
	}

	//! What the killer / shooter used: the vehicle they sit in, else the weapon
	//! in their hands at the time of the event. Same approximation as the
	//! game's own statistics; a grenade thrown just before switching shows the
	//! rifle. Prefab base name, e.g. "Rifle_M16A2".
	protected static string WeaponOf(IEntity who)
	{
		if (!who)
			return "";
		IEntity vehicle = CompartmentAccessComponent.GetVehicleIn(who);
		if (vehicle)
			return PrefabBase(vehicle);
		ChimeraCharacter ch = ChimeraCharacter.Cast(who);
		if (!ch)
			return PrefabBase(who);
		CharacterControllerComponent ctrl = ch.GetCharacterController();
		if (!ctrl || !ctrl.GetWeaponManagerComponent())
			return "";
		BaseWeaponComponent weapon = ctrl.GetWeaponManagerComponent().GetCurrentWeapon();
		if (!weapon)
			return "";
		return PrefabBase(weapon.GetOwner());
	}

	//! "{GUID}Prefabs/Characters/.../Character_US_Rifleman.et" -> "Character_US_Rifleman".
	protected static string PrefabBase(IEntity e)
	{
		if (!e)
			return "";
		EntityPrefabData data = e.GetPrefabData();
		if (!data)
			return e.ClassName();
		string path = data.GetPrefabName();
		return FilePath.StripExtension(FilePath.StripPath(path));
	}

	protected static string Esc(string s)
	{
		s.Replace("\\", "\\\\");
		s.Replace("\"", "\\\"");
		return s;
	}

	//------------------------------------------------------------------------------------------------
	//! Append pending lines. First write creates the file.
	protected void Flush()
	{
		if (m_aPending.IsEmpty())
			return;

		FileMode mode = FileMode.APPEND;
		if (!m_bFileStarted)
			mode = FileMode.WRITE;

		FileHandle file = FileIO.OpenFile(m_sPath, mode);
		if (!file)
		{
			Print("[Heat3D] cannot open " + m_sPath, LogLevel.ERROR);
			return; // keep the lines and try again next flush
		}

		foreach (string line : m_aPending)
			file.WriteLine(line);
		file.Close();

		m_bFileStarted = true;
		m_aPending.Clear();
	}
}
