# Google Apps Script 分享版部署／Google Apps Script Viewer Deployment

## 中文版本

### 用途與安全邊界

`deploy/google-apps-script/` 是唯讀分享與歷史資料分析頁，可從 Google Apps Script 部署成固定 Web App 網址。它支援中英切換、亮暗主題、多個 CSV／JSON 匯入、EVM／Power／Frequency Error 疊圖，以及 Trace 名稱、顏色與顯示控制。

此版本不控制 CMP180。Apps Script 執行在 Google 雲端，無法直接連線公司內網儀器；不得在檔案中加入 CMP180 IP、SCPI、序號、公司內部路徑、License 或未核准的量測資料。匯入檔案只在使用者瀏覽器記憶體中解析，不會由目前程式上傳或永久保存。

### 第一次建立

1. 開啟 [Google Apps Script](https://script.google.com/home/?hl=zh-tw)，新增專案並命名為 `CMP180 Cloud Viewer`。
2. 將 `Code.gs`、`Index.html`、`Stylesheet.html`、`JavaScript.html` 與 `appsscript.json` 建立或貼入專案。
3. 按「部署」→「新增部署」→ 類型選擇「網頁應用程式」。
4. 「執行身分」依公司政策選擇擁有者；「誰可以存取」建議限制為公司 Workspace 網域，不要公開給所有人。
5. 部署後複製 `/exec` 網址，提供給已授權同事。

### 使用 clasp 更新同一網址

Node.js 20+ 環境可安裝官方 `clasp`：

```powershell
npm install @google/clasp -g
clasp login
```

在 Apps Script 專案設定複製 Script ID，把 `.clasp.json.example` 複製為 `.clasp.json` 並填入 ID。不要提交 `.clasp.json`。接著在部署目錄執行：

```powershell
clasp push
clasp version "CMP180 Cloud Viewer update"
clasp deployments
clasp redeploy DEPLOYMENT_ID VERSION_NUMBER "CMP180 Cloud Viewer update"
```

`redeploy` 更新既有 deployment，因此分享出去的 `/exec` 網址不變。正式更新前先使用「部署」→「測試部署」驗證。

### 資料使用

從本機量測 Run 選取 `results.csv` 或 `results.json`，匯入雲端頁即可比較。分享檔案前必須確認沒有 IP、儀器序號、內部路徑、客戶／DUT 識別或其他公司機密。

## English Version

### Purpose and safety boundary

`deploy/google-apps-script/` is a read-only sharing and historical-analysis UI that can be deployed as a Google Apps Script Web App with a stable URL. It supports Chinese/English, light/dark themes, multiple CSV/JSON imports, EVM/Power/Frequency Error overlays, and editable trace names, colours, and visibility.

This version does not control the CMP180. Apps Script runs in Google Cloud and cannot directly connect to an intranet instrument. Do not add the CMP180 IP, SCPI, serial numbers, internal paths, licences, or unapproved measurement data. Imported files are parsed only in the user's browser memory and are not uploaded or persisted by the current implementation.

### First deployment

1. Open [Google Apps Script](https://script.google.com/home/?hl=en) and create a project named `CMP180 Cloud Viewer`.
2. Create or paste `Code.gs`, `Index.html`, `Stylesheet.html`, `JavaScript.html`, and `appsscript.json` into the project.
3. Select Deploy → New deployment → Web app.
4. Choose the execution identity required by company policy. Restrict access to the company Workspace domain rather than publishing to everyone.
5. Copy the deployed `/exec` URL and share it only with authorized colleagues.

### Keep the same URL with clasp

Install the official `clasp` in a Node.js 20+ environment:

```powershell
npm install @google/clasp -g
clasp login
```

Copy the Script ID from project settings. Copy `.clasp.json.example` to `.clasp.json` and enter the ID. Never commit `.clasp.json`. From the deployment directory run:

```powershell
clasp push
clasp version "CMP180 Cloud Viewer update"
clasp deployments
clasp redeploy DEPLOYMENT_ID VERSION_NUMBER "CMP180 Cloud Viewer update"
```

`redeploy` updates the existing deployment, so the shared `/exec` URL remains unchanged. Use Deploy → Test deployments before a production update.

### Data handling

Select `results.csv` or `results.json` from a local measurement run and import it into the cloud page. Before sharing a file, verify that it contains no IP address, instrument serial number, internal path, customer/DUT identity, or other company-confidential information.
