---
title: "DCS World (données en direct)"
nav_order: 10
lang: fr
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (données en direct) {#dcs-world-live-data}

Pendant que vous jouez à DCS World, le Watcher enregistre les données que le jeu envoie lui-même, afin que vous puissiez les regarder plus tard sur une carte dans la visionneuse 3DHeat.

*Détails techniques : adaptateur `dcs`, type [`telemetry`](sources-and-rules.md) ; il tourne pendant que `DCS.exe` est lancé et cherche de nouvelles données toutes les 0,1 s.*

## Ce qui est enregistré {#what-is-recorded}

- votre propre position à 10 Hz, en mètres est/haut/nord depuis l'origine du théâtre (à partir de la latitude, de la longitude et de l'altitude) ; lat/lon/alt et les mètres du monde de DCS (dcs_x nord, dcs_y haut, dcs_z est) en colonnes
- assiette, vitesse indiquée et vitesse vraie, Mach, vitesse verticale, incidence et dérapage, cap magnétique, hauteur sol et radar, accélérations sur trois axes, vitesse et vitesses de rotation, en vol, position et direction de la caméra, type d'appareil
- décollages et atterrissages avec le terrain ; crashs, éjections, morts de pilote
- abattages et être abattu, avec les deux types d'unités et l'arme ; les autres événements du jeu tels qu'ils sont donnés
- durées de vie par mission (spawn ... session_end), frags, morts, distance, altitude maximale, g maximal
- chaque ligne envoyée par le hook gardée en entier dans heat.raw.parquet, avec un vidage chaque seconde des tables d'export de l'appareil (moteurs, train et volets, charge, contre-mesures, route, navigation) et chaque autre callback (pause, chat, joueurs qui arrivent, chargement de mission)

## D'où viennent les données {#where-it-comes-from}

le hook du Watcher %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, lignes UDP vers 127.0.0.1:41993

## Comment l'activer {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (ajoute Scripts\Hooks\heat3d-watch.lua), puis redémarrez DCS

Saisissez la commande dans un terminal ouvert dans le dossier du Watcher (voir [Avant de commencer](before-you-start.md)). Si la commande échoue, la dernière ligne indique pourquoi ; [Installation et lancement](installing-and-running.md) décrit les causes les plus fréquentes.

