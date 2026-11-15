---
title: "NVIDIA Highlights"
nav_order: 8
lang: "sl"
source: nvidia-highlights.md
source_hash: "a3b769ab065c"
nav_exclude: true
search_exclude: true
---
# NVIDIA Highlights {#nvidia-highlights}

Nekatere igre prosijo vaš grafični gonilnik NVIDIA, naj shrani kratek video, ko se nekaj zgodi, na primer pobitje. Watcher si zabeleži vsak tak trenutek in ga, kadar je mogoče, postavi na zemljevid, kjer se je zgodil.

Adapter `nvidia-highlights` zapisuje posnetke, izpostavljene dele in posnetke zaslona, ki jih shrani aplikacija NVIDIA App (ali GeForce Experience), in vsakemu da mesto na zemljevidu, kadar je to mogoče. Ta stran pojasnjuje, kaj NVIDIA Highlights lahko in česa ne more dostaviti, katere datoteke watcher bere in kako izpostavljeni del dobi položaj. Generirana stran adapterja je [NVIDIA highlights (platform)](game-nvidia-highlights.md).

## Kaj NVIDIA Highlights lahko in česa ne more dostaviti {#what-nvidia-highlights-can-and-cannot-deliver}

Igra, ki podpira NVIDIA Highlights, se prek GfeSDK NVIDIA pogovarja z aplikacijo NVIDIA App. SDK prenaša samo dve vrsti sporočil:

1. **Enkrat, ob začetku**: vrste izpostavljenih delov, ki jih bo igra uporabljala - id (na primer `kill`), pomembnost, oznake in ime za prikaz v vsakem jeziku. NVIDIA App jih shrani za vsako igro.
2. **Ob trenutku igre**: "izpostavljeni del `<id>`, od `<ms>` pred zdaj do `<ms>` po zdaj". To je celotno sporočilo: id vrste, ki jo je igra prijavila, in dva časovna zamika, ki NVIDIA App povesta, kateri kos njenega krožnega snemanja naj ohrani.

SDK **nima polja za nič drugega**: ne za položaj, ne za tekmo ali krog, ne za nasprotnika, orožje, rezultat ali karkoli po meri. Igra tudi če bi hotela, ne more v izpostavljen del dati položaja. Ko se posnetek shrani, NVIDIA App doda datoteko, ime igre, dolžino in čas.

Torej lahko izpostavljen del pove samo "ta vrsta trenutka, v tej igri, ob tem času". Vse drugo mora priti od drugod.

## Kaj watcher bere {#what-the-watcher-reads}

Vse se bere iz datotek, ki jih NVIDIA App zapisuje za svojo galerijo. Ničesar ne pogovarja z gonilnikom ali aplikacijo. Mapa NVIDIA Overlay je `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| Datoteka | Kaj se iz nje vzame |
|---|---|
| `UGCTracker.json` | indeks galerije: vsak posnetek in posnetek zaslona s potjo, vrsto (video, slika), podvrsto (`InstantReplay`, ...), datumom, imenom profila igre, izvršljivo datoteko in kratkim imenom ter dolžino (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, mapa za zajem, in `settings.tempDirectory`, kjer izpostavljeni deli čakajo (`<temp>\Highlights\<game>`), dokler niso shranjeni |
| `Highlights\<game>\config.json` | vrste izpostavljenih delov, ki jih je vsaka igra prijavila: id in angleško ime za prikaz (ali id, kjer igra ni dala imena) |
| mapa za zajem (privzeto `%USERPROFILE%\Videos\NVIDIA`) in `<temp>\Highlights` | sami datoteke posnetkov in posnetkov zaslona (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), ena mapa za vsako igro |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | zahteve, ki jih zapisujejo igre z GfeSDK - vrstice `Posted Request HL...` - tako da je izpostavljen del, ki ga je igra zahtevala, zabeležen, tudi če posnetek ni bil shranjen. Konfiguracijske zahteve (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) se preskočijo. |

Za vsak nov predmet adapter zapiše eno vrstico: `highlight` za video, `screenshot` za sliko ali `highlight_request` za vrstico dnevnika GfeSDK. Njena polja:

| Polje | Kaj je |
|---|---|
| `ms` | trenutek: čas v imenu datoteke (`<Game> 2026.05.01 - 20.31.28.115.DVR.mp4`, lokalni čas shranitve posnetka), sicer datum iz indeksa, sicer čas spremembe datoteke |
| `game` | ime profila NVIDIA, ime mape ali ime igre iz imena datoteke |
| `clip`, `media` | pot do datoteke; `video`, `image` ali `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (iz začasne mape izpostavljenih delov) ali podvrsta iz indeksa |
| `duration_s`, `clip_start_ms` | dolžina, iz indeksa ali iz glave videa (`moov/mvhd`, najdena brez branja videa); trenutek, ko se posnetek začne |
| `highlight_id`, `highlight_name` | vrsta izpostavljenega dela, kadar jo kaj poimenuje (glej spodaj) |
| `exe` | izvršljiva datoteka igre, iz indeksa |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | izposojen položaj, kadar je bil najden (glej spodaj) |

