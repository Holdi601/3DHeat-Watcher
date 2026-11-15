---
title: "DCS World (ζωντανά δεδομένα)"
nav_order: 10
lang: "el"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (ζωντανά δεδομένα) {#dcs-world-live-data}

Όσο παίζετε DCS World, ο watcher αποθηκεύει τα δεδομένα που στέλνει το ίδιο το παιχνίδι, ώστε να μπορείτε να τα δείτε αργότερα πάνω σε έναν χάρτη στον 3DHeat viewer.

*Τεχνικές λεπτομέρειες: adapter `dcs`, είδος [`telemetry`](sources-and-rules.md)· τρέχει όσο τρέχει το `DCS.exe` και ελέγχει για νέα δεδομένα κάθε 0,1 s.*

## Τι καταγράφεται {#what-is-recorded}

- η δική σας θέση στα 10 Hz, σε μέτρα ανατολικά/ύψος/βόρεια από την αρχή του θεάτρου (από γεωγραφικό πλάτος/μήκος/ύψος)· τα lat/lon/alt και οι παγκόσμιες μετρήσεις του DCS (dcs_x βόρεια, dcs_y πάνω, dcs_z ανατολικά) ως στήλες
- στάση, ένδειξη και πραγματική ταχύτητα αέρα, Mach, κατακόρυφη ταχύτητα, γωνία πρόσπτωσης και πλευρική ολίσθηση, μαγνητική πορεία, AGL και ραδιοτραχύμετρο, g στους τρεις άξονες, ταχύτητα και ρυθμούς περιστροφής, στον αέρα, η θέση και το διάνυσμα κατεύθυνσης της κάμερας, τύπος αεροσκάφους
- απογειώσεις και προσγειώσεις με το αεροδρόμιο· συντριβές, εξοδιασμοί, θάνατοι πιλότου
- φόνοι και καταρρίψεις με τους δύο τύπους μονάδων και το όπλο· άλλα γεγονότα παιχνιδιού όπως δίνονται
- ζωές ανά αποστολή (spawn ... session_end), φόνοι, θάνατοι, απόσταση, μέγιστο ύψος, μέγιστο g
- κάθε γραμμή που στέλνει το hook κρατιέται ολόκληρη στο heat.raw.parquet, με ένα δείγμα των πινάκων εξαγωγής του αεροσκάφους κάθε δευτερόλεπτο (κινητήρες, σασί και πτερύγια, φορτίο, αντίμετρα, διαδρομή, πλοήγηση) και κάθε άλλη επιστροφή κλήσης (παύση, συνομιλία, παίκτες που μπαίνουν, φόρτωση αποστολής)

## Από πού προέρχεται {#where-it-comes-from}

το hook του watcher %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, γραμμές UDP στο 127.0.0.1:41993

## Πώς το ενεργοποιείτε {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (προσθέτει το Scripts\Hooks\heat3d-watch.lua), και μετά ξεκινήστε ξανά το DCS

Γράψε την εντολή σε ένα τερματικό που έχει ανοίξει στον φάκελο του watcher (βλ. [Before you start](before-you-start.md)). Αν αποτύχει, η τελευταία γραμμή λέει γιατί· το [Installing and running](installing-and-running.md) καλύπτει τις συνηθισμένες αιτίες.

`python -m heat3d_watch setup dcs` δείχνει ποια αρχεία θα άλλαζε· το `python -m heat3d_watch setup dcs --apply` τα αλλάζει, κρατώντας το αρχικό ως `<file>.heat3d-backup` (βλ. [Commands](commands.md#setup)). Τυπώνει `dcs: changed: ...` για κάθε αλλαγή, ή `dcs: nothing to change` αν είναι ήδη ενεργοποιημένο.

## Πώς λειτουργεί {#how-it-works}

DCS World: ένα μικρό script hook του ίδιου του watcher, που στέλνει γραμμές UDP στο 127.0.0.1:41993.

Το DCS εκτελεί αρχεία Lua από το `Saved Games\DCS*\Scripts\Hooks\` κατά την εκκίνηση· ένα hook μπορεί να διαβάζει τις συναρτήσεις εξαγωγής (`Export.Lo*`) και να λαμβάνει τις επιστροφές κλήσης της προσομοίωσης (`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - βλ. `<DCS>\API\DCS_ControlAPI.html` και <https://wiki.hoggitworld.com/view/DCS_Export_Script>.
Το `setup` γράφει εκεί το `heat3d-watch.lua` (δικό του αρχείο: το Export.lua και τα hooks άλλων εργαλείων δεν αγγίζονται), που στέλνει δέκα γραμμές το δευτερόλεπτο, μία ακόμη κάθε δευτερόλεπτο, και μία για κάθε γεγονός ή επιστροφή κλήσης, χωρίς ποτέ να περιμένει απάντηση. Η θύρα είναι 41993, ώστε το JoyPro (41992) και το Tacview (42674) να συνεχίζουν να λειτουργούν δίπλα της. Οι γραμμές (πεδία χωρισμένα με ';'):

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

`p` είναι το LoGetSelfData: Position x/y/z - οι παγκόσμιες μετρήσεις του DCS, x βόρεια, y πάνω, z ανατολικά - μαζί με LatLongAlt (μοίρες, m), Heading/Pitch/Bank (ακτίνια), με LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) και LoGetAccelerationUnits() x/y/z (g)· και, όπως τα τεκμηριώνει το `Scripts\Export.lua`, LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s), LoGetAngleOfAttack και LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad), LoGetRadarAltimeter (m), LoGetVectorVelocity (παγκόσμια m/s), LoGetAngularVelocity (rad/s), LoGetInAir, και το σημείο και το διάνυσμα κατεύθυνσης του LoGetCameraPosition (παγκόσμια μέτρα). Το `d` είναι ένα δείγμα ολόκληρων πινάκων κάθε δευτερόλεπτο, σε επίπεδα κλειδιά με τελείες: LoGetSelfData (χώρα, συνασπισμός, ονόματα μονάδας και ομάδας, επίπεδα τύπου, σημαίες), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus και μερικούς αριθμούς (παύση, επιτάχυνση χρόνου, θέση, πίεση, αποκλίσεις). Ο watcher κρατά κάθε γραμμή ολόκληρη στο ακατέργαστο αρχείο· το `p` γίνεται και γραμμές.

