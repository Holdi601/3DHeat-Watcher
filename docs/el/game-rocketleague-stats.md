---
title: "Rocket League (κατάσταση παιχνιδιού)"
nav_order: 40
lang: "el"
source: game-rocketleague-stats.md
source_hash: "3da6ea772068"
nav_exclude: true
search_exclude: true
---
# Rocket League (κατάσταση παιχνιδιού) {#rocket-league-game-state}

Όσο παίζετε Rocket League, ο watcher αποθηκεύει όσα αναφέρει το παιχνίδι σε προγράμματα του υπολογιστή σας, ώστε να τα δείτε αργότερα σε χάρτη στον 3DHeat viewer.

*Τεχνικές λεπτομέρειες: adapter `rocketleague-stats`, είδος [`gsi`](sources-and-rules.md)· τρέχει όσο εκτελείται το `RocketLeague.exe` και ελέγχει για νέα δεδομένα κάθε 0,05 s.*

## Τι καταγράφεται {#what-is-recorded}

- χτυπήματα της μπάλας με τη θέση της μπάλας (XYZ, μονάδες Unreal), ποιος την χτύπησε και οι ταχύτητες
- γκολ με τη θέση της πρόσκρουσης, σκόρερ, κάνων και ταχύτητα· χτυπήματα της οριζόντιας δοκού με τη θέση
- η ροή στατιστικών (καταστροφές, σώσεις, σουτ, epic saves, ...), κικ-οφ, επαναλήψεις, έναρξη και λήξη αγώνα, νικητής
- τα δικά σας γκολ, ασίστ, σώσεις, σουτ, καταστροφές, επαφές, σκορ και το σκορ των ομάδων, από το UpdateState
- η τελική γραμμή κάθε παίκτη στο τέλος του αγώνα
- οι δικές σας γραμμές ως `me`: ο παίκτης που ορίζετε στις ρυθμίσεις (`config --set player_names.rocketleague-stats=<name>`), αλλιώς αυτός που ακολουθεί η κάμερα του παιχνιδιού εκτός επαναλήψεων
- καμία θέση αυτοκινήτων: το API δεν έχει

## Από πού προέρχεται {#where-it-comes-from}

Stats API: ροή JSON μέσω TCP από 127.0.0.1:49123 (θύρα στο <RL>\TAGame\Config\TAStatsAPI.ini ή DefaultStatsAPI.ini)

## Πώς να το ενεργοποιήσετε {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (βάζει PacketSendRate=30), και μετά ξεκινήστε το Rocket League

Γράψτε την εντολή σε τερματικό που ανοίγει στον φάκελο του watcher (δείτε [Πριν ξεκινήσετε](before-you-start.md)). Αν αποτύχει, η τελευταία γραμμή λέει γιατί· η [Εγκατάσταση και εκτέλεση](installing-and-running.md) καλύπτει τις συνηθισμένες αιτίες.

