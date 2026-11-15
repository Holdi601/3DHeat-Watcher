---
title: Одржување
nav_order: 15
lang: "mk"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Одржување на овие страници {#maintaining-these-pages}

Списокот за проверка за секое издание. Страниците мора да кажуваат што прави кодот, да се читаат добро за почетник, за
8-годишно дете и за професионалец, и да постојат на секој јазик што го поддржува прегледувачот 3DHeat.

## Список за проверка на изданието {#release-checklist}

1. **Регенерирајте ги генерираните страници** од кодот:

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Пред commit, истото со `--check` мора да излезе со 0:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Споредете ги функциите од последното издание.** `VERSION` ја содржи верзијата; нејзиниот таг е `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Секоја нова команда, опција, колона, излез или однесување добива линија на страницата што го опфаќа, и
   линија во `CHANGELOG.md` под **Docs** што ја именува таа страница.

3. **Независен преглед.** Некој што не ја пишувал промената ги чита променетите страници - дијаграмите и
   сликите вклучени - трипати: како почетник (никогаш не користел терминал), како 8-годишно дете (дали
   првиот став кажува што е и зошто, со прости зборови?) и како професионалец (дали флаговите, стандардните вредности и
   колоните се точно она што го прави кодот?).

4. **Поправете го она што го нашол прегледот.** Сликите остануваат најмногу околу 900 px широки со текст од најмалку 12 px
   како што се прикажани; дијаграмите се генерираат од `tools/diagrams/*.json` со `tools/flow2svg.py`. Примерите користат
   само измислени имиња (`de_x`, „Demo Valley“, `<map>`): никогаш вистинска мапа, играч, id на натпревар или бројка
   од вистински датотеки.

5. **Преводи.** Секоја преведена страница го запишува хешот на англискиот извор од кој е направена.
   Повторно преведете ги страниците чиј хеш на англискиот извор се променил, па секој јазик прегледајте го на истите
   три начини (едноставно, почетник, професионалец), вклучително и ознаките на дијаграмите.

6. **Објавувајте дури по одобрување од сопственикот.** Направете commit локално; сопственикот одлучува кога ќе стане јавно.

## Преводи: командите {#translations-the-commands}

Страницата е преведена на 40-те јазици на прегледувачот 3DHeat: англискиот во `docs/`, секој друг
јазик во `docs/<lang>/` со исти имиња на датотеки. `tools/docs_i18n.py` ја води евиденцијата:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Преведувајте само она што го наведува `todo`: Markdown, врските, кодот, имињата на датотеки и колони оставете ги како што се,
преведете ги насловите и описите на сликите, и користете ги зборовите на самиот прегледувач 3DHeat за неговите копчиња
и панели (неговиот `src/i18n/locales/<lang>/`). Генерираните референтни страници и сликите од терминал остануваат
на англиски. На страницата, застарен превод тоа го кажува и ја поврзува англиската страница; недостасувачки
се враќа на англиски. Менито за јазик во заглавието и пренасочувањето на почетната страница според јазикот на прегледувачот
доаѓаат од `docs/_includes/`.
