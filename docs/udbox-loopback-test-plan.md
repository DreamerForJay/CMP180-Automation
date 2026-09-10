# UD Box 級聯迴路測試計畫（無 DUT）

## 1. 目的與邊界

本計畫處理的接線是「CMP180 → UD Box Up channel → RF 迴路線 → UD Box Down channel
→ CMP180」，路徑中**沒有 DUT**。目的是把 UD Box 自己當成受測物，量出這條鏈路的
轉換損耗、線性度與對 WLAN EVM 的劣化，並與已完成 HIL 的直連 loopback 基準對比。

本計畫**不是** UD Box 的規格驗證，也不是 compliance 流程。此 route 沒有任何 HIL
證據，所有結果一律標 `MEASURED`，不得作為 compliance 宣稱。

## 2. 接線與前提

```
CMP180 RF1.1 ──IF──> [UD Box Up: RF = LO + IF] ──RF──┐
                                                      │  RF1 → RF2 迴路線
CMP180 RF1.5 <──IF── [UD Box Dn: IF = RF − LO] <──RF──┘
```

儀器端假設為 **TMYTEK UD Box 0630**：IF 1–8 GHz、RF 6–30 GHz、LO 6–30 GHz、
conversion loss 約 10 dB typ（來源：datasheet RF Specifications 表，非實機驗證）。
若型號不同，第 3、4 節的所有數字都必須重算。

以下三項軟體無法讀回，必須由操作員在 TLKCore／UDBox GUI 確認並截圖存證：

1. **兩個 channel 是否共用同一顆 LO。** 若為獨立雙 LO，兩者的差頻會直接成為量到的
   頻率誤差，第 3 節的頻率抵銷不成立。
2. **Down channel 的 sideband 為高側**（`IF = RF − LO`）。設成低側收不到訊號。
3. **LO = 6000 MHz、兩個 channel 均已 enable。**

## 3. 頻率會自己抵銷

Up 走高側 `RF = LO + IF`，Down 走高側 `IF = RF − LO`，共用同一顆 LO 時：

```
IF_out = (LO + IF_in) − LO = IF_in
```

**Analyzer 頻率 = Generator 頻率**，與直連 loopback 相同。兩個後果：

- GPRF request **不可**送 `conversion` 區塊。`workflow/frequency_conversion.py` 模型的是
  「單次」轉換（兩端不同頻）；級聯後兩端同頻，送出 `conversion` 會把 analyzer 調到
  單次轉換的 RF 頻率，結果是量底噪。`configs/udbox_sweep.example.yaml` 是單次轉換的
  範例，**不可**套用到本接線。
- 可以直接沿用 6105 MHz 這個唯一完成 HIL 的頻率（見 `docs/hardware-discovery.md`），
  逐項對比直連基準；差異即為 UD Box 造成的劣化。

以 6105 MHz 驗算頻率預算：IF 6105 MHz 落在 1–8 GHz ✓；LO 6000 MHz 使
RF = 12105 MHz 落在 6–30 GHz ✓；兩端 6105 MHz 也都在 CMP180 400 MHz–8 GHz 內 ✓。

## 4. 功率預算

| 節點 | 電平 | 依據 |
|---|---|---|
| CMP180 Generator (RF1.1) | `Pgen` | GPRF 路徑上限 +8 dBm |
| UD Box IF1 輸入 | `Pgen` | 軟體用 `dut_max_input_dbm` 守住的節點 |
| UD Box RF1 輸出 | `Pgen − 10 dB` | Up conversion loss typ |
| UD Box RF2 輸入 | `Pgen − 約 11 dB` | 再減 12 GHz 迴路線損約 1 dB |
| UD Box IF2 輸出 | `Pgen − 約 21 dB` | 再減 Down conversion loss |
| CMP180 Analyzer (RF1.5) | 同上 | 由 `sa_safe_limit_dbm` 守住 |

**級聯總損耗約 21 dB**，比直連 loopback 的約 0 dB 差了一個數量級。這一點決定了後面
每一個階段的功率設定，也是第 7 節 WLAN EVM 受阻的原因。

### 保護手段：用功率上限，不用衰減器

真正的瓶頸是 **Down channel 的 RF2 輸入**，而那是迴路內部節點，軟體看不到也擋不到。
把它換算回軟體擋得到的 IF1：`RF2 ≈ IF1 − 11 dB`。因此本計畫以
**`stop_dbm` = `dut_max_input_dbm` = 0 dBm** 當守門，此時 RF2 約為 −11 dBm。
取得 TMYTEK 提供的 RF2 額定值之前，不得調高這兩個值。

**不建議**在 IF2 → RF1.5 加衰減器。analyzer 在 stop = 0 dBm 時也只收到約 −21 dBm，
距離 `sa_safe_limit_dbm: 0` 已有 21 dB 餘裕；加 pad 只會把低功率端推進底噪。同理，
RF1 → RF2 迴路也不建議加 pad——保護該節點的是 generator 功率上限，不是實體衰減。

CMP180 端的安全性沒有疑慮：即使 generator 意外開到 +8 dBm，analyzer 也只收到
約 −13 dBm。

## 5. 分階段執行

執行前先讀 `docs/hardware-test-sop.md` 與 `docs/development-workflow.md`。

### Stage 0 — 不送 RF 的前置（必做）

- UD Box 供電，TLKCore／UDBox GUI 連上，完成第 2 節的三項確認並截圖。
- CMP180 query-only preflight：`scripts/cmp180_rf_state_validate.py`，確認 Generator RF
  `OFF`、measurement `OFF`／`RDY`、error queue 空。
