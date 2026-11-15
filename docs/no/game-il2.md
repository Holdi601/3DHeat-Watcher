---
title: "IL-2 Sturmovik: Great Battles (live-data)"
nav_order: 26
lang: "no"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (live-data) {#il-2-sturmovik-great-battles-live-data}

Mens du spiller IL-2 Sturmovik: Great Battles, lagrer watcheren de dataene spillet selv sender ut, slik at du kan se på dem senere som statistikk og en tidslinje.

*Tekniske detaljer: adapter `il2`, type [`telemetry`](sources-and-rules.md); den kjører mens `Il-2.exe` eller `IL2Series.exe` kjører, og ser etter nye data hvert 0,1 s.*

## Hva som lagres {#what-is-recorded}

- flyvninger: flyet som er tatt (spawn) og når utdataene stopper (session_end) - ingen verdensposisjon: spillet sender ingen
- bomber og raketter sluppet (masse), treff og skade tatt, eksplosjoner, skuddserier - posisjoner lokale for flyet
- tilsynelatende lufthastighet, AGL, vertikal fart, g, motorturtall én gang i sekundet, med alle andre indikatorer pakken har (ladetrykk, motorrystelse, giret og trykk i giret, AoA, sideglidning, akselerasjon x/y/z, kabinrystelse, klaffer, luftbremser)
- flyvninger, avfyrte runder, bomber, raketter, treff tatt, høyeste fart, høyeste g, flytid; serverens tittel og pilotnavn på nett
- hver telemetripakke lagret hel i heat.raw.parquet

## Hvor dataene kommer fra {#where-it-comes-from}

spillets telemetri-UDP-utdata til 127.0.0.1:41995 ([KEY = telemetrydevice] i &lt;spill>\data\startup.cfg)

## Slik slår du det på {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (legger til addrN = "127.0.0.1:41995", enable = true), start IL-2 på nytt

Skriv kommandoen i en terminal som er åpnet i watcherens mappe (se [Før du starter](before-you-start.md)). Hvis den feiler, sier siste linje hvorfor; [Installere og kjøre](installing-and-running.md) dekker de vanligste årsakene.

`python -m heat3d_watch setup il2` viser filene den ville endret; `python -m heat3d_watch setup il2 --apply` endrer dem og beholder originalen som `<file>.heat3d-backup` (se [Kommandoer](commands.md#setup)). Den skriver `il2: changed: ...` for hver endring, eller `il2: nothing to change` når den allerede er på.

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

Den samme modulen dekker også: [IL-2 Sturmovik: Great Battles (repriser)](game-il2-tacview.md).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner lagres | nei |
| Opp-akse | `y` |
| Enheter | ingen: telemetrien har ingen verdensposisjoner |
| Speilvendt for vieweren | ingen |
| Enhetsskala (`scale`: vieweren ganger posisjonene med den) | 1 |

Disse havner i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet` sin footer, så 3DHeat-vieweren snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som «tillatt (leser bare det spillet publiserer)».
- Type `telemetry`: den leser bare det spillet eller plattformen gir ut (en UDP-port eller delt minne spillet publiserer), så den tar opp også i nettspill, ikke bare offline; flagget avgjør bare om minne noensinne kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som lagres {#statistics-recorded}

Statistikknøklene denne adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

En nøkkel i klammeparenteser blir fullført under kjøring (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell med spillets felter eller fra spillets egne statistikknavn, står ikke på listen; «Hva som lagres» over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeat sin [regel for konvertering](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller lagres, og slettes aldri. I tillegg til radene blir hver pakke, side, linje eller respons adapteren mottar, lagret uendret i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt som beholdes med navn; `used` markerer det som også ble til rader), og `selfCheck.completeness` i `meta.json` teller hver `type` - `lost` er 0.

**Leses**

- SET_FOCUS (flyet som er tatt: en flyvning), DROP_BOMB og ROCKET_LAUNCH (masse, lokal posisjon), HIT og DAMAGE (lokal posisjon, kraft), EXPLOSION (lokal posisjon, radius), GUN_FIRE (runder per avlesning) som rader
- SETUP_ENG (index, id, lokal posisjon, maksimalt turtall), SETUP_GUN (index, lokal posisjon, prosjektilmasse, munningshastighet) og SETUP_LGEAR (index, id, lokal posisjon) som rader: flyets motorer, kanoner og understell når flyvningen begynner
- SRV_TITLE, SRV_ADDR, SRS_ADDR og CLIENT_DAT (pilotnavn) inn i meta.json; CTRL_DAT sin coalition som flyvningens lag
- alle femten indikatorene i spesifikasjonen på den éngangssekundsbaserte `state`-raden (én verdi som tall, én per motor, understellsben eller akse som liste); høyeste fart, g og AGL fra hver pakke

**Lagres uendret**

- hver datagram hel som `payload`, under sin Packet_ID: `0x54000101` for telemetri (brukt når den ga en rad eller et meta.json-felt), enhver annen id som seg selv, et datagram som er for kort til en som `short`
- det bare den rå sidefilen har: indikatorene mellom éngangssekundsradene (spillet sender dem med 50 Hz / decimation), en SETUP-hendelse kortere enn spesifikasjonens oppsett, hendelses-id-er spesifikasjonen ikke lister

**Ikke tilgjengelig**

- en verdensposisjon: telemetriutdataene har ingen (hendelsespositioner er lokale for flyet); adapteren il2-tacview leser posisjoner fra spillets egne Tacview-opptak
- andre fly og spillere: utdataene beskriver bare spillerens eget fly

**Størrelse**: omtrent 8 MB per time ved oppsettets 10 Hz (decimation 5; en pakke er rundt 160 byte pluss rammen), 40 MB ved spillets fulle 50 Hz, før zstd; zstd krymper de repeterende flyttallene til en brøkdel

## Verifisert {#verified}

testet på pakker bygd etter spillets egen Il2_TeleOutput-spesifikasjon (rev 1.2); endringer i startup.cfg testet på en kopi av filen; ikke testet mot det kjørende spillet

## Kilde {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
