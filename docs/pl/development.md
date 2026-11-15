---
title: "Rozwój"
nav_order: 12
lang: "pl"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Rozwój {#development}

Ta strona dotyczy dodawania gry: jak buduje się adapter, jak się go testuje i jak powstaje jego dokumentacja.

## Repozytorium {#the-repository}

| Ścieżka | Co zawiera |
|---|---|
| `heat3d_watch/cli.py` | polecenia ([Polecenia](commands.md)) |
| `heat3d_watch/watcher.py` | pętla w tle: lista procesów, jeden wątek na adapter, aktualizacje |
| `heat3d_watch/session.py` | nagranie: `events.jsonl`, `heat.parquet`, `meta.json`, odzyskiwanie |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | ustawienia i folder danych |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | sprawdzenia pamięci i czytnik tylko do odczytu ([Odczyt pamięci](memory-reading.md)) |
| `heat3d_watch/notify.py` | powiadomienia Windows |
| `heat3d_watch/adapters/` | jeden moduł na grę lub rodzinę gier; moduły zaczynające się od `_` to wspólne pomocnicze |
| `heat3d_watch/decoders/` | dekodery telemetrii wyścigowej, skopiowane z rejestratorów okrążeń 3DHeat GameCapture |
| `heat3d_update/` | aktualizator ([Aktualizacje](updates.md)) |
| `mods/beamng/heat3d/` | mod protokołu BeamNG, który instaluje `setup beamng` |
| `tests/` | testy |
| `tools/gen_game_pages.py` | zapisuje strony gier tej dokumentacji |

## Adapter {#an-adapter}

Adapter to dataclass pochodzący od `heat3d_watch.adapters.base.Adapter`. Jego pola mówią, czym jest; jego metody wykonują pracę.

| Pole | Domyślnie | Co to jest |
|---|---|---|
| `id` | `""` | krótkie i stałe: foldery sesji, `disabled`, `replay_folders` i `player_names` odwołują się do niego |
| `game` | `""` | nazwa gry, tak jak ją piszą ludzie; sesje są zapisywane pod nią |
| `kind` | `"telemetry"` | jeden z: `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Źródła i zasady](sources-and-rules.md)) |
| `exes` | `()` | nazwy plików wykonywalnych (bez względu na wielkość liter), które oznaczają, że gra działa. Pusto: adapter działa zawsze (`always` ma wartość true) |
| `multiplayer` | `True` | gra jest grana online: jej pamięci nigdy nie czyta się |
| `source` | `""` | skąd pochodzą liczby, powiedziane raz |
| `records` | `()` | co jest zapisywane, jedna pozycja na każdy rodzaj rzeczy |
| `enable` | `""` | jak włączyć źródło; pusto, gdy nic nie trzeba |
| `interval` | `0.1` | sekundy między odpytaniami |
| `axes` | `Axes()` | pionowa oś świata, odbite osie, skala jednostek przeglądarki (zostaw 1) i uwaga o jednostkach |
| `verified` | `""` | co sprawdzono, uczciwie (zob. niżej) |
| `completeness` | `{}` | opis źródła zgodny z [zasadą konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: `read` (co staje się wierszami), `raw` (co zachowuje się w całości, pod jakim `type`), `missing` (czego źródło nie daje i dlaczego), `size` (jak duży na godzinę jest surowy strumień). Sekcja „Completeness” na stronie gry powstaje z tego |

`source`, `records`, `enable`, `verified` i `completeness` to dokumentacja, a nie ozdoba. `games` je wypisuje, `games --markdown` tworzy tabelę w [Wszystkie gry w jednej tabeli](watcher.md), a strony gier powstają z nich. Pisz je tak, by mówiły dokładnie to, co robi kod.

Metody, wszystkie opcjonalne:

| Metoda | Wywoływana | Co powinna robić |
|---|---|---|
| `missing(self) -> str \| None` | przez `games`, `status` i przed startem | powiedzieć, dlaczego adapter nie może tu działać (nie znaleziono DLL, brak folderu), albo `None` |
| `setup(self, ctx, *, apply) -> list[str]` | przez `setup` | włączyć własne wyjście gry; zwrócić jedną linię na zmianę i zmieniać pliki tylko wtedy, gdy `apply` jest prawdą. Przed pierwszą zmianą pliku zrobić kopię `<file>.heat3d-backup` i nigdy jej nie nadpisywać. Nadpisuj tylko wtedy, gdy jest co włączyć: `can_setup` (prawda, gdy `setup` jest nadpisane) decyduje, czy `setup` to wykona, czy powie, że nie ma nic do zmiany; klasa obsługująca kilka gier nadpisuje `can_setup` dla tych, których nie da się skonfigurować (`RallyAdapter` dla Richard Burns Rally). |
| `start(self, ctx)` | gdy pojawi się proces gry (adaptery działające zawsze: gdy startuje `run`) | otworzyć gniazda, znaleźć pliki, zapamiętać, od czego zacząć |
| `poll(self, ctx)` | co `interval` sekund, we własnym wątku adaptera | zebrać to, co gra powiedziała od ostatniego odpytania, i zapisać |
| `stop(self, ctx)` | gdy gry już nie ma albo watcher się zatrzymuje | zamknąć sesje i gniazda |

Każdy adapter działa we własnym wątku (`Runner`). Wyjątek w `poll` jest zapisany w dzienniku i adapter czeka `min(5, interval × 10 + 0.5)` sekund przed kolejnym odpytaniem. Po 20 błędach z rzędu albo po błędzie w `start` adapter jest zatrzymywany i nie uruchamia się ponownie, aż zmieni się id procesu gry. `missing()` jest sprawdzane przy każdym skanowaniu, więc niech będzie tanie.

Obiekt adaptera jest używany ponownie, gdy gra znów się uruchomi, więc `start` musi zresetować wszystko, co zostawił poprzedni przebieg.

### Rejestracja {#registering-it}

Umieść moduł w `heat3d_watch/adapters/` i wypisz adaptery na jego końcu:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` importuje każdy moduł pakietu (poza `base` i nazwami zaczynającymi się od `_`) i zbiera ich `ADAPTERS`. Dwa adaptery o tym samym id przerywają ładowanie z `ValueError`. Moduł, który nie daje się zaimportować (brakuje zależności), pomija swoje gry, a `games` wypisuje go z błędem, więc problem jednej gry nie zatrzymuje pozostałych.

## Context i Session {#context-and-session}

`start`, `poll`, `stop` i `setup` dostają `Context`:

| Składnik | Co to jest |
|---|---|
| `settings` | `Settings` ([Instalacja i uruchamianie](installing-and-running.md#settings)) |
| `data` | folder danych |
| `pid`, `exe` | id procesu gry i ścieżka pliku wykonywalnego, gdy adapter został uruchomiony dla działającej gry; folder instalacji jest obok `exe` |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | nowa `Session`. `game` nadpisuje nazwę gry adaptera (dla adapterów obejmujących wiele gier); `when` ustawia początek dla sesji opisujących przeszłość; `axes`, `source` i `multiplayer` domyślnie są z adaptera; `meta` to słownik zapisywany do `meta.json`; `geo` (`{"lat0": .., "lon0": ..}` albo ustawione potem `session.geo`) umieszcza sesję mapy płaskiej na Ziemi, w `meta.json` i w stopce tabeli |
| `close(session)` | kończy sesję: tabelę, `heat.raw.parquet`, `meta.json` i jej wiersz w `watcher.sqlite`. Sesja bez zdarzeń i bez surowych elementów jest usuwana; sesja z samymi surowymi elementami zostaje (bez tabeli, bez wiersza w bazie). Przyjmuje `None`. Zwraca ścieżkę tabeli albo `None`. |

`Session` zapisuje:

| Składnik | Co robi |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | jeden wiersz. `t` domyślnie to sekundy od początku sesji, `ms` – teraz. Pozycja liczy się tylko wtedy, gdy podano wszystkie `x`, `y` i `z` i są skończone. Atrybuty `None` są pomijane. |
| `position(x, y, z, **kw)` | zdarzenie o nazwie `position` |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | zachować jedną rzecz, którą źródło wysłało, w całości: bajty pakietu albo strony (`payload`), linię albo odpowiedź JSON tak, jak przyszła (`text`), albo wartości odczytu po nazwach (`fields`, każda jako osobna kolumna). `type` to słowo źródła na tę rzecz (id pakietu, nazwa mapowania, zdarzenie dziennika, endpoint); `used` mówi, że stała się też wierszami. Zapisywane do `raw.bin` w chwili wywołania, potem do `heat.raw.parquet` (zstd) przy zamknięciu albo odzyskaniu sesji i liczone według `type` w `meta.json` pod `selfCheck.completeness` |
| `stat(key, value, how="set")` | statystyka: `set` ustawia, `add` dodaje, `max` albo `min` zachowuje największą lub najmniejszą wartość |
| `now()` | sekundy od początku sesji |
| `meta` | słownik zapisywany do `meta.json` |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | kiedy, gdzie i co zapisano do tej pory |

`event`, `stat` i `raw` są bezpieczne dla wątków i mogą być wywoływane z wątku roboczego.

**Każdy adapter zachowuje wszystko, co wysyła jego źródło.** Wiersze to to, co rysuje przeglądarka; nie są zapisem. Każdy pakiet, który dociera do portu, każda odczytana strona pamięci dzielonej (cała mapa, za każdym razem gdy się zmieni), każda linia dziennika albo skryptu eksportu (także te, które adapter ignoruje), każda odpowiedź JSON albo wysłany dokument trafia do `session.raw(...)` w chwili, gdy przychodzi – niezależnie od tego, czy staje się wierszem – i nic nie jest przerzedzane poniżej tempa, w jakim adapter czyta. Element, który przychodzi przed otwarciem sesji, otwiera ją (sesja z samymi surowymi elementami zostaje) albo czeka, aż sesja się otworzy; nigdy nie jest odrzucany. Pola tanie w dekodowaniu i pewne w znaczeniu trafiają też do wierszy. To jest [zasada konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: strumień na żywo znika w chwili wysłania, więc to, czego adapter nie zachowa, przepada na zawsze, a to, co zachowa w całości, można zdekodować w dniu, w którym ktoś zrozumie format. Cenę płaci się rozmiarem; kompresja zstd i kodowanie słownikowe trzymają go w ryzach, a nie przez pomijanie rzeczy. Test każdego adaptera wysyła coś, czego nie używa, i sprawdza, że wraca w całości z `heat.raw.parquet` oraz że `selfCheck.completeness.lost` wynosi 0. `racing.Driving.raw` robi to samo dla adapterów wyścigowych (i otwiera sesję), a `racing.Pages` zachowuje strony pamięci dzielonej za każdym razem, gdy zmieni się ich zawartość, i liczy w `meta.json` w `unchanged_reads` odczyty, które nie przyniosły nic nowego.

Konwencje, na których polega reszta systemu:

- **Wiersze gracza są oznaczone na podstawie tego, co mówi źródło.** `player="me"`, gdy źródło jest grą gracza; gdy każdy gracz jest zapisany pod nazwą, `own_car=1` w wierszach samochodu gracza (po indeksie gracza w grze albo po obserwowanym uczestniku), albo nazwa gracza jako `session.meta["player"]` (od razu zapisana w `meta.json`), gdy źródło podaje nazwę gracza. Nigdy nie zgaduj: gdy źródło nie mówi, weź nazwę z ustawienia (`player_names`, `riot_id`) albo nie oznaczaj niczego.
  [Najlepsze momenty NVIDIA](nvidia-highlights.md) biorą pozycje tylko z takich wierszy (`platform.own_row`). Inni gracze są rozpoznawani po nazwie lub id.
- **Trasy są ograniczone zdarzeniami z pozycjami:** `spawn`, `respawn` i `session_start` zaczynają trasę; `death`, `finish`, `session_end` i `teleport` ją kończą. Gdy gracz przemieścił się bez podróżowania (reset, cofnięcie, szybka podróż, wczytany zapis), zapisz `teleport` w miejscu, które opuścił, a potem początek (`spawn`, albo `respawn` przy resecie nazwanym przez grę) w miejscu, do którego dotarł, tak by linia ciepła przeglądarki kończyła jedną trasę i zaczynała następną zamiast rysować przez całą mapę. `Driving.jumped` robi to dla pojazdów.
- **Pozycje zostają we własnych współrzędnych i jednostkach świata gry**, opisanych przez `axes`. Nie przeliczaj ich na inny układ, chyba że gra nie daje użytecznego układu świata (symulatory lotu zamieniają szerokość i długość geograficzną na mapę płaską, `Tangent`, wokół pierwszego namiaru – DCS wokół stałego początku swojego teatru – i przekazują `geo=tangent.geo()` do `open`, tak że stopka mówi, gdzie na Ziemi leży mapa). `axes.scale` to skala jednostek przeglądarki – mnoży każdą pozycję – i zostaje 1, dzięki czemu wiersze pasują do poziomu wyeksportowanego z tej samej gry w tych samych jednostkach; jednostkę podaj w `axes.units`.
- **Klucze statystyk** są pisane małymi literami z podkreślnikami i niosą jednostkę, gdy ma zastosowanie (`distance_km`, `top_speed_kmh`, `max_altitude_m`, `duration_s`). Czas zapisywany jako najlepszy zaczyna się od `best_` (zapisywany z `min`), miejsce kończy się na `_position`: `stats` pokazuje najmniejszą z tych wartości jako najlepszą, a największą z każdego innego klucza (`db.lower_is_better`).

## Pomocnicze {#helpers}

| Pomocnik | Moduł | Do czego |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | śledzenie dziennika, który zapisuje gra: odczyty współdzielone, tylko linie tej sesji, nowe i zastąpione pliki, tylko pełne linie |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` z `try_open(who)`, `receive()`, `close()` | `racing` | port telemetrii UDP na 127.0.0.1, zajmowany tylko gdy jest wolny, oddawany innemu programowi, opcjonalnie przekazywany dalej |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` z `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | sesje pojazdów: pozycje w stałym tempie, dystans, prędkość maksymalna, okrążenia; przy skoku `teleport` tam, gdzie był samochód, i `spawn` tam, gdzie jest (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | nazwana pamięć dzielona gry, tylko do odczytu, nigdy nietworzona |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | obserwowany folder powtórek: pliki konwertowane, gdy przestaną rosnąć, w wątku roboczym; pierwsze spojrzenie tylko zauważa, co tam jest, a `convert_existing(ctx, folder=None)` – polecenie [`replays`](commands.md#replays) – konwertuje te na żądanie |
| `load_state`, `save_state` | `platform` | zapamiętywanie tego, co adapter działający zawsze już widział, w `<data>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | ewidencja lotów (starty, lądowania, katastrofy, dystans) i mapa płaska wokół pierwszego namiaru (`Tangent.geo()` to `geo` sesji) |
| `backup_once(path)` | `gsi`, `racing` | zasada `<file>.heat3d-backup` |
| Pliki Steam | `_steam` | binarne i tekstowe KeyValues, folder Steam z rejestru |

Minimalny adapter dziennika, dla przykładu (wymyślona gra):

```python
from dataclasses import dataclass, field
from pathlib import Path

from ..session import Axes, Session
from ._logfollow import Follower, game_started, newest
from .base import Adapter, Context


@dataclass
class ExampleAdapter(Adapter):
    _session: Session | None = field(default=None, repr=False)
    _follow: Follower | None = field(default=None, repr=False)

    def start(self, ctx: Context) -> None:
        log = (ctx.exe.parent if ctx.exe else Path(".")) / "logs" / "game.log"
        self._session = None
        self._follow = Follower(lambda: newest(p for p in [log] if p.exists()), game_started(ctx.pid))

    def poll(self, ctx: Context) -> None:
        for line in self._follow.lines() if self._follow else []:
            if line.startswith("DIED "):
                if self._session is None:
                    self._session = ctx.open(self)
                self._session.event("death", player="me")
                self._session.stat("deaths", 1, "add")

    def stop(self, ctx: Context) -> None:
        self.poll(ctx)
        ctx.close(self._session)
        self._session = None


ADAPTERS = [
    ExampleAdapter(
        id="example",
        game="Example Game",
        kind="log",
        exes=("ExampleGame.exe",),
        source=r"<install>\logs\game.log (followed)",
        records=("deaths",),
        interval=0.5,
        axes=Axes(units="no positions recorded"),
        verified="tested on synthetic log lines in the game's format; untested against the game",
    )
]
```

Otwórz sesję przy pierwszej rzeczy wartej zapisania, a nie w `start`, tak by gra zostawiona w menu nie zostawiała śladu (pusta sesja i tak jest usuwana).

## Testy {#tests}

```bash
python -m pytest
```

`tests/conftest.py` daje każdemu testowi jednorazowy folder danych (`HEAT3D_WATCH_HOME`) i wyłącza sprawdzanie aktualizacji oraz powiadomienia (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). Test adaptera buduje wyjście gry z jej opublikowanego formatu – pakiety ze specyfikacji, linie dziennika w formacie gry, pliki w udokumentowanym układzie – i steruje adapterem bezpośrednio (skrócone z `tests/test_poe.py`; `data` i `install` to tymczasowe foldery):

```python
from dataclasses import replace
from heat3d_watch.adapters import poe
from heat3d_watch.adapters.base import Context
from heat3d_watch.config import Settings
from heat3d_watch.session import read_rows

ctx = Context(Settings(data=str(data)), data, exe=install / "PathOfExileSteam.exe")
a = replace(poe.ADAPTERS[0])   # a fresh copy of the adapter
a.start(ctx); a.poll(ctx); a.stop(ctx)
[session] = list((data / "sessions").glob("*/*"))
rows = read_rows(session)      # then check the rows and meta.json's stats
```

Adaptery sieciowe testuje się na fałszywym lokalnym serwerze albo wysyłając pakiety UDP do adaptera. Testy sprawdzające prawdziwe dane gry na komputerze dewelopera są oznaczone `@pytest.mark.local` i pomijane tam, gdzie tych danych nie ma. Te dane nigdy nie trafiają do repozytorium. `test_core.py` zawiera też test, który nie przechodzi, jeśli w pakiecie pojawi się jakikolwiek kod mogący zapisywać do innego procesu (`test_memory_reading_cannot_write`).

## Uczciwe `verified` {#an-honest-verified}

`verified` mówi, co sprawdzono i jak, oraz czego nie sprawdzono. Pokazują to `games` i każda strona gry, a gracze na tym polegają. Przykłady z kodu:

- „tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent over UDP; untested against the game”
- „tested on documents in the published GSI format posted to the running adapter; untested against the running game”
- „tested on real stats files and schemas from a local install; change detection tested on files built in the binary KeyValues format”

Pisz „untested against the game”, dopóki adapter nie nagrał działającej gry. Podaj tylko metodę i tolerancję: nigdy mapy, id meczu, nazwy gracza, daty, wielkości zbioru ani dokładnej liczby z prawdziwych plików, i nigdy „this machine” (czytelnicy tego nie znają). Nazwij źródło każdego przesunięcia i każdego układu, i powiedz, gdzie porównano dwa źródła. Nigdy nie twierdź więcej, niż zrobiono. Format, który został zgadnięty albo wzięty z narzędzi społeczności, opisuje się jako taki.

## Strony gier {#the-game-pages}

Każda strona w [Gry](games.md) jest generowana z adapterów, więc zawsze zgadza się z kodem. Po dodaniu albo zmianie adaptera wygeneruj je ponownie z folderu repozytorium:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(W PowerShell: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Dodaj `--check`, by tylko porównać: nic nie zapisuje i kończy się kodem 1, gdy strona jest nieaktualna (dotyczy też tabeli gier w `docs/watcher.md`).

Skrypt:

- ładuje adaptery przez `heat3d_watch.adapters.load()`, przy pustym tymczasowym folderze danych, tak by żaden profil pamięci ani ustawienie z twojego komputera nie trafiły na strony. Adaptery pamięci są pomijane, bo pochodzą z własnych profili graczy;
- nic nie zapisuje, jeśli moduł adaptera nie daje się zaimportować (strony straciłyby te gry);
- zapisuje `docs/game-<adapter id>.md` dla każdego adaptera i `docs/games.md` z tabelą przeglądową, a strony adapterów, które już nie istnieją, usuwa;
- bierze „What is recorded”, „Where it comes from”, „How to switch it on”, osie, flagę gry sieciowej i „Verified” z pól adaptera;
- zamienia docstring modułu w „How it works”. Pisz docstringi w zwykłym tekście, którego moduły już używają, a który skrypt przerabia: akapity; listy z `*`, `-` albo `1.`; układy i przykłady wcięte pod linią, która je wprowadza (stają się blokami kodu); tytuł podkreślony myślnikami albo krótki tytuł z tekstem wciętym bezpośrednio pod nim (stają się nagłówkami);
- wypisuje klucze statystyk, które kod adaptera ustawia po nazwie – `.stat("key", ...)`, obie strony wyrażenia `if` i wzorce f-stringów takie jak `score.{team}` – w klasach adaptera i w pomocnikach, których używa. Klucze brane ze zmiennej (tabela pól gry) nie są wypisywane;
- decyduje o „Positions” na podstawie `axes.units` (uwaga zaczynająca się od „no” albo „none” oznacza brak pozycji) i tego, co zapisuje jego kod.

Nie edytuj wygenerowanych stron ręcznie: zmień adapter i uruchom skrypt ponownie. Tabela w [Wszystkie gry w jednej tabeli](watcher.md) to wynik `python -m heat3d_watch games --markdown`.