- ⚠️ 這一步不可跳過。`docs/hardware-discovery.md` 記錄 2026-09-10 那次 preflight 發現
  **Generator 被留在 `ON`，1250 MHz／−30 dBm**。UD Box 現在接在該 port 上，帶電插拔
  會直接把功率灌進 IF1。

### Stage 1 — 直連基準（需暫時拔掉 UD Box）

在 6105 MHz 量 RF1.1 → RF1.5 直連的 GPRF 功率讀值，取得「線損 + CMP180 絕對功率
誤差」基準。**這是唯一能把線損從 UD Box 損耗中扣掉的機會**；接回 UD Box 之後就
做不了了。沒有這條基準，Stage 3 量到的損耗會混入未知線損。

### Stage 2 — 單點「通不通」（第一次送 RF 進 UD Box）

用 `configs/udbox_cascade_loopback.example.yaml`，把 `stop_dbm` 暫時改成 `-30`
（起點與終點相同即為單點）。

判定：實測級聯損耗落在 **20–25 dB** → 鏈路通了。若讀到底噪，最可能是 Down channel
sideband 設反或 channel 未 enable，回 Stage 0，不要靠加大功率硬試。

### Stage 3 — 功率掃描（特徵化）

還原 `stop_dbm: 0`，跑完整 16 點掃描（−30 → 0 dBm，step 2 dB）。

產出是**級聯 conversion loss 對輸入功率的曲線**。Gain 平坦代表線性；高端開始下掉
代表 Down channel 進入壓縮，該轉折點就是這條迴路的實務工作上限。

注意：這裡量到的壓縮是「Up 輸出 + 迴路線 + Down 輸入」的複合行為，**不是 UD Box 的
P1dB 規格**，artifact 與報告都不得寫成 P1dB。量完後把實測損耗回填範例的
`expected_dut_gain_db`。

### Stage 4 — WLAN TX EVM（目前被程式擋住，見第 7 節）

目標是用 6105 MHz／320 MHz／EHT 的已驗證 profile 跑 SingleShot，與直連基準對比
EVM、Frequency Error 與 Burst Power。

其中 **Frequency Error 是最有診斷價值的單一數字**：若 Up／Down 為獨立雙 LO，兩顆
LO 的差頻會原封不動出現在這一欄。

### Stage 5 — IF 頻率掃描（選配）

在 6 GHz WLAN band 內掃 IF，量級聯的頻率平坦度。約束：IF ∈ [1, 8] GHz、
RF = LO + IF ∈ [6, 30] GHz、兩端都在 CMP180 400 MHz–8 GHz 內。以 LO = 6000 MHz，
IF 可掃到接近 8 GHz 都成立。

## 6. Go／No-Go

送 RF 前以下全部為 Yes，任一項為 No 或 Unknown 即停止：

- [ ] Generator query 為 `OFF`，measurement 為 `OFF` 或 `RDY`，error queue 空。
- [ ] UD Box 已供電，LO 頻率、兩個 channel enable 與 Down channel sideband 已確認並截圖。
- [ ] 實際接線與第 2 節圖示一致，四段線材都已鎖固。
- [ ] `stop_dbm` 與 `dut_max_input_dbm` 均未超過 0 dBm。
- [ ] Stage 1 直連基準已完成並保存。
- [ ] 現場操作員在場，且知道 emergency stop 方式。

## 7. 目前程式擋住 Stage 4 的地方

以下兩處都是為**直連 loopback** 寫死的，遇到 21 dB 級聯損耗即不成立：

| 位置 | 現況 | 後果 |
|---|---|---|
| `web/custom_plans.py` `_requested_power_ceiling()` 與 `_gate()` | WLAN generator 功率硬上限 −30 dBm | 扣掉 21 dB 後 analyzer 僅約 −51 dBm，比已驗證的 −40 dBm 還低 11 dB |
| `web/real_service.py` `VERIFIED_EXPECTED_NOMINAL_POWER_DBM = -20.0` | Analyzer ranging 寫死 −20 dBm | 實際輸入約 −51 dBm，差 31 dB，極可能回 `INV`／reliability 74 |

GPRF 路徑沒有這兩個限制（上限 +8 dBm、ranging 由 plan 推算），因此
**Stage 2、3、5 以現有程式即可執行，Stage 4 必須先改碼**。

建議改法對齊 `workflow/frequency_sweep.py` 已走過的路線：把上限改為呼叫端宣告的
`maximum_generator_power_dbm`，並讓 `expected_nominal_power_dbm` 成為操作員輸入
（預設仍為 −20 dBm，直連行為不變），而不是無條件放寬。

另有一項標示缺口：`workflow/rf_routes.py` 的 `parse_route()` 只接受
`GENERATOR-ANALYZER` 兩段格式，無法表達路徑中的 UD Box，因此本計畫的
`cable_confirmation` 仍是 `RF1.1-RF1.5`。**這會讓 artifact 看起來像直連量測**，
在 Stage 4 改碼時應一併加入路徑描述欄位，否則等於留下假證據。

## 8. 待補資料

以下資料取得前，相關上限只能維持保守值：

- UD Box 完整型號、序號、韌體版本。
- **RF2（Down channel RF 輸入）的 absolute maximum rating。** datasheet 的 RF
  Specifications 表只給 P1dB（線性度），沒有損傷閾值；第 4 節的 0 dBm 是工作上限，
  不是損傷閾值。
- IF1 輸入的 absolute maximum rating（同上）。
- 兩個 channel 的 LO 架構（共用／獨立）與參考時脈來源。
