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
