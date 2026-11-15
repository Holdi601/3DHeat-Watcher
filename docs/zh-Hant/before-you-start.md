---
title: "開始之前"
nav_order: 2
lang: "zh-Hant"
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# 開始之前 {#before-you-start}

第一次使用命令列？這一頁會帶你從零開始，約十分鐘內完成可運作的 3DHeat Watcher。你在*終端機*中輸入指令，即一個你寫下一行、按 Enter 的視窗。

## 1. 安裝 Python {#install-python}

1. 從 <https://www.python.org/downloads/> 下載 Python 3.10 或更新版本。
2. 執行安裝程式。在第一個畫面勾選 **Add python.exe to PATH**，
   然後按 **Install Now**。
3. 確認安裝：開啟終端機（第 3 步），輸入 `python --version`。你應該會看到
   `Python 3.` 以及 10 或以上的數字。

在 Linux 或 macOS 上，Python 通常已經安裝好：本頁若寫 `python`，請改用 `python3`。

## 2. 取得 3DHeat Watcher {#get-3dheat-watcher}

從 [發行頁面](https://github.com/Holdi601/3DHeat-Watcher/releases) 下載 zip 檔，並解壓縮，
例如解壓到 `C:\Tools\3DHeat-Watcher`。（若你有 Git，也可以使用 `git clone`。）

## 3. 在該資料夾中開啟終端機 {#open-a-terminal-in-that-folder}

- **Windows：** 在檔案總管中開啟該資料夾，點一下網址列，輸入
  `powershell` 再按 Enter。會開啟一個藍色或黑色的視窗，已經位於該資料夾中。
- **macOS / Linux：** 開啟*終端機*，輸入 `cd `（後面要有一個空格），把資料夾拖進視窗，然後按 Enter。

`cd <folder>` 會把終端機移到另一個資料夾。本頁的所有指令都在工具自己的資料夾中輸入。

## 4. 安裝所需的套件 {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

最後你應該會看到 `Successfully installed ...`（或 `Requirement
already satisfied`）。

## 5. 確認它可以運作 {#check-it-works}

```bash
python -m heat3d_watch --version
```

你應該會看到：`1.0.2`（版本號）。

## 如何閱讀本頁的指令 {#how-to-read-the-commands-on-these-pages}

- `<角括號>` 中的文字是佔位符：請改輸入你自己的檔案或資料夾，不要輸入括號。`python -m heat3d_watch sessions --game <name>` 表示你要替換括號中的部分。
- 含有空格的路徑要加引號：`"C:\My Games\my file"`。
- 範例中以 `#` 開頭的行是註解；你不需要輸入。
- 成功的樣子：執行 `python -m heat3d_watch games` 後，會出現一個表格，每個遊戲一行。

## 常見錯誤 {#common-errors}

| 你看到的 | 該怎麼做 |
|---|---|
| `'python' is not recognized` 或 `command not found` | Python 不在 PATH 中：重新執行安裝程式並勾選 **Add python.exe to PATH**，然後開啟新的終端機。在 macOS/Linux 請試 `python3`。 |
| `No module named ...` | 略過了第 4 步，或在另一個資料夾中執行：用 `cd` 前往工具的資料夾，然後再執行一次。 |
| `pip is not recognized` | 改用 `python -m pip ...`，不要用 `pip ...`。 |
| `No such file or directory` / `can't open file` | 終端機位於錯誤的資料夾，或路徑打錯字：請檢查，並把含有空格的路徑加上引號。 |
| 紅色文字，以 `error:` 行結尾 | 閱讀最後一行：它會說明缺少什麼。[指令](../commands.md)頁面列出了各種訊息。 |
