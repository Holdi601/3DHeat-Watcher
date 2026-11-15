---
title: "iRacing (données en direct)"
nav_order: 28
lang: fr
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (données en direct) {#iracing-live-data}

Pendant que vous jouez à iRacing, le watcher enregistre les données que le jeu envoie lui-même, pour que vous puissiez les regarder plus tard sous forme de statistiques et de chronologie.

*Détails techniques : adaptateur `iracing`, type [`telemetry`](sources-and-rules.md) ; il tourne pendant que `iRacingSim64DX11.exe` ou `iRacingSim64.exe` est lancé et cherche de nouvelles données toutes les 0,1 s.*

## Ce qui est enregistré {#what-is-recorded}

- la conduite à 5 Hz sans position (iRacing n'en donne aucune en direct) : vitesse, rapport, accélérateur, frein, tour, part du tour, position en course et dans la catégorie, incidents
- début de session, entrée et sortie de la voiture, entrée et sortie de la voie des stands, tours avec leur temps, incidents avec leurs points, drapeau à damier, arrivée
- les fichiers de télémétrie .ibt écrits pendant la session (latitude, longitude, altitude - le visualiseur les lit)
- tours, meilleur tour, incidents, position en course, arrêts au stand, distance, vitesse maximale
- toute la mémoire partagée dans `heat.raw.parquet` : en-tête, en-têtes de variables, informations de session, chaque ligne de télémétrie lue

## D'où viennent les données {#where-it-comes-from}

mémoire partagée Local\IRSDKMemMapFileName (le SDK d'iRacing) ; fichiers .ibt dans %USERPROFILE%\Documents\iRacing\telemetry

## Comment l'activer {#how-to-switch-it-on}

Rien pour les données en direct. Pour les positions : enregistrez la télémétrie dans la voiture (Alt+L) ou réglez irsdkLog=1 dans app.ini

## Comment ça marche {#how-it-works}

iRacing, en direct : le SDK de télémétrie d'iRacing, lu nativement.

iRacing publie sa télémétrie à destination des applications dans un mappage de fichier nommé, `Local\IRSDKMemMapFileName`, que le simulateur crée pendant son exécution (et il signale `Local\IRSDKDataValidEvent` à chaque mise à jour, signal inutile ici : le watcher lit dix fois par seconde). La disposition est celle de `irsdk_defines.h` du SDK, aussi suivie par pyirsdk (MIT) - réécrite ici à partir de ces faits :

```text
irsdk_header (little-endian int32s)
    0 ver, 4 status (bit 0: connected), 8 tickRate,
    12 sessionInfoUpdate, 16 sessionInfoLen, 20 sessionInfoOffset,
    24 numVars, 28 varHeaderOffset, 32 numBuf, 36 bufLen, 40 pad[2],
    48 varBuf[4]: { tickCount, bufOffset, pad[2] } (16 bytes each)
irsdk_varHeader (144 bytes, numVars of them at varHeaderOffset)
    0 type (0 char, 1 bool, 2 int, 3 bitfield, 4 float, 5 double),
    4 offset (into a line), 8 count, 12 countAsTime + 3 pad,
    16 name[32], 48 desc[64], 112 unit[32]
session info: YAML text at sessionInfoOffset, rewritten when
    sessionInfoUpdate changes (track, sessions, drivers)
```

Le simulateur écrit `numBuf` lignes en tournant ; la plus récente est celle au tickCount le plus élevé, et une ligne est relue si son tickCount a bougé pendant sa copie.

Les données en direct n'ont aucune position dans le monde : latitude, longitude et altitude ne sont que dans les fichiers `.ibt` qu'iRacing enregistre dans `Documents\iRacing\telemetry` (Alt+L dans la voiture, ou `irsdkLog=1`), que le visualiseur 3DHeat lit lui-même. Le watcher enregistre donc la conduite sous forme d'événements sans coordonnées - vitesse, tour, part du tour parcourue, position en course, incidents - plus les tours, incidents, arrêts au stand et le drapeau à damier, et à la fin les fichiers `.ibt` écrits pendant la session sous forme d'événements `telemetry_file`, que le visualiseur ouvre.

À côté des lignes, toute la carte mémoire est conservée dans le fichier brut de la session (`heat.raw.parquet`) : la partie fixe de l'en-tête (`header`, à chaque changement), les en-têtes de variables (`var_headers`, en entier, et en JSON dans `text`, à chaque changement de disposition), le YAML des informations de session (`session_info`, son texte à chaque changement de `sessionInfoUpdate`) et la dernière ligne de télémétrie (`telemetry`, toutes ses variables, à chaque lecture qui trouve un nouveau tick). Les en-têtes de variables et une ligne suffisent à un décodeur ultérieur pour lire n'importe quelle variable.

Source : le SDK d'iRacing (irsdk_defines.h, documentation du SDK « iRacing » sur le forum) ; kutu/pyirsdk (MIT) pour confirmer les décalages.

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | non |
| Axe vertical | `y` |
| Unités | pas de positions en direct ; les fichiers .ibt portent latitude/longitude/altitude |
| Miroir pour le visualiseur | aucun |
| Échelle des unités (`scale` : le visualiseur multiplie les positions par elle) | 1 |

Ces valeurs vont dans `meta.json` de chaque session (`axes`) et, quand la session a des positions, dans le pied de page de `heat.parquet`, pour que le visualiseur 3DHeat tourne et mette à l'échelle les lignes lui-même : voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` l'affiche comme « autorisé (lit seulement ce que le jeu publie) ».
- Type `telemetry` : il ne lit que ce que le jeu ou la plateforme fournit (un port UDP ou une mémoire partagée que le jeu publie), donc il enregistre aussi en ligne et hors ligne ; le drapeau décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne : voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json` et table `stats` de `watcher.sqlite`) :

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Exhaustivité {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais perdu. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé en entier dans `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu une ligne), et `selfCheck.completeness` dans `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- depuis la dernière ligne de télémétrie : temps de session, numéro, état et identifiant, sur la piste, en replay, tour, tours parcourus, part et mètres du tour, dernier et meilleur tour, vitesse, rapport, accélérateur, frein, régime, voie des stands, surface de la piste, position en course et dans la catégorie, nombre d'incidents propres (les lignes `driving` à 5 Hz et les événements)
- désormais aussi sur les lignes `driving` : `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (degrés, à partir des radians du simulateur - seulement quand l'en-tête de variable donne l'unité en rad), `fuel_l` (unité l), `lat_accel` et `lon_accel` (unité m/s^2)
- depuis le YAML des informations de session : l'index de la voiture du joueur, la piste et sa configuration, les types de sessions, le nom de chaque pilote, sa voiture, son équipe et son numéro (lignes session_start, meta.json)
- vérifié sur un bloc construit à partir d'irsdk_defines.h dans les tests ; pas encore vérifié sur le simulateur

**Conservé brut**

- `telemetry` : la dernière ligne en entier, chaque variable que le simulateur publie (les tableaux CarIdx de chaque voiture, pneus, suspension, les tableaux haute fréquence `_ST` là où le simulateur les a ...), à chaque lecture qui trouve un nouveau tick ; `tick` le compteur de ticks du simulateur ; `used` est faux pendant qu'un replay joue
- `var_headers` : les en-têtes de variables en entier (144 octets chacun) et, dans `text`, en JSON (nom, type, décalage, nombre, unité, description), à chaque changement de disposition - de quoi lire chaque variable de chaque ligne conservée
- `session_info` : le texte YAML en entier à chaque fois que son compteur de mise à jour bouge (week-end, sessions et résultats, pilotes, réglages de voiture, radio, listes de caméras), `update` le compteur
- `header` : l'en-tête irsdk de 112 octets en entier à chaque changement (version, état, fréquence de tick, décalages, ticks des lignes)

**Non disponible**

- une position en direct : la mémoire partagée n'en a pas ; latitude, longitude et altitude ne sont que dans les fichiers .ibt (enregistrement activé), que le visualiseur lit - le watcher nomme ceux écrits pendant la session
- les ticks entre deux lectures : le simulateur écrit 60 lignes par seconde dans 3 ou 4 emplacements et le watcher lit 10 fois par seconde, donc la plupart des ticks sont écrasés avant d'être lus ; le fichier .ibt a chaque tick quand l'enregistrement est activé

**Taille** : une ligne de télémétrie fait quelques Ko (environ 5 à 10 Ko avec les tableaux de chaque voiture), conservée jusqu'à 10 fois par seconde, plus l'en-tête (112 octets) aussi souvent et le YAML des informations de session (des dizaines de Ko) quand il change : environ 0,2 à 0,4 Go par heure sur piste avant compression ; zstd le ramène à une fraction (pas encore mesuré sur une vraie session)

## Vérifié {#verified}

testé sur un bloc de mémoire partagée construit dans le test à partir de la disposition irsdk ; non testé avec le simulateur

## Source {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
