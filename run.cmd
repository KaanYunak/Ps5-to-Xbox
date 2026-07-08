@echo off
setlocal
cd /d "%~dp0"
set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONPATH=%CD%\src;%PYTHONPATH%"

call "%~dp0find-python.cmd"
if not errorlevel 1 (
  %PYTHON_CMD% -m ps5_to_xbox %*
  exit /b %ERRORLEVEL%
)

echo Python was not found. Run install.cmd first.
exit /b 1
