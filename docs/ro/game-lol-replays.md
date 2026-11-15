---
title: "League of Legends (reluări)"
nav_order: 30
lang: "ro"
source: game-lol-replays.md
source_hash: "216b88922360"
nav_exclude: true
search_exclude: true
---
# League of Legends (reluări) {#league-of-legends-replays}

După un meci din League of Legends, watcher-ul transformă reluarea salvată de client în fișiere pe care le puteți privi pe o hartă în vizualizatorul 3DHeat.

*Detalii tehnice: adaptorul `lol-replays`, tipul [`replay`](sources-and-rules.md); rulează tot timpul (nu așteaptă pornirea unui joc) și caută date noi la fiecare 5 s.*

## Ce se înregistrează {#what-is-recorded}

- fiecare jucător: campionul, rolul, echipa, uciderile, morțile, asistențele, aurul, daunele aduse campionilor și rezultatul, și fiecare alt număr din tabelul de scor de la sfârșitul jocului
- rândul tău ca statistici proprii, iar rândurile tale marcate ca ale tale (meta.json `player`), cu Riot ID-ul tău în setări
- cu propria cheie API Riot: poziția fiecărui jucător la fiecare minut cu statisticile minutului, și fiecare eveniment din cronologie (uciderile acolo unde s-au produs, clădirile, monștrii, ward-urile, obiectele, abilitățile), la ora de ceas dată de cronologie
- fiecare parte a fișierului de reluare, întreagă, în heat.raw.parquet; nedecodat: jocul clip de clip, care este criptat și ofuscat împotriva trișării

## De unde vine {#where-it-comes-from}

reluările salvate de clientul League: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (doar metadatele simple de la sfârșitul jocului); cu propria cheie API Riot, cronologia oficială a meciului din Match-V5 API-ul Riot

## Cum se activează {#how-to-switch-it-on}

salvați o reluare în clientul League (istoric meciuri > descărcare); pentru poziții setați riot_api_key și riot_platform cu `config --set`

## Cum funcționează {#how-it-works}

League of Legends și reluările VALORANT: ce se poate citi din ele așa cum sunt.

Ambele jocuri salvează reluările pe discul jucătorului și protejează ce se află înăuntru: datele jocului clip cu clip sunt ofuscate, și diferit la fiecare actualizare, ca să nu poată fi folosite pentru trișare. A le trece de această protecție înseamnă a desface codul jocului, ceea ce termenii Riot interzic (Termenii de utilizare 3.1 și 7.1) - deci nu se face aici. Ce transportă fiecare fișier în clar se citește, iar restul se păstrează așa cum este: fiecare parte a fișierului, întreagă, în `heat.raw.parquet` al sesiunii (regula convertorului 3DHeat, docs/converters.md din repository-ul vizualizatorului), numărată în `selfCheck.completeness` din meta.json.

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Ambele versiuni de container poartă tabelul de scor de la sfârșitul jocului ca JSON simplu (`statsJson`): pentru fiecare dintre cei zece jucători campionul, uciderile, morțile, asistențele, aurul, daunele aduse campionilor, obiectele, echipa, rolul, victoria, Riot ID-ul lor și fiecare alt număr pe care jocul îl totalizează (peste o sută pe jucător); toate devin rândul `player_result` al jucătorului. ROFL1 (patch 14.9 și anterior) îl are după un antet fix (`RIOT\0\0`, o semnătură de 256 de octeți, apoi lungimile); ROFL2 (14.11 încoace, `RIOT\2\0`) la sfârșitul fișierului, cu lungimea în ultimii patru octeți (afirmat de un inginer Riot, ReplayBook issue 299). Antetul payload-ului ROFL1 (id-ul jocului, lungimea, numărul de chunk-uri și de keyframe-uri, lungimea cheii chunk-ului) și tabelul de chunk-uri (id, tip, lungime, chunk-ul următor, offset) sunt în clar și se citesc; chiar chunk-urile sunt criptate și se păstrează întregi, necitite. Layouturile provin din roflxd.cs (MIT).

