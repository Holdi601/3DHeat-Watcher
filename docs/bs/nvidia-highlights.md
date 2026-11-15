---
title: "NVIDIA Highlights"
nav_order: 8
lang: "bs"
source: nvidia-highlights.md
source_hash: "a3b769ab065c"
nav_exclude: true
search_exclude: true
---
# NVIDIA Highlights {#nvidia-highlights}

Neke igre traže od vašeg NVIDIA grafičkog drivera da spremi kratak video kad se nešto desi, na primjer ubistvo.
Watcher bilježi svaki takav trenutak i, kad može, stavlja ga na mapu tamo gdje se desio.

Adapter `nvidia-highlights` snima klipove, highlighte i screenshotove koje sprema NVIDIA App (ili
GeForce Experience) i, kad može, svakom daje mjesto na mapi. Ova stranica objašnjava šta
NVIDIA Highlights može isporučiti, a šta ne, koje datoteke watcher čita i kako highlight
dobiva poziciju. Generirana stranica adaptera je [NVIDIA highlights (platforma)](game-nvidia-highlights.md).

## Šta NVIDIA Highlights može i ne može isporučiti {#what-nvidia-highlights-can-and-cannot-deliver}

Igra koja podržava NVIDIA Highlights razgovara s NVIDIA App-om preko NVIDIA-inog GfeSDK-a. SDK
nosi samo dvije vrste poruka:

1. **Jednom, na početku**: vrste highlighta koje će igra koristiti - id (kao `kill`),
   važnost, oznake i prikazano ime za svaki jezik. NVIDIA App ih sprema po igri.
2. **U trenutku igre**: "highlight `<id>`, od `<ms>` prije sada do `<ms>` poslije". To je
   cijela poruka: id vrste koju je igra registrirala i dva vremenska pomaka koja govore NVIDIA App-u
   koji dio svog kontinuiranog snimka da zadrži.

SDK **nema polje ni za šta drugo**: nema pozicije, meča ni runde, protivnika, oružja,
rezultata, niti ikakvih prilagođenih podataka. Igra ne može staviti poziciju u highlight čak ni kad bi htjela.
Kad se klip spremi, NVIDIA App dodaje datoteku, ime igre, dužinu i vrijeme.

Sve što highlight može reći jeste "ova vrsta trenutka, u ovoj igri, u ovo vrijeme". Sve ostalo mora
doći odnekud drugdje.

## Šta watcher čita {#what-the-watcher-reads}

