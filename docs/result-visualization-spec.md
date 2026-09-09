# 量測結果與視覺化規格 / Measurement Results and Visualization Specification

## 中文版本

### 1. 目標

每次單點或 sweep 量測都必須留下可追溯、可離線重製的資料。視覺化不得依賴 CMP180 仍在線，也不得只存在於 GUI；專案必須提供獨立腳本，可由既有 CSV／JSON 重新產生圖表與摘要。

### 2. 每次 Run 的輸出

每次 run 使用獨立目錄，至少包含：

```text
output/<timestamp>_<test-name>_<run-id>/
├─ metadata.json
├─ config.snapshot.yaml
├─ results.csv
├─ results.json
├─ raw/
├─ logs/
├─ plots/
└─ report.html
```

- `metadata.json`：run ID、時間、軟體版本、儀器 ID、狀態及完成／失敗原因。
- `config.snapshot.yaml`：實際執行時的 instrument、routing、WLAN、sweep 與 limits 設定。
- `results.csv`：方便 Excel、Python 與公司資料流程使用的逐點標準化資料。
- `results.json`：保留型別、單位、有效性、limit 狀態與原始回應關聯。
- `raw/`：CMP180 原始回應，供追蹤與 parser 重現。
- `plots/`：PNG 與可選 SVG 圖表。
- `report.html`：可直接用瀏覽器開啟的離線報告。

### 3. CSV 最低欄位

最低欄位包含：

- `run_id`、`point_index`、`timestamp`
- `frequency_hz`、`bandwidth_hz`、`generator_power_dbm`
- `evm_all_db`、`evm_data_db`、`evm_pilot_db`
- `burst_power_dbm`、`peak_power_dbm`
- `frequency_error_hz`、`clock_error_ppm`
- `reliability`、`valid`、`limit_status`、`error_message`

欄位名稱與單位固定，不因中英文介面切換而改變。無效值使用空值加上 `valid=false`，不得以數字 `0` 代替。

### 4. 獨立視覺化腳本

目前提供以下離線命令：

```powershell
python scripts\plot_results.py output\<run-id>\results.csv
python scripts\plot_results.py output\<run-id>\results.csv --engine pandas-matplotlib
python scripts\plot_results.py output\<run-id>\results.csv --engine both
python scripts\build_report.py output\<run-id>
```

`plot_results.py` 只讀輸入資料，預設將無外部套件依賴的 SVG 圖表寫入同一 run 的
`plots/`，並可用 `--output-dir` 指定輸出目錄。`build_report.py` 使用已保存的 CSV
重建自包含中英雙語 HTML，不會重新連線或控制 CMP180。Web 比較畫面另支援 SVG、
PNG 與整理後 CSV 匯出。

`--engine pandas-matplotlib` 會用 Pandas 讀取 stored CSV／正規化 `INV`，再以
Matplotlib `Agg` backend 產生 160 DPI PNG；`--engine both` 同時保留 SVG 與 PNG。
此路徑只讀 artifact，不會建立儀器連線或啟動 RF。

**2026-09-03 Web 同步更新**：新建立且具有可用頻率／功率軸的 Run，在保存 `results.csv` 後會自動建立 `plots-matplotlib/`。結果頁上方 Web SVG 是互動主圖，支援指標切換、滑鼠拖曳水平平移、滾輪縮放、hover 十字游標、A/B 游標與 SVG／Web PNG／CSV 匯出；X 軸會依資料自動切換為 Frequency (MHz) 或 Generator Power (dBm)，Y 軸跟隨所選指標顯示完整名稱與單位。下方 Pandas DataFrame + Matplotlib 區塊改為單一選單式 PNG 預覽，可在 EVM、Burst Power、Frequency Error、Clock Error 間切換並開啟原圖，不再一次顯示四張。Matplotlib PNG 以白底、高對比文字輸出，功率掃描會用變動的 Generator Power 作為 X 軸；舊 Run 不會自動改寫。

### 5. 必要圖表

對 frequency sweep，第一版至少產生：

1. Frequency vs. EVM All／Data／Pilot。
2. Frequency vs. Burst Power／Peak Power。
3. Frequency vs. Frequency Error。
4. Frequency vs. Clock Error。
5. 每個頻點的 PASS／FAIL／INVALID 狀態圖。

後續 power sweep 需增加 Power vs. EVM 與 Power vs. output power error。圖表必須顯示單位、run ID、測試時間、有效點與 limit line；無效點不得連成正常資料線。

**2026-09-03 更新**：Web 互動主圖已支援 Power Error (dB)，定義為 `Burst Power - expected_power_dbm`，並在功率軸 Burst Power 圖上畫出 `Expected = Generator Power` 參考線；頻率軸 Burst Power 則畫固定 expected-power 參考線。無效點（`valid=false`）仍不會連成正常資料線、以紅色標示。這些互動分析只使用本次或歷史 Run 保存的資料；是否能宣稱實機能力，仍以該 Run 的 HIL 證據與 metadata 為準。

### 6. GUI 與 Web 整合

- GUI／Web 在量測時顯示即時進度與預覽圖。
- 完成後使用同一套 analysis API 產生正式圖表，避免 GUI 與腳本算法不同。
- 支援繁體中文／英文標籤切換，但原始 CSV schema 保持英文且穩定。
- 使用者可下載 CSV、JSON、PNG／SVG 與 HTML report。

### 7. 驗收條件

