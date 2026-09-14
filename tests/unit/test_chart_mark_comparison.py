"""以正式 JavaScript 函式驗證標記對標 P1dB 與比較計算；純前端計算，不連線也不送 RF。"""
import shutil
import subprocess
from pathlib import Path

import pytest

APP_JS = Path("src/cmp180_evm/web/static/app.js")
INDEX_HTML = Path("src/cmp180_evm/web/static/index.html")
DESIGN_CSS = Path("src/cmp180_evm/web/static/design-system.css")


def _slice(source: str, start: str, end: str) -> str:
    return source[source.index(start):source.index(end)]


def test_mark_comparison_controls_and_styles_exist():
    html = INDEX_HTML.read_text(encoding="utf-8")
    css = DESIGN_CSS.read_text(encoding="utf-8")
    # 對標按鈕與比較面板必須同時存在，否則前端會在按下時找不到容器。
    assert 'id="chartMarkP1db"' in html
    assert 'id="chartMarkComparison"' in html
    for rule in (".chart-mark-guide", ".chart-mark-baseline", ".mark-compare-table"):
        assert rule in css


def test_align_to_p1db_and_comparison_rows():
    node = shutil.which("node")
    if not node:
        pytest.skip("需要 Node.js 執行前端函式")
    source = APP_JS.read_text(encoding="utf-8")
    numeric = _slice(source, "function finiteNumber(", "function normalizeHistoricalPoints(")
    metric_label = _slice(source, "function metricAxisLabel(", "const metricOrder=")
    marker = _slice(source, "function p1dbChartMarker(", "function p1dbMarkerMarkup(")
    marks = _slice(source, "function relabelChartMarks(", "function renderMarkComparison(")
    script = """
const assert=require('node:assert/strict');
let latestP1db=null;
const escapeHtml=value=>String(value);
""" + numeric + metric_label + marker + marks + """
// 對標線只能來自已求得的 P1dB：軸向、指標與 status 任一不符都必須拿不到標記。
const found={status:'found',ip1db_dbm:-12.5,op1db_dbm:12.25,target_gain_db:24.75};
assert.equal(p1dbChartMarker('frequency','gain_db',found),null);
assert.equal(p1dbChartMarker('power','evm_all_db',found),null);
assert.equal(p1dbChartMarker('power','gain_db',{status:'not_found',ip1db_dbm:-12.5}),null);
const gainMarker=p1dbChartMarker('power','gain_db',found);
assert.deepEqual([gainMarker.x,gainMarker.y],[-12.5,24.75]);
const poutMarker=p1dbChartMarker('power','pout_dbm',found);
assert.deepEqual([poutMarker.x,poutMarker.y],[-12.5,12.25]);
assert.ok(poutMarker.label.includes('OP1dB 12.25 dBm'));
// 全域 latestP1db 仍是單一 Run 的預設來源。
latestP1db=found;
assert.equal(p1dbChartMarker('power','pin_dbm').x,-12.5);

// 標記編號與上限：P1dB 基準只留一個，滿載時先丟最舊的實測標記。
let marks=[];
marks=addChartMark(marks,{x:-30,y:24.9,kind:'point',label:'M'});
marks=addChartMark(marks,{x:-20,y:24.6,kind:'point',label:'M'});
assert.deepEqual(marks.map(mark=>mark.label),['M1','M2']);
marks=addChartMark(marks,{x:-12.5,y:24.75,kind:'p1db',label:'P1dB'});
marks=addChartMark(marks,{x:-14,y:24.8,kind:'p1db',label:'P1dB'});
assert.equal(marks.filter(mark=>mark.kind==='p1db').length,1);
assert.equal(marks.at(-1).x,-14);
let trimmed=[{x:0,y:0,kind:'p1db',label:'P1dB'}];
for(let index=0;index<12;index++)trimmed=addChartMark(trimmed,{x:index,y:index,kind:'point',label:'M'},4);
assert.equal(trimmed.length,4);
assert.equal(trimmed.filter(mark=>mark.kind==='p1db').length,1);
assert.deepEqual(trimmed.filter(mark=>mark.kind!=='p1db').map(mark=>mark.label),['M1','M2','M3']);

// 比較基準優先取 P1dB；ΔX／ΔY 一律是「標記 − 基準」，基準自己沒有差值。
const rows=markComparisonRows([
 {x:-30,y:24.9,kind:'point',label:'M1'},
 {x:-12.5,y:24.75,kind:'p1db',label:'P1dB'},
 {x:-10,y:24.2,kind:'point',label:'M2'}]);
assert.deepEqual(rows.map(row=>row.baseline),[false,true,false]);
assert.equal(rows[1].dx,null);
assert.equal(rows[1].dy,null);
assert.ok(Math.abs(rows[0].dx+17.5)<1e-9);
assert.ok(Math.abs(rows[2].dx-2.5)<1e-9);
assert.ok(Math.abs(rows[2].dy+0.55)<1e-9);
assert.ok(rows.every(row=>row.baselineKind==='p1db'));
// 沒有 P1dB 標記時退回第一個標記當基準。
const fallback=markComparisonRows([{x:5,y:1,kind:'point',label:'M1'},{x:8,y:3,kind:'point',label:'M2'}]);
assert.equal(fallback[0].baseline,true);
assert.equal(fallback[1].dx,3);
assert.equal(fallback[0].baselineKind,'point');
assert.deepEqual(markComparisonRows([]),[]);

// 跨 Run P1dB 比較：少於兩個可用 Run 不輸出；not_found 與非功率掃描一律排除。
const traceA={name:'DUT A',color:'#18d7e5',axis:'power',p1db:{status:'found',ip1db_dbm:-12.5,op1db_dbm:12.25,target_gain_db:24.75}};
const traceB={name:'DUT B',color:'#f59e0b',axis:'power',p1db:{status:'found',ip1db_dbm:-11,op1db_dbm:13.5,target_gain_db:24.5}};
const traceC={name:'DUT C',color:'#a78bfa',axis:'power',p1db:{status:'not_found',ip1db_dbm:null}};
const traceD={name:'Freq',color:'#43c47a',axis:'frequency',p1db:{status:'found',ip1db_dbm:-9}};
assert.deepEqual(p1dbComparisonRows([traceA]),[]);
assert.deepEqual(p1dbComparisonRows([traceA,traceC,traceD]),[]);
const p1dbRows=p1dbComparisonRows([traceA,traceB,traceC,traceD]);
assert.deepEqual(p1dbRows.map(row=>row.name),['DUT A','DUT B']);
assert.equal(p1dbRows[0].delta_ip1db,null);
assert.ok(Math.abs(p1dbRows[1].delta_ip1db-1.5)<1e-9);
assert.ok(Math.abs(p1dbRows[1].delta_op1db-1.25)<1e-9);

// 單位與格式：dBm 相減必須顯示成 dB；頻率軸的 ΔX 換算成 MHz。
assert.equal(deltaUnitLabel('dBm'),'dB');
assert.equal(deltaUnitLabel('Hz'),'Hz');
assert.equal(metricUnitLabel('gain_db'),'dB');
assert.equal(metricUnitLabel('pout_dbm'),'dBm');
assert.equal(markAxisText('power',-12.345),'-12.35');
assert.equal(markAxisText('frequency',6105e6),'6105.000');
assert.equal(markAxisText('power',null),'—');
assert.equal(markDeltaText(null),'—');
assert.equal(markDeltaText(2.5,{axis:'power'}),'+2.500');
assert.equal(markDeltaText(-20e6,{axis:'frequency'}),'-20.000');
assert.equal(markDeltaText(1.234,{digits:2}),'+1.23');
"""
    subprocess.run([node, "-e", script], check=True, capture_output=True, text=True)
