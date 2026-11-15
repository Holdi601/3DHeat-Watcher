---
title: "IL-2 Sturmovik: Great Battles (repriser)"
nav_order: 27
lang: "no"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (repriser) {#il-2-sturmovik-great-battles-replays}

Etter en kamp i IL-2 Sturmovik: Great Battles gjør watcheren om repriseen spillet lagret, til filer du kan se på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `il2-tacview`, type [`replay`](sources-and-rules.md); den kjører hele tiden (den venter ikke på at et spill starter) og ser etter nye data hvert 5. s.*

## Hva som lagres {#what-is-recorded}

- hvert fly, kjøretøy og skip i opptaket: posisjoner én gang i sekundet (meter øst/opp/nord fra opptakets referansepunkt; bredde- og lengdegrad og høyde som kolonner)
- oppstillinger, ødeleggelser (død) og avganger (forlatt), take-off og landinger når de er tatt opp
- objekter, ødelagte, take-off, landinger og lengde per opptak
- hver linje i opptaket lagret hel i heat.raw.parquet, på radenes tidsur

## Hvor dataene kommer fra {#where-it-comes-from}

spillets egne Tacview-opptak &lt;spill>\data\Tracks\\\*.acmi (ACMI 2.x-tekst, vanlig eller zippet)

## Slik slår du det på {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 i [KEY = track_record])

Skriv kommandoen i en terminal som er åpnet i watcherens mappe (se [Før du starter](before-you-start.md)). Hvis den feiler, sier siste linje hvorfor; [Installere og kjøre](installing-and-running.md) dekker de vanligste årsakene.

`python -m heat3d_watch setup il2-tacview` viser filene den ville endret; `python -m heat3d_watch setup il2-tacview --apply` endrer dem og beholder originalen som `<file>.heat3d-backup` (se [Kommandoer](commands.md#setup)). Den skriver `il2-tacview: changed: ...` for hver endring, eller `il2-tacview: nothing to change` når den allerede er på.

## Slik fungerer det {#how-it-works}

IL-2 Sturmovik: Great Battles - spillets telemetri-utdata over UDP, og egne Tacview-opptak.

1. Telemetri («Telemetry output of IL2 v4.003», revisjon 1.2, levert som
   `<spill>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Slås på i
   `<spill>\data\startup.cfg`, seksjonen `[KEY = telemetrydevice]`: `addr`,
   `addr1`, ... = «IP[:port]» (flere mål samtidig), `decimation` (50 Hz /
   n), `enable`, `port`. `setup` legger til ett mål, 127.0.0.1:41995 (JoyPro bruker
   41994, spillets standard er 4322), og slår på utdataene. Pakkene, little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Indikatorer: 0 ENG_RPM, 1 ENG_MP, 2/3 motorrystelse, 4 LGEARS_STATE, 5
   LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz inkl. tyngdekraft),
   9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14
   VERTICAL_SPEED (m/s). Hendelser (2-byte pakket): 0 SET_FOCUS (STRING: lengdebyte + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float
   max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass,
   float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float
   pos[3]}, 4 DROP_BOMB og 5 ROCKET_LAUNCH
   {float pos[3], float mass, WORD flags}, 6 HIT og 7 DAMAGE {float pos[3],
   float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE
   gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long
   client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short
   coalition}. Hendelsespositioner er lokale for spillerens fly; strømmen har
   ingen verdensposisjon i det hele tatt - så dette er hendelser og tall, ikke en rute.

2. Tacview-opptak: `tacviewrecord = 1` i `[KEY = track_record]` gjør at spillet skriver
   `<spill>\data\Tracks\*.acmi` (i flerspiller bestemmer serveren).
   En ferdig fil konverteres: hvert fly, kjøretøy og skip med sine
   posisjoner, oppstilling og fjerning (ødelagt eller borte), take-off og landinger når opptaket har dem. ACMI 2.x-tekstformat, vanlig eller zippet, etter
   <https://www.tacview.net/documentation/acmi/en/> - «#t»-linjer flytter klokken,
   «id,Key=Value,...»-linjer setter egenskaper (hex-id-er, komma unnsluppet «\\,», en
   avsluttende «\\» fortsetter linjen), «-id» fjerner et objekt, objekt 0 bærer
   de globale verdiene (ReferenceLongitude/Latitude, RecordingTime, ...) og hendelsene
   («Event=Destroyed\|id\|text»). T = Lon\|Lat\|Alt[\|U\|V] eller
   Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], lengde- og breddegrad relativt til
   referansen, tomme felt er uendret. Posisjonene legges i et flatt kart rundt referansepunktet: x øst, y høyde, z nord, meter. Referansepunktet er øktens `geo`, lagret i meta.json og tabellens footer, så vieweren kan legge den virkelige verden under rutene.

Den samme modulen dekker også: [IL-2 Sturmovik: Great Battles (live-data)](game-il2.md).

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

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som «tillatt (leser bare det spillet publiserer)».
- Type `replay`: den leser bare det spillet eller plattformen gir ut (repriser og demoer spillet lagrer), så den tar opp også i nettspill, ikke bare offline; flagget avgjør bare om minne noensinne kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som lagres {#statistics-recorded}

Statistikknøklene denne adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

En nøkkel i klammeparenteser blir fullført under kjøring (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell med spillets felter eller fra spillets egne statistikknavn, står ikke på listen; «Hva som lagres» over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeat sin [regel for konvertering](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller lagres, og slettes aldri. I tillegg til radene blir hver pakke, side, linje eller respons adapteren mottar, lagret uendret i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt som beholdes med navn; `used` markerer det som også ble til rader), og `selfCheck.completeness` i `meta.json` teller hver `type` - `lost` er 0.

**Leses**

- hvert objekts T (lengdegrad, breddegrad, høyde, roll, pitch, yaw, U, V, heading) som posisjoner én gang i sekundet per objekt, med Name, Type, Pilot, Coalition/Color, Country, Group og Parent
- oppstillinger, fjerninger (død når en Destroyed-hendelse kom først, ellers forlatt), TakenOff- og Landed-hendelser, Message- og Bookmark-hendelser som rader
- de globale verdiene ReferenceLongitude/Latitude (kartets origo), RecordingTime/ReferenceTime (når), DataSource, DataRecorder og Title i meta.json

**Lagres uendret**

- hver ikke-tom logisk linje hel som `text` (en linje fortsatt med en avsluttende skråstrek er slått sammen, slik ACMI leser den), under sin type: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` og `event` (objekt 0), `object` (id,Key=Value,...)
- det bare den rå sidefilen har: posisjonene mellom de éngangssekundsradene, våpen, granater, fakler, chaff og andre objekter som ikke tegnes som ruter, hver annen egenskap (telemetri som IAS, AOA, gass, drivstoff der opptaket har det), andre globale verdier (Comments, Briefing, Author, Category), hendelser andre enn de som leses (Timeout, LeftArea, ...)

**Ikke tilgjengelig**

- ingenting utover det opptaket inneholder; det spillet ikke skriver inn i opptakene, finnes ikke i dem

**Størrelse**: omtrent opptakets egen tekst pluss rundt 70 byte per linje, før zstd: et opptak på 100 MB gir omtrent 150-250 MB rått, som zstd bringer nær størrelsen på det zippede opptaket

## Verifisert {#verified}

testet på syntetiske ACMI 2.2-filer (tekst og zippet); ikke testet på et opptak fra spillet

## Kilde {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
