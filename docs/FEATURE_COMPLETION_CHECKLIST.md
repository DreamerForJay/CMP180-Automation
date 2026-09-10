# 功能完成度 Checklist

> 本頁由 `docs/feature-completion-data.yaml` 經 `python scripts/build_feature_checklist.py` 產生。百分比與 Dashboard 不可手動修改；狀態判定必須同時查核程式碼、測試、artifact 與 HIL evidence。

## Dashboard

| Feature | Software | Mock | HIL | Approved | Overall | Score |
|---|---:|---:|---:|---:|---|---:|
| Core Instrument Control | ✅ | ✅ | ✅ | ✅ | COMPLETE | 100% |
| WLAN SingleShot | ✅ | ✅ | ✅ | ✅ | COMPLETE | 100% |
| Frequency Sweep | ✅ | ✅ | ✅ | ✅ | COMPLETE | 100% |
| Power Sweep | ✅ | ✅ | ✅ | ✅ | COMPLETE | 100% |
| Constellation | ✅ | ✅ | ❌ | ❌ | PARTIAL | 70% |
| MCS Sweep | ❌ | ❌ | ❌ | ❌ | TODO | 5% |
| PA Offline Analysis | ✅ | ✅ | N/A | ❌ | PARTIAL | 94% |
| Calibration | ✅ | ✅ | ✅ | ✅ | COMPLETE | 100% |
| DUT Model | ❌ | ❌ | ❌ | ❌ | TODO | 5% |
| UDBox | ✅ | ❌ | ❌ | ❌ | PARTIAL | 60% |
| 5G NR FR1 | ❌ | ❌ | ❌ | ❌ | TODO | 5% |
| Reporting | ✅ | ✅ | N/A | N/A | COMPLETE | 100% |
| Web UI | ✅ | ✅ | N/A | N/A | COMPLETE | 100% |
| RF Safety | ✅ | ✅ | ✅ | ✅ | COMPLETE | 100% |
| User Access Model | ✅ | N/A | N/A | N/A | COMPLETE | 100% |

## 自動計算摘要

- Overall Software Completion: **80%**
- Mock Verification: **71%**
- Hardware/HIL Completion: **55%**
- Documentation Completion: **100%**
- Production Readiness: **76%**

計分權重：Architecture/Data Model 15%、Software 25%、Unit Tested 15%、Mock 15%、HIL 20%、Approved 5%、Documented 5%。不適用項目不進入該分母；RF acquisition 未完成 HIL 時單項最高 70%。

## Core Instrument Control

Overall: **COMPLETE** · Priority: **P0** · Score: **100%**

Current implementation: InstrumentSession、typed registry、setter 與 lifecycle 已有 Mock 與實機證據。

Evidence: `src/cmp180_evm/instrument/；src/cmp180_evm/scpi/；docs/hardware-discovery.md`

Missing work: 無本輪缺口；新增命令仍須逐條取得 CMP180 證據。

- [x] Architecture / Data Model
- [x] Software Implemented
- [x] Unit Tested
- [x] Mock Verified
- [x] HIL Verified
- [x] Approved for DUT Use
- [x] Documented

Status: Software READY / Mock VERIFIED / HIL VERIFIED

## WLAN SingleShot

Overall: **COMPLETE** · Priority: **P0** · Score: **100%**

Current implementation: 28 欄五統計、Web guarded execution、artifact 與 deterministic cleanup 已完成。

Evidence: `src/cmp180_evm/workflow/single_measurement.py；docs/v1-acceptance-report.md`

Missing work: 區段外中心頻率仍逐點 HIL_PENDING，不擴張已核准 profile。

- [x] Architecture / Data Model
- [x] Software Implemented
- [x] Unit Tested
- [x] Mock Verified
- [x] HIL Verified
- [x] Approved for DUT Use
- [x] Documented

Status: Software READY / Mock VERIFIED / HIL VERIFIED

## Frequency Sweep

Overall: **COMPLETE** · Priority: **P0** · Score: **100%**

Current implementation: 固定與 guarded Web 掃描、取消、partial artifact 與 11 WLAN section 已有證據。

Evidence: `src/cmp180_evm/workflow/frequency_sweep.py；docs/hardware-discovery.md`

