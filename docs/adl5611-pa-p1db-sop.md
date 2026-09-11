# ADL5611 PA／P1dB 現場 SOP

本文件是 ADL5611 隔天現場量測的操作清單。它補充通用
[硬體量測 SOP](hardware-test-sop.md)、[使用者指南](user-guide.md) 與
[硬體探索紀錄](hardware-discovery.md)，不取代 `SPEC.MD` 的 RF 安全邊界。

## 量測目的

使用 CMP180 GPRF scalar power sweep 取得 ADL5611 的 conducted Pin、Pout、Gain 與
P1dB 判定。這不是 WLAN EVM 解調，也不是 DUT compliance PASS／FAIL；它只回答 PA 在指定
接線、衰減器與參考面設定下的功率增益與壓縮趨勢。

ADI ADL5611 標稱頻率範圍為 30 MHz 至 6 GHz；現有 Loopback approved baseline 的
6105 MHz 已超過標稱上限，不能直接當成 ADL5611 PA 結論。建議第一個現場點使用
900 MHz 或 2.4 GHz 這類落在 DUT 標稱範圍內、線材與儀器餘裕較容易確認的頻率。

## 量測前檢查

1. 確認 DUT、bias tee、DC 供電、RF input、RF output、實體 attenuator 與 CMP180 port
   都已標籤化，並拍照或記錄接線。
2. 確認 RF1.1 接 DUT input，RF1.5 接 DUT output；若經外部 coupler、pad 或 switch，
   將每個元件的 loss 寫入當次紀錄。
3. ADL5611 是主動 PA，`expected_dut_gain_db` 不得留 0。未填 `dut_max_input_dbm` 時，
   GPRF 計畫應被阻擋。
4. `output_attenuator_db` 只填實體接在 DUT output 與 RF1.5 之間的 attenuator；不得把它
   混成 CMP180 measurement EATT。
5. GPRF Web 的 RF1.5 analyzer 安全上限固定為 `+25 dBm`，比前面板 `+30 dBm Max`
   保留 5 dB 裕度；`dut_max_input_dbm` 則獨立保護 DUT input。兩者都不得用表單覆寫。
6. RF On 前確認 fan、散熱與 DC current limit；若 bias current 異常，先關 RF 與 DC，
   不要用 sweep 追問題。

## 建議起始設定

| 欄位 | 建議值 | 理由 |
|---|---:|---|
| Center frequency | 900 MHz | 落在 ADL5611 標稱範圍內，先避開 6105 MHz 邊界問題 |
| Start power | -35 dBm 或更低 | 先確認接線方向與參考面補償 |
| Step | 1 dB | P1dB 附近需要足夠解析度 |
| Dwell | 200 ms 起 | 沿用既有 GPRF workflow；現場再依穩定性調整 |
| Output attenuator | 20 至 30 dB | PA 接近壓縮時保護 RF1.5，實值以現場 pad 為準 |
| RF1.5 fixed safety limit | +25 dBm | 比前面板 +30 dBm Max 保留 5 dB；超過時點位 INVALID，並停止後續掃描 |

第一輪不要直接掃到預估 P1dB。先做 3 到 5 點低功率 sanity sweep，確認 `gain_db` 接近
datasheet 量級、`pout_dbm` 沒有落在底噪、reliability 為 0、error queue 空、final RF 為
OFF。只有 sanity 正常，才放寬 stop power。

## Web 操作流程

1. 啟動本機 Web，進入實機量測頁，切到 `RF 功率讀值（GPRF）`。
2. 按「載入 approved PA profile」作為模板，但將 Center frequency 改成 ADL5611 範圍內的
   頻率，例如 900 MHz；不要沿用 6105 MHz 當 DUT 結論。
3. 填入 `Input cable loss`、`Output cable loss`、`External gain`、`Output attenuator` 與
   `DUT max input`；RF1.5 安全上限固定為 `+25 dBm`。
4. 按「檢查 GPRF 計畫」。若 preview 顯示 stop 被裁切，先接受較保守裁切；不要用加大
   CMP180 EATT 的方式繞過。
5. 勾選 route、operator present 與最後 RF confirmation 後執行。
6. 每次結果先看 Valid Points、Max Pout、Max Compression、IP1dB／OP1dB 與 artifact
   metadata。`not_found` 代表掃描範圍內未達 1 dB 壓縮；`insufficient_points` 代表有效點
   不足，兩者都不能寫成 P1dB。

## 異常判讀

- 全部 INVALID 或畫面顯示 `No valid data`：不是正常 PA 結果。先查 raw response、
  reliability、frequency、expected power、baseband mode、routing 與 RF1.5 input range；
  不要重複跑 110 次 loopback 消耗時間。
- Gain 接近 0 dB：優先懷疑接線 bypass、DUT 未供電、參考面補償漏填或 PA 頻率超出範圍。
- Pout 一開始就很高：停止，確認 external attenuator 實體存在且數值填對。
- Gain 在低功率劇烈起伏：先用固定單點 repeats 檢查線材、DC 供電與熱穩定，不要直接拿來
  fit P1dB。
- 最後一點未達 1 dB compression：結果保持 `not_found`，報告中寫「本掃描範圍未觀察到
  P1dB」，不得外推。

## 報告最小欄位

結案報告至少放入 DUT ID、日期、操作者、fixture 圖、頻率、Start／Stop／Step、實體
attenuator、input/output cable loss、`dut_max_input_dbm`、固定 `RF1.5 +25 dBm` 上限、artifact
資料夾、有效點數、最大 Pout、最大 compression、P1dB 狀態、final RF state、measurement
state 與 error queue。若沒有新的 ADL5611 實機 artifact，只能寫「SOP 與軟體路徑完成」，
不能寫「ADL5611 PA/P1dB 已驗證」。
