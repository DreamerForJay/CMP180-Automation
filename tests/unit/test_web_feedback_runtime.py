"""以離線 DOM 替身驗證回饋狀態，不連接儀器。"""

import shutil
import subprocess
from pathlib import Path

import pytest


def test_history_and_toast_state_transitions(tmp_path: Path) -> None:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js 未安裝，略過前端執行測試")
    source = Path("src/cmp180_evm/web/static/app.js").read_text(encoding="utf-8")
    history = source.split("const historyFeedback=", 1)[1].split("function renderRunHistory", 1)[0]
    toast = source.split("let toastTimer=", 1)[1].split("$('#dismissToast').onclick", 1)[0]
    # 使用可控時鐘檢查通知取代與錯誤保留，避免測試等待真實延遲。
    script = """
const assert=require('node:assert/strict');
let language='zh',runHistory=[],rows=[];
const translations={zh:{refreshHistory:'重新整理'},en:{refreshHistory:'Refresh'}};
const elements=new Map();
const $=key=>{if(!elements.has(key))elements.set(key,{dataset:{},classList:{add(){},remove(){}},setAttribute(k,v){this[k]=v}});return elements.get(key)};
const filteredRuns=()=>rows;
let timers=0,cleared=[];
const setTimeout=()=>++timers,clearTimeout=id=>cleared.push(id);
""" + "const historyFeedback=" + history + "let toastTimer=" + toast + """
historyFeedback.phase='loading';renderHistoryFeedback();
assert.equal($('#refreshHistoryButton').disabled,true);
assert.equal($('#historyEmpty').hidden,true);
historyFeedback.phase='error';historyFeedback.detail='HTTP 500';renderHistoryFeedback();
assert.equal($('#refreshHistoryButton').disabled,false);
assert.equal($('#historyEmpty').hidden,true);
assert.match($('#historyNotice').textContent,/HTTP 500/);
language='en';renderHistoryFeedback();
assert.match($('#historyNotice').textContent,/previous load/);
historyFeedback.phase='ready';renderHistoryFeedback();
assert.match($('#historyEmpty').textContent,/No measurement records yet/);
runHistory=[{}];renderHistoryFeedback();
assert.match($('#historyEmpty').textContent,/No records match/);
toast({zh:'已完成',en:'Done'});
assert.equal(timers,1);
toast('HTTP 500','error');
assert.equal(timers,1);
assert.ok(cleared.includes(1));
assert.equal($('#toastTitle').textContent,'Action not completed');
language='zh';renderToast();
assert.equal($('#toastTitle').textContent,'操作未完成');
assert.equal($('#toastMessage').textContent,'HTTP 500');
"""
    path = tmp_path / "feedback.cjs"
    path.write_text(script, encoding="utf-8")
    result = subprocess.run([node, str(path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