Sve se čita iz datoteka koje NVIDIA App piše za svoju galeriju. Ništa ne razgovara s
driverom ni s aplikacijom. Folder NVIDIA Overlay je
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| Datoteka | Šta se iz nje uzima |
|---|---|
| `UGCTracker.json` | indeks galerije: svaki klip i screenshot s putanjom, tipom (video, image), podtipom (`InstantReplay`, ...), datumom, imenom profila igre, izvršnom datotekom i kratkim imenom, te dužinom (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, folder snimanja, i `settings.tempDirectory`, gdje highlighti čekaju (`<temp>\Highlights\<game>`) dok se ne spreme |
| `Highlights\<game>\config.json` | vrste highlighta koje je svaka igra registrirala: id i englesko prikazano ime (ili id gdje igra nije dala ime) |
| folder snimanja (zadano `%USERPROFILE%\Videos\NVIDIA`) i `<temp>\Highlights` | same datoteke klipova i screenshotova (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), jedan folder po igri |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | zahtjevi koje GfeSDK igre bilježe - linije `Posted Request HL...` - pa se highlight koji je igra tražila bilježi čak i kad nijedan klip nije zadržan. Zahtjevi za konfiguraciju (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) se preskaču. |

Za svaku novu stavku adapter piše jedan red: `highlight` za video, `screenshot` za sliku, ili
`highlight_request` za liniju GfeSDK loga. Njegova polja:

| Polje | Šta je to |
|---|---|
| `ms` | trenutak: vrijeme u imenu datoteke (`<Game> 2026.05.01 - 20.31.28.115.DVR.mp4`, lokalno vrijeme kad je klip spremljen), inače datum iz indeksa, inače vrijeme izmjene datoteke |
| `game` | ime NVIDIA profila, ime foldera ili igra iz imena datoteke |
| `clip`, `media` | putanja datoteke; `video`, `image` ili `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (iz privremenog foldera highlighta) ili podtip iz indeksa |
| `duration_s`, `clip_start_ms` | dužina, iz indeksa ili iz vlastitog zaglavlja videa (`moov/mvhd`, nađeno bez čitanja videa); trenutak kad klip počinje |
| `highlight_id`, `highlight_name` | vrsta highlighta, kad je nešto imenuje (vidite dolje) |
| `exe` | izvršna datoteka igre, iz indeksa |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | posuđena pozicija, kad je nađena (vidite dolje) |

Statistike sesije su `clips`, `screenshots`, `clip_seconds` i `placed` (stavke koje su dobile
poziciju).

**Id highlighta** nije upisan ni na jednom dokumentiranom mjestu. Adapter probava dva nedokumentirana:
polje stavke galerije čije ime sadrži "highlight", i - samo za datoteke u privremenom folderu
highlighta - jedan od registriranih id-ova igre (dug najmanje 4 znaka) koji
se pojavljuje u imenu datoteke. Spremljeni klip se zove po igri, što bi slučajno moglo sadržavati id poput "kill",
pa se njegovo ime ne pretražuje. Ova dva načina još nisu viđena kako rade na pravom računaru:
nijedan klip s id-om highlighta i nijedna linija GfeSDK zahtjeva nisu se pojavili tamo gdje je adapter
testiran. Indeks galerije, postavke, definicije highlighta i klipovi testirani su na pravim datotekama.

### Kad se stavke bilježe {#when-items-are-recorded}

- Klip se još neko vrijeme piše poslije pritiska tastera. Adapter čeka dok datoteka nema
  istu veličinu i vrijeme pri dva pogleda (svakih 10 s) i dok nije stara najmanje 5 s.
- Pri prvom pokretanju adaptera sve što je već u galeriji i logovima samo se zabilježi, ne
  snima, pa godine starih klipova ne preplave statistiku. Ono što je viđeno čuva se u
  `<data>\state\nvidia-highlights.json`, pa ponovno pokretanje ništa ne snimi dvaput.
- Stavke se grupiraju u jednu sesiju po igri. Sesija igre se zatvara nakon 30 minuta bez nove
  stavke i završava u svom zadnjem trenutku, a ne kad se igra zatvorila. Trenuci udaljeni više od 30 minuta idu
  u odvojene sesije.

## Kako highlight dobiva poziciju {#how-a-highlight-gets-a-position}

Sam highlight nema mjesto. Adapter traži trenutak u drugim snimcima koje je
watcher napravio iste igre u isto vrijeme:

1. **Ista igra**: folderi sesija u `<data>\sessions\` čije se ime igre poklapa s
   imenom igre highlighta. Imena se porede malim slovima, samo slova i cifre. Poklapaju se kad su
   jednaka, ili kad kraće ima najmanje 5 znakova i sadržano je u dužem
   (`Counter-Strike 2` i `Counter-Strike-2`).
2. **Isto vrijeme**: sesije čiji početak i kraj (iz `meta.json`, sa sekundom tolerancije na oba
   kraja) pokrivaju trenutak. Sesije koje su završile bez pozicija i vlastite sesije adaptera
   se preskaču.
3. **Igračev vlastiti red**: u njihovom `events.jsonl`, zadnji od igračevih vlastitih redova s
   pozicijom, u trenutku ili prije njega, ne više od 5 sekundi prije. Red je igračev vlastiti
   kad to kaže njegov izvor: `"player": "me"`, ili `"own_car": 1` (trkaće igre koje snimaju svaki automobil po
   vozaču), ili `player` koji je `player` sesije u `meta.json` (ime koje izvor daje
   igraču). Vidite [Igračevi vlastiti redovi](the-data.md#the-players-own-rows).

Ako se red nađe, highlight dobiva njegove `x`, `y`, `z`, svoj `session` (ili ime foldera),
`position_from` (folder iz kojeg je došao) i `position_lag_ms` (koliko prije trenutka je taj red
bio). Sesija highlighta preuzima ose tog snimka, pa se crta isto okrenuta. Ako nijedan red
nije nađen, highlight ostaje trenutak na vremenskoj liniji bez mjesta.

Šta treba znati o posuđenoj poziciji:

- **To je mjesto gdje ste bili kad je klip spremljen**, a ne gdje je akcija počela. Trenutak je
  vrijeme spremanja u imenu datoteke, što je kod Instant Replaya njegov kraj. `clip_start_ms` kaže kad
  klip počinje.
- **Neki drugi adapter je morao snimati istu igru u to vrijeme.** Oni koji označavaju
  igračeve vlastite redove, pa mogu smjestiti highlight: Counter-Strike 2 i Dota 2 game-state integracija,
  Forza, igre Assetto Corsa, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive,
  Euro Truck Simulator 2, American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War
  Thunder, Minecraft i profili memorije (kao `me`); F1 23/24/25, RaceRoom, Automobilista 2 i Project
  CARS 2 (redovi vašeg automobila nose `own_car` 1, prema indeksu igračevog automobila u igri, vlastitom slotu ili gledanom
  učesniku); Elite Dangerous (ime komandanta, u `meta.json` kao `player`, jer je dnevnik
  uvijek igračev).
- **Snimak se pretvara poslije meča**, pa može smjestiti samo klip koji se traži poslije
  pretvorbe: klip se smješta kad je snimljen, a snimak spremljen poslije se ne gleda ponovo.
  Snimci League of Legends imenuju vaše redove po Riot ID-u iz postavki i, uz Riot API ključ, daju
  im vrijeme zida koje navodi vremenska linija meča, pa se tada nalaze. CS2 demo uopće ne može smjestiti
  highlight: njegove pozicije su u vlastitoj tabeli konvertera, a ne u `events.jsonl`, a demo
  ima tickove igre, ali ne i vrijeme zida s kojim bi se poklopio trenutak klipa.
- U Rocket Leagueu jedini redovi s mjestom su događaji lopte. Vaš udarac lopte je vaš red,
  pa se highlight može smjestiti tamo gdje ste zadnji put udarili loptu.
- Igre bez ikakvog pozicijskog izvora (Overwatch 2, Call of Duty, Hunt: Showdown, ...) zadržavaju svoje
  highlighte kao vremensku liniju trenutaka.

## Zašto memorija ne može dati poziciju u multiplayeru {#why-memory-cannot-give-a-position-in-multiplayer}

Drugi način da se dobije pozicija bio bi čitanje iz memorije. Nijedna memorija ne dolazi u obzir:

- **U NVIDIA-inoj memoriji nema pozicije.** NVIDIA App prima ono što GfeSDK nosi - id
  highlighta i dva vremenska pomaka - plus video koji snima. Nigdje na NVIDIA-inoj strani nema
  pozicije za čitanje. (Watcher ionako ne čita NVIDIA-inu memoriju; čita datoteke gore.)
- **Memorija igre je zabranjena u multiplayeru.** Pozicija je u procesu igre, ali
  watcher nikad ne čita memoriju multiplayer igre: memory adapter za igru označenu kao igranu online
  odbija se prije nego što se išta otvori (vidite [Čitanje memorije](memory-reading.md)). Multiplayer igre rade
  pod anti-cheatima (Easy Anti-Cheat, BattlEye, Vanguard, ...) koji otvaranje procesa igre od strane drugog programa
  smatraju varanjem, zbog čega račun može dobiti ban. Čitanje stanja igre izvana
  je također ono što uvjeti igara zabranjuju. Highlight u multiplayer igri zato dobiva mjesto samo
  iz onoga što igra objavljuje: njene game-state integracije ili telemetrije, koju u isto vrijeme
  snima neki drugi adapter.
