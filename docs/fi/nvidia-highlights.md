---
title: NVIDIA Highlights
nav_order: 8
lang: "fi"
source: nvidia-highlights.md
source_hash: "a3b769ab065c"
nav_exclude: true
search_exclude: true
---
# NVIDIA Highlights {#nvidia-highlights}

Jotkin pelit pyytävät NVIDIA-näytönohjainta tallentamaan lyhyen videon, kun jotain tapahtuu, kuten tappo. Watcher merkitsee jokaisen näistä hetkistä ja, kun se pystyy, asettaa sen kartalle siihen kohtaan, missä se tapahtui.

`nvidia-highlights`-adapteri tallentaa klipit, kohokohdat ja kuvakaappaukset, jotka NVIDIA App (tai GeForce Experience) tallentaa, ja antaa jokaiselle paikan kartalla, kun se on mahdollista. Tämä sivu kertoo, mitä NVIDIA Highlights voi antaa ja mitä ei, mitä tiedostoja watcher lukee ja miten kohokohta saa sijainnin. Adapterin generoitu sivu on [NVIDIA highlights (alusta)](game-nvidia-highlights.md).

## Mitä NVIDIA Highlights voi antaa ja mitä ei {#what-nvidia-highlights-can-and-cannot-deliver}

Peli, joka tukee NVIDIA Highlightsia, puhuu NVIDIA Applle GfeSDK:n kautta. SDK kuljettaa vain kahdenlaisia viestejä:

1. **Kerran, käynnistyksessä**: kohokohtatyypit, joita peli käyttää: tunnus (kuten `kill`), merkitys, tagit ja näyttönimi kullakin kielellä. NVIDIA App tallentaa nämä pelikohtaisesti.
2. **Pelihetkellä**: "kohokohta `<id>`, `<ms>` nyt-hetkeä ennen ja `<ms>` sen jälkeen". Se on koko viesti: pelin rekisteröimän tyypin tunnus ja kaksi aikasiirtymää, joiden avulla NVIDIA App tietää, mikä osa sen jatkuvasta tallenteesta säilytetään.

SDK:ssa **ei ole kenttää millekään muulle**: ei sijaintia, ottelua tai kierrosta, vastustajaa, asetta, pistemäärää eikä mitään muuta omaa dataa. Peli ei voi laittaa kohokohtaan sijaintia, vaikka haluaisi. Kun klippi tallennetaan, NVIDIA App lisää tiedoston, pelin nimen, pituuden ja ajan.

Kohokohta voi siis kertoa vain: "tällainen hetki, tässä pelissä, tähän aikaan". Kaikki muu on haettava muualta.

## Mitä watcher lukee {#what-the-watcher-reads}

Kaikki luetaan tiedostoista, jotka NVIDIA App kirjoittaa omaa galleriaansa varten. Mitään ei lueta ajurilta tai sovellukselta. NVIDIA Overlay -kansio on `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| Tiedosto | Mitä siitä otetaan |
|---|---|
| `UGCTracker.json` | galleriaindeksi: jokainen klippi ja kuvakaappaus polkuineen, tyyppi (video, kuva), alatyyppi (`InstantReplay`, ...), päiväys, pelin profiilin nimi, suoritettava tiedosto ja lyhyt nimi sekä pituus (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, tallennuskansio, ja `settings.tempDirectory`, jossa kohokohdat odottavat (`<temp>\Highlights\<game>`), kunnes ne tallennetaan |
| `Highlights\<game>\config.json` | kohokohtatyypit, joita kukin peli on rekisteröinyt: tunnus ja englanninkielinen näyttönimi (tai tunnus, jos peli ei antanut nimeä) |
| tallennuskansio (oletus `%USERPROFILE%\Videos\NVIDIA`) ja `<temp>\Highlights` | itse klippi- ja kuvakaappaustiedostot (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), yksi kansio pelia kohden |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | GfeSDK-pelien lokittamat pyynnöt, rivit `Posted Request HL...`, joten pelin pyytämä kohokohta tallentuu, vaikka klippiä ei olisi säilytetty. Asetuspyynnöt (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) ohitetaan. |

Jokaisesta uudesta kohteesta adapteri kirjoittaa yhden rivin: `highlight` videolle, `screenshot` kuvalle tai `highlight_request` GfeSDK-lokin riville. Sen kentät:

| Kenttä | Mitä se on |
|---|---|
| `ms` | hetki: tiedostonimen aika (`<Game> 2026.05.01 - 20.31.28.115.DVR.mp4`, klipin tallennushetken paikallinen aika), muuten indeksin päiväys, muuten tiedoston muokkausaika |
| `game` | NVIDIA-profiilin nimi, kansion nimi tai tiedostonimen peli |
| `clip`, `media` | tiedoston polku; `video`, `image` tai `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (tilapäisestä kohokohtakansiosta) tai indeksin alatyyppi |
| `duration_s`, `clip_start_ms` | pituus indeksistä tai videon omasta otsikosta (`moov/mvhd`, luetaan ilman videon lukemista); hetki, jolloin klippi alkaa |
| `highlight_id`, `highlight_name` | kohokohtatyyppi, kun jokin sen nimeää (katso alla) |
| `exe` | pelin suoritettava tiedosto indeksistä |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | lainattu sijainti, kun sellainen löytyi (katso alla) |

