---
title: "Hearthstone (αρχεία καταγραφής)"
nav_order: 25
lang: "el"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (αρχεία καταγραφής) {#hearthstone-log-files}

Όσο παίζετε Hearthstone, ο watcher διαβάζει τα αρχεία που γράφει το παιχνίδι και αποθηκεύει τι συνέβη, ώστε να το δείτε αργότερα ως στατιστικά και χρονολόγιο.

*Τεχνικές λεπτομέρειες: προσαρμογέας `hearthstone`, είδος [`log`](sources-and-rules.md)· τρέχει όσο τρέχει το `Hearthstone.exe` και ελέγχει για νέα δεδομένα κάθε 0,5 s.*

## Τι καταγράφεται {#what-is-recorded}

- έναρξη και τέλος παιχνιδιού, με το αποτέλεσμα (νίκη, ήττα, ισοπαλία), τις γύρους και το όνομα του αντιπάλου
- κάθε γύρος
- κάθε γραμμή του Power.log και των άλλων logs ολόκληρη στο heat.raw.parquet
- παιχνίδια, νίκες, ήττες, ισοπαλίες, γύροι, μεγαλύτερο παιχνίδι

## Από πού προέρχεται {#where-it-comes-from}

&lt;εγκατάσταση>\Logs\Power.log (ή Logs\Hearthstone_\*\Power.log), αφού το %LOCALAPPDATA%\Blizzard\Hearthstone\log.config έχει ενότητα [Power], και κάθε άλλο \*.log που γράφει το παιχνίδι εκεί

## Πώς το ενεργοποιείτε {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` προσθέτει καταγραφή [Power] στο %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (κρατιέται αντίγραφο)· ξεκινήστε ξανά το παιχνίδι

Πληκτρολογήστε την εντολή σε τερματικό ανοιχτό στον φάκελο του watcher (δείτε [Πριν ξεκινήσετε](before-you-start.md)). Αν αποτύχει, η τελευταία γραμμή λέει γιατί· το [Εγκατάσταση και εκτέλεση](installing-and-running.md) καλύπτει τις συνηθισμένες αιτίες.

`python -m heat3d_watch setup hearthstone` δείχνει ποια αρχεία θα άλλαζε· `python -m heat3d_watch setup hearthstone --apply` τα αλλάζει, κρατώντας το αρχικό ως `<αρχείο>.heat3d-backup` (δείτε [Εντολές](commands.md#setup)). Τυπώνει `hearthstone: changed: ...` για κάθε αλλαγή, ή `hearthstone: nothing to change` όταν είναι ήδη ενεργό.

## Πώς λειτουργεί {#how-it-works}

Hearthstone: το Power.log του παιχνιδιού, που γράφεται μόλις το `log.config` το ζητήσει.

Το Hearthstone διαβάζει το `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` κατά την εκκίνηση· μια ενότητα `[Power]` με `LogLevel=1` και `FilePrinting=true` κάνει να γράφει κάθε αλλαγή κατάστασης κάθε παιχνιδιού στο `<εγκατάσταση>\Logs\Power.log` (οι νεότεροι clients βάζουν τα logs κάθε εκκίνησης σε δικό τους φάκελο, `Logs\Hearthstone_<ημερομηνία>\`). Είναι η τεκμηριωμένη καταγραφή αποσφαλμάτωσης που χρησιμοποιούν οι trackers τράπουλας από το 2014 (η ρύθμιση του Hearthstone Deck Tracker γράφει την ίδια ενότητα). Η `setup()` προσθέτει την ενότητα, με αντίγραφο του αρχείου όπως ήταν· το παιχνίδι χρειάζεται επανεκκίνηση για να τη διαβάσει.

Οι γραμμές που χρησιμοποιούνται, όλες από το `GameState.DebugPrintPower()` (οι γραμμές `PowerTaskList` τις επαναλαμβάνουν και παραλείπονται):

```text
D 20:15:01.1234567 GameState.DebugPrintPower() - CREATE_GAME
D 20:15:01.1234567 GameState.DebugPrintPower() -     Player EntityID=2 PlayerID=1 GameAccountId=[hi=1 lo=2]
D 20:15:01.1234567 GameState.DebugPrintGame() - PlayerID=1, PlayerName=Name#1234
D 20:15:02.1234567 GameState.DebugPrintPower() -     FULL_ENTITY - Updating [entityName=... id=4 zone=HAND
                   zonePos=0 cardId=CS2_029 player=1] CardID=CS2_029
D 20:16:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=TURN value=3
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=Name#1234 tag=PLAYSTATE value=WON
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=STATE value=COMPLETE
```

Η πλευρά του παίκτη είναι εκείνη της οποίας οι κάρτες της αρχικής χειρός έχουν ονόματα (των αντιπάλων κρύβονται), αλλιώς η πλευρά που δεν είναι το AI (λογαριασμός 0) ή το "UNKNOWN HUMAN PLAYER". Οι γραμμές φέρουν μόνο την ώρα της ημέρας· η ημερομηνία είναι η σημερινή. Καμία θέση.

Κάθε γραμμή του Power.log κρατιέται ολόκληρη στο ωμό συνοδευτικό της συνεδρίας (κανόνας μετατροπέα του 3DHeat), μαζί με τις επαναλήψεις του `PowerTaskList`, τις επιλογές, τα choices και τις ενημερώσεις οντοτήτων: το `type` είναι η μέθοδος που την έγραψε (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Κάθε άλλο log που γράφει το παιχνίδι δίπλα του - `LoadingScreen.log`, `Decks.log`, `Zone.log`, `Arena.log`, ..., το καθένα όταν το ζητά το log.config (τα trackers τράπουλας συχνά το κάνουν) - παρακολουθείται με τον ίδιο τρόπο και κρατιέται με το όνομά του στο `log`.

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

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

Ένα κλειδί σε αγκύλες συμπληρώνεται κατά την εκτέλεση (το `score.{team}` είναι ένα κλειδί ανά ομάδα). Τα κλειδιά που ο κώδικας τα παίρνει από πίνακα πεδίων του παιχνιδιού ή από τα δικά του ονόματα στατιστικών δεν βρίσκονται σε αυτή τη λίστα· το "Τι καταγράφεται" παραπάνω τα ονομάζει.

## Πληρότητα {#completeness}

Ο watcher ακολουθεί τον [κανόνα μετατροπέα](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) του 3DHeat: ό,τι έχει η πηγή διαβάζεται ή κρατιέται, ποτέ δεν πετιέται. Εκτός από τις γραμμές, κάθε πακέτο, σελίδα, γραμμή ή απάντηση που λαμβάνει ο προσαρμογέας κρατιέται ολόκληρο στο `heat.raw.parquet` της συνεδρίας (στήλες `time`, `ms`, `type`, `used`, `payload`, `text`, και όποιο πεδίο κρατιέται με το όνομά του· το `used` σημαίνει τι έγινε επίσης γραμμές), και το `meta.json` `selfCheck.completeness` μετράει κάθε `type` - το `lost` είναι 0.

**Διαβάζονται**

- `CREATE_GAME`, οι παίκτες (οντότητα, αναγνωριστικό παίκτη, λογαριασμός· ο λογαριασμός 0 είναι το AI) και τα ονόματά τους (`DebugPrintGame`)
- ποια πλευρά είναι του παίκτη, από τις ονομασμένες κάρτες της αρχικής χειρός
- `TAG_CHANGE` των TURN, PLAYSTATE (won, lost, tied) και STATE COMPLETE: γύροι, αποτέλεσμα, αντίπαλος

**Κρατιούνται ωμά**

- κάθε γραμμή του Power.log ολόκληρη, `type` = η μέθοδος που την έγραψε (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` όπου έγινε γραμμή: κάθε κάρτα που παίχτηκε, τραβήχτηκε και αποκαλύφθηκε, κάθε αλλαγή tag, επίθεση, επιλογή και choice είναι εδώ, ακόμα όχι σε γραμμές
- κάθε γραμμή των άλλων logs στον ίδιο φάκελο (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... - όσα ανοίγει το log.config), με τα ίδια `type`, με το όνομα του log στο `log`
- γραμμή χωρίς επίπεδο και ώρα ημέρας ως `untimed`, χωρίς μέθοδο ως `untagged`

**Δεν είναι διαθέσιμα**

- θέσεις: ένα παιχνίδι με κάρτες δεν έχει
- οι κρυφές κάρτες του αντιπάλου: το log ονομάζει μια κάρτα μόνο αφού αποκαλυφθεί
- logs που δεν ανοίγει το log.config: το `setup` ζητά μόνο το [Power]· τα άλλα έρχονται όταν ένα άλλο εργαλείο (tracker τράπουλας) τα έχει ανοίξει
- logs προηγούμενων εκκινήσεων: κάθε εκκίνηση γράφει νέο φάκελο· όσα είναι παλαιότερα από αυτή την εκτέλεση του παιχνιδιού δεν ξαναδιαβάζονται

**Μέγεθος**: το Power.log με Verbose είναι 1-5 MB ανά παιχνίδι, 10-40 MB την ώρα παιχνιδιού· τα άλλα logs προσθέτουν λίγα· το zstd στο heat.raw.parquet τα κάνει περίπου το ένα δέκατο ή λιγότερο (οι γραμμές επαναλαμβάνονται πολύ)

## Επαλήθευση {#verified}

δοκιμάστηκε σε συνθετικές γραμμές Power.log στη μορφή του παιχνιδιού· δεν έχει δοκιμαστεί στο παιχνίδι

## Πηγή {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Δημιουργήθηκε από τον προσαρμογέα με το tools/gen_game_pages.py· αλλάξτε τον προσαρμογέα και τρέξτε το ξανά αντί να επεξεργαστείτε αυτή τη σελίδα. -->
