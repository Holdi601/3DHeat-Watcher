---
title: "Преди да започнете"
nav_order: 2
lang: "bg"
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Преди да започнете {#before-you-start}

Нов ли сте в командния ред? Тази страница ви води от нищо до работещ
3DHeat Watcher за около десет минути. Въвеждате команди в *терминал* - прозорец, в който
пишете ред и натискате Enter.

## 1. Инсталирайте Python {#install-python}

1. Изтеглете Python 3.10 или по-нов от <https://www.python.org/downloads/>.
2. Стартирайте инсталатора. На първия екран отметнете **Add python.exe to PATH**,
   после щракнете **Install Now**.
3. Проверете: отворете терминал (стъпка 3) и напишете `python --version`. Трябва да
   видите `Python 3.` и номер 10 или по-голям.

В Linux или macOS Python обикновено е инсталиран: използвайте `python3` там, където тези страници пишат `python`.

## 2. Вземете 3DHeat Watcher {#get-3dheat-watcher}

Изтеглете zip архива от
[страницата с издания](https://github.com/Holdi601/3DHeat-Watcher/releases) и разархивирайте,
например в `C:\Tools\3DHeat-Watcher`. (Ако имате Git, `git clone` също работи.)

## 3. Отворете терминал в тази папка {#open-a-terminal-in-that-folder}

- **Windows:** отворете папката във File Explorer, щракнете в адресния ред, напишете
  `powershell` и натиснете Enter. Отваря се син или черен прозорец, вече в тази
  папка.
- **macOS / Linux:** отворете *Terminal* и напишете `cd ` (с интервал), плъзнете
  папката в прозореца, натиснете Enter.

`cd <folder>` премества терминала в друга папка. Всички команди на тези
страници се пишат в собствената папка на инструмента.

## 4. Инсталирайте нужното {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

В края трябва да видите `Successfully installed ...` (или `Requirement
already satisfied`).

## 5. Проверете, че работи {#check-it-works}

```bash
python -m heat3d_watch --version
```

Трябва да видите: `1.0.2` (номерът на версията).

## Как да четете командите на тези страници {#how-to-read-the-commands-on-these-pages}

- Думите в `<ъглови скоби>` са места за попълване: напишете вместо тях своя файл или папка,
  без скобите. `python -m heat3d_watch sessions --game <name>` означава, че заменяте
  частта в скоби.
- Път с интервали се пише в кавички: `"C:\My Games\my file"`.
- Редовете, които започват с `#` в примерите, са коментари; не ги пишете.
- Успехът изглежда така: след `python -m heat3d_watch games` - таблица с по един ред за всяка игра.

## Чести грешки {#common-errors}

| Виждате | Направете това |
|---|---|
| `'python' is not recognized` или `command not found` | Python не е в PATH: стартирайте инсталатора отново и отметнете **Add python.exe to PATH**, после отворете нов терминал. В macOS/Linux опитайте `python3`. |
| `No module named ...` | стъпка 4 е пропусната или е пусната в друга папка: `cd` до папката на инструмента и я пуснете отново. |
| `pip is not recognized` | използвайте `python -m pip ...` вместо `pip ...`. |
| `No such file or directory` / `can't open file` | терминалът е в грешна папка или пътят е написан грешно: проверете го и сложете пътищата с интервали в кавички. |
| червен текст, завършващ с ред `error:` | прочетете последния ред: той казва какво липсва. Страницата [Команди](../commands.md) изброява съобщенията. |
