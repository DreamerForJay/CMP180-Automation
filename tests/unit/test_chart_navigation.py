"""以正式 JavaScript 函式驗證資料視窗，不操作 RF。"""
import shutil
import subprocess
from pathlib import Path

import pytest


def test_zoom_pan_bounds_and_fixed_canvas():
    node = shutil.which("node")
    if not node:
        pytest.skip("需要 Node.js")
    source = Path("src/cmp180_evm/web/static/app.js").read_text(encoding="utf-8")
    geometry = source[source.index("const chartFrame="):source.index("function axisTickLabel(")]
    zoom = source[source.index("function zoomChartAt("):source.index("$('#chart').addEventListener('wheel'")]
    script = """
const assert=require('node:assert/strict');
const attributes={};
const svg={style:{},setAttribute:(key,value)=>attributes[key]=value};
const $=()=>svg;
"""+geometry+"""
const chartView={x:0,y:0,width:900,height:390};
"""+zoom+"""
const samples=Array.from({length:16},(_,i)=>({x:-80+i*5,y:30+i/100}));
chartDataWindow(-80,0,samples);
const minimum=chartZoomLimits.minWidth;
zoomChartAt(.5,1/1.2);
assert.ok(chartView.width<900);
assert.ok(Math.abs(chartView.x+chartView.width/2-450)<1e-8);
for(let i=0;i<100;i++)zoomChartAt(.95,1/1.2);
assert.equal(chartView.width,minimum);
for(const requested of [-1e8,1e8]){
 chartView.x=clampChartX(requested);
 assert.ok(chartView.x>=0&&chartView.x+chartView.width<=900);
 const window=chartDataWindow(-80,0,samples);
 assert.ok(samples.some(point=>point.x>=window.xmin&&point.x<=window.xmax));
 syncChartViewportSize();assert.equal(attributes.viewBox,'0 0 900 390');
}
for(let i=0;i<100;i++)zoomChartAt(.5,1.2);
assert.equal(chartView.width,900);assert.equal(chartView.x,0);
assert.ok(chartClipMarkup().includes('clip-path'));
"""
    subprocess.run([node,"-e",script],check=True,capture_output=True,text=True)
