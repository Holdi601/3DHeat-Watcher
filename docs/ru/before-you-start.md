---
title: С чего начать
nav_order: 2
lang: ru
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# С чего начать {#before-you-start}

Впервые в командной строке? Эта страница проведёт вас от нуля до работающего 3DHeat Watcher примерно
за десять минут. Вы вводите команды в *терминал* — окно, в котором вы пишете строку и нажимаете Enter.

## 1. Установите Python {#install-python}

1. Скачайте Python 3.10 или новее с <https://www.python.org/downloads/>.
2. Запустите установщик. На первом экране отметьте **Add python.exe to PATH**, затем нажмите
   **Install Now**.
3. Проверьте: откройте терминал (шаг 3) и введите `python --version`. Вы должны увидеть
   `Python 3.` и число 10 или больше.

В Linux или macOS Python обычно уже установлен: используйте `python3` там, где эти страницы пишут `python`.

## 2. Получите 3DHeat Watcher {#get-3dheat-watcher}

Скачайте zip со [страницы релизов](https://github.com/Holdi601/3DHeat-Watcher/releases) и распакуйте
его, например, в `C:\Tools\3DHeat-Watcher`. (Если у вас есть Git, подойдёт и `git clone`.)

## 3. Откройте терминал в этой папке {#open-a-terminal-in-that-folder}

- **Windows:** откройте папку в Проводнике, щёлкните в адресной строке, введите `powershell` и нажмите
  Enter. Откроется синее или чёрное окно, уже в этой папке.
- **macOS / Linux:** откройте *Terminal* и введите `cd ` (с пробелом), перетащите папку в окно и
  нажмите Enter.

`cd <folder>` переводит терминал в другую папку. Все команды на этих страницах вводятся в папке самого
инструмента.

## 4. Установите то, что ему нужно {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

В конце вы должны увидеть `Successfully installed ...` (или `Requirement already satisfied`).

## 5. Проверьте, что всё работает {#check-it-works}

```bash
python -m heat3d_watch --version
```

Вы должны увидеть номер версии, например `1.0.2`.

## Как читать команды на этих страницах {#how-to-read-the-commands-on-these-pages}

- Слова в `<угловых скобках>` — заполнители: вместо них введите свой файл или папку, без скобок.
  `python -m heat3d_watch sessions --game <name>` означает, что вы заменяете часть в скобках.
- Путь с пробелами берётся в кавычки: `"C:\My Games\my file"`.
- Строки, которые начинаются с `#` в примерах, — комментарии; их не вводят.
- Успех выглядит так: после `python -m heat3d_watch games` — таблица с одной строкой на игру.

## Частые ошибки {#common-errors}

| Вы видите | Что делать |
|---|---|
| `'python' is not recognized` или `command not found` | Python не в PATH: запустите установщик снова и отметьте **Add python.exe to PATH**, затем откройте новый терминал. В macOS/Linux попробуйте `python3`. |
| `No module named ...` | шаг 4 пропущен или выполнен в другой папке: выполните `cd` в папку инструмента и повторите. |
| `pip is not recognized` | используйте `python -m pip ...` вместо `pip ...`. |
| `No such file or directory` / `can't open file` | терминал в неверной папке или путь набран с ошибкой: проверьте его и берите пути с пробелами в кавычки. |
| красный текст, оканчивающийся строкой `error:` | прочитайте последнюю строку: в ней сказано, чего не хватает. На странице [Команды](../commands.md) перечислены сообщения. |
