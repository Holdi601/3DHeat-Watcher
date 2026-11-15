---
title: "RaceRoom Racing Experience (živi podaci)"
nav_order: 38
lang: "hr"
source: game-raceroom.md
source_hash: "ffd0499ca059"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (živi podaci) {#raceroom-racing-experience-live-data}

Dok igrate RaceRoom Racing Experience, watcher sprema podatke koje sama igra šalje, pa ih kasnije možete pogledati na karti u 3DHeat pregledniku.

*Tehnički detalji: adapter `raceroom`, vrsta [`telemetry`](sources-and-rules.md); radi dok je pokrenut `RRRE64.exe` ili `RRRE.exe` i traži nove podatke svakih 0,1 s.*

## Što se bilježi {#what-is-recorded}

- pozicija svakog automobila (svjetske XYZ, m) 10 puta u sekundi, po imenu vozača, vlastiti automobil označen, uz brzinu i poziciju u utrci; vlastiti stupanj prijenosa, gas i kočnica
- početak sesije sa stazom koju igra navodi; krugovi po automobilu s vremenom kruga; završetci; vlastita zaustavljanja u boksu
- teleportacije (povratak u boks, ponovno pokretanje): `teleport` gdje je automobil bio, `spawn` gdje je sada
- vlastiti krugovi, najbolji krug, pozicija u utrci, udaljenost, najveća brzina
- cijela dijeljena memorija igre u `heat.raw.parquet`, svaki put kad se promijeni
- vlastite bodove za incidente

## Odakle dolazi {#where-it-comes-from}

dijeljena memorija $R3E (r3e.h verzija 3 tvrtke Sector3)

## Kako to uključiti {#how-to-switch-it-on}

Ništa ne treba uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

## Kako radi {#how-it-works}

Dijeljena memorija koju vozne igre objavljuju za nadzorne ploče, otvorena samo za čitanje - i nikad stvorena.

Nekoliko simulatora svoju telemetriju daje kao imenovano Windows preslikavanje datoteke koje igra stvara, a svatko ga smije čitati: Kunosove stranice `Local\acpmf_*` (Assetto Corsa, ACC, AC Rally, AC EVO-ov `Local\acevo_pmf_*`), iRacingov `Local\IRSDKMemMapFileName`, RaceRoomov `$R3E`, Automobilista 2 / Project CARS 2-ov `$pcars2$`.

Zašto ne `mmap.mmap(-1, size, tagname=...)`, što je uobičajen način u Pythonu: kad preslikavanje još ne postoji, on ga *stvara* - ovdje samo za čitanje. Igra pokrenuta poslije tada otvara watcherovo preslikavanje umjesto vlastitog i ne može u njega pisati, pa je njezina telemetrija mrtva dok watcher ne pusti. Watcher pokreće adapter čim se pojavi proces igre, a to je upravo trenutak kad igra još nije napravila svoje preslikavanje. Zato se ovdje otvara s `OpenFileMappingW`, koji samo pronalazi postojeće preslikavanje, mapira ga s `FILE_MAP_READ` i javlja „još nije tu“ inače; adapteri pokušaju ponovno malo kasnije.

Ovdje ništa ne može pisati: pogled je mapiran samo za čitanje i iz njega se samo kopira s `ctypes.string_at`.

Ovdje se čitaju i dvije igre; svaki automobil na stazi nalazi se na njihovim stranicama.

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

Sector3-ov `r3e.h` (github.com/sector3studios/r3e-api, sample-c/src/r3e.h, verzija 3.6), `#pragma pack(1)`. Zaglavlje kaže gdje počinju vozači i kolika je jedna stavka (`all_drivers_offset`, `driver_data_size`), pa se dio za svakog vozača - ime, utor, mjesto, svjetska pozicija (float x y z, m), odvoženi krugovi, vrijeme tekućeg kruga, status završetka, traka u boksu, brzina - čita prema tome. Vlastita polja igrača (najbolji i prethodni krug, pozicija u utrci, bodovi za incidente, mjenjač, pedale, nazivi staze i izvedbe) čitaju se na pomacima 3.6 samo kad je `all_drivers_offset` ona vrijednost 2008 na koju ga taj raspored stavlja. Y se uzima kao gore; zaglavlje to ne kaže.

Isti modul služi i: [Automobilista 2 (živi podaci)](game-automobilista-2.md), [Project CARS 2 (živi podaci)](game-project-cars-2.md).

## Pozicije i osi {#positions-and-axes}

| | |
|---|---|
| Bilježe se pozicije | da |
| Os prema gore | `y` |
| Jedinice | metri; pretpostavljeno Y gore (r3e.h to ne kaže) |
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

- po utoru vozača (prema vlastitom pomaku i veličini zaglavlja): ime, utor, status završetka, mjesto, svjetska pozicija, odvoženi krugovi, vrijeme tekućeg kruga, traka u boksu, brzina
- vlastita polja igrača, samo kad stranica odgovara rasporedu r3e.h 3.6: nazivi staze i izvedbe, vrsta sesije, pozicija u utrci, najbolji i prethodni krug, bodovi za incidente, mjenjač, gas, kočnica, utor igrača
- pomaci izvedeni iz r3e.h 3.6 tvrtke Sector3 i provjereni na stranici izrađenoj iz njega u testovima; još nije provjereno u samoj igri

**Čuva se sirovo**

- `r3e`: cijelo preslikavanje $R3E, svako čitanje čiji se bajtovi razlikuju od zadnje sačuvane kopije - svako polje r3e.h: fizika igrača (orijentacija, brzine, ubrzanja, g-sile), motor, gorivo, gume, kočnice, oštećenja, zastavice, izbornik boksa, vremena sektora, cijeli podaci o vozaču za svaki utor vozača (klasa, model, tim, vremena sektora, zaostaci, kazne, gume)
- `used` je istinit za stranicu pročitanu u retke; lažan za onu u izbornicima, pauziranu, u reprizi, drugog rasporeda ili uhvaćenu usred pisanja (`torn` 1); `unchanged_reads` u meta.json broji čitanja koja su bajt po bajt bila ista kao ranije sačuvana kopija

**Nije dostupno**

- ulazi i fizika drugih vozača: stranica daje samo igračevu
- točna vremena krugova drugih automobila: utor ima samo vrijeme tekućeg kruga, pa je krug zadnje viđeno vrijeme tekućeg kruga (na oko 0,1 s)
- vlastita polja igrača na rasporedu koji nije 3.6: čuvaju se sirova, ne čitaju se dok se ne provjere

**Veličina**: stranica je 44 KB (r3e.h 3.6; preslikavanje je zaokruženo na cijele stranice od 4 KB), do 10 puta u sekundi dok se vozi: oko 1,6 GB po satu prije sažimanja; prazni utori vozača i polja koja se ne mijenjaju vrlo se dobro sažimaju zstd-om (još nije izmjereno na pravoj sesiji)

## Provjereno {#verified}

testirano na stranici izrađenoj u testu iz r3e.h 3.6 (pomaci izvedeni iz službenog zaglavlja); neprovjereno u samoj igri; vremena krugova drugih automobila su zadnje viđeno vrijeme tekućeg kruga (na oko 0,1 s)

## Izvor {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
