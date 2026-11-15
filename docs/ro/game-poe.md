---
title: "Path of Exile (fișiere de jurnal)"
nav_order: 36
lang: "ro"
source: game-poe.md
source_hash: "9facfd5a1551"
nav_exclude: true
search_exclude: true
---
# Path of Exile (fișiere de jurnal) {#path-of-exile-log-files}

Cât timp jucați Path of Exile, watcher-ul citește fișierele pe care le scrie jocul și salvează ce s-a întâmplat, ca să le puteți vedea mai târziu ca statistici și ca o cronologie.

*Detalii tehnice: adaptorul `poe`, tipul [`log`](sources-and-rules.md); rulează cât timp `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` sau `PathOfExile_x64_KG.exe` rulează și caută date noi la fiecare 0,5 s.*

## Ce se înregistrează {#what-is-recorded}

- zonele intrate, cu nivelul zonei, id-ul zonei și sămânța ei
- creșterile de nivel, cu clasa și nivelul
- morțile („has been slain”)
- jucătorii care intră și ies din zonă, șoaptele primite și trimise, cererile de comerț, comerțurile acceptate
- fiecare linie din Client.txt din această sesiune, întreagă, în heat.raw.parquet
- morți, niveluri câștigate, nivelul cel mai înalt, zone intrate, zone distincte, șoapte, cereri de comerț, comerțuri

## De unde vine {#where-it-comes-from}

&lt;install>\logs\Client.txt al Path of Exile sau Path of Exile 2 (urmărit; folderul de instalare este cel al executabilului care rulează)

## Cum se activează {#how-to-switch-it-on}

Nu trebuie activat nimic: watcher-ul citește sursa așa cum o oferă jocul sau platforma.

## Cum funcționează {#how-it-works}

Path of Exile și Path of Exile 2: jurnalul clientului, `<install>\logs\Client.txt`.

Ambele jocuri adaugă la un singur Client.txt din folderul lor de instalare, cât timp sunt instalate (fișierul crește de-a lungul pornirilor). Liniile arată așa:

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- ora locală, un contor de milisecunde, un hash, nivelul și firul, apoi ce arată fereastra de chat. Mesajele sunt ale clientului în engleză; un client într-o altă limbă le scrie traduse și nu sunt înțelese aici. Nimic nu dă o poziție. Formatul nu este documentat de Grinding Gear Games; este jurnalul text simplu al jocului, așa cum îl citesc de ani de zile uneltele comunității (aplicațiile de comerț, ghidurile de nivel) - de ex. <https://github.com/klayveR/poe-log-monitor> (MIT) pentru lista de evenimente.

Folderul de instalare este cel al executabilului care rulează; fără unul, se caută bibliotecile Steam și folderul implicit al clientului independent.

Fiecare linie a acestei sesiuni este păstrată întreagă în sidecar-ul brut al sesiunii (regula convertorului 3DHeat), indiferent dacă înseamnă ceva aici: `type` este nivelul și logger-ul din paranteze (`INFO Client`, `DEBUG Client`, `WARN Client`, ...), o linie cu ștampilă fără paranteze este `untagged`, o linie fără ștampilă de timp este `untimed`.

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

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează” de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- `You have entered <zone>`, cu nivelul zonei, id-ul zonei și sămânța din linia `Generating level` de dinaintea ei
- `<name> (<class>) is now level <n>`, `<name> has been slain`, jucători care intră și ies din zonă, șoapte primite și trimise (cu indicația dacă sunt cerere de comerț), comerțuri acceptate și anulate

**Păstrat brut**

- fiecare linie a acestei sesiuni întreagă, `type` = nivelul și logger-ul din paranteze (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client`, ...), `used` unde a devenit rând: chatul global, de comerț, de grup și de breaslă, `Connecting to instance server`, notificările AFK și DND, răspunsurile la comenzi de chat precum `/played` și `/deaths`, liniile de încărcare și de motor ale clientului - păstrate, încă nu transformate în rânduri
- o linie cu ștampilă fără paranteze (`***** LOG FILE OPENING *****`) ca `untagged`, o linie fără ștampilă de timp ca `untimed`

**Nu este disponibil**

- poziții: nimic din jurnal nu dă una
- ce scrie clientul într-o altă limbă: liniile sunt păstrate, dar doar mesajele în engleză sunt transformate în rânduri
- liniile din pornirile anterioare: Client.txt crește de-a lungul pornirilor; liniile ștampilate înainte de această rulare a jocului sunt lăsate (au fost păstrate când au fost jucate)
- uciderile, daunele, prada și arborele pasiv: jocul nu le jurnalizează

**Dimensiune**: Client.txt crește cu aproximativ 0,3-3 MB pe oră (cele mai multe din liniile DEBUG la încărcarea zonelor, mai multe cu chatul de comerț aglomerat); zstd din heat.raw.parquet îl face cam o zecime

## Verificat {#verified}

testat pe linii sintetice din Client.txt, în formatul jocului; netestat cu jocul

## Sursă {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
