<#
  physics-loop round 1: Claude + Codex build the lithic fracture physics, then an independent red team (Claude + Codex) must PASS.

  ใช้:   pwsh -File physics-loop/run-loop.ps1 [-MaxIterations 40] [-MaxHours 16] [-MaxTurnsPerIteration 100]
  หยุด:  สร้างไฟล์ physics-loop/STOP หรือกด Ctrl+C

  ตัวตัดสินคือ verify.ps1 ไม่ใช่ AI:
    exit 0 = เสร็จ (เทคนิคผ่าน + red team ทั้งสองฝ่าย PASS บน tree เดียวกัน)
    exit 3 = เทคนิคผ่าน แต่ยังไม่มี/ไม่ผ่าน red team ของ tree นี้ -> สคริปต์นี้เรียก red team ให้ (ครั้งเดียวต่อ tree)
    อื่น ๆ = ยังไม่เสร็จ
#>
param(
    [int]$MaxIterations = 40,
    [double]$MaxHours = 16,
    [int]$MaxTurnsPerIteration = 100
)

$ErrorActionPreference = 'Stop'
$Loop = $PSScriptRoot
$Root = Split-Path $Loop -Parent
Set-Location $Root

$AllowedTools = @(
    'Read', 'Edit', 'Write', 'Glob', 'Grep', 'WebSearch', 'WebFetch',
    'Bash(bash physics-loop/tools/codex.sh:*)',
    'Bash(CODEX_SANDBOX=read-only bash physics-loop/tools/codex.sh:*)',
    'Bash(git diff:*)', 'Bash(git status:*)', 'Bash(git log:*)', 'Bash(git show:*)', 'Bash(git rev-parse:*)',
    'Bash(pwsh -NoProfile -File physics-loop/verify.ps1:*)',
    'Bash(python:*)'
)
$RedTeamTools = @(
    'Read', 'Glob', 'Grep', 'WebSearch', 'WebFetch',
    'Bash(git diff:*)', 'Bash(git status:*)', 'Bash(git log:*)', 'Bash(git show:*)', 'Bash(git rev-parse:*)',
    'Bash(python:*)'
)

$KeyPaths = @('lithics', 'tests/lithics', 'data/lithics_validation', 'docs/physics_world')
$CommitPaths = $KeyPaths + @('worklog/2026-10-15-physics-loop-r1', 'worklog/INDEX.md', 'physics-loop')

# ไฟล์ที่ AI ห้ามแก้ ถ้าถูกแก้ลูปจะหยุดทันที
$Protected = @(
    'physics-loop/verify.ps1', 'physics-loop/GOAL.md', 'physics-loop/PROMPT.md', 'physics-loop/REDTEAM_PROMPT.md',
    'physics-loop/run-loop.ps1', 'physics-loop/budget.json'
)
foreach ($dir in 'physics-loop/tools', 'physics-loop/spec', 'world', 'agents', 'prototypes', 'data/external') {
    $Protected += @(Get-ChildItem $dir -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch '__pycache__' } |
        ForEach-Object { Resolve-Path -Relative $_.FullName })
}
$Protected += @(Get-ChildItem tests -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '__pycache__' -and $_.FullName -notmatch '[\\/]tests[\\/]lithics[\\/]' } |
    ForEach-Object { Resolve-Path -Relative $_.FullName })

$env:BASH_DEFAULT_TIMEOUT_MS = '1800000'
$env:BASH_MAX_TIMEOUT_MS = '1800000'

foreach ($cmd in 'claude', 'codex', 'git', 'python', 'bash') {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { throw "ไม่พบคำสั่ง '$cmd'" }
}

$Hashes = @{}
foreach ($f in $Protected) { $Hashes[$f] = (Get-FileHash $f).Hash }

New-Item -ItemType Directory -Force "$Loop/.loop", "$Loop/redteam" | Out-Null
$deadline = (Get-Date).AddHours($MaxHours)

function Get-RedTeamSnapshot {
    $h = @{}
    Get-ChildItem "$Loop/redteam" -File -ErrorAction SilentlyContinue | ForEach-Object { $h[$_.Name] = (Get-FileHash $_.FullName).Hash }
    return $h
}

function Assert-Untouched([hashtable]$RtBefore) {
    foreach ($f in $Protected) {
        if (-not (Test-Path $f) -or (Get-FileHash $f).Hash -ne $Hashes[$f]) {
            throw "ไฟล์ที่ห้ามแก้ถูกแก้: $f — หยุดลูป (ดูด้วย git diff)"
        }
    }
    $now = Get-RedTeamSnapshot
    if ($now.Count -ne $RtBefore.Count) { throw 'ไฟล์ใน physics-loop/redteam/ ถูกเพิ่มหรือลบโดย AI — หยุดลูป' }
    foreach ($k in $now.Keys) {
        if ($RtBefore[$k] -ne $now[$k]) { throw "ไฟล์ red team ถูกแก้โดย AI: $k — หยุดลูป" }
    }
}

function Invoke-Verify {
    $out = & pwsh -NoProfile -File "$Loop/verify.ps1" 2>&1 | Out-String
    $code = $LASTEXITCODE
    "exit=$code  ($(Get-Date -Format s))`n$out" | Set-Content "$Loop/.loop/last-verify.txt" -Encoding utf8
    return $code
}

