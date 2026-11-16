---
title: "NVIDIA Highlights"
nav_order: 8
lang: "ro"
source: nvidia-highlights.md
source_hash: "cd2a5cc2c5fd"
nav_exclude: true
search_exclude: true
---
# NVIDIA Highlights {#nvidia-highlights}

Unele jocuri cer driverului tău grafic NVIDIA să salveze un scurt video când se întâmplă ceva, cum ar fi o eliminare. Watcher-ul notează fiecare astfel de moment și, când poate, îl pune pe hartă, acolo unde s-a întâmplat.

Adaptorul `nvidia-highlights` înregistrează clipurile, highlight-urile și capturile de ecran pe care le salvează aplicația NVIDIA (sau GeForce Experience) și îi dă fiecăruia un loc pe hartă, când poate. Această pagină explică ce poate și ce nu poate livra NVIDIA Highlights, ce fișiere citește watcher-ul și cum primește un highlight o poziție. Pagina generată a adaptorului este [NVIDIA highlights (platformă)](game-nvidia-highlights.md).

## Ce poate și ce nu poate livra NVIDIA Highlights {#what-nvidia-highlights-can-and-cannot-deliver}

Un joc care suportă NVIDIA Highlights vorbește cu aplicația NVIDIA prin GfeSDK-ul NVIDIA. SDK-ul transportă doar două feluri de mesaje:

1. **O singură dată, la pornire**: tipurile de highlight pe care le va folosi jocul - un id (cum ar fi `kill`), o importanță, etichete și un nume afișat pentru fiecare limbă. Aplicația NVIDIA le ține pe joc.
2. **Într-un moment al jocului**: „highlight `<id>`, de la `<ms>` înainte de acum până la `<ms>` după”. Atât este tot mesajul: id-ul unui tip pe care jocul l-a înregistrat și două decalaje de timp, care îi spun aplicației NVIDIA ce porțiune din înregistrarea ei rulantă să păstreze.

SDK-ul **nu are niciun câmp pentru altceva**: nicio poziție, niciun meci sau rundă, niciun adversar, nicio armă, niciun scor, nicio dată personalizată. Un joc nu poate pune o poziție într-un highlight nici dacă ar vrea. Când clipul este salvat, aplicația NVIDIA adaugă un fișier, un nume de joc, o lungime și o oră.

Deci tot ce poate spune un highlight este „acest fel de moment, în acest joc, la această oră”. Orice altceva trebuie luat de altundeva.

## Ce citește watcher-ul {#what-the-watcher-reads}

Totul se citește din fișierele pe care aplicația NVIDIA le scrie pentru galeria ei. Nimic nu vorbește cu driverul sau cu aplicația. Folderul NVIDIA Overlay este `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| Fișier | Ce se ia din el |
|---|---|
| `UGCTracker.json` | indexul galeriei: fiecare clip și captură de ecran, cu calea, tipul (video, imagine), subtipul (`InstantReplay`, ...), data, numele de profil al jocului, executabilul și numele scurt, și lungimea (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, folderul de capturi, și `settings.tempDirectory`, unde așteaptă highlight-urile (`<temp>\Highlights\<game>`) până sunt salvate |
| `Highlights\<game>\config.json` | tipurile de highlight pe care le-a înregistrat fiecare joc: id-ul și numele afișat în engleză (sau id-ul, dacă jocul nu i-a dat unul) |
| folderul de capturi (implicit `%USERPROFILE%\Videos\NVIDIA`) și `<temp>\Highlights` | fișierele clipurilor și capturilor de ecran (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), câte un folder per joc |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | cererile pe care jocurile cu GfeSDK le scriu în jurnal - liniile `Posted Request HL...` - ca un highlight cerut de joc să fie înregistrat chiar și când niciun clip nu a fost păstrat. Cererile de configurare (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) sunt sărite. |

Pentru fiecare element nou, adaptorul scrie un rând: `highlight` pentru un video, `screenshot` pentru o imagine sau `highlight_request` pentru o linie din jurnalul GfeSDK. Câmpurile lui:

| Câmp | Ce este |
|---|---|
| `ms` | momentul: ora din numele fișierului (`<Game> 2026.05.01 - 20.31.28.115.DVR.mp4`, ora locală la care a fost salvat clipul), altfel data din index, altfel ora modificării fișierului |
| `game` | numele de profil NVIDIA, numele folderului sau numele jocului din numele fișierului |
| `clip`, `media` | calea fișierului; `video`, `image` sau `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (din folderul temporar de highlight-uri) sau subtipul din index |
| `duration_s`, `clip_start_ms` | lungimea, din index sau din antetul video al fișierului (`moov/mvhd`, găsit fără să citească videoclipul); momentul la care începe clipul |
| `highlight_id`, `highlight_name` | tipul de highlight, când ceva îl numește (vezi mai jos) |
| `exe` | executabilul jocului, din index |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | poziția împrumutată, când s-a găsit una (vezi mai jos) |

