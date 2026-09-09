import type { DesignSystem, Page, SlideMeta } from '@open-slide/core';
import { useSlidePageNumber } from '@open-slide/core';
import architecture from './assets/architecture.png';
import lifecycle from './assets/lifecycle.png';

export const design: DesignSystem = {
  palette: { bg: '#0a1020', text: '#e8eef8', accent: '#22d3ee' },
  fonts: {
    display: '"PingFang TC", "Microsoft JhengHei", "Noto Sans TC", system-ui, sans-serif',
    body: '"PingFang TC", "Microsoft JhengHei", "Noto Sans TC", system-ui, sans-serif',
  },
  typeScale: { hero: 104, body: 36 },
  radius: 14,
};

const muted = '#93a7c4';
const line = '#1d2b47';
const panel = '#101a30';
const ok = '#34d399';
const warn = '#fbbf24';
const danger = '#fb7185';
const mono = '"JetBrains Mono", "Cascadia Mono", Consolas, ui-monospace, monospace';

const fill = {
  width: '100%',
  height: '100%',
  background: 'var(--osd-bg)',
  color: 'var(--osd-text)',
  fontFamily: 'var(--osd-font-body)',
  position: 'relative',
} as const;

const Footer = () => {
  const { current, total } = useSlidePageNumber();
  return (
    <div
      style={{
        position: 'absolute',
        left: 100,
        right: 100,
        bottom: 48,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: 22,
        color: muted,
        fontFamily: mono,
      }}
    >
      <span>CMP180 WLAN TX EVM Automation</span>
      <span>
        {String(current).padStart(2, '0')} / {String(total).padStart(2, '0')}
      </span>
    </div>
  );
};

const Eyebrow = ({ text }: { text: string }) => (
  <div
    style={{
      fontSize: 24,
      letterSpacing: '0.22em',
      color: 'var(--osd-accent)',
      fontFamily: mono,
    }}
  >
    {text}
  </div>
);

const Heading = ({ text }: { text: string }) => (
  <h2
    style={{
      fontFamily: 'var(--osd-font-display)',
      fontSize: 68,
      fontWeight: 800,
      lineHeight: 1.2,
      margin: '24px 0 0',
    }}
  >
    {text}
  </h2>
);

const Card = ({ tone, title, body }: { tone: string; title: string; body: string }) => (
  <div
    style={{
      flex: 1,
      background: panel,
      border: '1px solid ' + line,
      borderTop: '4px solid ' + tone,
      borderRadius: 'var(--osd-radius)',
      padding: '36px 34px',
    }}
  >
    <div style={{ fontSize: 34, fontWeight: 700, lineHeight: 1.25 }}>{title}</div>
    <p style={{ fontSize: 27, lineHeight: 1.6, color: muted, margin: '20px 0 0' }}>{body}</p>
  </div>
);

const Stat = ({ value, unit, label }: { value: string; unit: string; label: string }) => (
  <div
    style={{
      flex: 1,
      background: panel,
      border: '1px solid ' + line,
      borderRadius: 'var(--osd-radius)',
      padding: '38px 32px',
    }}
  >
    <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
      <span
        style={{
          fontSize: 82,
          fontWeight: 800,
          color: 'var(--osd-accent)',
          fontFamily: mono,
          lineHeight: 1,
        }}
      >
        {value}
      </span>
      <span style={{ fontSize: 30, color: muted }}>{unit}</span>
    </div>
    <div style={{ fontSize: 26, color: muted, marginTop: 22, lineHeight: 1.5 }}>{label}</div>
  </div>
);

const Row = ({ k, v, tone }: { k: string; v: string; tone: string }) => (
  <div
    style={{
      display: 'flex',
      alignItems: 'center',
      gap: 28,
      padding: '22px 30px',
      background: panel,
      border: '1px solid ' + line,
      borderLeft: '4px solid ' + tone,
      borderRadius: 10,
    }}
  >
    <span style={{ fontSize: 28, fontWeight: 700, minWidth: 300 }}>{k}</span>
    <span style={{ fontSize: 26, color: muted, lineHeight: 1.5 }}>{v}</span>
  </div>
);

const bullets = {
  fontSize: 34,
  lineHeight: 1.65,
  margin: '48px 0 0',
  paddingLeft: 40,
  color: 'var(--osd-text)',
} as const;

