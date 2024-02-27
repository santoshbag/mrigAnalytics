@echo off

set TODAY=%DATE:~10,4%%DATE:~4,2%%DATE:~7,2%

for /f "usebackq" %%i in (`PowerShell $date ^= Get-Date^; $date ^= $date.AddDays^(-1^)^; $date.ToString^('yyyyMMdd'^)`) do set YESTERDAY=%%i 

set startdate=%1
set enddate=%2


if [%1] == [] set startdate=%YESTERDAY%
if [%2] == [] set enddate=%TODAY%

echo Welcome to Mrig Data Run!
@echo -------------Mrig Data Run----------- >> dailyBatchRunLog.txt
@echo ------------%date% %time%------------>> dailyBatchRunLog.txt 
cd /D G:\Mrig Analytics\mrigAnalytics\data


rem python.exe test.py %startdate% %enddate%
echo Daily download started
python.exe datarun.py
exit /B 1

:usage
@echo Batch file did not run
@echo(
@echo Usage : datarun.cmd startDate endDate : dates in YYYYMMDD format
@echo(

exit /B 1 
