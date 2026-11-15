---
title: "Поддръжка на страниците"
nav_order: 15
lang: "bg"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Поддръжка на тези страници {#maintaining-these-pages}

Списъкът за проверка при всяко издание. Страниците трябва да казват какво прави кодът, да се четат добре от начинаещ, от 8-годишно дете и от професионалист, и да съществуват на всеки език, който поддържа визуализаторът на 3DHeat.

## Списък за издание {#release-checklist}

1. **Регенерирайте създадените от кода страници**:

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Преди подаване на промените същото с `--check` трябва да завърши с код 0:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Сравнете функциите от последното издание.** `VERSION` съдържа версията; етикетът ѝ е `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Всяка нова команда, опция, колона, изход или поведение получава ред на страницата, която го описва, и ред в `CHANGELOG.md` под **Docs**, който назовава страницата.

3. **Независим преглед.** Някой, който не е писал промяната, прочита променените страници - включително диаграмите и картинките - три пъти: като начинаещ (никога не е ползвал терминал), като 8-годишно дете (първият параграф казва ли какво е и защо, с прости думи?) и като професионалист (флаговете, стойностите по подразбиране и колоните съвпадат ли точно с това, което прави кодът).

4. **Поправете какво е открил прегледът.** Картинките остават най-много около 900 px широки, с текст поне 12 px, както са показани; диаграмите се създават от `tools/diagrams/*.json` с `tools/flow2svg.py`. Примерите използват само измислени имена (`de_x`, "Demo Valley", `<map>`): никога реална карта, играч, идентификатор на мач или фигура от истински файлове.

5. **Преводи.** Всяка преведена страница записва хеша на английския източник, от който е направена. Преведете отново страниците, чийто английски хеш се е променил, и после всеки език се преглежда по същите три начина (прост, за начинаещ, за професионалист), включително етикетите на диаграмите.

6. **Публикувайте само след одобрение от собственика.** Подавайте локално; собственикът решава кога става публично.

## Преводите: командите {#translations-the-commands}

Сайтът е преведен на 40-те езика, които поддържа визуализаторът на 3DHeat: английският е в `docs/`, всеки друг език - в `docs/<lang>/` със същите имена на файлове. `tools/docs_i18n.py` води записите:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Превеждайте само това, което показва `todo`: запазвайте Markdown, връзките, кода, имената на файлове и колоните; превеждайте заглавията и описанията на картинките, и използвайте собствените думи на визуализатора на 3DHeat за бутоните и панелите му (неговите `src/i18n/locales/<lang>/`). Създадените референтни страници и терминалните картинки остават на английски. В сайта превод, който е остарял, го казва и сочи английската страница; липсващият превод пада обратно към английския. Менюто за езици в горната част и пренасочването по езика на браузъра на началната страница идват от `docs/_includes/`.
