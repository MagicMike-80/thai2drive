@echo off
cd /d "%~dp0"
echo.
echo ========================================
echo   Thai2Drive - Generer sporsmal fra fil
echo ========================================
echo.
if "%~1"=="" (
  echo Dra og slipp en bildefil eller PDF hit!
  echo Stottede formater: jpg, png, pdf
  pause
  exit /b
)
python generate_from_file.py %* --antall 2
echo.
pause