const Cover: Page = () => (
  <div
    style={{
      ...fill,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      padding: '0 130px',
    }}
  >
    <Eyebrow text="FINAL PROJECT / 2026" />
    <h1
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 'var(--osd-size-hero)',
        fontWeight: 900,
        lineHeight: 1.12,
        margin: '34px 0 0',
      }}
    >
      CMP180 WLAN TX EVM
      <br />
      自動化量測系統
    </h1>
    <p style={{ fontSize: 38, color: muted, lineHeight: 1.6, margin: '38px 0 0', maxWidth: 1250 }}>
      用可重現、可稽核的 Python 流程，取代重複的 CMsquares 手動量測
    </p>
    <div
      style={{
        marginTop: 56,
        paddingTop: 34,
        borderTop: '1px solid ' + line,
        display: 'flex',
        gap: 64,
        fontSize: 24,
        color: muted,
        fontFamily: mono,
      }}
    >
      <span>Rohde &amp; Schwarz CMP180</span>
      <span>Python 3.11+</span>
      <span>2.4 / 5 / 6 GHz</span>
    </div>
  </div>
);

const Problem: Page = () => (
  <div style={{ ...fill, padding: '100px 100px 0' }}>
    <Eyebrow text="01 / 問題" />
    <Heading text="手動量測沒辦法重現，也沒辦法稽核" />
    <ul style={bullets}>
      <li>CMsquares 逐項手動設定，同一顆待測物換人量就換結果。</li>
      <li>量測條件留在操作者腦中，事後無法追溯當時究竟量了什麼。</li>
      <li>掃描一整段頻段要重複上百次相同操作，費時且容易出錯。</li>
      <li>RF 開關靠人記得關，異常中斷時沒有保證會回到安全狀態。</li>
    </ul>
    <Footer />
  </div>
);

const Goal: Page = () => (
  <div style={{ ...fill, padding: '100px 100px 0' }}>
    <Eyebrow text="02 / 目標" />
    <Heading text="三個必須同時成立的目標" />
    <div style={{ display: 'flex', gap: 32, marginTop: 60 }}>
      <Card
        tone="#22d3ee"
        title="可重現"
        body="量測條件寫在 YAML 與程式裡，任何人用同一份設定都會得到同一個流程。"
      />
      <Card
        tone={ok}
        title="可稽核"
        body="每次 Run 都輸出 CSV、JSON、metadata 與 raw response，事後可完整還原。"
      />
      <Card
        tone={danger}
        title="失敗即安全"
        body="RF 一旦開啟，任何例外、逾時或取消都保證回到 RF Off，不依賴操作者記憶。"
      />
    </div>
    <Footer />
  </div>
);

const Architecture: Page = () => (
  <div style={{ ...fill, padding: '80px 80px 0' }}>
    <Eyebrow text="03 / 系統架構" />
    <h2
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 60,
        fontWeight: 800,
        lineHeight: 1.2,
        margin: '20px 0 0',
      }}
    >
      分層職責與 RF 授權邊界
    </h2>
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: 760,
        marginTop: 18,
      }}
    >
      <img
        src={architecture}
        alt="CMP180 系統架構圖"
        style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', borderRadius: 12 }}
      />
    </div>
    <Footer />
  </div>
);

const Learning: Page = () => (
  <div style={{ ...fill, padding: '100px 100px 0' }}>
    <Eyebrow text="03 / 學習與工具鏈" />
    <Heading text="從 RF 量測走到可維護的自動化" />
    <div style={{ display: 'flex', flexDirection: 'column', gap: 22, marginTop: 54 }}>
      <Row
        k="RF / EVM"
        v="整理 dBm、dB、EVM、burst power、frequency error 與 invalid token 的判讀規則。"
        tone="#22d3ee"
      />
      <Row
        k="CMP180 / SCPI"
        v="透過 CMsquares、Command Help 與 query-only discovery 建立可驗證的命令邊界。"
        tone={ok}
      />
      <Row
        k="Python / CI"
        v="使用 Python 3.11、typed config、pytest 與 GitHub Actions，讓沒有儀器時也能回歸。"
        tone={warn}
      />
      <Row
        k="Web / Report"
        v="把安全確認、非同步 job、run history、圖表與 artifacts 整合成操作員可交接的介面。"
        tone={danger}
      />
    </div>
    <Footer />
  </div>
);

const Safety: Page = () => (
  <div style={{ ...fill, padding: '100px 100px 0' }}>
    <Eyebrow text="04 / RF 安全設計" />
    <Heading text="送出 RF 之前要通過三道閘門" />
    <div style={{ display: 'flex', flexDirection: 'column', gap: 22, marginTop: 54 }}>
      <Row
        k="1. Route 驗證"
        v="只允許已驗證的 RF1.1 到 RF1.5 loopback，generator 與 analyzer 不得同 port。"
        tone="#22d3ee"
      />
      <Row
        k="2. 核准 Profile"
        v="只放行已完成 HIL 的 band 與 bandwidth 區段，功率限制在 -55 到 -30 dBm。"
        tone={ok}
      />
      <Row
        k="3. 操作員確認"
        v="最後摘要列出實際頻率、功率與頻寬，未確認就不會送出任何 RF。"
        tone={warn}
      />
      <Row
        k="不可繞過的收尾"
        v="成功、錯誤、逾時、取消都會走 finally：先 STOP 或 ABORT，再 RF Off。"
        tone={danger}
      />
    </div>
    <Footer />
  </div>
);

