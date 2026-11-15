---
title: "NVIDIA highlights (platforma)"
nav_order: 34
lang: "hr"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA highlights (platforma) {#nvidia-highlights-platform}

Watcher sprema ono što NVIDIA highlights čuva o vašim igrama, pa svoju povijest kasnije možete pogledati na karti u 3DHeat pregledniku.

*Tehnički detalji: adapter `nvidia-highlights`, vrsta [`platform`](sources-and-rules.md); radi cijelo vrijeme (ne čeka da se igra pokrene) i traži nove podatke svakih 10 s.*

## Što se bilježi {#what-is-recorded}

- svaki novi isječak, highlight ili snimka ekrana: igra, datoteka, vrsta, trajanje i trenutak (vrijeme sata u ms)
- ID i naziv highlighta kad ga je igra prijavila NVIDIA-i
- gdje je igrač bio u tom trenutku, kad je drugi adapter tada bilježio istu igru
- zahtjevi za highlight iz igara s GfeSDK-om, čak i kad se nijedan isječak ne čuva

## Odakle dolazi {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;game>\config.json; isječci u mapi za snimanje (%USERPROFILE%\Videos\NVIDIA\\&lt;Game>\\\*.mp4) i &lt;temp>\Highlights\\&lt;game>; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## Kako to uključiti {#how-to-switch-it-on}

NVIDIA App: uključeni Instant Replay ili Highlights, isječci spremljeni tipkom ili od same igre

## Kako radi {#how-it-works}

Što pokretač i upravljački program grafike čuvaju o igranju: Steamova statistika, postignuća, vrijeme igranja i vremenske crte, te NVIDIA-ini highlighti i isječci.

Nijedan od ovih izvora ne traži da igra surađuje niti da radi, pa su tri adaptera ovdje uvijek uključena i pregledavaju nekoliko datoteka svakih nekoliko sekundi.

#### NVIDIA highlighti i isječci (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Što čuva NVIDIA App / GeForce Experience, sve pod `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
```text
UGCTracker.json      indeks galerije: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, kad je datoteka napisana), profileName, drsName
                     (izvršna datoteka), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (gdje se isječci spremaju),
                     settings.tempDirectory (highlighti čekaju u
                     <temp>\Highlights\<game> dok se ne spreme)
Highlights\<game>\config.json  vrste highlighta koje je igra prijavila:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: text}}}, profileName, drsName, shortName}
```
i same datoteke isječaka, `<capture folder>\<Game>\<Game> yyyy.mm.dd -
hh.mm.ss.ff.DVR.mp4` (snimke ekrana: `<Game> Screenshot yyyy.mm.dd - ...png`), a vrijeme u imenu je lokalno vrijeme kad je isječak spremljen. Igre s GfeSDK-om bilježe i svoje pozive za highlight u `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

Što ovo može a što ne može donijeti: igra koja podržava NVIDIA Highlights (GfeSDK) prijavljuje vrste highlighta jednom - ID kao "kill", značaj, oznake, prikazni naziv - a kasnije kaže samo "highlight <id>, from <ms> before now to <ms> after". Nema pozicija, nema utakmice ni runde, nema protivnika, nema prilagođenih podataka: SDK nema polje ni za jedno od toga. Spremljen isječak dodaje samo datoteku, naziv igre, trajanje i vrijeme. Dakle bilježi se „ova vrsta trenutka, u ovoj igri, u ovo vrijeme“ - a mjesto samo tako da se vrijeme potraži u zapisu drugog adaptera za istu igru (`position_at`), što ovaj adapter radi za svaki isječak koji zabilježi.
<https://developer.nvidia.com/highlights>

Svaki adapter pamti što je već vidio u `<data>\state\<id>.json`, pa ponovno pokretanje ne bilježi ništa dvaput.

Svaka sesija čuva i odakle su njezini redci došli, cijelo (pravilo pretvarača 3DHeat, docs/converters.md u repozitoriju preglednika), u `heat.raw.parquet`: bajtovi datoteke statistike i njezine sheme te blok localconfig igre (steam-stats; datoteku statistike koju dekoder ne može pročitati dobije sesija koja sadrži samo njezine bajtove), zaglavlje datoteke vremenske crte i svaki unos kao JSON (steam-timeline), svaki unos indeksa galerije za isječak, definicije highlighta igre i svaki redak GfeSDK dnevnika, i one koji nisu zahtjevi za highlight (nvidia-highlights).

Isti modul služi i: [Steam statistika (platforma)](game-steam-stats.md), [Steam Timeline (platforma)](game-steam-timeline.md).

## Pozicije i osi {#positions-and-axes}

| | |
|---|---|
| Bilježe se pozicije | samo posuđene: mjesto koje drugo snimanje iste igre ima za taj trenutak |
| Os prema gore | `y` |
| Jedinice | metri |
| Zrcaljeno za preglednik | nema |
| Mjerilo jedinice (`scale`: preglednik ovim množi pozicije) | 1 |

Ovo ide u `meta.json` (`axes`) svake sesije i, kad sesija ima pozicije, u podnožje `heat.parquet`, pa 3DHeat preglednik sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igranje na mreži (`multiplayer`): **ne**. `games --markdown` to prikazuje kao "single-player".
- Vrsta `platform`: čita samo ono što igra ili platforma daje (ono što Steam ili upravljački program grafike čuva), pa bilježi i u igri na mreži i izvan nje; zastavica odlučuje samo smije li se ikad čitati memorija.
- Memorija: adapter je **nikad** ne čita. Memoriju čitaju samo adapteri vrste `memory`, i nikad za igru označenu kao igranu na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` u `meta.json` svake sesije i tablica `stats` u `watcher.sqlite`):

