# Schedule-Sentinel.ps1
# Mendaftarkan skrip GitHub Streak Sentinel ke Windows Task Scheduler secara otomatis

$TaskName = "GitHubStreakSentinel"
$PythonPath = (Get-Command python).Source
$ScriptPath = "$PSScriptRoot\main.py"
$TriggerTime = "19:00"

Write-Host "Mendaftarkan Windows Task Scheduler: $TaskName pada jam $TriggerTime..." -ForegroundColor Cyan

$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument "`"$ScriptPath`"" -WorkingDirectory $PSScriptRoot
$Trigger = New-ScheduledTaskTrigger -Daily -At $TriggerTime
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Force | Out-Null

Write-Host "Task berhasil didaftarkan! Sentinel akan memeriksa streak setiap hari jam $TriggerTime." -ForegroundColor Green
Write-Host "Untuk menguji jalankan: Start-ScheduledTask -TaskName $TaskName" -ForegroundColor Yellow
