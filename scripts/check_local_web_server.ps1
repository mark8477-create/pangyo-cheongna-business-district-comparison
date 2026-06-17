$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PidFile = Join-Path $ProjectRoot ".tmp\web-server.pid"
$Url = "http://127.0.0.1:8765/"

$ServerPid = if (Test-Path $PidFile) { Get-Content $PidFile -ErrorAction SilentlyContinue } else { $null }
$ProcessAlive = [bool]($ServerPid -and (Get-Process -Id $ServerPid -ErrorAction SilentlyContinue))

try {
    $Response = Invoke-WebRequest $Url -UseBasicParsing -TimeoutSec 5
    $HttpStatus = $Response.StatusCode
    $Bytes = $Response.RawContentLength
} catch {
    $HttpStatus = 0
    $Bytes = 0
}

[pscustomobject]@{
    Url = $Url
    Pid = $ServerPid
    ProcessAlive = $ProcessAlive
    HttpStatus = $HttpStatus
    Bytes = $Bytes
}