Session tilastot ovat `clips`, `screenshots`, `clip_seconds` ja `placed` (kohteet, jotka saivat sijainnin).

**Kohokohdan tunnus** ei ole kirjattu mihinkään dokumentoituun paikkaan. Adapteri kokeilee kahta dokumentoimatonta tapaa: galleriamerkinnän kenttää, jonka nimessä on "highlight", ja, vain tilapäisen kohokohtakansion tiedostoille, yhtä pelin rekisteröidystä tunnuksesta (vähintään 4 merkkiä pitkä), joka esiintyy tiedostonimessä. Tallennettua klippiä nimetään pelin mukaan, ja sen nimessä voisi sattumalta olla tunnus kuten "kill", joten sen nimeä ei etsitä. Nämä kaksi tapaa eivät ole toimineet todellisella koneella: klippiä, jolla on kohokohdan tunnus, ja GfeSDK-pyyntörivia ei ole vielä nähty siellä, missä adapteria testattiin. Galleriaindeksi, asetukset, kohokohtien määritykset ja klipit on testattu oikeilla tiedostoilla.

### Milloin kohteet tallennetaan {#when-items-are-recorded}

- Klippiä kirjoitetaan vielä hetken näppäinpainalluksen jälkeen. Adapteri odottaa, kunnes tiedostolla on sama koko ja aika kahdella tarkastuksella (10 s välein), ja tiedoston on oltava vähintään 5 s vanha.
- Kun adapteri käynnistyy ensimmäisen kerran, kaikki galleriassa ja lokeissa jo oleva vain merkitään, ei tallenneta. Näin vuosien vanhat klipit eivät täytä tilastoja. Sen, minkä adapteri on nähnyt, säilyttää tiedosto `<data>\state\nvidia-highlights.json`, joten uudelleenkäynnistys ei tallenna mitään kahdesti.
- Kohteet ryhmitellään yhteen sessioon pelia kohden. Pelin sessio päättyy 30 minuutin kuluttua ilman uutta kohdetta, ja se päättyy viimeiseen hetkeensä eikä siihen, kun peli suljettiin. Hetket, jotka ovat yli 30 minuutin päässä toisistaan, menevät erillisiin sessioihin.

## Miten kohokohta saa sijainnin {#how-a-highlight-gets-a-position}

Kohokohdalla itsessään ei ole paikkaa. Adapteri etsii hetken muista tallenteista, jotka watcher on tehnyt samasta pelistä samaan aikaan:

1. **Sama peli**: session kansiot kohdassa `<data>\sessions\`, joiden pelin nimi vastaa kohokohdan pelin nimeä. Nimet verrataan pienillä kirjaimilla, ja vain kirjaimet ja numerot huomioidaan. Ne vastaavat, kun ne ovat samat, tai kun lyhyempi on vähintään 5 merkkiä pitkä ja sisältyy pidempään (`Counter-Strike 2` ja `Counter-Strike-2`).
2. **Sama aika**: sessiot, joiden alku ja loppu (tiedostosta `meta.json`, molemmissa päissä sekunnin varalla) kattavat hetken. Sessiot, jotka päättyivät ilman sijainteja, ja adapterin omat sessiot ohitetaan.
3. **Pelaajan oma rivi**: tiedostosta `events.jsonl` viimeisin pelaajan oma rivi, jolla on sijainti, ei myöhemmin kuin hetki ja enintään 5 s ennen sitä. Rivi on pelaajan oma, kun sen lähde sanoo niin: `"player": "me"`, tai `"own_car": 1` (kilpailupelit, jotka tallentavat jokaisen auton kuljettajansa mukaan), tai `player`, joka on session `player` tiedostossa `meta.json` (nimi, jonka lähde antaa pelaajalle). Katso [Pelaajan omat rivit](the-data.md#the-players-own-rows).

Jos rivi löytyy, kohokohdalle tulevat sen `x`, `y`, `z`, sen `session` (tai kansion nimi), `position_from` (kansio, josta se tuli) ja `position_lag_ms` (kuinka kauan ennen hetkeä rivi oli). Kohokohta-sessio ottaa sen tallenteen akselit, joten se piirtyy samalla tavalla. Jos riviä ei löydy, kohokohta jää ajanjanalle hetkenä ilman paikkaa.

Lainatusta sijainnista on hyvä tietää:

- **Se on missä olit, kun klippi tallennettiin**, ei missä toiminta alkoi. Hetki on tiedostonimen tallennusaika, joka Instant Replayn kohdalla on sen loppu. `clip_start_ms` kertoo, mistä klippi alkaa.
- **Toisen adapterin on täytynyt tallentaa sama peli samaan aikaan.** Ne, jotka merkitsevät pelaajan omat rivit ja voivat siis sijoittaa kohokohdan, ovat: Counter-Strike 2 ja Dota 2 game-state integration, Forza, Assetto Corsa -pelit, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive, Euro Truck Simulator 2, American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War Thunder, Minecraft ja muistiprofiilit (merkintä `me`); F1 23/24/25, RaceRoom, Automobilista 2 ja Project CARS 2 (omat autosi rivit saavat `own_car` 1:n pelin pelaajan autoindeksin, oman paikan tai katsotun osallistujan mukaan); Elite Dangerous (komentajan nimi tiedostossa `meta.json` kentässä `player`, koska päiväkirja on aina pelaajan oma).
- **Toisto muunnetaan ottelun jälkeen**, joten se voi sijoittaa vain klipin, jota haetaan muunnoksen jälkeen: klippi sijoitetaan, kun se tallennetaan, ja myöhemmin tallennettua toistoa ei katsota uudelleen. League of Legends -toistot nimeävät rivinsä Riot ID:llä asetuksissa, ja Riot API -avaimella ne antavat riveille seinäkellon ajan, jonka ottelun aikajana kertoo, joten ne löydetään silloin. CS2-demo ei voi sijoittaa kohokohtaa lainkaan: sen sijainnit ovat muuntimen omassa taulussa, eivätkä ne ole tiedostossa `events.jsonl`, ja demossa on pelin tikit mutta ei seinäkellon aikaa, johon klipin hetkeä verrattaisiin.
- Rocket Leaguessa ainoat rivit, joilla on paikka, ovat pallotapahtumat. Oman osumasi pallo on sinun rivisi, joten kohokohta voi sijoittua sinne, missä viimeksi osuit palloon.
- Pelit, joilla ei ole lainkaan paikkalähdettä (Overwatch 2, Call of Duty, Hunt: Showdown ja muut), säilyttävät kohokohtansa aikajanana hetkistä.

## Miksi muisti ei anna sijaintia moninpelissä {#why-memory-cannot-give-a-position-in-multiplayer}

Toinen tapa saada sijainti olisi lukea se muistista. Kumpikaan muisti ei toimi:

- **NVIDIAn muistissa ei ole sijaintia.** NVIDIA App saa sen, mitä GfeSDK kuljettaa: kohokohdan tunnuksen ja kaksi aikasiirtymää, sekä videon, jonka se tallentaa. NVIDIAn puolella ei ole mitään sijaintia, jonka voisi lukea. (Watcher ei lue NVIDIAn muistia joka tapauksessa; se lukee yllä mainitut tiedostot.)
- **Pelin muisti on moninpelissä koskematon.** Sijainti on pelin prosessissa, mutta watcher ei koskaan lue moninpelin muistia: verkkoon merkityn pelin muistisovitin hylätään ennen kuin mitään avataan (katso [Muistin lukeminen](memory-reading.md)). Moninpelit toimivat anti-cheat-järjestelmien alla (Easy Anti-Cheat, BattlEye, Vanguard ja muut), jotka pitävät toisen ohjelman avaamaa pelin prosessia huijauksena, mikä voi johtaa tilin bannaamiseen. Pelin tilan lukeminen ulkopuolelta on myös kielletty pelien käyttöehdoissa. Kohokohta moninpelissä saa siis paikan vain siitä, mitä peli julkaisee, eli sen game-state integration tai telemetria, jonka toinen adapteri tallentaa samaan aikaan.
