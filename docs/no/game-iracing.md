---
title: "iRacing (live-data)"
nav_order: 28
lang: "no"
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (live-data) {#iracing-live-data}

Mens du spiller iRacing, lagrer watcheren de dataene spillet selv sender ut, slik at du kan se på dem senere som statistikk og en tidslinje.

*Tekniske detaljer: adapter `iracing`, type [`telemetry`](sources-and-rules.md); den kjører mens `iRacingSim64DX11.exe` eller `iRacingSim64.exe` kjører, og ser etter nye data hvert 0,1 s.*

## Hva som lagres {#what-is-recorded}

- kjøringen 5 ganger i sekundet uten posisjon (iRacing gir ingen live): fart, gir, gass, brems, runde, andel av runden, posisjon i løpet og i klassen, hendelser
- øktstart, å gå inn i og ut av bilen, inn og ut av depotveien, runder med rundetid, hendelser med poeng, ruteflagget, målgang
- .ibt-telemetrifilene som skrives under økten (bredde-, lengdegrad og høyde - vieweren leser dem)
- runder, beste runde, hendelser, posisjon i løpet, depotstopp, distanse, toppfart
- hele det delte minnet i `heat.raw.parquet`: hodet, variabelhodene, øktinformasjonen, hver telemetrilinje som leses

## Hvor dataene kommer fra {#where-it-comes-from}

delt minne Local\IRSDKMemMapFileName (iRacing SDK); .ibt-filer i %USERPROFILE%\Documents\iRacing\telemetry

## Slik slår du det på {#how-to-switch-it-on}

Ingenting for livedataene. For posisjoner: logg telemetri i bilen (Alt+L) eller sett irsdkLog=1 i app.ini

## Slik fungerer det {#how-it-works}

iRacing, live: iRacing SDK-ens delte minne, lest direkte.

iRacing publiserer telemetrien sin for apper i en navngitt filmapping,
`Local\IRSDKMemMapFileName`, som simulatoren oppretter mens den kjører (og signaliserer
`Local\IRSDKDataValidEvent` ved hver oppdatering, noe som ikke trengs her: watcheren
ser etter ti ganger i sekundet). Oppsettet er SDK-ens `irsdk_defines.h`,
også fulgt av pyirsdk (MIT) - skrevet om her fra disse fakta:

```text
irsdk_header (little-endian int32s)
    0 ver, 4 status (bit 0: connected), 8 tickRate,
    12 sessionInfoUpdate, 16 sessionInfoLen, 20 sessionInfoOffset,
    24 numVars, 28 varHeaderOffset, 32 numBuf, 36 bufLen, 40 pad[2],
    48 varBuf[4]: { tickCount, bufOffset, pad[2] } (16 bytes each)
irsdk_varHeader (144 bytes, numVars of them at varHeaderOffset)
    0 type (0 char, 1 bool, 2 int, 3 bitfield, 4 float, 5 double),
    4 offset (into a line), 8 count, 12 countAsTime + 3 pad,
    16 name[32], 48 desc[64], 112 unit[32]
session info: YAML text at sessionInfoOffset, rewritten when
    sessionInfoUpdate changes (track, sessions, drivers)
```

Simulatoren skriver `numBuf` linjer på omgang; den nyeste er den med høyest
tickCount, og en linje leses på nytt hvis tickCount endret seg mens den ble kopiert.

Live-data har ingen verdensposisjon - breddegrad, lengdegrad og høyde finnes bare i
.ibt-filene iRacing logger til `Documents\iRacing\telemetry` (Alt+L i bilen, eller
`irsdkLog=1`), som 3DHeat-vieweren leser selv. Så dette lagrer kjøringen som hendelser
uten koordinater - fart, runde, andelen av runden som er kjørt, posisjon i løpet, hendelser -
pluss runder, hendelser, depotstopp og ruteflagget, og til slutt de .ibt-filene som ble
skrevet under økten, som `telemetry_file`-hendelser, for vieweren å åpne.

Ved siden av radene lagres hele minnekartet i øktens rå sidefil
(`heat.raw.parquet`): hodets faste del (`header`, hver gang den endrer seg), variabelhodene
(`var_headers`, hele, og som JSON i `text`, hver gang oppsettet endrer seg), øktinformasjonen
som YAML (`session_info`, teksten hver gang `sessionInfoUpdate` endrer seg) og den nyeste
telemetrilinjen (`telemetry`, hver variabel i den, ved hver lesing som finner et nytt tikk).
Variabelhodene og en linje er alt en senere dekoder trenger for å lese hver variabel.

Kilde: iRacing SDK (irsdk_defines.h, dokumentasjonen i iRacing SDK-forumet);
kutu/pyirsdk (MIT) for bekreftelse av forskyvningene.

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner lagres | nei |
| Opp-akse | `y` |
| Enheter | ingen posisjoner live; .ibt-filene har breddegrad/lengdegrad/høyde |
| Speilvendt for vieweren | ingen |
| Enhetsskala (`scale`: vieweren ganger posisjonene med den) | 1 |

Disse havner i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet` sin footer, så 3DHeat-vieweren snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som «tillatt (leser bare det spillet publiserer)».
- Type `telemetry`: den leser bare det spillet eller plattformen gir ut (en UDP-port eller delt minne spillet publiserer), så den tar opp også i nettspill, ikke bare offline; flagget avgjør bare om minne noensinne kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som lagres {#statistics-recorded}

Statistikknøklene denne adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

En nøkkel i klammeparenteser blir fullført under kjøring (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell med spillets felter eller fra spillets egne statistikknavn, står ikke på listen; «Hva som lagres» over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeat sin [regel for konvertering](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller lagres, og slettes aldri. I tillegg til radene blir hver pakke, side, linje eller respons adapteren mottar, lagret uendret i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt som beholdes med navn; `used` markerer det som også ble til rader), og `selfCheck.completeness` i `meta.json` teller hver `type` - `lost` er 0.

**Leses**

- fra den nyeste telemetrilinjen: øktens tid, nummer, tilstand og id, på banen, repriseavspilling, runde, runder fullført, andel og meter av runden, siste og beste runde, fart, gir, gass, brems, turtall, depotvei, banedekke, posisjon i løpet og i klassen, eget antall hendelser (`driving`-radene 5 ganger i sekundet og hendelsene)
- nå også på `driving`-radene: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (grader, fra simulatorens radianer - bare når variabelhodet oppgir enheten som rad), `fuel_l` (enhet l), `lat_accel` og `lon_accel` (enhet m/s^2)
- fra øktinformasjonens YAML: spillerens bilindeks, bane og konfigurasjon, øktTyper, hver sjåfør sitt navn, bil, lag og nummer (session_start-radene, meta.json)
- sjekket mot et blokk bygd etter irsdk_defines.h i testene; ikke ennå mot simulatoren

**Lagres uendret**

- `telemetry`: den nyeste linjen hel, hver variabel simulatoren publiserer (CarIdx-tabellene for hver bil, dekk, fjæring, de høyfrekvente `_ST`-tabellene der simulatoren har dem ...), ved hver lesing som finner et nytt tikk; `tick` er simulatorens tikkteller; `used` er falsk mens en repriseavspilling går
- `var_headers`: variabelhodene hele (144 byte hver) og, i `text`, som JSON (navn, type, forskyvning, antall, enhet, beskrivelse), hver gang oppsettet endrer seg - nok til å lese hver variabel i hver lagret linje
- `session_info`: YAML-teksten hel hver gang oppdateringstelleren endrer seg (helgen, økter og resultater, sjåfører, bilinnstilling, radio, kameralister), `update` er telleren
- `header`: de 112 byte med irsdk-hode hele hver gang det endrer seg (versjon, status, tikkrate, forskyvninger, linjenes tikk)

**Ikke tilgjengelig**

- en verdensposisjon live: det delte minnet har ingen; breddegrad, lengdegrad og høyde finnes bare i .ibt-filene (med logging på), som vieweren leser - watcheren nevner de som ble skrevet under økten
- tikkene mellom to lesinger: simulatoren skriver 60 linjer i sekundet i 3 eller 4 plasser, og watcheren leser 10 ganger i sekundet, så de fleste tikk blir overskrevet før de kan leses; .ibt-filen har hvert tikk når logging er på

**Størrelse**: en telemetrilinje er noen KB (omtrent 5 til 10 KB med alle bilenes tabeller), lagret opptil 10 ganger i sekundet, pluss hodet (112 byte) like ofte og øktinformasjonens YAML (titalls KB) når den endrer seg: omtrent 0,2 til 0,4 GB per time på banen før komprimering; zstd gjør det til en brøkdel (ikke målt på en ekte økt ennå)

## Verifisert {#verified}

testet på et delt-minne-blokk bygd i testen fra irsdk-oppsettet; ikke testet mot simulatoren

## Kilde {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
