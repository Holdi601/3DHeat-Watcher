---
title: "IL-2 Sturmovik: Great Battles (données en direct)"
nav_order: 26
lang: fr
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (données en direct) {#il-2-sturmovik-great-battles-live-data}

Pendant que vous jouez à IL-2 Sturmovik: Great Battles, le watcher enregistre les données que le jeu envoie lui-même, pour que vous puissiez les regarder plus tard sous forme de statistiques et de chronologie.

*Détails techniques : adaptateur `il2`, type [`telemetry`](sources-and-rules.md) ; il tourne pendant que `Il-2.exe` ou `IL2Series.exe` est lancé et cherche de nouvelles données toutes les 0,1 s.*

## Ce qui est enregistré {#what-is-recorded}

- les sorties : l'avion pris (spawn) et le moment où la sortie s'arrête (session_end) - sans position dans le monde : le jeu n'en envoie pas
- bombes et roquettes lâchées (masse), coups au but et dégâts subis, explosions, rafales de tir - positions locales à l'avion
- vitesse indiquée équivalente, AGL, vitesse verticale, g, régime moteur une fois par seconde, avec tous les autres indicateurs du paquet (pression d'admission, vibrations du moteur, état et pression du train, AoA, dérapage, accélérations x/y/z, vibrations du cockpit, volets, aérofreins)
- sorties, munitions tirées, bombes, roquettes, coups subis, vitesse maximale, g maximal, temps de vol ; titre du serveur et nom du pilote en ligne
- chaque paquet de télémétrie conservé en entier dans heat.raw.parquet

## D'où viennent les données {#where-it-comes-from}

la sortie UDP de télémétrie du jeu vers 127.0.0.1:41995 ([KEY = telemetrydevice] dans &lt;jeu>\data\startup.cfg)

## Comment l'activer {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (ajoute addrN = "127.0.0.1:41995", enable = true), puis redémarrez IL-2

Tapez la commande dans un terminal ouvert dans le dossier du watcher (voir [Avant de commencer](before-you-start.md)). Si elle échoue, la dernière ligne indique pourquoi ; [Installation et lancement](installing-and-running.md) couvre les causes habituelles.

`python -m heat3d_watch setup il2` liste les fichiers qu'il modifierait ; `python -m heat3d_watch setup il2 --apply` les modifie, en gardant l'original sous `<file>.heat3d-backup` (voir [Commandes](commands.md#setup)). Il affiche `il2: changed: ...` pour chaque modification, ou `il2: nothing to change` quand c'est déjà activé.

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

Ce même module sert aussi : [IL-2 Sturmovik: Great Battles (replays)](game-il2-tacview.md).

## Positions et axes {#positions-and-axes}

| | |
|---|---|
| Positions enregistrées | non |
| Axe vertical | `y` |
| Unités | aucune : la télémétrie n'a pas de positions dans le monde |
| Miroir pour le visualiseur | aucun |
| Échelle des unités (`scale` : le visualiseur multiplie les positions par elle) | 1 |

Ces valeurs vont dans `meta.json` de chaque session (`axes`) et, quand la session a des positions, dans le pied de page de `heat.parquet`, pour que le visualiseur 3DHeat tourne et mette à l'échelle les lignes lui-même : voir [Les données](the-data.md).

## Multijoueur {#multiplayer}

- Marqué comme joué en ligne (`multiplayer`) : **oui**. `games --markdown` l'affiche comme « autorisé (lit seulement ce que le jeu publie) ».
- Type `telemetry` : il ne lit que ce que le jeu ou la plateforme fournit (un port UDP ou une mémoire partagée que le jeu publie), donc il enregistre aussi en ligne et hors ligne ; le drapeau décide seulement si la mémoire peut être lue.
- Mémoire : **jamais** lue par cet adaptateur. Seuls les adaptateurs `memory` lisent la mémoire, et jamais pour un jeu marqué comme joué en ligne : voir [Sources et règles](sources-and-rules.md).

## Statistiques enregistrées {#statistics-recorded}

Clés de statistiques que le code de cet adaptateur fixe par leur nom (`stats` de chaque session dans `meta.json` et table `stats` de `watcher.sqlite`) :

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

Une clé entre accolades est complétée à l'exécution (`score.{team}` est une clé par équipe). Les clés que le code prend dans une table des champs du jeu ou dans les noms de statistiques du jeu ne figurent pas dans cette liste ; « Ce qui est enregistré » plus haut les nomme.

## Exhaustivité {#completeness}

Le watcher suit la [règle du convertisseur](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat : ce que la source contient est lu ou conservé, jamais perdu. En plus des lignes, chaque paquet, page, ligne ou réponse reçu par l'adaptateur est conservé en entier dans `heat.raw.parquet` de la session (colonnes `time`, `ms`, `type`, `used`, `payload`, `text`, puis tout champ conservé par son nom ; `used` marque ce qui est aussi devenu une ligne), et `selfCheck.completeness` dans `meta.json` compte chaque `type` - `lost` vaut 0.

**Lu**

- SET_FOCUS (l'avion pris : une sortie), DROP_BOMB et ROCKET_LAUNCH (masse, position locale), HIT et DAMAGE (position locale, force), EXPLOSION (position locale, rayon), GUN_FIRE (rafales par interrogation) comme lignes
- SETUP_ENG (index, id, position locale, régime maximal), SETUP_GUN (index, position locale, masse du projectile, vitesse initiale) et SETUP_LGEAR (index, id, position locale) comme lignes : les moteurs, canons et jambes de train de l'avion au début de la sortie
- SRV_TITLE, SRV_ADDR, SRS_ADDR et CLIENT_DAT (nom du pilote) dans meta.json ; la coalition de CTRL_DAT comme équipe de la sortie
- les quinze indicateurs de la spécification sur la ligne `state` une fois par seconde (une valeur en nombre, une par moteur, jambe de train ou axe en liste) ; vitesse, g et AGL maximaux relevés dans chaque paquet

**Conservé brut**

- chaque datagramme en entier comme `payload`, sous son Packet_ID : `0x54000101` pour la télémétrie (utilisé quand il a fait une ligne ou une entrée de meta.json), tout autre identifiant tel quel, un datagramme trop court pour en être un sous `short`
- ce que seul le fichier brut contient : les indicateurs entre les lignes d'une seconde (le jeu les envoie à 50 Hz / decimation), un événement SETUP plus court que la disposition de la spécification, des identifiants d'événements que la spécification ne liste pas

**Non disponible**

- une position dans le monde : la sortie de télémétrie n'en a pas (les positions des événements sont locales à l'avion) ; l'adaptateur il2-tacview lit les positions dans les enregistrements Tacview du jeu
- les autres avions et joueurs : la sortie ne décrit que l'avion propre du joueur

**Taille** : environ 8 Mo par heure à 10 Hz (réglage de setup, décimation 5 ; un paquet fait environ 160 octets plus son cadre), 40 Mo à 50 Hz plein régime, avant zstd ; zstd réduit les flottants répétitifs à une fraction

## Vérifié {#verified}

testé sur des paquets construits à partir de la spécification officielle Il2_TeleOutput du jeu (rév. 1.2) ; modifications de startup.cfg testées sur une copie du fichier ; non testé avec le jeu en marche

## Source {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
