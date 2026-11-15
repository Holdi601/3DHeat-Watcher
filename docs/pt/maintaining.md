---
title: Manutenção
nav_order: 15
lang: "pt"
source: maintaining.md
source_hash: "2b2ca419262b"
nav_exclude: true
search_exclude: true
---
# Manutenção destas páginas {#maintaining-these-pages}

A lista de verificação de cada versão. As páginas precisam de dizer o que o código faz, ser fáceis de ler para um iniciante, uma criança de 8 anos e um especialista, e existir em todos os idiomas que o visualizador do 3DHeat suporta.

## Lista de verificação da versão {#release-checklist}

1. **Gerar de novo as páginas geradas** a partir do código:

   ```bash
   python tools/gen_game_pages.py
   python tools/gen_docs_reference.py
   for f in tools/diagrams/*.json; do python tools/flow2svg.py $f docs/assets/img/$(basename $f .json).svg; done
   ```

   Antes de fazer commit, o mesmo com `--check` deve terminar com código 0:

   ```bash
   python tools/gen_game_pages.py --check
   python tools/gen_docs_reference.py --check
   ```

2. **Comparar as funcionalidades desde a última versão.** `VERSION` guarda a versão; a tag dela é `v<VERSION>`:

   ```bash
   git log --oneline v$(cat VERSION)..HEAD
   ```

   Cada novo comando, opção, coluna, saída ou comportamento ganha uma linha na página que o cobre, e uma
   linha em `CHANGELOG.md`, sob **Docs**, a citar essa página.

3. **Revisão independente.** Alguém que não escreveu a alteração lê as páginas alteradas - diagramas e
   imagens inclusive - três vezes: como iniciante (nunca usou um terminal), como criança de 8 anos (o
   primeiro parágrafo diz o que é e porquê, em palavras simples?) e como especialista (opções, predefinições e
   colunas são exatamente o que o código faz?).

4. **Corrigir o que a revisão encontrou.** As imagens continuam com no máximo cerca de 900 px de largura e
   texto de pelo menos 12 px, como mostrado; os diagramas são gerados de `tools/diagrams/*.json` com
   `tools/flow2svg.py`. Os exemplos usam apenas nomes inventados (`de_x`, "Demo Valley", `<mapa>`): nunca
   um mapa real, um jogador real, um id de partida real ou uma figura de ficheiros reais.

5. **Traduções.** Cada página traduzida regista o hash do texto em inglês a partir do qual foi feita.
   Traduza de novo as páginas cujo hash da fonte em inglês mudou, e depois faça com que cada idioma seja
   revisto das três formas (simples, iniciante, especialista), incluindo os rótulos dos diagramas.

6. **Publicar só com a aprovação do dono.** Faça commit local; o dono decide quando vai a público.

## Traduções: os comandos {#translations-the-commands}

O site é traduzido para os 40 idiomas do visualizador do 3DHeat: o inglês fica em `docs/`, e cada outro
idioma em `docs/<idioma>/`, com os mesmos nomes de ficheiro. `tools/docs_i18n.py` faz a contabilidade:

```bash
python tools/docs_i18n.py hashes             # após qualquer mudança em inglês: regista o hash de cada página
python tools/docs_i18n.py svg-strings        # após qualquer mudança em imagem: os rótulos a traduzir
python tools/docs_i18n.py status             # por idioma: atuais, desatualizadas, páginas em falta
python tools/docs_i18n.py todo --lang de     # as páginas em alemão a (re)traduzir
python tools/docs_i18n.py svg-build --lang de    # as imagens em alemão a partir de docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # marca as páginas em alemão com o hash do inglês
python tools/docs_i18n.py check              # sai com código 1 quando hashes ou rótulos estão desatualizados
```

Traduza apenas o que `todo` lista: mantenha Markdown, links, código, nomes de ficheiro e de colunas como estão,
traduza os títulos e as descrições das imagens, e use as palavras próprias do visualizador do 3DHeat para
os botões e painéis (em `src/i18n/locales/<idioma>/`). As páginas de referência geradas e as imagens de
terminal continuam em inglês. No site, uma tradução desatualizada diz isso e leva à página em inglês; uma
em falta cai de volta para o inglês. O menu de idiomas do cabeçalho e o redirecionamento por idioma do
navegador na página inicial vêm de `docs/_includes/`.
