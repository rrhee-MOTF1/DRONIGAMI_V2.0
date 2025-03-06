@echo off

set "pythonVersion=3.13.1"
set "pythonDownloadUrl=https://www.python.org/ftp/python/%pythonVersion%/python-%pythonVersion%-amd64.exe"
set "installDir=C:\Python"
set "batchFilePath=%CD%\dronigami.bat"
set "desktopPath=%USERPROFILE%\Desktop"
set "shortcutName=DRONIGAMI.lnk"
set "iconPath=%CD%\shortcut_icon.ico"

python --version 2>nul | findstr /i "%pythonVersion%" >nul
if %errorlevel% equ 0 (
    echo Python %pythonVersion% is already installed.
    goto SkipInstall
)

echo Python %pythonVersion% is not installed. Installing...
powershell -Command "Invoke-WebRequest -Uri %pythonDownloadUrl% -OutFile %TEMP%\python-installer.exe"

"%TEMP%\python-installer.exe" /quiet InstallAllUsers=1 PrependPath=1 DefaultCustomInstall=1 DefaultPath=%installDir% /wait

del "%TEMP%\python-installer.exe" /f /q

:SkipInstall
python -m venv DRONIGAMI_v1.0.0_ENV

call DRONIGAMI_v1.0.0_ENV\Scripts\activate.bat

echo Environment activated.

pip install -r requirements.txt

echo Requirements installed.

echo Creating shortcut on the Desktop...

powershell -Command ^
    $WshShell = New-Object -ComObject WScript.Shell; ^
    $Shortcut = $WshShell.CreateShortcut('%desktopPath%\%shortcutName%'); ^
    $Shortcut.TargetPath = '%batchFilePath%'; ^
    $Shortcut.WorkingDirectory = '%CD%'; ^
    $Shortcut.IconLocation = '%iconPath%'; ^
    $Shortcut.Save()

echo Shortcut created.

pause
