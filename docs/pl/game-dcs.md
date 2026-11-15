---
title: "DCS World (dane na żywo)"
nav_order: 10
lang: "pl"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (dane na żywo) {#dcs-world-live-data}

Podczas gry w DCS World watcher zapisuje dane, które sama gra wysyła na zewnątrz, abyś mógł później obejrzeć je na mapie w viewerze 3DHeat.

*Szczegóły techniczne: adapter `dcs`, rodzaj [`telemetry`](sources-and-rules.md); działa, gdy `DCS.exe` jest uruchomiony, i sprawdza nowe dane co 0,1 s.*

## Co jest zapisywane {#what-is-recorded}

- własna pozycja 10 razy na sekundę w metrach na wschód/w górę/na północ od początku układu teatru (z szerokości, długości i wysokości geograficznej); lat/lon/alt oraz własne metry świata DCS (dcs_x – północ, dcs_y – góra, dcs_z – wschód) jako kolumny
- orientacja, wskazywana i prawdziwa prędkość powietrzna, Mach, prędkość pionowa, kąt natarcia i ślizgu, kurs magnetyczny, AGL i wysokość radiowa, przeciążenia na trzech osiach, prędkość i prędkości obrotu, czy w powietrzu, położenie kamery i jej wektor kierunku, typ statku powietrznego
- starty i lądowania wraz z lotniskiem; katastrofy, katapultowania, śmierci pilotów
- zestrzelenia i bycie zestrzelonym z obydwoma typami jednostek i uzbrojeniem; inne zdarzenia gry tak, jak zostały podane
- życia na misję (spawn ... session_end), zabójstwa, śmierci, dystans, najwyższa wysokość, najwyższe przeciążenie
- każda linia wysłana przez hak zachowana w całości w `heat.raw.parquet`, wraz z zrzutem tabel eksportu statku powietrznego raz na sekundę (silniki, podwozie i klapy, ładunek, środki przeciwdziałania, trasa, nawigacja) oraz każdy inny callback (pauza, czat, dołączanie graczy, wczytywanie misji)

## Skąd pochodzi {#where-it-comes-from}

hak watchera %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, linie UDP na 127.0.0.1:41993

## Jak to włączyć {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (dodaje Scripts\Hooks\heat3d-watch.lua), potem uruchom DCS ponownie

Wpisz polecenie w terminalu otwartym w folderze watchera (zob. [Zanim zaczniesz](before-you-start.md)). Jeśli się nie uda, ostatnia linia powie dlaczego; [Instalacja i uruchamianie](installing-and-running.md) opisuje typowe przyczyny.

`python -m heat3d_watch setup dcs` wypisuje pliki, które by zmienił; `python -m heat3d_watch setup dcs --apply` zmienia je, zachowując oryginał jako `<file>.heat3d-backup` (zob. [Polecenia](commands.md#setup)). Dla każdej zmiany wypisuje `dcs: changed: ...`, a gdy już jest włączone, `dcs: nothing to change`.

## Jak to działa {#how-it-works}

DCS World: mały skrypt haka należący do watchera, który wysyła linie UDP na 127.0.0.1:41993.

DCS uruchamia pliki Lua z `Saved Games\DCS*\Scripts\Hooks\` na starcie; hak może
korzystać z funkcji eksportu (`Export.Lo*`) i otrzymywać callbacki symulacji
(`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) – zob.
`<DCS>\API\DCS_ControlAPI.html` oraz <https://wiki.hoggitworld.com/view/DCS_Export_Script>.
`setup` zapisuje tam `heat3d-watch.lua` (własny plik: Export.lua i haki innych narzędzi
nie są ruszane), który wysyła dziesięć linii na sekundę, jedną dodatkową na sekundę
i po jednej na każde zdarzenie gry lub callback, nigdy nie czekając na odpowiedź. Port
41993 został dobrany tak, by hak JoyPro (41992) i Tacview (42674) działały obok niego.
Linie (pola rozdzielone znakiem `;`):

```text
hello;v=2                                       the hook was loaded
start;mission=..;map=..;me=<player id>;name=..;mp=0|1;file=..;server=0|1
mis;t=..;date.Day=..;start_time=..;weather...   the mission's date, start time and weather, flattened
p;t=<model s>;x=;y=;z=;lat=;lon=;alt=;hdg=;pitch=;bank=;ias=;agl=;g=;type=;tas=;mach=;vv=;aoa=;aos=;
  mhdg=;ralt=;gx=;gz=;vx=;vy=;vz=;wx=;wy=;wz=;air=;cx=;cy=;cz=;cfx=;cfy=;cfz=
d;t=..;self.Name=..;eng.RPM.left=..;mech.gear.value=..;pay.Stations.1.count=..;...   once a second
ev;t=..;name=<onGameEvent name>;args=a|b|c      every onGameEvent
cb;t=..;name=<callback>;args=a|b                every other callback (pause, chat, players, loading)
noexport;t=..                                   the server forbids ownship export
stop;t=..                                       the mission ended
```

`p` to LoGetSelfData: Position x/y/z – własne metry świata DCS, x na północ, y w górę,
z na wschód – plus LatLongAlt (stopnie, m), Heading/Pitch/Bank (radiany), z
LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) i LoGetAccelerationUnits()
x/y/z (g); a także, tak jak dokumentuje je `Scripts\Export.lua`: LoGetTrueAirSpeed (m/s),
LoGetMachNumber, LoGetVerticalVelocity (m/s), LoGetAngleOfAttack i LoGetAngleOfSideSlip
(rad), LoGetMagneticYaw (rad), LoGetRadarAltimeter (m), LoGetVectorVelocity (m/s w świecie),
LoGetAngularVelocity (rad/s), LoGetInAir oraz punkt i wektor kierunku z LoGetCameraPosition
(metry świata). `d` to zrzut całych tabel raz na sekundę, spłaszczonych do kluczy z kropkami:
LoGetSelfData (kraj, koalicja, nazwy jednostki i grupy, poziomy typu, flagi),
LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo,
LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute,
LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus oraz kilka liczb
(pauza, przyspieszenie czasu, miejsce, ciśnienie, odchylenia). Watcher zachowuje każdą linię
w całości w surowym sidecarze; `p` trafia też do wierszy.

Pozycje trafiają do tej samej płaskiej mapy co u innych symulatorów lotu (`Tangent`: x na
wschód, y – wysokość nad poziomem morza, z na północ, metry), liczone z LatLongAlt wokół
stałego początku teatru (`THEATRES`, z pola `map` linii startu), więc każda misja na jednym
teatrze dzieli jedną mapę, na którą viewer może położyć prawdziwy świat. Teatr spoza tabeli
bierze szerokość i długość pierwszego fixu zaokrąglone do pełnych stopni. Współrzędne DCS
x/y/z są zachowane jako `dcs_x`, `dcs_y`, `dcs_z`; fix bez LatLongAlt nie da się umieścić i
jest tylko liczony (`fixes_without_latlon`). Początek jest w `geo` sesji, w `meta.json` i w
stopce tabeli.

Argumenty onGameEvent, tak jak podaje je DCS_ControlAPI: takeoff/landing (playerID,
unit_missionID, airdromeName), crash/eject/pilot_death (playerID, unit_missionID), kill
(killerPlayerID, killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide,
weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide), mission_end
(winner, msg).

Serwer gry wieloosobowej może zabronić eksportu własnego statku (LoIsOwnshipExportAllowed
to false); wtedy nie ma pozycji, tylko zdarzenia, i sesja to mówi.

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisywane pozycje | tak |
| Oś w górę | `y` |
| Jednostki | metry (wschód, wysokość, północ od początku teatru) |
| Odbicie dla viewera | `z` |
| Skala jednostki (`scale`: viewer mnoży przez nią pozycje) | 1 |

Trafiają one do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`, więc viewer 3DHeat sam obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Gra wieloosobowa {#multiplayer}

- Oznaczona jako grana online (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „allowed (reads only what the game publishes)”.
- Rodzaj `telemetry`: czyta tylko to, co gra lub platforma udostępnia (port UDP albo pamięć współdzielona, które gra publikuje), więc nagrywa także w grze online; flaga decyduje tylko o tym, czy pamięć może kiedykolwiek być czytana.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Tylko adaptery `memory` czytają pamięć i nigdy dla gry oznaczonej jako grana online – zob. [Źródła i zasady](sources-and-rules.md).

## Zapisywane statystyki {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

Klucz w nawiasach klamrowych jest uzupełniany podczas działania (`score.{team}` to jeden klucz na drużynę). Klucze, które kod bierze z tabeli pól gry albo z jej własnych nazw statystyk, nie są na tej liście; „Co jest zapisywane” wyżej je wymienia.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co zawiera źródło, jest czytane lub zachowywane, nigdy pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzymuje, jest zachowywana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text` i każde pole zachowane po nazwie; `used` oznacza to, co stało się także wierszami), a `selfCheck.completeness` w `meta.json` liczy każdy `type` – `lost` to 0.

