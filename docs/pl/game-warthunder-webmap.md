---
title: "War Thunder (stan gry)"
nav_order: 47
lang: "pl"
source: game-warthunder-webmap.md
source_hash: "d6026c277030"
nav_exclude: true
search_exclude: true
---
# War Thunder (stan gry) {#war-thunder-game-state}

Podczas gry w War Thunder watcher zapisuje to, co gra przekazuje programom na twoim komputerze, dzięki czemu możesz później obejrzeć to na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `warthunder-webmap`, rodzaj [`gsi`](sources-and-rules.md); działa, gdy działa `aces.exe`, i sprawdza nowe dane co 0,5 s.*

## Co jest zapisywane {#what-is-recorded}

- własna pozycja (wschód/północ na mapie w metrach; wysokość z /state w samolocie, w przeciwnym razie 0) dwa razy na sekundę, kurs, prędkość
- pojawienia się i opuszczenie mapy przez własny pojazd (zniszczony, wylądował, powrót do hangaru), jedna wyprawa za każdym razem
- inne samoloty i jednostki naziemne na minimapie jako pozycje ze śledzonymi id i stroną (bez wysokości)
- lotniska, strefy przechwytywania i bazy raz, oraz zmiany strony stref
- wiersze z kanału zabójstw i obrażeń (kto, pojazd, czasownik); zabójstwa i śmierci gracza, gdy ustawiona jest twoja nazwa (`config --set player_names.warthunder-webmap=<nazwa>`)
- pojawienia się, dystans, najwyższa wysokość, najwyższa prawdziwa prędkość powietrzna, pojazd; zabójstwa i śmierci przy ustawionej nazwie
- każda odpowiedź mapy webowej zachowana w całości w heat.raw.parquet - pełne /state i /indicators, czat, cele bitwy i obraz mapy także; między bitwami w osobnej sesji

## Skąd pochodzą dane {#where-it-comes-from}

lokalna mapa webowa gry, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## Jak to włączyć {#how-to-switch-it-on}

Nic nie trzeba włączać: watcher czyta źródło tak, jak udostępnia je gra lub platforma.

## Jak to działa {#how-it-works}

War Thunder: lokalna mapa webowa gry na <http://127.0.0.1:8111>.

Gra udostępnia stronę, którą może pokazać drugi ekran albo telefon („mapa webowa”), oraz JSON za nią, gdy działa - we wszystkich trybach, także wieloosobowym:

```text
/map_info.json   {"map_min": [x, y], "map_max": [x, y], "grid_steps", "grid_zero", "map_generation",
                  "hud_type", "valid"}: zasięg mapy w metrach; valid false w hangarze
/map_obj.json    [{"type": aircraft|ground_model|airfield|capture_zone|bombing_point|defending_point|
                  respawn_base_*|..., "icon": Player|Fighter|Bomber|Mediumtank|SPAA|..., "color": "#rrggbb",
                  "x", "y" (0..1 obrazu mapy, y w dół), "dx", "dy" (kierunek),
                  airfields "sx", "sy", "ex", "ey"}]: to, co pokazuje minimapa; własny pojazd gracza
                  z ikoną "Player"; bez id, bez wysokości
/state           {"valid", "H, m", "TAS, km/h", "IAS, km/h", "M", "Vy, m/s", ...}: wartości lotu,
                  ważne tylko w samolocie
/indicators      {"valid", "army": air|tank|..., "type": pojazd}
/hudmsg?lastEvt=N&lastDmg=M   {"events": [...], "damage": [...]} nowsze niż podane id, każde
                  {"id", "msg", "sender", "enemy", "mode", "time"}; linie obrażeń brzmią jak
                  "Nazwa (Pojazd) shot down Nazwa (Pojazd)"
/gamechat?lastId=N  czat nowszy niż podane id, [{"id", "msg", "sender", "enemy", "mode", "time"}]
/mission.json    cele bitwy i ich stan
/map.img         obraz mapy, na którym strona rysuje obiekty
```

Każda odpowiedź jest zachowywana w całości w surowym pliku dodatkowym sesji pod swoim adresem (map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img); między bitwami odpowiedzi trafiają do osobnej sesji.

Pozycja na mapie staje się metrami dzięki zasięgowi: u = min_x + x \* (max_x - min_x) na wschód, v = max_y - y \* (max_y - min_y) na północ (y obrazu biegnie w dół). Wiersze mają x = u, y = wysokość (`H, m` własnego samolotu; 0 dla wszystkiego innego), z = v, więc Y jest w górę; z jest lustrzane dla przeglądarki, aby północ nie była rysowana na południu.