Missing work: 自訂範圍不自動繼承已核准矩陣，仍需各條件 HIL。

- [x] Architecture / Data Model
- [x] Software Implemented
- [x] Unit Tested
- [x] Mock Verified
- [x] HIL Verified
- [x] Approved for DUT Use
- [x] Documented

Status: Software READY / Mock VERIFIED / HIL VERIFIED

## Power Sweep

Overall: **COMPLETE** · Priority: **P0** · Score: **100%**

Current implementation: INVALID fail-fast、-55 至 -40 dBm 與 approved V1 evidence 已完成。

Evidence: `src/cmp180_evm/workflow/power_sweep.py；docs/v1-acceptance-report.md`

Missing work: 其他功率、route 與 DUT 條件不在現行 approval 範圍。

- [x] Architecture / Data Model
- [x] Software Implemented
- [x] Unit Tested
- [x] Mock Verified
- [x] HIL Verified
- [x] Approved for DUT Use
- [x] Documented

Status: Software READY / Mock VERIFIED / HIL VERIFIED

## Constellation

Overall: **PARTIAL** · Priority: **P0** · Score: **70%**

Current implementation: 標準 model、I/Q parser、BPSK 至 4096-QAM Mock、分析、Web scatter 與五種 artifact 已完成。

Evidence: `src/cmp180_evm/constellation/；tests/unit/test_constellation.py；Web Constellation tab`

Missing work: CMP180 acquisition SCPI、回傳格式驗證、實機 HIL 與 DUT profile approval。

- [x] Architecture / Data Model
- [x] Software Implemented
- [x] Unit Tested
- [x] Mock Verified
- [ ] HIL Verified
- [ ] Approved for DUT Use
- [x] Documented

Status: Software READY / Mock VERIFIED / HIL PENDING

## MCS Sweep

Overall: **TODO** · Priority: **P1** · Score: **5%**

Current implementation: 僅有既有 EHT MCS11 baseline，尚無 multi-MCS framework。

Evidence: `docs/project-development-log.md`

Missing work: Data model、selected-list validation、Mock、chart、artifact、SCPI evidence 與 HIL。

- [ ] Architecture / Data Model
- [ ] Software Implemented
- [ ] Unit Tested
- [ ] Mock Verified
- [ ] HIL Verified
- [ ] Approved for DUT Use
- [x] Documented

Status: Software PENDING / Mock PENDING / HIL PENDING

## PA Offline Analysis

Overall: **PARTIAL** · Priority: **P1** · Score: **94%**

Current implementation: Demo P1dB 與 OIP3／IM3、H2／H3、ACP／ACLR 已有軟體與測試。

Evidence: `src/cmp180_evm/web/mock_service.py；tests/unit/test_web_mock_service.py`

Missing work: 統一 MEASURED／DERIVED／SIMULATED offline schema 與完整 Psat／insufficient_data framework。

- [x] Architecture / Data Model
- [x] Software Implemented
- [x] Unit Tested
- [x] Mock Verified
- N/A — HIL Verified
- [ ] Approved for DUT Use
- [x] Documented

Status: Software READY / Mock VERIFIED / HIL N/A

## Calibration

Overall: **COMPLETE** · Priority: **P1** · Score: **100%**

Current implementation: Profile lifecycle、內插、禁止外插、adapter 與 V1 approval gate 已完成。

Evidence: `src/cmp180_evm/calibration.py；configs/calibration.example.yaml；docs/v1-acceptance-report.md`

Missing work: 新 fixture／cable／route 必須個別校正與核准。

- [x] Architecture / Data Model
- [x] Software Implemented
- [x] Unit Tested
- [x] Mock Verified
- [x] HIL Verified
- [x] Approved for DUT Use
- [x] Documented

Status: Software READY / Mock VERIFIED / HIL VERIFIED

## DUT Model

Overall: **TODO** · Priority: **P1** · Score: **5%**

Current implementation: GPRF 表單已有部分 DUT 參考面欄位，尚無獨立 DUT profile schema。

Evidence: `docs/dut-udbox-measurement-spec.md；src/cmp180_evm/web/static/index.html`

Missing work: dut_profile.example.yaml、驗證、Mock、artifact 與真實 DUT HIL。

