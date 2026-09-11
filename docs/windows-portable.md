# Windows 可攜版

適用 Windows 10／11 x64。接收者不需要安裝 Python。

1. 將 `CMP180-Windows-x64.zip` 完整解壓縮到可寫入的資料夾。
2. 雙擊 `CMP180.exe`，瀏覽器會自動開啟本機工作站。
3. 預設為 Demo／Mock，不連接 CMP180。模擬資料不是實機驗證。
4. 結果存放於 EXE 旁的 `output/`。請保留整個資料夾，不能只複製 EXE。
5. 結束前等待工作完成，再於主控台按 Ctrl+C；關閉瀏覽器不會停止伺服器。

若瀏覽器沒有開啟，可手動前往 http://127.0.0.1:8765。
若埠號已被使用，可執行 `CMP180.exe --port 8766`。

實機操作員必須先閱讀 `docs/hardware-test-sop.md`，確認接線、衰減與輸入限制，
再以 `CMP180.exe --hardware` 啟動。此參數只啟用原有實機入口與安全確認，
不代表已核准 RF 或完成新 HIL。VISA 傳輸可能仍需要另裝相容 VISA runtime；
本次發布不包含實機連線或 RF 驗證。量測中不可強制終止程序。

## 重建與發布檢查

在專案虛擬環境安裝 `.[build,hardware,dev]` 後執行：

```powershell
.venv/Scripts/python.exe scripts/build_windows.py
```

產物為 `dist/CMP180/CMP180.exe` 與 `dist/CMP180-Windows-x64.zip`。
發布前執行 pytest、兩份 YAML validation、`git diff --check`，並從其他工作目錄
啟動 EXE，確認首頁、靜態檔案、能力設定與 Mock artifact 可讀寫。
發布包不包含開發機的 output、私人設定或量測證據。跨電腦的首次啟動仍需由接收者確認。
