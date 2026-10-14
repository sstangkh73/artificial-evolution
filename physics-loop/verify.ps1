# ตัวตัดสินของ physics-loop รอบ 1: exit 0 = เสร็จ, 3 = เทคนิคผ่านแต่ยังรอ/ไม่ผ่าน red team, อื่น ๆ = ยังไม่เสร็จ
# AI ห้ามแก้ไฟล์นี้และ tools/ (ถ้าถูกแก้ ลูปจะหยุด)
param([switch]$Quick)
$env:PYTHONIOENCODING = 'utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Set-Location (Split-Path $PSScriptRoot -Parent)
if ($Quick) { python physics-loop/tools/verify_physics.py --quick } else { python physics-loop/tools/verify_physics.py }
exit $LASTEXITCODE
