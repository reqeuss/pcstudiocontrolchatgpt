@echo off
setlocal
cd /d "%~dp0"
title PC Studio Control - Installation

echo ==========================================
echo        PC Studio Control - Installation
echo ==========================================

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3"
) else (
  set "PY=python"
)

%PY% --version
if errorlevel 1 (
  echo Python 3.11+ est requis.
  echo Installe-le depuis https://www.python.org/downloads/
  pause
  exit /b 1
)

%PY% -m pip install --upgrade pip
if errorlevel 1 goto error

%PY% -m pip install -r requirements.txt
if errorlevel 1 goto error

if not defined PC_STUDIO_WORKSPACE set "PC_STUDIO_WORKSPACE=%USERPROFILE%\PCStudioWorkspace"
if not exist "%PC_STUDIO_WORKSPACE%" mkdir "%PC_STUDIO_WORKSPACE%"

%PY% -m py_compile server.py
if errorlevel 1 goto error

echo.
echo Installation terminee.
echo Workspace : %PC_STUDIO_WORKSPACE%
echo Configuration : pc-studio.config.json
echo Consulte README.md pour connecter ChatGPT Desktop ou ZCode.
pause
exit /b 0

:error
echo.
echo Installation echouee. Consulte le message ci-dessus.
pause
exit /b 1
