"""執行正式 Loopback JavaScript，確認缺值不會偽裝成有效 RF 數據。"""

import shutil
import subprocess
from pathlib import Path

import pytest


def test_loopback_missing_data_and_invalid_diagnostics():
    node = shutil.which("node")
    if not node:
        pytest.skip("需要 Node.js")
    source = Path("src/cmp180_evm/web/static/loopback.js").read_text(encoding="utf-8")
    functions = source[source.index("const LOOPBACK_METRIC_FIELDS"):source.index("function renderLoopbackBatchResult")]
    script = """
const assert = require('node:assert/strict');
const elements = {};
const document = {querySelector: id => elements[id] ||= {}};
const formatMeasured = value => value ?? '—';
const escapeHtml = value => value;
const metric = (label, value) => `${label}: ${value}`;
""" + functions + """
for (const value of [null, undefined, '', ' ', 'INV']) {
 const html = loopbackSvg([{evm_all_db: value}], 'evm_all_db', 'EVM');
 assert.ok(!html.includes('<circle'));
 assert.ok(html.includes('fill="#aebed0"'));
}
assert.ok(loopbackSvg([{evm_all_db: 0, valid: true}], 'evm_all_db', 'EVM').includes('<circle'));
assert.ok(loopbackSvg([], 'evm_all_db', 'EVM').includes('等待'));
const points = [{point_index:0, valid:false, invalid_reasons:['INVALID_RELIABILITY'], evm_all_db:null}];
renderLoopbackLive(points);
assert.ok(elements['#loopbackCharts'].innerHTML.includes('無法判定 RF 效能'));
const empty = {mean:null, std_dev:null};
renderLoopbackResult({points, loopback:{analysis:{statistics:{evm_all_carriers_db:empty, burst_power_dbm:empty, frequency_error_hz:empty}, outliers:[]}}});
assert.ok(elements['#loopbackMetrics'].innerHTML.includes('Avg EVM: — dB'));
assert.ok(!elements['#loopbackMetrics'].innerHTML.includes('0.000'));
"""
    subprocess.run([node, "-e", script], check=True, capture_output=True, text=True)
