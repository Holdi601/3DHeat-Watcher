---
title: NVIDIA Highlights
nav_order: 8
lang: "hu"
source: nvidia-highlights.md
source_hash: "a3b769ab065c"
nav_exclude: true
search_exclude: true
---
# NVIDIA Highlights {#nvidia-highlights}

Egyes játékok megkérik az NVIDIA grafikus-illesztőprogramját, hogy mentsen egy rövid videót, amikor valami történik, például egy ölés. A watcher feljegyzi ezeket a pillanatokat, és ha tudja, a térképen is a helyükre teszi.

A `nvidia-highlights` adapter rögzíti azokat a klipeket, kiemeléseket és képernyőképeket, amelyeket az NVIDIA App (vagy a GeForce Experience) ment, és ha tud, helyet ad nekik a térképen. Ez az oldal leírja, mit tud és mit nem tud az NVIDIA Highlights, mely fájlokat olvassa a watcher, és hogyan kap egy kiemelés helyet. Az adapter generált oldala: [NVIDIA highlights (platform)](game-nvidia-highlights.md).

## Mit tud és mit nem tud az NVIDIA Highlights {#what-nvidia-highlights-can-and-cannot-deliver}

Egy NVIDIA Highlights-t támogató játék az NVIDIA App-pal a GfeSDK-n keresztül beszél. Az SDK csak kétféle üzenetet visz:

1. **Egyszer, az indításkor**: a kiemelés-fajták, amelyeket a játék használni fog – egy azonosító (például `kill`), egy fontosság, címkék, és egy megjelenítési név nyelvenként. Az NVIDIA App ezeket játékonként tárolja.
2. **Egy játékpillanatban**: "`<id>` kiemelés, `<ms>` ezredmásodperccel ezelőttről és `<ms>` utánig". Ez a teljes üzenet: egy, a játék által regisztrált fajta azonosítója, és két időeltolás, amely megmondja az NVIDIA App-nak, az állandóan futó felvétel melyik szakaszát tartsa meg.

Az SDK-ban **nincs mező semmi másra**: nincs pozíció, meccs vagy kör, nincs ellenfél, fegyver, pontszám, sem bármilyen egyedi adat. Egy játék akkor sem tud pozíciót tenni egy kiemelésbe, ha szeretne. Amikor a klip mentésre kerül, az NVIDIA App hozzáad egy fájlt, egy játéknevet, egy hosszt és egy időt.

Tehát egy kiemelés csak ennyit tud mondani: "ilyen fajta pillanat, ebben a játékban, ekkor". Minden többit máshonnan kell megkapni.

## Mit olvas a watcher {#what-the-watcher-reads}

Mindent olyan fájlokból olvas, amelyeket az NVIDIA App a saját galériájának ír. Semmi nem beszél az illesztőprogrammal vagy az alkalmazással. Az NVIDIA Overlay mappa a `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| Fájl | Amit kiolvas belőle |
|---|---|
| `UGCTracker.json` | a galéria-index: minden klip és képernyőkép az útvonalával, típusával (videó, kép), alfajtájával (`InstantReplay`, ...), dátumával, a játék profilnevével, végrehajtható fájljával és rövid nevével, valamint hosszával (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, a rögzítési mappa, és `settings.tempDirectory`, ahol a kiemelések várnak (`<temp>\Highlights\<game>`) a mentésig |
| `Highlights\<game>\config.json` | a játékok által regisztrált kiemelés-fajták: azonosító, és az angol megjelenítési név (vagy az azonosító, ha a játék nem adott nevet) |
| a rögzítési mappa (alapértelmezés `%USERPROFILE%\Videos\NVIDIA`) és `<temp>\Highlights` | maguk a klip- és képernyőkép-fájlok (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), játékonként egy mappában |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | a GfeSDK-t használó játékok kéréseinek naplója – a `Posted Request HL...` sorok –, így a játék által kért kiemelés akkor is rögzítődik, ha nem maradt meg klip. A konfigurációs kérések (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) kimaradnak. |

Minden új tételhez a watcher egy sort ír: `highlight` egy videóhoz, `screenshot` egy képhez, vagy `highlight_request` egy GfeSDK-naplósorhoz. A mezői:

| Mező | Mit jelent |
|---|---|
| `ms` | a pillanat: a fájlnévben lévő idő (`<Game> 2026.05.01 - 20.31.28.115.DVR.mp4`, a klip mentésének helyi ideje), különben az index dátuma, különben a fájl módosítási ideje |
| `game` | a NVIDIA-profil neve, a mappa neve vagy a fájlnév játéka |
| `clip`, `media` | a fájl elérési útja; `video`, `image` vagy `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (az ideiglenes kiemelés-mappából) vagy az index alfajtája |
| `duration_s`, `clip_start_ms` | a hossz, az indexből vagy a videó saját fejlécéből (`moov/mvhd`, a videó olvasása nélkül megtalálva); az a pillanat, ahol a klip kezdődik |
| `highlight_id`, `highlight_name` | a kiemelés-fajta, ha valami megnevezi (lásd lent) |
| `exe` | a játék végrehajtható fájlja, az indexből |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | a kölcsönzött pozíció, ha találtunk egyet (lásd lent) |