const Lifecycle: Page = () => (
  <div style={{ ...fill, padding: '80px 80px 0' }}>
    <Eyebrow text="05 / SINGLESHOT 生命週期" />
    <h2
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 60,
        fontWeight: 800,
        lineHeight: 1.2,
        margin: '20px 0 0',
      }}
    >
      七個階段，收尾不可繞過
    </h2>
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: 620,
        marginTop: 24,
      }}
    >
      <img
        src={lifecycle}
        alt="SingleShot 量測生命週期圖"
        style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', borderRadius: 12 }}
      />
    </div>
    <p style={{ fontSize: 27, color: muted, lineHeight: 1.6, marginTop: 26, maxWidth: 1620 }}>
      紅色虛線是兩條失敗路徑：安全檢查未過就直接終止且全程未送 RF；RF 開啟後的任何例外都必經
      CLEANING_UP。
    </p>
    <Footer />
  </div>
);

const Results: Page = () => (
  <div style={{ ...fill, padding: '100px 100px 0' }}>
    <Eyebrow text="06 / 實機驗證成果" />
    <Heading text="同一支 Python 工具完成的 HIL 覆蓋" />
    <div style={{ display: 'flex', gap: 28, marginTop: 62 }}>
      <Stat value="11" unit="區段" label="2.4 / 5 / 6 GHz 合法 WLAN band 與頻寬組合" />
      <Stat value="176" unit="/ 176" label="channel center 全數量測有效，無 INVALID" />
      <Stat value="28" unit="欄位" label="OFDM SISO 結果解析並寫入 artifacts" />
      <Stat value="5" unit="種輸出" label="CSV / JSON / metadata / raw / report" />
    </div>
    <p style={{ fontSize: 28, color: muted, lineHeight: 1.6, marginTop: 56, maxWidth: 1500 }}>
      涵蓋 20 / 40 / 80 / 160 / 320 MHz。執行時由後端在 RF Off 且量測 idle 的狀態下自動選取匹配
      waveform，並做絕對路徑 readback 確認。
    </p>
    <Footer />
  </div>
);

const Reporting: Page = () => (
  <div style={{ ...fill, padding: '100px 100px 0' }}>
    <Eyebrow text="08 / 資料輸出" />
    <Heading text="每次量測都留下可追溯證據" />
    <div style={{ display: 'flex', gap: 28, marginTop: 62 }}>
      <Stat value="CSV" unit="" label="供 Excel、Pandas 與後續統計分析使用" />
      <Stat value="JSON" unit="" label="保存 normalized results 與 structured metadata" />
      <Stat value="RAW" unit="" label="保留儀器原始回應，方便回查 parser 與異常" />
      <Stat value="PNG" unit="" label="由 Pandas / Matplotlib 產生，可直接放入報告" />
    </div>
    <p style={{ fontSize: 28, color: muted, lineHeight: 1.6, marginTop: 56, maxWidth: 1540 }}>
      沒有 approved limit profile 時，報告只標示 MEASURED。Invalid point 會中斷曲線，不補 0，也不寫成
      compliance PASS。
    </p>
    <Footer />
  </div>
);

const WebTool: Page = () => (
  <div style={{ ...fill, padding: '100px 100px 0' }}>
    <Eyebrow text="07 / 操作介面" />
    <Heading text="雙語響應式 Web 量測工作區" />
    <ul style={bullets}>
      <li>單點、頻率掃描、功率掃描三個分頁，示範與實機共用同一套流程。</li>
      <li>非同步 Job API：逐點進度、即時 EVM 趨勢、暫停與取消，只保留單一 active job。</li>
      <li>Runs Table 支援搜尋、篩選與排序；刪除需輸入 Run ID 並移入可復原 Trash。</li>
      <li>2 到 8 個 Run 疊圖比較，可自訂 Trace 並匯出 SVG / PNG / CSV。</li>
      <li>歷史分析只讀既有 artifacts，全程不送 RF。</li>
    </ul>
    <Footer />
  </div>
);

const Engineering: Page = () => (
  <div style={{ ...fill, padding: '100px 100px 0' }}>
    <Eyebrow text="08 / 工程實務" />
    <Heading text="讓這套系統可以被別人接手" />
    <div style={{ display: 'flex', flexDirection: 'column', gap: 22, marginTop: 54 }}>
      <Row
        k="SCPI 集中管理"
        v="指令收斂到 configs/scpi_command_map.yaml，不在程式各處散落字串。"
        tone="#22d3ee"
      />
      <Row
        k="Protocol 抽象"
        v="Workflow 對 InstrumentSession 撰寫，實機 session 與 Mock 後端可直接互換。"
        tone={ok}
      />
      <Row
        k="設定即型別"
        v="YAML 經 pydantic 模型驗證，錯誤設定在連線之前就被擋下。"
        tone={warn}
      />
      <Row
        k="CI 不碰實機"
        v="GitHub Actions 跑 Windows 與 Python 3.11 的 unit、Mock 與設定驗證，永不執行實機 RF。"
        tone={danger}
      />
    </div>
    <Footer />
  </div>
);

