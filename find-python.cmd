@echo off
set "PYTHON_CMD="

call :try_cmd "py -3.14" && exit /b 0
call :try_cmd "py -3.13" && exit /b 0
call :try_cmd "py -3.12" && exit /b 0
call :try_cmd "py -3.11" && exit /b 0
call :try_cmd "py -3.10" && exit /b 0
call :try_cmd "py -3" && exit /b 0
call :try_cmd "python" && exit /b 0
call :try_cmd "python3" && exit /b 0

call :try_path "%LocalAppData%\Programs\Python\Python314\python.exe" && exit /b 0
call :try_path "%LocalAppData%\Programs\Python\Python313\python.exe" && exit /b 0
call :try_path "%LocalAppData%\Programs\Python\Python312\python.exe" && exit /b 0
call :try_path "%LocalAppData%\Programs\Python\Python311\python.exe" && exit /b 0
call :try_path "%LocalAppData%\Programs\Python\Python310\python.exe" && exit /b 0
call :try_path "%ProgramFiles%\Python314\python.exe" && exit /b 0
call :try_path "%ProgramFiles%\Python313\python.exe" && exit /b 0
call :try_path "%ProgramFiles%\Python312\python.exe" && exit /b 0
call :try_path "%ProgramFiles%\Python311\python.exe" && exit /b 0
call :try_path "%ProgramFiles%\Python310\python.exe" && exit /b 0
call :try_path "%ProgramFiles(x86)%\Python312-32\python.exe" && exit /b 0
call :try_path "%ProgramFiles(x86)%\Python311-32\python.exe" && exit /b 0
call :try_path "%ProgramFiles(x86)%\Python310-32\python.exe" && exit /b 0

exit /b 1

:try_cmd
%~1 --version >nul 2>&1
if not errorlevel 1 (
  set "PYTHON_CMD=%~1"
  exit /b 0
)
exit /b 1

:try_path
if not exist "%~1" exit /b 1
"%~1" --version >nul 2>&1
if not errorlevel 1 (
  set "PYTHON_CMD="%~1""
  exit /b 0
)
exit /b 1
