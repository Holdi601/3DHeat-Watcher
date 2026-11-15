---
title: "RaceRoom Racing Experience (podaci uživo)"
nav_order: 38
lang: "bs"
source: game-raceroom.md
source_hash: "ffd0499ca059"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (podaci uživo) {#raceroom-racing-experience-live-data}

Dok igrate RaceRoom Racing Experience, watcher sprema podatke koje igra sama šalje, da ih kasnije možete pogledati na mapi u preglednik 3DHeat-u.

*Tehnički detalji: adapter `raceroom`, vrsta [`telemetry`](sources-and-rules.md); radi dok je pokrenut `RRRE64.exe` ili `RRRE.exe` i svakih 0,1 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- položaj svakog auta (svjetski XYZ, m) na 10 Hz po imenu vozača, vlastiti auto označen, s brzinom i pozicijom u trci; vlastiti stepen prijenosa, gas, kočnica
- početak sesije sa stazom koju igra imenuje; krugovi po autu s vremenom kruga; završeci; vlastita zaustavljanja u boksu
- teleportacije (nazad u boks, restart): `teleport` gdje je auto bio, `spawn` gdje je sada
- vlastiti krugovi, najbolji krug, pozicija u trci, pređena distanca, najveća brzina
- cijela stranica dijeljene memorije igre u `heat.raw.parquet`, svaki put kad se promijeni
- vlastiti bodovi incidenata

## Odakle dolazi {#where-it-comes-from}

dijeljena memorija $R3E (Sector3-ov r3e.h, verzija 3)

## Kako ga uključiti {#how-to-switch-it-on}

Ništa ne treba uključivati: watcher čita izvor onako kako ga igra ili platforma daje.

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

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

Sector3-ov `r3e.h` (github.com/sector3studios/r3e-api, sample-c/src/r3e.h,
verzija 3.6), `#pragma pack(1)`. Zaglavlje kaže gdje vozači počinju
i koliko je velik jedan (`all_drivers_offset`, `driver_data_size`), pa se
dio po vozaču - ime, slot, mjesto, svjetski položaj (float x y z, m),
završeni krugovi, vrijeme tekućeg kruga, status cilja, boks traka, brzina - čita
prema njima. Igračeva vlastita polja (najbolji i prethodni krug, pozicija u trci,
bodovi incidenata, stepen prijenosa, pedale, nazivi staze i rasporeda) čitaju se na njihovim
pomacima za 3.6 samo kad je `all_drivers_offset` 2008, koliko ga taj raspored
postavlja. Y se uzima kao gore; zaglavlje to ne kaže.

Isti modul služi i za: [Automobilista 2 (podaci uživo)](game-automobilista-2.md), [Project CARS 2 (podaci uživo)](game-project-cars-2.md).

## Položaji i ose {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Osa gore | `y` |
| Jedinice | metri; Y gore pretpostavljeno (r3e.h to ne kaže) |
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

- po slotu vozača (prema vlastitom pomaku i veličini iz zaglavlja): ime, slot, status cilja, mjesto, svjetski položaj, završeni krugovi, vrijeme tekućeg kruga, boks traka, brzina
- igračeva vlastita polja, samo kad je stranica raspored r3e.h 3.6: nazivi staze i rasporeda, vrsta sesije, pozicija u trci, najbolji i prethodni krug, bodovi incidenata, stepen prijenosa, gas, kočnica, igračev slot
- pomaci izvedeni iz Sector3-ovog r3e.h 3.6 i provjereni na stranici izgrađenoj prema njemu u testovima; još ne prema igri

**Čuva se sirovo**

- `r3e`: cijelo mapiranje $R3E, svako čitanje čiji se bajtovi razlikuju od zadnje sačuvane kopije - svako polje iz r3e.h: igračeva fizika (orijentacija, brzine, ubrzanja, g-sile), motor, gorivo, gume, kočnice, oštećenja, zastave, meni boksa, vremena sektora, cijeli podaci o vozaču svakog slota (klasa, model, tim, vremena sektora, razlike, kazne, gume)
- `used` je istinito za stranicu pročitanu u redove; neistinito za onu u menijima, pauzi, u snimku, drugog rasporeda ili uhvaćenu usred pisanja (`torn` 1); `unchanged_reads` u meta.json broji čitanja koja su bila bajt po bajt ista kao ranije sačuvana kopija

**Nije dostupno**

- ulazi i fizika ostalih vozača: stranica daje samo igračeve vlastite
- tačna vremena krugova drugih auta: slot ima samo vrijeme tekućeg kruga, pa je krug zadnje viđeno vrijeme tekućeg kruga (na oko 0,1 s)
- igračeva vlastita polja na rasporedu različitom od 3.6: čuvaju se sirova, ne čitaju, dok se ne provjere

**Veličina**: stranica je 44 KB (r3e.h 3.6; mapiranje se zaokružuje na cijele stranice od 4 KB), do 10 puta u sekundi u vožnji: oko 1,6 GB na sat prije kompresije; prazni slotovi vozača i polja koja se ne mijenjaju vrlo se dobro komprimiraju zstd-om (još nije izmjereno na pravoj sesiji)

## Provjereno {#verified}

testirano na stranici izgrađenoj u testu prema r3e.h 3.6 (pomaci izvedeni iz službenog zaglavlja); nije testirano na igri; vremena krugova drugih auta su zadnje viđeno vrijeme tekućeg kruga (na oko 0,1 s)

## Izvor {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
