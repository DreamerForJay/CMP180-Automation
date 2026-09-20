## CMP180 WLAN TX EVM 自動化量測系統 {{TAG}}

Windows 10／11 64 位元可攜版，不需要安裝 Python。

### 安裝

1. 下載 `CMP180-Windows-x64.zip`（{{SIZE}} MB）並**完整解壓縮**到可寫入的資料夾。
2. 雙擊資料夾內的 `CMP180.exe`。請保留整個資料夾，不要只複製執行檔，也不要直接從壓縮檔內執行。
3. 瀏覽器會開啟 `http://127.0.0.1:8765`；埠號被占用時可用 `CMP180.exe --port 8766`。
4. 結束時回到主控台按 Ctrl+C。關閉瀏覽器分頁不會停止工作站。

完整說明見 [Windows 可攜版文件](https://github.com/DreamerForJay/CMP180-Automation/blob/main/docs/windows-portable.md)與[使用手冊](https://dreamerforjay.github.io/CMP180-Automation/manual/cmp180-user-manual.html)。

### SmartScreen 提示

這個執行檔沒有程式碼簽章憑證，Windows SmartScreen 可能顯示「已保護您的電腦」。請先用下方雜湊值核對檔案，確認無誤後再選擇「其他資訊」→「仍要執行」。

### 檔案校驗

```
SHA-256  {{SHA}}
```

PowerShell 核對方式，輸出應與上方一致：

```powershell
(Get-FileHash .\CMP180-Windows-x64.zip -Algorithm SHA256).Hash
```

### 預設為模擬模式

雙擊啟動不會建立 CMP180 連線，也不會送出任何射頻命令，適合展示與訓練。模擬輸出一律保留 `source=mock` 或 `simulated=true` 標記，**不能作為實機或合規證據**。

實機操作前必須閱讀[硬體量測標準作業程序](https://github.com/DreamerForJay/CMP180-Automation/blob/main/docs/hardware-test-sop.md)，確認接線、衰減、頻率、頻寬、功率、DUT 與分析儀輸入上限，再以 `CMP180.exe --hardware` 啟動。此參數只開啟既有安全閘門，不會替操作員確認硬體。

### 本次發布不含新的實機射頻驗證

打包與驗證只使用模擬與既有已保存結果。要宣稱硬體能力，必須另附核准設定、原始回應、錯誤佇列、最終射頻狀態與日期化實機證據。
