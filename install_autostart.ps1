# PowerShell Script to automatically start Sentinel on Windows Startup
$WshShell = New-Object -ComObject WScript.Shell
$StartupFolder = [Environment]::GetFolderPath("Startup")
$ShortcutPath = Join-Path $StartupFolder "GitHubStreakSentinel.lnk"
$TargetVbs = Join-Path (Get-Location) "start_sentinel_silent.vbs"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = "`"$TargetVbs`""
$Shortcut.WorkingDirectory = (Get-Location).Path
$Shortcut.Description = "GitHub Streak Sentinel Background Runner"
$Shortcut.Save()

Write-Host "Sentinel berhasil dipasang ke Windows Startup!" -ForegroundColor Green
Write-Host "Shortcut dibuat di: $ShortcutPath" -ForegroundColor Cyan
Write-Host "Sekarang Sentinel akan otomatis aktif di background setiap kali Windows menyala." -ForegroundColor Yellow
