<#
    download_pdfs.ps1
    -----------------
    ดึง PDF ของเปเปอร์เรื่อง "อายุขัยมนุษย์" เข้ามาไว้ในโฟลเดอร์นี้

    ทำไมต้องรันเอง: สภาพแวดล้อม sandbox ที่ Claude รันอยู่บล็อกการดาวน์โหลดไฟล์ binary
    (endpoint ที่เสิร์ฟ PDF โดน block/robot-page) แต่เครื่องคุณเน็ตปกติ โหลดได้

    วิธีใช้ (PowerShell):
        cd C:\artificial-evolution\papers\longevity
        ./download_pdfs.ps1

    - ฉบับ Open Access (#2,#6,#9,#11) : โหลดอัตโนมัติผ่าน NCBI PMC OA service (ถูกกฎหมาย)
    - ฉบับ free-to-read (#7,#8)        : ลองโหลดตรง (อาจติด Cloudflare ของ publisher)
    - ฉบับ paywall (#1,#3,#4,#5,#10,#12,#13) : สคริปต์จะพิมพ์ลิงก์ให้เปิดโหลดเองผ่าน browser
#>

$ErrorActionPreference = 'Stop'
$UA  = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
$dir = $PSScriptRoot
if (-not $dir) { $dir = (Get-Location).Path }
Set-Location $dir
Write-Host "โฟลเดอร์ปลายทาง: $dir`n" -ForegroundColor Cyan

function Test-Pdf($path) {
    if (-not (Test-Path $path)) { return $false }
    $fs = [System.IO.File]::OpenRead($path)
    try { $b = New-Object byte[] 4; [void]$fs.Read($b,0,4); return ([System.Text.Encoding]::ASCII.GetString($b) -eq '%PDF') }
    finally { $fs.Close() }
}

# ---- 1) Free / Open-Access papers: try several mirrors per paper ------------
# วิธีที่เวิร์กบ่อยสุดบนเน็ตปกติคือ europepmc "render" endpoint แล้วค่อย fallback
# ไป PMC /pdf/ และหน้า publisher โดยตรง สคริปต์จะลองทีละ URL จนได้ไฟล์ %PDF จริง
$papers = @(
    @{ out='02_Stenholm2016_lifestyle_diseasefree_LE.pdf'; urls=@(
        'https://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC6937009&blobtype=pdf'
        'https://pmc.ncbi.nlm.nih.gov/articles/PMC6937009/pdf/' ) }
    @{ out='05_Yuan2023_growth_bodysize_aging_tradeoffs.pdf'; urls=@(
        'https://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC10792675&blobtype=pdf'
        'https://pmc.ncbi.nlm.nih.gov/articles/PMC10792675/pdf/' ) }
    @{ out='09_Kitazoe2017_mitochondrial_longevity.pdf'; urls=@(
        'https://royalsocietypublishing.org/doi/pdf/10.1098/rsob.170083'
        'https://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC5666079&blobtype=pdf'
        'https://pmc.ncbi.nlm.nih.gov/articles/PMC5666079/pdf/' ) }
    @{ out='11_CALERIE2023_pace_of_aging_abstract.pdf'; urls=@(
        'https://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC10737863&blobtype=pdf'
        'https://pmc.ncbi.nlm.nih.gov/articles/PMC10737863/pdf/' ) }
    @{ out='07_Speakman2005_bodysize_metabolism_lifespan.pdf'; urls=@(
        'https://journals.biologists.com/jeb/article-pdf/208/9/1717/1241442/1717.pdf' ) }
    @{ out='08_Hulbert2007_metabolic_rate_membrane_lifespan.pdf'; urls=@(
        'https://journals.physiology.org/doi/pdf/10.1152/physrev.00047.2006' ) }
)

$ok = @(); $fail = @()
foreach ($p in $papers) {
    $dest = Join-Path $dir $p.out
    $got  = $false
    foreach ($u in $p.urls) {
        try {
            Invoke-WebRequest -Uri $u -OutFile $dest -UserAgent $UA -MaximumRedirection 5 -TimeoutSec 120
            if (Test-Pdf $dest) { $got = $true; break }
            else { Remove-Item $dest -Force -ErrorAction SilentlyContinue }
        } catch { }
    }
    if ($got) { $ok += $p.out; Write-Host "OK   -> $($p.out)" -ForegroundColor Green }
    else      { $fail += $p.out; Write-Host "FAIL -> $($p.out) (เปิดลิงก์โหลดเองใน browser)" -ForegroundColor Red }
}

# ---- 3) Paywalled: print links to open manually ----------------------------
$manual = @(
    'เปิดใน browser แล้วโหลดเอง (paywall / ต้องมีสิทธิ์เข้าถึง):'
    ' #1  Li 2018 (Circulation)      -> https://pmc.ncbi.nlm.nih.gov/articles/PMC6207481/'
    ' #3  Herskind 1996 (Hum Genet)  -> https://pubmed.ncbi.nlm.nih.gov/8786073/'
    ' #4  Heritability 2025 (Science)-> https://www.science.org/doi/10.1126/science.adz1187'
    ' #5  Kirkwood 1977 (Nature)     -> https://www.nature.com/articles/270301a0'
    ' #10 Ravussin 2015 (CALERIE)    -> https://pmc.ncbi.nlm.nih.gov/articles/PMC4841173/'
    ' #12 Lopez-Otin 2013 (Cell)     -> https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3836174/'
    ' #13 Lopez-Otin 2023 (Cell)     -> https://pubmed.ncbi.nlm.nih.gov/36599349/'
)

Write-Host "`n==================== สรุป ====================" -ForegroundColor Cyan
Write-Host ("โหลดสำเร็จ {0} ไฟล์:" -f $ok.Count) -ForegroundColor Green
$ok | ForEach-Object { Write-Host "   ✓ $_" }
if ($fail.Count) { Write-Host ("โหลดไม่สำเร็จ {0}:" -f $fail.Count) -ForegroundColor Red; $fail | ForEach-Object { Write-Host "   ✗ $_" } }
Write-Host ""
$manual | ForEach-Object { Write-Host $_ -ForegroundColor DarkYellow }
