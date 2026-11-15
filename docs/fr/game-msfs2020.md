---
title: "Microsoft Flight Simulator 2020 (données en direct)"
nav_order: 31
lang: "fr"
source: game-msfs2020.md
source_hash: "9b9e8389114b"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2020 (données en direct) {#microsoft-flight-simulator-2020-live-data}

Pendant que vous jouez à Microsoft Flight Simulator 2020, le Watcher enregistre les données que le simulateur envoie lui-même, afin que vous puissiez les regarder plus tard sur une carte dans la visionneuse 3DHeat.

*Détails techniques : adaptateur `msfs2020`, type [`telemetry`](sources-and-rules.md) ; il tourne pendant que `FlightSimulator.exe` est lancé et cherche de nouvelles données toutes les 0,1 s.*

## Ce qui est enregistré {#what-is-recorded}

- la position de votre avion à chaque image du simulateur, prise à 10 Hz (latitude/longitude/altitude en mètres est/haut/nord depuis le premier relevé ; lat/lon/alt gardées en colonnes)
- assiette, vitesse indiquée, vitesse sol, hauteur sol, g, au sol ; vitesse vraie, Mach, vitesse verticale, incidence, dérapage, cap magnétique, vitesses et accélérations du corps et vitesses de rotation à environ 10 Hz
- poids, carburant, volets, train, aérofreins, frein de parking, pilote automatique, manette des gaz, régime, météo, vitesse de simulation, heure et état de la caméra une fois par seconde ; le titre de l'avion et son type, modèle et identifiant ATC
- décollages, atterrissages, crashs, vols démarrés et arrêtés (session_start/session_end)
- temps de vol, temps en l'air, distance, altitude maximale, g maximal, atterrissages
- chaque message SimConnect gardé en entier dans heat.raw.parquet

## D'où viennent les données {#where-it-comes-from}

SimConnect par le SimConnect.dll propre au joueur (le dossier du simulateur, ou %MSFS_SDK%\SimConnect SDK\lib)

## Comment l'activer {#how-to-switch-it-on}

rien ; SimConnect.dll est fourni avec MSFS 2020 (ou le SDK de MSFS)

## Fonctionnement {#how-it-works}

Microsoft Flight Simulator 2020 et 2024 : SimConnect, par le SimConnect.dll propre au joueur.

SimConnect est l'API cliente publiée du simulateur (documentation du SDK : <https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>, <https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>). Le Watcher ne livre pas la DLL : il charge celle qui est venue avec le simulateur ou son SDK - MSFS 2020 place `SimConnect.dll` dans son dossier d'installation ; MSFS 2024 sur Steam ne livre que sa version interne, donc les joueurs de 2024 installent le SDK de MSFS 2024 (`<SDK>\SimConnect SDK\lib\SimConnect.dll` ; le simulateur 2024 accepte aussi les clients 2020).

Les appels, tirés de SimConnect.h, renvoient tous un HRESULT (0 = S_OK) :

```text
SimConnect_Open(HANDLE*, LPCSTR name, HWND, DWORD, HANDLE, DWORD config)
SimConnect_AddToDataDefinition(HANDLE, DWORD define, LPCSTR var, LPCSTR units,
                               SIMCONNECT_DATATYPE (FLOAT64 = 4), float epsilon, DWORD datum)
SimConnect_RequestDataOnSimObject(HANDLE, DWORD request, DWORD define, DWORD object (0 = user),
                                  SIMCONNECT_PERIOD (SIM_FRAME = 3), DWORD flags, DWORD origin,
                                  DWORD interval, DWORD limit)
SimConnect_SubscribeToSystemEvent(HANDLE, DWORD event, LPCSTR name)
SimConnect_GetNextDispatch(HANDLE, SIMCONNECT_RECV**, DWORD*)   E_FAIL when nothing waits
SimConnect_Close(HANDLE)
```

Chaque message commence par SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID} (#pragma pack 1). Ceux lus ici :

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Variables de simulation (unités demandées pour qu'aucune conversion ne soit nécessaire) : PLANE LATITUDE/LONGITUDE (degrés), PLANE ALTITUDE (mètres, au-dessus du niveau de la mer), PLANE ALT ABOVE GROUND (mètres), PLANE PITCH/BANK DEGREES et PLANE HEADING DEGREES TRUE (degrés ; les signes propres à SimConnect - nez haut = tangage négatif), AIRSPEED INDICATED et GROUND VELOCITY (nœuds), G FORCE (gforce), SIM ON GROUND (booléen). Événements système : SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded, Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Trois autres définitions de données demandent le reste du vol (`MOTION_VARS`, toutes les six images du simulateur), l'état plus lent de l'avion (`STATE_VARS`, une fois par seconde) et ses noms (`NAME_VARS`, chaînes de 256 octets, quand elles changent) ; chacune est sa propre définition, donc une variable qu'une version du simulateur ne connaît pas ne coûte que son bloc. Chaque message est gardé en entier dans le fichier brut annexe de la session.

Les positions vont dans la même carte plate que celle de X-Plane (x est, y altitude, z nord en mètres depuis le premier relevé de la séance) ; ce relevé est le `geo` de la session, dans meta.json et dans le pied de la table.

Le même module sert aussi : [Microsoft Flight Simulator 2024 (données en direct)](game-msfs2024.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `y` |
| Unités | mètres (est, altitude, nord depuis le premier relevé) |
| Miroir pour la visionneuse | `z` |
| Échelle (`scale` : la visionneuse multiplie les positions par elle) | 1 |

Ces valeurs vont dans le `meta.json` de chaque session (`axes`) et, quand la session a des positions, dans le pied de `heat.parquet`, afin que la visionneuse 3DHeat tourne et mette à l'échelle les lignes toute seule - voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` l'affiche comme « autorisé (lit seulement ce que le jeu publie) ».
- Type `telemetry` : il ne lit que ce que le jeu ou la plateforme fournit (un port UDP ou une mémoire partagée que le jeu publie), donc il enregistre aussi en ligne ; l'indicateur ne décide que de la possibilité de lire la mémoire.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne - voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json`, et la table `stats` de `watcher.sqlite`) :

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Exhaustivité {#completeness}

Le Watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou gardé, jamais jeté. En plus des lignes, chaque paquet, page, ligne ou réponse que reçoit l'adaptateur est gardé en entier dans `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ gardé par son nom ; `used` marque ce qui est aussi devenu des lignes), et `selfCheck.completeness` dans `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- SIMOBJECT_DATA de la définition de position (chaque image du simulateur) : latitude, longitude, altitude, hauteur sol, tangage, inclinaison, cap vrai, IAS, vitesse sol, g, au sol - la dernière image de l'interrogation en ligne, chaque image pour les toucher des roues et les décollages
- SIMOBJECT_DATA de la définition de mouvement (environ 10 Hz : TAS, Mach, vitesse verticale, incidence, dérapage, cap magnétique, vitesse du corps, accélération et vitesse de rotation sur trois axes) et de la définition d'état (1 Hz : poids, carburant, volets, train, aérofreins, frein de parking, pilote automatique, moteurs, manette et régime, température extérieure, vent, pression au niveau de la mer, vitesse de simulation, heure zoulou et locale, état de la caméra) sur les lignes, telles que reçues en dernier
- SIMOBJECT_DATA de la définition des noms (titre, type ATC, modèle et identifiant) dans meta.json et `aircraft` des lignes ; OPEN (application et version) dans meta.json
- EVENT et EVENT_FILENAME : SimStart, SimStop, Crashed, FlightLoaded (le fichier de vol) et AircraftLoaded (le fichier de l'avion) comme vols, crashs et meta.json
- QUIT termine la session

**Gardé brut**

- chaque message que SimConnect remet au Watcher, en entier comme `payload`, sous son nom SIMCONNECT_RECV_ID : `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (une variable ou un événement que le simulateur n'a pas accepté, avec l'identifiant d'envoi et l'index), tout autre identifiant par son nom ou `RECV_<id>`
- ce que seul le fichier brut annexe contient : la position de chaque image du simulateur entre les lignes, les événements Pause, Sim, CrashReset, PositionChanged et FlightSaved, une définition coupée par le simulateur (une variable qu'il ne connaît pas : le bloc n'est alors pas lu par son nom) ; `requests` dans meta.json liste les variables et unités de chaque définition, dans l'ordre, pour que les charges utiles se lisent sans ce module

**Non disponible**

- les autres avions (trafic IA, autres joueurs en ligne) : SimConnect_RequestDataOnSimObjectType interrogerait chaque avion dans un rayon - plus de charge pour le simulateur, et les vols d'autres joueurs
- le bloc de mouvement à chaque image : il est demandé toutes les six images (environ 10 Hz, la cadence des lignes), ce qui garde le flux brut près d'un cinquième de sa taille ; le bloc de position reste à chaque image
- les milliers d'autres variables de simulation (radios, feux, jauges de chaque moteur, pannes) : une définition ne contient que ce qu'elle demande ; les listes demandent le vol, l'état de l'avion et l'heure de la simulation
- les observations météo, les installations (aéroports, VOR), les données client des modules complémentaires : des requêtes séparées, non faites

**Taille** : environ 30 à 55 Mo par heure avant zstd : le bloc de position à chaque image (environ 200 octets avec son cadre, 30 à 60 par seconde), le bloc de mouvement à environ 10 Hz (environ 240 octets), le bloc d'état une fois par seconde ; zstd réduit les doubles plusieurs fois

## Vérifié {#verified}

décodage des messages testé sur des tampons construits à partir des dispositions de SimConnect.h ; la connexion SimConnect en direct n'est pas testée

## Source {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
