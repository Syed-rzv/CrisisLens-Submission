@echo off
setlocal enabledelayedexpansion

set LOG_DIR=%~dp0logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

for /f "tokens=1-6 delims=/:. " %%a in ("%date% %time%") do (
    set YYYY=%%c
    set MM=%%b
    set DD=%%a
    set HH=%%d
    set Min=%%e
    set Sec=%%f
)
set LOGFILE=%LOG_DIR%\arima_forecast_%YYYY%%MM%%DD%_%HH%%Min%%Sec%.txt

echo ARIMA Forecast Run >> "%LOGFILE%"
echo Started at %date% %time% >> "%LOGFILE%"
echo. >> "%LOGFILE%"

cd /d "%~dp0crisislens-API"
C:\Users\97150\anaconda3\python.exe arima_forecast_service.py --periods 30 --by-type >> "%LOGFILE%" 2>&1
set EXITCODE=%ERRORLEVEL%

if %EXITCODE%==0 (
    echo Forecast completed at %date% %time% >> "%LOGFILE%"
) else (
    echo Failed with exit code %EXITCODE% >> "%LOGFILE%"
)

endlocal