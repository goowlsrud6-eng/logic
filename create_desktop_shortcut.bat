@echo off
setlocal
cd /d "%~dp0"
set "SCRIPT=%cd%\run_windows_cmd.bat"
set "SHORTCUT=%USERPROFILE%\Desktop\특별재고 대시보드.lnk"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%SCRIPT%'; $Shortcut.WorkingDirectory = '%cd%'; $Shortcut.IconLocation = 'shell32.dll,220'; $Shortcut.Save()"

echo 바탕화면에 '특별재고 대시보드' 바로가기를 만들었습니다.
echo 이제 바탕화면 바로가기를 더블클릭해서 실행하세요.
pause
