# 使用手冊（面向非技術使用者）

本資料夾放的是「完全沒碰過程式或射頻儀器也看得懂」的完整操作手冊。內容涵蓋安裝、啟動、介面導覽、每個功能的操作方式、結果判讀、RF 安全 SOP、CLI 參考、疑難排解、能力邊界與名詞辭典。

| 檔案 | 用途 |
|---|---|
| [`cmp180-user-manual.html`](cmp180-user-manual.html) | **單一來源（source of truth）**。瀏覽器直接開啟，有側邊目錄、可搜尋、亮色排版、響應式，並內建列印樣式 |
| [`cmp180-user-manual.pdf`](cmp180-user-manual.pdf) | A4 列印／寄送版，約 52 頁 |
| [`cmp180-user-manual.docx`](cmp180-user-manual.docx) | Word 可再編輯版本 |

## 與其他文件的關係

本手冊是**入門與操作**用途，不取代權威規格：

1. 需求與安全邊界以根目錄 `SPEC.MD` 為準。
2. 實機操作細節以 [`docs/hardware-test-sop.md`](../hardware-test-sop.md) 為準。
3. 功能完成度以 [`docs/FEATURE_COMPLETION_CHECKLIST.md`](../FEATURE_COMPLETION_CHECKLIST.md) 為準。

若手冊與上述文件衝突，以上述文件為準，並回頭修正手冊。

## 重新產生 PDF 與 DOCX

修改 `cmp180-user-manual.html` 之後執行：

```powershell
.\scripts\build_manual.ps1
```

該腳本會以本機 Chrome 或 Edge 的 headless 模式列印 PDF（列印前自動展開 FAQ 的 `<details>`），再呼叫 `scripts/build_manual_docx.py` 產生 DOCX。轉換器只使用 Python 標準函式庫，不需要額外安裝套件。

只重建 DOCX：

```powershell
python scripts\build_manual_docx.py
```

## 維護原則

- 手冊中**所有能力宣稱都必須對得上專案內既有證據**。不確定是否已完成實機驗證的功能，一律寫成 `HIL PENDING` 或「尚未核准」，不得寫成「已通過」。
- 安全章節（CH 8）的規則不得為了簡化說明而放寬。
- 新增或修改功能時，一併檢查手冊 CH 5（功能說明）與 CH 11（能力邊界）是否需要同步更新。
