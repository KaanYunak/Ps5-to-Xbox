@echo off
setlocal
cd /d "%~dp0"

echo [ps5-to-xbox] Installer
echo.

call "%~dp0find-python.cmd"
if errorlevel 1 goto :no_python

:install_with_python
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

:no_python
echo Python was not found.
where winget >nul 2>&1
if errorlevel 1 goto :python_failed

echo Trying to install Python 3.12 with winget...
winget install -e --id Python.Python.3.12 --source winget

call "%~dp0find-python.cmd"
if not errorlevel 1 goto :python_found_after_winget

:python_failed
echo.
echo Python could not be installed automatically.
echo Install Python 3.12 from https://www.python.org/downloads/windows/
echo Then close this window, open a new cmd, and run install.cmd again.
exit /b 1

:python_found_after_winget
echo.
echo Python is now available as: %PYTHON_CMD%
goto :install_with_python

:pip_failed
echo.
echo Installation failed. Check the error above.
exit /b 1
