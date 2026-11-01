@echo off
setlocal
cd /d "%~dp0"
title PC Studio Control - Diagnostic

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3"
) else (
  set "PY=python"
)

%PY% -c "import mcp, requests; print('Dependances Python : OK')"
if errorlevel 1 (
  echo Lance INSTALL.bat avant de continuer.
  pause
  exit /b 1
)

%PY% -m py_compile server.py
if errorlevel 1 (
  echo Erreur de syntaxe dans server.py.
  pause
  exit /b 1
)

%PY% -c "from server import studio_status; import json; print(json.dumps(studio_status(), indent=2, ensure_ascii=False))"
if errorlevel 1 (
  echo Le diagnostic a echoue.
  pause
  exit /b 1
)

echo.
echo Diagnostic termine. Le client MCP demarre server.py via stdio.
echo Aucun serveur reseau public n'est lance.
pause
