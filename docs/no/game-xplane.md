---
title: "X-Plane (live-data)"
nav_order: 49
lang: "no"
source: game-xplane.md
source_hash: "be1c5b21d2ef"
nav_exclude: true
search_exclude: true
---
# X-Plane (live-data) {#x-plane-live-data}

Mens du spiller X-Plane, lagrer watcheren de dataene spillet selv sender ut, slik at du kan se på dem senere på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `xplane`, type [`telemetry`](sources-and-rules.md); den kjører mens `X-Plane.exe` kjører, og ser etter nye data hvert 0,1 s.*

## Hva som lagres {#what-is-recorded}

- egen posisjon 10 ganger i sekundet (breddegrad/lengdegrad/høyde som meter øst/opp/nord fra første posisjon; bredde-, lengde- og høyde lagres som kolonner)
- holdning, indikert og sann lufthastighet, bakkefart, Mach, vertikal fart, AoA, sideglidning, magnetisk kurs, AGL, g (normal, aksial, side), hastighet og rotasjonsrater, klaffer, luftbrems, gass, på bakken
- vekter (totalt, drivstoff, last), gir-håndtak, autopilot, motorturtall og N1, simulatorens tid og dato, pause, simuleringshastighet, avspilling, utetemperatur og lufttrykk ved havflate (X-Plane 12) én gang i sekundet
- take-off, landinger, krasj, tilbakestillinger av flyvningen (session_start/session_end per flyvning)
- flytid, lufttid, distanse, høyeste høyde, høyeste g, landinger
- hvert svar X-Plane sender lagret hel i heat.raw.parquet

## Hvor dataene kommer fra {#where-it-comes-from}

X-Planes UDP-grensesnitt på 127.0.0.1:49000 (RREF-datarefs og RPOS-posisjon, besvart til watcheren)

## Slik slår du det på {#how-to-switch-it-on}

X-Plane 12: Settings > Network > Accept incoming connections (X-Plane 11 svarer som standard)

## Slik fungerer det {#how-it-works}

X-Plane 11 og 12: simulatorens eget UDP-grensesnitt på port 49000.

