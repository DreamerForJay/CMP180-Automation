# 架構圖 Architecture Diagrams

[繁體中文](#繁體中文) · [English](#english)

## 繁體中文

本資料夾放的是由 [Archify](https://github.com/tt-a1i/archify) 產生的互動式系統圖。每張圖都是
**單一檔案的 HTML**，直接用瀏覽器開啟即可，不需要架站、也沒有外部相依。圖內建深／淺主題、
搜尋、focus、路徑追蹤、導覽章節與 PNG／SVG 匯出。

| 圖 | 內容 | 來源 |
|---|---|---|
| [系統架構](system-architecture.html) | 從操作員瀏覽器到 CMP180 實機的完整分層、RF 授權區與設定／證據流向 | [`system-architecture.json`](system-architecture.json) |
| [SingleShot 生命週期](single-measurement-lifecycle.html) | `MeasurementPhase` 七個階段、`finally` 收尾保證與不送 RF 的拒絕路徑 | [`single-measurement-lifecycle.json`](single-measurement-lifecycle.json) |

![CMP180 系統架構圖](system-architecture.png)

![SingleShot 量測生命週期圖](single-measurement-lifecycle.png)

> 上面兩張是靜態預覽。GitHub 不會直接執行 HTML，請下載或 clone 後開啟 `.html` 才有互動功能。

### 這兩張圖對應的程式碼

系統架構圖的節點都標了 `SRC` 徽章，指向 revision `bfe8e7e` 當下真實存在的檔案與行號，
共 16 筆原始碼引用，由 Archify 對本 repo 驗證通過後才產生：

- `src/cmp180_evm/web/server.py` — `Cmp180WebHandler` 與 `/api/*`
- `src/cmp180_evm/web/jobs.py` — `JobManager` 單一 active job、暫停與取消
- `src/cmp180_evm/workflow/single_measurement.py` — `validate_safety` 與 `run_single_measurement`
- `src/cmp180_evm/web/capabilities.py` — 已核准的 band／bandwidth profile
- `src/cmp180_evm/instrument/base.py` — `InstrumentSession` Protocol（實機與 Mock 共用）
- `src/cmp180_evm/scpi/registry.py` — 集中式 SCPI 指令表
- `src/cmp180_evm/results/artifacts.py` — CSV／JSON／metadata／report 輸出

生命週期圖對應 `workflow/single_measurement.py` 的 `MeasurementPhase` 與 `run_single_measurement`，
另見[SingleShot 狀態機](../single-measurement-state-machine.md)。圖上刻意呈現兩件事：

1. **RF 收尾不可繞過** — RF On 之後的任何例外、逾時或取消都會落入 `finally`，先 `stop_measurement`
   再 `rf_off`；收尾自身的錯誤被收集到 `cleanup_errors`，不會遮蔽原始例外。
2. **拒絕即不送 RF** — 缺少操作員確認、generator 與 analyzer 同 port、或功率超過核准上限，
   都在 `VALIDATING` 就丟出 `SafetyGuardError`，全程沒有送出任何 RF。

### 重新產生

圖的權威來源是 `.json`，`.html` 是編譯產物。安裝 Archify skill 後：

```powershell
node bin/archify.mjs validate architecture docs/diagrams/system-architecture.json --quality showcase --repo-root .
node bin/archify.mjs deliver  architecture docs/diagrams/system-architecture.json docs/diagrams/system-architecture.html --quality showcase --repo-root .
node bin/archify.mjs visual-check docs/diagrams/system-architecture.html
```

改動架構後請一併更新 `.json` 並重新 `deliver`，讓圖和程式碼不會失真。若有節點的 `sources`
指向已不存在的檔案，`deliver` 會直接失敗——這是刻意的，用來擋下過期的架構圖。

### 目前狀態

兩張圖都通過 Archify 的 9 項 artifact 檢查（showcase profile，0 error、0 warning），
並以真實 Chrome 在 1440×900、1600×1000、1920×1080、2048×1320 四種桌面尺寸完成 containment
與可讀性驗證。生命週期圖的第三條 band 是渲染器固定版面的一部分，本圖未使用。

## English

This folder holds interactive system diagrams generated with [Archify](https://github.com/tt-a1i/archify).
Each diagram is a **single self-contained HTML file** — open it in a browser, no server and no external
dependencies. Dark/light themes, search, focus, relationship tracing, guided views, and PNG/SVG export
are built in.

| Diagram | Content | Source |
|---|---|---|
| [System architecture](system-architecture.html) | Every layer from the operator browser to the CMP180 instrument, the RF-authorised zone, and how configuration and evidence flow | [`system-architecture.json`](system-architecture.json) |
| [SingleShot lifecycle](single-measurement-lifecycle.html) | The seven `MeasurementPhase` states, the guaranteed `finally` cleanup, and the reject path that transmits no RF | [`single-measurement-lifecycle.json`](single-measurement-lifecycle.json) |

The architecture nodes carry `SRC` badges pointing at files and line numbers that genuinely exist at
revision `bfe8e7e` — 16 source references, verified against this repository before the artifact was
produced.

The `.json` file is the authoritative source; the `.html` is compiled output. Rebuild with `validate`,
then `deliver`, then `visual-check` (see the PowerShell block above). `deliver` fails outright when a
node's `sources` no longer resolve, which is deliberate: it stops a stale architecture diagram from
shipping.

Both diagrams pass all 9 Archify artifact checks under the showcase profile with 0 errors and 0
warnings, and were containment- and readability-checked in real Chrome at 1440×900, 1600×1000,
1920×1080, and 2048×1320. The third band in the lifecycle diagram belongs to the renderer's fixed
layout and is unused here.
