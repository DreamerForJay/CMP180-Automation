# 功能開發與文件同步規則

本專案採用「程式、測試、文件一起完成」的 Definition of Done。功能只有程式碼
完成，但操作文件、設定範例或驗證證據沒有更新時，該功能仍視為未完成。

## 每次功能修改必做

1. 更新或新增程式碼。
2. 更新單元測試、Mock 或 hardware test。
3. 更新受影響的 YAML 範例與欄位說明。
4. 更新 `docs/user-guide.md` 的使用步驟。
5. 更新 `README.md` 的功能狀態或快速指令。
6. 若涉及需求、架構或安全限制，更新 `SPEC.MD`。
7. 若涉及 SCPI，更新 `docs/scpi-command-matrix.md` 與
   `configs/scpi_command_map.yaml`。
8. 若涉及實機，更新 `docs/hardware-discovery.md` 或新增具日期的驗證證據。
9. 執行完整測試並記錄通過數量。
10. 執行 `git diff --check`，確認沒有空白或衝突標記問題。

## 文件對應表

| 變更類型 | 必須同步更新 |
|---|---|
| CLI command/argument | `README.md`、`docs/user-guide.md`、CLI tests |
| GUI 按鈕、畫面或流程 | `README.md`、`docs/user-guide.md`、GUI tests |
| YAML 欄位或預設值 | YAML example、config models、loader tests、`SPEC.MD` |
| 連線方式 | `README.md`、instrument example、hardware validation、session tests |
| SCPI command | command map、SCPI matrix、來源證據、registry tests |
| EVM workflow | `SPEC.MD`、user guide、Mock tests、結果 schema 文件 |
| 安全限制 | `SPEC.MD`、hardware validation、validator tests |
| 打包方式 | `README.md`、PyInstaller spec、發布檢查 |

## SCPI 文件最低要求

任何 CMP180 專屬命令加入 command map 前，必須記錄：

- 功能名稱。
- 完整 command/query 字串。
- 參數與單位。
- 回傳欄位與單位。
- 來源：CMP180 Remote Manual、Command Help 或 SCPI Recorder。
- CMP180 firmware / WLAN software 版本。
- 真實硬體驗證日期。
- 成功回應與錯誤佇列結果。
- 是否會改變 RF、routing、workspace 或量測狀態。

不得用其他 R&S 儀器的命令猜測 CMP180 命令。

## 提交前檢查

```powershell
New-Item -ItemType Directory -Force output | Out-Null
.\.venv\Scripts\python.exe -m pytest -q --basetemp=output\pytest-tmp
git diff --check
git status --short
```

提交訊息應描述功能，不使用模糊的 `update` 或 `fix stuff`。若文件與功能在同一次
變更中完成，應放在同一個 commit 或相鄰且容易追蹤的 commits。

## Pull Request 驗收

- 測試全數通過。
- 文件連結有效。
- README 的目前狀態正確。
- 實機功能有證據且沒有未審核的 SCPI。
- RF safety 與 `finally` 關閉策略經測試。
- 不包含 `.venv`、logs、outputs、憑證或內部敏感資料。
