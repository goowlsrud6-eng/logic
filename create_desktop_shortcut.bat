@echo off
setlocal
cd /d "%~dp0"
set "SCRIPT=%cd%\run_windows_cmd.bat"
set "SHORTCUT=%USERPROFILE%\Desktop\Special Stock Dashboard.lnk"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%SCRIPT%'; $Shortcut.WorkingDirectory = '%cd%'; $Shortcut.IconLocation = 'shell32.dll,220'; $Shortcut.Save()"

echo Created a desktop shortcut: Special Stock Dashboard
echo Double-click the shortcut on your Desktop to start the dashboard.
pause