Kolory pokazują strony tak, jak widzi je gracz: własne żółte (domyślnie #faC81E), drużyna zielona, sojusznicy niebiescy (#174DFF), wrogowie czerwoni (#f40C00); palety dla daltonistów zmieniają je, więc decyduje odcień, a nie dokładna wartość. Gra nikogo nie nazywa na mapie i nie nadaje obiektom id: inne obiekty dostają tu id, bo są śledzone od odpytania do odpytania (najbliższy tego samego typu i ikony), co może zamienić miejscami dwa samoloty tego samego typu, które przelatują blisko siebie. Nazwa własnego gracza nie jest też w API: podaj ją w ustawieniach (`config --set player_names.warthunder-webmap=<twoja nazwa>`), a linie kanału zabójstw dotyczące gracza staną się zabójstwami i śmierciami; bez niej są zapisywane jako kanał zabójstw.

Źródła: strona gry <http://127.0.0.1:8111> i jej JSON; fakty o polach opisane w projekcie JoyPro 2 (docs/telemetry-recording.md; GPL, użyte tylko dla faktów).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisywane pozycje | tak |
| Oś pionowa | `y` |
| Jednostki | metry (wschód/północ na mapie; wysokość tylko dla własnego samolotu) |
| Lustrzane odbicie dla przeglądarki | `z` |
| Skala jednostek (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Trafiają one do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`, więc przeglądarka 3DHeat sama obraca i skaluje wiersze - zobacz [Dane](the-data.md).

## Gra wieloosobowa {#multiplayer}

- Oznaczona jako grana online (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „dozwolone (czyta tylko to, co gra publikuje)”.
- Rodzaj `gsi`: czyta tylko to, co gra lub platforma udostępnia (interfejs stanu gry lub lokalne API, które gra udostępnia), więc zapisuje także w grze online, a w trybie offline; flaga decyduje tylko o tym, czy wolno kiedykolwiek czytać pamięć.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Pamięć czytają tylko adaptery `memory`, i nigdy dla gry oznaczonej jako grana online - zobacz [Źródła i zasady](sources-and-rules.md).

## Zapisywane statystyki {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

Klucz w nawiasach klamrowych jest uzupełniany podczas działania (`score.{team}` to jeden klucz na drużynę). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” powyżej podaje je z nazwy.

## Kompletność {#completeness}

Watcher stosuje zasadę konwertera 3DHeat ([zasada konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)): to, co zawiera źródło, jest odczytywane albo zachowywane, nigdy pomijane. Oprócz wierszy każdy pakiet, strona, linia czy odpowiedź, którą odbiera adapter, jest zachowywana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem pola zachowane po nazwie; `used` oznacza, co też stało się wierszami), a `selfCheck.completeness` w `meta.json` liczy każdy `type` - `lost` wynosi 0.

**Odczytywane**

- /map_info.json: zasięg mapy i siatka (metry, id mapy) do meta.json; nieprawidłowe kończy bitwę
- /map_obj.json (dwa razy na sekundę): własny pojazd, inne samoloty i jednostki naziemne (śledzone id, strona z koloru, ikona, kurs, kolor) oraz lotniska, strefy i bazy jako wiersze
- /state (dwa razy na sekundę, w samolocie): wysokość, TAS, IAS, Mach i Vy we własnych wierszach
- /indicators (co 2 s): armia i typ pojazdu
- /hudmsg (raz na sekundę): linie kanału zabójstw i obrażeń jako zabójstwa, śmierci, trafienia i wiersze kanału; inne zdarzenia HUD jako wiersze

**Zachowywane w całości**

- każda odpowiedź w całości, `text` to JSON taki, jaki wysłała gra, pod swoim adresem: `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission`; `map_img` to bajty obrazu mapy jako `payload`, raz w bitwie
- to, co trzyma tylko surowy plik dodatkowy: każde pole /state poza pięcioma odczytywanymi (AoA, AoS, Ny, Wx, przepustnica, obroty, paliwo, ... - zestaw jednego samolotu różni się od innego), każde pole /indicators (przyrządy kokpitu samolotów, prędkość, bieg, załoga i stabilizator czołgów), inne klucze obiektów mapy (color[], blink, icon_bg, końce lotnisk), sender, enemy i mode z hudmsg, czat (/gamechat, raz na sekundę), cele bitwy i ich stan (/mission.json, co 10 s w bitwie), linie powiedziane przed startem watchera
- między bitwami (hangar, ładowanie) odpowiedzi trafiają do osobnej sesji oznaczonej w meta.json jako `between_battles`, która nie ma wierszy

**Niedostępne**

- nazwy, id i wysokości pojazdów innych graczy: mapa webowa ich nie ma (id są tu nadawane przez śledzenie obiektów od odpytania do odpytania); kanał zabójstw nazywa graczy bez pozycji
- wszystko poza mapą webową: powtórki gry czyta konwerter powtórek War Thunder, a pamięć gry nie jest nigdy czytana (gra online)
- /map_obj.json częściej niż dwa razy na sekundę: częstotliwość odpytywania jest niska, żeby nie obciążać własnego serwera WWW gry

**Rozmiar**: około 50-120 MB na godzinę JSON przed zstd w bitwie (map_obj 5-15 KB dwa razy na sekundę, state około 1,5 KB dwa razy na sekundę, indicators co 2 s, czat i linie HUD małe) plus obraz mapy raz w bitwie (poniżej 2 MB); 1-2 MB na godzinę między bitwami (wygląd mapy dwa razy na sekundę, HUD i czat raz, każdy jako krótka odpowiedź); zstd zmniejsza powtarzający się JSON ponad dziesięciokrotnie

## Sprawdzone {#verified}

przetestowane na fałszywym lokalnym serwerze, który podaje odpowiedzi w formacie mapy webowej gry; nieprzetestowane z działającą grą

## Źródło {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