X-Plane svarer alle som spør på 127.0.0.1:49000, i den takten som er bedt om, til
adressen og porten forespørselen kom fra (X-Planes dokument «Exchanging Data with
X-Plane», levert i `<X-Plane>\Instructions\`):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref-sti (413 byte).
      Svaret er "RREF" + én intern byte + (int32 index, float32 verdi)-par;
      freq 0 stopper den.
RPOS  "RPOS\0" + takten som en NUL-avsluttet ASCII-streng ("10\0"). Svaret er
      "RPOS" + én intern byte + double lon, lat, høyde (m MSL) + float AGL (m),
      pitch, sann kurs, roll (grader), vx øst, vy opp, vz sør (m/s), P, Q, R
      (rad/s), tett pakket.
```

RPOS gir bredde- og lengdegrad som doubler (RREF bare som floats, en halv meter
fra hverandre), så den styrer posisjonen; RREF gir resten og springer inn når
RPOS uteblir. Datarefs (navnene som i X-Plane 12 sin `Resources\plugins\DataRefs.txt`,
<https://developer.x-plane.com/datarefs/>):

```text
sim/flightmodel/position/latitude, longitude, elevation  deg, deg, m MSL
sim/flightmodel/position/true_theta, true_phi, true_psi  pitch, roll, sann kurs (deg)
sim/flightmodel/position/indicated_airspeed              knop
sim/flightmodel/position/groundspeed                     m/s
sim/flightmodel/position/y_agl                           m over bakken
sim/flightmodel/forces/g_nrml                            g, normalt på vingene
sim/flightmodel/failures/onground_any                    1 på bakken
sim/flightmodel2/misc/has_crashed                        1 krasjet
sim/time/total_flight_time_sec                           siden flyvningen ble tilbakestilt
```

og resten av flyvningen i samme takt (sann lufthastighet, vertikal fart, AoA,
sideglidning, magnetisk kurs, Mach, aksial og side-g, rotasjonsrater, klaffer,
luftbrems, gass: `DATAREFS`), med flyets tregere tilstand én gang i sekundet
(vekter, gir-håndtak, autopilot, motorer, simulatorens tid, pause og
hastighet, vær: `SLOW_DATAREFS`). Hvert datagram lagres også hel i
øktens rå sidefil, og meta.json navngir dataref-en bak hver RREF-indeks.

X-Plane 12 tar bare imot disse når Settings > Network > «Accept incoming
connections» er på. Posisjonene legges i et flatt kart rundt øktens første posisjon
(`Tangent`): x øst, z nord i meter, y høyden over havet - så en rett flyvning
forblir rett uansett hvor langt den går, noe et ekte tangentplan ville bøye nedover
med jorden. Kartets origo er øktens `geo`: meta.json og tabellens footer bærer den,
så vieweren kan legge den virkelige verden under flyvningen.

Denne modulen har også det de andre flysimulatorene har felles: det flate kartet,
regnskapet for flyvningene (take-off, landinger, krasj, distanse), UDP-socketen og
Steam-bibliotekslisten.

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner lagres | ja |
| Opp-akse | `y` |
| Enheter | meter (øst, høyde, nord fra første posisjon) |
| Speilvendt for vieweren | `z` |
| Enhetsskala (`scale`: vieweren ganger posisjonene med den) | 1 |

Disse havner i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet` sin footer, så 3DHeat-vieweren snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **nei**. `games --markdown` viser dette som «enkeltspiller».
- Type `telemetry`: den leser bare det spillet eller plattformen gir ut (en UDP-port eller delt minne spillet publiserer), så den tar opp også i nettspill, ikke bare offline; flagget avgjør bare om minne noensinne kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som lagres {#statistics-recorded}

Statistikknøklene denne adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

En nøkkel i klammeparenteser blir fullført under kjøring (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell med spillets felter eller fra spillets egne statistikknavn, står ikke på listen; «Hva som lagres» over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeat sin [regel for konvertering](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller lagres, og slettes aldri. I tillegg til radene blir hver pakke, side, linje eller respons adapteren mottar, lagret uendret i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt som beholdes med navn; `used` markerer det som også ble til rader), og `selfCheck.completeness` i `meta.json` teller hver `type` - `lost` er 0.

**Leses**

- RPOS (10 Hz): lengdegrad, breddegrad, høyde, AGL, pitch, sann kurs, roll, hastighet (øst, opp, sør) og rotasjonsrater P/Q/R - alt på radene
- RREF (10 Hz): de 27 datarefs i `DATAREFS` - posisjon, holdning, IAS, bakkefart, TAS, vertikal fart, AoA, sideglidning, magnetisk kurs, Mach, g normal/aksial/side, rotasjonsrater, klaffer, luftbrems, gass, AGL, krasjet, på bakken, flytid - på radene
- RREF (1 Hz): de 20 datarefs i `SLOW_DATAREFS` - vekter, gir-håndtak, autopilotservoer, simulatorens tid og dato, pause, simuleringshastighet, repriseavspilling, antall motorer, turtall for motor 1-4, N1 for motor 1-2, utelufttemperatur, lufttrykk ved havflate - på radene slik sist mottatt

**Lagres uendret**

- hvert datagram hel som `payload`, under sin firebokstavs-overskrift: `RREF` og `RPOS` (brukt når avlesningen ga en rad; i menyene, uten posisjon, gir de ingen), alt annet X-Plane sender til watcherens port under sin egen overskrift eller `unknown`; meta.json sitt `requests` sier hvilken dataref hver RREF-indeks er, så nyttelastene kan leses uten denne modulen

**Ikke tilgjengelig**

- alle andre datarefs (X-Plane har tusenvis): RREF sender bare det som er bedt om, ett abonnement hver; listen ber om flyet, flyets tilstand og simulatorens tid - mer cockpitdetalj (radioer, lys, hver motors instrumenter, feil) ville multiplisere forespørslene
- flyets navn og ICAO-type: byte-array-datarefs, som RREF sender én float per tegn for
- andre fly (AI og flerspiller): sim/multiplayer/position-datarefs er ikke bedt om
- DATA-utdataene (Settings > Data Output): de sendes til en fast adresse valgt i simulatoren, ikke til den som spør; RREF og RPOS dekker det watcheren leser

**Størrelse**: omtrent 17 MB per time før zstd (RREF og RPOS 10 ganger i sekundet, omtrent 220 og 70 byte pluss en ramme hver, den trege RREF én gang i sekundet), hvis X-Plane sender hver avlesnings verdier i én pakke, slik den gjør; zstd reduserer flyttallene flere ganger

## Verifisert {#verified}

testet mot en falsk X-Plane som svarer på RREF/RPOS etter X-Plane 12 sin «Exchanging Data with X-Plane»; datarefnavnene sjekket mot X-Plane 12 sin DataRefs.txt; ikke testet mot den kjørende simulatoren

## Kilde {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