Statistika seje so `clips`, `screenshots`, `clip_seconds` in `placed` (predmeti, ki so dobili položaj).

**Id izpostavljenega dela** ni zapisan na nobenem dokumentiranem mestu. Adapter poskusi dva nedokumentirana: polje vnosa galerije, katerega ime vsebuje "highlight", in - samo za datoteke v začasni mapi izpostavljenih delov - enega od prijavljenih id-jev igre (dolg vsaj 4 znake), ki se pojavi v imenu datoteke. Shranjen posnetek je poimenovan po igri, zato bi lahko vseboval id kot "kill" po naključju, zato se njegovo ime ne preiskuje. Ta dva načina na pravem računalniku še nista delovala: nobenega posnetka z id-jem izpostavljenega dela in nobene vrstice zahteve GfeSDK ni bilo tam, kjer je bil adapter preizkušen. Indeks galerije, nastavitve, opredelitve izpostavljenih delov in posnetki so bili preizkušeni na pravih datotekah.

### Kdaj se predmeti zapišejo {#when-items-are-recorded}

- Posnetek se še nekaj časa zapisuje po pritisku tipke. Adapter počaka, da ima datoteka dvakrat zapored isto velikost in čas (vsakih 10 s), in da je stara vsaj 5 s.
- Ob prvem zagonu adapterja se vse, kar je že v galeriji in dnevnikih, samo zabeleži, ne zapiše, da stara leta posnetkov ne napolnijo statistike. Kar je videl, shrani v `<data>\state\nvidia-highlights.json`, zato ponovni zagon ničesar ne zapiše dvakrat.
- Predmeti se združijo v eno sejo na igro. Seja igre se zapre po 30 minutah brez novega predmeta in konča ob svojem zadnjem trenutku, ne ob zaprtju. Trenutki, ki so več kot 30 minut narazen, gredo v ločene seje.

## Kako izpostavljen del dobi položaj {#how-a-highlight-gets-a-position}

Sam izpostavljen del nima mesta. Adapter poišče trenutek v drugih posnetkih, ki jih je watcher naredil iz iste igre ob istem času:

