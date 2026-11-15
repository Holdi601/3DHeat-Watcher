---
title: 시작하기 전에
nav_order: 2
lang: "ko"
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# 시작하기 전에 {#before-you-start}

명령줄이 처음입니까? 이 페이지는 약 10분 만에 아무것도 없는 상태에서 작동하는 3DHeat Watcher까지 안내합니다. 명령은 *터미널*에 입력합니다. 한 줄을 쓰고 Enter를 누르는 창입니다.

## 1. Python 설치 {#install-python}

1. <https://www.python.org/downloads/>에서 Python 3.10 이상을 내려받으세요.
2. 설치 프로그램을 실행하세요. 첫 화면에서 **Add python.exe to PATH**를 체크한 다음 **Install Now**를 누르세요.
3. 확인하세요: 터미널(3단계)을 열고 `python --version`을 입력하세요. `Python 3.`과 10 이상의 숫자가 보여야 합니다.

Linux나 macOS에는 보통 Python이 이미 설치되어 있습니다. 이 페이지에 `python`이라고 나오는 곳에 `python3`을 쓰세요.

## 2. 3DHeat Watcher 받기 {#get-3dheat-watcher}

[릴리스 페이지](https://github.com/Holdi601/3DHeat-Watcher/releases)에서 zip 파일을 내려받아 압축을 푸세요. 예를 들어 `C:\Tools\3DHeat-Watcher`에 풉니다. (git이 있다면 `git clone`도 됩니다.)

## 3. 그 폴더에서 터미널 열기 {#open-a-terminal-in-that-folder}

- **Windows:** 파일 탐색기에서 폴더를 열고, 주소창을 클릭한 뒤 `powershell`을 입력하고 Enter를 누르세요. 파란색 또는 검은색 창이 열리는데, 이미 그 폴더에 들어가 있습니다.
- **macOS / Linux:** *Terminal*을 열고 `cd `(뒤에 빈칸 하나)를 입력한 뒤, 폴더를 창으로 끌어다 놓고 Enter를 누르세요.

`cd <folder>`는 터미널을 다른 폴더로 옮깁니다. 이 페이지들의 모든 명령은 도구의 폴더 안에서 입력합니다.

## 4. 필요한 것 설치하기 {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

끝에 `Successfully installed ...`가 보여야 합니다(또는 `Requirement already satisfied`).

## 5. 작동하는지 확인하기 {#check-it-works}

```bash
python -m heat3d_watch --version
```

이것이 보여야 합니다: `1.0.2 (버전 번호)`.

## 이 페이지의 명령 읽는 법 {#how-to-read-the-commands-on-these-pages}

- `<꺾쇠괄호>` 안의 말은 **자리 표시자**입니다. 괄호 없이 본인의 파일이나 폴더를 입력하세요. `python -m heat3d_watch sessions --game <name>`에서는 괄호 부분을 바꾸면 됩니다.
- 공백이 있는 경로는 따옴표로 감쌉니다: `"C:\My Games\my file"`.
- 예시에서 `#`으로 시작하는 줄은 주석입니다. 입력하지 않습니다.
- 성공의 모습: `python -m heat3d_watch games` 뒤에 게임마다 한 줄씩 있는 표가 나옵니다.

## 흔한 오류 {#common-errors}

| 보이는 것 | 할 일 |
|---|---|
| `'python' is not recognized` 또는 `command not found` | Python이 PATH에 없습니다. 설치 프로그램을 다시 실행해 **Add python.exe to PATH**를 체크하고, 새 터미널을 여세요. macOS/Linux에서는 `python3`을 시도하세요. |
| `No module named ...` | 4단계를 건너뛰었거나 다른 폴더에서 실행했습니다. 도구의 폴더로 `cd` 한 뒤 다시 실행하세요. |
| `pip is not recognized` | `pip ...` 대신 `python -m pip ...`를 쓰세요. |
| `No such file or directory` / `can't open file` | 터미널이 잘못된 폴더에 있거나, 경로에 오타가 있습니다. 확인하고, 공백이 있는 경로는 따옴표로 감싸세요. |
| 빨간 글씨가 `error:` 줄로 끝남 | 마지막 줄을 읽으세요. 무엇이 없는지 알려 줍니다. [명령](../commands.md) 페이지에 메시지 목록이 있습니다. |
