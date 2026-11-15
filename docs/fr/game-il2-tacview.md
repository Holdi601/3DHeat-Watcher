---
title: "IL-2 Sturmovik: Great Battles (replays)"
nav_order: 27
lang: "fr"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (replays) {#il-2-sturmovik-great-battles-replays}

Après une partie d'IL-2 Sturmovik: Great Battles, le watcher transforme le replay que le jeu a sauvegardé en fichiers que vous pouvez regarder sur une carte dans le visualiseur 3DHeat.

*Détails techniques : adaptateur `il2-tacview`, type [`replay`](sources-and-rules.md) ; il tourne en permanence (il n'attend pas le lancement d'un jeu) et cherche de nouvelles données toutes les 5 s.*

## Ce qui est enregistré {#what-is-recorded}

- chaque avion, véhicule et navire de l'enregistrement : positions une fois par seconde (mètres est/haut/nord depuis le point de référence de l'enregistrement ; latitude/longitude/altitude en colonnes)
- apparitions, destructions (mort) et départs (quitte la zone), décollages et atterrissages quand ils sont enregistrés
- objets, destructions, décollages, atterrissages et longueur par enregistrement
- chaque ligne de l'enregistrement conservée en entier dans heat.raw.parquet, sur l'horloge des lignes

## D'où viennent les données {#where-it-comes-from}

les enregistrements Tacview du jeu lui-même &lt;jeu>\data\Tracks\\\*.acmi (texte ACMI 2.x, brut ou compressé)

## Comment l'activer {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 dans [KEY = track_record])

Tapez la commande dans un terminal ouvert dans le dossier du watcher (voir [Avant de commencer](before-you-start.md)). Si elle échoue, la dernière ligne indique pourquoi ; [Installation et lancement](installing-and-running.md) couvre les causes habituelles.

