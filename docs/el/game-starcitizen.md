---
title: "Star Citizen (αρχεία καταγραφής)"
nav_order: 42
lang: "el"
source: game-starcitizen.md
source_hash: "6528f948d2e5"
nav_exclude: true
search_exclude: true
---
# Star Citizen (αρχεία καταγραφής) {#star-citizen-log-files}

Όσο παίζετε Star Citizen, ο watcher διαβάζει τα αρχεία που γράφει το παιχνίδι και αποθηκεύει τι συνέβη, ώστε να το δείτε αργότερα ως στατιστικά και χρονολόγιο.

*Τεχνικές λεπτομέρειες: προσαρμογέας `starcitizen`, είδος [`log`](sources-and-rules.md)· τρέχει όσο τρέχει το `StarCitizen.exe` και ελέγχει για νέα δεδομένα κάθε 0,5 s.*

## Τι καταγράφεται {#what-is-recorded}

- θάνατοι με θύμα, δολοφόνο, όπλο, τύπο ζημιάς και ζώνη (παίκτες και NPC)
- οχήματα απενεργοποιημένα και καταστραμμένα, με οδηγό, αιτία και ζώνη
- στόχοι quantum travel, αλλαγές ηλιακού συστήματος, εμφανίσεις, επανεμφανίσεις, ανικανοποιήσεις
- κάθε γραμμή του Game.log ολόκληρη στο heat.raw.parquet
- φόνοι (παίκτες και NPC), θάνατοι, αυτοκτονίες, οχήματα καταστραμμένα και χαμένα, quantum jumps

## Από πού προέρχεται {#where-it-comes-from}

&lt;εγκατάσταση>\StarCitizen\LIVE\Game.log (ο φάκελος build του εκτελέσιμου StarCitizen.exe που τρέχει)· μόνο το αρχείο καταγραφής που γράφει το παιχνίδι - είναι παιχνίδι με Easy Anti-Cheat: τίποτα δεν αγγίζει τη διεργασία του

## Πώς το ενεργοποιείτε {#how-to-switch-it-on}

Δεν χρειάζεται να ενεργοποιήσετε τίποτα: ο watcher διαβάζει την πηγή όπως τη δίνει το παιχνίδι ή η πλατφόρμα.

## Πώς λειτουργεί {#how-it-works}

Star Citizen: το δικό του αρχείο καταγραφής του client, `<εγκατάσταση>\StarCitizen\LIVE\Game.log`.

