---
title: Antes de começar
nav_order: 2
lang: pt
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Antes de começar {#before-you-start}

Nunca usou a linha de comando? Esta página leva você do zero a um 3DHeat Watcher
funcionando em cerca de dez minutos. Você digita comandos em um *terminal*, uma janela
onde escreve uma linha e pressiona Enter.

## 1. Instalar o Python {#install-python}

1. Baixe o Python 3.10 ou mais recente em <https://www.python.org/downloads/>.
2. Execute o instalador. Na primeira tela, marque **Add python.exe to PATH**,
   depois clique em **Install Now**.
3. Confira: abra um terminal (passo 3) e digite `python --version`. Você deve
   ver `Python 3.` e um número 10 ou maior.

No Linux ou no macOS, o Python geralmente já está instalado: use `python3` onde
estas páginas dizem `python`.

## 2. Obter o 3DHeat Watcher {#get-3dheat-watcher}

Baixe o zip na [página de lançamentos](https://github.com/Holdi601/3DHeat-Watcher/releases) e descompacte-o,
por exemplo em `C:\Ferramentas\3DHeat-Watcher`. (Se tiver o Git, `git clone` também funciona.)

## 3. Abrir um terminal nessa pasta {#open-a-terminal-in-that-folder}

- **Windows:** abra a pasta no Explorador de Arquivos, clique na barra de endereço, digite
  `powershell` e pressione Enter. Abre uma janela azul ou preta, já nessa
  pasta.
- **macOS / Linux:** abra o *Terminal* e digite `cd ` (com um espaço), arraste a
  pasta para a janela, pressione Enter.

`cd <pasta>` move o terminal para outra pasta. Todos os comandos destas páginas são
digitados na própria pasta da ferramenta.

## 4. Instalar o que ela precisa {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Você deve ver `Successfully installed ...` no final (ou `Requirement
already satisfied`).

## 5. Conferir se funciona {#check-it-works}

```bash
python -m heat3d_watch --version
```

Você deve ver: `1.0.2 (o número da versão)`.

## Como ler os comandos destas páginas {#how-to-read-the-commands-on-these-pages}

- Palavras entre `<colchetes angulares>` são marcadores: digite o seu próprio arquivo ou pasta
  no lugar, sem os colchetes. `python -m heat3d_watch sessions --game <nome>` quer dizer
  que você substitui a parte entre colchetes.
- Um caminho com espaços vai entre aspas: `"C:\Meus Jogos\meu arquivo"`.
- Linhas que começam com `#` nos exemplos são comentários; você não as digita.
- O sucesso tem esta cara: depois de `python -m heat3d_watch games`, uma tabela com uma linha por jogo.

## Erros comuns {#common-errors}

| Você vê | Faça isto |
|---|---|
| `'python' is not recognized` ou `command not found` | O Python não está no PATH: execute o instalador de novo e marque **Add python.exe to PATH**, depois abra um novo terminal. No macOS/Linux tente `python3`. |
| `No module named ...` | o passo 4 foi pulado ou foi executado em outra pasta: use `cd` para ir à pasta da ferramenta e execute de novo. |
| `pip is not recognized` | use `python -m pip ...` em vez de `pip ...`. |
| `No such file or directory` / `can't open file` | o terminal está na pasta errada, ou o caminho está digitado errado: confira, e coloque entre aspas os caminhos com espaços. |
| texto vermelho terminando em uma linha `error:` | leia a última linha: ela diz o que está faltando. A página [Comandos](../commands.md) lista as mensagens. |
