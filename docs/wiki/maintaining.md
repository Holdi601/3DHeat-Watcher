# Maintaining these pages

The checklist for every release. The pages must say what the code does, read well for a beginner, an
8-year-old and a pro, and exist in every language the 3DHeat viewer supports.

## Release checklist

1. **Regenerate the generated pages** from the code:

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Before committing, the same with `--check` must exit with 0:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Diff the features since the last release.** `VERSION` holds the version; its tag is `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Every new command, option, column, output or behaviour gets a line on the page that covers it, and a
   line in `CHANGELOG.md` under **Docs** naming that page.

3. **Independent review.** Someone who did not write the change reads the changed pages - diagrams and
   pictures included - three times: as a beginner (never used a terminal), as an 8-year-old (does the
   first paragraph say what it is and why, in plain words?) and as a pro (are flags, defaults and
   columns exactly what the code does?).

4. **Fix what the review found.** Pictures stay at most about 900 px wide with text of at least 12 px
   as shown; diagrams are generated from `tools/diagrams/*.json` with `tools/flow2svg.py`. Examples use
   made-up names only (`de_x`, "Demo Valley", `<map>`): never a real map, player, match id or figure
   from real files.

5. **Translations.** Each translated page records the hash of the English source it was made from.
   Re-translate the pages whose English source hash changed, then have each language reviewed the same
   three ways (plain, beginner, pro), including the diagram labels.

6. **Push only after the owner's go-ahead.** Commit locally; the owner decides when it goes public.

## Translations: the commands

The site is translated into the 3DHeat viewer's 40 languages: English in `docs/`, each other
language in `docs/<lang>/` with the same file names. `tools/docs_i18n.py` does the bookkeeping:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Translate only what `todo` lists: keep Markdown, links, code, file and column names as they are,
translate titles and picture descriptions, and use the 3DHeat viewer's own words for its buttons
and panels (its `src/i18n/locales/<lang>/`). Generated reference pages and terminal pictures stay
English. On the site, an outdated translation says so and links the English page; a missing one
falls back to English. The header's language menu and the home page's browser-language redirect
come from `docs/_includes/`.
