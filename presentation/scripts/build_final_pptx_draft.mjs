import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import pptxgen from "pptxgenjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const presentationDir = path.resolve(__dirname, "..");
const repoDir = path.resolve(presentationDir, "..");
const outDir = path.join(presentationDir, "exports");
const finalPath = path.join(outDir, "CMP180-final-project-draft.pptx");
await fs.mkdir(outDir, { recursive: true });

const fontFamily = "Microsoft JhengHei";
const monoFont = "Consolas";
const slideSize = { width: 1920, height: 1080 };
const colors = {
  bg: "0A1020",
  text: "E8EEF8",
  muted: "93A7C4",
  line: "1D2B47",
  panel: "101A30",
  cyan: "22D3EE",
  green: "34D399",
  amber: "FBBF24",
  rose: "FB7185",
};

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "CMP180 Automation";
pptx.subject = "CMP180 WLAN TX EVM internship final-project draft";
pptx.title = "CMP180 WLAN TX EVM 自動化量測系統";
pptx.company = "Internship project";
pptx.lang = "zh-TW";
pptx.theme = {
  headFontFace: fontFamily,
  bodyFontFace: fontFamily,
  lang: "zh-TW",
};

function px(value) {
  return value / 96;
}

function frame(position) {
  return {
    x: px(position.left),
    y: px(position.top),
    w: px(position.width),
    h: px(position.height),
  };
}

function addBox(slide, left, top, width, height, fill = colors.panel, line = colors.line) {
  slide.addShape(pptx.ShapeType.rect, {
    ...frame({ left, top, width, height }),
    fill: { color: fill },
    line: { color: line, width: 1 },
  });
}

function addText(slide, text, position, style = {}) {
  slide.addText(text, {
    ...frame(position),
    margin: 0,
    fontFace: style.typeface ?? fontFamily,
    fontSize: Math.round((style.fontSize ?? 34) * 0.75),
    color: style.color ?? colors.text,
    bold: style.bold ?? false,
    fit: "shrink",
    breakLine: false,
    valign: style.valign ?? "mid",
  });
}

function addFooter(slide, index, total) {
  addText(slide, "CMP180 WLAN TX EVM Automation", { left: 100, top: 1014, width: 700, height: 36 }, {
    typeface: monoFont,
    fontSize: 22,
    color: colors.muted,
  });
  addText(slide, `${String(index).padStart(2, "0")} / ${String(total).padStart(2, "0")}`, {
    left: 1680,
    top: 1014,
    width: 140,
    height: 36,
  }, {
    typeface: monoFont,
    fontSize: 22,
    color: colors.muted,
  });
}

function addBullets(slide, items, top = 330) {
  items.forEach((item, idx) => {
    addText(slide, "•", { left: 128, top: top + idx * 88, width: 36, height: 52 }, {
      fontSize: 34,
      color: colors.cyan,
      bold: true,
    });
    addText(slide, item, { left: 178, top: top + idx * 88, width: 1550, height: 68 }, {
      fontSize: 32,
      color: colors.text,
    });
  });
}

function addTitle(slide, eyebrow, title) {
  addText(slide, eyebrow, { left: 100, top: 92, width: 760, height: 42 }, {
    typeface: monoFont,
    fontSize: 24,
    color: colors.cyan,
    bold: false,
  });
  addText(slide, title, { left: 100, top: 150, width: 1500, height: 150 }, {
    fontSize: 64,
    bold: true,
    color: colors.text,
  });
}

function addRows(slide, rows, top = 330) {
  rows.forEach((row, idx) => {
    const y = top + idx * 118;
    addBox(slide, 100, y, 1660, 90);
    addBox(slide, 100, y, 8, 90, row.tone, row.tone);
    addText(slide, row.k, { left: 136, top: y + 18, width: 350, height: 54 }, {
      fontSize: 29,
      bold: true,
      color: colors.text,
    });
    addText(slide, row.v, { left: 510, top: y + 17, width: 1180, height: 58 }, {
      fontSize: 27,
      color: colors.muted,
    });
  });
}

function addImageSlide(slide, eyebrow, title, imagePath) {
  addTitle(slide, eyebrow, title);
  slide.addImage({
    path: imagePath,
    ...frame({ left: 150, top: 315, width: 1620, height: 620 }),
    sizing: { type: "contain", x: px(150), y: px(315), w: px(1620), h: px(620) },
  });
}

