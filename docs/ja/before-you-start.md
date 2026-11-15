---
title: "始める前に"
nav_order: 2
lang: "ja"
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# 始める前に {#before-you-start}

コマンドラインは初めてですか？ このページは、ゼロから動く 3DHeat Watcher までを約10分で案内します。コマンドは *ターミナル* に入力します。行を書いて Enter を押すウィンドウのことです。

## 1. Python をインストール {#install-python}

1. <https://www.python.org/downloads/> から Python 3.10 以降をダウンロードします。
2. インストーラーを実行します。最初の画面で **Add python.exe to PATH** にチェックを入れてから、**Install Now** をクリックします。
3. 確認します: ターミナルを開き（手順3）、`python --version` と入力します。`Python 3.` と、10 以上の番号が表示されるはずです。

Linux や macOS では、Python はたいてい最初からインストールされています。これらのページで `python` と書いてある所は `python3` を使ってください。

## 2. 3DHeat Watcher を入手 {#get-3dheat-watcher}

[リリースのページ](https://github.com/Holdi601/3DHeat-Watcher/releases) から zip をダウンロードし、展開します。たとえば `C:\Tools\3DHeat-Watcher` へ。（Git があれば `git clone` も使えます。）

## 3. そのフォルダーでターミナルを開く {#open-a-terminal-in-that-folder}

- **Windows:** エクスプローラーでフォルダーを開き、アドレスバーをクリックして `powershell` と入力し、Enter を押します。そのフォルダーがすでに開かれた、青または黒のウィンドウが開きます。
- **macOS / Linux:** *ターミナル* を開き、`cd `（空白を1つ入れる）と入力し、フォルダーをウィンドウにドラッグして、Enter を押します。

`cd <folder>` は、ターミナルを別のフォルダーへ移動させます。このページのすべてのコマンドは、ツール自身のフォルダーで入力します。

## 4. 必要なものをインストール {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

最後に `Successfully installed ...` と表示されるはずです（または `Requirement already satisfied`）。

## 5. 動作を確認 {#check-it-works}

```bash
python -m heat3d_watch --version
```

次のように表示されるはずです: `1.0.2 (the version number)`。

## このページのコマンドの読み方 {#how-to-read-the-commands-on-these-pages}

- `<山括弧>` の中の言葉は **置き換え用の場所** です。山括弧を外し、自分のファイルまたはフォルダーを入力してください。`python -m heat3d_watch sessions --game <name>` は、括弧の部分を置き換えるという意味です。
- スペースを含むパスは引用符で囲みます: `"C:\My Games\my file"`。
- 例の中で `#` で始まる行はコメントです。入力しません。
- 成功時の表示: `python -m heat3d_watch games` の後に、ゲームごとに1行のテーブルが出ます。

## よくあるエラー {#common-errors}

| 表示 | 対処 |
|---|---|
| `'python' is not recognized` または `command not found` | Python が PATH にありません。インストーラーをもう一度実行し、**Add python.exe to PATH** にチェックを入れてから、新しいターミナルを開いてください。macOS/Linux では `python3` を試します。 |
| `No module named ...` | 手順4を飛ばしたか、別のフォルダーで実行しました。ツールのフォルダーへ `cd` で移動し、もう一度実行してください。 |
| `pip is not recognized` | `pip ...` の代わりに `python -m pip ...` を使います。 |
| `No such file or directory` / `can't open file` | ターミナルが違うフォルダーにいるか、パスの綴りが違います。確認し、スペースを含むパスは引用符で囲んでください。 |
| `error:` で終わる赤い文字 | 最後の行を読みます。何が足りないかが書かれています。[コマンド](../commands.md) のページに、メッセージの一覧があります。 |
