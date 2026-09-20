# CMP180 文件中心

本頁是繁體中文文件入口，區分權威規格、操作文件、驗證證據、設計規劃與封存參考。功能修改時，請依[開發流程](development-workflow.md)同步程式、測試與受影響文件。

## 目錄

1. [操作員必讀](#操作員必讀)
2. [安全、校正與實機驗證](#安全校正與實機驗證)
3. [工程與架構](#工程與架構)
4. [文件權威順序](#文件權威順序)

## 操作員必讀

| 文件 | 用途 |
|---|---|
| [完整使用手冊](manual/README.md) | **零基礎入門**：安裝、操作、結果判讀、射頻安全與疑難排解（HTML／PDF／DOCX） |
| [使用者指南](user-guide.md) | 安裝、命令列、網頁、模擬與實機操作 |
| [Windows 可攜版](windows-portable.md) | 解壓、啟動、實機參數與重新打包 |
| [硬體量測標準作業程序](hardware-test-sop.md) | 接線、射頻安全、執行順序與異常處理 |
| [Web 介面指南](web-gui-guide.md) | 模式、確認流程、結果與輸出檔案 |
| [量測範例與欄位](measurement-example-and-fields.md) | EVM、功率、頻率誤差與結果解讀 |
| [回路驗證](loopback-validation.md) | 重複量測、穩定性、合理性、離群點與檔案證據 |

## 安全、校正與實機驗證

| 文件 | 用途 |
|---|---|
| [安全掃描](sweep-safety.md) | 頻率／功率安全包絡與實機閘門 |
| [自訂實機掃描](custom-hardware-sweep.md) | 自訂計畫、啟動條件與驗收程序 |
| [限制設定檔](limit-profiles.md) | 通過、失敗、無效與核准規則 |
| [校正設定檔](calibration-profiles.md) | 路徑損耗、內插、期限與追溯 |
| [校正介面](calibration-adapters.md) | 外部校正儀器的介面邊界 |
| [硬體探索](hardware-discovery.md) | 已驗證 CMP180 事實與結果證據 |
| [唯讀硬體驗證](hardware-readonly-validation.md) | 只讀探索紀錄與安全限制 |
| [V1 驗收報告](v1-acceptance-report.md) | 已通過能力、簽核閘門與離線報告 |
| [實機展示腳本](v1-demo-script.md) | 安全展示流程與備援方式 |

## 工程與架構

| 文件 | 用途 |
|---|---|
| [命令矩陣](scpi-command-matrix.md) | 命令來源、狀態、副作用與資料格式 |
| [單次量測狀態機](single-measurement-state-machine.md) | 狀態轉換與清理流程 |
| [系統架構圖](diagrams/README.md) | 系統組成與量測生命週期 |
| [功能完成度清單](FEATURE_COMPLETION_CHECKLIST.md) | 自動計算程式、模擬、實機與發布狀態 |
| [結果視覺化規格](result-visualization-spec.md) | 表格、結構化資料與圖表要求 |
| [射頻工作站介面規劃](rf-workstation-ux-plan.md) | 執行紀錄、曲線與安全操作介面 |
| [網頁介面路線圖](ui-ux-roadmap.md) | 介面階段與響應式驗收標準 |
| [CMP180 三維檢視器](cmp180-3d-viewer.md) | 首頁模型、離線資產與操作方式 |
| [網站檢視與改進計畫](web-audit-2026-09-10.md) | 工作區檢查、缺陷證據與後續驗收 |
| [開發流程](development-workflow.md) | 完成定義、測試與文件同步 |
| [專案開發日誌](project-development-log.md) | 問題、解法、進度與交付項目 |

## 文件權威順序

1. 根目錄 `SPEC.MD` 是目前需求與安全邊界的權威規格。
2. `AGENTS.md` 定義程式註解、文件語言、實機安全與開發規則。
3. `README.md` 與本頁提供目前能力與導覽，不取代詳細標準作業程序。
4. `HANDOFF.md` 是變動較快的交接與硬體證據紀錄，不取代權威規格。
5. `CMP180_DEVELOPMENT_SPEC_AND_PLAN.md` 是早期 CMP180 計畫；`DEVELOPMENT_SPEC_AND_PLAN.md` 是歷史設備資料，兩者與目前規格衝突時都以 `SPEC.MD` 為準。
6. `web-v2-design.md` 與 `src/cmp180_evm/web/static_v2/` 是封存參考；正式前端是 `src/cmp180_evm/web/static/`。

文件使用繁體中文。網頁右上角的中文／英文切換屬於系統介面功能，仍會保留，不代表文件需要維護兩份語言版本。
