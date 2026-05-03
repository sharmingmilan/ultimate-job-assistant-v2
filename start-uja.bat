@echo off
REM Ultimate Job Assistant — local web host launcher (Windows)
REM Requires Python 3.11+ on PATH.

setlocal
set SCRIPT_DIR=%~dp0
set HOST_DIR=%SCRIPT_DIR%host
set VENV_DIR=%HOST_DIR%\.venv

cd /d "%HOST_DIR%"

where py >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python launcher 'py' not found. Install Python 3.11+ from https://www.python.org/downloads/
    exit /b 1
)

py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.11+ required but not found. Install from https://www.python.org/downloads/
    exit /b 1
)

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [uja] creating venv at %VENV_DIR%
    py -3.11 -m venv "%VENV_DIR%"
)

call "%VENV_DIR%\Scripts\activate.bat"
echo [uja] installing dependencies...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt

echo [uja] launching host...
python -m uja_host.main %*
endlocal
