---
title: "EA SPORTS F1 24 (ζωντανά δεδομένα)"
nav_order: 15
lang: "el"
source: game-f1-24.md
source_hash: "a189298930fc"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 24 (ζωντανά δεδομένα) {#ea-sports-f1-24-live-data}

Όσο παίζετε EA SPORTS F1 24, ο watcher αποθηκεύει τα δεδομένα που στέλνει το ίδιο το παιχνίδι, ώστε να μπορείτε να τα δείτε αργότερα πάνω σε έναν χάρτη στον 3DHeat viewer.

*Τεχνικές λεπτομέρειες: adapter `f1-24`, είδος [`telemetry`](sources-and-rules.md)· τρέχει όσο τρέχει το `F1_24.exe` και ελέγχει για νέα δεδομένα κάθε 0,1 s.*

## Τι καταγράφεται {#what-is-recorded}

- η θέση κάθε αυτοκινήτου (παγκόσμια XYZ, σε μέτρα) στα 10 Hz, με το όνομα του οδηγού, την ομάδα, και το δικό σας αυτοκίνητο σημειωμένο (`own_car` 1, από τον δείκτη του αυτοκινήτου σας)· με ταχύτητα, ταχύτητα ταχυτήτων, γκάζι, φρένο, τιμόνι, στροφές, DRS, yaw, pitch, roll (μοίρες) και g
- γύροι ανά αυτοκίνητο με τον χρόνο γύρου και τη θέση στον αγώνα· τερματισμοί και αποσύρσεις
- τα γεγονότα του αγώνα: έναρξη και λήξη συνεδρίας, γρηγορότερος γύρος, ποινές, προσπεράσεις, συγκρούσεις, safety car, κόκκινη σημαία, φώτα εκκίνησης, καρό σημαία, νικητής, flashbacks (`teleport` εκεί που ήταν το αυτοκίνητο, `spawn` εκεί που επέστρεψε)
- πίστα, τύπος συνεδρίας, γύροι και οδηγοί κάθε συνεδρίας
- οι δικοί σας γύροι, καλύτερος γύρος, θέση στον αγώνα και στην εκκίνηση, pit stops, ποινές, προσπεράσεις, συγκρούσεις, απόσταση, μέγιστη ταχύτητα
- κάθε πακέτο που στέλνει το παιχνίδι, ολόκληρο, στο `heat.raw.parquet` - και όσα δεν διαβάζονται σε γραμμές

## Από πού προέρχεται {#where-it-comes-from}

UDP telemetry 127.0.0.1:20777 (Documents\My Games\F1 24\hardwaresettings\hardware_settings_config.xml)

## Πώς το ενεργοποιείτε {#how-to-switch-it-on}

Στο παιχνίδι: Settings > Telemetry Settings > UDP Telemetry On, IP 127.0.0.1, port 20777· ή `python -m heat3d_watch setup f1-24 --apply` (αλλάζει το hardware_settings_config.xml, με αντίγραφο πρώτα· το παιχνίδι πρέπει να είναι κλειστό). Αν άλλη εφαρμογή έχει ήδη την 20777, ο watcher αφήνει τη θύρα σε εκείνη

Γράψε την εντολή σε ένα τερματικό που έχει ανοίξει στον φάκελο του watcher (βλ. [Before you start](before-you-start.md)). Αν αποτύχει, η τελευταία γραμμή λέει γιατί· το [Installing and running](installing-and-running.md) καλύπτει τις συνηθισμένες αιτίες.

`python -m heat3d_watch setup f1-24` δείχνει ποια αρχεία θα άλλαζε· το `python -m heat3d_watch setup f1-24 --apply` τα αλλάζει, κρατώντας το αρχικό ως `<file>.heat3d-backup` (βλ. [Commands](commands.md#setup)). Τυπώνει `f1-24: changed: ...` για κάθε αλλαγή, ή `f1-24: nothing to change` αν είναι ήδη ενεργοποιημένο.

## Πώς λειτουργεί {#how-it-works}

EA SPORTS F1 23, F1 24 και F1 25: το επίσημο UDP telemetry, κάθε αυτοκίνητο στην πίστα.

Τα παιχνίδια το στέλνουν μόνα τους (Settings > Telemetry Settings, ή
`Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`,
`<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`).
Little-endian, συμπαγές, με κεφαλίδα 29 bytes σε κάθε πακέτο (η ίδια στις μορφές 2023,
2024 και 2025):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Τι διαβάζεται, ανά αναγνωριστικό πακέτου:

```text
0 Motion        CarMotionData[22], 60 bytes each: world position x y z
                (metres; Y is up), world velocity, forward and right
                vectors (int16 / 32767), g-forces, yaw pitch roll
1 Session       weather, temperatures, total laps, track length, session
                type, track id, ... network game
2 Lap Data      LapData[22]: last lap time, lap distance, race position,
                current lap number, pit stops, penalties, grid position,
                driver and result status. 50 bytes per car in 2023; 57 in
                2024 and 2025, which added the minutes parts of the deltas
                and the speed trap.
3 Event         a four-letter code and a union of details: SSTA SEND FTLP
                RTMT DRSE DRSD TMPT CHQF RCWN PENA SPTP STLG LGOT DTSV SGSV
                FLBK BUTN RDFL OVTK SCAR COLL
4 Participants  ParticipantData[22]: AI or human, driver, team, race
                number, name (48 bytes in 2023 and 2024, 32 in 2025; 58,
                60 and 57 bytes per car)
6 Car Telemetry CarTelemetryData[22], 60 bytes: speed km/h, throttle,
                steer, brake, clutch, gear, rpm, DRS ...
```

Κάθε πακέτο κρατιέται επίσης ολόκληρο, όπως ήρθε, στο ακατέργαστο βοηθητικό αρχείο της συνεδρίας
(`heat.raw.parquet`, `type` το όνομα του πακέτου - `motion`, `car_status` ... -
με `format`, `packet_id`, `frame` και `session_uid`) - όσα διαβάζονται παραπάνω και όσα
δεν διαβάζει ακόμα τίποτα: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby
Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time
Trial, 15 Lap Positions, κάθε μεταγενέστερο αναγνωριστικό, και πακέτα σε μορφή που ο
watcher δεν διαβάζει. Άρα ένας μελλοντικός αποκωδικοποιητής χρειάζεται μόνο το βοηθητικό αρχείο.

Η θέση κάθε αυτοκινήτου βρίσκεται στο πακέτο Motion - και στο online, όπου την δίνει το ίδιο το
παιχνίδι (μόνο τα καύσιμα, το ERS, η ζημιά και τα λάστιχα κρατιούνται πίσω για παίκτες με
περιορισμένο "Your Telemetry"). Κάθε αυτοκίνητο καταγράφεται περίπου στα 10 Hz κάτω από το
όνομα του οδηγού ("car N" μέχρι να έρθουν τα ονόματα), η ομάδα με το όνομά της, και το
αυτοκίνητο του παίκτη σημειωμένο ως `own`.

Πηγές: το "F1 25 UDP Specification" της EA (forums.ea.com, F1 games info hub),
οι προδιαγραφές F1 23 και F1 24· οι ίδιοι πίνακες σε αντίγραφο στο
MacManley/f1-25-udp (MIT). Τα πακέτα στα τεστ φτιάχνονται από αυτές τις διατάξεις.

Το ίδιο module εξυπηρετεί και τα: [EA SPORTS F1 23 (ζωντανά δεδομένα)](game-f1-23.md), [EA SPORTS F1 25 (ζωντανά δεδομένα)](game-f1-25.md).

## Θέσεις και άξονες {#positions-and-axes}

| | |
|---|---|
| Καταγράφονται θέσεις | ναι |
| Άξονας προς τα πάνω | `y` |
| Μονάδες | μέτρα |
| Καθρέφτης για τον προβολέα | καμία |
| Κλίμακα μονάδας (`scale`: ο viewer πολλαπλασιάζει τις θέσεις με αυτήν) | 1 |

Αυτά μπαίνουν στο `meta.json` (`axes`) κάθε συνεδρίας και, όταν η συνεδρία έχει θέσεις, στο υποσέλιδο του `heat.parquet`, ώστε ο 3DHeat viewer να γυρίζει και να κλιμακώνει τις γραμμές μόνος του - βλ. [The data](the-data.md).

## Πολλαπλός παίκτης {#multiplayer}

- Σημειωμένο ως παιγμένο online (`multiplayer`): **ναι**. Το `games --markdown` το δείχνει ως "allowed (reads only what the game publishes)".
- Είδος `telemetry`: διαβάζει μόνο ό,τι δίνει το παιχνίδι ή η πλατφόρμα (μια θύρα UDP ή κοινή μνήμη που δημοσιεύει το παιχνίδι), οπότε καταγράφει και στο online παιχνίδι, όπως και offline· η σήμανση αποφασίζει μόνο αν επιτρέπεται ποτέ η ανάγνωση μνήμης.
- Μνήμη: **ποτέ** δεν διαβάζεται από αυτόν τον adapter. Μόνο οι adapters `memory` διαβάζουν μνήμη, και ποτέ για παιχνίδι σημειωμένο ως παιγμένο online - βλ. [Sources and rules](sources-and-rules.md).

## Στατιστικά που καταγράφονται {#statistics-recorded}

Τα κλειδιά στατιστικών που ορίζει ο κώδικας αυτού του adapter με όνομα (το `stats` κάθε συνεδρίας στο `meta.json` και ο πίνακας `stats` του `watcher.sqlite`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

Ένα κλειδί μέσα σε άγκιστρα συμπληρώνεται κατά την εκτέλεση (το `score.{team}` είναι ένα κλειδί ανά ομάδα). Τα κλειδιά που ο κώδικας παίρνει από πίνακα πεδίων του παιχνιδιού ή από τα δικά του ονόματα στατιστικών δεν είναι σε αυτή τη λίστα· το "Τι καταγράφεται" παραπάνω τα ονομάζει.

## Πληρότητα {#completeness}

Ο watcher ακολουθεί τον [κανόνα μετατροπέα](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) του 3DHeat: ό,τι έχει η πηγή διαβάζεται ή κρατιέται, δεν πετιέται ποτέ. Εκτός από τις γραμμές, κάθε πακέτο, σελίδα, γραμμή ή απάντηση που λαμβάνει ο adapter κρατιέται ολόκληρο στο `heat.raw.parquet` της συνεδρίας (στήλες `time`, `ms`, `type`, `used`, `payload`, `text`, και κάθε πεδίο που κρατιέται με το όνομά του· το `used` σημειώνει ό,τι έγινε και γραμμές), και το `selfCheck.completeness` του `meta.json` μετράει κάθε `type` - το `lost` είναι 0.

**Διαβάζεται**

- 0 Motion: η παγκόσμια θέση και ταχύτητα κάθε αυτοκινήτου, και τώρα και το yaw, pitch, roll (μοίρες, από τα ακτίνια της προδιαγραφής) και τα πλευρικά, διαμήκη και κατακόρυφα g, σε κάθε γραμμή θέσης του αυτοκινήτου
- 1 Session: πίστα, τύπος συνεδρίας, συνολικοί γύροι, μήκος πίστας, online ή όχι (`sessions` στο meta.json)
- 2 Lap Data: χρόνος τελευταίου γύρου, αριθμός γύρου, θέση στον αγώνα και στην εκκίνηση, pit stops, ποινές, κατάσταση αποτελέσματος (γύροι, τερματισμοί, αποσύρσεις, στατιστικά)
- 3 Event: κάθε κωδικός εκτός του BUTN ως δική του γραμμή, με τις λεπτομέρειές του
- 4 Participants: ονόματα οδηγών, ομάδες, αριθμός ενεργών αυτοκινήτων (τα `player` και `team` των γραμμών, `drivers` στο meta.json)
- 6 Car Telemetry: ταχύτητα, ταχύτητα ταχυτήτων, γκάζι, φρένο, και τώρα και το τιμόνι (-1..1), τις στροφές και το DRS, σε κάθε γραμμή θέσης του αυτοκινήτου
- ελεγμένο με τις δημοσιευμένες προδιαγραφές UDP της EA για τις μορφές 2023, 2024 και 2025 (τα μεγέθη πακέτων ελέγχονται στα τεστ)· δεν έχει ελεγχθεί ακόμα με το ίδιο το παιχνίδι

**Κρατιέται ολόκληρο**

- κάθε πακέτο ολόκληρο στο `heat.raw.parquet`, `payload` το datagram, `type` το όνομα του αναγνωριστικού του: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` για αναγνωριστικό που οι προδιαγραφές δεν αναφέρουν ακόμα)· στήλες `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- το `used` είναι true για τα πακέτα που διαβάζονται παραπάνω (Motion, Session, Lap Data, Participants, Car Telemetry, και οι κωδικοί Event εκτός του BUTN)· τα υπόλοιπα - ρυθμίσεις αυτοκινήτου, κατάσταση αυτοκινήτου (καύσιμα, ERS, τύπος και ηλικία λάστιχων, σημαίες), τελική κατάταξη, lobby, ζημιά αυτοκινήτου, ιστορικό συνεδρίας (κάθε χρόνος γύρου και τομέα ανά αυτοκίνητο), σετ λάστιχων, motion ex (η ανάρτηση του δικού σας αυτοκινήτου, ταχύτητες τροχών, τοπική ταχύτητα, γωνιακή ταχύτητα και επιτάχυνση), time trial, θέσεις γύρων, γεγονότα κουμπιών BUTN - κρατιούνται για έναν μελλοντικό αποκωδικοποιητή
- `format <year>`: πακέτο σε μορφή πριν από το 2023 (άλλη διάταξη κεφαλίδας), ολόκληρο· `short`: datagram μικρότερο από την κεφαλίδα των 29 bytes, ολόκληρο

**Δεν είναι διαθέσιμο**

- καύσιμα, ERS, ζημιά και σετ λάστιχων άλλων παικτών online, όταν το "Your Telemetry" τους είναι περιορισμένο: το παιχνίδι στέλνει μηδενικά γι' αυτούς
- πακέτα που στάλθηκαν όσο ο watcher δεν τρέχει, ή όσο άλλη εφαρμογή κρατά τη θύρα 20777: το UDP δεν το αποθηκεύει το παιχνίδι

**Μέγεθος**: με ρυθμό αποστολής 60 Hz, κάθε πακέτο είναι περίπου 0,38 MB/s (Motion, Lap Data, Car Telemetry, Car Status και Motion Ex στα 60 Hz, Session History και Tyre Sets 20 το δευτερόλεπτο, Car Damage 10 το δευτερόλεπτο, Session και Car Setups 2 το δευτερόλεπτο)· συν περίπου 0,03 MB/s από τις κεφαλίδες των στοιχείων: περίπου 1,5 GB την ώρα οδήγησης πριν από τη συμπίεση, περίπου 0,55 GB στον προεπιλεγμένο ρυθμό των 20 Hz· το zstd το κατεβάζει σε ένα μικρό κλάσμα (οι άδειες θέσεις αυτοκινήτων και οι επαναλαμβανόμενες τιμές συμπιέζονται καλά· δεν έχει μετρηθεί ακόμα σε πραγματική συνεδρία)

## Επαληθεύτηκε {#verified}

δοκιμάστηκε σε πακέτα των μορφών 2023, 2024 και 2025, φτιαγμένα από τη δημοσιευμένη προδιαγραφή της EA, σταλμένα μέσω UDP· δεν έχει δοκιμαστεί με το παιχνίδι

## Πηγή {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
