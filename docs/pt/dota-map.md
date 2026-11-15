---
title: "Mapa do Dota 2"
nav_order: 6.5
lang: "pt"
source: dota-map.md
source_hash: "c9830d37ea89"
nav_exclude: true
search_exclude: true
---
# O mapa do Dota 2 como nível (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

grava o mapa do Dota 2 como geometria de nível para o visualizador do 3DHeat: o chão, os
penhascos, a água, cada árvore e os prédios, no quadro e nas unidades em que as
[tabelas de replay do Dota 2](game-dota-replays.md) são desenhadas. Carregue o `.glb` no
painel **Fundo / nível** do visualizador (**Modelo 3D…**) sob uma tabela do Dota, e o calor
dos heróis fica sobre as rotas, o das torres sobre as torres. Código:
[`heat3d_watch/decoders/dota_map.py`](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/decoders/dota_map.py).

Ele precisa do Dota 2 instalado e da linha de comando do Source2Viewer. Nada do jogo está
nas ferramentas nem é transferido por elas: o mapa sai da própria instalação, e o ficheiro
que ele grava é para guardar, não para partilhar - o mapa é da Valve.

## O que ele precisa {#what-it-needs}

- **Dota 2**, instalado pela Steam. Sem `--game`, ele é procurado como
  `steamapps\common\dota 2 beta\game\dota` em cada biblioteca da Steam. `--game` aceita a
  pasta `dota 2 beta` ou a pasta `game\dota` dela.
- **CLI do Source2Viewer** (ValveResourceFormat, MIT,
  [versões](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)):
  `--source2viewer`, depois a variável de ambiente `HEAT3D_SOURCE2VIEWER`, depois
  `Source2Viewer-CLI` / `Source2Viewer-CLI.exe` no `PATH` - o mesmo da ferramenta CS2 do
  3DHeat, no comando `map`, então uma só cópia serve às duas.
- numpy (já necessário ao watcher).