- 不連 CMP180，僅以保存的 CSV／JSON 即可重建相同圖表。
- 中途失敗時，已完成點仍存在 CSV，並可產生 partial report。
- 圖表不修改原始資料，並能清楚區分有效、失敗與無效點。
- 使用固定 fixture 執行視覺化腳本，檢查輸出檔存在、欄位映射與資料點數。
- 功能實作時同步更新 `README.md`、`docs/user-guide.md`、GUI 規格與測試。

---

## English Version

### 1. Goal

Every single-point or sweep measurement must produce traceable data that can be reproduced offline. Visualization must not require the CMP180 to remain online and must not exist only inside the GUI. The project must provide standalone scripts that regenerate plots and summaries from existing CSV/JSON artifacts.

### 2. Output from every run

Each run uses a separate directory containing at least:

```text
output/<timestamp>_<test-name>_<run-id>/
├─ metadata.json
├─ config.snapshot.yaml
├─ results.csv
├─ results.json
├─ raw/
├─ logs/
├─ plots/
└─ report.html
```

- `metadata.json`: run ID, timestamps, software version, instrument ID, status, and completion/failure reason.
- `config.snapshot.yaml`: effective instrument, routing, WLAN, sweep, and limit settings.
- `results.csv`: normalized point-by-point data for Excel, Python, and company data workflows.
- `results.json`: typed values, units, validity, limit status, and links to raw responses.
- `raw/`: original CMP180 responses for traceability and parser reproduction.
- `plots/`: PNG and optional SVG plots.
- `report.html`: a standalone offline report that opens in a browser.

### 3. Minimum CSV columns

The minimum columns are:

- `run_id`, `point_index`, `timestamp`
- `frequency_hz`, `bandwidth_hz`, `generator_power_dbm`
- `evm_all_db`, `evm_data_db`, `evm_pilot_db`
- `burst_power_dbm`, `peak_power_dbm`
- `frequency_error_hz`, `clock_error_ppm`
- `reliability`, `valid`, `limit_status`, `error_message`

Column names and units remain stable regardless of the selected UI language. Invalid values use an empty value with `valid=false`; numeric zero must not be substituted.

### 4. Standalone visualization scripts

The following offline commands are available:

```powershell
python scripts\plot_results.py output\<run-id>\results.csv
python scripts\plot_results.py output\<run-id>\results.csv --engine pandas-matplotlib
python scripts\plot_results.py output\<run-id>\results.csv --engine both
python scripts\build_report.py output\<run-id>
```

`plot_results.py` reads only its input and writes dependency-free SVG charts to the run's
`plots/` directory by default; `--output-dir` selects another destination. `build_report.py`
rebuilds a self-contained bilingual HTML report from the saved CSV without reconnecting
to or controlling the CMP180. The Web comparison view additionally exports SVG, PNG, and
a normalized comparison CSV.

`--engine pandas-matplotlib` loads the stored CSV through Pandas, normalizes `INV`, and
uses the headless Matplotlib `Agg` backend to create 160 DPI PNG files. `--engine both`
keeps both SVG and PNG outputs. This artifact-only path never connects to the instrument
or starts RF.

**2026-09-03 Web integration update:** newly created runs with a usable frequency or power axis automatically generate `plots-matplotlib/` after `results.csv` is saved. The upper Web SVG is the interactive primary chart, with metric switching, horizontal mouse-drag panning, wheel zoom, hover crosshairs, A/B cursors, and SVG/Web PNG/CSV export. Its X axis switches automatically between Frequency (MHz) and Generator Power (dBm), while the Y axis follows the selected metric's full name and unit. The lower Pandas DataFrame + Matplotlib area is now a single selectable PNG preview for EVM, Burst Power, Frequency Error, or Clock Error instead of four always-visible images. Matplotlib PNGs use a white background and high-contrast text, and power sweeps use the varying Generator Power as the X axis. Historical runs are not rewritten automatically.

### 5. Required plots

For a frequency sweep, the first release must produce at least:

1. Frequency vs. EVM All/Data/Pilot.
2. Frequency vs. Burst Power/Peak Power.
3. Frequency vs. Frequency Error.
4. Frequency vs. Clock Error.
5. PASS/FAIL/INVALID status for every frequency point.

A later power-sweep release adds Power vs. EVM and Power vs. output-power error. Every plot must show units, run ID, test time, valid points, and limit lines. Invalid points must not be connected as normal data.

**2026-09-03 update:** the Web interactive primary chart now supports Power Error (dB), defined as `Burst Power - expected_power_dbm`. A power-axis Burst Power chart draws the `Expected = Generator Power` reference line, while a frequency-axis Burst Power chart draws a fixed expected-power reference line. Invalid points (`valid=false`) are still disconnected from normal traces and marked in red. These analyses use only saved current or historical run data; hardware capability claims still depend on that run's HIL evidence and metadata.

### 6. GUI and web integration

- The GUI/web application displays live progress and preview plots during a measurement.
- After completion, it uses the same analysis API as the standalone scripts to prevent algorithm differences.
- Traditional Chinese and English plot labels are supported, while the raw CSV schema remains stable English.
- Users can download CSV, JSON, PNG/SVG, and the HTML report.

### 7. Acceptance criteria

- The same plots can be rebuilt from saved CSV/JSON without a CMP180 connection.
- If a run stops partway through, completed points remain in CSV and can produce a partial report.
- Plot generation does not modify source data and clearly distinguishes valid, failed, and invalid points.
- Visualization tests use fixed fixtures and verify output files, column mapping, and point counts.
- When implemented, the feature updates `README.md`, `docs/user-guide.md`, the GUI specification, and tests in the same change.
