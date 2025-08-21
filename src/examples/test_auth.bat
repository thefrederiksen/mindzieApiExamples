@echo off
echo ============================================================
echo Testing Authenticated Hello World
echo ============================================================
echo.

REM Set your credentials here (replace with your actual values)
set MINDZIE_TENANT_ID=your-tenant-id-here
set MINDZIE_API_KEY=your-api-key-here

echo Current credentials:
echo MINDZIE_TENANT_ID=%MINDZIE_TENANT_ID%
echo MINDZIE_API_KEY=%MINDZIE_API_KEY%
echo.

if "%MINDZIE_TENANT_ID%"=="your-tenant-id-here" (
    echo [ERROR] Please edit this file and add your actual credentials!
    echo.
    echo Edit the lines:
    echo   set MINDZIE_TENANT_ID=your-actual-tenant-id
    echo   set MINDZIE_API_KEY=your-actual-api-key
    echo.
    pause
    exit /b 1
)

echo Running authenticated hello world...
python hello_world_authenticated.py

echo.
pause