const slides = [
  ["FINAL PROJECT / DRAFT", "CMP180 WLAN TX EVM\n自動化量測系統", { cover: true },
    "開場說明：這是一份草稿版結案報告，重點是展示實習期間完成的 CMP180 WLAN TX EVM 自動化、RF 安全邊界、artifacts 與可交接文件。"],
  ["01 / 問題", "手動量測的重現與稽核問題", [
    "CMsquares 手動設定容易讓頻率、功率、routing 與 expected power 漂移。",
    "掃描多個測試點時，重複操作成本高，資料抄錄也容易出錯。",
    "量測條件若只留在操作者記憶中，事後很難還原。",
    "RF 異常收尾必須由程式保證，不能只靠人工記得關閉。"],
    "這頁用來說明專案動機。避免說手動工具不好，重點放在重現性、資料追溯與安全收尾。"],
  ["02 / 目標", "實習專案的交付範圍", [
    "建立 Python 3.11+ CMP180 WLAN TX EVM 自動化系統。",
    "完成 SingleShot、Frequency Sweep、Power Sweep 與 loopback baseline。",
    "輸出 CSV、JSON、metadata、raw response、HTML report 與圖表。",
    "建立 Web GUI、Mock mode、文件中心、SOP、Demo 腳本與 GitHub/CI 整理。"],
    "這頁把期末交付講清楚，並且為後面誠實邊界鋪路。"],
  ["03 / 學習與工具鏈", "從 RF 量測走到可維護的自動化", { rows: [
    { k: "RF / EVM", v: "整理 dBm、dB、EVM、burst power、frequency error 與 invalid token 判讀。", tone: colors.cyan },
    { k: "CMP180 / SCPI", v: "透過 CMsquares、Command Help 與 query-only discovery 建立命令邊界。", tone: colors.green },
    { k: "Python / CI", v: "使用 typed config、pytest 與 GitHub Actions 支撐無儀器回歸。", tone: colors.amber },
    { k: "Web / Report", v: "整合安全確認、job progress、run history、圖表與 artifacts。", tone: colors.rose },
  ]}, "這頁呈現實習學習成果，不只列功能。"],
  ["04 / 系統架構", "分層職責與 RF 授權邊界", { image: "architecture" },
    "講解 Web/CLI、workflow、service、SCPI registry、InstrumentSession 與 CMP180 的分層。"],
  ["05 / RF 安全設計", "送出 RF 前的三道閘門", { rows: [
    { k: "Route 驗證", v: "只允許已驗證的 RF1.1 到 RF1.5 loopback，generator 與 analyzer 不得同 port。", tone: colors.cyan },
    { k: "核准 Profile", v: "只放行已完成 HIL 的 band、bandwidth、frequency 與功率範圍。", tone: colors.green },
    { k: "操作員確認", v: "最後摘要列出實際頻率、功率與頻寬，未確認就不送 RF。", tone: colors.amber },
    { k: "例外收尾", v: "成功、錯誤、逾時、取消都會 Stop 或 Abort，再 RF Off。", tone: colors.rose },
  ]}, "強調這套系統的安全價值。"],
  ["06 / SingleShot 生命週期", "七個階段與不可繞過的 cleanup", { image: "lifecycle" },
    "說明安全檢查失敗不送 RF，RF 開啟後任何例外都進入 cleanup。"],
  ["07 / 實機驗證成果", "WLAN loopback 主線完成 HIL", { stats: [
    { value: "11", label: "approved WLAN section 代表點" },
    { value: "110/110", label: "Loopback repeats 有效" },
    { value: "28", label: "OFDM SISO 結果欄位" },
    { value: "5", label: "statistics 全部保存" },
  ], caption: "涵蓋 2.4 / 5 / 6 GHz 與 20 / 40 / 80 / 160 / 320 MHz。這些證據只授權已核准 loopback profile，不等於 DUT compliance。" },
    "這頁引用 HANDOFF 與 docs/loopback-validation.md。"],
  ["08 / 資料輸出", "每次量測都留下可追溯證據", { stats: [
    { value: "CSV", label: "資料分析與 Excel 檢查" },
    { value: "JSON", label: "結構化結果與 metadata" },
    { value: "RAW", label: "儀器原始回應" },
    { value: "PNG", label: "Matplotlib 報告圖" },
  ], caption: "沒有 approved limit profile 時只標示 MEASURED。Invalid point 不補 0，也不寫成 PASS。" },
    "展示 run artifact 資料夾時，可以打開 CSV、JSON、metadata、HTML report 與 PNG。"],
  ["09 / Web GUI", "雙語響應式量測工作區", [
    "WLAN SingleShot、Frequency Sweep、Power Sweep 與 GPRF Power Reading 分類清楚。",
    "Preview 會顯示 rejection reason、修正方式與正確範圍。",
    "非同步 job 顯示進度、趨勢、取消與 partial artifacts。",
    "Run History 支援搜尋、篩選、排序、載入歷史設定與 2 到 8 筆 run 比較。"],
    "這頁可搭配現場 Web 或錄影素材。"],
  ["10 / 工程實務", "讓系統可以被別人接手", { rows: [
    { k: "SCPI 集中管理", v: "指令收斂到 command map 與 typed registry，不散落在 workflow。", tone: colors.cyan },
    { k: "Protocol 抽象", v: "Workflow 對 InstrumentSession 撰寫，實機與 Mock backend 可切換。", tone: colors.green },
    { k: "設定驗證", v: "YAML 經模型與 cross-field safety validation，錯誤在連線前被擋下。", tone: colors.amber },
    { k: "CI 邊界", v: "GitHub Actions 只跑 unit、Mock 與 config validation，不碰公司 CMP180。", tone: colors.rose },
  ]}, "這頁用工程交接角度說明品質。"],
  ["11 / 問題與修正", "實習期間的關鍵除錯案例", [
    "真實 CMP180 ID token 與預期不同，identity gate 依實機證據修正。",
    "Power point 回傳 INV 曾被誤標完成，後來加入 critical field gate。",
    "Web 自訂值曾執行固定 profile，後來讓前後端共用同一個 plan。",
    "Measurement 長時間 RUN，追到 repetition 漂移為 Continuous 並修正成 SingleShot readback。",
    "GPRF power 受 WLAN ARB burst 影響，改用 CW 量測並在結束後恢復 ARB。"],
    "挑 4 到 5 個講即可，重點是如何發現、如何修、為什麼這樣修。"],
  ["12 / 誠實邊界", "目前還不能宣稱的能力", [
    "V1 loopback acceptance 不等於 DUT 或 UDBox compliance。",
    "正式 calibration profile 與 approved limit profile 仍需 RF owner 核准。",
    "MCS sweep、Constellation 與 5G NR FR1 仍屬下一階段 scope。",
    "Mock、Preview、CMsquares 手動操作與 stored FETCh 不算新的完整 Python 實機量測。"],
    "這頁是保護專案可信度的關鍵。"],
  ["13 / Demo 流程", "現場展示以安全與證據為主", [
    "先展示文件中心與 hardware SOP。",
    "用 Mock / Demo mode 示範完整操作流程。",
    "展示實機 preview gate、最後確認與 rejection reason。",
    "開啟既有 run history、HTML report、CSV、JSON、metadata 與 Matplotlib PNG。",
    "結尾指到 README、SPEC、SCPI matrix、Demo 腳本與錄影計畫。"],
    "這頁對應 docs/live-demo-recording-plan.md。"],
  ["14 / 下一步", "交接後的擴充方向", [
    "取得 traceable path loss、DUT/UDBox route 與 RF owner approval。",
    "完成 approved calibration/limit profile 後再宣稱 compliance。",
    "擴充 MCS sweep、Constellation、5G NR FR1、RBAC 與 structured audit logging。"],
    "結尾重申：目前最完整、最可信的主線是 WLAN loopback 自動化。"],
];

