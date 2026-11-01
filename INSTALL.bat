@echo off
setlocal
cd /d "%~dp0"
echo ==========================================
echo        PC Studio Control - Installation
echo ==========================================
where py >nul 2>nul
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")
%PY% --version
if errorlevel 1 (
  echo Python 3.11+ est requis. Installe-le depuis https://www.python.org/downloads/
  pause
  exit /b 1
)
%PY% -m pip install --upgrade pip
if errorlevel 1 goto error
%PY% -m pip install -r requirements.txt
if errorlevel 1 goto error
if not defined PC_STUDIO_WORKSPACE set "PC_STUDIO_WORKSPACE=%USERPROFILE%\PCStudioWorkspace"
if not exist "%PC_STUDIO_WORKSPACE%" mkdir "%PC_STUDIO_WORKSPACE%"
echo Installation terminee. Workspace : %PC_STUDIO_WORKSPACE%
echo Configure ensuite le serveur MCP avec mcp.example.json.
pause
exit /b 0
:error
echo Installation echouee.
pause
exit /b 1