Οι θέσεις μπαίνουν στον ίδιο επίπεδο χάρτη με των άλλων προσομοιωτών πτήσης (`Tangent`: x ανατολικά, y ύψος πάνω από τη θάλασσα, z βόρεια, σε μέτρα), από το LatLongAlt, γύρω από τη σταθερή αρχή του θεάτρου (`THEATRES`, από το `map` της γραμμής start), ώστε κάθε αποστολή στο ίδιο θέατρο να μοιράζεται έναν χάρτη, πάνω στον οποίο ο viewer μπορεί να βάλει τον πραγματικό κόσμο. Ένα θέατρο που δεν υπάρχει στον πίνακα παίρνει το γεωγραφικό πλάτος και μήκος της πρώτης μέτρησης, στρογγυλεμένα σε ολόκληρες μοίρες. Τα x/y/z του DCS κρατιούνται ως `dcs_x`, `dcs_y`, `dcs_z`· μια μέτρηση χωρίς LatLongAlt δεν μπορεί να τοποθετηθεί και μετράται μόνο (`fixes_without_latlon`). Η αρχή είναι το `geo` της συνεδρίας, στο meta.json και στο υποσέλιδο του πίνακα.

Τα ορίσματα του onGameEvent, όπως τα δίνει το DCS_ControlAPI: takeoff/landing (playerID, unit_missionID, airdromeName), crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID, killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide, weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide), mission_end (winner, msg).

