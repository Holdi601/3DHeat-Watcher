---
title: "NVIDIA Highlights"
nav_order: 8
lang: "sq"
source: nvidia-highlights.md
source_hash: "cd2a5cc2c5fd"
nav_exclude: true
search_exclude: true
---
# NVIDIA Highlights {#nvidia-highlights}

Disa lojëra i kërkojnë drejtuesit grafik NVIDIA të ruajë një video të shkurtër kur ndodh diçka, si një vrasje.
Watcher-i shënon secilin nga ato momente dhe, kur mundet, e vendos në hartë aty ku ndodhi.

Adapteri `nvidia-highlights` regjistron klipet, momentet e spikatura dhe pamjet e ekranit që ruan NVIDIA App (ose
GeForce Experience), dhe i jep secilit një vend në hartë kur mundet. Kjo faqe shpjegon çfarë mund të japë
NVIDIA Highlights dhe çfarë jo, cilët skedarë i lexon watcher-i, dhe si merr një moment të spikatur një
pozicion. Faqja e gjeneruar e adapterit është [NVIDIA highlights (platformë)](game-nvidia-highlights.md).

## Çfarë mund të japë NVIDIA Highlights dhe çfarë jo {#what-nvidia-highlights-can-and-cannot-deliver}

Një lojë që mbështet NVIDIA Highlights flet me NVIDIA App përmes GfeSDK të NVIDIA. SDK-ja
bart vetëm dy lloje mesazhesh:

1. **Një herë, në fillim**: llojet e momenteve të spikatura që do të përdorë loja - një id (si `kill`), një
   rëndësi, etiketa dhe një emër për çdo gjuhë. NVIDIA App i ruan këto për çdo lojë.
2. **Në një moment loje**: "momenti i spikatur `<id>`, nga `<ms>` para tani deri `<ms>` pas". Ky është
   i gjithë mesazhi: id-ja e një lloji që loja e regjistroi, dhe dy zhvendosje kohe që i tregojnë NVIDIA App
   cilën pjesë të regjistrimit të vet rrotullues ta mbajë.

SDK-ja **nuk ka fushë për asgjë tjetër**: as pozicion, as ndeshje ose raund, as kundërshtar, as armë, as
pikë, as të dhëna të personalizuara të ndonjë lloji. Një lojë nuk mund të vërë një pozicion në një moment të spikatur edhe sikur të donte.
Kur klipi ruhet, NVIDIA App shton një skedar, një emër loje, një gjatësi dhe një kohë.

Pra gjithçka që mund të thotë një moment i spikatur është "ky lloj momenti, në këtë lojë, në këtë kohë". Çdo gjë më shumë
duhet të vijë nga diku tjetër.

## Çfarë lexon watcher-i {#what-the-watcher-reads}

