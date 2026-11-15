---
title: "NVIDIA Highlights"
nav_order: 8
lang: "hr"
source: nvidia-highlights.md
source_hash: "a3b769ab065c"
nav_exclude: true
search_exclude: true
---
# NVIDIA Highlights {#nvidia-highlights}

Neke igre traže od vašeg NVIDIA upravljačkog programa da spremi kratak video kad se nešto dogodi, na primjer ubojstvo. Watcher bilježi svaki takav trenutak i, kad može, stavlja ga na kartu tamo gdje se dogodio.

Adapter `nvidia-highlights` bilježi isječke, istaknute trenutke i snimke zaslona koje NVIDIA aplikacija (ili GeForce Experience) sprema, i svakom daje mjesto na karti kad ga može naći. Ova stranica objašnjava što NVIDIA Highlights može isporučiti, a što ne, koje datoteke watcher čita i kako istaknuti trenutak dobiva poziciju. Generirana stranica adaptera je [NVIDIA highlights (platforma)](game-nvidia-highlights.md).

## Što NVIDIA Highlights može, a što ne može isporučiti {#what-nvidia-highlights-can-and-cannot-deliver}

Igra koja podržava NVIDIA Highlights razgovara s NVIDIA aplikacijom preko NVIDIA-inog GfeSDK-a. SDK nosi samo dvije vrste poruka:

1. **Jednom, na početku**: vrste istaknutih trenutaka koje će igra koristiti - ID (npr. `kill`), važnost, oznake i prikazni naziv po jeziku. NVIDIA aplikacija ih sprema po igri.
2. **U trenutku igre**: "istaknuti trenutak `<id>`, od `<ms>` prije sada do `<ms>` poslije". To je cijela poruka: ID vrste koju je igra registrirala i dva vremenska pomaka koji NVIDIA aplikaciji kažu koji dio njezine kontinuirane snimke treba zadržati.

SDK **nema polje ni za što drugo**: nema pozicije, utakmice ili runde, protivnika, oružja, rezultata, nikakvih prilagođenih podataka. Igra ne može staviti poziciju u istaknuti trenutak čak i kad bi to htjela. Kad se isječak spremi, NVIDIA aplikacija dodaje datoteku, ime igre, trajanje i vrijeme.

Dakle, istaknuti trenutak može reći samo "ova vrsta trenutka, u ovoj igri, u ovo vrijeme". Sve više mora doći odnekud drugdje.

## Što watcher čita {#what-the-watcher-reads}

Sve se čita iz datoteka koje NVIDIA aplikacija piše za svoju galeriju. Ništa ne razgovara s upravljačkim programom ili aplikacijom. Mapa NVIDIA Overlay je `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| Datoteka | Što se iz nje uzima |
|---|---|
| `UGCTracker.json` | indeks galerije: svaki isječak i snimka zaslona s putanjom, vrstom (video, slika), podvrstom (`InstantReplay`, ...), datumom, nazivom profila igre, izvršnom datotekom i kratkim nazivom igre, te duljinom (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, mapa za snimanje, i `settings.tempDirectory`, gdje istaknuti trenuci čekaju dok se ne spreme (`<temp>\Highlights\<game>`) |
| `Highlights\<game>\config.json` | vrste istaknutih trenutaka koje je svaka igra registrirala: ID, i engleski prikazni naziv (ili ID ako ga igra nije dala) |
| mapa za snimanje (zadano `%USERPROFILE%\Videos\NVIDIA`) i `<temp>\Highlights` | same datoteke isječaka i snimki zaslona (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), jedna mapa po igri |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | zahtjevi koje bilježe igre s GfeSDK-om - redci `Posted Request HL...` - pa se istaknuti trenutak koji je igra zatražila bilježi čak i kad nijedan isječak nije sačuvan. Zahtjevi za konfiguraciju (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) se preskaču. |

Za svaku novu stavku adapter piše jedan redak: `highlight` za video, `screenshot` za sliku ili `highlight_request` za redak GfeSDK zapisnika. Njegova polja:

| Polje | Što je |
|---|---|
| `ms` | trenutak: vrijeme u imenu datoteke (`<Game> 2026.05.01 - 20.31.28.115.DVR.mp4`, lokalno vrijeme kad je isječak spremljen), inače datum iz indeksa, inače vrijeme izmjene datoteke |
| `game` | naziv NVIDIA profila, ime mape ili ime igre iz imena datoteke |
| `clip`, `media` | putanja datoteke; `video`, `image` ili `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (iz privremene mape istaknutih trenutaka) ili podvrsta iz indeksa |
| `duration_s`, `clip_start_ms` | duljina, iz indeksa ili iz vlastitog zaglavlja videa (`moov/mvhd`, pronađeno bez čitanja videa); trenutak kad isječak počinje |
| `highlight_id`, `highlight_name` | vrsta istaknutog trenutka, kad ga nešto imenuje (vidi dolje) |
| `exe` | izvršna datoteka igre, iz indeksa |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | posuđena pozicija, kad je nađena (vidi dolje) |

