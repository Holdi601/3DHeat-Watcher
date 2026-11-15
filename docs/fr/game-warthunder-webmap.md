---
title: "War Thunder (état du jeu)"
nav_order: 47
lang: fr
source: game-warthunder-webmap.md
source_hash: "d6026c277030"
nav_exclude: true
search_exclude: true
---
# War Thunder (état du jeu) {#war-thunder-game-state}

Pendant que vous jouez à War Thunder, le Watcher enregistre ce que le jeu indique à des programmes sur votre propre ordinateur, afin que vous puissiez le regarder plus tard sur une carte dans la visionneuse 3DHeat.

*Détails techniques : adaptateur `warthunder-webmap`, type [`gsi`](sources-and-rules.md) ; il tourne pendant que `aces.exe` est lancé et cherche de nouvelles données toutes les 0,5 s.*

## Ce qui est enregistré {#what-is-recorded}

- votre propre position (est/nord de la carte en mètres ; hauteur depuis /state en avion, sinon 0) deux fois par seconde, cap, vitesse
- les apparitions et la sortie de votre véhicule de la carte (détruit, atterri, retour au hangar), une sortie par sortie
- les autres avions et unités au sol sur la minicarte, en positions avec des identifiants suivis et le camp (sans hauteur)
- les terrains, zones de capture et bases une fois, et les zones qui changent de camp
- les lignes du fil des frags et des dégâts (qui, véhicule, verbe) ; vos frags et vos morts quand votre nom est renseigné (`config --set player_names.warthunder-webmap=<nom>`)
- apparitions, distance, altitude maximale, TAS maximale, véhicule ; frags et morts quand votre nom est renseigné
- chaque réponse de la carte web gardée en entier dans heat.raw.parquet - le /state et le /indicators complets, le chat, les objectifs de la bataille et l'image de la carte comprises ; entre les batailles, dans une session à part

## D'où viennent les données {#where-it-comes-from}

la carte web locale du jeu, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## Comment l'activer {#how-to-switch-it-on}

Rien à activer : le Watcher lit la source telle que le jeu ou la plateforme la fournit.

## Fonctionnement {#how-it-works}

War Thunder : la carte web locale du jeu, sur <http://127.0.0.1:8111>.

Le jeu sert la page qu'un second écran ou un téléphone peut afficher (la « carte web »), ainsi que le JSON qui la sous-tend, pendant qu'il tourne - dans tous les modes, multijoueur compris :

```text
/map_info.json   {"map_min": [x, y], "map_max": [x, y], "grid_steps", "grid_zero", "map_generation",
                  "hud_type", "valid"}: the map's extent in metres; valid false in the hangar
/map_obj.json    [{"type": aircraft|ground_model|airfield|capture_zone|bombing_point|defending_point|
                  respawn_base_*|..., "icon": Player|Fighter|Bomber|Mediumtank|SPAA|..., "color": "#rrggbb",
                  "x", "y" (0..1 of the map picture, y down), "dx", "dy" (direction),
                  airfields "sx", "sy", "ex", "ey"}]: what the minimap shows, the player's own
                  vehicle with icon "Player"; no ids, no heights
/state           {"valid", "H, m", "TAS, km/h", "IAS, km/h", "M", "Vy, m/s", ...}: flight values,
                  valid only in an aircraft
/indicators      {"valid", "army": air|tank|..., "type": the vehicle}
/hudmsg?lastEvt=N&lastDmg=M   {"events": [...], "damage": [...]} newer than the ids given, each
                  {"id", "msg", "sender", "enemy", "mode", "time"}; damage lines read like
                  "Name (Vehicle) shot down Name (Vehicle)"
/gamechat?lastId=N  the chat newer than the id given, [{"id", "msg", "sender", "enemy", "mode", "time"}]
/mission.json    the battle's objectives and their status
/map.img         the map's picture the page draws the objects on
```

Chaque réponse est gardée en entier dans le fichier brut annexe de la session, sous son point d'accès (map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img) ; entre les batailles, les réponses vont dans une session à part.

