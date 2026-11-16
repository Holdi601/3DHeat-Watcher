---
title: "Dota 2 (Replays)"
nav_order: 12
lang: "de"
source: game-dota-replays.md
source_hash: "c0ed25c261f6"
nav_exclude: true
search_exclude: true
---
# Dota 2 (Replays) {#dota-2-replays}

Nach einem Match von Dota 2 macht der Watcher aus dem Replay, das das Spiel gespeichert hat, Dateien, die du auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `dota-replays`, Art [`replay`](sources-and-rules.md); er läuft ständig (er wartet nicht auf den Start eines Spiels) und sucht alle 5 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- Position, Höhe, Leben und Stufe jedes Helden, 7,5 Mal pro Sekunde, solange er lebt
- Kills und Tode dort, wo sie passierten; Türme, Kasernen, Roshan und Tormentors dort, wo sie fielen; Wards dort, wo sie gesetzt wurden
- Map-Pings, Kartenzeichnungen und Befehle (bewegen, angreifen, zaubern, kaufen, ...) jedes Spielers dort, wohin sie zeigten
- der Punktestand und die Zeile jedes Spielers; die des angemeldeten Spielers als Statistiken
- alles andere, was das Replay enthält, ganz neben der Tabelle behalten: jeder Frame und jede Netzwerknachricht, jede Änderung einer Entitätseigenschaft, jeder Eintrag der Stringtabelle

## Woher es kommt {#where-it-comes-from}

Replays, die Dota 2 speichert: &lt;Dota>/game/dota/replays/&lt;match id>.dem (im Client heruntergeladen oder mit `dota-replay <match id>`)

## So schaltest du es ein {#how-to-switch-it-on}

Lade das Replay eines Matches in Dota 2 herunter oder hole ein öffentliches: `python -m heat3d_watch dota-replay <match id>`; installiere den Leser: github.com/Holdi601/3DHeat-Ext-DotaReplay (`heat3d-dota-replay`, bringt gem-dota mit)

Gib den Befehl in einem Terminal ein, das im Ordner des Watchers geöffnet ist (siehe [Vor dem Start](before-you-start.md)). Wenn er fehlschlägt, sagt die letzte Zeile, warum; [Installation und Start](installing-and-running.md) beschreibt die üblichen Ursachen.

Einstellungen aus Umgebungsvariablen:

- `HEAT3D_DOTA_REPLAY`: der Ordner des Lesers (ein Klon oder entpacktes Release), wenn er nicht installiert ist oder nicht neben dem Watcher liegt

## Wie es funktioniert {#how-it-works}

Replays und Demos: was ein Spiel von einem Match speichert, wird umgewandelt, sobald das Match vorbei ist.

Ein Replay enthält alles, was eine Live-Oberfläche in Mehrspielerspielen zurückhält - die Position jedes Spielers, jeden Kill dort, wo er passierte -, und es ist eine Datei, die das Spiel für seine Spieler schreibt; das Lesen berührt deshalb nichts im Spiel. Der Watcher schaut in die Ordner, in die Spiele sie speichern, wartet, bis eine neue Datei nicht mehr wächst (sonst schreibt das Spiel noch), und wandelt sie in einem Arbeits-Thread um, damit eine lange Umwandlung nie den Rest des Watchers aufhält.

Das erste Mal, wenn ein Ordner gesehen wird, werden die Replays darin nur vermerkt, nicht umgewandelt: Ein Spieler mit jahrelangen Demos würde sonst feststellen, dass der Watcher einen Tag lang beschäftigt ist. `python -m heat3d_watch replays <adapter> [folder]` wandelt die vorhandenen auf Wunsch um.

#### Dota 2 {#dota-2}

