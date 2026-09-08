# 期末專案簡報 Final-project deck

[繁體中文](#繁體中文) · [English](#english)

## 繁體中文

這裡是 CMP180 期末專案簡報的原始碼，用 [open-slide](https://github.com/1weiho/open-slide) 撰寫：
每一頁是一個 React 元件，畫布固定 1920×1080。

### 交付檔案

| 檔案 | 用途 |
|---|---|
| `exports/CMP180-final-project.pptx` | **可直接上傳 Google 簡報或 Canva 編輯的版本**，15 頁、16:9、附講稿備忘 |
| `exports/CMP180-final-project-draft.pptx` | 草稿版結案簡報，可先給 mentor 修改與確認 |
| `slides/cmp180-final-project/index.tsx` | open-slide 原始碼，改這裡才是改簡報本身 |
| `slides/cmp180-final-project/assets/` | 兩張系統圖，由 `docs/diagrams/` 的 Archify 成品以深色主題擷取 |

`.pptx` 是給 Google 簡報／Canva 用的匯出版，open-slide 原始碼才是可維護的來源。
內容有更動時兩邊要一起改。

### 上傳到 Google 簡報

1. Google 雲端硬碟 → 新增 → 檔案上傳 → 選 `CMP180-final-project.pptx`。
2. 在該檔案按右鍵 → 開啟工具 → Google 簡報。
3. 檔案 → 另存為 Google 簡報，之後即可直接編輯與共用。

字型使用 Microsoft JhengHei（中文）與 Consolas（等寬）。Google 簡報沒有這兩套字型時會自動替換，
版面會保持，但字寬略有差異；介意的話可全選改成思源黑體。

### 上傳到 Canva

Canva → 建立設計 → 匯入檔案 → 選同一個 `.pptx`。文字會轉成可編輯的文字框，不是整頁圖片。

### 本機預覽與修改

```powershell
cd presentation
npm install
npm run dev      # http://localhost:5173
npm run build    # 產生靜態網站到 presentation/dist（未納入版本庫）
npm run build:pptx:draft  # 產生 presentation/exports/CMP180-final-project-draft.pptx
```

開發伺服器起來後點該簡報即可翻頁，按 `F` 進全螢幕播放，改 `index.tsx` 會即時熱更新。

### 為什麼 PPTX 另外產生

`.pptx` 不是從 open-slide 匯出，而是用 `pptxgenjs` 依同一份內容重建的。
這樣文字在 Google 簡報與 Canva 裡才是真正可編輯的文字框，而不是一張圖。

## English

Source for the CMP180 final-project deck, written with
[open-slide](https://github.com/1weiho/open-slide) — each page is a React component on a fixed
1920×1080 canvas.

| File | Purpose |
|---|---|
| `exports/CMP180-final-project.pptx` | **Upload-and-edit version for Google Slides or Canva** — 15 slides, 16:9, with speaker notes |
| `exports/CMP180-final-project-draft.pptx` | Draft final-project deck for mentor review and revision |
| `slides/cmp180-final-project/index.tsx` | open-slide source; edit here to change the deck itself |
| `slides/cmp180-final-project/assets/` | The two system diagrams, captured in dark theme from the Archify artifacts in `docs/diagrams/` |

**Google Slides:** upload the `.pptx` to Drive, right-click → Open with → Google Slides, then
File → Save as Google Slides. **Canva:** Create a design → Import file → pick the same `.pptx`.
Text arrives as real, editable text boxes rather than a flattened image.

Fonts are Microsoft JhengHei (Chinese) and Consolas (monospace). Google Slides and Canva
substitute anything they lack; the layout holds, though glyph widths shift slightly.

```powershell
cd presentation
npm install
npm run dev      # http://localhost:5173
npm run build    # static site into presentation/dist (git-ignored)
npm run build:pptx:draft  # writes presentation/exports/CMP180-final-project-draft.pptx
```

The `.pptx` is rebuilt from the same content with `pptxgenjs` rather than exported from
open-slide, so the text stays editable downstream. Keep `index.tsx` and the `.pptx` in sync
when the deck changes.

Navigation in the dev server: arrow keys / PageUp / PageDown move between pages, `F` enters
fullscreen play mode, Esc exits.