Une position sur la carte devient des mètres grâce à l'étendue : u = min_x + x \* (max_x - min_x) à l'est, v = max_y - y \* (max_y - min_y) au nord (l'axe y de l'image descend). Les lignes sont x = u, y = hauteur (le « H, m » de l'avion propre ; 0 pour tout le reste), z = v, donc Y est vers le haut ; z est miroité pour la visionneuse, pour que le nord ne soit pas dessiné au sud.

Les couleurs indiquent les camps tels que le joueur les voit : le sien en jaune (#faC81E par défaut), l'escouade en vert, les alliés en bleu (#174DFF), les ennemis en rouge (#f40C00) ; les palettes pour daltoniens changent ces couleurs, donc c'est la teinte qui décide, pas la valeur exacte. Le jeu ne nomme personne sur la carte et ne donne pas d'identifiants aux objets : les autres objets reçoivent ici des identifiants en les suivant d'une interrogation à l'autre (le plus proche du même type et de la même icône), ce qui peut échanger deux avions du même type qui passent près l'un de l'autre. Le nom du joueur n'est pas non plus dans l'API : donnez-le dans les réglages (`config --set player_names.warthunder-webmap=<votre nom>`) et les lignes du fil des frags qui le concernent deviennent des frags et des morts ; sans lui, elles sont gardées comme fil des frags.

Sources : la page propre au jeu sur <http://127.0.0.1:8111> et son JSON ; les faits sur les champs, tels que documentés par le projet JoyPro 2 (docs/telemetry-recording.md ; GPL, utilisé pour les faits seulement).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `y` |
| Unités | mètres (est/nord de la carte ; hauteur seulement pour l'avion propre) |
| Miroir pour la visionneuse | `z` |
| Échelle (`scale` : la visionneuse multiplie les positions par elle) | 1 |

Ces valeurs vont dans le `meta.json` de chaque session (`axes`) et, quand la session a des positions, dans le pied de `heat.parquet`, afin que la visionneuse 3DHeat tourne et mette à l'échelle les lignes toute seule - voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` l'affiche comme « autorisé (lit seulement ce que le jeu publie) ».
- Type `gsi` : il ne lit que ce que le jeu ou la plateforme fournit (une intégration d'état de jeu ou une API locale que le jeu sert), donc il enregistre aussi en ligne ; l'indicateur ne décide que de la possibilité de lire la mémoire.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne - voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json`, et la table `stats` de `watcher.sqlite`) :

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Exhaustivité {#completeness}

Le Watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou gardé, jamais jeté. En plus des lignes, chaque paquet, page, ligne ou réponse que reçoit l'adaptateur est gardé en entier dans `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ gardé par son nom ; `used` marque ce qui est aussi devenu des lignes), et `selfCheck.completeness` dans `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- /map_info.json : l'étendue et la grille de la carte (mètres, identifiant de la carte) dans meta.json ; une carte invalide termine la bataille
- /map_obj.json (deux fois par seconde) : le véhicule propre, les autres avions et unités au sol (identifiants suivis, camp d'après la couleur, icône, cap, couleur) et les terrains, zones et bases comme lignes
- /state (deux fois par seconde, en avion) : hauteur, TAS, IAS, Mach et Vy sur les lignes propres
- /indicators (toutes les 2 s) : armée et type de véhicule
- /hudmsg (une fois par seconde) : les lignes du fil des frags et des dégâts comme frags, morts, coups et lignes de fil ; les autres événements de l'ATH comme lignes

**Gardé brut**

- chaque réponse en entier, `text` le JSON tel que le jeu l'a envoyé, sous son point d'accès : `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission` ; `map_img` les octets de l'image de la carte en `payload`, une fois par bataille
- ce que seul le fichier brut annexe contient : chaque champ de /state au-delà des cinq lus (AoA, AoS, Ny, Wx, accélérateur, régime, carburant, ... - l'ensemble diffère d'un avion à l'autre), chaque champ de /indicators (les instruments de bord des avions, la vitesse, le rapport, l'équipage et les stabilisateurs des chars), les autres clés des objets de carte (color[], blink, icon_bg, extrémités des terrains), l'expéditeur, l'ennemi et le mode des lignes de hudmsg, le chat (/gamechat, une fois par seconde), les objectifs de la bataille et leur statut (/mission.json, toutes les 10 s en bataille), les lignes dites avant le démarrage du Watcher
- entre les batailles (hangar, chargement), les réponses vont dans une session à part, marquée `between_battles` dans meta.json, qui n'a pas de lignes

**Non disponible**

- les noms, identifiants et hauteurs des véhicules des autres joueurs : la carte web n'en a pas (les identifiants sont donnés ici en suivant les objets d'une interrogation à l'autre) ; le fil des frags nomme les joueurs sans positions
- tout ce qui est hors de la carte web : les replays du jeu sont lus par le convertisseur de replays War Thunder, et la mémoire du jeu n'est jamais lue (jeu en ligne)
- /map_obj.json plus souvent que deux fois par seconde : la cadence d'interrogation reste basse, pour ne pas charger le serveur web du jeu

**Taille** : environ 50 à 120 Mo par heure de JSON avant zstd en bataille (map_obj de 5 à 15 Ko deux fois par seconde, state d'environ 1,5 Ko deux fois par seconde, indicators toutes les 2 s, le chat et les lignes HUD petits) plus l'image de la carte une fois par bataille (moins de 2 Mo) ; 1 à 2 Mo par heure entre les batailles (l'aspect de la carte deux fois par seconde, HUD et chat une fois, chacun une courte réponse) ; zstd réduit bien au-delà de dix fois le JSON répété

## Vérifié {#verified}

testé contre un faux serveur local qui sert des réponses au format de la carte web du jeu ; non testé avec le jeu lancé

## Source {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
