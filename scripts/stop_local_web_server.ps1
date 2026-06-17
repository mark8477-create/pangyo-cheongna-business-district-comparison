$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PidFile = Join-Path $ProjectRoot ".tmp\web-server.pid"

if (-not (Test-Path $PidFile)) {
    Write-Output "No PID file found."
    exit 0
}

$ServerPid = Get-Content $PidFile -ErrorAction SilentlyContinue
if ($ServerPid) {
    Stop-Process -Id $ServerPid -Force -ErrorAction SilentlyContinue
}
Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
Write-Output "Local web server stopped."