Το παιχνίδι γράφει το Game.log από την αρχή σε κάθε εκκίνηση (το προηγούμενο πηγαίνει στο `logbackups\`). Διαβάζεται μόνο αυτό το αρχείο: το Star Citizen τρέχει το Easy Anti-Cheat, και τίποτα εδώ δεν πλησιάζει τη διεργασία του παιχνιδιού. Οι γραμμές ξεκινούν με μια χρονοσήμανση UTC και ένα επίπεδο, και μετά μια ετικέτα σε γωνιακές αγκύλες:

```text
<2025-04-13T17:17:51.279Z> [Notice] <Actor Death> CActor::Kill: 'Victim' [200146297631] in zone
    'ANVL_Hornet_F7A_Mk2_2677329226210' killed by 'Killer' [202061381370] using
    'GATS_BallisticGatling_S3_2677329225797' [Class unknown] with damage type 'VehicleDestruction'
    from direction x: 0.000000, y: 0.000000, z: 0.000000 [Team_ActorTech][Actor]
<...> [Notice] <Vehicle Destruction> CVehicle::OnAdvanceDestroyLevel: Vehicle 'ANVL_Arrow_123' [123] in zone
    'OOC_Stanton_1_Hurston' [pos x: 1.0, y: 2.0, z: 3.0 vel x: 0, y: 0, z: 0] driven by 'Driver' [456]
    advanced from destroy level 0 to 2 caused by 'Attacker' [789] with 'Combat' [Team_VehicleFeatures][Vehicle]
<...> [Notice] <AccountLoginCharacterStatus_Character> Character: createdAt 1 - updatedAt 2 - geid 3 -
    accountId 4 - name Handle - state STATE_CURRENT [Team_GameServices][Login]
<...> [Notice] <Quantum Navtarget> CSCItemQuantumDrive::RmMulticastOnQTToPoint : Local client user
    Handle[200000000001] received QT data for Entity:AEGS_Gladius_123[123] to Target Stanton1b ...
<...> [Notice] <Changing Solar System> ... Client entity Handle ... changing system from Stanton to Pyro ...
```

(εδώ σπασμένες· στο αρχείο κάθε μία είναι μία γραμμή). Η ζώνη ενός θανάτου είναι συνήθως το όχημα όπου καθόταν το θύμα, όχι ένα μέρος. Η μορφή δεν τεκμηριώνεται από την Cloud Imperium και αλλάζει ανάμεσα στα patches· τα μοτίβα ακολουθούν τις γραμμές που διαβάζουν τα κοινοτικά trackers θανάτων (π.χ. <https://github.com/DimmaDont/all-slain>, MIT - μόνο τα γεγονότα), και ό,τι δεν ταιριάζει παραλείπεται, δεν μαντεύεται. Η `pos` ενός οχήματος είναι σχετική με τη ζώνη και κρατιέται μόνο ως κείμενο: δεν σχεδιάζονται συντεταγμένες.

Κάθε γραμμή κρατιέται ολόκληρη στο ωμό συνοδευτικό της συνεδρίας (κανόνας μετατροπέα του 3DHeat), ταιριάζει ή όχι: το `type` είναι η ετικέτα της γραμμής στις γωνιακές αγκύλες (`Actor Death`, `Spawn Flow`, ...), αλλιώς η πρώτη λέξη της σε αγκύλες (`Notice`, `CSessionManager::OnClientSpawned`), αλλιώς `untagged`· μια γραμμή χωρίς χρονοσήμανση είναι `untimed`.

## Θέσεις και άξονες {#positions-and-axes}

| | |
|---|---|
| Καταγράφονται θέσεις | όχι |
| Άξονας προς τα πάνω | `y` |
| Μονάδες | καμία θέση καταγράφεται |
| Καθρέφτης για τον viewer | κανένας |
| Κλίμακα μονάδας (`scale`: ο viewer πολλαπλασιάζει τις θέσεις με αυτήν) | 1 |

Αυτά μπαίνουν στο `meta.json` (`axes`) κάθε συνεδρίας και, όταν η συνεδρία έχει θέσεις, στο υποσέλιδο του `heat.parquet`, ώστε ο 3DHeat viewer να γυρίζει και να κλιμακώνει τις γραμμές μόνος του - δείτε [Τα δεδομένα](the-data.md).

## Πολλοί παίκτες {#multiplayer}

- Σημειωμένο ως παιγμένο online (`multiplayer`): **ναι**. Η `games --markdown` το δείχνει ως "επιτρέπεται (διαβάζει μόνο ό,τι δημοσιεύει το παιχνίδι)".
- Είδος `log`: διαβάζει μόνο ό,τι δίνει το παιχνίδι ή η πλατφόρμα (αρχεία που γράφει το παιχνίδι όσο τρέχει), άρα καταγράφει και στο online παιχνίδι και offline· η σημαία αποφασίζει μόνο αν επιτρέπεται ποτέ ανάγνωση μνήμης.
- Μνήμη: **ποτέ** δεν διαβάζεται από αυτόν τον προσαρμογέα. Μόνο οι προσαρμογείς `memory` διαβάζουν μνήμη, και ποτέ για παιχνίδι σημειωμένο ως παιγμένο online - δείτε [Πηγές και κανόνες](sources-and-rules.md).

## Στατιστικά που καταγράφονται {#statistics-recorded}

Κλειδιά στατιστικών που ορίζει ο κώδικας αυτού του προσαρμογέα με όνομα (το `stats` κάθε συνεδρίας στο `meta.json` και ο πίνακας `stats` του `watcher.sqlite`):

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

Ένα κλειδί σε αγκύλες συμπληρώνεται κατά την εκτέλεση (το `score.{team}` είναι ένα κλειδί ανά ομάδα). Τα κλειδιά που ο κώδικας τα παίρνει από πίνακα πεδίων του παιχνιδιού ή από τα δικά του ονόματα στατιστικών δεν βρίσκονται σε αυτή τη λίστα· το "Τι καταγράφεται" παραπάνω τα ονομάζει.

## Πληρότητα {#completeness}

Ο watcher ακολουθεί τον [κανόνα μετατροπέα](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) του 3DHeat: ό,τι έχει η πηγή διαβάζεται ή κρατιέται, ποτέ δεν πετιέται. Εκτός από τις γραμμές, κάθε πακέτο, σελίδα, γραμμή ή απάντηση που λαμβάνει ο προσαρμογέας κρατιέται ολόκληρο στο `heat.raw.parquet` της συνεδρίας (στήλες `time`, `ms`, `type`, `used`, `payload`, `text`, και όποιο πεδίο κρατιέται με το όνομά του· το `used` σημαίνει τι έγινε επίσης γραμμές), και το `meta.json` `selfCheck.completeness` μετράει κάθε `type` - το `lost` είναι 0.

**Διαβάζονται**

- `<Actor Death>`: θύμα, δολοφόνος, όπλο και η κλάση του, τύπος ζημιάς, ζώνη· NPC ή παίκτης
- `<Vehicle Destruction>`: όχημα, ζώνη, σχετική θέση ως κείμενο μέσα στη ζώνη, οδηγός, αιτία, τρόπος, επίπεδο καταστροφής
- στόχοι `<Quantum Navtarget>`, `<Changing Solar System>`, `OnClientSpawned`, επανεμφανίσεις στο νοσοκομείο, ανικανοποιήσεις με τις αιτίες τους, `EndSession`
- το αναγνωριστικό του παίκτη (handle) από το `<AccountLoginCharacterStatus_Character>` ή τη γραμμή σύνδεσης

**Κρατιούνται ωμά**

- κάθε γραμμή του Game.log ολόκληρη, `type` = η ετικέτα της σε γωνιακές αγκύλες (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), αλλιώς η πρώτη λέξη της σε αγκύλες (`Notice`, `CSessionManager::OnClientSpawned`, ...), αλλιώς `untagged`· γραμμές χωρίς χρονοσήμανση (η κεφαλίδα του αρχείου, το σπασμένο κείμενο) ως `untimed`· το `used` όπου η γραμμή έγινε γραμμή

**Δεν είναι διαθέσιμα**

- θέσεις: το αρχείο δεν δίνει καμία σε πλαίσιο που μπορεί να σχεδιαστεί (η `pos` ενός καταστραμμένου οχήματος είναι σχετική με μια ζώνη της οποίας η θέση δεν καταγράφεται)
- οτιδήποτε από τη διεργασία ή το δίκτυο του παιχνιδιού: το Star Citizen τρέχει Easy Anti-Cheat· διαβάζεται μόνο το αρχείο καταγραφής
- αρχεία προηγούμενων εκκινήσεων (`logbackups`): το Game.log κάθε εκκίνησης κρατιέται όταν παιχτεί
- γραμμές σε μορφή που αλλάζει ένα patch: κρατιούνται ωμές, και αποκωδικοποιούνται ξανά όταν γίνει γνωστή η νέα μορφή

**Μέγεθος**: το Game.log μεγαλώνει περίπου 5-15 MB την ώρα παιχνιδιού (περισσότερα σε πολυσύχναστες περιοχές και με σφάλματα)· το zstd στο heat.raw.parquet το κάνει περίπου το ένα δέκατο

## Επαλήθευση {#verified}

δοκιμάστηκε σε συνθετικές γραμμές Game.log στη μορφή που τεκμηριώνουν τα κοινοτικά trackers· δεν έχει δοκιμαστεί στο παιχνίδι

## Πηγή {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Δημιουργήθηκε από τον προσαρμογέα με το tools/gen_game_pages.py· αλλάξτε τον προσαρμογέα και τρέξτε το ξανά αντί να επεξεργαστείτε αυτή τη σελίδα. -->
