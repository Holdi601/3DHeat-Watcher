---
title: "Star Citizen (fișiere de jurnal)"
nav_order: 42
lang: "ro"
source: game-starcitizen.md
source_hash: "6528f948d2e5"
nav_exclude: true
search_exclude: true
---
# Star Citizen (fișiere de jurnal) {#star-citizen-log-files}

Cât timp jucați Star Citizen, watcher-ul citește fișierele pe care le scrie jocul și salvează ce s-a întâmplat, ca să le puteți vedea mai târziu ca statistici și ca o cronologie.

*Detalii tehnice: adaptorul `starcitizen`, tipul [`log`](sources-and-rules.md); rulează cât timp `StarCitizen.exe` rulează și caută date noi la fiecare 0,5 s.*

## Ce se înregistrează {#what-is-recorded}

- morțile, cu victima, ucigașul, arma, tipul de daună și zona (jucători și PNJ-uri)
- vehicule scoase din luptă și distruse, cu pilotul, cauza și zona
- ținte de călătorie quantum, schimbări de sistem solar, apariții, reapariții, incapacitări
- fiecare linie din Game.log, întreagă, în heat.raw.parquet
- eliminări (jucător și PNJ), morți, sinucideri, vehicule distruse și pierdute, salturi quantum

## De unde vine {#where-it-comes-from}

&lt;install>\StarCitizen\LIVE\Game.log (folderul de build al StarCitizen.exe care rulează), doar fișierul de jurnal pe care îl scrie jocul - un joc cu Easy Anti-Cheat: nimic nu atinge procesul lui

## Cum se activează {#how-to-switch-it-on}

Nu trebuie activat nimic: watcher-ul citește sursa așa cum o oferă jocul sau platforma.

## Cum funcționează {#how-it-works}

Star Citizen: jurnalul propriu al clientului, `<install>\StarCitizen\LIVE\Game.log`.

Jocul scrie Game.log din nou la fiecare pornire (cel anterior merge în `logbackups\`). Doar acel fișier este citit: Star Citizen rulează Easy Anti-Cheat, iar aici nimic nu se apropie de procesul jocului. Liniile încep cu o ștampilă de timp UTC și un nivel, apoi o etichetă între paranteze unghiulare:

```text
<2025-04-13T17:17:51.279Z> [Notice] <Actor Death> CActor::Kill: 'Victim' [200146297631] in zone
    'ANVL_Hornet_F7A_Mk2_2677329226210' killed by 'Killer' [202061381370] using
    'GATS_BallisticGatling_S3_2677329225797' [Class unknown] with damage type 'VehicleDestruction'
    from direction x: 0.000000, y: 0.000000, z: 0.000000 [Team_ActorTech][Actor]
<...> [Notice] <Vehicle Destruction> CVehicle::OnAdvanceDestroyLevel: Vehicle 'ANVL_Arrow_123' [123] in zone
    'OOC_Stanton_1_Hurston' [pos x: 1.0, y: 2.0, z: 3.0 vel x: 0, y: 0, z: 0] driven by 'Driver' [456]
    advanced from destroy level 0 to 2 caused by 'Attacker' [789] with 'Combat' [Team_VehicleFeatures][Vehicle]
<...> [Notice] <AccountLoginCharacterStatus_Character> Character: createdAt 1 - updatedAt 2 - geid 3 -
    accountId 4 - name Handle - state STATE_CURRENT [Team_GameServices][Login]
<...> [Notice] <Quantum Navtarget> CSCItemQuantumDrive::RmMulticastOnQTToPoint : Local client user
    Handle[200000000001] received QT data for Entity:AEGS_Gladius_123[123] to Target Stanton1b ...
<...> [Notice] <Changing Solar System> ... Client entity Handle ... changing system from Stanton to Pyro ...
```

(împărțite aici pe mai multe rânduri; câte o linie fiecare în fișier). Zona unei morți este de obicei nava în care stătea victima, nu un loc. Formatul nu este documentat de Cloud Imperium și se schimbă între patch-uri; șabloanele urmează liniile pe care le citesc uneltele comunității de urmărire a eliminărilor (de ex. <https://github.com/DimmaDont/all-slain>, MIT - doar fapte), iar ce nu se potrivește este sărit, nu ghicit. `pos` unui vehicul este relativ la zonă și este păstrat doar ca text: nu se desenează nicio coordonată.

Fiecare linie este păstrată întreagă în sidecar-ul brut al sesiunii (regula convertorului 3DHeat), potrivită sau nu: `type` este eticheta liniei între paranteze unghiulare (`Actor Death`, `Spawn Flow`, ...), altfel primul ei cuvânt între paranteze (`Notice`, `CSessionManager::OnClientSpawned`), altfel `untagged`; o linie fără ștampilă de timp este `untimed`.

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

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează” de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- `<Actor Death>`: victima, ucigașul, arma și clasa ei, tipul de daună, zona; PNJ sau jucător
- `<Vehicle Destruction>`: vehiculul, zona, poziția relativă la zonă ca text, pilotul, cauza, modul, nivelul distrugerii
- ținte `<Quantum Navtarget>`, `<Changing Solar System>`, `OnClientSpawned`, reapariții la spital, incapacitări cu cauzele lor, `EndSession`
- jucătorul (handle-ul) din `<AccountLoginCharacterStatus_Character>` sau din linia de autentificare

**Păstrat brut**

- fiecare linie din Game.log întreagă, `type` = eticheta ei între paranteze unghiulare (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), altfel primul cuvânt între paranteze (`Notice`, `CSessionManager::OnClientSpawned`, ...), altfel `untagged`; liniile fără ștampilă de timp (antetul jurnalului, text rupt pe rânduri) ca `untimed`; `used` unde linia a devenit rând

**Nu este disponibil**

- poziții: jurnalul nu dă niciuna într-un cadru care poate fi desenat (`pos` unui vehicul distrus este relativ la o zonă al cărei loc nu este jurnalizat)
- orice din procesul sau din rețeaua jocului: Star Citizen rulează Easy Anti-Cheat; se citește doar fișierul de jurnal
- jurnalele din pornirile anterioare (`logbackups`): Game.log al fiecărei porniri este păstrat când este jucat
- linii într-un format pe care un patch îl schimbă: păstrate brut, decodate din nou când se cunoaște forma nouă

**Dimensiune**: Game.log crește cu aproximativ 5-15 MB pe oră de joc (mai mult în zonele aglomerate și cu erori); zstd din heat.raw.parquet îl face cam o zecime

## Verificat {#verified}

testat pe linii sintetice din Game.log, în formatul documentat de uneltele comunității; netestat cu jocul

## Sursă {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
