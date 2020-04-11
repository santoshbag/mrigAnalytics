@echo off
for /f "usebackq" %%i in (`PowerShell $date ^= Get-Date^; $date ^= $date.AddDays^(-1^)^; $date.ToString^('yyyymmdd'^)`) do set YESTERDAY=%%i 
echo %YESTERDAY%
