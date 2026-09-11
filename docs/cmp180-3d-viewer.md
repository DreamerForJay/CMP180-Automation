# CMP180 360° 立體檢視器

## 繁體中文

首頁已使用現有 Blender 外觀模型建立真正的 3D 檢視器，可水平繞行完整 360°。這是照片估算的外觀參考，並非原廠機構 CAD；新增參考照片可供後續修整把手、側面網孔與背板標示，本次沒有宣稱重新完成高精度建模。

### 操作

1. 開啟首頁即自動載入模型並旋轉，不必按啟用按鈕；載入期間呈現主題背景。
2. 滑鼠拖曳或手機水平滑動旋轉；滾輪、雙指捏合或「＋／−」縮放。手機垂直滑動可繼續捲頁。
3. 「正面／背面／側面」切換固定視角；「重設視角」恢復預設三分之四視角與距離。
4. 模型載入後預設自動旋轉（減少動態偏好除外）；可暫停，拖曳時會停止。切換工作區、離開可見範圍或背景頁面會暫停。
5. 全螢幕依瀏覽器支援提供，按同一按鈕或 Escape 離開；不支援的裝置不顯示按鈕。
6. 「靜態圖」結束 3D 檢視並移除模型。載入錯誤／超過 45 秒會保留圖片並提供重試；重試避開失敗下載快取。

鍵盤使用者可 Tab 到元件與按鈕，方向鍵旋轉，Page Up／Page Down 或縮放按鈕縮放。按鈕至少 44px 高。操作與狀態隨右上語言切換；減少動態偏好啟用時不自動旋轉，快捷視角立即切換。

這些操作只改變瀏覽器相機與模型，不送出量測、SCPI 或 RF 工作。

### 資產與離線執行

- 原始來源：`assets/cmp180_3d/cmp180.blend` 與 `cmp180.glb`，保留可編輯零件。
- Web 副本：`src/cmp180_evm/web/static/assets/cmp180-web.glb`。
- 最佳化：398 個網格合併為 21 組，保留 316,668 個三角面；位置採 16-bit 量化，未做刪面簡化。10,698,916 bytes 降為 7,210,932 bytes（約減少 32.6%）。
- 檢視器：`@google/model-viewer` 4.3.1，約 1.07 MB；固定版本程式與 Apache-2.0 授權一併放在 `static/vendor/model-viewer/`。
- 全部資產由本機 Web 服務提供，不需要 CDN、AR 服務或外部解碼器；使用內建 neutral 環境光。
- `cmp180-web.manifest.json` 保存來源／產物 SHA-256、大小、網格數與工具版本，供測試確認重建一致性。

### 重建

安裝工具時需要網路；正常啟動網站不需要 npm、建模工具或網際網路。

```powershell
npm install --prefix .tools/cmp180-viewer --no-audit --no-fund --ignore-scripts --save-exact @google/model-viewer@4.3.1 @gltf-transform/core@4.5.0 @gltf-transform/functions@4.5.0
node scripts/build_cmp180_web.mjs
```

先完成 Blender 匯出，再執行此步驟。腳本只更新 Web 副本、版本 manifest 與本機檢視器，不改原始 `.blend`／`.glb`。參考 [model-viewer 官方文件](https://modelviewer.dev/docs/) 與 [glTF Transform](https://gltf-transform.dev/)。

### 驗收

資產測試檢查有效 GLB、三角面／材質保留、無外部資源或解碼器、檔案指紋與授權。瀏覽器需驗證自動載入、拖曳／鍵盤／觸控、縮放、視角、自轉暫停、全螢幕退出、語言、深淺色與失敗後重試。WebGL 不可用時應回到靜態圖。Safari／iPhone 實機和低階 GPU 仍需裝置驗收。

## English

The home page now uses the existing Blender exterior model in a genuine 3D viewer with unrestricted horizontal 360° orbit. It remains a photo-estimated reference, not manufacturer CAD. The newly supplied photographs can inform later improvements to handles, ventilation, and rear labels; this change does not claim a new precision modeling pass.

### Controls

1. 首頁自動載入模型並旋轉，減少動態偏好除外。
2. Drag with a mouse or swipe horizontally on a phone to orbit. Use the wheel, pinch, or +/− to zoom. Vertical phone swipes continue scrolling the page.
3. Front/Rear/Side choose fixed views; Reset restores the three-quarter view and distance.
4. 預設自動旋轉，可暫停，拖曳時停止。 It pauses when switching workspaces, leaving the visible area, or backgrounding the page.
5. Fullscreen is available where supported; use the same button or Escape to exit. Unsupported devices omit this control.
6. Still image ends the 3D session and removes the model. Errors or a 45-second timeout preserve the poster and offer retry. Retry avoids the failed download cache.

Keyboard users can Tab to the viewer and controls, use arrow keys to orbit, and Page Up/Page Down or the zoom buttons to zoom. Buttons are at least 44px tall. Labels and status follow the language selector. Reduced-motion users get no initial auto-rotation and immediate preset changes.

These controls only modify the browser camera and model. They do not submit measurement, SCPI, or RF jobs.

### Assets and offline operation

- Editable sources remain in `assets/cmp180_3d/cmp180.blend` and `cmp180.glb`.
- The web copy is `src/cmp180_evm/web/static/assets/cmp180-web.glb`.
- Optimization joins 398 meshes into 21 groups, retaining 316,668 triangles. Positions are quantized to 16 bits without triangle simplification. Size decreases from 10,698,916 to 7,210,932 bytes, approximately 32.6%.
- The pinned viewer is `@google/model-viewer` 4.3.1, approximately 1.07 MB, shipped with its Apache-2.0 license in `static/vendor/model-viewer/`.
- Assets are served locally without a CDN, AR service, or external decoder, using the built-in neutral lighting environment.
- `cmp180-web.manifest.json` records source/output SHA-256, size, mesh counts, and tool versions for rebuild verification.

### Rebuild

Tool installation requires network access. Normal website operation requires neither npm, modeling tools, nor the internet.

```powershell
npm install --prefix .tools/cmp180-viewer --no-audit --no-fund --ignore-scripts --save-exact @google/model-viewer@4.3.1 @gltf-transform/core@4.5.0 @gltf-transform/functions@4.5.0
node scripts/build_cmp180_web.mjs
```

Run this after exporting from Blender. The script updates only the web copy, manifest, and local viewer, preserving the original `.blend`/`.glb`. See the [official model-viewer documentation](https://modelviewer.dev/docs/) and [glTF Transform](https://gltf-transform.dev/).

### Acceptance

Asset tests validate GLB structure, triangle/material preservation, absence of external resources/decoders, fingerprints, and licensing. Browser acceptance covers opt-in loading, drag/keyboard/touch, zoom, presets, rotation pausing, fullscreen exit, languages, themes, and failure/retry. WebGL failure must retain the still image. Safari/iPhone hardware and low-end GPUs still require device acceptance.
