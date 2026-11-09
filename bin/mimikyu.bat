@echo off
REM Portable launcher for Mimikyu Desktop Pet on Windows
REM Runs silently in the background with pythonw (no cmd console)

set "SCRIPT_DIR=%~dp0"
set "REPO_DIR=%SCRIPT_DIR%.."

where pythonw >nul 2>nul
if %errorlevel% equ 0 (
    start "" pythonw "%REPO_DIR%\src\mimikyu.py"
) else (
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        start "" python "%REPO_DIR%\src\mimikyu.py"
    ) else (
        echo Error: Python was not found in your system PATH.
        echo Please install Python 3 from https://www.python.org/
        pause
    )
)
