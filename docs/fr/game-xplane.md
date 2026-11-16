---
title: "X-Plane (données en direct)"
nav_order: 49
lang: "fr"
source: game-xplane.md
source_hash: "be1c5b21d2ef"
nav_exclude: true
search_exclude: true
---
# X-Plane (données en direct) {#x-plane-live-data}

Pendant que vous jouez à X-Plane, le watcher enregistre les données que le jeu envoie lui-même, pour que vous puissiez les regarder plus tard sur une carte dans le visualiseur 3DHeat.

*Détails techniques : adaptateur `xplane`, type [`telemetry`](sources-and-rules.md) ; il tourne pendant que `X-Plane.exe` est lancé et cherche de nouvelles données toutes les 0,1 s.*

## Ce qui est enregistré {#what-is-recorded}

- votre propre position à 10 Hz (latitude/longitude/altitude en mètres est/haut/nord depuis le premier relevé ; lat/lon/alt conservées en colonnes)
- attitude, vitesse indiquée et vitesse vraie, vitesse sol, Mach, vitesse verticale, AoA, dérapage, cap magnétique, AGL, g (normal, axial, latéral), vitesses et vitesses de rotation, volets, aérofreins, accélérateur, au sol
- masses (totale, carburant, charge utile), levier de train, pilote automatique, régime moteur et N1, heure et date du simulateur, pause, vitesse de simulation, replay, température extérieure et pression au niveau de la mer (X-Plane 12) une fois par seconde
- décollages, atterrissages, crashs, remises à zéro vol (session_start/session_end par vol)
- temps de vol, temps en l'air, distance, altitude maximale, g maximal, atterrissages
- chaque réponse envoyée par X-Plane conservée en entier dans heat.raw.parquet

## D'où viennent les données {#where-it-comes-from}

l'interface UDP de X-Plane sur 127.0.0.1:49000 (RREF pour les datarefs et RPOS pour la position, répondues au watcher)

## Comment l'activer {#how-to-switch-it-on}

X-Plane 12 : Settings > Network > Accept incoming connections (X-Plane 11 répond par défaut)

## Comment ça marche {#how-it-works}

X-Plane 11 et 12 : l'interface UDP du simulateur lui-même, sur le port 49000.