Ένας διακομιστής πολλών παικτών μπορεί να απαγορεύσει την εξαγωγή του δικού σας αεροσκάφους (LoIsOwnshipExportAllowed είναι false)· τότε δεν υπάρχουν θέσεις, μόνο γεγονότα, και η συνεδρία το λέει.

## Θέσεις και άξονες {#positions-and-axes}

| | |
|---|---|
| Καταγράφονται θέσεις | ναι |
| Άξονας προς τα πάνω | `y` |
| Μονάδες | μέτρα (ανατολικά, ύψος, βόρεια από την αρχή του θεάτρου) |
| Καθρέφτης για τον προβολέα | `z` |
| Κλίμακα μονάδας (`scale`: ο viewer πολλαπλασιάζει τις θέσεις με αυτήν) | 1 |

Αυτά μπαίνουν στο `meta.json` (`axes`) κάθε συνεδρίας και, όταν η συνεδρία έχει θέσεις, στο υποσέλιδο του `heat.parquet`, ώστε ο 3DHeat viewer να γυρίζει και να κλιμακώνει τις γραμμές μόνος του - βλ. [The data](the-data.md).

## Πολλαπλός παίκτης {#multiplayer}

- Σημειωμένο ως παιγμένο online (`multiplayer`): **ναι**. Το `games --markdown` το δείχνει ως "allowed (reads only what the game publishes)".
- Είδος `telemetry`: διαβάζει μόνο ό,τι δίνει το παιχνίδι ή η πλατφόρμα (μια θύρα UDP ή κοινή μνήμη που δημοσιεύει το παιχνίδι), οπότε καταγράφει και στο online παιχνίδι, όπως και offline· η σήμανση αποφασίζει μόνο αν επιτρέπεται ποτέ η ανάγνωση μνήμης.
- Μνήμη: **ποτέ** δεν διαβάζεται από αυτόν τον adapter. Μόνο οι adapters `memory` διαβάζουν μνήμη, και ποτέ για παιχνίδι σημειωμένο ως παιγμένο online - βλ. [Sources and rules](sources-and-rules.md).

## Στατιστικά που καταγράφονται {#statistics-recorded}

