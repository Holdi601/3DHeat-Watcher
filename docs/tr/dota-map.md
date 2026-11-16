---
title: "Dota 2 haritası"
nav_order: 6.5
lang: "tr"
source: dota-map.md
source_hash: "6c7a1c39d1bf"
nav_exclude: true
search_exclude: true
---
# Dota 2 haritası, bir seviye olarak (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

Dota 2 haritası 3B olarak - zemin, uçurumlar, su, her ağaç ve binalar, [Dota 2 replay tablolarının](game-dota-replays.md) çizildiği çerçevede ve birimlerde - kendi aracı **3DHeat Dota** tarafından üretilir ([3DHeat-Ext-Dota](https://github.com/Holdi601/3DHeat-Ext-Dota), [belgeler](https://holdi601.github.io/3DHeat-Ext-Dota/)). Watcher'ın dışında, kendi başına bir projedir.

Bir kez kurun; aracın [Başlamadan önce](https://holdi601.github.io/3DHeat-Ext-Dota/before-you-start.html) sayfasında anlatıldığı gibi (bir Python paketi, artı Source2Viewer'ın komut satırı), sonra şunlardan birini çalıştırın

```bash
heat3d-dota-maps level -o dota.glb
```

ya da watcher üzerinden

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

ki bu, `heat3d-dota-maps level` komutunu aynı seçeneklerle çalıştırır ve çıktısını ile çıkış durumunu olduğu gibi geçirir. Watcher aracı, `PATH` üzerindeki `heat3d-dota-maps` komutu olarak, kurulu `heat3d_ext_dota` paketi olarak, ya da `HEAT3D_DOTA_MAPS` içinde ya da watcher'ın yanında (bir 3DHeat kopyasında `exporters/ext/dota-maps`) kaynak klasörü olarak bulur. Hiçbir parçası watcher'a aktarılmaz; yalnızca çalıştırılır. Araç hiçbir yerde yoksa `dota-map` nereden alınacağını yazar ve çıkış kodu 2 ile çıkar.

`.glb` dosyasını, bir Dota tablosunun altında görüntüleyicinin **Arka plan / seviye** paneline (**3B model…**) yükleyin: görüntüleyici dosyayı parçalarından tanır, seviye kütüphanesinde tutar ve bundan sonra **Dota 2 haritası** düğmesi onu yükler. Seviyenin nasıl üretildiği, parçaları ve nasıl denetlendiği: [Seviye oluşturma](https://holdi601.github.io/3DHeat-Ext-Dota/level.html).