const total = slides.length;
for (const [idx, item] of slides.entries()) {
  const [eyebrow, title, body, notes] = item;
  const slide = pptx.addSlide();
  slide.background = { color: colors.bg };

  if (body?.cover) {
    addText(slide, eyebrow, { left: 130, top: 185, width: 760, height: 42 }, {
      typeface: monoFont,
      fontSize: 24,
      color: colors.cyan,
    });
    addText(slide, title, { left: 130, top: 260, width: 1350, height: 260 }, {
      fontSize: 84,
      bold: true,
      color: colors.text,
    });
    addText(slide, "實習結案報告草稿", { left: 130, top: 560, width: 900, height: 60 }, {
      fontSize: 36,
      color: colors.muted,
    });
    addText(slide, "Rohde & Schwarz CMP180 · Python 3.11+ · WLAN TX EVM", {
      left: 130,
      top: 930,
      width: 1200,
      height: 48,
    }, {
      typeface: monoFont,
      fontSize: 24,
      color: colors.muted,
    });
  } else if (body?.image === "architecture") {
    addImageSlide(
      slide,
      eyebrow,
      title,
      path.join(repoDir, "docs", "diagrams", "system-architecture.png"),
    );
  } else if (body?.image === "lifecycle") {
    addImageSlide(
      slide,
      eyebrow,
      title,
      path.join(repoDir, "docs", "diagrams", "single-measurement-lifecycle.png"),
    );
  } else {
    addTitle(slide, eyebrow, title);
    if (Array.isArray(body)) {
      addBullets(slide, body);
    } else if (body?.rows) {
      addRows(slide, body.rows);
    } else if (body?.stats) {
      body.stats.forEach((stat, statIdx) => {
        const x = 100 + statIdx * 420;
        addBox(slide, x, 350, 380, 245);
        addText(slide, stat.value, { left: x + 32, top: 390, width: 300, height: 88 }, {
          typeface: monoFont,
          fontSize: 54,
          bold: true,
          color: colors.cyan,
        });
        addText(slide, stat.label, { left: x + 32, top: 505, width: 315, height: 90 }, {
          fontSize: 25,
          color: colors.muted,
        });
      });
      addText(slide, body.caption, { left: 100, top: 660, width: 1540, height: 120 }, {
        fontSize: 28,
        color: colors.muted,
      });
    }
  }
  slide.addNotes(notes);
  addFooter(slide, idx + 1, total);
}

await pptx.writeFile({ fileName: finalPath });
console.log(JSON.stringify({ finalPath, slideCount: slides.length }, null, 2));
