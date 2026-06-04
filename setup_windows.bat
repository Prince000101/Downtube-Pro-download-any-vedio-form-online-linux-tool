@echo off
chcp 65001 >nul
title DownTube — Windows Setup
echo ============================================
echo   DownTube — Windows Setup
echo ============================================
echo.

REM --- Check Python ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed.
    echo Download it from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
echo [OK] Python found

REM --- Check Git ---
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed.
    echo Download from: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo [OK] Git found

REM --- Install dependencies ---
echo.
echo Installing Python dependencies...
pip install PyQt5 pyinstaller
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [OK] Dependencies installed

REM --- Build standalone executable ---
echo.
echo Building standalone executable (this may take a minute)...
pyinstaller --onefile --windowed --name "DownTube.exe" ^
    --add-data "core;core" ^
    --add-data "ui;ui" ^
    --add-data "theme;theme" ^
    --add-data "icon.png;." ^
    --hidden-import core.engine ^
    --hidden-import core.queue ^
    --hidden-import core.history ^
    --hidden-import ui.main_window ^
    --hidden-import ui.download_page ^
    --hidden-import ui.history_page ^
    --hidden-import ui.settings_page ^
    --hidden-import ui.widgets ^
    --hidden-import ui.format_dialog ^
    --hidden-import ui.search_dialog ^
    --hidden-import theme.manager ^
    --hidden-import theme.colors ^
    --hidden-import theme.icons main.py
if %errorlevel% neq 0 (
    echo [ERROR] Build failed.
    pause
    exit /b 1
)
echo [OK] Executable built

REM --- Copy to desktop ---
echo.
set DESKTOP=%USERPROFILE%\Desktop
copy /Y "dist\DownTube.exe" "%DESKTOP%\DownTube.exe" >nul
echo [OK] Copied to desktop: %DESKTOP%\DownTube.exe

echo.
echo ============================================
echo   Setup complete!
echo.
echo   Double-click DownTube.exe on your desktop
echo   to run the app.
echo.
echo   Note: Place yt-dlp.exe next to the
echo   executable for full functionality.
echo ============================================
pause
