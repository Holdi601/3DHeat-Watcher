---
title: Συντήρηση των σελίδων
nav_order: 15
lang: "el"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Συντήρηση των σελίδων {#maintaining-these-pages}

Η λίστα ελέγχου για κάθε έκδοση. Οι σελίδες πρέπει να λένε τι κάνει ο κώδικας, να διαβάζονται καλά από αρχάριο, από παιδί 8 χρονών και από επαγγελματία, και να υπάρχουν σε κάθε γλώσσα που υποστηρίζει ο 3DHeat viewer.

## Λίστα ελέγχου έκδοσης {#release-checklist}

1. **Ξαναδημιούργησε τις παραγόμενες σελίδες** από τον κώδικα:

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Πριν από το commit, το ίδιο με `--check` πρέπει να τελειώνει με 0:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Σύγκρινε τις λειτουργίες από την τελευταία έκδοση.** Το `VERSION` κρατά την έκδοση· η ετικέτα της είναι `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Κάθε νέα εντολή, επιλογή, στήλη, έξοδος ή συμπεριφορά παίρνει μια γραμμή στη σελίδα που την καλύπτει, και μια γραμμή στο `CHANGELOG.md` στην ενότητα **Docs** με το όνομα της σελίδας.

3. **Ανεξάρτητος έλεγχος.** Κάποιος που δεν έγραψε την αλλαγή διαβάζει τις αλλαγμένες σελίδες - και τα διαγράμματα και τις εικόνες - τρεις φορές: ως αρχάριος (ποτέ δεν χρησιμοποίησε τερματικό), ως παιδί 8 χρονών (λέει η πρώτη παράγραφος τι είναι και γιατί, με απλά λόγια;) και ως επαγγελματίας (είναι οι σημαίες, οι προεπιλογές και οι στήλες ακριβώς ό,τι κάνει ο κώδικας;).

4. **Διόρθωσε όσα βρήκε ο έλεγχος.** Οι εικόνες μένουν έως περίπου 900 px πλάτος με κείμενο τουλάχιστον 12 px όπως φαίνονται· τα διαγράμματα παράγονται από τα `tools/diagrams/*.json` με το `tools/flow2svg.py`. Τα παραδείγματα χρησιμοποιούν μόνο φτιαχτά ονόματα (`de_x`, "Demo Valley", `<map>`): ποτέ πραγματικό χάρτη, παίκτη, αναγνωριστικό αγώνα ή σχήμα από πραγματικά αρχεία.

5. **Μεταφράσεις.** Κάθε μεταφρασμένη σελίδα καταγράφει τον κατακερματισμό (hash) της αγγλικής πηγής από την οποία έγινε. Μετάφρασε ξανά τις σελίδες όπου αλλάξει ο κατακερματισμός της αγγλικής πηγής, και αφήστε κάθε γλώσσα να την ελέγξει με τους τρεις τρόπους (απλά, για αρχάριο, για επαγγελματία), συμπεριλαμβανομένων των ετικετών στα διαγράμματα.

6. **Η ώθηση μόνο μετά από το πράσινο φως του ιδιοκτήτη.** Κάνε commit τοπικά· ο ιδιοκτήτης αποφασίζει πότε γίνεται δημόσιο.

## Μεταφράσεις: οι εντολές {#translations-the-commands}

Ο ιστότοπος μεταφράζεται στις 40 γλώσσες του 3DHeat viewer: τα αγγλικά βρίσκονται στο `docs/`, κάθε άλλη γλώσσα στο `docs/<lang>/` με τα ίδια ονόματα αρχείων. Το `tools/docs_i18n.py` κάνει τη διαχείριση:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Μετάφραζε μόνο όσα δείχνει το `todo`: κρατήστε το Markdown, τους συνδέσμους, τον κώδικα και τα ονόματα αρχείων και στηλών όπως είναι, μετάφρασε τους τίτλους και τις περιγραφές των εικόνων, και χρησιμοποίησε τις δικές του λέξεις του 3DHeat viewer για τα κουμπιά και τα panels του (από το `src/i18n/locales/<lang>/`). Οι παραγόμενες σελίδες αναφοράς και οι εικόνες του τερματικού μένουν αγγλικές. Στον ιστότοπο, μια παλιά μετάφραση το λέει και συνδέει με την αγγλική σελίδα· μια λείπουσα μετάφραση πέφτει στα αγγλικά. Το μενού γλωσσών της κεφαλίδας και η αυτόματη ανακατεύθυνση της αρχικής σελίδας με βάση τη γλώσσα του περιηγητή προέρχονται από το `docs/_includes/`.
