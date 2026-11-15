---
title: "Microsoft Flight Simulator 2024 (ζωντανά δεδομένα)"
nav_order: 32
lang: "el"
source: game-msfs2024.md
source_hash: "011c18a23252"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2024 (ζωντανά δεδομένα) {#microsoft-flight-simulator-2024-live-data}

Όσο παίζετε Microsoft Flight Simulator 2024, ο watcher αποθηκεύει τα δεδομένα που στέλνει το ίδιο το παιχνίδι, ώστε να μπορείτε να τα δείτε αργότερα πάνω σε έναν χάρτη στον 3DHeat viewer.

*Τεχνικές λεπτομέρειες: adapter `msfs2024`, είδος [`telemetry`](sources-and-rules.md)· τρέχει όσο τρέχει το `FlightSimulator2024.exe` και ελέγχει για νέα δεδομένα κάθε 0,1 s.*

## Τι καταγράφεται {#what-is-recorded}

- η θέση του αεροσκάφους σας σε κάθε frame του προσομοιωτή, με δείγμα 10 Hz (γεωγραφικό πλάτος/μήκος/ύψος ως μέτρα ανατολικά/ύψος/βόρεια από την πρώτη μέτρηση· το lat/lon/alt κρατιέται ως στήλες)
- στάση, ένδειξη ταχύτητας αέρα, ταχύτητα εδάφους, AGL, g, στο έδαφος· πραγματική ταχύτητα αέρα, Mach, κατακόρυφη ταχύτητα, γωνία πρόσπτωσης, πλευρική ολίσθηση, μαγνητική πορεία, ταχύτητες σώματος, επιταχύνσεις και ρυθμοί περιστροφής σε περίπου 10 Hz
- βάρος, καύσιμα, πτερύγια, σασί, spoilers, φρένο στάθμευσης, autopilot, γκάζι, στροφές, καιρός, ρυθμός προσομοίωσης, ώρα και κατάσταση κάμερας μία φορά το δευτερόλεπτο· ο τίτλος του αεροσκάφους και ο τύπος, το μοντέλο και το αναγνωριστικό του ATC
- απογειώσεις, προσγειώσεις, συντριβές, πτήσεις που ξεκίνησαν και σταμάτησαν (session_start/session_end)
- χρόνος πτήσης, χρόνος στον αέρα, απόσταση, μέγιστο ύψος, μέγιστο g, προσγειώσεις
- κάθε μήνυμα SimConnect, ολόκληρο, στο heat.raw.parquet

## Από πού προέρχεται {#where-it-comes-from}

SimConnect μέσω του δικού σας SimConnect.dll (ο φάκελος του προσομοιωτή, ή %MSFS2024_SDK%\SimConnect SDK\lib)

## Πώς το ενεργοποιείτε {#how-to-switch-it-on}

τίποτα στον προσομοιωτή· χρειάζεται το SimConnect.dll - το MSFS 2020 το έχει στον φάκελό του, οι παίκτες του MSFS 2024 εγκαθιστούν το SDK του MSFS 2024

## Πώς λειτουργεί {#how-it-works}

Microsoft Flight Simulator 2020 και 2024: SimConnect, μέσω του δικού σας SimConnect.dll.

Το SimConnect είναι το δημοσιευμένο API πελάτη του προσομοιωτή (τεκμηρίωση SDK:
<https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>,
<https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>).
Ο watcher δεν συνοδεύει το DLL: φορτώνει αυτό που έχει έρθει με τον προσομοιωτή ή με το SDK του -
το MSFS 2020 βάζει το `SimConnect.dll` στον φάκελο εγκατάστασής του· το MSFS 2024 στο Steam
περιλαμβάνει μόνο το εσωτερικό του, γι' αυτό οι παίκτες του 2024 εγκαθιστούν το SDK του MSFS 2024
(`<SDK>\SimConnect SDK\lib\SimConnect.dll`· ο προσομοιωτής του 2024 δέχεται και πελάτες του 2020).

Οι κλήσεις, από το SimConnect.h, όλες επιστρέφουν HRESULT (0 = S_OK):

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

Κάθε μήνυμα ξεκινά με SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID}
(#pragma pack 1). Αυτά που διαβάζονται εδώ:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Μεταβλητές προσομοίωσης (ζητούνται με μονάδες ώστε να μη χρειάζεται μετατροπή): PLANE
LATITUDE/LONGITUDE (μοίρες), PLANE ALTITUDE (μέτρα, πάνω από τη θάλασσα), PLANE
ALT ABOVE GROUND (μέτρα), PLANE PITCH/BANK DEGREES και PLANE HEADING DEGREES
TRUE (μοίρες· τα πρόσημα του ίδιου του SimConnect - η μύτη πάνω δίνει αρνητικό pitch), AIRSPEED
INDICATED και GROUND VELOCITY (κόμβοι), G FORCE (gforce), SIM ON GROUND (bool).
Συμβάντα συστήματος: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded,
Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Τρεις ακόμα ορισμοί δεδομένων ζητούν το υπόλοιπο της πτήσης (`MOTION_VARS`,
κάθε έκτο frame του προσομοιωτή), την πιο αργή κατάσταση του αεροσκάφους (`STATE_VARS`, μία
φορά το δευτερόλεπτο) και τα ονόματά του (`NAME_VARS`, συμβολοσειρές των 256 bytes, όταν αλλάζουν)· ο
καθένας είναι δικός του ορισμός, οπότε μια μεταβλητή που δεν γνωρίζει μια έκδοση του προσομοιωτή
κοστίζει μόνο εκείνο το μπλοκ. Κάθε μήνυμα κρατιέται ολόκληρο στο ακατέργαστο βοηθητικό αρχείο της συνεδρίας.

Οι θέσεις μπαίνουν στον ίδιο επίπεδο χάρτη με του X-Plane (x ανατολικά, y ύψος, z βόρεια,
σε μέτρα από την πρώτη μέτρηση της συνεδρίας)· αυτή η μέτρηση είναι το `geo` της συνεδρίας, στο
meta.json και στο υποσέλιδο του πίνακα.

Το ίδιο module εξυπηρετεί και το: [Microsoft Flight Simulator 2020 (ζωντανά δεδομένα)](game-msfs2020.md).

## Θέσεις και άξονες {#positions-and-axes}

| | |
|---|---|
| Καταγράφονται θέσεις | ναι |
| Άξονας προς τα πάνω | `y` |
| Μονάδες | μέτρα (ανατολικά, ύψος, βόρεια από την πρώτη μέτρηση) |
| Καθρέφτης για τον προβολέα | `z` |
| Κλίμακα μονάδας (`scale`: ο viewer πολλαπλασιάζει τις θέσεις με αυτήν) | 1 |

Αυτά μπαίνουν στο `meta.json` (`axes`) κάθε συνεδρίας και, όταν η συνεδρία έχει θέσεις, στο υποσέλιδο του `heat.parquet`, ώστε ο 3DHeat viewer να γυρίζει και να κλιμακώνει τις γραμμές μόνος του - βλ. [The data](the-data.md).

## Πολλαπλός παίκτης {#multiplayer}

- Σημειωμένο ως παιγμένο online (`multiplayer`): **ναι**. Το `games --markdown` το δείχνει ως "allowed (reads only what the game publishes)".
- Είδος `telemetry`: διαβάζει μόνο ό,τι δίνει το παιχνίδι ή η πλατφόρμα (μια θύρα UDP ή κοινή μνήμη που δημοσιεύει το παιχνίδι), οπότε καταγράφει και στο online παιχνίδι, όπως και offline· η σήμανση αποφασίζει μόνο αν επιτρέπεται ποτέ η ανάγνωση μνήμης.
- Μνήμη: **ποτέ** δεν διαβάζεται από αυτόν τον adapter. Μόνο οι adapters `memory` διαβάζουν μνήμη, και ποτέ για παιχνίδι σημειωμένο ως παιγμένο online - βλ. [Sources and rules](sources-and-rules.md).

## Στατιστικά που καταγράφονται {#statistics-recorded}

Τα κλειδιά στατιστικών που ορίζει ο κώδικας αυτού του adapter με όνομα (το `stats` κάθε συνεδρίας στο `meta.json` και ο πίνακας `stats` του `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Ένα κλειδί μέσα σε άγκιστρα συμπληρώνεται κατά την εκτέλεση (το `score.{team}` είναι ένα κλειδί ανά ομάδα). Τα κλειδιά που ο κώδικας παίρνει από πίνακα πεδίων του παιχνιδιού ή από τα δικά του ονόματα στατιστικών δεν είναι σε αυτή τη λίστα· το "Τι καταγράφεται" παραπάνω τα ονομάζει.

## Πληρότητα {#completeness}

Ο watcher ακολουθεί τον [κανόνα μετατροπέα](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) του 3DHeat: ό,τι έχει η πηγή διαβάζεται ή κρατιέται, δεν πετιέται ποτέ. Εκτός από τις γραμμές, κάθε πακέτο, σελίδα, γραμμή ή απάντηση που λαμβάνει ο adapter κρατιέται ολόκληρο στο `heat.raw.parquet` της συνεδρίας (στήλες `time`, `ms`, `type`, `used`, `payload`, `text`, και κάθε πεδίο που κρατιέται με το όνομά του· το `used` σημειώνει ό,τι έγινε και γραμμές), και το `selfCheck.completeness` του `meta.json` μετράει κάθε `type` - το `lost` είναι 0.

**Διαβάζεται**

- δεδομένα θέσης SIMOBJECT_DATA (σε κάθε frame του προσομοιωτή): γεωγραφικό πλάτος, μήκος, ύψος, AGL, pitch, bank, πραγματική πορεία, IAS, ταχύτητα εδάφους, g, στο έδαφος - η τελευταία μέτρηση της δειγματοληψίας ως γραμμή, κάθε frame για αγγίγματα και απογειώσεις
- δεδομένα κίνησης SIMOBJECT_DATA (περίπου 10 Hz: TAS, Mach, κατακόρυφη ταχύτητα, γωνία πρόσπτωσης, ολίσθηση, μαγνητική πορεία, ταχύτητα σώματος, επιτάχυνση και ρυθμός περιστροφής σε τρεις άξονες) και δεδομένα κατάστασης (1 Hz: βάρη, καύσιμα, πτερύγια, σασί, spoilers, φρένο στάθμευσης, autopilot, κινητήρες, γκάζι και στροφές, εξωτερική θερμοκρασία, άνεμος, πίεση στη θάλασσα, ρυθμός προσομοίωσης, ώρα zulu και τοπική, κατάσταση κάμερας) πάνω στις γραμμές όπως έρχονται
- δεδομένα ονομάτων SIMOBJECT_DATA (τίτλος, τύπος ATC, μοντέλο και αναγνωριστικό) στο meta.json και στη στήλη `aircraft` των γραμμών· OPEN (εφαρμογή και έκδοση) στο meta.json
- EVENT και EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (το αρχείο της πτήσης) και AircraftLoaded (το αρχείο του αεροσκάφους) ως πτήσεις, συντριβές και meta.json
- το QUIT τερματίζει τη συνεδρία

**Κρατιέται ολόκληρο**

- κάθε μήνυμα που παραλαμβάνει ο watcher από το SimConnect, ολόκληρο ως `payload`, με το όνομα του SIMCONNECT_RECV_ID του: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (μεταβλητή ή συμβάν που ο προσομοιωτής δεν δέχτηκε, με το send id και το index), κάθε άλλο αναγνωριστικό με το όνομά του ή ως `RECV_<id>`
- ό,τι κρατά μόνο το ακατέργαστο βοηθητικό αρχείο: κάθε θέση του frame ανάμεσα στις γραμμές, τα συμβάντα Pause, Sim, CrashReset, PositionChanged και FlightSaved, ένας ορισμός που έκοψε ο προσομοιωτής (μία μεταβλητή που δεν γνώριζε· τότε το μπλοκ δεν διαβάζεται με ονόματα)· το `requests` του meta.json καταγράφει κάθε μεταβλητή και μονάδα κάθε ορισμού με τη σειρά τους, ώστε τα payloads να διαβάζονται χωρίς αυτό το module

**Δεν είναι διαθέσιμο**

- άλλα αεροσκάφη (κίνηση AI, άλλοι παίκτες online): το SimConnect_RequestDataOnSimObjectType θα ρωτούσε κάθε αεροσκάφος σε μια ακτίνα - περισσότερο φορτίο για τον προσομοιωτή, και πτήσεις άλλων παικτών
- το μπλοκ κίνησης σε κάθε frame: ζητιέται κάθε έκτο frame (περίπου 10 Hz, ο ρυθμός των γραμμών), που κρατά την ακατέργαστη ροή περίπου στο ένα πέμπτο του μεγέθους· το μπλοκ θέσης μένει σε κάθε frame
- οι χιλιάδες άλλες μεταβλητές του προσομοιωτή (ραδιόφωνα, φώτα, κάθε μετρητής κινητήρα, βλάβες): ένας ορισμός κρατά ό,τι ζητά· οι λίστες ζητούν την πτήση, την κατάσταση του αεροσκάφους και τον χρόνο του προσομοιωτή
- μετεωρολογικές παρατηρήσεις, εγκαταστάσεις (αεροδρόμια, VOR), δεδομένα πελάτη προσθηκών: ξεχωριστά αιτήματα, δεν γίνονται

**Μέγεθος**: περίπου 30-55 MB την ώρα πριν από το zstd: το μπλοκ θέσης σε κάθε frame του προσομοιωτή (περίπου 200 bytes με το πλαίσιό του, 30-60 το δευτερόλεπτο), το μπλοκ κίνησης περίπου 10 Hz (περίπου 240 bytes), το μπλοκ κατάστασης μία φορά το δευτερόλεπτο· το zstd μειώνει αρκετές φορές τα διπλά δεκαδικά

## Επαληθεύτηκε {#verified}

η αποκωδικοποίηση των μηνυμάτων δοκιμάστηκε σε buffers φτιαγμένα από τις διατάξεις του SimConnect.h· η ζωντανή σύνδεση με το SimConnect δεν έχει δοκιμαστεί

## Πηγή {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
