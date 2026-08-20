@echo off
setlocal
chcp 65001 >nul
title Research-OS Easy Mode
cd /d "%~dp0"

set "PYTHONUTF8=1"
set "PYTHONDONTWRITEBYTECODE=1"
set "LOCAL_PYTHON=%~dp0.venv\Scripts\python.exe"
set "CODEX_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if exist "%LOCAL_PYTHON%" goto run_local
if exist "%CODEX_PYTHON%" goto run_codex
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 goto run_py
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 goto run_python

echo.
echo Python 3 was not found.
echo Install Python 3.12 or newer, then double-click this file again.
echo.
pause
exit /b 1

:run_local
"%LOCAL_PYTHON%" -B -m research_os_mvp easy --workspace "%~dp0workspace"
goto finish

:run_codex
"%CODEX_PYTHON%" -B -m research_os_mvp easy --workspace "%~dp0workspace"
goto finish

:run_py
py -3 -B -m research_os_mvp easy --workspace "%~dp0workspace"
goto finish

:run_python
python -B -m research_os_mvp easy --workspace "%~dp0workspace"

:finish
set "APP_EXIT=%ERRORLEVEL%"
echo.
if not "%APP_EXIT%"=="0" echo The app stopped with error code %APP_EXIT%.
echo Press any key to close this window.
pause >nul
exit /b %APP_EXIT%
