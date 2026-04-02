@echo off
REM Launch Rolling Game
REM This batch file activates the virtual environment and runs the game

cd /d "%~dp0"

echo.
echo ========================================
echo   🎮 ROLLING GAME - LAUNCHER
echo ========================================
echo.

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Starting game...
python questionmark.py

pause
