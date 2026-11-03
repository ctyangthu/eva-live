# 長榮航空航班動態系統

依長榮航空 2026/27 冬季（NW26）國際線班表，在世界地圖上推算每一個航班的位置，並提供出發／抵達看板、時刻表與航線網路。從桃園、松山、高雄出發，共 51 個國際航點、55 條航線、177 個航段，每週自臺灣出發 541 班。

## 功能

- **依日期套用班表**：每個航段記錄行駛星期（例如維也納 BR65 為週三、五、日），各機場時區與日光節約時間由瀏覽器換算，所以同一班機在不同日期的臺北時間會跟著變。德里航線 2026/12/1 首航、上海浦東 BR752/751 自 11/6 起每週五，也依日期判斷。
- **即時與模擬**：預設使用現在時間；可切換日期、拖曳時間軸（臺北時間），並以 1×–3600× 播放。前一兩天起飛、仍在空中的長程航班會繼續顯示。
- **地圖**：Miller 投影、以東經 143° 為中心，倫敦到紐約一張圖看完。航線依大圓繪製並以區域上色，飛機沿大圓航線移動、機頭朝行進方向；陰影為當下的夜間區域。可拖曳縮放，並有全航網、亞太、東北亞、東南亞、歐洲、北美等範圍；圖例可逐一顯示或隱藏各區域。
- **航班詳情**：起降時間（當地與臺北時間）、飛行進度、推算地速與高度、已飛與剩餘距離、行駛星期；經停曼谷的 BR61/62、BR67/68、BR75/76 會列出兩個航段。
- **出發／抵達看板**：依桃園、松山、高雄篩選本日航班，狀態依時刻表推算（預定、即將起飛、已起飛、飛行中、即將抵達、已抵達）。
- **空中**：目前在空中的航班，分為從臺灣出發與飛往臺灣，依剩餘時間排序。
- **時刻表**：依航點分組，可依區域、航班號或城市搜尋，標示本日不飛與正在飛行的航段。
- **航點**：各區域航點、每週班次與最短飛行時間；點選航點會在地圖上標出航線並帶出時刻表。

## 限制

- 航班狀態與位置依表定時間推算（扣除約 14 分鐘滑行出發、6 分鐘滑行抵達，沿大圓航線移動），不含延誤、取消、改降等即時資訊；實際航路會因空域與風向繞行，兩岸航線尤其明顯。
- 同一航班常輪替機型，班表記錄的是 2026/11/2–12/1 期間執飛天數最多的機型。
- 高雄—上海浦東（BR706/705，每週 5 班）與松山—上海虹橋（BR772/771，每週 6 班）的行駛星期未公開，只列入時刻表與航線圖，不列入每日動態。
- 班表適用 2026/10/25–2027/3/27；超出期間的日期仍以本班表推算並提示。美國 2027/3/14 起改夏令時間，該段期間北美航班的推算時刻可能有一小時誤差。
- 本系統為非官方展示，與長榮航空無關，實際航班請以長榮航空公告為準。

## 專案結構

```
src/app.html                網頁原始碼（資料以佔位字串嵌入）
data/schedule-nw26.txt      班表：每行一個航段（航班、起訖、當地時間、星期、機型）
data/airports.json          54 個機場：中英文名稱、區域、座標、IANA 時區
data/map.json               投影並簡化後的陸地、國界與臺灣路徑
tools/schedule.py           解析 schedule-nw26.txt
tools/check_schedule.py     以時區換算飛行時間，檢查 +1/+2 與時刻是否合理
tools/build_map.py          由 Natural Earth 1:50m（world-atlas）產生 data/map.json
tools/build.py              組出 dist/index.html
```

## 建置

```bash
python3 tools/build.py
```

產出的 `dist/index.html` 可直接用瀏覽器開啟。推送到 `main` 後，GitHub Actions 會自動建置並部署到 GitHub Pages。

修改班表後先檢查再建置：

```bash
python3 tools/check_schedule.py
```

```bash
python3 tools/build.py
```

重新產生地圖時，先下載 [land-50m.json](https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/land-50m.json) 與 [countries-50m.json](https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-50m.json)，再執行：

```bash
python3 tools/build_map.py land-50m.json countries-50m.json
```

## 資料來源

- 班表：[AeroLOPA](https://www.aerolopa.com/routes/br/boeing-777-300er) 長榮航空 777-300ER、787-9、787-10、A330-300 航線（2026/11/2–12/1）與各航線時刻（2026/11/3–2027/3/3）；[AeroRoutes](https://www.aeroroutes.com/eng/tag/EVA+Air) 長榮航空 NW26 公告（[青森](https://www.aeroroutes.com/eng/260416-brnw26aoj)、[神戶](https://www.aeroroutes.com/eng/260724-brnw26ukb)、[德里](https://www.aeroroutes.com/eng/260805-brnw26del)）。整理於 2026/11/3。
- 地圖：[world-atlas](https://github.com/topojson/world-atlas)（Natural Earth 1:50m，公有領域）。