**Odczytane**

- `p` (10 Hz): pozycja, LatLongAlt, orientacja, IAS, AGL, przeciążenia (x/y/z), typ statku, a także TAS, Mach, prędkość pionową, AoA, ślizg, kurs magnetyczny, wysokość radiową, prędkość w świecie, prędkości obrotu, w powietrzu i punkt/wektor kamery z haka 2 – wszystko jako kolumny wierszy (jednostki tak, jak podaje je Export.lua)
- `start`: misja, teatr, własne id i nazwa gracza, gra wieloosobowa, plik misji, serwer; `mis`: data misji i godzina startu do meta.json
- `ev`: każde onGameEvent jako wiersz (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, każda inna nazwa tak, jak podana)
- `noexport` i `stop` jako wiersze i w meta.json

**Zachowane surowo**

- każda linia wysłana przez hak, w całości, jako `text` pod swoim rodzajem: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; linia innego rodzaju pod `unknown`
- `d` (1 Hz, tylko surowo): LoGetSelfData w całości (kraj, koalicja, nazwa jednostki i grupy, poziomy typu, flagi), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, wektor wiatru, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, radiolatarnie, pauza, przyspieszenie czasu, miejsce, ciśnienie, odchylenia – spłaszczone do kluczy z kropkami
- `mis`: tabela pogody misji, spłaszczona; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage z ich argumentami