Η εντολή `python -m heat3d_watch setup rocketleague-stats` δείχνει ποια αρχεία θα άλλαζε· η `python -m heat3d_watch setup rocketleague-stats --apply` τα αλλάζει, κρατώντας το αρχικό ως `<file>.heat3d-backup` (δείτε [Εντολές](commands.md#setup)). Τυπώνει `rocketleague-stats: changed: ...` για κάθε αλλαγή, ή `rocketleague-stats: nothing to change` όταν είναι ήδη ενεργό.

## Πώς λειτουργεί {#how-it-works}

Rocket League: το επίσημο Stats API, μια τοπική υποδοχή στην οποία το παιχνίδι γράφει τα δεδομένα του αγώνα.

Ενεργοποιείται στο `<RL>\TAGame\Config\TAStatsAPI.ini` — ή στο `DefaultStatsAPI.ini` όταν αυτό δεν υπάρχει, που το διαβάζει το παιχνίδι μόνο τότε — στην ενότητα `[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   UpdateState messages per second; 0 (the default) switches the API off, at most 120
Port             the TCP port the game listens on, default 49123 (WebPort 49124 is a WebSocket copy)
```

Το παιχνίδι είναι ο server: ένας πελάτης συνδέεται στο 127.0.0.1:49123 και διαβάζει μια ροή αντικειμένων JSON `{"Event": name, "Data": {...}}` (σε μερικές εκδόσεις το Data έρχεται ως αλφαριθμητικό JSON), το ένα μετά το άλλο χωρίς διαχωριστικά. Τα συμβάντα στέλνονται τη στιγμή που γίνονται, ανεξάρτητα από τον ρυθμό:

```text
UpdateState   MatchGuid, Players[] (Name, PrimaryId, Shortcut, TeamNum 0 blue / 1 orange,
              Score, Goals, Shots, Assists, Saves, Touches, CarTouches, Demos; car state
              only for spectators), Game (Teams[], TimeSeconds, bOvertime, Ball {Speed,
              TeamNum}, bReplay, bHasWinner, Winner, Arena, bHasTarget, Target)
BallHit       Players[] (Name, Shortcut, TeamNum), Ball {PreHitSpeed, PostHitSpeed, Location {X,Y,Z}}
GoalScored    GoalSpeed, GoalTime, ImpactLocation {X,Y,Z}, Scorer, Assister, BallLastTouch
CrossbarHit   BallLocation {X,Y,Z}, BallSpeed, ImpactForce, BallLastTouch
StatfeedEvent EventName, Type, MainTarget, SecondaryTarget
MatchEnded    WinnerTeamNum
MatchCreated, MatchInitialized, CountdownBegin, RoundStarted, GoalReplayStart/WillEnd/End,
MatchPaused/Unpaused, PodiumStart, ReplayCreated, MatchDestroyed, ClockUpdatedSeconds
```

Οι θέσεις είναι σε μονάδες Unreal (εκατοστά), με Z προς τα πάνω· το γήπεδο είναι περίπου 8200 x 10240 με τα τέρματα στο Y = ±5120. Οι θέσεις των αυτοκινήτων δεν είναι μέρος του API: αυτό που έχει τόπο είναι η μπάλα εκεί που χτυπήθηκε, σκοράρισε ή χτύπησε τη δοκό.

Κάθε μήνυμα κρατιέται επίσης ολόκληρο (κανόνας μετατροπέα του 3DHeat, docs/converters.md στο αποθετήριο του viewer): `heat.raw.parquet`, με `type` το όνομα συμβάντος του μηνύματος και `text` το αντικείμενο όπως ήρθε από τη ροή. Ένα UpdateState byte προς byte ίδιο με το προηγούμενο (παύση αγώνα, μενού) κρατιέται μία φορά και μετράται στο `unchanged_replies` του meta.json. Τα μηνύματα ανάμεσα στους αγώνες περιμένουν σε καθυστέρηση για την επόμενη συνεδρία αγώνα· ό,τι μένει όταν κλείσει το παιχνίδι παίρνει συνεδρία δική του. Οι χαρακτήρες ανάμεσα στα αντικείμενα που δεν είναι JSON κρατιούνται ως "junk".

Πηγές: <https://www.rocketleague.com/en/developer/stats-api> (η επίσημη σελίδα)· τα ονόματα πεδίων και η μορφοποίηση TCP επιβεβαιώθηκαν από τον πελάτη rlstatsapi (<https://docs.rs/crate/rlstatsapi>, MIT· διαβάστηκε μόνο για τα δεδομένα του).

## Θέσεις και άξονες {#positions-and-axes}

| | |
|---|---|
| Καταγράφονται θέσεις | ναι |
| Άξονας προς τα πάνω | `z` |
| Μονάδες | μονάδες Unreal (εκατοστά) |
| Καθρέφτισμα για τον viewer | κανένα |
| Κλίμακα μονάδας (`scale`: ο viewer πολλαπλασιάζει τις θέσεις με αυτήν) | 1 |

Αυτά μπαίνουν στο `meta.json` (`axes`) κάθε συνεδρίας και, όταν η συνεδρία έχει θέσεις, στο footer του `heat.parquet`, ώστε ο viewer του 3DHeat να γυρίζει και να κλιμακώνει τις γραμμές μόνος του — δείτε [Τα δεδομένα](the-data.md).

## Πολλαπλός παίκτης {#multiplayer}

- Σημειωμένο ως παιγμένο online (`multiplayer`): **ναι**. Η `games --markdown` το εμφανίζει ως "allowed (reads only what the game publishes)".
- Είδος `gsi`: διαβάζει μόνο όσα δίνει το παιχνίδι ή η πλατφόρμα (ένα game-state integration ή τοπικό API που σερβίρει το παιχνίδι), άρα καταγράφει και στο online παιχνίδι και offline· η σήμανση αποφασίζει μόνο αν επιτρέπεται ποτέ η ανάγνωση μνήμης.
- Μνήμη: **ποτέ** δεν διαβάζεται από αυτόν τον adapter. Μόνο οι adapters `memory` διαβάζουν μνήμη, και ποτέ για παιχνίδι σημειωμένο ως παιγμένο online — δείτε [Πηγές και κανόνες](sources-and-rules.md).

## Στατιστικά που καταγράφονται {#statistics-recorded}

Κλειδιά στατιστικών που ορίζει ο κώδικας του adapter με το όνομά τους (το `stats` κάθε συνεδρίας στο `meta.json` και ο πίνακας `stats` του `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

Ένα κλειδί σε αγκύλες συμπληρώνεται κατά τον χρόνο εκτέλεσης (το `score.{team}` είναι ένα κλειδί ανά ομάδα). Τα κλειδιά που ο κώδικας παίρνει από πίνακα πεδίων του παιχνιδιού ή από τα δικά του ονόματα στατιστικών δεν είναι σε αυτή τη λίστα· το "Τι καταγράφεται" παραπάνω τα ονομάζει.

## Πληρότητα {#completeness}

Ο watcher ακολουθεί τον [κανόνα μετατροπέα](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) του 3DHeat: ό,τι έχει η πηγή διαβάζεται ή κρατιέται, ποτέ δεν πετιέται. Εκτός από τις γραμμές, κάθε πακέτο, σελίδα, γραμμή ή απάντηση που λαμβάνει ο adapter κρατιέται ολόκληρο στο `heat.raw.parquet` της συνεδρίας (στήλες `time`, `ms`, `type`, `used`, `payload`, `text`, και όποιο πεδίο κρατιέται με το όνομά του· το `used` σημαδεύει ό,τι έγινε και γραμμές), και το `selfCheck.completeness` του `meta.json` μετρά κάθε `type` — το `lost` είναι 0.

**Διαβάζεται**

- BallHit (θέση, ποιος, ομάδα, ταχύτητες πριν και μετά), GoalScored (θέση πρόσκρουσης, σκόρερ, κάνων, ταχύτητα, χρόνος γκολ), CrossbarHit (θέση, τελευταία επαφή, ταχύτητα, δύναμη), StatfeedEvent (συμβάν, είδος, κύριος και δευτερεύων στόχος), MatchEnded (νικητής, αποτέλεσμα)· το όνομα κάθε άλλου συμβάντος ως γραμμή
- από το UpdateState: η αρένα, ο στόχος της κάμερας εκτός επαναλήψεων (ποιος είναι το `me`), τα σκορ των ομάδων, τα γκολ, οι ασίστ, οι σώσεις, τα σουτ, οι καταστροφές, οι επαφές και τα σκορ κάθε παίκτη (τα δικά σας ως στατιστικά, όλων ως `player_result` στο τέλος του αγώνα)· η παράταση από το ClockUpdatedSeconds

**Κρατιέται ως έχει**

- κάθε μήνυμα ολόκληρο όπως ήρθε από τη ροή (`text`), κάτω από το δικό του όνομα συμβάντος: `UpdateState` (το PrimaryId και το Shortcut κάθε παίκτη, το ρολόι, η ταχύτητα της μπάλας και η ομάδα της, τα ονόματα και τα χρώματα των ομάδων, οι σημαίες επαναλήψεων και νικητή, και η κατάσταση αυτοκινήτου όπου τη στέλνει το παιχνίδι), `BallHit`, `GoalScored` (με την τελευταία επαφή της μπάλας), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` και κάθε συμβάν που προσθέτει κάποια μεταγενέστερη έκδοση
- ένα UpdateState byte προς byte ίδιο με το προηγούμενο (παύση, μενού) κρατιέται μία φορά και μετράται (`unchanged_replies` στο meta.json)
- μηνύματα ανάμεσα στους αγώνες: στη δική τους ώρα πριν την έναρξη του επόμενου αγώνα· μετά τον τελευταίο αγώνα, σε δική τους συνεδρία (`raw_only` στο meta.json)
- `unreadable`: ένα αντικείμενο που δεν είναι μήνυμα του Stats API· `junk`: χαρακτήρες ανάμεσα σε αντικείμενα

**Δεν είναι διαθέσιμα**

- θέσεις αυτοκινήτων και κατάσταση αυτοκινήτου όσο παίζετε: το παιχνίδι τα στέλνει μόνο στους θεατές
- UpdateState ανάμεσα σε δύο αποστολές: το παιχνίδι στέλνει PacketSendRate φορές το δευτερόλεπτο (το `setup` βάζει 30, το παιχνίδι επιτρέπει έως 120)· τα συμβάντα στέλνονται τη στιγμή που γίνονται
- το αντίγραφο WebSocket στο WebPort (49124): τα ίδια μηνύματα με τη θύρα TCP, δεν διαβάζονται δύο φορές

**Μέγεθος**: ένα UpdateState είναι 1-3 KB για έξι παίκτες, 30 το δευτερόλεπτο· περίπου 100-300 MB την ώρα στο `raw.bin` όσο τρέχει αγώνας, ένα δέκατο ή λιγότερο στο zstd `heat.raw.parquet` (εκτίμηση από τη δημοσιευμένη μορφή, δεν έχει μετρηθεί στο παιχνίδι)

## Επαλήθευση {#verified}

δοκιμάστηκε σε μηνύματα στη δημοσιευμένη μορφή, που έστελνε ένας ψεύτικος τοπικός server· δεν έχει δοκιμαστεί με το ίδιο το παιχνίδι

## Πηγή {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Δημιουργήθηκε από τον adapter με το tools/gen_game_pages.py· αλλάξτε τον adapter και τρέξτε ξανά το εργαλείο, αντί να επεξεργάζεστε αυτή τη σελίδα. -->
