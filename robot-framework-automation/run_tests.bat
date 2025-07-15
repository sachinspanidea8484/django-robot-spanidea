@echo off
set TIMESTAMP=%DATE:~10,4%-%DATE:~4,2%-%DATE:~7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

set LOG_DIR=logs\run_%TIMESTAMP%
mkdir %LOG_DIR%

robot --output %LOG_DIR%\output.xml --log %LOG_DIR%\log.html --report %LOG_DIR%\report.html tests
