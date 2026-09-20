# 由單一來源 docs/manual/cmp180-user-manual.html 重新產生 PDF 與 DOCX 版使用手冊。
# PDF 以本機 Chrome／Edge 的 headless 列印產生；DOCX 由純標準函式庫的轉換器產生。
# 這個腳本不連線儀器、不送出 SCPI、不啟用 RF。

[CmdletBinding()]
param(
    [string]$Source = "docs/manual/cmp180-user-manual.html"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$src = Resolve-Path $Source
$stem = [System.IO.Path]::GetFileNameWithoutExtension($src)
$dir = Split-Path -Parent $src
$pdf = Join-Path $dir "$stem.pdf"
$docx = Join-Path $dir "$stem.docx"

# 列印版把 FAQ 的 <details> 全部展開，否則收合內容不會出現在 PDF。
$printHtml = Join-Path ([System.IO.Path]::GetTempPath()) "$stem.print.html"
(Get-Content -LiteralPath $src -Raw -Encoding UTF8) `
    -replace '<details class="faq">', '<details class="faq" open>' |
    Out-File -LiteralPath $printHtml -Encoding utf8

$browsers = @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe"
)
$browser = $browsers | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $browser) { throw "找不到 Chrome 或 Edge，無法產生 PDF。" }

& $browser --headless --disable-gpu --no-pdf-header-footer `
    --run-all-compositor-stages-before-draw --virtual-time-budget=12000 `
    "--print-to-pdf=$pdf" "file:///$printHtml" | Out-Null
Remove-Item -LiteralPath $printHtml -Force

$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }
& $python "scripts/build_manual_docx.py" $src $docx

Write-Output "HTML : $src"
Write-Output "PDF  : $pdf"
Write-Output "DOCX : $docx"
