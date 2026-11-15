---
title: "IL-2 Sturmovik: Great Battles (επαναλήψεις)"
nav_order: 27
lang: "el"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (επαναλήψεις) {#il-2-sturmovik-great-battles-replays}

Μετά από αγώνα του IL-2 Sturmovik: Great Battles, ο watcher μετατρέπει την επανάληψη που αποθήκευσε το παιχνίδι σε αρχεία που μπορείτε να δείτε σε χάρτη στον 3DHeat viewer.

*Τεχνικές λεπτομέρειες: adapter `il2-tacview`, είδος [`replay`](sources-and-rules.md)· τρέχει συνεχώς (δεν περιμένει να ξεκινήσει παιχνίδι) και ελέγχει για νέα δεδομένα κάθε 5 s.*

## Τι καταγράφεται {#what-is-recorded}

- κάθε αεροσκάφος, όχημα και πλοίο της εγγραφής: θέσεις μία φορά το δευτερόλεπτο (μέτρα ανατολικά/πάνω/βόρεια από το σημείο αναφοράς της εγγραφής· γεωγραφικό πλάτος/μήκος/υψόμετρο ως στήλες)
- εμφανίσεις, καταστροφές (θάνατος) και αποχωρήσεις (left), απογειώσεις και προσγειώσεις όταν έχουν καταγραφεί
- αντικείμενα, καταστροφές, απογειώσεις, προσγειώσεις και διάρκεια ανά εγγραφή
- κάθε γραμμή της εγγραφής ολόκληρη στο heat.raw.parquet, στον χρόνο των γραμμών

## Από πού προέρχεται {#where-it-comes-from}

Οι δικές του εγγραφές Tacview του παιχνιδιού &lt;game>\data\Tracks\\\*.acmi (κείμενο ACMI 2.x, απλό ή συμπιεσμένο σε zip)

## Πώς να το ενεργοποιήσετε {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 στο [KEY = track_record])

Γράψτε την εντολή σε τερματικό που ανοίγει στον φάκελο του watcher (δείτε [Πριν ξεκινήσετε](before-you-start.md)). Αν αποτύχει, η τελευταία γραμμή λέει γιατί· η [Εγκατάσταση και εκτέλεση](installing-and-running.md) καλύπτει τις συνηθισμένες αιτίες.

Η εντολή `python -m heat3d_watch setup il2-tacview` δείχνει ποια αρχεία θα άλλαζε· η `python -m heat3d_watch setup il2-tacview --apply` τα αλλάζει, κρατώντας το αρχικό ως `<file>.heat3d-backup` (δείτε [Εντολές](commands.md#setup)). Τυπώνει `il2-tacview: changed: ...` για κάθε αλλαγή, ή `il2-tacview: nothing to change` όταν είναι ήδη ενεργό.

## Πώς λειτουργεί {#how-it-works}

IL-2 Sturmovik: Great Battles — η έξοδος τηλεμετρίας UDP του παιχνιδιού και οι δικές του εγγραφές Tacview.

1. Τηλεμετρία ("Telemetry output of IL2 v4.003", αναθεώρηση 1.2, που συνοδεύει το αρχείο `<game>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Ενεργοποιείται στο `<game>\data\startup.cfg`, ενότητα `[KEY = telemetrydevice]`: τα `addr`, `addr1`, ... = "IP[:port]" (πολλαπλοί προορισμοί ταυτόχρονα), `decimation` (50 Hz / n), `enable`, `port`. Το `setup` προσθέτει έναν προορισμό, 127.0.0.1:41995 (το JoyPro χρησιμοποιεί το 41994, η προεπιλογή του παιχνιδιού είναι το 4322), και ενεργοποιεί την έξοδο. Πακέτα, little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Ενδείκτες: 0 ENG_RPM, 1 ENG_MP, 2/3 τρέμουλο κινητήρα, 4 LGEARS_STATE, 5 LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz με τη βαρύτητα), 9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14 VERTICAL_SPEED (m/s). Συμβάντα (συσκευασμένα σε 2 bytes): 0 SET_FOCUS (STRING: byte μήκους + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass, float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float pos[3]}, 4 DROP_BOMB και 5 ROCKET_LAUNCH {float pos[3], float mass, WORD flags}, 6 HIT και 7 DAMAGE {float pos[3], float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short coalition}. Οι θέσεις των συμβάντων είναι τοπικές ως προς το αεροσκάφος του παίκτη· η ροή δεν έχει καθόλου θέση στον κόσμο — άρα αυτά είναι συμβάντα και αριθμοί, όχι διαδρομή.

2. Εγγραφή Tacview: το `tacviewrecord = 1` στο `[KEY = track_record]` κάνει το παιχνίδι να γράφει `<game>\data\Tracks\*.acmi` (σε multiplayer αποφασίζει ο server). Ένα ολοκληρωμένο αρχείο μετατρέπεται: κάθε αεροσκάφος, όχημα και πλοίο με τις θέσεις του, εμφάνιση και αφαίρεση (καταστράφηκε ή έφυγε), απογειώσεις και προσγειώσεις όταν τις έχει η εγγραφή. Μορφή κειμένου ACMI 2.x, απλή ή συμπιεσμένη, σύμφωνα με <https://www.tacview.net/documentation/acmi/en/> — οι γραμμές "#t" μετακινούν το ρολόι, οι γραμμές "id,Key=Value,..." ορίζουν ιδιότητες (αναγνωριστικά σε δεκαεξαδικό, κόμματα διαφυγής "\\,", ένα επιλογικό "\\" στο τέλος συνεχίζει τη γραμμή), το "-id" αφαιρεί ένα αντικείμενο, το αντικείμενο 0 φέρει τις γενικές τιμές (ReferenceLongitude/Latitude, RecordingTime, ...) και τα συμβάντα ("Event=Destroyed\|id\|text"). T = Lon\|Lat\|Alt[\|U\|V] ή Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], με γεωγραφικό μήκος και πλάτος σε σχέση με το σημείο αναφοράς, τα κενά πεδία αμετάβλητα. Οι θέσεις μπαίνουν σε επίπεδο χάρτη γύρω από το σημείο αναφοράς: x ανατολικά, y υψόμετρο, z βόρεια, σε μέτρα. Το σημείο αναφοράς είναι το `geo` της συνεδρίας, που κρατιέται στο meta.json και στο footer του πίνακα, ώστε ο viewer να βάζει τον πραγματικό κόσμο κάτω από τις διαδρομές.

Η ίδια ενότητα εξυπηρετεί επίσης: [IL-2 Sturmovik: Great Battles (ζωντανά δεδομένα)](game-il2.md).

## Θέσεις και άξονες {#positions-and-axes}

| | |
|---|---|
| Καταγράφονται θέσεις | ναι |
| Άξονας προς τα πάνω | `y` |
| Μονάδες | μέτρα (ανατολικά, υψόμετρο, βόρεια από την πρώτη μέτρηση) |
| Καθρέφτισμα για τον viewer | `z` |
| Κλίμακα μονάδας (`scale`: ο viewer πολλαπλασιάζει τις θέσεις με αυτήν) | 1 |

Αυτά μπαίνουν στο `meta.json` (`axes`) κάθε συνεδρίας και, όταν η συνεδρία έχει θέσεις, στο footer του `heat.parquet`, ώστε ο viewer του 3DHeat να γυρίζει και να κλιμακώνει τις γραμμές μόνος του — δείτε [Τα δεδομένα](the-data.md).

## Πολλαπλός παίκτης {#multiplayer}

- Σημειωμένο ως παιγμένο online (`multiplayer`): **ναι**. Η `games --markdown` το εμφανίζει ως "allowed (reads only what the game publishes)".
- Είδος `replay`: διαβάζει μόνο όσα δίνει το παιχνίδι ή η πλατφόρμα (επαναλήψεις και εγγραφές που αποθηκεύει το παιχνίδι), άρα καταγράφει και στο online παιχνίδι και offline· η σήμανση αποφασίζει μόνο αν επιτρέπεται ποτέ η ανάγνωση μνήμης.
- Μνήμη: **ποτέ** δεν διαβάζεται από αυτόν τον adapter. Μόνο οι adapters `memory` διαβάζουν μνήμη, και ποτέ για παιχνίδι σημειωμένο ως παιγμένο online — δείτε [Πηγές και κανόνες](sources-and-rules.md).

## Στατιστικά που καταγράφονται {#statistics-recorded}

Κλειδιά στατιστικών που ορίζει ο κώδικας του adapter με το όνομά τους (το `stats` κάθε συνεδρίας στο `meta.json` και ο πίνακας `stats` του `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

Ένα κλειδί σε αγκύλες συμπληρώνεται κατά τον χρόνο εκτέλεσης (το `score.{team}` είναι ένα κλειδί ανά ομάδα). Τα κλειδιά που ο κώδικας παίρνει από πίνακα πεδίων του παιχνιδιού ή από τα δικά του ονόματα στατιστικών δεν είναι σε αυτή τη λίστα· το "Τι καταγράφεται" παραπάνω τα ονομάζει.

## Πληρότητα {#completeness}

Ο watcher ακολουθεί τον [κανόνα μετατροπέα](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) του 3DHeat: ό,τι έχει η πηγή διαβάζεται ή κρατιέται, ποτέ δεν πετιέται. Εκτός από τις γραμμές, κάθε πακέτο, σελίδα, γραμμή ή απάντηση που λαμβάνει ο adapter κρατιέται ολόκληρο στο `heat.raw.parquet` της συνεδρίας (στήλες `time`, `ms`, `type`, `used`, `payload`, `text`, και όποιο πεδίο κρατιέται με το όνομά του· το `used` σημαδεύει ό,τι έγινε και γραμμές), και το `selfCheck.completeness` του `meta.json` μετρά κάθε `type` — το `lost` είναι 0.

**Διαβάζεται**

- η θέση T κάθε αντικειμένου (γεωγραφικό μήκος, πλάτος, υψόμετρο, roll, pitch, yaw, U, V, heading) ως θέση μία φορά το δευτερόλεπτο ανά αντικείμενο, με Name, Type, Pilot, Coalition/Color, Country, Group και Parent
- εμφανίσεις, αφαιρέσεις (θάνατος όταν πρώτα ήρθε συμβάν Destroyed, αλλιώς αποχώρηση), συμβάντα TakenOff και Landed, συμβάντα Message και Bookmark ως γραμμές
- οι γενικές τιμές ReferenceLongitude/Latitude (η αρχή του χάρτη), RecordingTime/ReferenceTime (πότε), DataSource, DataRecorder και Title στο meta.json

**Κρατιέται ως έχει**

- κάθε μη κενή λογική γραμμή ολόκληρη ως `text` (μια γραμμή που συνεχίζεται με επιλογικό "\" ενώνεται, όπως τη διαβάζει το ACMI), με το είδος της: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` και `event` (αντικείμενο 0), `object` (id,Key=Value,...)
- ό,τι κρατά μόνο το ακατέργαστο αρχείο: οι θέσεις ανάμεσα στις μία-τη-δευτερόλεπτο γραμμές, τα όπλα, βλήματα, φλόγες, chaff και άλλα αντικείμενα που δεν σχεδιάζονται ως διαδρομές, κάθε άλλη ιδιότητα (τηλεμετρία όπως IAS, AOA, γκάζι, καύσιμο όπου την έχει η εγγραφή), άλλες γενικές τιμές (Comments, Briefing, Author, Category), συμβάντα εκτός από τα διαβαζόμενα (Timeout, LeftArea, ...)

**Δεν είναι διαθέσιμα**

- τίποτα πέρα από όσα έχει η εγγραφή· ό,τι δεν γράφει το παιχνίδι στις εγγραφές του δεν υπάρχει σε αυτές

**Μέγεθος**: περίπου το κείμενο της ίδιας της εγγραφής συν περίπου 70 bytes ανά γραμμή, πριν τη συμπίεση· μια εγγραφή 100 MB γίνεται περίπου 150-250 MB ακατέργαστα, που το zstd τα φέρνει κοντά στο μέγεθος της συμπιεσμένης εγγραφής

## Επαλήθευση {#verified}

δοκιμάστηκε σε συνθετικά αρχεία ACMI 2.2 (απλά και συμπιεσμένα)· δεν έχει δοκιμαστεί σε εγγραφή από το ίδιο το παιχνίδι

## Πηγή {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Δημιουργήθηκε από τον adapter με το tools/gen_game_pages.py· αλλάξτε τον adapter και τρέξτε ξανά το εργαλείο, αντί να επεξεργάζεστε αυτή τη σελίδα. -->
