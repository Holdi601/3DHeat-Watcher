# Before you start

New to the command line? This page gets you from nothing to a working
3DHeat Watcher in about ten minutes. You type commands into a *terminal*, a window
where you write a line and press Enter.

## 1. Install Python

1. Download Python 3.10 or later from <https://www.python.org/downloads/>.
2. Run the installer. On the first screen tick **Add python.exe to PATH**,
   then click **Install Now**.
3. Check it: open a terminal (step 3) and type `python --version`. You should
   see `Python 3.` and a number of 10 or more.

On Linux or macOS, Python is usually installed already: use `python3` where
these pages say `python`.

## 2. Get 3DHeat Watcher

Download the zip from the
[Releases page](https://github.com/Holdi601/3DHeat-Watcher/releases) and unpack it, for
example to `C:\Tools\3DHeat-Watcher`. (If you have Git, `git clone` works too.)

## 3. Open a terminal in that folder

- **Windows:** open the folder in File Explorer, click the address bar, type
  `powershell` and press Enter. A blue or black window opens, already in
  that folder.
- **macOS / Linux:** open *Terminal* and type `cd ` (with a space), drag the
  folder into the window, press Enter.

`cd <folder>` moves the terminal to another folder. All commands on these
pages are typed in the tool's own folder.

## 4. Install what it needs

```bash
python -m pip install -r requirements.txt
```

You should see `Successfully installed ...` at the end (or `Requirement
already satisfied`).

## 5. Check it works

```bash
python -m heat3d_watch --version
```

You should see: `1.0.2 (the version number)`.

## How to read the commands on these pages

- Words in `<angle brackets>` are placeholders: type your own file or folder
  instead, without the brackets. `python -m heat3d_watch sessions --game <name>` means
  you replace the bracketed part.
- A path with spaces goes in quotes: `"C:\My Games\my file"`.
- Lines starting with `#` in the examples are comments; you do not type them.
- Success looks like this: after `python -m heat3d_watch games`, a table with one line per game.

## Common errors

| You see | Do this |
|---|---|
| `'python' is not recognized` or `command not found` | Python is not on PATH: run the installer again and tick **Add python.exe to PATH**, then open a new terminal. On macOS/Linux try `python3`. |
| `No module named ...` | step 4 was skipped or ran in another folder: `cd` to the tool's folder and run it again. |
| `pip is not recognized` | use `python -m pip ...` instead of `pip ...`. |
| `No such file or directory` / `can't open file` | the terminal is in the wrong folder, or the path is mistyped: check it, and put paths with spaces in quotes. |
| red text ending in an `error:` line | read the last line: it says what is missing. The [Commands](commands) page lists the messages. |