`python -m heat3d_watch setup dcs` liste les fichiers qu'il modifierait ; `python -m heat3d_watch setup dcs --apply` les modifie, en gardant l'original sous le nom `<file>.heat3d-backup` (voir [Commandes](commands.md#setup)). Il affiche `dcs: changed: ...` pour chaque modification, ou `dcs: nothing to change` si c'est déjà activé.

## Fonctionnement {#how-it-works}

DCS World : un petit script hook du Watcher, qui envoie des lignes UDP vers 127.0.0.1:41993.

DCS lance au démarrage les fichiers Lua de `Saved Games\DCS*\Scripts\Hooks\` ; un hook peut lire les fonctions d'export (`Export.Lo*`) et recevoir les callbacks de la simulation (`DCS.setUserCallbacks` : onSimulationStart/Frame/Stop, onGameEvent) - voir `<DCS>\API\DCS_ControlAPI.html` et <https://wiki.hoggitworld.com/view/DCS_Export_Script>. `setup` écrit `heat3d-watch.lua` là-bas (son propre fichier : Export.lua et les hooks d'autres outils ne sont pas touchés). Il envoie dix lignes par seconde, une de plus par seconde, et une par événement ou callback du jeu, sans jamais attendre de réponse. Le port est 41993 pour que le hook de JoyPro (41992) et Tacview (42674) continuent de fonctionner à côté. Les lignes (champs séparés par « ; ») :

```text
hello;v=2                                       the hook was loaded
start;mission=..;map=..;me=<player id>;name=..;mp=0|1;file=..;server=0|1
mis;t=..;date.Day=..;start_time=..;weather...   the mission's date, start time and weather, flattened
p;t=<model s>;x=;y=;z=;lat=;lon=;alt=;hdg=;pitch=;bank=;ias=;agl=;g=;type=;tas=;mach=;vv=;aoa=;aos=;
  mhdg=;ralt=;gx=;gz=;vx=;vy=;vz=;wx=;wy=;wz=;air=;cx=;cy=;cz=;cfx=;cfy=;cfz=
d;t=..;self.Name=..;eng.RPM.left=..;mech.gear.value=..;pay.Stations.1.count=..;...   once a second
ev;t=..;name=<onGameEvent name>;args=a|b|c      every onGameEvent
cb;t=..;name=<callback>;args=a|b                every other callback (pause, chat, players, loading)
noexport;t=..                                   the server forbids ownship export
stop;t=..                                       the mission ended
```

`p` est LoGetSelfData : Position x/y/z - les mètres du monde de DCS, x nord, y haut, z est - plus LatLongAlt (degrés, m), Heading/Pitch/Bank (radians), avec LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) et LoGetAccelerationUnits() x/y/z (g) ; et, comme `Scripts\Export.lua` les documente, LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s), LoGetAngleOfAttack et LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad), LoGetRadarAltimeter (m), LoGetVectorVelocity (m/s du monde), LoGetAngularVelocity (rad/s), LoGetInAir, et le point et le vecteur de direction de LoGetCameraPosition (mètres du monde). `d` est un vidage chaque seconde de tables entières, aplaties en clés pointées : LoGetSelfData (pays, coalition, noms d'unité et de groupe, niveaux de type, drapeaux), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus et quelques nombres (pause, accélération du temps, siège, pression, déviations). Le Watcher garde chaque ligne en entier dans le fichier brut annexe ; `p` devient aussi les lignes.

Les positions vont dans la même carte plate que celles des autres simulateurs de vol (`Tangent` : x est, y altitude au-dessus du niveau de la mer, z nord, en mètres) à partir de LatLongAlt, autour de l'origine fixe du théâtre (`THEATRES`, à partir du `map` de la ligne de départ), de sorte que chaque mission d'un même théâtre partage une seule carte, et sur laquelle la visionneuse peut poser le vrai monde. Un théâtre absent de la table prend la latitude et la longitude du premier relevé, arrondies au degré entier. Les x/y/z propres à DCS sont gardés en `dcs_x`, `dcs_y`, `dcs_z` ; un relevé sans LatLongAlt ne peut pas être placé et est seulement compté (`fixes_without_latlon`). L'origine est le `geo` de la session, dans meta.json et dans le pied de la table.

Les arguments de onGameEvent, tels que DCS_ControlAPI les donne : takeoff/landing (playerID, unit_missionID, airdromeName), crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID, killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide, weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide), mission_end (winner, msg).

Un serveur multijoueur peut interdire l'export de son propre appareil (LoIsOwnshipExportAllowed vaut false) ; il n'y a alors plus de positions, seulement des événements, et la session le dit.

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `y` |
| Unités | mètres (est, altitude, nord depuis l'origine du théâtre) |
| Miroir pour la visionneuse | `z` |
| Échelle (`scale` : la visionneuse multiplie les positions par elle) | 1 |

Ces valeurs vont dans le `meta.json` de chaque session (`axes`) et, quand la session a des positions, dans le pied de `heat.parquet`, afin que la visionneuse 3DHeat tourne et mette à l'échelle les lignes toute seule - voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` l'affiche comme « autorisé (lit seulement ce que le jeu publie) ».
- Type `telemetry` : il ne lit que ce que le jeu ou la plateforme fournit (un port UDP ou une mémoire partagée que le jeu publie), donc il enregistre aussi en ligne ; l'indicateur ne décide que de la possibilité de lire la mémoire.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne - voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json`, et la table `stats` de `watcher.sqlite`) :

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Exhaustivité {#completeness}

Le Watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou gardé, jamais jeté. En plus des lignes, chaque paquet, page, ligne ou réponse que reçoit l'adaptateur est gardé en entier dans `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ gardé par son nom ; `used` marque ce qui est aussi devenu des lignes), et `selfCheck.completeness` dans `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- `p` (10 Hz) : position, LatLongAlt, assiette, IAS, AGL, g (x/y/z), type d'appareil, et le TAS, le Mach, la vitesse verticale, l'incidence, le dérapage, le cap magnétique, l'altitude radar, la vitesse du monde, les vitesses de rotation, « en vol » et le point et la direction de la caméra du hook 2 - tous en colonnes de lignes (unités telles que Export.lua les donne)
- `start` : mission, théâtre, id et nom du joueur, multijoueur, fichier de mission, serveur ; `mis` : la date et l'heure de début de la mission dans meta.json
- `ev` : chaque onGameEvent en ligne (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, tout autre nom tel quel)
- `noexport` et `stop` en lignes et dans meta.json

**Gardé brut**

- chaque ligne envoyée par le hook, en entier, comme `text` sous son type : `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop` ; une ligne d'un autre type sous `unknown`
- `d` (1 Hz, brut seulement) : LoGetSelfData en entier (pays, coalition, nom d'unité et de groupe, niveaux de type, drapeaux), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, vecteur de vent, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, balises radio, pause, accélération du temps, siège, pression, déviations - aplatis en clés pointées
- `mis` : la table météo de la mission, aplatie ; `cb` : onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage avec leurs arguments

**Non disponible**

- les autres unités (LoGetWorldObjects, LoGetObjectById) et les données de capteurs (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo) : non demandées - chaque objet d'une mission à 10 Hz coûte cher dans le cadre propre de DCS, et un serveur les bloque (allow_object_export, allow_sensor_export) ; Tacview les enregistre
- la table complète de la mission (DCS.getCurrentMission contient chaque unité et chaque déclencheur, des mégaoctets) : seuls sa date, son heure de début, sa météo, son sortie, son théâtre et sa version sont envoyés
- les callbacks onPlayerTry\* : ils répondent à DCS (autoriser ou refuser), donc le hook n'y touche pas
- les adresses et UCID des autres joueurs : net.get_player_info ne les donne qu'à un serveur, et ils ne sont pas à garder pour le joueur
- les entrées d'une table au-delà de 800 clés ou de 6 niveaux de profondeur dans une ligne `d` sont coupées, pour qu'une ligne reste un seul datagramme

**Taille** : environ 20 Mo par heure de lignes `p` (10 par seconde, environ 500 octets chacune avec son cadre) et 15 à 40 Mo de vidages `d` (un par seconde, 4 à 10 Ko selon la charge et la route de l'appareil), avant zstd ; les clés répétées se compressent environ dix fois

## Vérifié {#verified}

format des lignes testé avec des datagrammes synthétiques ; le hook Lua n'est pas testé dans DCS (écrit à partir de l'API hook/export de DCS et de la liste des fonctions Lo\* de Scripts\Export.lua, non exécuté)

## Source {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