Pozițiile nu vin din fișier. Cu o cheie de dezvoltator Riot a jucătorului însuși (`riot_api_key` din setări; o cheie personală este făcută tocmai pentru „afișarea statisticilor proprii ale jucătorului"), cronologia oficială a meciului este luată din Match-V5 API-ul Riot: poziția fiecărui jucător o dată pe minut, cu tot ce spune cadrul minutului despre el (aur, experiență, nivel, minioni, statisticile campionului și ale daunelor), și fiecare eveniment al cronologiei - uciderile, clădirile, monștrii elită, ward-urile, obiectele, abilitățile, nivelurile - fiecare ca rând, plasat unde are un loc. Fără cheie nu se ia și nu se trimite nimic.

Același modul servește și: [VALORANT (reluări)](game-valorant-replays.md).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa verticală | `y` |
| Unități | unitățile hărții Summoner's Rift (cam 15000 de la un capăt la altul) |
| Oglindit pentru vizualizator | niciunul |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, ca vizualizatorul 3DHeat să rotească și să scaleze rândurile singur; vedeți [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)".
- Tipul `replay`: citește doar ce oferă jocul sau platforma (reluările și demo-urile pe care le salvează jocul), deci înregistrează și în jocul online, nu doar offline; marcajul decide doar dacă memoria poate fi citită vreodată.
- Memoria: **niciodată** citită de acest adaptor. Doar adaptoarele de tip `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online; vedeți [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul adaptorului le setează pe nume (fiecare `stats` din sesiune, în `meta.json`, și tabelul `stats` din `watcher.sqlite`):

`champion`, `game_seconds`, `won`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează" de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- fișierul JSON de metadate: durata jocului, versiunea, id-urile ultimului chunk și keyframe, și `statsJson` - fiecare câmp din tabelul de scor al fiecărui jucător, pe rândul său `player_result` (numerele date ca text se citesc ca numere)
- ROFL1: blocul de lungimi, antetul payload-ului (id-ul jocului, durata jocului, numărul de keyframe-uri și chunk-uri, id-urile chunk-urilor de pornire și de începere a jocului, intervalul keyframe-urilor, cheia chunk-ului așa cum este stocată) și tabelul de chunk-uri (id, tip, lungime, chunk-ul următor, offset) - în `rofl` din meta.json și în `text` rândurilor brute
- ROFL2: șirul de versiune
- cronologia Match-V5 (doar cu cheia API proprie): fiecare cadru de participant pe un rând `position` (sau `participant_frame` fără loc), cu toate câmpurile lui aplatizate (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...); fiecare eveniment ca rând, numit după tipul lui, plasat acolo unde are un `position`, CHAMPION_KILL ca ucidere și moarte

**Păstrat brut**

- fiecare parte a fișierului .rofl, întreagă, în ordinea din fișier (`offset`), astfel încât părțile sunt fișierul: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); orice porțiune pe care nicio parte n-o acoperă ca `unknown`
- cronologia întreagă: `timeline <type>` pentru fiecare eveniment, `timeline participantFrame` pentru cadrul fiecărui jucător (`participant` id-ul său), `timeline` pentru rest

**Nu este disponibil**

- jocul însuși (pozițiile, abilitățile, fiecare unitate, clip cu clip): chunk-urile ROFL1 și corpul ROFL2 sunt criptate, iar pachetele din interior sunt ofuscate la fiecare patch; a le trece înseamnă a desface clientul, ceea ce termenii Riot interzic (3.1, 7.1). Păstrate întregi, nu citite
- pozițiile fără cheia proprie de API Riot: fișierul nu le are în clar

**Dimensiune**: sidecarul brut are cam dimensiunea reluării: chunk-urile criptate nu se comprimă

## Verificat {#verified}

cititorul de metadate testat pe fișiere construite după layourile din roflxd.cs (MIT); cronologia după JSON-ul documentat al Match-V5; nicio reluare reală nu a fost disponibilă pentru verificare

## Sursă {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
