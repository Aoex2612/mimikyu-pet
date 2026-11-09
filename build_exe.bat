@echo off
REM Script to build a standalone single-file Mimikyu.exe for Windows
REM Requires Python with pip

echo ========================================================
echo       Building Mimikyu Desktop Pet for Windows
echo ========================================================
echo.

echo [1/3] Ensuring required packages (pyinstaller, pillow) are installed...
pip install --upgrade pyinstaller pillow

echo.
echo [2/3] Compiling standalone executable with PyInstaller...
pyinstaller --noconsole --onefile ^
    --name "Mimikyu" ^
    --icon "assets\mimikyu.ico" ^
    --add-data "sprites;sprites" ^
    src\mimikyu_windows.py

echo.
echo [3/3] Build finished!
if exist "dist\Mimikyu.exe" (
    echo.
    echo ========================================================
    echo SUCCESS: Standalone executable created at:
    echo        dist\Mimikyu.exe
    echo ========================================================
    echo You can distribute dist\Mimikyu.exe to any Windows machine.
    echo No Python or dependencies required to run it!
) else (
    echo.
    echo Build failed or output not found in dist\Mimikyu.exe
)

echo.
pause