- [ ] Architecture / Data Model
- [ ] Software Implemented
- [ ] Unit Tested
- [ ] Mock Verified
- [ ] HIL Verified
- [ ] Approved for DUT Use
- [x] Documented

Status: Software PENDING / Mock PENDING / HIL PENDING

## UDBox

Overall: **PARTIAL** · Priority: **P1** · Score: **60%**

Current implementation: GPRF conversion 計畫、YAML 範例與 UI preset 已存在，但不是完整 UDBox stack。

Evidence: `configs/udbox_sweep.example.yaml；src/cmp180_evm/web/gprf_service.py`

Missing work: 獨立資料模型、Mock、artifact、UI 分析與真實 UDBox HIL。

- [x] Architecture / Data Model
- [x] Software Implemented
- [x] Unit Tested
- [ ] Mock Verified
- [ ] HIL Verified
- [ ] Approved for DUT Use
- [x] Documented

Status: Software READY / Mock PENDING / HIL PENDING

## 5G NR FR1

Overall: **TODO** · Priority: **P2** · Score: **5%**

Current implementation: 僅列為 scope gap，沒有 production command 或量測 workflow。

Evidence: `docs/project-development-log.md`

Missing work: Profile、result model、Mock、chart、artifact、官方 CMP180 command evidence 與 HIL。

- [ ] Architecture / Data Model
- [ ] Software Implemented
- [ ] Unit Tested
- [ ] Mock Verified
- [ ] HIL Verified
- [ ] Approved for DUT Use
- [x] Documented

Status: Software PENDING / Mock PENDING / HIL PENDING

## Reporting

Overall: **COMPLETE** · Priority: **P1** · Score: **100%**

Current implementation: CSV／JSON／HTML／Matplotlib 與 acceptance report builder 已完成。

Evidence: `src/cmp180_evm/results/；scripts/build_report.py；tests/unit/test_result_visualization.py`

Missing work: 新 measurement family 必須沿用 provenance 與 artifact schema。

- [x] Architecture / Data Model
- [x] Software Implemented
- [x] Unit Tested
- [x] Mock Verified
- N/A — HIL Verified
- N/A — Approved for DUT Use
- [x] Documented

Status: Software READY / Mock VERIFIED / HIL N/A

## Web UI

Overall: **COMPLETE** · Priority: **P0** · Score: **100%**

Current implementation: 正式 static/ 工作區具響應式 UI、Mock、guarded hardware、history、chart 與 Constellation。

Evidence: `src/cmp180_evm/web/static/；tests/unit/test_web_original_static.py`

Missing work: 新功能仍須維持窄螢幕與無 RF 的 CI 驗收。

- [x] Architecture / Data Model
- [x] Software Implemented
- [x] Unit Tested
- [x] Mock Verified
- N/A — HIL Verified
- N/A — Approved for DUT Use
- [x] Documented

Status: Software READY / Mock VERIFIED / HIL N/A

## RF Safety

Overall: **COMPLETE** · Priority: **P0** · Score: **100%**

Current implementation: Route／profile／power gate 與 success/error/timeout/cancel cleanup 已有測試及 HIL。

Evidence: `src/cmp180_evm/workflow/；docs/hardware-test-sop.md；docs/v1-acceptance-report.md`

Missing work: 每個新增 RF workflow 都必須重新驗證，不可繼承 unrelated HIL。

- [x] Architecture / Data Model
- [x] Software Implemented
- [x] Unit Tested
- [x] Mock Verified
- [x] HIL Verified
- [x] Approved for DUT Use
- [x] Documented

Status: Software READY / Mock VERIFIED / HIL VERIFIED

## User Access Model

Overall: **COMPLETE** · Priority: **P0** · Score: **100%**

Current implementation: Single Permission Model；RF safety 與使用者角色分離。

Evidence: `SPEC.MD；docs/FEATURE_COMPLETION_CHECKLIST.md`

Missing work: 無；權限模型已定義完成，RF safety gate 獨立保留。

- [x] Architecture / Data Model
- [x] Software Implemented
- N/A — Unit Tested
- N/A — Mock Verified
- N/A — HIL Verified
- N/A — Approved for DUT Use
- [x] Documented

Status: Software READY / Mock N/A / HIL N/A

