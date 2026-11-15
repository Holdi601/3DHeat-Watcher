---
title: "Automobilista 2 (živi podatki)"
nav_order: 6
lang: "sl"
source: game-automobilista-2.md
source_hash: "5e3ca1507524"
nav_exclude: true
search_exclude: true
---
# Automobilista 2 (živi podatki) {#automobilista-2-live-data}

Medtem ko igrate Automobilista 2, watcher shrani podatke, ki jih igra sama pošilja ven, da si jih lahko pozneje ogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `automobilista-2`, vrsta [`telemetry`](sources-and-rules.md); teče, medtem ko se izvaja `AMS2AVX.exe` ali `AMS2.exe`, in vsakih 0,1 s preverja nove podatke.*

## Kaj se zapiše {#what-is-recorded}

- položaj (svetovne koordinate XYZ, m) vsakega avtomobila desetkrat na sekundo, po imenu voznika, lastni avto označen, s hitrostjo in uvrstitvijo; lastna prestava, plin, zavora
- začetek seje s progo, ki jo poimenuje igra; krogi po avtomobilih s časom kroga; cilji; lastni postanki v boksih
- teleporti (vrnitev v bokse, ponovni zagon): `teleport`, kje je bil avtomobil, `spawn`, kje je zdaj
- lastni krogi, najboljši krog, uvrstitev, razdalja, najvišja hitrost
- celotna stran skupnega pomnilnika igre v `heat.raw.parquet`, ob vsaki spremembi

## Od kod prihajajo {#where-it-comes-from}

skupni pomnilnik $pcars2$ (postavitev SMS SharedMemory.h)

## Kako vklopiti {#how-to-switch-it-on}

V igri: Options > System > Shared Memory: "Project CARS 2"

## Kako deluje {#how-it-works}

Skupni pomnilnik, ki ga dirkalne simulacije objavljajo za nadzorne plošče, odprt samo za branje - in
nikoli ustvarjen.

Več simulacij svojo telemetrijo objavlja kot imenovano preslikavo datoteke v Windows, ki jo igra
ustvari in jo lahko vsak prebere: Kunosove strani `Local\acpmf_*` (Assetto Corsa,
ACC, AC Rally, AC EVO-jeve `Local\acevo_pmf_*`), iRacingova
`Local\IRSDKMemMapFileName`, RaceRoomova `$R3E`, Automobilista 2 / Project CARS 2 `$pcars2$`.

Zakaj ne `mmap.mmap(-1, size, tagname=...)`, ki je sicer običajen način v Pythonu: ko preslikava
še ne obstaja, jo *ustvari* - tu samo za branje. Igra, zagnana kasneje, odpre watcherjevo preslikavo
namesto svoje in potem vanjo ne more pisati, zato je njena telemetrija mrtva, dokler watcher ne izpusti.
Watcher adapter zažene takoj, ko se pojavi proces igre, in to je ravno trenutek, ko igra še ni
ustvarila svoje preslikave. Zato to odpre z `OpenFileMappingW`, ki res najde samo obstoječo
preslikavo, jo preslika z `FILE_MAP_READ` in sicer javi "še ni tu"; adapterji poskusijo
čez trenutek znova.

Nič tukaj ne more pisati: pogled je preslikan samo za branje in se iz njega kopira samo z
`ctypes.string_at`.

Tu se berejo tudi dve igri; vsi avtomobili na progi so na njunih straneh.

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

SMS-ova `SharedMemory.h` (priložena v mapi Support\SharedMemory igre;
AMS2: Options > System > Shared Memory "Project CARS 2"), `#pragma pack(4)`.
`mParticipantInfo[64]` od bajta 28, po 100 bajtov vsak: mIsActive, mName[64],
mWorldPosition[3] (m, y navzgor), mCurrentLapDistance, mRacePosition,
mLapsCompleted, mCurrentLap, mCurrentSector; mViewedParticipantIndex (20)
je avto igralca; za vsakega udeleženca mLastLapTimes (9200), mRaceStates
(9520), mSpeeds (10800); igralčev mBestLapTime (6716), mLastLapTime
(6720), mSpeed (6848), mBrake, mThrottle, mGear; mSequenceNumber (7320) je
lih, medtem ko igra piše. Odmiki so bili določeni iz dveh neodvisnih
kopij glave (igrina lastna kopija ni nameščena tukaj), ki se ujemata.

