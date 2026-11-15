---
title: Sula dtosaíonn tú
nav_order: 2
lang: "ga"
source: before-you-start.md
source_hash: "0bf5e50d8593"
nav_exclude: true
search_exclude: true
---
# Sula dtosaíonn tú {#before-you-start}

An bhfuil tú nua leis an líne ordaithe? Tugann an leathanach seo thú ó rud ar bith go dtí 3DHeat Watcher atá ag obair i
thart ar dheich nóiméad. Clóscríobhann tú orduithe isteach i *teirminéal*, fuinneog
ina scríobhann tú líne agus ina mbrúnn tú Enter.

## 1. Suiteáil Python {#install-python}

1. Íoslódáil Python 3.10 nó níos nuaí ó <https://www.python.org/downloads/>.
2. Rith an suiteálaí. Ar an gcéad scáileán cuir tic i **Add python.exe to PATH**,
   ansin cliceáil **Install Now**.
3. Seiceáil é: oscail teirminéal (céim 3) agus clóscríobh `python --version`. Ba chóir duit
   `Python 3.` agus uimhir 10 nó níos mó a fheiceáil.

Ar Linux nó macOS, is minic go bhfuil Python suiteáilte cheana: úsáid `python3` nuair a deir
na leathanaigh seo `python`.

## 2. Faigh 3DHeat Watcher {#get-3dheat-watcher}

Íoslódáil an zip ón
[leathanach Releases](https://github.com/Holdi601/3DHeat-Watcher/releases) agus dízipeáil é, mar
shampla go `C:\Tools\3DHeat-Watcher`. (Má tá Git agat, oibríonn `git clone` freisin.)

## 3. Oscail teirminéal sa fhillteán sin {#open-a-terminal-in-that-folder}

- **Windows:** oscail an fillteán in File Explorer, cliceáil an barra seoltaí, clóscríobh
  `powershell` agus brúigh Enter. Osclaíonn fuinneog ghorm nó dhubh, cheana féin sa
  fhillteán sin.
- **macOS / Linux:** oscail *Terminal* agus clóscríobh `cd ` (le spás), tarraing an
  fillteán isteach sa fhuinneog, brúigh Enter.

Bogann `cd <folder>` an teirminéal go fillteán eile. Clóscríobhtar gach ordú ar na leathanaigh
seo i bhfillteán na huirlise féin.

## 4. Suiteáil an méid atá ag teastáil uaithi {#install-what-it-needs}

```bash
python -m pip install -r requirements.txt
```

Ba chóir duit `Successfully installed ...` a fheiceáil ag an deireadh (nó `Requirement
already satisfied`).

## 5. Seiceáil go n-oibríonn sé {#check-it-works}

```bash
python -m heat3d_watch --version
```

Ba chóir duit a fheiceáil: `1.0.2 (the version number)`.

## Conas na horduithe ar na leathanaigh seo a léamh {#how-to-read-the-commands-on-these-pages}

- Is ionadchoinneálaithe iad focail idir `<angle brackets>`: clóscríobh do chomhad nó d'fhillteán féin
  ina n-ionad, gan na lúibíní. Ciallaíonn `python -m heat3d_watch sessions --game <name>` go
  gcuireann tú an chuid idir lúibíní in ionad.
- Téann cosán a bhfuil spásanna ann idir comharthaí athfhriotail: `"C:\My Games\my file"`.
- Is nótaí iad línte a thosaíonn le `#` sna samplaí; ní chlóscríobhann tú iad.
- Seo cuma an rath: tar éis `python -m heat3d_watch games`, tábla le líne amháin in aghaidh an chluiche.

## Earráidí coitianta {#common-errors}

| Feiceann tú | Déan seo |
|---|---|
| `'python' is not recognized` nó `command not found` | Níl Python ar PATH: rith an suiteálaí arís agus cuir tic i **Add python.exe to PATH**, ansin oscail teirminéal nua. Ar macOS/Linux bain triail as `python3`. |
| `No module named ...` | scipeáladh céim 4 nó ritheadh í i bhfillteán eile: úsáid `cd` chun dul go fillteán na huirlise agus rith arís í. |
| `pip is not recognized` | úsáid `python -m pip ...` in ionad `pip ...`. |
| `No such file or directory` / `can't open file` | tá an teirminéal sa fhillteán mícheart, nó tá an cosán clóscríofa go mícheart: seiceáil é, agus cuir cosáin a bhfuil spásanna iontu idir comharthaí athfhriotail. |
| téacs dearg ag críochnú le líne `error:` | léigh an líne dheireanach: deir sí cad atá ar iarraidh. Liostaíonn an leathanach [Orduithe](../commands.md) na teachtaireachtaí. |
