---
title: "Avant de commencer"
nav_order: 2
lang: fr
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Avant de commencer {#before-you-start}

Vous débutez avec la ligne de commande ? Cette page vous mène de zéro à un 3DHeat Watcher qui
fonctionne, en une dizaine de minutes. Vous tapez des commandes dans un *terminal*, une fenêtre
où vous écrivez une ligne et appuyez sur Entrée.

## 1. Installer Python {#install-python}

1. Téléchargez Python 3.10 ou plus récent sur <https://www.python.org/downloads/>.
2. Lancez l'installeur. Sur le premier écran, cochez **Add python.exe to PATH**,
   puis cliquez sur **Install Now**.
3. Vérifiez : ouvrez un terminal (étape 3) et tapez `python --version`. Vous devez
   voir `Python 3.` suivi d'un numéro égal ou supérieur à 10.

Sous Linux ou macOS, Python est généralement déjà installé : utilisez `python3` là où ces
pages disent `python`.

## 2. Récupérer 3DHeat Watcher {#get-3dheat-watcher}

Téléchargez le zip depuis la [page des versions](https://github.com/Holdi601/3DHeat-Watcher/releases) et
décompressez-le, par exemple dans `C:\Outils\3DHeat-Watcher`. (Si vous avez Git, `git clone` fonctionne aussi.)

## 3. Ouvrir un terminal dans ce dossier {#open-a-terminal-in-that-folder}

- **Windows :** ouvrez le dossier dans l'Explorateur de fichiers, cliquez dans la barre d'adresse, tapez
  `powershell` et appuyez sur Entrée. Une fenêtre bleue ou noire s'ouvre, déjà dans ce
  dossier.
- **macOS / Linux :** ouvrez *Terminal* et tapez `cd ` (avec un espace), glissez le
  dossier dans la fenêtre, appuyez sur Entrée.

`cd <dossier>` déplace le terminal vers un autre dossier. Toutes les commandes de ces
pages se tapent dans le dossier de l'outil.

## 4. Installer ce dont il a besoin {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Vous devez voir `Successfully installed ...` à la fin (ou `Requirement
already satisfied`).

## 5. Vérifier que cela fonctionne {#check-it-works}

```bash
python -m heat3d_watch --version
```

Vous devez voir : `1.0.2 (le numéro de version)`.

## Comment lire les commandes de ces pages {#how-to-read-the-commands-on-these-pages}

- Les mots entre `<chevrons>` sont des espaces réservés : tapez à la place votre propre fichier ou dossier,
  sans les chevrons. `python -m heat3d_watch sessions --game <nom>` signifie
  que vous remplacez la partie entre chevrons.
- Un chemin qui contient des espaces se met entre guillemets : `"C:\Mes Jeux\mon fichier"`.
- Les lignes qui commencent par `#` dans les exemples sont des commentaires ; vous ne les tapez pas.
- Une réussite ressemble à ceci : après `python -m heat3d_watch games`, un tableau avec une ligne par jeu.

## Erreurs courantes {#common-errors}

| Vous voyez | Faites ceci |
|---|---|
| `'python' is not recognized` ou `command not found` | Python n'est pas dans le PATH : relancez l'installeur et cochez **Add python.exe to PATH**, puis ouvrez un nouveau terminal. Sous macOS/Linux, essayez `python3`. |
| `No module named ...` | l'étape 4 a été sautée ou lancée dans un autre dossier : `cd` jusqu'au dossier de l'outil et relancez-la. |
| `pip is not recognized` | utilisez `python -m pip ...` au lieu de `pip ...`. |
| `No such file or directory` / `can't open file` | le terminal est dans le mauvais dossier, ou le chemin est mal tapé : vérifiez, et mettez les chemins contenant des espaces entre guillemets. |
| du texte rouge se terminant par une ligne `error:` | lisez la dernière ligne : elle indique ce qui manque. La page [Commandes](commands.md) liste les messages. |