`clip_seconds`, `clips`, `placed`, `screenshots`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz imena statistike same igre nisu na ovom popisu; odjeljak „Što se bilježi“ ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeata: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je postalo i retkom), a `selfCheck.completeness` u `meta.json`-u broji svaki `type` - `lost` je 0.

**Čita se**

- svaki novi isječak i snimka ekrana: igra, datoteka, vrsta, medij, trajanje (indeks, inače zaglavlje MP4), trenutak iz imena datoteke, ID i naziv highlighta gdje ih je igra prijavila, i igračevo mjesto tada iz zapisa drugog adaptera
- zahtjevi za GfeSDK highlight (svaki `Posted Request HL...`, osim poziva za konfiguraciju) s njihovim vremenom

**Čuva se sirovo**

- `UGC`: cijeli unos isječka iz indeksa galerije UGCTracker.json, svako polje koje NVIDIA piše
- `clip_file`: za isječak koji indeks ne navodi, putanja datoteke, veličina, vrijeme i mapa
- `highlights_config`: `Highlights\<game>\config.json` igre kako je napisan (značaj, oznake, nazivi na svakom jeziku), jednom po sesiji
- `gfesdk_log`: svaki redak GfeSDK dnevnika pročitan nakon prvog pokretanja, `used` istinit za zahtjeve za highlight i lažan za ostalo (konfiguracija, postavke videa, vlastite poruke SDK-a)

**Nije dostupno**

- sami isječci i snimke ekrana: video i slike ostaju gdje ih je NVIDIA spremila; retci imenuju datoteku
- što je bilo prije prvog pokretanja adaptera: uzima se kao već viđeno, pa godine isječaka ne postanu odjednom sesije (`baseline`; False ih bilježi)
- `apps` i `info` iz UGCTracker.json-a i GallerySettings.json: postavke aplikacije, ne trenuci igranja; koristi se mapa za snimanje koju navode
- pozicije, runde, protivnici: GfeSDK za njih nema polja

**Veličina**: oko 1 KB po isječku i nekoliko KB definicija i redaka dnevnika po pokretanju igre: dalje od 1 MB po satu

## Provjereno {#verified}

testirano na pravom indeksu galerije, postavkama, definicijama highlighta i isječcima iz lokalne instalacije; redci zahtjeva GfeSDK highlighta i ID-jevi highlighta u isječcima nisu testirani

## Izvor {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
