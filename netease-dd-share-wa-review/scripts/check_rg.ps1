$ErrorActionPreference = 'Continue'

Write-Host '--- rg command resolution ---'
$commands = Get-Command rg -All -ErrorAction SilentlyContinue
if (-not $commands) {
  Write-Host 'rg not found in PATH'
} else {
  $commands | Format-List CommandType,Source,Path
}

Write-Host '--- rg version ---'
try {
  rg --version
  $versionExit = $LASTEXITCODE
} catch {
  Write-Host $_.Exception.Message
  $versionExit = 1
}

Write-Host '--- rg file sample ---'
try {
  rg --files | Select-Object -First 10
  $filesExit = $LASTEXITCODE
} catch {
  Write-Host $_.Exception.Message
  $filesExit = 1
}

$first = @($commands | Select-Object -First 1)[0]
$firstPath = if ($first) { [string]$first.Source } else { '' }
$usesWindowsApps = $firstPath -like '*\WindowsApps\OpenAI.Codex_*\rg*'
$healthy = ($versionExit -eq 0) -and (-not $usesWindowsApps)

Write-Host '--- verdict ---'
if ($healthy) {
  Write-Host "OK: rg is usable from $firstPath"
  exit 0
}

Write-Host 'WARN: rg is not healthy. Use PowerShell fallback from references/rg-maintenance.md.'
if ($usesWindowsApps) {
  Write-Host 'Reason: PATH resolves rg to the Codex WindowsApps packaged binary first.'
}
if ($versionExit -ne 0) {
  Write-Host "Reason: rg --version failed with exit code $versionExit."
}
if ($filesExit -ne 0) {
  Write-Host "Reason: rg --files failed with exit code $filesExit."
}
exit 1
