---
title: "Maintenance de ces pages"
nav_order: 15
lang: "fr"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Maintenance de ces pages {#maintaining-these-pages}

La liste de contrôle de chaque version. Les pages doivent dire ce que fait le code, se lire bien pour un débutant, un
enfant de 8 ans et un pro, et exister dans toutes les langues que le viewer 3DHeat prend en charge.

## Liste de contrôle de version {#release-checklist}

1. **Régénérer les pages générées** à partir du code :

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Avant de valider, les mêmes commandes avec `--check` doivent se terminer par 0 :

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Comparer les fonctions depuis la dernière version.** `VERSION` contient la version ; son étiquette est `v<VERSION>` :

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Chaque nouvelle commande, option, colonne, sortie ou comportement reçoit une ligne sur la page qui le couvre, et une
   ligne dans `CHANGELOG.md` sous **Docs** qui nomme cette page.

3. **Relecture indépendante.** Quelqu'un qui n'a pas écrit la modification lit les pages modifiées - schémas et
   images compris - trois fois : en débutant (n'a jamais utilisé de terminal), en enfant de 8 ans (le
   premier paragraphe dit-il ce que c'est et pourquoi, en mots simples ?) et en pro (les options, valeurs par défaut et
   colonnes sont-elles exactement ce que fait le code ?).

4. **Corriger ce que la relecture a trouvé.** Les images restent à environ 900 px de large au plus, avec un texte d'au moins 12 px
   tel qu'affiché ; les schémas sont générés à partir de `tools/diagrams/*.json` avec `tools/flow2svg.py`. Les exemples n'utilisent
   que des noms inventés (`de_x`, « Demo Valley », `<map>`) : jamais une vraie carte, un vrai joueur, un identifiant de match ou un chiffre
   tiré de vrais fichiers.

5. **Traductions.** Chaque page traduite garde le hash de la source anglaise dont elle vient.
   Retraduisez les pages dont le hash de la source anglaise a changé, puis faites relire chaque langue des trois mêmes
   façons (simple, débutant, pro), étiquettes de schéma comprises.

6. **Ne publier qu'après l'accord du propriétaire.** Validez en local ; le propriétaire décide quand cela devient public.

## Traductions : les commandes {#translations-the-commands}

Le site est traduit dans les 40 langues du viewer 3DHeat : l'anglais dans `docs/`, chaque autre
langue dans `docs/<lang>/` avec les mêmes noms de fichiers. `tools/docs_i18n.py` tient la comptabilité :

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Ne traduisez que ce que `todo` liste : gardez le Markdown, les liens, le code, les noms de fichiers et de colonnes tels quels,
traduisez les titres et les descriptions d'images, et utilisez les mots propres au viewer 3DHeat pour ses boutons
et ses panneaux (son dossier `src/i18n/locales/<lang>/`). Les pages de référence générées et les images de terminal restent
en anglais. Sur le site, une traduction périmée le dit et renvoie vers la page anglaise ; une page manquante
retombe sur l'anglais. Le menu de langue de l'en-tête et la redirection de la page d'accueil selon la langue du navigateur
viennent de `docs/_includes/`.
