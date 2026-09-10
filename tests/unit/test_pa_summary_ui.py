"""PA 摘要以合成資料驗證；不連線儀器。"""
import shutil
import subprocess
from pathlib import Path

import pytest


def test_demo_pa_points_are_not_hidden_by_measurement_family():
    source = Path("src/cmp180_evm/web/static/app.js").read_text(encoding="utf-8")

    # Demo 沒有 GPRF measurement_family，但仍須依 Pin／Pout／Gain 欄位顯示 P1dB 摘要。
    assert "const hasPa=source.some(point=>point&&Object.hasOwn(point,'gain_db'));" in source
    assert "const hasPa=isGprf&&" not in source


def test_pa_summary_reference_planes_and_missing_values():
    node = shutil.which("node")
    if not node:
        pytest.skip("需要 Node.js 執行前端函式")
    source = Path("src/cmp180_evm/web/static/app.js").read_text(encoding="utf-8")
    functions = source[source.index("function p1dbMetrics("):source.index("function render(data)")]
    numeric = source[source.index("function finiteNumber("):source.index("function finiteNumber(") + source[source.index("function finiteNumber("):].index("\n")]
    # 直接執行正式函式；INVALID 刻意放入極端值，避免錯把輸入掃描跨度當增益漣波。
    script = """
const assert=require('node:assert/strict');
const metric=(label,value)=>label+':'+value+'|';
""" + numeric + functions + """
const points=[
 {valid:true,pin_dbm:-80,pout_dbm:-49.9,gain_db:30.1},
 {valid:true,pin_dbm:-5,pout_dbm:25.55,gain_db:30.55},
 {valid:false,pin_dbm:0,pout_dbm:100,gain_db:100}];
const freq=paSummaryMetrics(points,'frequency',null);
assert.ok(freq.includes('Gain Peak-to-Peak Ripple:0.450 dB'));
assert.ok(freq.includes('Gain Std Dev:0.225 dB'));
assert.ok(freq.includes('Valid Points:2/3'));
const power=paSummaryMetrics(points,'power',{status:'not_found',small_signal_gain_db:30.3,max_compression_db:0.2});
assert.ok(power.includes('Max Pout:25.55 dBm'));
assert.ok(power.includes('IP1dB:not_found'));
assert.ok(!power.includes('Ripple'));
assert.ok(!power.includes('Average Power'));
const missing=p1dbMetrics({status:'insufficient_points',small_signal_gain_db:null});
assert.ok(missing.includes('Small-signal Gain:—'));
assert.ok(missing.includes('IP1dB:insufficient_points'));
assert.ok(paSummaryMetrics([], 'frequency', null).includes('Mean Gain:—'));
assert.ok(p1dbMetrics({status:'found',ip1db_dbm:0,op1db_dbm:29}).includes('IP1dB:0.00 dBm'));
"""
    subprocess.run([node, "-e", script], check=True, capture_output=True, text=True)
