# 提交前檢查（docs/development-workflow.md）：一次跑完 pytest、config validation、
# git diff --check 與 Ruff；mypy 仍單獨顯示既有型別債而不擋提交。

$ErrorActionPreference = "Stop"
# OneDrive 非 ASCII 路徑可能讓某些 venv launcher 失效；允許 CI／開發者指定已驗證的 Python。
$python = if ($env:CMP180_PYTHON) { $env:CMP180_PYTHON } else { ".\.venv\Scripts\python.exe" }

New-Item -ItemType Directory -Force output | Out-Null

Write-Host "== pytest ==" -ForegroundColor Cyan
& $python -m pytest -q --basetemp=output\pytest-tmp
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "== validate-config (instrument) ==" -ForegroundColor Cyan
& $python -m cmp180_evm validate-config configs\instrument.example.yaml
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "== validate-config (wlan_baseline) ==" -ForegroundColor Cyan
& $python -m cmp180_evm validate-config configs\wlan_baseline.example.yaml
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "== git diff --check ==" -ForegroundColor Cyan
git diff --check
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "== ruff ==" -ForegroundColor Cyan
& $python -m ruff check .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "== mypy (non-blocking) ==" -ForegroundColor Yellow
& $python -m mypy src
if ($LASTEXITCODE -ne 0) {
    Write-Warning "mypy reported existing type debt; review the output above."
}

Write-Host "All required checks passed. Review any mypy findings above." -ForegroundColor Green
exit 0
