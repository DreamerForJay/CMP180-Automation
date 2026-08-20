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

規劃提供以下離線命令：

```powershell
python scripts\plot_results.py output\<run-id>\results.csv
python scripts\build_report.py output\<run-id>
```

`plot_results.py` 必須只讀輸入資料，預設將圖表寫入同一 run 的 `plots/`，並支援指定輸出目錄。`build_report.py` 必須使用已保存的 artifacts 建立 HTML，不得重新連線或控制 CMP180。

### 5. 必要圖表

對 frequency sweep，第一版至少產生：

1. Frequency vs. EVM All／Data／Pilot。
2. Frequency vs. Burst Power／Peak Power。
3. Frequency vs. Frequency Error。
4. Frequency vs. Clock Error。
5. 每個頻點的 PASS／FAIL／INVALID 狀態圖。

後續 power sweep 需增加 Power vs. EVM 與 Power vs. output power error。圖表必須顯示單位、run ID、測試時間、有效點與 limit line；無效點不得連成正常資料線。

**2026-08-20 更新（Mock 版本已完成）**：Web GUI 功率掃描 tab 的圖表已支援 Power vs. EVM（沿用現有結果圖表，X 軸依掃描類型自動切換頻率／功率並標示單位），且無效點（`valid=false`）不會連成正常資料線、以紅色標示。Run ID／測試時間顯示在圖表正上方的 `#runMeta`，不是畫在 SVG 內部。**Power vs. output power error**（設定功率與實際 Burst Power 的差值）尚未實作——目前只能透過既有下拉選單看 Power vs. Burst Power（絕對值，不是誤差），仍是待辦。這些都只是 Mock 資料，實機功率掃描仍未通過 HIL（見 `docs/sweep-safety.md`）。

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

The planned offline commands are:

```powershell
python scripts\plot_results.py output\<run-id>\results.csv
python scripts\build_report.py output\<run-id>
```

`plot_results.py` must only read its input data. By default, it writes plots to the run's `plots/` directory and supports an explicit output directory. `build_report.py` must build HTML from saved artifacts without reconnecting to or controlling the CMP180.

### 5. Required plots

For a frequency sweep, the first release must produce at least:

1. Frequency vs. EVM All/Data/Pilot.
2. Frequency vs. Burst Power/Peak Power.
3. Frequency vs. Frequency Error.
4. Frequency vs. Clock Error.
5. PASS/FAIL/INVALID status for every frequency point.

A later power-sweep release adds Power vs. EVM and Power vs. output-power error. Every plot must show units, run ID, test time, valid points, and limit lines. Invalid points must not be connected as normal data.

**2026-08-20 update (mock version complete)**: the Web GUI's Power Sweep tab chart now supports Power vs. EVM (the existing results chart, with its X axis auto-switching between frequency and power depending on sweep type, labeled with units). Invalid points (`valid=false`) are no longer connected into the normal data line and are marked in red. Run ID/test time appear in `#runMeta` directly above the chart, not drawn inside the SVG itself. **Power vs. output-power error** (the difference between set power and actual Burst Power) is not implemented yet — the existing metric dropdown only offers Power vs. Burst Power (an absolute value, not an error), which remains open work. All of this is mock data only; the real power sweep has not passed HIL (see `docs/sweep-safety.md`).

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
