@echo off
REM Ultimate Job Assistant — MCP server bootstrap (Windows).
REM
REM Per ADR-002 D1, the v0.2.x runtime is a JSON-RPC-over-stdio MCP
REM server. This script does NOT launch the server itself — Cowork's
REM MCP runtime handles process lifecycle. It just verifies Python
REM 3.11+, creates host/.venv-mcp/ on first run, installs deps, and
REM prints the Cowork MCP-config snippet (with the project root
REM prefilled) for the user to paste into Cowork's MCP registration.
REM
REM Optional first arg: project-root path.

setlocal EnableDelayedExpansion
set SCRIPT_DIR=%~dp0
set HOST_DIR=%SCRIPT_DIR%host
set VENV_DIR=%HOST_DIR%\.venv-mcp

set PROJECT_ROOT=%~1
if "%PROJECT_ROOT%"=="" if not "%UJA_PROJECT_ROOT%"=="" set PROJECT_ROOT=%UJA_PROJECT_ROOT%
if "%PROJECT_ROOT%"=="" set PROJECT_ROOT=^<set this to your Ultimate Job Assistant folder^>

REM --- Python 3.11+ detection ----------------------------------------
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

REM --- venv bootstrap ------------------------------------------------
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [uja-mcp] creating venv at %VENV_DIR%
    py -3.11 -m venv "%VENV_DIR%"
)

set VENV_PY=%VENV_DIR%\Scripts\python.exe

echo [uja-mcp] installing dependencies...
"%VENV_PY%" -m pip install --quiet --upgrade pip
"%VENV_PY%" -m pip install --quiet -r "%HOST_DIR%\requirements.txt"

echo.
echo ================================================================
echo   Ultimate Job Assistant — MCP server ready to register
echo ================================================================
echo.
echo Stdio command (Cowork registers this; do NOT run it directly):
echo.
echo     cd %HOST_DIR% ^&^& "%VENV_PY%" -m uja_mcp.server
echo.
echo Cowork MCP-config snippet (paste under "mcpServers"):
echo.
echo {
echo   "mcpServers": {
echo     "uja": {
echo       "command": "%VENV_PY:\=\\%",
echo       "args": ["-m", "uja_mcp.server"],
echo       "cwd": "%HOST_DIR:\=\\%",
echo       "env": {
echo         "UJA_PROJECT_ROOT": "%PROJECT_ROOT:\=\\%",
echo         "UJA_MCP_LOG_LEVEL": "INFO"
echo       }
echo     }
echo   }
echo }
echo.
echo Notes:
echo   * UJA_PROJECT_ROOT is read once at server startup and persisted to
echo     %%USERPROFILE%%\.uja\config.json.
echo   * Server logs go to stderr; level via UJA_MCP_LOG_LEVEL.
echo   * Template: references\cowork-mcp-config-snippet.json
echo ================================================================
endlocal
