@echo off
title Install Dependencies

echo Installing required packages.
pip install -r requirements.txt --quiet
if %ERRORLEVEL% equ 0 (
    echo All packages installed successfully, mate!
) else (
    echo Bugger, something went wrong during installation. Check the errors above.
    pause
    exit /b %ERRORLEVEL%
)

echo Press any key to close, mate.
pause
exit /b 0