const Honest: Page = () => (
  <div style={{ ...fill, padding: '100px 100px 0' }}>
    <Eyebrow text="09 / 誠實邊界" />
    <Heading text="目前還不能宣稱的事" />
    <div style={{ display: 'flex', gap: 32, marginTop: 60 }}>
      <Card
        tone={warn}
        title="尚未套用校正補償"
        body="Power Reference Plane 補償還沒套用，metadata 記錄 calibration_applied=false。"
      />
      <Card
        tone={warn}
        title="不宣稱 PASS"
        body="沒有正式 limit profile 的實機結果只標示 MEASURED，不等於 RF compliance 通過。"
      />
      <Card
        tone={warn}
        title="Draft 校正流程"
        body="Path Loss profile 可建立與審查，但外部校正儀器 adapter 尚未通過 HIL。"
      />
    </div>
    <p style={{ fontSize: 27, color: muted, lineHeight: 1.6, marginTop: 46, maxWidth: 1560 }}>
      Mock、dry-run、CMsquares 手動量測或單獨的 stored FETCh，都不會被描述成新的完整實機量測。
    </p>
    <Footer />
  </div>
);

const Next: Page = () => (
  <div style={{ ...fill, padding: '100px 100px 0' }}>
    <Eyebrow text="10 / 下一步" />
    <Heading text="接下來要補上的三件事" />
    <ul style={bullets}>
      <li>完成外部校正儀器 adapter 的 HIL 驗證，讓 Path Loss 補償可正式套用。</li>
      <li>重驗固定功率掃描 profile，排除最新 waveform 仍出現的 INV 點位。</li>
      <li>多圖同步：讓 EVM、Power 與 Frequency Error 共用 X 軸與游標。</li>
    </ul>
    <div
      style={{
        marginTop: 72,
        padding: '34px 38px',
        background: panel,
        border: '1px solid ' + line,
        borderLeft: '4px solid var(--osd-accent)',
        borderRadius: 12,
      }}
    >
      <p style={{ fontSize: 30, lineHeight: 1.6, margin: 0 }}>
        目前狀態：Mock 與示範可用；實機 SingleShot 與 11 個 WLAN 區段已通過 HIL。
      </p>
    </div>
    <Footer />
  </div>
);

const DemoFlow: Page = () => (
  <div style={{ ...fill, padding: '100px 100px 0' }}>
    <Eyebrow text="14 / DEMO 流程" />
    <Heading text="現場展示以安全與證據為主" />
    <ul style={bullets}>
      <li>先展示 README、文件中心與 hardware SOP，說明 RF 操作邊界。</li>
      <li>用 Mock / Demo mode 示範 Web 操作，不需要實機也能看完整流程。</li>
      <li>展示實機 preview gate、最後確認、rejection reason 與安全阻擋訊息。</li>
      <li>開啟既有 run history、HTML report、CSV、JSON、metadata 與 Matplotlib PNG。</li>
      <li>若現場沒有 RF 授權，只展示 stored artifacts，不啟動新的 RF job。</li>
    </ul>
    <Footer />
  </div>
);

const End: Page = () => (
  <div
    style={{
      ...fill,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      padding: '0 130px',
    }}
  >
    <Eyebrow text="THANK YOU" />
    <h2
      style={{
        fontFamily: 'var(--osd-font-display)',
        fontSize: 92,
        fontWeight: 900,
        lineHeight: 1.15,
        margin: '34px 0 0',
      }}
    >
      可重現、可稽核，
      <br />
      而且失敗時一定安全
    </h2>
    <p style={{ fontSize: 34, color: muted, lineHeight: 1.6, margin: '40px 0 0', maxWidth: 1250 }}>
      架構圖與生命週期圖的互動版本收錄在 repo 的 docs/diagrams。
    </p>
  </div>
);

export const meta: SlideMeta = {
  title: 'CMP180 WLAN TX EVM 自動化量測系統',
  createdAt: '2026-09-03T00:31:11.715Z',
};

export default [
  Cover,
  Problem,
  Goal,
  Learning,
  Architecture,
  Safety,
  Lifecycle,
  Results,
  Reporting,
  WebTool,
  Engineering,
  Honest,
  Next,
  DemoFlow,
  End,
] satisfies Page[];
