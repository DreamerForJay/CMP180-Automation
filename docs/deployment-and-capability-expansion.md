# 交付方式與 CMP180 能力擴充

## 中文版

### 建議交付架構

公司內部正式使用應採用「本機控制服務 + 瀏覽器」：一台與 CMP180 位於同一受控網段的 Windows 量測電腦執行 Python 服務，操作者以瀏覽器開啟 Web。此方式能使用 TCP Socket 控制儀器、保存本機 artifacts，並保留 STOP／ABORT／RF Off 清理。正式開放給多位同事前，仍須加入登入、角色權限、HTTPS、操作稽核與單一量測工作鎖。

建議同時提供四種入口：

1. Web GUI：日常量測、校正、紀錄、比較與報告的主要入口。
2. CLI／PowerShell 選單：維修、網路診斷、設定驗證與無 GUI 的自動批次入口。
3. GitHub repository：版本控制、Issue、Pull Request、CI、安裝與開發文件；不保存公司機密、輸出結果或授權資料。
4. Google Apps Script／GitHub Pages：只能作唯讀手冊、Demo 與去識別化報告檢視器。雲端頁面無法直接安全連到隔離內網的 CMP180，不可當成正式 RF 控制端。

交付給夥伴時，提供版本標籤或鎖定 commit、安裝套件、README、操作 SOP、範例 YAML、Mock 驗收、實機權限申請方式與回復程序。量測電腦建議建立 Windows service 或受控啟動捷徑，避免要求一般使用者手動輸入長指令。

### 能力不是單一範圍

Web 必須同時呈現四層：

- Catalog：R&S 型錄上限，例如 400 MHz–8 GHz、最高 500 MHz 頻寬、兩組 VSA/VSG 與 16 ports。
- Installed：這一台 CMP180 實際安裝的硬體、選件、授權與可用 waveform。
- Approved Profile：公司 RF／安全負責人核准的頻率、功率、路由、頻寬、點數與 dwell envelope。
- Verified HIL：已在特定接線、線損、波形與觸發條件下取得有效結果的點位。

型錄上限只供規劃，不能直接授權 RF。若要逐步擴充到官方能力，應針對每個 band、bandwidth、route、waveform family 與功率區間建立驗證矩陣；依序完成 query-only discovery、RF Off setter/readback、低功率 SingleShot、邊界點、短掃描、長掃描與失敗清理，再擴大核准 Profile。500 MHz 是儀器最高分析頻寬，不代表 WLAN TX EVM 一定有 500 MHz waveform 或解調模式；實際可用值仍由應用、選件與 waveform 決定。

目前 `configs/instrument_capabilities.example.yaml` 是能力分層範例，`/api/capabilities` 只讀公開資料。RF 執行仍以 `approved_profile` 為唯一授權來源。

### 下一批 HIL 擴充順序

1. 由 `*OPT?`、CMsquares 與官方選件文件建立 Installed snapshot。
2. 探索所有 RF port catalog 與可用 Analyzer／Generator resource；不開 RF。
3. 建立 waveform catalog，記錄 standard、bandwidth、MCS、GI、LTF、stream 與 trigger marker。
4. 針對每個候選 profile 執行 RF Off readback 驗證。
5. 在已校正路徑與低功率下執行單點 HIL，要求非 INV、關鍵欄位有效、error queue empty、RF Off。
6. 通過邊界點後才增加 span、點數、功率與其他 route。

## English Version

### Recommended delivery architecture

The production intranet deployment should use a local control service plus a browser. A controlled Windows measurement workstation on the same instrument network runs the Python service, and operators use the Web UI. This preserves TCP Socket access, local artifacts, and STOP/ABORT/RF-Off cleanup. Authentication, role-based access, HTTPS, audit logging, and a single-active-measurement lock are required before multi-user rollout.

Provide four complementary entry points:

1. Web GUI for routine measurements, calibration, history, comparison, and reports.
2. CLI/PowerShell menu for maintenance, network diagnosis, configuration validation, and headless automation.
3. GitHub repository for version control, issues, pull requests, CI, installation, and development documentation; never store company secrets, measurement output, or license data.
4. Google Apps Script/GitHub Pages for read-only manuals, demos, and de-identified report viewing. A cloud browser page cannot safely reach an isolated CMP180 network and must not be the production RF controller.

A partner handoff should include a tagged version or pinned commit, installer, README, operator SOP, example YAML, mock acceptance procedure, hardware-access process, and rollback procedure. A Windows service or controlled launcher is preferable to asking routine users to type long commands.

### Capability is layered, not a single range

The Web UI must show four layers at once:

- Catalog: R&S brochure maximums such as 400 MHz to 8 GHz, up to 500 MHz bandwidth, two VSA/VSG resources, and 16 ports.
- Installed: hardware, options, licenses, and waveforms actually available on this CMP180.
- Approved Profile: frequency, power, route, bandwidth, point-count, and dwell envelope approved by company RF/safety owners.
- Verified HIL: points that produced valid results with a specific route, path loss, waveform, and trigger setup.

Catalog maximums are planning information and never grant RF authorization. Expanding toward full instrument capability requires a verification matrix for every band, bandwidth, route, waveform family, and power range. Perform query-only discovery, RF-Off setter/readback, low-power SingleShot, boundary points, short sweeps, longer sweeps, and failure cleanup before expanding an approved profile. The 500 MHz figure is the maximum instrument analysis bandwidth; it does not guarantee a 500 MHz WLAN TX EVM waveform or demodulation mode. Actual availability depends on the application, installed options, and waveform.

`configs/instrument_capabilities.example.yaml` is the layered capability example. `/api/capabilities` is read-only. RF execution continues to use `approved_profile` as its sole authorization source.

### Next HIL expansion sequence

1. Build an Installed snapshot from `*OPT?`, CMsquares, and official option records.
2. Discover RF port and Analyzer/Generator resource catalogs without enabling RF.
3. Build a waveform catalog containing standard, bandwidth, MCS, GI, LTF, streams, and trigger markers.
4. Validate setter/readback with RF Off for every candidate profile.
5. Run a low-power SingleShot on a calibrated path; require no INV, valid critical fields, an empty error queue, and final RF Off.
6. Expand span, points, power, and routes only after boundary-point acceptance.
