# Windows Credential Manager helper.
# This script intentionally does not print secrets. It only checks whether the target exists.
param([string]$Target = 'df-cms-review/tongyifeng')
$cmd = Get-Command cmdkey.exe -ErrorAction SilentlyContinue
if (-not $cmd) { Write-Output 'cmdkey_missing'; exit 2 }
$list = cmdkey.exe /list:$Target 2>$null
if ($LASTEXITCODE -eq 0 -and ($list -join "`n") -match [regex]::Escape($Target)) { Write-Output 'credential_exists'; exit 0 }
Write-Output 'credential_missing'
exit 1