function Save-Commit([string]$Message) {
    $paths = @($CommitPaths | Where-Object { Test-Path $_ })
    git add -- @paths
    git commit -qm $Message --allow-empty
}

function Add-ClaudeUsage($raw, [string]$label) {
    try {
        $res = ($raw | Out-String) | ConvertFrom-Json
        $u = $res.usage
        $tokens = [int64]$u.input_tokens + [int64]$u.output_tokens + [int64]$u.cache_creation_input_tokens
        & python physics-loop/tools/budget.py add claude $tokens
        Write-Host ("Claude {0}: {1:N0} tokens, `${2:N2}" -f $label, $tokens, $res.total_cost_usd)
        return $res.result
    } catch {
        Write-Host "อ่านผล JSON ของ Claude ไม่ได้ ($label)" -ForegroundColor Yellow
        return ($raw | Out-String)
    }
}

function Restore-KeyPaths {
    # red team ต้องไม่แก้ไฟล์: ย้อนทุกอย่างใน key paths กลับไปเป็นสถานะที่ commit ไว้
    $dirty = git status --porcelain -- @KeyPaths
    if ($dirty) {
        Write-Host "red team แก้ไฟล์ — ย้อนกลับ:`n$dirty" -ForegroundColor Yellow
        git checkout -- @KeyPaths
        git clean -fdq -- @KeyPaths
    }
}

function Invoke-RedTeam([string]$Key) {
    $prompt = Get-Content "$Loop/REDTEAM_PROMPT.md" -Raw
    $header = "# red team key $Key  commit $(git rev-parse HEAD)  $(Get-Date -Format s)`n`n"

    $cf = "$Loop/redteam/$Key-claude.md"
    if (-not (Test-Path $cf)) {
        Write-Host "--- red team: Claude (key $Key) ---" -ForegroundColor Magenta
        $raw = $prompt | claude -p --output-format json --max-turns 80 --allowedTools @RedTeamTools
        $text = Add-ClaudeUsage $raw 'red team'
        ($header + $text) | Set-Content $cf -Encoding utf8
        Restore-KeyPaths
    }

    $xf = "$Loop/redteam/$Key-codex.md"
    if (-not (Test-Path $xf)) {
        Write-Host "--- red team: Codex (key $Key) ---" -ForegroundColor Magenta
        $text = & bash physics-loop/tools/codex.sh $prompt 2>&1 | Out-String
        ($header + $text) | Set-Content $xf -Encoding utf8
        Restore-KeyPaths
    }
    Save-Commit "physics-loop: red team $Key"
}

function Test-Done {
    $code = Invoke-Verify
    Write-Host "verify exit=$code"
    if ($code -eq 3) {
        $key = (Get-Content "$Loop/.loop/verify_status.json" -Raw | ConvertFrom-Json).redteam_key
        $haveBoth = (Test-Path "$Loop/redteam/$key-claude.md") -and (Test-Path "$Loop/redteam/$key-codex.md")
        if (-not $haveBoth) {
            Invoke-RedTeam $key
            $code = Invoke-Verify
            Write-Host "verify หลัง red team exit=$code"
        } else {
            Write-Host "red team ของ tree $key ไม่ผ่าน — รอบถัดไปต้องแก้ blocking findings" -ForegroundColor Yellow
        }
    }
    return ($code -eq 0)
}

if (Test-Done) { Write-Host 'verify ผ่านอยู่แล้ว ไม่มีอะไรต้องทำ' -ForegroundColor Green; exit 0 }

for ($i = 1; $i -le $MaxIterations; $i++) {
    if (Test-Path "$Loop/STOP") {
        Write-Host 'พบไฟล์ physics-loop/STOP — หยุดลูป' -ForegroundColor Yellow
        Get-Content "$Loop/STOP" -ErrorAction SilentlyContinue
        exit 2
    }
    if ((Get-Date) -gt $deadline) { Write-Host 'ครบเวลาที่กำหนด — หยุดลูป'; exit 2 }

    Write-Host "`n=== รอบที่ $i / $MaxIterations   $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" -ForegroundColor Cyan
    & python physics-loop/tools/budget.py
    $rt = Get-RedTeamSnapshot
    $log = "$Loop/.loop/iter-{0:D3}.json" -f $i
    $raw = Get-Content "$Loop/PROMPT.md" -Raw |
        claude -p --output-format json --permission-mode acceptEdits --max-turns $MaxTurnsPerIteration --allowedTools @AllowedTools
    $raw | Set-Content $log -Encoding utf8
    Write-Host (Add-ClaudeUsage $raw "รอบ $i")

    Assert-Untouched $rt
    Save-Commit "physics-loop: iteration $i"

    if (Test-Done) { Write-Host "สำเร็จ — ฟิสิกส์ผ่าน verify และ red team ในรอบที่ $i" -ForegroundColor Green; exit 0 }
}

Write-Host 'ครบจำนวนรอบแต่ยังไม่ผ่าน — ดู physics-loop/progress.md, physics-loop/redteam/ และ physics-loop/.loop/' -ForegroundColor Yellow
exit 1
