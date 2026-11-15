---
title: "Перад пачаткам"
nav_order: 2
lang: be
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Перад пачаткам {#before-you-start}

Упершыню ў камандным радку? Гэтая старонка правядзе вас ад нуля да працоўнага
3DHeat Watcher прыкладна за дзесяць хвілін. Вы друкуеце каманды ў *тэрмінал* — акно,
дзе пішуць радок і націскаюць Enter.

## 1. Усталюйце Python {#install-python}

1. Спампуйце Python 3.10 або навейшы з <https://www.python.org/downloads/>.
2. Запусціце ўсталёўшчык. На першым экране адзначце **Add python.exe to PATH**,
   потым націсніце **Install Now**.
3. Праверце: адкрыйце тэрмінал (крок 3) і ўвядзіце `python --version`. Вы павінны
   ўбачыць `Python 3.` і лік 10 або больш.

У Linux або macOS Python звычайна ўжо ўсталяваны: выкарыстоўвайце `python3` там, дзе
на гэтых старонках напісана `python`.

## 2. Атрымайце 3DHeat Watcher {#get-3dheat-watcher}

Спампуйце zip са
[старонкі Releases](https://github.com/Holdi601/3DHeat-Watcher/releases) і распакуйце яго, напрыклад
у `C:\Tools\3DHeat-Watcher`. (Калі ў вас ёсць Git, падыдзе і `git clone`.)

## 3. Адкрыйце тэрмінал у гэтай папцы {#open-a-terminal-in-that-folder}

- **Windows:** адкрыйце папку ў Правадыру, пстрыкніце ў адрасным радку, увядзіце
  `powershell` і націсніце Enter. Адкрыецца сіняе або чорнае акно, ужо ў
  гэтай папцы.
- **macOS / Linux:** адкрыйце *Terminal* і ўвядзіце `cd ` (з прабелам), перацягніце
  папку ў акно, націсніце Enter.

`cd <folder>` пераносіць тэрмінал у іншую папку. Усе каманды на гэтых
старонках друкуюцца ў папцы самога інструмента.

## 4. Усталюйце тое, што патрэбна {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

У канцы вы ўбачыце `Successfully installed ...` (або `Requirement
already satisfied`).

## 5. Праверце, што ён працуе {#check-it-works}

```bash
python -m heat3d_watch --version
```

Вы ўбачыце: `1.0.2 (the version number)`.

## Як чытаць каманды на гэтых старонках {#how-to-read-the-commands-on-these-pages}

- Словы ў `<вуглавых дужках>` — запаўняльнікі: увядзіце замест іх свой файл або папку,
  без дужак. `python -m heat3d_watch sessions --game <name>` значыць,
  што вы замяняеце частку ў дужках.
- Шлях з прабеламі бярэцца ў двукоссі: `"C:\My Games\my file"`.
- Радкі, што пачынаюцца з `#` у прыкладах, — каментарыі; іх не друкуюць.
- Поспех выглядае так: пасля `python -m heat3d_watch games` табліца з радком на кожную гульню.

## Частыя памылкі {#common-errors}

| Вы бачыце | Што рабіць |
|---|---|
| `'python' is not recognized` або `command not found` | Python няма ў PATH: запусціце ўсталёўшчык зноў і адзначце **Add python.exe to PATH**, потым адкрыйце новы тэрмінал. У macOS/Linux паспрабуйце `python3`. |
| `No module named ...` | крок 4 прапушчаны або выкананы ў іншай папцы: перайдзіце праз `cd` у папку інструмента і выканайце яго зноў. |
| `pip is not recognized` | выкарыстоўвайце `python -m pip ...` замест `pip ...`. |
| `No such file or directory` / `can't open file` | тэрмінал не ў той папцы, або шлях памылкова напісаны: праверце яго і бярыце шляхі з прабеламі ў двукоссі. |
| чырвоны тэкст, што заканчваецца радком `error:` | прачытайце апошні радок: ён кажа, чаго не хапае. Паведамленні пералічаны на старонцы [Каманды](../commands.md). |