Dota 2 speichert die Replays, die ein Spieler herunterlädt (die Details eines Matches oder Watch > Replays), unter `<Dota>/game/dota/replays/<match id>.dem`; Valve hält das Replay jedes öffentlichen Matches einige Wochen auf seinen Servern vor, und `python -m heat3d_watch dota-replay <match id>` holt eines anhand seiner ID über OpenDota. Den Watcher lesen sie nicht selbst: Das tut ein externer Leser (3DHeat Dota Replay, github.com/Holdi601/3DHeat-Ext-DotaReplay, `exporters/ext/dota-replay`, Befehl `heat3d-dota-replay`, liest über gem-dota, MIT). Er ist getrennt gehalten, damit ein Problem mit ihm nichts anderes berührt, und wird für jedes neue Replay in einem eigenen Prozess gestartet, wenn er im PATH steht, installiert ist oder neben dem Watcher liegt; fehlt er, sagt der Watcher einmal, wie man ihn installiert. Er schreibt Position, Höhe, Leben, Stufe, Blickrichtung, Mana, Erfahrung, Attribute und Gegenstände jedes Helden 7,5 Mal pro Sekunde, solange er lebt; Kills und Tode dort, wo sie passierten; Türme, Kasernen, Roshan und Tormentors dort, wo sie fielen; jeden Ward dort, wo er gesetzt und wo er beendet wurde; die Einträge des Kampflogs über die Helden (Schaden, Heilung, Fähigkeiten, Gegenstände, Käufe, Runen, Gold, Erfahrung, Modifikatoren); und jeden Map-Ping, jede Kartenzeichnung und jeden Befehl jedes Spielers - in `dota/<match>.parquet`; jede andere Einheit (Creeps, Beschwörungen, Illusionen, Kuriere, Gebäude) einmal pro Sekunde in `<match>.units.parquet`; das ganze Kampflog in `<match>.combatlog.parquet`; und das Match, den Chat, den Draft, alles andere, was der Parser herauszieht, und den Spielbericht des Spiels am Matchende in `<match>.match.json`, im Session-Ordner. Alles andere, was das Replay enthält, wird ganz daneben behalten (Konverterregel von 3DHeat): jeder Frame und jede Netzwerknachricht in `<match>.packets.parquet`, jede Änderung einer Entitätseigenschaft in `<match>.entities.parquet`, jeder Eintrag der Stringtabelle in `<match>.strings.parquet`, gezählt in `selfCheck.completeness` des Match-Dokuments. Positionen sind Dotas Welteinheiten, dieselben, die die Game-State-Integration meldet. Die Scoreboard-Zeile des angemeldeten Spielers wird zur Statistik der Session: Kills, Tode, Assists, letzte Treffer, Denies, Nettowert, GPM, XPM, Heldenschaden, Wards und ob das Match gewonnen wurde. Ein neuer Dota-Patch kann die Entitäten des Replays ändern, bevor gem folgt; ein Replay, das gem nicht bis zum Ende lesen kann, wird so weit umgewandelt, wie es geht, und in seiner Zusammenfassung als `incomplete` markiert.