`python -m heat3d_watch setup il2-tacview` liste les fichiers qu'il modifierait ; `python -m heat3d_watch setup il2-tacview --apply` les modifie, en gardant l'original sous `<file>.heat3d-backup` (voir [Commandes](commands.md#setup)). Il affiche `il2-tacview: changed: ...` pour chaque modification, ou `il2-tacview: nothing to change` quand c'est déjà activé.

## Comment ça marche {#how-it-works}

IL-2 Sturmovik: Great Battles - la sortie de télémétrie UDP du jeu, et ses propres enregistrements Tacview.

1. Télémétrie (« Telemetry output of IL2 v4.003 », révision 1.2, fournie sous
   `<jeu>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Activée dans
   `<jeu>\data\startup.cfg`, section `[KEY = telemetrydevice]` : `addr`,
   `addr1`, ... = « IP[:port] » (plusieurs cibles à la fois), `decimation` (50 Hz /
   n), `enable`, `port`. `setup` ajoute une cible, 127.0.0.1:41995 (JoyPro utilise
   41994, le port par défaut du jeu est 4322), et active la sortie. Paquets,
   en petit-boutiste :

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Indicateurs : 0 ENG_RPM, 1 ENG_MP, 2/3 vibrations du moteur, 4 LGEARS_STATE, 5
   LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz, gravité incluse), 9
   COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14
   VERTICAL_SPEED (m/s). Événements (compactés sur 2 octets) : 0 SET_FOCUS (STRING :
   octet de longueur + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float
   max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass,
   float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float
   pos[3]}, 4 DROP_BOMB et 5 ROCKET_LAUNCH
   {float pos[3], float mass, WORD flags}, 6 HIT et 7 DAMAGE {float pos[3],
   float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE
   gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long
   client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short
   coalition}. Les positions des événements sont locales à l'avion du joueur ; le flux
   n'a aucune position dans le monde - ce sont donc des événements et des chiffres, pas une trajectoire.

2. Enregistrement Tacview : `tacviewrecord = 1` dans `[KEY = track_record]` fait
   écrire au jeu `<jeu>\data\Tracks\*.acmi` (en multijoueur, c'est le serveur qui décide).
   Un fichier terminé est converti : chaque avion, véhicule et navire avec ses
   positions, son apparition et son retrait (détruit ou parti), ses décollages et atterrissages quand
   l'enregistrement les contient. Format texte ACMI 2.x, brut ou compressé, selon
   <https://www.tacview.net/documentation/acmi/en/> - les lignes « #t » font avancer
   l'horloge, les lignes « id,Key=Value,... » fixent des propriétés (identifiants en hexadécimal, virgules échappées « \\, »,
   une « \\ » en fin de ligne la prolonge), « -id » retire un objet, l'objet 0 porte les
   globales (ReferenceLongitude/Latitude, RecordingTime, ...) et les événements
   (« Event=Destroyed\|id\|text »). T = Lon\|Lat\|Alt[\|U\|V] ou
   Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], longitude et latitude par rapport à
   la référence, les champs vides restent inchangés. Les positions vont dans une carte plane
   autour du point de référence : x est, y altitude, z nord, en mètres. Le point de
   référence est le `geo` de la session, porté par meta.json et le pied de page de la table, afin que
   le visualiseur puisse poser le monde réel sous les trajectoires.

Ce même module sert aussi : [IL-2 Sturmovik: Great Battles (données en direct)](game-il2.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | oui |
| Axe vertical | `y` |
| Unités | mètres (est, altitude, nord depuis le premier relevé) |
| Miroir pour le visualiseur | `z` |
| Échelle des unités (`scale` : le visualiseur multiplie les positions par elle) | 1 |

Ces valeurs vont dans `meta.json` de chaque session (`axes`) et, quand la session a des positions, dans le pied de page de `heat.parquet`, pour que le visualiseur 3DHeat tourne et mette à l'échelle les lignes lui-même : voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` l'affiche comme « autorisé (lit seulement ce que le jeu publie) ».
- Type `replay` : il ne lit que ce que le jeu ou la plateforme fournit (les replays et démos que le jeu sauvegarde), donc il enregistre aussi en ligne et hors ligne ; le drapeau décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne : voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json` et table `stats` de `watcher.sqlite`) :

`destroyed`, `duration_s`, `objects`, `{r.event}s`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Exhaustivité {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais perdu. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé en entier dans `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu une ligne), et `selfCheck.completeness` dans `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- la position T de chaque objet (longitude, latitude, altitude, roulis, tangage, lacet, U, V, cap) comme des positions une fois par seconde et par objet, avec Name, Type, Pilot, Coalition/Color, Country, Group et Parent
- apparitions, retraits (mort si un événement Destroyed est venu avant, sinon parti), événements TakenOff et Landed, événements Message et Bookmark comme lignes
- les globales ReferenceLongitude/Latitude (l'origine de la carte), RecordingTime/ReferenceTime (quand), DataSource, DataRecorder et Title dans meta.json

**Conservé brut**

- chaque ligne logique non vide en entier comme `text` (une ligne prolongée par une « \\ » finale est recollée, comme la lit ACMI), sous son genre : `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` et `event` (objet 0), `object` (id,Key=Value,...)
- ce que seul le fichier brut contient : les positions entre les lignes d'une seconde, les armes, obus, fusées éclairantes, leurres et autres objets non tracés, toute autre propriété (télémétrie comme IAS, AOA, accélérateur, carburant quand l'enregistrement les contient), autres globales (Comments, Briefing, Author, Category), événements autres que ceux lus (Timeout, LeftArea, ...)

**Non disponible**

- rien de ce que l'enregistrement contient ; ce que le jeu n'écrit pas dans ses enregistrements n'y est pas

**Taille** : à peu près le texte de l'enregistrement lui-même, plus environ 70 octets par ligne, avant zstd : un enregistrement de 100 Mo donne environ 150 à 250 Mo bruts, que zstd ramène près de la taille de l'enregistrement compressé

## Vérifié {#verified}

testé sur des fichiers ACMI 2.2 synthétiques (texte et compressés) ; non testé sur un enregistrement du jeu

## Source {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
