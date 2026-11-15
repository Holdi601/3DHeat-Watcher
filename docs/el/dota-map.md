---
title: "Χάρτης Dota 2"
nav_order: 6.5
lang: "el"
source: dota-map.md
source_hash: "3dcde11c7784"
nav_exclude: true
search_exclude: true
---
# Ο χάρτης του Dota 2 ως πίστα (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

Ο χάρτης του Dota 2 σε τρεις διαστάσεις - έδαφος, γκρεμοί, νερό, κάθε δέντρο και τα κτίρια, στο πλαίσιο και στις μονάδες
στα οποία σχεδιάζονται οι [πίνακες replay του Dota 2](game-dota-replays.md) - φτιάχνεται από το δικό του εργαλείο,
το **3DHeat Dota** ([3DHeat-Ext-Dota](https://github.com/Holdi601/3DHeat-Ext-Dota),
[τεκμηρίωση](https://holdi601.github.io/3DHeat-Ext-Dota/)). Διαβάζει τα αρχεία παιχνιδιού της Valve, γι' αυτό
βρίσκεται έξω από τον watcher: αν χρειαστεί ποτέ να αφαιρεθεί, ο watcher μένει.

Εγκαταστήστε το μία φορά, όπως λέει η σελίδα του [Πριν ξεκινήσετε](https://holdi601.github.io/3DHeat-Ext-Dota/before-you-start.html)
του (πακέτο Python, και η γραμμή εντολών του Source2Viewer). Μετά, είτε

```bash
heat3d-dota-maps level -o dota.glb
```

είτε, μέσω του watcher,

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

που τρέχει το `heat3d-dota-maps level` με τις ίδιες επιλογές και περνά στην έξοδό του και τον κωδικό εξόδου του.
Ο watcher βρίσκει το εργαλείο ως την εντολή `heat3d-dota-maps` στο `PATH`, ως το εγκατεστημένο πακέτο
`heat3d_ext_dota`, ή ως τον φάκελο του κώδικά του στο `HEAT3D_DOTA_MAPS` ή δίπλα στον watcher (`exporters/ext/dota-maps`
σε ένα αντίγραφο του 3DHeat). Δεν εισάγεται τίποτα από αυτό στον watcher· απλώς εκτελείται. Όταν δεν βρίσκεται πουθενά,
το `dota-map` λέει πού να το κατεβάσετε και τερματίζει με κωδικό εξόδου 2.

Φορτώστε το `.glb` στο πάνελ **Φόντο / πίστα** του προβολέα (**3D μοντέλο…**) κάτω από έναν πίνακα του Dota: ο προβολέας
αναγνωρίζει το αρχείο από τα μέρη του, το κρατά στη βιβλιοθήκη πιστών του, και από εκεί και πέρα το κουμπί του **Χάρτη Dota 2**
το φορτώνει. Πώς φτιάχνεται η πίστα, τα μέρη της και πώς ελέγχθηκε:
[Δημιουργία πίστας](https://holdi601.github.io/3DHeat-Ext-Dota/level.html).
