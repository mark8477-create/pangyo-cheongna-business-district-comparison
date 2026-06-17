$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$StartScript = Join-Path $PSScriptRoot "start_local_web_server.ps1"
$TaskName = "OfficeDistrictComparisonLocalWeb"
$PowerShell = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$Action = New-ScheduledTaskAction `
    -Execute $PowerShell `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$StartScript`""
$Trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 5 `
    -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Starts the office district comparison static web server at login." `
    -Force | Out-Null

Write-Output "Startup task registered: $TaskName"
