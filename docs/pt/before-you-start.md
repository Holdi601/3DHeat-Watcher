---
title: Antes de começar
nav_order: 2
lang: "pt"
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Antes de começar {#before-you-start}

A linha de comando é novidade? Esta página guia do zero até um 3DHeat Watcher a funcionar em cerca de dez minutos.
Os comandos escrevem-se num *terminal*, uma janela onde se escreve uma linha e se prime Enter.

## 1. Instalar o Python {#install-python}

1. Transfira o Python 3.10 ou mais recente em <https://www.python.org/downloads/>.
2. Execute o instalador. No primeiro ecrã, marque **Add python.exe to PATH** e depois clique em **Install Now**.
3. Verifique: abra um terminal (passo 3) e escreva `python --version`. Deve aparecer
   `Python 3.` e um número 10 ou maior.

No Linux ou no macOS, o Python costuma já estar instalado: use `python3` onde
estas páginas dizem `python`.

## 2. Obter o 3DHeat Watcher {#get-3dheat-watcher}

Transfira o zip na [página de lançamentos](https://github.com/Holdi601/3DHeat-Watcher/releases) e extraia-o,
por exemplo para `C:\Ferramentas\3DHeat-Watcher`. (Com o Git, `git clone` também funciona.)

## 3. Abrir um terminal nessa pasta {#open-a-terminal-in-that-folder}

- **Windows:** no Explorador de Ficheiros, abra a pasta, clique na barra de endereço, escreva
  `powershell` e prima Enter. Abre-se uma janela azul ou preta, já nessa
  pasta.
- **macOS / Linux:** abra o *Terminal*, escreva `cd ` (com um espaço), arraste a
  pasta para a janela e prima Enter.

`cd <pasta>` move o terminal para outra pasta. Todos os comandos destas páginas se escrevem
na própria pasta da ferramenta.

## 4. Instalar o que ela precisa {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

No fim deve aparecer `Successfully installed ...` (ou `Requirement
already satisfied`).

## 5. Verificar se funciona {#check-it-works}

```bash
python -m heat3d_watch --version
```

Deve aparecer: `1.0.2 (o número da versão)`.

## Como ler os comandos destas páginas {#how-to-read-the-commands-on-these-pages}

- Palavras entre `<colchetes angulares>` são marcadores: escreva o ficheiro ou a pasta próprios no lugar,
  sem os colchetes. `python -m heat3d_watch sessions --game <nome>` quer dizer que a parte entre colchetes se substitui.
- Um caminho com espaços vai entre aspas: `"C:\Meus Jogos\meu ficheiro"`.
- As linhas que começam com `#` nos exemplos são comentários; não se escrevem.
- Sucesso tem este aspeto: depois de `python -m heat3d_watch games`, uma tabela com uma linha por jogo.

## Erros comuns {#common-errors}

| Aparece | Faça isto |
|---|---|
| `'python' is not recognized` ou `command not found` | O Python não está no PATH: execute o instalador de novo e marque **Add python.exe to PATH**, depois abra um terminal novo. No macOS/Linux, experimente `python3`. |
| `No module named ...` | o passo 4 foi saltado ou executado noutra pasta: use `cd` para ir à pasta da ferramenta e execute de novo. |
| `pip is not recognized` | use `python -m pip ...` em vez de `pip ...`. |
| `No such file or directory` / `can't open file` | o terminal está na pasta errada, ou o caminho está mal escrito: verifique, e coloque entre aspas os caminhos com espaços. |
| texto vermelho que termina numa linha `error:` | leia a última linha: diz o que falta. A página [Comandos](commands.md) lista as mensagens. |