Statisticile sesiunii sunt `clips`, `screenshots`, `clip_seconds` și `placed` (elementele care au primit o poziție).

**Id-ul highlight-ului** nu este scris în niciun loc documentat. Adaptorul încearcă două moduri nedocumentate: un câmp al intrării din galerie al cărui nume conține „highlight” și - doar pentru fișierele din folderul temporar de highlight-uri - unul dintre id-urile înregistrate de joc (de cel puțin 4 caractere) care apare în numele fișierului. Un clip salvat este numit după joc, care ar putea conține din întâmplare un id ca „kill”, deci numele lui nu este căutat. Aceste două moduri nu au fost văzute încă funcționând pe un calculator real: niciun clip cu un id de highlight și nicio linie de cerere GfeSDK nu a apărut acolo unde a fost testat adaptorul. Indexul galeriei, setările, definițiile highlight-urilor și clipurile au fost testate pe fișiere reale.

### Când se înregistrează elementele {#when-items-are-recorded}

- Un clip mai este scris un timp după apăsarea tastei. Adaptorul așteaptă până când un fișier are aceeași dimensiune și aceeași oră la două verificări (la fiecare 10 s) și are cel puțin 5 s vechime.
- Prima dată când rulează adaptorul, tot ce este deja în galerie și în jurnale este doar notat, nu înregistrat, ca anii de clipuri vechi să nu inunde statisticile. Ce a văzut este păstrat în `<data>\state\nvidia-highlights.json`, deci o repornire nu înregistrează nimic de două ori.
- Elementele sunt grupate într-o sesiune per joc. Sesiunea unui joc se închide după 30 de minute fără un element nou și se termină la ultimul ei moment, nu când s-a închis jocul. Momentele mai depărtate de 30 de minute merg în sesiuni separate.

## Cum primește un highlight o poziție {#how-a-highlight-gets-a-position}

Highlight-ul în sine nu are un loc. Adaptorul caută momentul în celelalte înregistrări pe care le-a făcut watcher-ul din același joc, în același timp:

