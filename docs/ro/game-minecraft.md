---
title: "Minecraft (fișiere de jurnal)"
nav_order: 33
lang: "ro"
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (fișiere de jurnal) {#minecraft-log-files}

Cât timp jucați Minecraft, watcher-ul citește fișierele pe care le scrie jocul și salvează ce s-a întâmplat, ca să le puteți vedea mai târziu pe o hartă în vizualizatorul 3DHeat.

*Detalii tehnice: adaptorul `minecraft`, tipul [`log`](sources-and-rules.md); rulează cât timp `javaw.exe` sau `java.exe` este pornit și caută date noi la fiecare 0,5 s.*

## Ce se înregistrează {#what-is-recorded}

- poziția ta și a celorlalți jucători (blocuri = m, y în sus) de fiecare dată când se salvează lumea; dimensiunea ca sesiune
- apariția cu poziție când un jucător se conectează la serverul (integrat)
- intrări, ieșiri, morți cu mesajul morții, progrese, linii de chat
- morți, progrese, mesaje de chat; din fișierul de statistici: timpul de joc, distanța, uciderile de mobi și de jucători, săriturile, daunele, blocurile sparte, obiectele fabricate (partea din această sesiune)
- fiecare linie de jurnal și fiecare statistică, progres și fișier de jucător salvat, întregi, în heat.raw.parquet

## De unde vine {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (urmărit), saves\\&lt;lume>\stats\\&lt;uuid>.json și saves\\&lt;lume>\playerdata\\&lt;uuid>.dat și level.dat (NBT comprimat gzip), citite când jocul le salvează

## Cum se activează {#how-to-switch-it-on}

Nu trebuie activat nimic: watcher-ul citește sursa așa cum o oferă jocul sau platforma.

## Cum funcționează {#how-it-works}

Minecraft (Java Edition): jurnalul, statisticile și fișierele de jucător pe care le scrie jocul.

Unde (`%APPDATA%\.minecraft\`):

* `logs\latest.log` - jurnalul jocului, nou la fiecare pornire (cel vechi este împachetat într-un .log.gz datat). Linii `[hh:mm:ss] [fir/NIVEL]: mesaj` (încărcătoarele de moduri scriu `[ddMMMyyyy hh:mm:ss.mmm] [fir/NIVEL] [logger/]: ...`). Ce văd jucătorii în chat se află aici: intrările și ieșirile, mesajele morții, progresele, chat-ul - serverul integrat al unei lumi single-player scrie aceleași linii încă o dată, deci o linie repetată în aceeași secundă se numără o dată. „Setting user: <nume>" numește jucătorul; linia serverului „<nume>[...] logged in with entity id N at (x, y, z)" arată unde a apărut.
* `saves\<lume>\stats\<uuid>.json` - ecranul de statistici, scris când se salvează lumea (salvare automată la fiecare câteva minute și la ieșire): `stats` -> `minecraft:custom` (play_time în ticuri, mob_kills, distanțele \*_one_cm, jump, ...), `minecraft:mined`, `minecraft:crafted`, ... Totaluri pentru lume; cifrele sesiunii sunt diferența față de ce spunea fișierul când a pornit jocul. Format: <https://minecraft.wiki/w/Statistics>
* `saves\<lume>\playerdata\<uuid>.dat` (și `level.dat` -> Data -> Player pentru gazda single-player) - NBT comprimat gzip, scris la aceleași salvări: `Pos` [x, y, z] ca double, `Rotation` [yaw, pitch], `Dimension` („minecraft:overworld"; un int 0/-1/1 înainte de 1.16). NBT conform <https://minecraft.wiki/w/NBT_format> - citit aici de un cititor mic de-al nostru.
* `saves\<lume>\advancements\<uuid>.json` - progresul din ecranul de progrese, scris la aceleași salvări.

Coordonatele sunt în blocuri, un bloc un metru, y în sus; x est, z sud - un cadru drept, desenat așa cum este. Pozițiile vin doar când se salvează lumea, deci un traseu are câteva puncte pe fiecare salvare automată, nu o urmă continuă; dimensiunea este `session`, astfel că Nether-ul nu se desenează peste Overworld.

Tot ce se citește se păstrează întreg în sidecarul brut al sesiunii (regula convertorului 3DHeat): fiecare linie de jurnal sub nivelul ei (`INFO`, `WARN`, `ERROR`, ...; o linie fără capul din paranteze, precum o urmă de stivă, ca `untagged`), iar fiecare fișier salvat sub tipul lui (`stats`, `advancements`, `playerdata`, `level.dat`) - JSON ca text, NBT ca octeții lui. Cifrele unui fișier de statistici se înțeleg doar față de ce spunea el când a pornit jocul, deci și acea primă copie se păstrează (`baseline`), prima dată când se schimbă fișierul.

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa verticală | `y` |
| Unități | blocuri (1 bloc = 1 m) |
| Oglindit pentru vizualizator | niciunul |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, ca vizualizatorul 3DHeat să rotească și să scaleze rândurile singur; vedeți [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)".
- Tipul `log`: citește doar ce oferă jocul sau platforma (fișierele pe care le scrie jocul cât timp rulează), deci înregistrează și în jocul online, nu doar offline; marcajul decide doar dacă memoria poate fi citită vreodată.
- Memoria: **niciodată** citită de acest adaptor. Doar adaptoarele de tip `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online; vedeți [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul adaptorului le setează pe nume (fiecare `stats` din sesiune, în `meta.json`, și tabelul `stats` din `watcher.sqlite`):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează" de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- latest.log: numele jucătorului (`Setting user`), conectările cu poziția, intrările, ieșirile, morțile cu mesajul morții, progresele, liniile de chat, oprirea serverului
- stats/<uuid>.json: timpul de joc, distanța, uciderile de mobi și de jucători, săriturile, daunele date și primite, blocurile sparte, obiectele fabricate - partea din această sesiune
- playerdata/<uuid>.dat și level.dat (NBT): poziția, dimensiunea, yaw, pitch, viața, nivelul de experiență

**Păstrat brut**

- fiecare linie din latest.log, întreagă, `type` = nivelul ei (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`), cu firul loggerului în `thread`, `used` acolo unde a devenit rând; o linie fără capul din paranteze (o urmă de stivă, un banner de mod) ca `untagged`
- fiecare stats/<uuid>.json, întreg, ca text, `type` `stats` (`used`: cifrele lui sunt în statistici), cu prima copie de la pornirea jocului ca `baseline`
- fiecare advancements/<uuid>.json, întreg, ca text, `type` `advancements` (fiecare criteriu și momentul în care a fost îndeplinit; încă nu sunt transformate în rânduri)
- fiecare playerdata/<uuid>.dat și level.dat, întregi, ca octeți (NBT comprimat gzip), `type` `playerdata` / `level.dat`, `used` acolo unde a dat o poziție: inventarul, lada de ender, efectele, punctul de apariție, regulile jocului, sămânța lumii și ora există doar aici
- fiecare fișier salvat are `world` și `file` (calea lui sub `saves`)

**Nu este disponibil**

- o urmă a poziției: jocul scrie poziția jucătorului doar când se salvează lumea (la fiecare câteva minute și la ieșire)
- poziții pe un server găzduit de altcineva: fișierele lui de lume sunt pe server, nu aici; se citește doar jurnalul în acel caz
- lumea însăși (fișierele region .mca, entitățile, hărțile data/\*.dat și raidurile): mari, iar terenul nu este jocul
- jurnalele sesiunilor anterioare (logs/\*.log.gz): sunt păstrate când au fost jucate
- Bedrock Edition: nu scrie un astfel de jurnal sau astfel de fișiere

**Dimensiune**: latest.log 0,1-2 MB pe oră (mai mult cu moduri); un fișier de statistici 5-50 KB și un fișier de jucător 5-100 KB la fiecare salvare automată, level.dat 1-20 KB - în total cam 1-5 MB pe oră; zstd din `heat.raw.parquet` face textul cam o zecime (fișierele NBT sunt deja comprimate gzip)

## Verificat {#verified}

testat pe linii de jurnal sintetice, JSON de statistici și fișiere NBT construite după formatele publicate; netestat cu jocul

## Sursă {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