`<map>` é `dota` (a predefinição: o mapa normal) ou o nome de outro mapa em
`game\dota\maps\`, ou o caminho do `.vpk` de um mapa.

## Como ele é feito {#how-it-is-made}

1. **A malha de colisão.** O Source2Viewer exporta `maps/<map>/world_physics.vmdl_c` de
   `maps/<map>.vpk` como glTF. Os grupos têm nome pela superfície. Grupos chamados `clip`
   (as paredes invisíveis) ou `sky` são descartados. Grupos chamados `water`, `slime` ou
   `window` são **água**: o rio e os lagos são `water_slime`, os riachos estreitos pela
   selva são `window`; num replay, os heróis ficam 16 unidades abaixo do primeiro e algumas
   unidades abaixo do segundo. Só as faces voltadas para cima são mantidas. O resto é o
   terreno, dividido face por face: uma face cuja normal aponta para cima com pelo menos 0,7
   (inclinações de até cerca de 45 graus) é **chão**; o restante - faces de penhasco, as
   paredes do mapa - é **estrutura**.
2. **As entidades.** O Source2Viewer descompila os blocos de entidades do mapa
   (`maps/<map>/entities/*.vents_c`) para texto: blocos com cabeçalho `====<n>====`, um
   `chave valor` por linha. Os blocos usados são `default_ents` e cada camada do mundo que
   uma entidade `info_world_layer` ali mostra no início (flag de spawn 1) - as camadas das
   duas bases. As camadas que começam ocultas guardam o que aparece quando uma base cai e
   ficam de fora.
3. **O que é desenhado.** As árvores (`ent_dota_tree`) e os prédios: torres, quartéis, os
   ancestrais (`npc_dota_fort`), os preenchimentos (`npc_dota_building`), postos avançados,
   fontes, os santuários da sabedoria, as piscinas de lótus, os portões gêmeos, vigias
   (`npc_dota_lantern`) e os depósitos de itens neutros. Lojas (o lojista é um personagem),
   o salão da fama, bandeiras, luzes e partículas não entram.
4. **Os modelos.** Cada modelo que essas entidades citam é exportado de
   `game\dota\pak01_dir.vpk` numa só execução do Source2Viewer. As malhas de um modelo que
   são outro estado da mesma coisa - o toco de uma árvore cortada, o close-up mostrado no
   inspetor, os escombros - ficam de fora pelo nome (`stump`, `inspector`, `destruction`).
5. **Os prédios** são a malha do próprio modelo, afinada por **agrupamento de vértices**:
   cada ponto vai para a média dos pontos no seu cubo do tamanho de `--detail` (predefinição 8
   unidades, cerca de um terço da largura de um herói), e os triângulos que colapsam ou se
   repetem são retirados. 0 mantém todos os triângulos.
6. **As árvores** são o contorno de cada modelo como um sólido baixo de revolução: a altura
   dele em cinco faixas, cada uma um anel de seis lados tão largo quanto a maioria dos
   pontos do modelo naquela altura (o 90º percentil da distância deles ao eixo do tronco),
   fechado embaixo e pontudo em cima - 60 triângulos, a altura e a largura reais do modelo.
   Um pinheiro sai como cone, um carvalho como uma bola sobre um caule. As malhas reais
   pesariam cerca de dez vezes mais sobre as cerca de 2.000 árvores.
7. **Posicionadas** como o jogo as posiciona: escaladas por `scales`, giradas por `angles`
   (pitch, yaw e roll do Source, em graus), movidas para `origin`.
8. **Para o quadro do visualizador.** O Source2Viewer grava glTF em metros, Y para cima: o
   (Y, Z, X) do jogo vezes 0,0254. Isso é desfeito, e cada ponto é gravado como (X, Z, -Y)
   do jogo: Y para cima, com o Y do jogo invertido - o quadro em que as tabelas do Dota são
   desenhadas pelas dicas `heat3d` dela (`up: z`, `flipY: true`, escala 1). Uma rotação, não
   um espelho.

## O ficheiro {#the-file}

Um glTF 2.0 binário como o da ferramenta CS2 do 3DHeat (veja a página de exportação de mapas
dela): um nó e uma malha por parte na raiz, sem transformações, sombreado plano (um vértice
por canto de triângulo com a normal do próprio triângulo), índices `uint32`, sem
materiais, texturas ou UVs, `asset.generator` `heat3d_watch`, unidades do jogo.

| Parte | O que é |
|---|---|
| `ground:terrain` | o chão por onde se anda |
| `structure:terrain` | faces de penhasco e as paredes do mapa |
| `water:water_slime`, `water:window` | o rio e os lagos; os riachos da selva |
| `structure:tree` | cada árvore de pé no início |
| `structure:tower`, `structure:barracks`, `structure:ancient`, `structure:filler`, `structure:outpost`, `structure:fountain`, `structure:shrine`, `structure:lotus_pool`, `structure:twin_gate`, `structure:watcher`, `structure:neutral_stash` | os prédios, por tipo |

O prefixo `ground:` / `structure:` / `water:` é como todos os exportadores de nível do 3DHeat
dizem ao visualizador o que é cada parte; ele toma a palavra deles. Como as unidades são as
do jogo (cerca de uma polegada cada), outro visualizador de glTF mostra o mapa cerca de 39
vezes maior; no 3DHeat ele fica exatamente sob a tabela.

O que ele imprime, numa execução de exemplo (os números dependem da versão do mapa):

```text
reading dota.vpk: collision mesh and entities
reading 30 models from pak01_dir.vpk
dota.glb: dota, 700,000 triangles (230,000 ground) in 16 parts; 2,400 trees, 70 buildings
```

As duas primeiras linhas vão para o fluxo de erros, a última para a saída. Um modelo que o
Source2Viewer não encontrou fica de fora e é citado no fim da última linha
(`; 1 model(s) not found, left out: ...`). Erros - Dota 2 não encontrado, mapa não
encontrado, Source2Viewer não encontrado ou com falha - imprimem `dota-map: <motivo>` e saem
com código 1.

## Como foi testado {#how-it-was-checked}

Com o replay de uma partida pública convertido pelo watcher (patch 7.40) e o mapa do jogo
instalado:

- cada amostra de posição de herói, a olhar reto para baixo, encontra chão na face mais alta
  até 64 unidades acima dos seus pés; a altura mediana acima dele é 0 unidades, e 99,5 % estão
  a até 16 unidades; com o mapa espelhado (Y não invertido), só cerca de metade encontra chão,
  e o resto flutua ou afunda a altura de um penhasco;
- as 22 torres, 12 quartéis, 2 ancestrais, 14 preenchimentos, 2 postos avançados, 2 fontes e
  10 vigias que a tabela de unidades do replay coloca estão sobre as entidades do mapa do
  mesmo tipo, com precisão de 0,02 unidades, na horizontal e na altura;
- o pé de cada árvore está sobre o chão.

Os testes (`tests/test_dota_map.py`) verificam o leitor de blocos, os quadros, a divisão do
terreno, os contornos das árvores e o agrupamento, a colocação e a exportação completa com o
Source2Viewer substituído por um simulador - só com dados inventados.

## O que ele não faz {#what-it-does-not-do}

- Sem texturas nem cores: o visualizador sombreia o nível do próprio modo.
- Nenhuma árvore cortada nem prédio destruído durante a partida: o mapa como começa.
- Mapas de evento e personalizados não foram testados; as classes de entidade deles podem ser
  diferentes.
- Os enfeites (pedras, cercas, bandeiras) só estão nele na medida em que fazem parte da malha
  de colisão.