1. **Același joc**: folderele de sesiune din `<data>\sessions\` al căror nume de joc se potrivește cu al highlight-ului. Numele se compară cu litere mici, doar litere și cifre. Se potrivesc când sunt egale, sau când cel mai scurt are cel puțin 5 caractere și este conținut în cel mai lung (`Counter-Strike 2` și `Counter-Strike-2`).
2. **Același timp**: sesiunile al căror început și sfârșit (din `meta.json`, cu o secundă de rezervă la ambele capete) acoperă momentul. Sesiunile care s-au încheiat fără poziții și sesiunile proprii ale adaptorului sunt sărite.
3. **Rândul propriu al jucătorului**: în `events.jsonl` al lor, cel mai recent dintre rândurile jucătorului care au o poziție, la sau înainte de moment și nu cu mai mult de 5 secunde înainte. Un rând este al jucătorului când sursa lui o spune: `"player": "me"`, sau `"own_car": 1` (jocurile de curse care înregistrează fiecare mașină după pilotul ei), sau un `player` care este `player` al sesiunii din `meta.json` (numele pe care îl dă sursa jucătorului). Vezi [Rândurile proprii ale jucătorului](the-data.md#the-players-own-rows).

Dacă se găsește un rând, highlight-ul primește `x`, `y`, `z`, `session` (sau numele folderului), `position_from` (folderul de unde a venit) și `position_lag_ms` (cât timp înainte de moment era rândul acela). Sesiunea highlight-ului ia axele acelei înregistrări, deci este desenată în același fel. Dacă nu se găsește niciun rând, highlight-ul rămâne un moment pe cronologie, fără loc.

Lucruri de știut despre poziția împrumutată:

- **Este locul unde erai când a fost salvat clipul**, nu unde a început acțiunea. Momentul este ora salvării din numele fișierului, care pentru un Instant Replay este sfârșitul lui. `clip_start_ms` spune când începe clipul.
- **Un alt adaptor trebuie să fi înregistrat același joc în același timp.** Cele care marchează rândurile proprii ale jucătorului și deci pot plasa un highlight: integrarea stării jocului Counter-Strike 2 și Dota 2, Forza, jocurile Assetto Corsa, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive, Euro Truck Simulator 2, American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War Thunder, Minecraft și profilele de memorie (ca `me`); F1 23/24/25, RaceRoom, Automobilista 2 și Project CARS 2 (rândurile mașinii tale poartă `own_car` 1, după indexul mașinii jucătorului al jocului, slotul propriu sau participantul urmărit); Elite Dangerous (numele comandantului, în `meta.json` ca `player`, fiindcă jurnalul este mereu al jucătorului).
- **O reluare este convertită după meci**, deci poate plasa doar un clip care este căutat după conversie: clipul este plasat când este înregistrat, iar o reluare salvată mai târziu nu mai este privită din nou. Reluările League of Legends îți numesc rândurile după Riot ID-ul din setări și, cu o cheie de API Riot, le dau ora de ceas din cronologia meciului, deci sunt găsite atunci. Un demo CS2 nu poate plasa deloc un highlight: pozițiile lui sunt în tabelul propriu al convertorului, nu în `events.jsonl`, iar un demo are tick-urile jocului, dar nu o oră de ceas cu care să se potrivească momentul unui clip.
- În Rocket League singurele rânduri cu loc sunt evenimentele cu mingea. O lovitură a ta în minge este un rând al tău, deci un highlight poate fi plasat unde ai lovit ultima oară mingea.
- Jocurile fără nicio sursă poziționată (Overwatch 2, Call of Duty, Hunt: Showdown, ...) își păstrează highlight-urile ca o cronologie de momente.

## De ce memoria nu poate da o poziție în multiplayer {#why-memory-cannot-give-a-position-in-multiplayer}

Celălalt mod de a obține o poziție ar fi să o citești din memorie. Niciuna dintre memorii nu merge:

- **Memoria NVIDIA nu are nicio poziție în ea.** Aplicația NVIDIA primește ce transportă GfeSDK - un id de highlight și două decalaje de timp - plus video-ul pe care îl înregistrează. Nu există nicio poziție nicăieri de partea NVIDIA ca să fie citită. (Watcher-ul nu citește oricum memoria NVIDIA; citește fișierele de mai sus.)
- **Memoria jocului este interzisă în multiplayer.** Poziția este în procesul jocului, dar watcher-ul nu citește niciodată memoria unui joc multiplayer: un adaptor de memorie pentru un joc marcat ca jucat online este refuzat înainte să se deschidă ceva (vezi [Citirea memoriei](memory-reading.md)). Jocurile multiplayer rulează sub sisteme anti-cheat (Easy Anti-Cheat, BattlEye, Vanguard, ...) care tratează ca trișare ca un alt program să deschidă procesul jocului, ceea ce poate duce la suspendarea contului. Un highlight dintr-un joc multiplayer primește deci un loc doar din ce publică jocul: integrarea lui a stării jocului sau telemetria, înregistrate de alt adaptor în același timp.