Obe strani se poleg tega shranita celi (docs/converters.md, "Live sources"): celotna
preslikava, ob vsakem branju, katerega bajti se razlikujejo od zadnje shranjene kopije, v
surovi spremljevalni datoteki seje pod `type` `r3e` ali `pcars2` - vsaka reža voznika in vsako polje
strukture, tudi tista, ki tukaj niso prebrana, da kasnejši dekoder potrebuje samo spremljevalno datoteko.

Isti modul streže tudi: [Project CARS 2 (živi podatki)](game-project-cars-2.md), [RaceRoom Racing Experience (živi podatki)](game-raceroom.md).

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Zabeleženi položaji | da |
| Navpična os | `y` |
| Enote | metri |
| Zrcaljenje za pregledovalnik | brez |
| Merilo enote (`scale`: pregledovalnik z njim pomnoži položaje) | 1 |

Te vrednosti gredo v `meta.json` vsake seje (`axes`) in, kadar seja vsebuje položaje, v nogo `heat.parquet`, zato pregledovalnik 3DHeat vrti in meri vrstice sam - glejte [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igranje na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `telemetry`: bere samo, kar igra ali platforma ponudi (UDP vrata ali skupni pomnilnik, ki ga igra objavlja), zato zapisuje tudi pri igri na spletu in ne samo offline; zastavica odloča samo o tem, ali sme kdaj brati pomnilnik.
- Pomnilnik: tega adapterja **nikoli** ne bere. Samo adapterji vrste `memory` berejo pomnilnik, in nikoli za igro, označeno kot igranje na spletu - glejte [Viri in pravila](sources-and-rules.md).

## Zabeležene statistike {#statistics-recorded}

Ključi statistik, ki jih koda tega adapterja nastavlja po imenu (`stats` v `meta.json` vsake seje in tabela `stats` v `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

Ključ v zavitih oklepajih se dokonča med delovanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz imen statistik igre, na tem seznamu niso; zgoraj v "Kaj se zapiše" so našteti.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir ima, se prebere ali shrani, nikoli ne izgine. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani nedotaknjen v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in polja, shranjena po imenu; `used` označuje, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- za vsakega udeleženca (do 64): aktiven, ime, svetovni položaj, uvrstitev, opravljeni krogi; njegov zadnji čas kroga, stanje dirke in hitrost
- avto igralca (mViewedParticipantIndex), stanje igre in seje, lokacija in različica proge, najboljši in zadnji krog, hitrost, zavora, plin, prestava; mSequenceNumber, da se preskoči kopija, ujeta med pisanjem
- odmiki iz dveh neodvisnih kopij SMS-ovega SharedMemory.h, ki se ujemata, preverjeni na strani, zgrajeni iz njiju v testih; še ne na igri

**Shranjeno surovo**

- `pcars2`: celotna preslikava $pcars2$ - struktura sega daleč čez 11.312 bajtov, ki se tu berejo - ob vsakem branju, katerega bajti se razlikujejo od zadnje shranjene kopije: vsaka usmerjenost udeleženca, časi sektorjev, imena avtomobilov in razredov, načini in zastavice boksov, fizika igralca, pnevmatike, vzmetenje, poškodbe, vreme in vse, kar so kasnejše različice Automobilista 2 dodale
- `used` je resničen za stran, prebrano v vrstice; false za stran v menijih, med pavzo, v ponovitvi, drugačne postavitve ali ujeto med pisanjem (`torn` 1); `unchanged_reads` v meta.json šteje branja, ki so bajt za bajtom enaka prej shranjeni kopiji

**Ni na voljo**

- vnosi in fizika drugih udeležencev: stran daje samo gledani avto
- vse, medtem ko je v igri možnost skupnega pomnilnika izklopljena (Automobilista 2 takrat ne piše nič)

**Velikost**: preslikava meri približno 20 do 30 KB (glede na različico igre), do 10-krat na sekundo med vožnjo: približno 0,7 do 1,1 GB na uro pred stiskanjem; zstd skrči prazne reže udeležencev in imena, ki se ne spreminjajo, na delček (še ni izmerjeno na pravi seji)

## Preverjeno {#verified}

preizkušeno na strani, zgrajeni v testu; odmiki iz dveh neodvisnih kopij SharedMemory.h, ki se ujemata, ne iz kopije, ki jo igra dostavlja; nepreizkušeno z igro

## Vir {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
