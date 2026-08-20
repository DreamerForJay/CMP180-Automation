# 提交前檢查（docs/development-workflow.md）：一次跑完 pytest、config validation、
# git diff --check，並加上 ruff/mypy（非阻斷，先觀察雜訊量，不擋提交）。

$ErrorActionPreference = "Stop"
$python = ".\.venv\Scripts\python.exe"

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

Write-Host "== ruff (non-blocking) ==" -ForegroundColor Yellow
& $python -m ruff check .

Write-Host "== mypy (non-blocking) ==" -ForegroundColor Yellow
& $python -m mypy src

Write-Host "All required checks passed. Review any ruff/mypy findings above." -ForegroundColor Green