Dasselbe Modul bedient außerdem: [Counter-Strike 2 (Replays)](game-cs2-demos.md), [Squad (Replays)](game-squad-demos.md), [War Thunder (Replays)](game-warthunder-replays.md), [World of Tanks (Replays)](game-wot-replays.md), [World of Warships (Replays)](game-wows-replays.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | ja |
| Oben-Achse | `z` |
| Einheiten | Dota-Welteinheiten (Hammer-Einheiten; die Karte ist etwa 16400 breit) |
| Für den Viewer gespiegelt | `y` |
| Einheitenfaktor (`scale`: der Viewer multipliziert Positionen damit) | 1 |

Diese landen in der `meta.json` jeder Session (`axes`) und, wenn die Session Positionen hat, im Footer von `heat.parquet`, damit der 3DHeat-Viewer die Zeilen selbst dreht und skaliert - siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt das als "erlaubt (liest nur, was das Spiel veröffentlicht)".
- Art `replay`: Er liest nur, was das Spiel oder die Plattform herausgibt (Replays und Demos, die das Spiel speichert), deshalb zeichnet er auch im Online-Spiel auf wie offline; die Markierung entscheidet nur, ob Speicher jemals gelesen werden darf.
- Speicher: **nie** von diesem Adapter gelesen. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist - siehe [Quellen und Regeln](sources-and-rules.md).

## Erfasste Statistiken {#statistics-recorded}

Statistik-Schlüssel, die der Code dieses Adapters namentlich setzt (das `stats` jeder Session in `meta.json` und die Tabelle `stats` in `watcher.sqlite`):

`duration`, `hero`, `score.{team}`, `team`, `won`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; "Was aufgezeichnet wird" oben nennt sie.

## Vollständigkeit {#completeness}

Der Konverter folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was das Replay enthält, wird gelesen oder behalten, nie weggelassen. Neben der Tabelle wird alles andere, was das Replay enthält, ganz in Beiblättern daneben im Ordner `dota/` der Session behalten - `<match>.packets.parquet`, `<match>.entities.parquet`, `<match>.strings.parquet` (Spalten `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, je nachdem, was zutrifft) - und `selfCheck.completeness` des Match-Dokuments (`<match>.match.json`) zählt jeden `type` - `lost` ist 0.

**Gelesen**

- die Tabelle (`dota/<match>.parquet`): Position, Höhe, Leben, Stufe, Blickrichtung, Mana, Erfahrung, Attribute, Rüstung, Geschwindigkeit, Schaden, Gegenstände und der Cursor des Spielers, 7,5 Mal pro Sekunde; Kills, Tode, Ziele, Wards, die Einträge des Kampflogs über Helden; Map-Pings (`ping`, DOTA_UM_LocationPing), Kartenzeichnungen (`map_line`, DOTA_UM_MapLine) und jeder Einheitenbefehl (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` der Befehlstyp, `value` die Fähigkeits- oder Gegenstands-ID, `text` die Klasse des Ziels; am befohlenen Punkt, sonst beim Helden)
- `<match>.units.parquet`: jede andere Einheit einmal pro Sekunde; `<match>.combatlog.parquet`: das ganze Kampflog, so wie gem es liest, jedes Feld
- das Match-Dokument: alles, was gem herauszieht, und ganz die eigenen Datensätze des Replays - `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: Abspiellänge, jeder Spielername, Held, Steam-ID, Team), `matchDetails` (DOTA_UM_MatchDetails: das Spielprotokoll des Game Coordinators am Matchende, jede Spielerzahl, Gegenstände, Schaden nach Art, Picks und Bans) und `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: Kills, Tode, Assists, Stufe, letzte Treffer und Denies, wie aus dem Strom gelesen, gegen `matchDetails`, pro Spieler

**Roh behalten**

- `<match>.packets.parquet`: jeder Frame, der kein Paket ist (`type` `frame <n>`), und jede Netzwerknachricht (`message <n>`, `name` Valves), vollständig in `payload`, in Dateireihenfolge (`seq`, `frame`), mit `decoded` dem Protobuf als JSON (ein Bytefeld als seine Länge angegeben); jede Nachrichtenart wird dekodiert: svc_PacketEntities (der Entitätenstrom), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, die Kampflog-Nachrichten, GE_SosStartSoundEvent, DOTA_UM_TE_\* (Projektile, Animationen, Blut), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; die Sendetabellen, die Klassenliste und die Serverinformationen, die ein späterer Entitäten-Decoder braucht, sind darunter
- `<match>.entities.parquet`: jede Eigenschaft jeder Entität jedes Mal, wenn sie sich ändert (`type` die Eigenschaft, `name` die Klasse, `entity` ihr Index; `value`, `vector` oder `decoded`), ihr ganzer Zustand beim Erzeugen und jedes Erzeugen, Eintreten, Verlassen und Löschen - Millionen Zeilen für ein ganzes Match
- `<match>.strings.parquet`: jeder Eintrag der Stringtabelle aus jedem Update und jedem vollständigen Abbild, der Wert ganz; `userinfo`, `ActiveModifiers` und `EconItems` aus ihren Protobufs dekodiert
- `selfCheck.completeness` im Match-Dokument zählt Frames und Nachrichten nach Valves Namen, Kampflog-Einträge (`combatlog <type>`), Spielereignisse (`gameevent <name>`), Stringtabellen-Einträge (`stringtable <name>`) und Entitätenupdates (`entity <class>`); einige werden nur roh behalten (vollständige Entitäts-Abbilder, die gem überspringt, weil es aus den Deltas neu aufbaut, und Einträge von Tabellen, deren Werte nichts liest), lost 0

**Nicht verfügbar**

- Sprache: das Replay hat die Sprachkonfiguration, aber keine Sprachdaten
- Namen hinter Hashes und IDs: Sounds und Partikel sind nach Hashes der Spieldateien benannt, Fähigkeiten nach IDs; das Replay trägt die Namen nicht (Gegenstände werden über gems Katalog benannt, wo er sie hat)
- alles, was nur die Clients der Spieler wussten (ihre Kamera, ihr Bildschirm), über das hinaus, was der Server übertrug; der Cursor und jeder Befehl sind enthalten

**Größe**: die Beiblätter zusammen sind etwas größer als das Replay selbst, die Pakete und die Entitäten am größten; ein ganzes Match braucht ein bis zwei Minuten in einem Prozess

## Geprüft {#verified}

an einem öffentlichen Match-Replay geprüft: Kills, Tode, Assists, Stufe, letzte Treffer und Denies stimmen für alle zehn Spieler mit dem Spielbericht des Matchendes überein; jede Nachricht im Paket-Beiblatt wird Byte für Byte neu serialisiert; die Tabelle und die Statistiken durch Tests mit synthetischen Daten

## Quelle {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
