@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")
%PY% -c "import mcp, requests; print('Dependances OK')"
if errorlevel 1 (
  echo Lance d'abord INSTALL.bat.
  pause
  exit /b 1
)
if not defined PC_STUDIO_WORKSPACE set "PC_STUDIO_WORKSPACE=%USERPROFILE%\PCStudioWorkspace"
if not exist "%PC_STUDIO_WORKSPACE%" mkdir "%PC_STUDIO_WORKSPACE%"
echo PC Studio Control est pret.
echo Workspace : %PC_STUDIO_WORKSPACE%
echo Le client MCP demarre server.py via stdio.
echo Aucun serveur reseau public n'est lance.
pause