X-Plane répond à quiconque le demande sur 127.0.0.1:49000, au débit demandé, à l'adresse et au port d'où vient la requête (document « Exchanging Data with X-Plane » de X-Plane, fourni dans `<X-Plane>\Instructions\`) :

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

RPOS donne la latitude et la longitude en doubles (RREF seulement en flottants, à un demi-mètre près), donc il pilote la position ; RREF apporte le reste et prend le relais quand RPOS ne vient pas. Datarefs (noms tels que dans `Resources\plugins\DataRefs.txt` de X-Plane 12, <https://developer.x-plane.com/datarefs/>) :

```text
sim/flightmodel/position/latitude, longitude, elevation  deg, deg, m MSL
sim/flightmodel/position/true_theta, true_phi, true_psi  pitch, roll, true heading (deg)
sim/flightmodel/position/indicated_airspeed              knots
sim/flightmodel/position/groundspeed                     m/s
sim/flightmodel/position/y_agl                           m above ground
sim/flightmodel/forces/g_nrml                            g, normal to the wings
sim/flightmodel/failures/onground_any                    1 on the ground
sim/flightmodel2/misc/has_crashed                        1 crashed
sim/time/total_flight_time_sec                           since the flight was reset
```

et le reste du vol au même débit (vitesse vraie, vitesse verticale, AoA, dérapage, cap magnétique, Mach, g axial et latéral, vitesses de rotation, volets, aérofreins, accélérateur : `DATAREFS`), avec l'état plus lent de l'appareil une fois par seconde (masses, levier de train, servos du pilote automatique, heure du simulateur, pause et vitesse, météo : `SLOW_DATAREFS`). Chaque datagramme est aussi conservé en entier dans le fichier brut de la session, et meta.json nomme le dataref derrière chaque index RREF.

X-Plane 12 n'accepte ces requêtes qu'avec Settings > Network > « Accept incoming connections » activé. Les positions vont dans une carte plane autour du premier relevé de la session (`Tangent`) : x est, z nord, en mètres, y l'altitude au-dessus du niveau de la mer - ainsi un vol en palier reste en palier quelle que soit la distance, ce qu'un vrai plan tangent ferait pencher avec la courbure de la Terre. L'origine de la carte est le `geo` de la session : meta.json et le pied de page de la table le portent, pour que le visualiseur puisse poser le monde réel sous le vol.

Ce module regroupe aussi ce que les autres simulateurs de vol partagent : la carte plane, la comptabilité des vols (décollages, atterrissages, crashs, distance), le socket UDP et la liste de bibliothèque Steam.

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `y` |
| Unités | mètres (est, altitude, nord depuis le premier relevé) |
| Miroir pour le visualiseur | `z` |
| Échelle des unités (`scale` : le visualiseur multiplie les positions par cette valeur) | 1 |

Ces valeurs vont dans le `meta.json` de chaque session (`axes`) et, quand la session contient des positions, dans le pied de `heat.parquet`, pour que le visualiseur 3DHeat tourne et mette à l'échelle les lignes toute seule : voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **non**. `games --markdown` l'affiche comme « solo ».
- Type `telemetry` : il ne lit que ce que le jeu ou la plateforme fournit (un port UDP ou une mémoire partagée que le jeu publie), donc il enregistre aussi en ligne et hors ligne ; le drapeau décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne : voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json` et table `stats` de `watcher.sqlite`) :

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Exhaustivité {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais perdu. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé en entier dans `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu une ligne), et `selfCheck.completeness` dans `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- RPOS (10 Hz) : longitude, latitude, altitude, AGL, tangage, cap vrai, roulis, vitesse (est, haut, sud) et vitesses de rotation P/Q/R - tout sur les lignes
- RREF (10 Hz) : les 27 datarefs de `DATAREFS` - position, attitude, IAS, vitesse sol, TAS, vitesse verticale, AoA, dérapage, cap magnétique, Mach, g normal/axial/latéral, vitesses de rotation, volets, aérofreins, accélérateur, AGL, crashé, au sol, temps de vol - sur les lignes
- RREF (1 Hz) : les 20 datarefs de `SLOW_DATAREFS` - masses, levier de train, servos du pilote automatique, heure et date du simulateur, pause, vitesse de simulation, replay, nombre de moteurs, régime des moteurs 1 à 4, N1 des moteurs 1 et 2, température extérieure, pression au niveau de la mer - sur les lignes, à leur dernière valeur reçue

**Conservé brut**

- `RREF` et `RPOS` en entier comme `payload`, sous leur en-tête de quatre lettres (utilisés quand l'interrogation a fait une ligne ; dans les menus, sans relevé, ils n'en font aucune) ; tout ce que X-Plane envoie au port du watcher sous son propre en-tête, ou `unknown` ; `requests` dans meta.json dit quel dataref correspond à chaque index RREF, si bien que les charges utiles se lisent sans ce module
**Non disponible**

- les autres datarefs (X-Plane en a des milliers) : RREF n'envoie que ce qui est demandé, une souscription chacune ; la liste demande le vol, l'état de l'appareil et l'heure du simulateur - davantage de détails de cockpit (radios, lumières, toutes les jauges de moteur, pannes) multiplieraient les requêtes
- le nom de l'appareil et son type ICAO : des datarefs en tableaux d'octets, que RREF envoie comme un flottant par caractère
- les autres avions (IA et multijoueur) : les datarefs sim/multiplayer/position ne sont pas demandés
- la sortie DATA (Settings > Data Output) : elle envoie vers une adresse fixe choisie dans le simulateur, pas à qui la demande ; RREF et RPOS couvrent ce que lit le watcher

**Taille** : environ 17 Mo par heure avant zstd (RREF et RPOS à 10 Hz, d'environ 220 et 70 octets plus un cadre chacun, le RREF lent une fois par seconde), si X-Plane envoie les valeurs de chaque interrogation dans un seul paquet comme il le fait ; zstd réduit les flottants plusieurs fois

## Vérifié {#verified}

testé contre un faux X-Plane répondant à RREF/RPOS selon « Exchanging Data with X-Plane » de X-Plane 12 ; noms des datarefs vérifiés sur DataRefs.txt de X-Plane 12 ; non testé avec le simulateur en marche

## Source {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