Statistika sesije je `clips`, `screenshots`, `clip_seconds` i `placed` (stavke koje su dobile poziciju).

**ID istaknutog trenutka** nije zapisan ni na jednom dokumentiranom mjestu. Adapter pokušava dva nedokumentirana: polje unosa galerije čiji naziv sadrži "highlight", i - samo za datoteke u privremenoj mapi istaknutih trenutaka - jedan od ID-ova koje je igra registrirala (duljine najmanje 4 znaka) koji se pojavljuje u imenu datoteke. Spremljeni isječak nosi ime po igri, pa bi u njemu slučajno mogao biti ID poput "kill", zato se njegovo ime ne pretražuje. Ova dva načina na pravom računalu još nisu viđena da rade: nije se pojavio isječak s ID-om istaknutog trenutka, ni redak GfeSDK zahtjeva, na mjestu gdje je adapter testiran. Indeks galerije, postavke, definicije istaknutih trenutaka i isječci testirani su na pravim datotekama.

### Kada se stavke bilježe {#when-items-are-recorded}

- Isječak se još neko vrijeme piše nakon pritiska tipke. Adapter čeka dok datoteka ne ima istu veličinu i vrijeme pri dva pregleda (svakih 10 s) i dok nije stara najmanje 5 s.
- Pri prvom pokretanju adapter samo zabilježi ono što je već u galeriji i zapisnicima, ne bilježi to, da godine starih isječaka ne preplave statistiku. Što je vidio pohranjeno je u `<data>\state\nvidia-highlights.json`, pa ponovno pokretanje ništa ne bilježi dvaput.
- Stavke se grupiraju u jednu sesiju po igri. Sesija igre se zatvara nakon 30 minuta bez nove stavke, i završava na svojem zadnjem trenutku, a ne kad se igra zatvorila. Trenuci udaljeni više od 30 minuta idu u zasebne sesije.

## Kako istaknuti trenutak dobiva poziciju {#how-a-highlight-gets-a-position}

Sam istaknuti trenutak nema mjesto. Adapter traži trenutak u drugim snimkama koje je watcher napravio za istu igru u isto vrijeme:

