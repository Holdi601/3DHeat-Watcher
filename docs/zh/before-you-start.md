---
title: 开始之前
nav_order: 2
lang: zh
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# 开始之前 {#before-you-start}

第一次使用命令行？本页带你从零开始，用大约十分钟让 3DHeat Watcher 正常运行。你在一个*终端*中输入命令，那是一个让你输入一行并按回车的窗口。

## 1. 安装 Python {#install-python}

1. 从 <https://www.python.org/downloads/> 下载 Python 3.10 或更高版本。
2. 运行安装程序。在第一个界面勾选 **Add python.exe to PATH**，然后点击 **Install Now**。
3. 检查：打开一个终端（第 3 步），输入 `python --version`。你应该会看到 `Python 3.`，以及 10 或更大的版本号。

在 Linux 或 macOS 上，Python 通常已经安装：在这些页面写 `python` 的地方，请使用 `python3`。

## 2. 获取 3DHeat Watcher {#get-3dheat-watcher}

从 [发布页面](https://github.com/Holdi601/3DHeat-Watcher/releases) 下载压缩包，并解压，例如解压到 `C:\Tools\3DHeat-Watcher`。（如果你安装了 Git，`git clone` 也可以。）

## 3. 在该文件夹中打开终端 {#open-a-terminal-in-that-folder}

- **Windows：** 在文件资源管理器中打开该文件夹，点击地址栏，输入
  `powershell` 并按回车。一个蓝色或黑色的窗口会打开，并且已经位于该文件夹中。
- **macOS / Linux：** 打开 *终端*，输入 `cd `（注意后面有一个空格），把文件夹拖进窗口，然后按回车。

`cd <folder>` 可以把终端移动到另一个文件夹。本页中的所有命令都在工具自己的文件夹中输入。

## 4. 安装它所需的组件 {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

结束时你应该会看到 `Successfully installed ...`（或者 `Requirement already satisfied`）。

## 5. 检查它是否正常工作 {#check-it-works}

```bash
python -m heat3d_watch --version
```

你应该会看到：`1.0.2`（版本号）。

## 如何阅读这些页面上的命令 {#how-to-read-the-commands-on-these-pages}

- `<尖括号>` 中的词是占位符：请输入你自己的文件或文件夹，并去掉尖括号。`python -m heat3d_watch sessions --game <name>` 的意思是：替换掉尖括号部分。
- 包含空格的路径需要加引号：`"C:\My Games\my file"`。
- 示例中以 `#` 开头的行是注释；你不需要输入它们。
- 成功的样子：运行 `python -m heat3d_watch games` 后，出现一个表格，每款游戏一行。

## 常见错误 {#common-errors}

| 你看到的 | 怎么做 |
|---|---|
| `'python' is not recognized` 或 `command not found` | Python 不在 PATH 中：重新运行安装程序，勾选 **Add python.exe to PATH**，然后打开一个新的终端。在 macOS/Linux 上请试用 `python3`。 |
| `No module named ...` | 第 4 步被跳过，或者是在另一个文件夹中运行的：`cd` 进入工具的文件夹，然后再运行一次。 |
| `pip is not recognized` | 使用 `python -m pip ...` 代替 `pip ...`。 |
| `No such file or directory` / `can't open file` | 终端位于错误的文件夹，或者路径拼写有误：请检查，并把包含空格的路径放在引号中。 |
| 红色文字，以 `error:` 行结尾 | 阅读最后一行：它会说明缺少什么。[命令](../commands.md) 页面列出了这些信息。 |