**Niedostępne**

- inne jednostki (LoGetWorldObjects, LoGetObjectById) i dane czujników (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): nie są żądane – każdy obiekt misji 10 razy na sekundę jest kosztowny w ramce DCS, a serwer je ogranicza (allow_object_export, allow_sensor_export); Tacview je zapisuje
- cała tabela misji (DCS.getCurrentMission przechowuje każdą jednostkę i wyzwalacz, megabajty): wysyłane są tylko jej data, godzina startu, pogoda, sortie, teatr i wersja
- callbacki onPlayerTry\*: odpowiadają DCS (zezwalają lub odmawiają), więc hak ich nie rusza
- adresy innych graczy i UCID: net.get_player_info podaje je tylko serwerowi, a nie są własnością gracza do zachowania
- wpisy tabeli powyżej 800 kluczy lub 6 poziomów w głąb w jednej linii `d` są przycinane, żeby jedna linia była jednym datagramem

**Rozmiar**: około 20 MB na godzinę linii `p` (10 na sekundę, około 500 bajtów każda wraz z ramką) i 15–40 MB zrzutów `d` (jeden na sekundę, 4–10 KB zależnie od ładunku i trasy statku), przed kompresją zstd; powtarzające się klucze kompresują się około dziesięciokrotnie.

## Sprawdzone {#verified}

format linii przetestowany na syntetycznych datagramach; hak Lua nie był testowany wewnątrz DCS (napisany na podstawie API haków DCS i listy funkcji Lo\* z `Scripts\Export.lua`, nie uruchamiany)

## Źródło {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