Gjithçka lexohet nga skedarë që NVIDIA App i shkruan për galerinë e vet. Asgjë nuk flet me
drejtuesin ose aplikacionin. Dosja NVIDIA Overlay është
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| Skedari | Çfarë merret prej tij |
|---|---|
| `UGCTracker.json` | indeksi i galerisë: çdo klip dhe pamje ekrani me rrugën, llojin (video, image), nënllojin (`InstantReplay`, ...), datën, emrin e profilit të lojës, ekzekutuesen dhe emrin e shkurtër, dhe gjatësinë (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, dosja e kapjes, dhe `settings.tempDirectory`, ku momentet e spikatura presin (`<temp>\Highlights\<game>`) derisa të ruhen |
| `Highlights\<game>\config.json` | llojet e momenteve të spikatura që regjistroi çdo lojë: id, dhe emri i shfaqur anglisht (ose id-ja kur loja nuk dha asnjë) |
| dosja e kapjes (parazgjedhja `%USERPROFILE%\Videos\NVIDIA`) dhe `<temp>\Highlights` | vetë skedarët e klipeve dhe pamjeve të ekranit (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), një dosje për lojë |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | kërkesat që logojnë lojërat me GfeSDK - rreshtat `Posted Request HL...` - ndaj një moment i spikatur që kërkoi loja regjistrohet edhe kur nuk u mbajt asnjë klip. Kërkesat e konfigurimit (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) anashkalohen. |

Për çdo send të ri adapteri shkruan një rresht: `highlight` për një video, `screenshot` për një imazh, ose
`highlight_request` për një rresht të ditarit GfeSDK. Fushat e tij:

| Fusha | Çfarë është |
|---|---|
| `ms` | momenti: ora në emrin e skedarit (`<Game> 2026.05.01 - 20.31.28.115.DVR.mp4`, ora vendore kur u ruajt klipi), përndryshe data e indeksit, përndryshe koha e ndryshimit të skedarit |
| `game` | emri i profilit NVIDIA, emri i dosjes ose loja e emrit të skedarit |
| `clip`, `media` | rruga e skedarit; `video`, `image` ose `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (nga dosja e përkohshme e momenteve të spikatura) ose nënlloji i indeksit |
| `duration_s`, `clip_start_ms` | gjatësia, nga indeksi ose nga header-i i vetë videos (`moov/mvhd`, gjetur pa lexuar videon); momenti kur fillon klipi |
| `highlight_id`, `highlight_name` | lloji i momentit të spikatur, kur diçka e emërton (shih më poshtë) |
| `exe` | ekzekutuesja e lojës, nga indeksi |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | pozicioni i huazuar, kur u gjet një (shih më poshtë) |

Statistikat e seancës janë `clips`, `screenshots`, `clip_seconds` dhe `placed` (sendet që morën një
pozicion).

**Id-ja e momentit të spikatur** nuk shkruhet në asnjë vend të dokumentuar. Adapteri provon dy të padokumentuara:
një fushë e hyrjes së galerisë emri i së cilës përmban "highlight", dhe - vetëm për skedarët në dosjen e
përkohshme të momenteve të spikatura - një nga id-të e regjistruara të lojës (të paktën 4 shkronja të gjata) që
shfaqet në emrin e skedarit. Një klip i ruajtur emërtohet sipas lojës, që mund të përmbajë një id si "kill"
rastësisht, ndaj emri i tij nuk kërkohet. Këto dy mënyra nuk janë parë ende të funksionojnë në një makinë të vërtetë:
asnjë klip me id momenti të spikatur, dhe asnjë rresht kërkese GfeSDK, nuk ka ndodhur aty ku u provua adapteri.
Indeksi i galerisë, cilësimet, përkufizimet e momenteve të spikatura dhe klipet u provuan me skedarë të vërtetë.

### Kur regjistrohen sendet {#when-items-are-recorded}

- Një klip shkruhet ende për njëfarë kohe pas shtypjes së tastit. Adapteri pret derisa një skedar të ketë
  të njëjtën madhësi dhe kohë në dy shikime (çdo 10 s) dhe të jetë të paktën 5 s i vjetër.
- Herën e parë që ekzekutohet adapteri, gjithçka që është tashmë në galeri dhe në ditarë vetëm shënohet, nuk
  regjistrohet, që vite klipesh të vjetra të mos e përmbytin statistikën. Çfarë ka parë ruhet në
  `<data>\state\nvidia-highlights.json`, kështu që një rinisje nuk regjistron asgjë dy herë.
- Sendet grupohen në një seancë për lojë. Seanca e një loje mbyllet pas 30 minutash pa send të ri, dhe
  mbaron në momentin e saj të fundit, jo kur u mbyll. Momentet më shumë se 30 minuta larg njëri-tjetrit
  shkojnë në seanca të veçanta.

## Si merr një moment i spikatur një pozicion {#how-a-highlight-gets-a-position}

Vetë momenti i spikatur nuk ka vend. Adapteri e kërkon momentin në regjistrimet e tjera që
watcher-i bëri për të njëjtën lojë në të njëjtën kohë:

1. **E njëjta lojë**: dosjet e seancave nën `<data>\sessions\` emri i lojës së të cilave përputhet me atë të
   momentit të spikatur. Emrat krahasohen me shkronja të vogla, vetëm shkronja dhe shifra. Përputhen kur janë
   të barabartë, ose kur më i shkurtri ka të paktën 5 shkronja dhe përmbahet në më të gjatin
   (`Counter-Strike 2` dhe `Counter-Strike-2`).
2. **E njëjta kohë**: seancat fillimi dhe mbarimi i të cilave (nga `meta.json`, me një sekondë lëvizshmëri në të dy
   skajet) e mbulojnë momentin. Seancat që mbaruan pa pozicione, dhe seancat e vetë adapterit, anashkalohen.
3. **Rreshti i vetë lojtarit**: në `events.jsonl` të tyre, më i fundit nga rreshtat e vetë lojtarit me një
   pozicion, në ose para momentit dhe jo më shumë se 5 sekonda para tij. Një rresht është i vetë lojtarit
   kur burimi i tij e thotë: `"player": "me"`, ose `"own_car": 1` (lojërat e garave që regjistrojnë çdo makinë sipas
   shoferit të saj), ose një `player` që është `player` i seancës në `meta.json` (emri që burimi i jep
   lojtarit). Shih [Rreshtat e vetë lojtarit](the-data.md#the-players-own-rows).

Nëse gjendet një rresht, momenti i spikatur merr `x`, `y`, `z`, `session` (ose emrin e dosjes),
`position_from` (dosja nga erdhi) dhe `position_lag_ms` (sa para momentit ishte ai rresht).
Seanca e momentit të spikatur merr boshtet e atij regjistrimi, ndaj vizatohet në të njëjtën mënyrë. Nëse nuk gjendet asnjë rresht,
momenti i spikatur mbetet një moment në afatkohë pa vend.

Çfarë duhet ditur për pozicionin e huazuar:

- **Është aty ku ishe kur u ruajt klipi**, jo ku filloi veprimi. Momenti është koha e
  ruajtjes në emrin e skedarit, që për një Instant Replay është fundi i tij. `clip_start_ms` tregon kur
  fillon klipi.
- **Një adapter tjetër duhet të ketë regjistruar të njëjtën lojë në atë kohë.** Ata që shënojnë
  rreshtat e vetë lojtarit, dhe pra mund të vendosin një moment të spikatur: integrimi i gjendjes së lojës i Counter-Strike 2 dhe Dota 2,
  Forza, lojërat Assetto Corsa, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive,
  Euro Truck Simulator 2, American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War
  Thunder, Minecraft dhe profilet e memories (si `me`); F1 23/24/25, RaceRoom, Automobilista 2 dhe Project
  CARS 2 (rreshtat e makinës sate mbajnë `own_car` 1, sipas indeksit të makinës së lojtarit të lojës, vendit të vet ose
  pjesëmarrësit të shikuar); Elite Dangerous (emri i komandantit, në `meta.json` si `player`, pasi ditari është
  gjithmonë i lojtarit).
- **Një riluajtje konvertohet pas ndeshjes**, ndaj mund të vendosë vetëm një klip që kërkohet pas
  konvertimit: klipi vendoset kur regjistrohet, dhe një riluajtje e ruajtur më vonë nuk shikohet përsëri.
  Riluajtjet e League of Legends i emërtojnë rreshtat e tu sipas Riot ID në cilësime dhe, me një çelës Riot API, u japin
  orën e murit që thotë afatkohëzimi i ndeshjes, ndaj gjenden atëherë. Një demo CS2 nuk mund të vendosë një
  moment të spikatur fare: pozicionet e saj janë në tabelën e vetë konvertuesit, jo në `events.jsonl`, dhe një demo
  ka tick-et e lojës por jo orë muri për të krahasuar momentin e një klipi.
- Në Rocket League rreshtat e vetme me vend janë ngjarjet e topit. Një goditje e topit nga ti është një rresht yti, ndaj
  një moment i spikatur mund të vendoset aty ku e godite topin së fundi.
- Lojërat pa asnjë burim pozicioni (Overwatch 2, Call of Duty, Hunt: Showdown, ...) i mbajnë
  momentet e spikatura si afatkohë momentesh.

## Pse memoria nuk mund të japë pozicion në lojë me shumë lojtarë {#why-memory-cannot-give-a-position-in-multiplayer}

Mënyra tjetër për të marrë një pozicion do të ishte leximi i tij nga memoria. Asnjëra memorie nuk funksionon:

- **Memoria e NVIDIA nuk ka pozicion.** NVIDIA App merr çfarë bart GfeSDK - një id
  momenti të spikatur dhe dy zhvendosje kohe - plus videon që regjistron. Nuk ka pozicion askund në anën e
  NVIDIA për t'u lexuar. (Watcher-i nuk e lexon memorien e NVIDIA gjithsesi; lexon skedarët më sipër.)
- **Memoria e lojës është e ndaluar në lojë me shumë lojtarë.** Pozicioni është në procesin e lojës, por
  watcher-i nuk e lexon kurrë memorien e një loje me shumë lojtarë: një adapter memorieje për një lojë të shënuar si e luajtur online
  refuzohet para se të hapet çfarëdo (shih [Leximi i memories](memory-reading.md)). Lojërat me shumë lojtarë punojnë
  nën anti-cheat (Easy Anti-Cheat, BattlEye, Vanguard, ...) që e trajtojnë hapjen e procesit të lojës nga një program tjetër
  si mashtrim, gjë që mund të bëjë të ndalohet llogaria. Prandaj një moment i spikatur në një lojë me shumë lojtarë merr vend vetëm
  nga çfarë publikon loja: integrimi i gjendjes së lojës ose telemetria, e regjistruar nga një adapter tjetër në
  të njëjtën kohë.