Τα κλειδιά στατιστικών που ορίζει ο κώδικας αυτού του adapter με όνομα (το `stats` κάθε συνεδρίας στο `meta.json` και ο πίνακας `stats` του `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

Ένα κλειδί μέσα σε άγκιστρα συμπληρώνεται κατά την εκτέλεση (το `score.{team}` είναι ένα κλειδί ανά ομάδα). Τα κλειδιά που ο κώδικας παίρνει από πίνακα πεδίων του παιχνιδιού ή από τα δικά του ονόματα στατιστικών δεν είναι σε αυτή τη λίστα· το "Τι καταγράφεται" παραπάνω τα ονομάζει.

## Πληρότητα {#completeness}

Ο watcher ακολουθεί τον [κανόνα μετατροπέα](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) του 3DHeat: ό,τι έχει η πηγή διαβάζεται ή κρατιέται, δεν πετιέται ποτέ. Εκτός από τις γραμμές, κάθε πακέτο, σελίδα, γραμμή ή απάντηση που λαμβάνει ο adapter κρατιέται ολόκληρο στο `heat.raw.parquet` της συνεδρίας (στήλες `time`, `ms`, `type`, `used`, `payload`, `text`, και κάθε πεδίο που κρατιέται με το όνομά του· το `used` σημειώνει ό,τι έγινε και γραμμές), και το `selfCheck.completeness` του `meta.json` μετράει κάθε `type` - το `lost` είναι 0.

**Διαβάζεται**

- `p` (10 Hz): θέση, LatLongAlt, στάση, IAS, AGL, g (x/y/z), τύπος αεροσκάφους, και από το hook 2 το TAS, το Mach, την κατακόρυφη ταχύτητα, τη γωνία πρόσπτωσης, την πλευρική ολίσθηση, τη μαγνητική πορεία, το ραδιοτραχύμετρο, την παγκόσμια ταχύτητα, τους ρυθμούς περιστροφής, τον αέρα και το σημείο/διάνυσμα κατεύθυνσης της κάμερας - όλα ως στήλες γραμμών (μονάδες όπως τις δίνει το Export.lua)
- `start`: αποστολή, θέατρο, δικό σας αναγνωριστικό και όνομα παίκτη, πολλαπλός παίκτης, αρχείο αποστολής, διακομιστής· `mis`: η ημερομηνία και η ώρα έναρξης της αποστολής στο meta.json
- `ev`: κάθε onGameEvent ως γραμμή (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, κάθε άλλο όνομα όπως δίνεται)
- `noexport` και `stop` ως γραμμές και στο meta.json

**Κρατιέται ολόκληρο**

- κάθε γραμμή που στέλνει το hook, ολόκληρη, ως `text` κάτω από το είδος της: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`· γραμμή οποιουδήποτε άλλου είδους κάτω από το `unknown`
- `d` (1 Hz, μόνο ακατέργαστο): το LoGetSelfData ολόκληρο (χώρα, συνασπισμός, όνομα μονάδας και ομάδας, επίπεδα τύπου, σημαίες), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, διάνυσμα ανέμου, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, ραδιοφάροι, παύση, επιτάχυνση χρόνου, θέση, πίεση, αποκλίσεις - σε επίπεδα κλειδιά με τελείες
- `mis`: ο πίνακας καιρού της αποστολής, σε επίπεδα κλειδιά· `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage με τα ορίσματά τους

**Δεν είναι διαθέσιμο**

- άλλες μονάδες (LoGetWorldObjects, LoGetObjectById) και δεδομένα αισθητήρων (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): δεν ζητιούνται - κάθε αντικείμενο μιας αποστολής στα 10 Hz κοστίζει μέσα στο πλαίσιο του ίδιου του DCS, και ένας διακομιστής τα περιορίζει (allow_object_export, allow_sensor_export)· το Tacview τα καταγράφει
- ολόκληρος ο πίνακας αποστολής (το DCS.getCurrentMission κρατά κάθε μονάδα και κάθε σκανδάλη, μεγαβάιτ): στέλνονται μόνο η ημερομηνία, η ώρα έναρξης, ο καιρός, η διαδρομή, το θέατρο και η έκδοση
- οι επιστροφές κλήσης onPlayerTry\*: απαντούν στο DCS (επιτρέπουν ή αρνούνται), άρα το hook τις αφήνει
- οι διευθύνσεις και τα UCID των άλλων παικτών: το net.get_player_info τα δίνει μόνο σε διακομιστή, και δεν είναι του παίκτη για να τα κρατάει
- οι καταχωρήσεις ενός πίνακα πέρα από 800 κλειδιά ή 6 επίπεδα βάθος σε μία γραμμή `d` κόβονται, ώστε μία γραμμή να μένει ένα datagram

**Μέγεθος**: περίπου 20 MB την ώρα για τις γραμμές `p` (10 το δευτερόλεπτο, περίπου 500 bytes η καθεμία μαζί με το πλαίσιό της) και 15-40 MB για τα δείγματα `d` (ένα το δευτερόλεπτο, 4-10 KB ανάλογα με το φορτίο και τη διαδρομή του αεροσκάφους), πριν από το zstd· τα επαναλαμβανόμενα κλειδιά συμπιέζονται περίπου δέκα φορές

## Επαληθεύτηκε {#verified}

η μορφή των γραμμών δοκιμάστηκε με συνθετικά datagrams· το Lua hook δεν έχει δοκιμαστεί μέσα στο DCS (γράφτηκε από το API hook/export του DCS και τη λίστα συναρτήσεων Lo* του Scripts\Export.lua, δεν έχει τρέξει)

## Πηγή {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
