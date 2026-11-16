---
title: "VALORANT (reluări)"
nav_order: 45
lang: "ro"
source: game-valorant-replays.md
source_hash: "10a648aabdf1"
nav_exclude: true
search_exclude: true
---
# VALORANT (reluări) {#valorant-replays}

După un meci din VALORANT, watcher-ul transformă reluarea salvată de joc în fișiere pe care le puteți privi sub formă de statistici și cronologie.

*Detalii tehnice: adaptorul `valorant-replays`, tipul [`replay`](sources-and-rules.md); rulează tot timpul (nu așteaptă pornirea unui joc) și caută date noi la fiecare 5 s.*

## Ce se înregistrează {#what-is-recorded}

- harta, id-ul meciului și agenții aleși; blocul de informații al reluării (durata, versiunile, numele, steagurile de compresie și criptare, momentul înregistrării)
- cronologia evenimentelor serverului: uciderile (ucigașul și victima ca id-uri de rețea), începutul rundelor, bombele plantate, dezactivate și explodate, ultimele folosite, schimbarea părților - fiecare cu id-ul și metadatele sale
- fiecare parte a fișierului, întreagă, în heat.raw.parquet; nedecodat: pozițiile, numele sau scorurile - sunt în fluxul ofuscat

## De unde vine {#where-it-comes-from}

reluările salvate de VALORANT: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (doar părțile care nu sunt ofuscate)

## Cum se activează {#how-to-switch-it-on}

salvați o reluare în VALORANT (carieră > meci > descărcare reluare)

## Cum funcționează {#how-it-works}

League of Legends și reluările VALORANT: ce se poate citi din ele așa cum sunt.

Ambele jocuri salvează reluările pe discul jucătorului și protejează ce se află înăuntru: datele jocului clip cu clip sunt ofuscate, și diferit la fiecare actualizare, ca să nu poată fi folosite pentru trișare. Această parte nu este decodată nicăieri în 3DHeat. Ce transportă fiecare fișier în clar se citește, iar restul se păstrează așa cum este: fiecare parte a fișierului, întreagă, în `heat.raw.parquet` al sesiunii (regula convertorului 3DHeat, docs/converters.md din repository-ul vizualizatorului), numărată în `selfCheck.completeness` din meta.json.

#### Valorant (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, o reluare locală Unreal Engine (layoutul după vrfkit, Apache-2.0, și ValorantReplayParser, MIT). În clar: blocul de informații al reluării (durata, versiunea de rețea, changelist-ul, numele ei, momentul înregistrării, dacă este comprimată sau criptată), harta, id-ul meciului și agenții aleși (în antet), și cronologia evenimentelor proprii ale serverului - uciderile (ucigașul și victima ca id-uri de rețea, nu nume), începutul rundelor, bombele plantate, dezactivate și explodate, ultimele folosite, schimbarea părților - fiecare cu timpul, id-ul și metadatele sale. Pozițiile, numele, scorurile și tot restul se află în fluxul ofuscat (chunk-urile de date ale reluării și de checkpoint), care se păstrează întreg și nu se citește.

Același modul servește și: [League of Legends (reluări)](game-lol-replays.md).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | nu |
| Axa verticală | `z` |
| Unități | unitățile lumii VALORANT |
| Oglindit pentru vizualizator | niciunul |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, ca vizualizatorul 3DHeat să rotească și să scaleze rândurile singur; vedeți [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)".
- Tipul `replay`: citește doar ce oferă jocul sau platforma (reluările și demo-urile pe care le salvează jocul), deci înregistrează și în jocul online, nu doar offline; marcajul decide doar dacă memoria poate fi citită vreodată.
- Memoria: **niciodată** citită de acest adaptor. Doar adaptoarele de tip `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online; vedeți [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul adaptorului le setează pe nume (fiecare `stats` din sesiune, în `meta.json`, și tabelul `stats` din `watcher.sqlite`):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează" de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- blocul de informații, fiecare câmp (`vrf` din meta.json): versiunea fișierului, versiunile personalizate, durata, versiunea de rețea, changelist-ul, numele, steagul de viu, momentul înregistrării, steagurile de comprimare și criptare, cheia așa cum este stocată
- chunk-ul de antet: harta, id-ul meciului și agenții aleși (recunoscuți după forma lor)
- fiecare chunk de eveniment: id, grup, metadate, timpul de început și de sfârșit, iar din datele lui numele evenimentului, timpul său în secunde și numerele dinaintea lui (id-urile de rețea ale ucigașului și victimei) - un rând fiecare

**Păstrat brut**

- fiecare chunk întreg, în ordinea din fișier (`offset`), astfel încât părțile sunt fișierul: `info`, `header`, `event <grup>`, `replay_data`, `checkpoint`, `chunk <n>` pentru un tip pe care layoutul nu îl numește, `trailing` pentru octeții de după ultimul chunk întreg

**Nu este disponibil**

- pozițiile, numele, scorurile, abilitățile, fiecare cadru al jocului: chunk-urile de date ale reluării și de checkpoint sunt ofuscate. Păstrate întregi, nu citite
- conținutul unei reluări criptate: parcursă și păstrată întreagă, nimic citit înăuntru

**Dimensiune**: sidecarul brut are cam dimensiunea reluării: fluxul ofuscat nu se comprimă

## Verificat {#verified}

construit după layoutul containerului documentat de vrfkit (Apache-2.0); netestat pe o reluare reală, nicio reluare nu a fost disponibilă - verifică înainte de citire și sare peste ce nu se potrivește

## Sursă {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
