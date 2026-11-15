---
title: "Automobilista 2 (podaci uživo)"
nav_order: 6
lang: "bs"
source: game-automobilista-2.md
source_hash: "5e3ca1507524"
nav_exclude: true
search_exclude: true
---
# Automobilista 2 (podaci uživo) {#automobilista-2-live-data}

Dok igrate Automobilista 2, watcher sprema podatke koje igra sama šalje, da ih kasnije možete pogledati na mapi u preglednik 3DHeat-u.

*Tehnički detalji: adapter `automobilista-2`, vrsta [`telemetry`](sources-and-rules.md); radi dok je pokrenut `AMS2AVX.exe` ili `AMS2.exe` i svakih 0,1 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- položaj svakog auta (svjetski XYZ, m) na 10 Hz po imenu vozača, vlastiti auto označen, s brzinom i pozicijom u trci; vlastiti stepen prijenosa, gas, kočnica
- početak sesije sa stazom koju igra imenuje; krugovi po autu s vremenom kruga; završeci; vlastita zaustavljanja u boksu
- teleportacije (nazad u boks, restart): `teleport` gdje je auto bio, `spawn` gdje je sada
- vlastiti krugovi, najbolji krug, pozicija u trci, pređena distanca, najveća brzina
- cijela stranica dijeljene memorije igre u `heat.raw.parquet`, svaki put kad se promijeni

## Odakle dolazi {#where-it-comes-from}

dijeljena memorija $pcars2$ (raspored SMS SharedMemory.h)

## Kako ga uključiti {#how-to-switch-it-on}

U igri: Options > System > Shared Memory: "Project CARS 2"

## Kako radi {#how-it-works}

Dijeljena memorija koju trkaće igre objavljuju za instrument table, otvara se samo za čitanje - i
nikad se ne stvara.

Nekoliko simulacija daje svoju telemetriju kao imenovano Windows mapiranje datoteke koje
igra stvara, a svako ga smije čitati: Kunosove stranice `Local\acpmf_*` (Assetto Corsa,
ACC, AC Rally, `Local\acevo_pmf_*` za AC EVO), iRacingov
`Local\IRSDKMemMapFileName`, RaceRoomov `$R3E`, `$pcars2$` za Automobilista 2 / Project CARS 2.

Zašto ne `mmap.mmap(-1, size, tagname=...)`, što je uobičajen Python način: kad
mapiranje još ne postoji, on ga *stvara* - ovdje, samo za čitanje. Igra
pokrenuta poslije toga otvara watcher-ovo mapiranje umjesto da napravi svoje i
tada ne može pisati u njega, pa joj je telemetrija mrtva dok watcher ne pusti.
Watcher pokreće adapter čim se pojavi proces igre, a to je
upravo trenutak kad igra još nije napravila svoje mapiranje. Zato se ovdje otvara s
`OpenFileMappingW`, koji nalazi samo postojeće mapiranje, mapira ga s
`FILE_MAP_READ`, a inače javlja "još nije tu"; adapteri pokušaju ponovo
malo poslije.

Ovdje ništa ne može pisati: pogled je mapiran samo za čitanje i iz njega se samo kopira
pomoću `ctypes.string_at`.

Ovdje se čitaju i dvije igre; svaki auto na stazi je u njihovim stranicama.

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

SMS-ov `SharedMemory.h` (isporučuje se u igrinom folderu Support\SharedMemory;
AMS2: Options > System > Shared Memory "Project CARS 2"), `#pragma pack(4)`.
`mParticipantInfo[64]` od bajta 28, po 100 bajtova: mIsActive, mName[64],
mWorldPosition[3] (m, Y gore), mCurrentLapDistance, mRacePosition,
mLapsCompleted, mCurrentLap, mCurrentSector; mViewedParticipantIndex (20)
je igračev auto; po učesniku mLastLapTimes (9200), mRaceStates
(9520), mSpeeds (10800); igračevi mBestLapTime (6716), mLastLapTime
(6720), mSpeed (6848), mBrake, mThrottle, mGear; mSequenceNumber (7320) je
neparan dok igra piše. Pomaci su izvedeni iz dvije
neovisne kopije zaglavlja (igrina vlastita kopija ovdje nije instalirana),
koje se slažu.

Obje stranice se osim toga čuvaju cijele (docs/converters.md, "Live sources"):
cijelo mapiranje, svako čitanje čiji se bajtovi razlikuju od zadnje sačuvane kopije, u
sirovom sidecaru sesije pod `type` `r3e` ili `pcars2` - svaki slot vozača i
svako polje strukture, i ona koja se ovdje ne čitaju, pa kasnijem dekoderu
treba samo sidecar.

Isti modul služi i za: [Project CARS 2 (podaci uživo)](game-project-cars-2.md), [RaceRoom Racing Experience (podaci uživo)](game-raceroom.md).

## Položaji i ose {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Osa gore | `y` |
| Jedinice | metri |
| Zrcaljeno za preglednik | nijedna |
| Skala jedinica (`scale`: preglednik njome množi položaje) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označena kao igrana online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `telemetry`: čita samo ono što igra ili platforma daje (UDP port ili dijeljenu memoriju koju igra objavljuje), pa snima i u online igri kao i offline; oznaka odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj je adapter **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

Ključ u vitičastim zagradama dovršava se pri izvođenju (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Šta se bilježi" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeat-ovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje čuvano po imenu; `used` označava šta je također postalo redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- po učesniku (do 64): aktivan, ime, svjetski položaj, pozicija u trci, završeni krugovi; njegovo zadnje vrijeme kruga, stanje trke i brzina
- igračev auto (mViewedParticipantIndex), stanje igre i sesije, lokacija na stazi i varijanta, najbolji i zadnji krug, brzina, kočnica, gas, stepen prijenosa; mSequenceNumber za preskakanje kopije uhvaćene usred pisanja
- pomaci iz dvije neovisne kopije SMS-ovog SharedMemory.h koje se slažu, provjereni na stranici izgrađenoj prema njima u testovima; još ne prema igri

**Čuva se sirovo**

- `pcars2`: cijelo mapiranje $pcars2$ - struktura ide znatno dalje od 11.312 bajtova koji se ovdje čitaju - svako čitanje čiji se bajtovi razlikuju od zadnje sačuvane kopije: orijentacija svakog učesnika, vremena sektora, nazivi auta i klasa, načini i oznake boksa, igračeva fizika, gume, ovjes, oštećenja, vrijeme i sve što su kasnije verzije Automobilista 2 dodale
- `used` je istinito za stranicu pročitanu u redove; neistinito za onu u menijima, pauzi, u snimku, drugog rasporeda ili uhvaćenu usred pisanja (`torn` 1); `unchanged_reads` u meta.json broji čitanja koja su bila bajt po bajt ista kao ranije sačuvana kopija

**Nije dostupno**

- ulazi i fizika ostalih učesnika: stranica daje samo auto koji se gleda
- sve dok je opcija dijeljene memorije u igri isključena (Automobilista 2 tada ništa ne piše)

**Veličina**: mapiranje je oko 20 do 30 KB (ovisno o verziji igre), do 10 puta u sekundi u vožnji: otprilike 0,7 do 1,1 GB na sat prije kompresije; zstd prazne slotove učesnika i nepromjenjiva imena smanjuje na djelić (još nije izmjereno na pravoj sesiji)

## Provjereno {#verified}

testirano na stranici izgrađenoj u testu; pomaci iz dvije neovisne kopije SharedMemory.h koje se slažu, ne iz kopije koju igra isporučuje; nije testirano na igri

## Izvor {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
