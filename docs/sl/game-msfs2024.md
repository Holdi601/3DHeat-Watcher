---
title: "Microsoft Flight Simulator 2024 (podatki v živo)"
nav_order: 32
lang: "sl"
source: game-msfs2024.md
source_hash: "011c18a23252"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2024 (podatki v živo) {#microsoft-flight-simulator-2024-live-data}

Medtem ko igrate Microsoft Flight Simulator 2024, watcher shrani podatke, ki jih igra sama pošilja ven, da jih lahko pozneje pogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `msfs2024`, vrsta [`telemetry`](sources-and-rules.md); teče, dokler je `FlightSimulator2024.exe` zagnan, in novih podatkov išče vsakih 0,1 s.*

## Kaj se zapiše {#what-is-recorded}

- položaj lastnega letala ob vsakem okvirju simulacije, zajet 10-krat na sekundo (zemljepisna širina/dolžina/višina kot metri vzhodno/navzgor/severno od prve meritve; lat/lon/alt ohranjeni kot stolpci)
- lega, indicirana hitrost, hitrost glede na tla, AGL, g, na tleh; dejanska hitrost, Mach, vertikalna hitrost, napadni kot, zdrs, magnetni smerni kot, hitrosti telesa, pospeški in hitrosti vrtenja približno 10-krat na sekundo
- teža, gorivo, zakrilca, podvozje, zračne zavore, avtopilot, plin, vrtljaji, vreme, hitrost simulacije, čas in stanje kamere enkrat na sekundo; naslov letala in tip ter model in id po ATC
- vzleti, pristanki, trki, leti začeti in ustavljeni (session_start/session_end)
- čas leta, čas v zraku, razdalja, največja višina, največ g, pristanki
- vsako sporočilo SimConnect v celoti v heat.raw.parquet

## Od kod prihaja {#where-it-comes-from}

SimConnect prek lastne datoteke SimConnect.dll igralca (mapa simulatorja ali %MSFS2024_SDK%\SimConnect SDK\lib)

## Kako ga vklopiti {#how-to-switch-it-on}

nič v simulatorju; potrebuje SimConnect.dll - MSFS 2020 ga ima v svoji mapi, igralci MSFS 2024 namestijo SDK MSFS 2024

## Kako deluje {#how-it-works}

Microsoft Flight Simulator 2020 in 2024: SimConnect, prek lastne datoteke SimConnect.dll igralca.

SimConnect je objavljeni odjemalski API simulatorja (dokumentacija SDK:
<https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>,
<https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>).
Watcher DLL ne priloži: naloži tisto, ki je prišla s simulatorjem ali njegovim SDK - MSFS 2020 ima `SimConnect.dll` v svoji mapi namestitve; MSFS 2024 na Steamu priloži samo svojo notranjo različico, zato igralci 2024 namestijo SDK MSFS 2024 (`<SDK>\SimConnect SDK\lib\SimConnect.dll`; simulator 2024 sprejema tudi odjemalce 2020).

Klici iz SimConnect.h, vsi vrnejo HRESULT (0 = S_OK):

```text
SimConnect_Open(HANDLE*, LPCSTR name, HWND, DWORD, HANDLE, DWORD config)
SimConnect_AddToDataDefinition(HANDLE, DWORD define, LPCSTR var, LPCSTR units,
                               SIMCONNECT_DATATYPE (FLOAT64 = 4), float epsilon, DWORD datum)
SimConnect_RequestDataOnSimObject(HANDLE, DWORD request, DWORD define, DWORD object (0 = user),
                                  SIMCONNECT_PERIOD (SIM_FRAME = 3), DWORD flags, DWORD origin,
                                  DWORD interval, DWORD limit)
SimConnect_SubscribeToSystemEvent(HANDLE, DWORD event, LPCSTR name)
SimConnect_GetNextDispatch(HANDLE, SIMCONNECT_RECV**, DWORD*)   E_FAIL, kadar nič ne čaka
SimConnect_Close(HANDLE)
```

Vsako sporočilo se začne s SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID}
(#pragma pack 1). Tista, ki jih tu beremo:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], nato različice DWORD
3  QUIT            simulator se zapira
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, nato vrednosti (tu vsaka FLOAT64)
```

Spremenljivke simulacije (zahtevane enote, da pretvorba ni potrebna): PLANE
LATITUDE/LONGITUDE (stopinje), PLANE ALTITUDE (metri, nad morsko gladino), PLANE
ALT ABOVE GROUND (metri), PLANE PITCH/BANK DEGREES in PLANE HEADING DEGREES
TRUE (stopinje; lastni predznaki SimConnect - nos navzgor je negativen nagib), AIRSPEED
INDICATED in GROUND VELOCITY (vozli), G FORCE (gforce), SIM ON GROUND (bool).
Sistemski dogodki: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded,
Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Tri dodatne opredelitve podatkov zahtevajo preostanek leta (`MOTION_VARS`,
vsak šesti okvir simulacije), počasnejše stanje letala (`STATE_VARS`, enkrat na sekundo)
in njegova imena (`NAME_VARS`, nizi po 256 bajtov, ko se spremenijo); vsaka je svoja
opredelitev, zato spremenljivka, ki je ena različica simulacije ne pozna, stane samo
svoj blok. Vsako sporočilo je ohranjeno v celoti v surovi spremljevalni datoteki seje.

Položaji gredo v isti ravni zemljevid kot pri X-Plane (x vzhod, y višina, z sever, v metrih od prve meritve seje); ta meritev je `geo` seje, v meta.json in nogi tabele.

Isti modul služi tudi: [Microsoft Flight Simulator 2020 (podatki v živo)](game-msfs2020.md).

## Osi položajev {#positions-and-axes}

| | |
|---|---|
| Zapisani položaji | da |
| Os navzgor | `y` |
| Enote | metri (vzhod, višina, sever od prve meritve) |
| Zrcaljeno za pregledovalnik | `z` |
| Merilo enot (`scale`: pregledovalnik položaje pomnoži z njim) | 1 |

Ti gredo v `meta.json` vsake seje (`axes`) in, kadar ima seja položaje, v nogo `heat.parquet`, tako pregledovalnik sam obrača in meri vrstice - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igrano na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `telemetry`: bere samo to, kar igra ali platforma objavi (vrata UDP ali deljeni pomnilnik, ki ju igra objavlja), zato zapisuje tudi pri igri na spletu, tako kot offline; zastavica odloča samo, ali sme kdaj brati pomnilnik.
- Pomnilnik: tega adapterja **nikoli** ne bere. Pomnilnik berejo samo adapterji `memory`, in nikoli za igro, označeno kot igrano na spletu - glej [Viri in pravila](sources-and-rules.md).

## Statistike {#statistics-recorded}

Ključi statistik, ki jih koda tega adapterja nastavi po imenu (`stats` vsake seje v `meta.json` in tabela `stats` v `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Ključ v zavitih oklepajih se dokonča med delovanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz lastnih imen statistik igre, na tem seznamu niso; "Kaj se zapiše" zgoraj jih navaja.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir vsebuje, se prebere ali ohrani, nikoli ne izpusti. Poleg vrstic je vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, ohranjen v celoti v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text`, nato vsako polje, ohranjeno po imenu; `used` označi, kar je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- SIMOBJECT_DATA opredelitve položaja (vsak okvir simulacije): zemljepisna širina, dolžina, višina, AGL, nagib, bank, pravi smerni kot, IAS, hitrost glede na tla, g, na tleh - zadnji okvir anketiranja kot vrstica, vsak okvir za dotike tal in vzlete
- SIMOBJECT_DATA opredelitve gibanja (približno 10 Hz: TAS, Mach, vertikalna hitrost, napadni kot, zdrs, magnetni smerni kot, hitrost telesa, pospešek in hitrost vrtenja na treh oseh) ter opredelitve stanja (1 Hz: teže, gorivo, zakrilca, podvozje, zračne zavore, avtopilot, motorji, plin in vrtljaji, zunanja temperatura, veter, tlak na morski gladini, hitrost simulacije, zulu in lokalni čas, stanje kamere) na vrstice, kakor so bile nazadnje prejete
- SIMOBJECT_DATA opredelitve imen (naslov, tip ATC, model in id) v meta.json in `aircraft` vrstic; OPEN (aplikacija in različica) v meta.json
- EVENT in EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (datoteka leta) in AircraftLoaded (datoteka letala) kot leti, trki in meta.json
- QUIT konča sejo

**Ohranjeno surovo**

- vsako sporočilo, ki ga SimConnect preda watcherju, v celoti kot `payload`, pod imenom njegovega SIMCONNECT_RECV_ID: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (spremenljivka ali dogodek, ki ga simulator ni sprejel, s send id in indeksom), vsak drug id po imenu ali `RECV_<id>`
- kar samo surova spremljevalna datoteka drži: vsak položaj okvirja simulacije med vrsticami, dogodki Pause, Sim, CrashReset, PositionChanged in FlightSaved, opredelitev, ki jo je simulator prekinil (ena spremenljivka, ki je ni poznal: blok se potem ne bere po imenu); `requests` v meta.json navaja vsako opredelitev z njenimi spremenljivkami in enotami po vrsti, zato se koristne obremenitve preberejo tudi brez tega modula

**Ni na voljo**

- drugi letalniki (AI promet, drugi igralci na spletu): SimConnect_RequestDataOnSimObjectType bi anketiral vsak letalnik v krogu - več obremenitve za simulator in tuji leti
- blok gibanja pri vsakem okvirju simulacije: zahteva se vsak šesti okvir (okoli 10 Hz, hitrost vrstic), kar surovi tok ohrani blizu petine velikosti; blok položaja ostane pri vsakem okvirju
- na tisoče drugih spremenljivk simulacije (radijske postaje, luči, vsak merilnik motorja, okvare): opredelitev drži samo to, kar zahteva; seznami zahtevajo let, stanje letala in čas simulacije
- vremenska opazovanja, objekti (letališča, VOR-i), podatki odjemalcev dodatkov: ločene zahteve, niso narejene

**Velikost**: okoli 30-55 MB na uro pred zstd: blok položaja pri vsakem okvirju simulacije (okoli 200 bajtov z okvirjem, 30-60 na sekundo), blok gibanja pri okoli 10 Hz (okoli 240 bajtov), blok stanja enkrat na sekundo; zstd skrči dvojne vrednosti večkrat

## Preverjeno {#verified}

preizkušeno dekodiranje sporočil na medpomnilnikih, zgrajenih iz postavitev iz SimConnect.h; živa povezava SimConnect je nepreizkušena

## Vir {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
