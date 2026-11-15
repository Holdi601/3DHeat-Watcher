---
title: Перш ніж почати
nav_order: 2
lang: uk
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Перш ніж почати {#before-you-start}

Ви лише починаєте працювати з командним рядком? Ця сторінка проведе вас від нуля до робочого
3DHeat Watcher приблизно за десять хвилин. Ви вводите команди в *термінал* - вікно, де ви пишете
рядок і натискаєте Enter.

## 1. Встановіть Python {#install-python}

1. Завантажте Python 3.10 або новіший з <https://www.python.org/downloads/>.
2. Запустіть інсталятор. На першому екрані позначте **Add python.exe to PATH**,
   потім натисніть **Install Now**.
3. Перевірте: відкрийте термінал (крок 3) і введіть `python --version`. Ви маєте побачити
   `Python 3.` і число 10 або більше.

У Linux або macOS Python зазвичай уже встановлено: там, де ці сторінки пишуть `python`, використовуйте
`python3`.

## 2. Отримайте 3DHeat Watcher {#get-3dheat-watcher}

Завантажте zip зі
[сторінки випусків](https://github.com/Holdi601/3DHeat-Watcher/releases) і розпакуйте його, наприклад,
у `C:\Tools\3DHeat-Watcher`. (Якщо у вас є Git, підійде й `git clone`.)

## 3. Відкрийте термінал у цій папці {#open-a-terminal-in-that-folder}

- **Windows:** відкрийте папку в Провіднику файлів, клацніть рядок адреси, введіть
  `powershell` і натисніть Enter. Відкриється синє або чорне вікно, вже в цій папці.
- **macOS / Linux:** відкрийте *Terminal* і введіть `cd ` (з пробілом), перетягніть папку
  у вікно і натисніть Enter.

`cd <folder>` переміщує термінал в іншу папку. Усі команди на цих сторінках вводяться в папці
самого інструмента.

## 4. Встановіть те, що йому потрібно {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Наприкінці ви маєте побачити `Successfully installed ...` (або `Requirement
already satisfied`).

## 5. Перевірте, що він працює {#check-it-works}

```bash
python -m heat3d_watch --version
```

Ви маєте побачити: `1.0.2 (the version number)`.

## Як читати команди на цих сторінках {#how-to-read-the-commands-on-these-pages}

- Слова в `<кутових дужках>` - це заповнювачі: введіть замість них власний файл або папку, без
  дужок. `python -m heat3d_watch sessions --game <name>` означає, що ви замінюєте частину в дужках.
- Шлях із пробілами береться в лапки: `"C:\My Games\my file"`.
- Рядки, що починаються з `#` у прикладах, - це коментарі; їх не вводять.
- Успіх виглядає так: після `python -m heat3d_watch games` - таблиця з одним рядком на кожну гру.

## Поширені помилки {#common-errors}

| Ви бачите | Що робити |
|---|---|
| `'python' is not recognized` або `command not found` | Python немає в PATH: запустіть інсталятор знову і позначте **Add python.exe to PATH**, потім відкрийте новий термінал. На macOS/Linux спробуйте `python3`. |
| `No module named ...` | крок 4 пропущено або виконано в іншій папці: виконайте `cd` до папки інструмента і запустіть знову. |
| `pip is not recognized` | використовуйте `python -m pip ...` замість `pip ...`. |
| `No such file or directory` / `can't open file` | термінал у неправильній папці або шлях написано з помилкою: перевірте його і візьміть шляхи з пробілами в лапки. |
| червоний текст, що закінчується рядком `error:` | прочитайте останній рядок: там сказано, чого бракує. На сторінці [Команди](../commands.md) перелічено повідомлення. |
