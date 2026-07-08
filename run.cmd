@echo off
setlocal
cd /d "%~dp0"
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONPATH=%CD%\src;%PYTHONPATH%"

py -3 --version >nul 2>&1
if not errorlevel 1 (
  py -3 -m ps5_to_xbox %*
  exit /b %ERRORLEVEL%
)

python --version >nul 2>&1
if not errorlevel 1 (
  python -m ps5_to_xbox %*
  exit /b %ERRORLEVEL%
)

echo Python was not found. Run install.cmd first.
exit /b 1
