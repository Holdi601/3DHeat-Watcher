---
title: "Automobilista 2 (živi podaci)"
nav_order: 6
lang: "hr"
source: game-automobilista-2.md
source_hash: "5e3ca1507524"
nav_exclude: true
search_exclude: true
---
# Automobilista 2 (živi podaci) {#automobilista-2-live-data}

Dok igrate Automobilista 2, watcher sprema podatke koje sama igra šalje, pa ih kasnije možete pogledati na karti u 3DHeat pregledniku.

*Tehnički detalji: adapter `automobilista-2`, vrsta [`telemetry`](sources-and-rules.md); radi dok je pokrenut `AMS2AVX.exe` ili `AMS2.exe` i traži nove podatke svakih 0,1 s.*

## Što se bilježi {#what-is-recorded}

- pozicija svakog automobila (svjetske XYZ, m) 10 puta u sekundi, po imenu vozača, vlastiti automobil označen, uz brzinu i poziciju u utrci; vlastiti stupanj prijenosa, gas i kočnica
- početak sesije sa stazom koju igra navodi; krugovi po automobilu s vremenom kruga; završetci; vlastita zaustavljanja u boksu
- teleportacije (povratak u boks, ponovno pokretanje): `teleport` gdje je automobil bio, `spawn` gdje je sada
- vlastiti krugovi, najbolji krug, pozicija u utrci, udaljenost, najveća brzina
- cijela dijeljena memorija igre u `heat.raw.parquet`, svaki put kad se promijeni

## Odakle dolazi {#where-it-comes-from}

dijeljena memorija $pcars2$ (raspored SMS SharedMemory.h)

## Kako to uključiti {#how-to-switch-it-on}

U igri: Options > System > Shared Memory: "Project CARS 2"

## Kako radi {#how-it-works}

Dijeljena memorija koju vozne igre objavljuju za nadzorne ploče, otvorena samo za čitanje - i nikad stvorena.

Nekoliko simulatora svoju telemetriju daje kao imenovano Windows preslikavanje datoteke koje igra stvara, a svatko ga smije čitati: Kunosove stranice `Local\acpmf_*` (Assetto Corsa, ACC, AC Rally, AC EVO-ov `Local\acevo_pmf_*`), iRacingov `Local\IRSDKMemMapFileName`, RaceRoomov `$R3E`, Automobilista 2 / Project CARS 2-ov `$pcars2$`.

Zašto ne `mmap.mmap(-1, size, tagname=...)`, što je uobičajen način u Pythonu: kad preslikavanje još ne postoji, on ga *stvara* - ovdje samo za čitanje. Igra pokrenuta poslije tada otvara watcherovo preslikavanje umjesto vlastitog i ne može u njega pisati, pa je njezina telemetrija mrtva dok watcher ne pusti. Watcher pokreće adapter čim se pojavi proces igre, a to je upravo trenutak kad igra još nije napravila svoje preslikavanje. Zato se ovdje otvara s `OpenFileMappingW`, koji samo pronalazi postojeće preslikavanje, mapira ga s `FILE_MAP_READ` i javlja „još nije tu“ inače; adapteri pokušaju ponovno malo kasnije.

Ovdje ništa ne može pisati: pogled je mapiran samo za čitanje i iz njega se samo kopira s `ctypes.string_at`.

Ovdje se čitaju i dvije igre; svaki automobil na stazi nalazi se na njihovim stranicama.

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

SMS-ov `SharedMemory.h` (isporučen u mapi Support\SharedMemory igre; AMS2: Options > System > Shared Memory "Project CARS 2"), `#pragma pack(4)`. `mParticipantInfo[64]` od bajta 28, po 100 bajtova: mIsActive, mName[64], mWorldPosition[3] (m, Y gore), mCurrentLapDistance, mRacePosition, mLapsCompleted, mCurrentLap, mCurrentSector; mViewedParticipantIndex (20) je automobil igrača; po sudioniku mLastLapTimes (9200), mRaceStates (9520), mSpeeds (10800); igračev mBestLapTime (6716), mLastLapTime (6720), mSpeed (6848), mBrake, mThrottle, mGear; mSequenceNumber (7320) je neparan dok igra piše. Pomaci su izvedeni iz dviju neovisnih kopija zaglavlja (igrina vlastita kopija nije instalirana ovdje), koje se slažu.