1. **Ista igra**: mape sesija pod `<data>\sessions\` čiji se naziv igre podudara s nazivom istaknutog trenutka. Nazivi se uspoređuju malim slovima, samo slova i brojke. Podudaraju se kad su jednaki, ili kad je kraći dugačak najmanje 5 znakova i sadržan je u dužem (`Counter-Strike 2` i `Counter-Strike-2`).
2. **Isto vrijeme**: sesije čiji početak i kraj (iz `meta.json`, uz sekundu rezerve na objema stranama) pokrivaju trenutak. Sesije koje su završile bez pozicija, i vlastite sesije adaptera, preskaču se.
3. **Vlastiti redak igrača**: u njegovu `events.jsonl`, najkasniji vlastiti redak igrača s pozicijom, u trenutku ili najviše 5 sekundi prije njega. Redak je vlastit kad to njegov izvor kaže: `"player": "me"`, ili `"own_car": 1` (igre utrka koje bilježe svaki automobil po vozaču), ili `player` koji je `player` sesije u `meta.json` (ime koje izvor daje igraču). Vidi [Vlastiti redci igrača](the-data.md#the-players-own-rows).

Ako se redak nađe, istaknuti trenutak dobiva svoje `x`, `y`, `z`, svoju `session` (ili ime mape), `position_from` (mapa iz koje je došao) i `position_lag_ms` (koliko je prije trenutka taj redak bio). Istaknuta sesija preuzima osi te snimke, pa se crta na isti način. Ako se redak ne nađe, istaknuti trenutak ostaje kao trenutak na vremenskoj crti bez mjesta.

Stvari koje treba znati o posuđenoj poziciji:

- **To je gdje ste bili kad je isječak spremljen**, ne gdje je radnja počela. Trenutak je vrijeme spremanja iz imena datoteke, što je kod Instant Replaya njegov kraj. `clip_start_ms` kaže kad isječak počinje.
- **Druga aplikacija je morala u to vrijeme snimati istu igru.** Oni koji označavaju vlastite retke igrača, pa mogu smjestiti istaknuti trenutak: CS2 i Dota 2 game-state integracija, Forza, Assetto Corsa igre, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive, Euro Truck Simulator 2, American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War Thunder, Minecraft i profili memorije (kao `me`); F1 23/24/25, RaceRoom, Automobilista 2 i Project CARS 2 (retci vašeg automobila nose `own_car` 1, po indeksu igračeva automobila igre, njegovu vlastitom mjestu ili promatranom sudioniku); Elite Dangerous (ime zapovjednika, u `meta.json` kao `player`, jer je dnevnik uvijek igračev).
- **Replay se pretvara nakon utakmice**, pa može smjestiti samo isječak koji se traži nakon pretvorbe: isječak se smješta kad se snimi, a replay spremljen kasnije ne gleda se ponovno. Replayi League of Legends imenuju svoje retke po Riot ID-u iz postavki i, uz Riot API ključ, dobivaju vrijeme sata iz vremenske crte utakmice, pa se tada nađu. Demo CS2 ne može smjestiti istaknuti trenutak uopće: njegove pozicije su u vlastitoj tablici pretvarača, a ne u `events.jsonl`, i demo ima ticke igre, ali nema vrijeme sata po kojem bi se trenutak isječka mogao uskladiti.
- U Rocket League jedini retci s mjestom su događaji s loptom. Vaš pogodak loptu je vaš redak, pa se istaknuti trenutak može smjestiti tamo gdje ste zadnji put udarili loptu.
- Igre bez ikakvog izvora pozicije (Overwatch 2, Call of Duty, Hunt: Showdown, ...) zadržavaju istaknute trenutke kao vremensku crtu trenutaka.

## Zašto memorija ne može dati poziciju u multiplayeru {#why-memory-cannot-give-a-position-in-multiplayer}

Drugi način da se dobije pozicija bio bi čitanje iz memorije. Nijedan ne radi:

- **NVIDIA-ina memorija nema poziciju.** NVIDIA aplikacija prima ono što GfeSDK nosi - ID istaknutog trenutka i dva vremenska pomaka - plus video koji snimi. Nigdje na NVIDIA-inoj strani nema pozicije koju bi se moglo pročitati. (Watcher svejedno ne čita NVIDIA-inu memoriju; čita gore navedene datoteke.)
- **Memorija igre je izvan dosega u multiplayeru.** Pozicija je u procesu igre, ali watcher nikad ne čita memoriju igre za više igrača: adapter memorije za igru označenu kao igra na mreži odbija se prije nego se išta otvori (vidi [Čitanje memorije](memory-reading.md)). Igre za više igrača rade pod anti-cheat sustavima (Easy Anti-Cheat, BattlEye, Vanguard, ...) koji smatraju da drugi program koji otvori proces igre znači varanje, što može dovesti do zabrane računa. Čitanje stanja igre izvana je i ono što uvjeti igara zabranjuju. Istaknuti trenutak u igri za više igrača zato dobiva mjesto samo iz onoga što igra objavljuje: njezine game-state integracije ili telemetrije, koju u isto vrijeme bilježi drugi adapter.