1. **Ista igra**: mape sej pod `<data>\sessions\`, katerih ime igre se ujema z igro izpostavljenega dela. Imena se primerjajo z malimi črkami, samo črke in številke. Ujemajo se, kadar sta enaka ali kadar ima krajše vsaj 5 znakov in je vsebovano v daljšem (`Counter-Strike 2` in `Counter-Strike-2`).
2. **Isti čas**: seje, katerih začetek in konec (iz `meta.json`, z eno sekundo rezerve na obeh straneh) pokrivata trenutek. Seje, ki so se končale brez položajev, in seje samega adapterja se preskočijo.
3. **Lastna vrstica igralca**: v njegovem `events.jsonl` zadnja od igralčevih lastnih vrstic s položajem, ob trenutku ali največ 5 sekund pred njim. Vrstica je igralčeva lastna, kadar tako pove njen vir: `"player": "me"`, ali `"own_car": 1` (dirkalne igre, ki zapisujejo vsak avto po imenu voznika), ali `player`, ki je `player` seje v `meta.json` (ime, ki ga vir da igralcu). Glej [Lastne vrstice igralca](the-data.md#the-players-own-rows).

Če je vrstica najdena, izpostavljen del dobi `x`, `y`, `z`, svojo `session` (ali ime mape), `position_from` (mapo, iz katere prihaja) in `position_lag_ms` (koliko pred trenutkom je bila ta vrstica). Seja izpostavljenega dela prevzame osi tega posnetka, zato se riše enako obrnjena. Če vrstica ni najdena, izpostavljen del ostane trenutek na časovnici brez mesta.

Stvari, ki jih je treba vedeti o izposojenem položaju:

- **Tam ste bili, ko je bil posnetek shranjen**, ne tam, kjer se je dejanje začelo. Trenutek je čas shranitve v imenu datoteke, ki je pri Instant Replay njegov konec. `clip_start_ms` pove, kdaj se posnetek začne.
- **Drug adapter mora med tem snemati isto igro.** Tisti, ki označijo lastne vrstice igralca in zato lahko postavijo izpostavljen del: Counter-Strike 2 in Dota 2 game-state integration, Forza, igre Assetto Corsa, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive, Euro Truck Simulator 2, American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War Thunder, Minecraft in profili pomnilnika (kot `me`); F1 23/24/25, RaceRoom, Automobilista 2 in Project CARS 2 (vrstice vašega avta imajo `own_car` 1, po indeksu igralčevega avta v igri, njegovi lastni reži ali gledanemu udeležencu); Elite Dangerous (ime poveljnika, v `meta.json` kot `player`, ker je dnevnik vedno igralčev).
- **Replay se pretvori po tekmi**, zato lahko postavi samo posnetek, ki je poiskan po pretvorbi: posnetek se postavi, ko je zapisan, shranjen replay pa se pozneje ne pregleda znova. Replayi League of Legends imenujejo vaše vrstice po Riot ID-ju v nastavitvah in, z lastnim ključem Riot API, dobijo čas po uri, ki ga navaja časovnica tekme, zato se takrat najdejo. Demo CS2 izpostavljenega dela sploh ne more postaviti: njegovi položaji so v lastni tabeli pretvornika, ne v `events.jsonl`, demo pa ima igrine takte, ne pa časa po uri, s katerim bi se trenutek posnetka lahko ujemal.
- V Rocket League so edine vrstice s krajem dogodki z žogo. Vaš zadetek žoge je vaša vrstica, zato se izpostavljen del lahko postavi tja, kjer ste nazadnje zadeli žogo.
- Igre brez kakršnega koli vira položajev (Overwatch 2, Call of Duty, Hunt: Showdown, ...) ohranijo svoje izpostavljene dele kot časovnico trenutkov.

## Zakaj pomnilnik v več igralcih ne more dati položaja {#why-memory-cannot-give-a-position-in-multiplayer}

Drug način, kako dobiti položaj, bi bil, da ga preberemo iz pomnilnika. Nobeden ne deluje:

- **Pomnilnik NVIDIA nima položaja.** NVIDIA App prejme, kar prenaša GfeSDK - id izpostavljenega dela in dva časovna zamika - plus video, ki ga posname. Na strani NVIDIA ni nikjer položaja, ki bi ga lahko prebrali. (Watcher tako ali tako ne bere pomnilnika NVIDIA; bere zgoraj naštete datoteke.)
- **Pomnilnik igre je v več igralcih nedotakljiv.** Položaj je v procesu igre, watcher pa pomnilnika igre za več igralcev nikoli ne bere: adapter pomnilnika za igro, označeno kot igrano na spletu, se zavrne, preden se kaj odpre (glej [Branje pomnilnika](memory-reading.md)). Igre z več igralci tečejo pod zaščito proti goljufanju (Easy Anti-Cheat, BattlEye, Vanguard, ...), ki štejejo, da drug program, ki odpre proces igre, pomeni goljufanje, kar lahko račun pripelje do prepovedi. Branje stanja igre od zunaj pa prepovedujejo tudi pogoji iger. Izpostavljen del v igri z več igralci zato dobi mesto samo iz tega, kar igra objavi: njene game-state integration ali telemetrije, ki jo ob istem času zapiše drug adapter.