Obje stranice čuvaju se cijele uz to (docs/converters.md, „Live sources“): cijelo preslikavanje, svako čitanje čiji se bajtovi razlikuju od zadnje sačuvane kopije, u sirovom pratećem dijelu sesije pod `type` `r3e` ili `pcars2` - svaki utor vozača i svako polje strukture, i ona koja se ovdje ne čitaju, pa kasnijem dekoderu treba samo prateći dio.

Isti modul služi i: [Project CARS 2 (živi podaci)](game-project-cars-2.md), [RaceRoom Racing Experience (živi podaci)](game-raceroom.md).

## Pozicije i osi {#positions-and-axes}

| | |
|---|---|
| Bilježe se pozicije | da |
| Os prema gore | `y` |
| Jedinice | metri |
| Zrcaljeno za preglednik | nema |
| Mjerilo jedinice (`scale`: preglednik ovim množi pozicije) | 1 |

Ovo ide u `meta.json` (`axes`) svake sesije i, kad sesija ima pozicije, u podnožje `heat.parquet`, pa 3DHeat preglednik sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igranje na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `telemetry`: čita samo ono što igra ili platforma daje (UDP port ili dijeljena memorija koju igra objavljuje), pa bilježi i u igri na mreži i izvan nje; zastavica odlučuje samo smije li se ikad čitati memorija.
- Memorija: adapter je **nikad** ne čita. Memoriju čitaju samo adapteri vrste `memory`, i nikad za igru označenu kao igranu na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` u `meta.json` svake sesije i tablica `stats` u `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz imena statistike same igre nisu na ovom popisu; odjeljak „Što se bilježi“ ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeata: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je postalo i retkom), a `selfCheck.completeness` u `meta.json`-u broji svaki `type` - `lost` je 0.

**Čita se**

- po sudioniku (do 64): aktivnost, ime, svjetska pozicija, pozicija u utrci, odvoženi krugovi; njegovo zadnje vrijeme kruga, stanje utrke i brzina
- automobil igrača (mViewedParticipantIndex), stanje igre i sesije, lokacija i varijanta staze, najbolji i zadnji krug, brzina, kočnica, gas, mjenjač; mSequenceNumber preskače kopiju uhvaćenu usred pisanja
- pomaci iz dviju neovisnih kopija SMS-ova SharedMemory.h koje se slažu, provjereni na stranici izrađenoj iz njih u testovima; još nije provjereno u samoj igri

**Čuva se sirovo**

- `pcars2`: cijelo preslikavanje $pcars2$ - struktura seže daleko preko 11 312 bajtova koji se ovdje čitaju - svako čitanje čiji se bajtovi razlikuju od zadnje sačuvane kopije: orijentacija svakog sudionika, vremena sektora, imena automobila i klasa, načini i zastavice u boksu, fizika igrača, gume, ovjes, oštećenja, vrijeme i sve što su kasnije verzije Automobilista 2 dodale
- `used` je istinit za stranicu pročitanu u retke; lažan za onu u izbornicima, pauziranu, u reprizi, drugog rasporeda ili uhvaćenu usred pisanja (`torn` 1); `unchanged_reads` u meta.json broji čitanja koja su bajt po bajt bila ista kao ranije sačuvana kopija

**Nije dostupno**

- ulazi i fizika drugih sudionika: stranica daje samo gledani automobil
- sve dok je opcija dijeljene memorije igre isključena (Automobilista 2 tada ne piše ništa)

**Veličina**: preslikavanje je oko 20 do 30 KB (ovisno o verziji igre), do 10 puta u sekundi dok se vozi: otprilike 0,7 do 1,1 GB po satu prije sažimanja; zstd smanjuje prazne utore sudionika i imena koja se ne mijenjaju na djelić (još nije izmjereno na pravoj sesiji)

## Provjereno {#verified}

testirano na stranici izrađenoj u testu; pomaci iz dviju neovisnih kopija SharedMemory.h koje se slažu, a ne iz kopije koju igra isporučuje; neprovjereno u samoj igri

## Izvor {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