A munkamenet statisztikái: `clips`, `screenshots`, `clip_seconds` és `placed` (a helyet kapott tételek).

**A kiemelés azonosítója** nincs sehol dokumentált helyen. Az adapter két nem dokumentált helyet próbál: a galéria-bejegyzés egy mezőjét, amelynek nevében szerepel a "highlight", és – csak az ideiglenes kiemelések mappájában lévő fájlokra – a játék regisztrált azonosítóinak egyikét (legalább 4 karakter hosszú), amely előfordul a fájlnévben. Egy mentett klip a játék nevéről kapja a nevét, amelyben véletlenül lehet olyan azonosító, mint a "kill", ezért a nevét nem keressük. Ez a két mód egy valódi gépen még nem működött: nem volt olyan klip, amelynek kiemelés-azonosítója lett volna, és nem fordult elő GfeSDK-kérés-sor ott, ahol az adaptert tesztelték. A galéria-index, a beállítások, a kiemelés-definíciók és a klipek valódi fájlokon tesztelve vannak.

### Mikor kerülnek be a tételek {#when-items-are-recorded}

- Egy klip egy ideig még íródik a gombnyomás után. Az adapter addig vár, amíg egy fájl két ellenőrzéskor (10 másodpercenként) is azonos méretű és időbélyegű, és legalább 5 másodperces.
- Az adapter első futásakor a galériában és a naplókban lévő minden tételt csak feljegyzi, nem rögzíti, így az évek régi klipjei nem árasztják el a statisztikát. Amit látott, az a `<data>\state\nvidia-highlights.json` fájlban marad, így az újraindítás nem rögzít kétszer semmit.
- A tételek játékonként egy munkamenetbe kerülnek. Egy játék munkamenete 30 perc új tétel nélkül zárul, és az utolsó pillanatánál ér véget, nem akkor, amikor bezárult. A 30 percnél távolabbi pillanatok külön munkamenetbe kerülnek.

## Hogyan kap egy kiemelés helyet {#how-a-highlight-gets-a-position}

A kiemelésnek önmagában nincs helye. Az adapter a pillanatot a watcher ugyanarról a játékról, ugyanabban az időben készített más felvételeiben keresi:

1. **Ugyanaz a játék**: a `<data>\sessions\` alatti munkamenet-mappák, amelyek játéknevei egyeznek a kiemelésével. A neveket kisbetűsen, csak betűkkel és számjegyekkel hasonlítjuk össze. Egyeznek, ha egyenlők, vagy ha a rövidebb legalább 5 karakter, és benne van a hosszabban (`Counter-Strike 2` és `Counter-Strike-2`).
2. **Ugyanaz az idő**: azok a munkamenetek, amelyek kezdete és vége (a `meta.json`-ból, mindkét végén egy másodperces tűréssel) lefedi a pillanatot. A pozíció nélkül véget ért munkamenetek és az adapter saját munkamenetei kimaradnak.
3. **A játékos saját sora**: a `events.jsonl`-ben a játékos saját, pozícióval rendelkező sorai közül az utolsó, amely a pillanat előtt vagy ott van, és legfeljebb 5 másodperccel előbb. Egy sor akkor a játékos saját, ha a forrása azt mondja: `"player": "me"`, vagy `"own_car": 1` (a minden autót pilótájuk szerint rögzítő versenyjátékoknál), vagy egy `player`, amely a munkamenet `player` mezője a `meta.json`-ban (a név, amelyet a forrás a játékosnak ad). Lásd [A játékos saját sorai](the-data.md#the-players-own-rows).

Ha találunk sort, a kiemelés megkapja a `x`, `y`, `z` értékeit, a `session`-t (vagy a mappa nevét), a `position_from`-ot (a mappát, ahonnan jött) és a `position_lag_ms`-t (mennyivel volt a sor a pillanat előtt). A kiemelés-munkamenet azt a felvétel tengelyeit veszi át, így ugyanúgy van tájolva. Ha nincs ilyen sor, a kiemelés az idővonalon marad pillanatként, hely nélkül.

Amit a kölcsönzött pozícióról tudni kell:

- **Ott vagy, ahol a klip mentésekor voltál**, nem ott, ahol az akció kezdődött. A pillanat a fájlnévben lévő mentési idő, ami egy Instant Replay esetén a végét jelenti. A `clip_start_ms` mondja meg, mikor kezdődik a klip.
- **Egy másik adapternek ugyanabban az időben ugyanazt a játékot kellett rögzítenie.** Azok, amelyek a játékos saját soraival jelölnek, és így helyet tudnak adni egy kiemelésnek: a Counter-Strike 2 és a Dota 2 játékállapot-integrációja, a Forza, az Assetto Corsa játékok, az EA SPORTS WRC, a DiRT Rally 2.0, a Richard Burns Rally, a BeamNG.drive, az Euro Truck Simulator 2, az American Truck Simulator, a DCS World, az X-Plane, a Microsoft Flight Simulator, a War Thunder, a Minecraft és a memóriaprofilok (mint `me`); az F1 23/24/25, a RaceRoom, az Automobilista 2 és a Project CARS 2 (a saját autód sorai `own_car` 1-et kapnak, a játék játékos-autóindexe, a saját helye vagy a megfigyelt résztvevő alapján); az Elite Dangerous (a parancsnok neve, a `meta.json`-ban `player`-ként, mert a napló mindig a játékosé).
- **A visszajátszást a meccs után alakítjuk át**, ezért csak olyan klipet tud helyhez juttatni, amelyet az átalakítás után néznek meg: a klip akkor kap helyet, amikor rögzítik, és a később mentett visszajátszást nem nézzük újra. A League of Legends visszajátszásai a Riot-azonosítóddal nevezik meg a sorokat a beállításokban, és egy Riot API-kulccsal megadják nekik a meccs idővonalán közölt valós időt, így akkor találhatók meg. Egy CS2-demo nem tud helyet adni egy kiemelésnek: a pozíciói az átalakító saját táblázatában vannak, nem az `events.jsonl`-ben, és a demóban a játék tickjei vannak, de nincs valós idő, amellyel a klip pillanatát össze lehetne vetni.
- A Rocket League-ben csak a labdaesemények kapnak helyet. A labdaütésed a te sorod, így a kiemelés oda kerülhet, ahol utoljára megütötted a labdát.
- Azok a játékok, amelyeknek egyáltalán nincs pozíciós forrásuk (Overwatch 2, Call of Duty, Hunt: Showdown, ...), a kiemeléseiket pillanatok idővonalaként tartják meg.

## Miért nem adhat pozíciót a memória többjátékos játékban {#why-memory-cannot-give-a-position-in-multiplayer}

A másik mód egy pozíció megszerzésére az lenne, ha kiolvasnánk a memóriából. Egyik memória sem működik:

- **Az NVIDIA memóriájában nincs pozíció.** Az NVIDIA App azt kapja, amit a GfeSDK hordoz – egy kiemelés-azonosítót és két időeltolást –, valamint a rögzített videót. Az NVIDIA oldalán nincs semmi pozíció, amit ki lehetne olvasni. (A watcher amúgy sem olvas NVIDIA-memóriát; a fenti fájlokat olvassa.)
- **A játék memóriája többjátékos módban tilos.** A pozíció a játék folyamatában van, de a watcher soha nem olvas többjátékos játék memóriáját: az online játszottként jelölt játékhoz tartozó memória-adaptert semmi nem nyitja meg (lásd [Memória olvasása](memory-reading.md)). A többjátékos játékok anti-csalás rendszerek alatt futnak (Easy Anti-Cheat, BattlEye, Vanguard, ...), amelyek csalásnak tekintik, ha más program nyit meg a játék folyamatát, és ez a fiók tiltásához vezethet. A játék állapotának kívülről való olvasása a játékok feltételei szerint is tilos. Ezért egy többjátékos játékban egy kiemelés csak attól kap helyet, amit a játék maga közzétesz: a játékállapot-integrációjából vagy telemetriájából, amelyet egy másik adapter rögzít ugyanabban az időben.
