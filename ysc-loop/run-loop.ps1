<#
  YSC 2027 phase 3 loop: Claude and Codex as equal partners (adapted from auto-loop/)

  ใช้:     pwsh -File ysc-loop/run-loop.ps1 [-MaxIterations 20] [-MaxHours 6] [-MaxTurnsPerIteration 80]
  หยุด:    สร้างไฟล์ ysc-loop/STOP (ลูปจะหยุดก่อนเริ่มรอบถัดไป) หรือกด Ctrl+C

  หลักการ: ลูปนี้ (ไม่ใช่ AI) เป็นคนตัดสินว่าเสร็จหรือยัง โดยดูจาก verify.ps1 เท่านั้น
  ต่างจาก auto-loop/ ตรงที่ทำงานที่ root ของ repo, commit เฉพาะ path ของงานนี้ (ไม่ใช่ git add -A)
  และบันทึกโทเค็นของ Claude เพื่อให้ tools/budget.py เลือกได้ว่าใครนำในแต่ละรอบ
#>
param(
    [int]$MaxIterations = 20,
    [double]$MaxHours = 6,
    [int]$MaxTurnsPerIteration = 80
)

$ErrorActionPreference = 'Stop'
$Loop = $PSScriptRoot
$Root = Split-Path $Loop -Parent
Set-Location $Root

# เครื่องมือที่ Claude ใช้ได้โดยไม่ต้องขออนุญาต
$AllowedTools = @(
    'Read', 'Edit', 'Write', 'Glob', 'Grep',
    'Bash(bash ysc-loop/tools/codex.sh:*)',
    'Bash(git diff:*)', 'Bash(git status:*)', 'Bash(git log:*)', 'Bash(git show:*)',
    'Bash(pwsh -NoProfile -File ysc-loop/verify.ps1)',
    'Bash(python:*)'
)

# path ที่ลูป commit ให้ (ห้ามใช้ git add -A เพราะ repo มีไฟล์ข้อมูลที่ยังไม่ track อยู่มาก)
$CommitPaths = @(
    'simulation', 'scripts', 'tests', 'docs/ysc2027_tool_discovery',
    'worklog/2026-10-14-ysc-phase3-loop', 'worklog/INDEX.md', 'ysc-loop'
)

# ไฟล์ที่ AI ห้ามแก้ ถ้าถูกแก้ลูปจะหยุดทันที (กันการโกงให้ verify ผ่าน)
$Protected = @(
    'ysc-loop/verify.ps1', 'ysc-loop/GOAL.md', 'ysc-loop/PROMPT.md', 'ysc-loop/run-loop.ps1', 'ysc-loop/budget.json'
)
foreach ($dir in 'ysc-loop/tools', 'world', 'agents', 'tests', 'data/tool_discovery_smoke_20261014') {
    $Protected += @(Get-ChildItem $dir -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch '__pycache__' } |
        ForEach-Object { Resolve-Path -Relative $_.FullName })
}

# ให้คำสั่ง Bash ของ AI (รวมถึงงานที่ส่งให้ Codex และการรัน pilot) รันได้นานสุด 30 นาทีต่อครั้ง
$env:BASH_DEFAULT_TIMEOUT_MS = '1800000'
$env:BASH_MAX_TIMEOUT_MS = '1800000'

foreach ($cmd in 'claude', 'codex', 'git', 'python') {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        throw "ไม่พบคำสั่ง '$cmd'"
    }
}

$Hashes = @{}
foreach ($f in $Protected) { $Hashes[$f] = (Get-FileHash $f).Hash }

New-Item -ItemType Directory -Force "$Loop/.loop" | Out-Null
$deadline = (Get-Date).AddHours($MaxHours)

function Invoke-Verify {
    $out = & pwsh -NoProfile -File "$Loop/verify.ps1" 2>&1 | Out-String
    $code = $LASTEXITCODE
    "exit=$code  ($(Get-Date -Format s))`n$out" | Set-Content "$Loop/.loop/last-verify.txt" -Encoding utf8
    return $code
}

function Save-Commit([string]$Message) {
    $paths = @($CommitPaths | Where-Object { Test-Path $_ })
    $paths += @(Get-ChildItem data -Directory -Filter 'tool_discovery_pilot_*' -ErrorAction SilentlyContinue |
        ForEach-Object { "data/$($_.Name)" })
    git add -- @paths
    git commit -qm $Message --allow-empty
}

if ((Invoke-Verify) -eq 0) { Write-Host 'verify ผ่านอยู่แล้ว ไม่มีอะไรต้องทำ'; exit 0 }

for ($i = 1; $i -le $MaxIterations; $i++) {
    if (Test-Path "$Loop/STOP") {
        Write-Host 'พบไฟล์ ysc-loop/STOP — หยุดลูป' -ForegroundColor Yellow
        Get-Content "$Loop/STOP" -ErrorAction SilentlyContinue
        exit 2
    }
    if ((Get-Date) -gt $deadline) { Write-Host 'ครบเวลาที่กำหนด — หยุดลูป'; exit 2 }

    Write-Host "`n=== รอบที่ $i / $MaxIterations   $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -ForegroundColor Cyan
    & python ysc-loop/tools/budget.py
    $log = "$Loop/.loop/iter-{0:D3}.json" -f $i
    $raw = Get-Content "$Loop/PROMPT.md" -Raw |
        claude -p --output-format json --permission-mode acceptEdits --max-turns $MaxTurnsPerIteration --allowedTools @AllowedTools
    $raw | Set-Content $log -Encoding utf8

    try {
        $res = ($raw | Out-String) | ConvertFrom-Json
        Write-Host $res.result
        $u = $res.usage
        $tokens = [int64]$u.input_tokens + [int64]$u.output_tokens + [int64]$u.cache_creation_input_tokens
        & python ysc-loop/tools/budget.py add claude $tokens
        Write-Host ("Claude รอบนี้: {0:N0} tokens, `${1:N2}" -f $tokens, $res.total_cost_usd)
    } catch {
        Write-Host "อ่านผล JSON ของ Claude ไม่ได้ (ดู $log)" -ForegroundColor Yellow
    }

    foreach ($f in $Protected) {
        if (-not (Test-Path $f) -or (Get-FileHash $f).Hash -ne $Hashes[$f]) {
            throw "ไฟล์ที่ห้ามแก้ถูกแก้: $f — หยุดลูป (ดูด้วย git diff)"
        }
    }

    Save-Commit "ysc-loop: iteration $i"

    $code = Invoke-Verify
    Write-Host "verify exit=$code"
    if ($code -eq 0) { Write-Host "สำเร็จ — verify ผ่านในรอบที่ $i" -ForegroundColor Green; exit 0 }
}

Write-Host 'ครบจำนวนรอบแต่ verify ยังไม่ผ่าน — ดู ysc-loop/progress.md และ ysc-loop/.loop/' -ForegroundColor Yellow
exit 1
