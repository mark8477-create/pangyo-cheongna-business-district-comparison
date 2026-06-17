$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$WebRoot = Join-Path $ProjectRoot "web"
$TempRoot = Join-Path $ProjectRoot ".tmp"
$PidFile = Join-Path $TempRoot "web-server.pid"
$LogFile = Join-Path $TempRoot "web-server.log"
$ErrorLogFile = Join-Path $TempRoot "web-server-error.log"
$Python = "C:\Users\dydtm\AppData\Local\Python\bin\python.exe"
$Port = 8765
$Url = "http://127.0.0.1:$Port/"

New-Item -ItemType Directory -Force $TempRoot | Out-Null

if (Test-Path $PidFile) {
    $ExistingPid = Get-Content $PidFile -ErrorAction SilentlyContinue
    if ($ExistingPid -and (Get-Process -Id $ExistingPid -ErrorAction SilentlyContinue)) {
        try {
            $Response = Invoke-WebRequest $Url -UseBasicParsing -TimeoutSec 3
            if ($Response.StatusCode -eq 200) {
                Write-Output "Server already running: $Url (PID $ExistingPid)"
                exit 0
            }
        } catch {
            Stop-Process -Id $ExistingPid -Force -ErrorAction SilentlyContinue
        }
    }
}

$Process = Start-Process `
    -FilePath $Python `
    -ArgumentList "-m", "http.server", "$Port", "--bind", "0.0.0.0", "--directory", $WebRoot `
    -WindowStyle Hidden `
    -RedirectStandardOutput $LogFile `
    -RedirectStandardError $ErrorLogFile `
    -PassThru

$Process.Id | Set-Content $PidFile
Start-Sleep -Seconds 2
$Response = Invoke-WebRequest $Url -UseBasicParsing -TimeoutSec 5
Write-Output "Server started: $Url (PID $($Process.Id), HTTP $($Response.StatusCode))"
