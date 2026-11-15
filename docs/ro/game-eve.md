---
title: "EVE Online (fișiere de jurnal)"
nav_order: 20
lang: "ro"
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (fișiere de jurnal) {#eve-online-log-files}

Cât timp jucați EVE Online, watcher-ul citește fișierele pe care le scrie jocul și salvează ce s-a întâmplat, ca să le puteți vedea mai târziu ca statistici și ca o cronologie.

*Detalii tehnice: adaptorul `eve`, tipul [`log`](sources-and-rules.md); rulează cât timp `exefile.exe` rulează și caută date noi la fiecare 0,5 s.*

## Ce se înregistrează {#what-is-recorded}

- daune date și primite de la cealaltă navă, pilot, sigla corporației, armă și calitatea lovirii
- ratări date și primite
- recompense de vânătoare plătite (pentru PNJ-uri) cu ISK
- salturi între sisteme
- fiecare linie din gamelog și din jurnalul de chat, întreagă, în heat.raw.parquet
- daune date și primite, lovituri, ratări, vânători plătite și ISK, salturi

## De unde vine {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt și Chatlogs\\\*.txt de lângă ele (fiecare fișier scris de la pornirea clientului)

## Cum se activează {#how-to-switch-it-on}

Nu trebuie activat nimic: watcher-ul citește sursa așa cum o oferă jocul sau platforma.

## Cum funcționează {#how-it-works}

EVE Online: jurnalele de joc ale clientului, `Documents\EVE\logs\Gamelogs\*.txt`.

Clientul scrie câte un fișier pentru fiecare personaj și fiecare autentificare, `<yyyymmdd>_<hhmmss>[_<id personaj>].txt`; scrierea în fișier este activă implicit. Mai mulți clienți care rulează unul lângă altul scriu fiecare propriul fișier, așa că se urmărește fiecare fișier scris de la pornirea jocului. Antetul și liniile (ora EVE este UTC):

```text
------------------------------------------------------------
  Gamelog
  Listener: Character Name
  Session Started: 2024.07.02 19:41:40
------------------------------------------------------------
[ 2024.07.02 20:31:28 ] (combat) <color=0xff00ffff><b>200</b> <color=0x77ffffff><font size=10>to</font>
    <b><color=0xffffffff>Pilot[TICK](../Ship)</b><font size=10><color=0x77ffffff> - Weapon - Penetrates
[ 2024.06.25 15:20:01 ] (combat) <color=0xffcc0000><b>375</b> ... from ... - Weapon - Hits
[ 2024.06.25 15:21:00 ] (bounty) <font size=12><b><color=0xff00aa00>15,000 ISK</b> added to next bounty payout
[ 2024.06.25 15:30:00 ] (None) Jumping from System A to System B
```

(linia de combat este o singură linie în fișier). Etichetele de formatare sunt șterse înainte de potrivire. Fișierul a fost UTF-8 și UTF-16 de-a lungul anilor; se citesc ambele. Formatul nu este documentat de CCP; este jurnalul text simplu al clientului, citit așa cum citesc uneltele comunității de jurnal de luptă (de ex. <https://docs.rs/crate/eve-log-parser>). Fără poziții.

Alături, `Documents\EVE\logs\Chatlogs\<channel>_<yyyymmdd>_<hhmmss>[_<id>].txt`: câte un fișier pentru fiecare canal de chat și fiecare autentificare (când jurnalizarea chatului este activă, implicit în client), UTF-16, un antet care numește canalul și ascultătorul, apoi `[ yyyy.mm.dd hh:mm:ss ] Expeditor > mesaj`.

Fiecare linie din ambele este păstrată întreagă în sidecar-ul brut al sesiunii (regula convertorului 3DHeat): o linie de gamelog sub canalul ei între paranteze (`combat`, `notify`, `bounty`, `None`, ...), o linie de chat ca `chat` cu canalul ei, liniile de antet ca `gamelog header` / `chatlog header`.

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | nu |
| Axa verticală | `y` |
| Unități | nu se înregistrează poziții |
| Oglindit pentru vizualizator | niciunul |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, ca vizualizatorul 3DHeat să rotească și să scaleze rândurile singur; vedeți [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)”.
- Tipul `log`: citește doar ce oferă jocul sau platforma (fișiere pe care le scrie jocul cât timp rulează), deci înregistrează și în jocul online, nu doar offline; marcajul decide doar dacă memoria poate fi citită vreodată.
- Memoria: **niciodată** citită de acest adaptor. Doar adaptoarele de tip `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online; vedeți [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul adaptorului le setează pe nume (fiecare `stats` din sesiune, în `meta.json`, și tabelul `stats` din `watcher.sqlite`):

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează” de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- `(combat)` din gamelog: lovituri date și primite (cantitatea, celălalt pilot, sigla corporației, nava, arma, calitatea lovirii) și ratările în ambele sensuri
- `(bounty)` din gamelog: plăți cu ISK și liniile `Jumping from A to B`
- ascultătorul din antetul gamelog-ului: al cui este jurnalul

**Păstrat brut**

- fiecare linie de gamelog întreagă, `type` = canalul ei între paranteze (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), cu `file` și `listener`; `used` unde a devenit rând; liniile de antet ca `gamelog header`
- fiecare linie de chat întreagă (Local, corporație, flotă, canale private, anunțurile `EVE System` precum schimbarea canalului Local la un salt), `type` `chat`, cu `channel`, `listener` și `file`; liniile de antet ca `chatlog header`. Încă nu sunt făcute rânduri
- etichetele de formatare (`<color>`, `<b>`, `<font>`) rămân în textul brut; rândurile le au șterse

**Nu este disponibil**

- poziții: clientul nu scrie niciuna în jurnalele sale
- luptele altor piloți: un gamelog este al ascultătorului
- jurnalele din autentificările anterioare: fiecare autentificare scrie fișiere noi; cele mai vechi decât această rulare a clientului nu se mai citesc
- chatul când jucătorul a oprit jurnalizarea chatului din setările clientului
- fișierele de cache și de setări ale clientului: nu sunt jurnale, și nu sunt documentate

**Dimensiune**: un gamelog are 0,1-2 MB pe oră (cele mai multe în luptă); jurnalele de chat depind de canalele deschise - un canal Local sau de flotă aglomerat, 0,5-3 MB pe oră; zstd din heat.raw.parquet le face cam o zecime

## Verificat {#verified}

testat pe linii sintetice de gamelog, în formatul publicat de analizoarele comunității; netestat cu jocul

## Sursă {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
