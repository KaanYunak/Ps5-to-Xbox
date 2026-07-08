@echo off
setlocal
cd /d "%~dp0"

echo [ps5-to-xbox] Installer
echo.

call :find_python
if errorlevel 1 goto :no_python

echo Using Python: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

%PYTHON_CMD% -m pip --version >nul 2>&1
if errorlevel 1 (
  echo pip not found, trying ensurepip...
  %PYTHON_CMD% -m ensurepip --upgrade
  if errorlevel 1 goto :pip_failed
)

echo Installing Python packages from requirements.txt...
%PYTHON_CMD% -m pip install --upgrade pip
if errorlevel 1 goto :pip_failed

%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 goto :pip_failed

echo Installing this project in editable mode...
%PYTHON_CMD% -m pip install -e . --no-deps
if errorlevel 1 goto :pip_failed

echo.
echo Install complete.
echo Next:
echo   list-devices.cmd
echo   run.cmd --verbose
echo.
echo Note: vgamepad may open the ViGEmBus driver installer and ask for admin approval.
exit /b 0

:find_python
py -3.12 --version >nul 2>&1 && set "PYTHON_CMD=py -3.12" && exit /b 0
py -3 --version >nul 2>&1 && set "PYTHON_CMD=py -3" && exit /b 0
python --version >nul 2>&1 && set "PYTHON_CMD=python" && exit /b 0

echo Python was not found.
where winget >nul 2>&1
if errorlevel 1 exit /b 1

echo Trying to install Python 3.12 with winget...
winget install -e --id Python.Python.3.12 --source winget
if errorlevel 1 exit /b 1

py -3.12 --version >nul 2>&1 && set "PYTHON_CMD=py -3.12" && exit /b 0
py -3 --version >nul 2>&1 && set "PYTHON_CMD=py -3" && exit /b 0
python --version >nul 2>&1 && set "PYTHON_CMD=python" && exit /b 0
exit /b 1

:no_python
echo.
echo Python could not be installed automatically.
echo Install Python 3.12 from https://www.python.org/downloads/windows/
echo Then close this window, open a new cmd, and run install.cmd again.
exit /b 1

:pip_failed
echo.
echo Installation failed. Check the error above.
exit /b 1
