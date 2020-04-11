@echo off

set TODAY=%DATE:~10,4%%DATE:~4,2%%DATE:~7,2%

for /f "usebackq" %%i in (`PowerShell $date ^= Get-Date^; $date ^= $date.AddDays^(-1^)^; $date.ToString^('yyyyMMdd'^)`) do set YESTERDAY=%%i 

set startdate=%1
set enddate=%2
set alldata=%3
set progressbar=%4

if [%1] == [] set startdate=%YESTERDAY%
if [%2] == [] set enddate=%TODAY%
if [%3] == [] set alldata="0"
if [%4] == [] set progressbar="1"

echo Welcome to Mrig Data Run!
@echo -------------Mrig Data Run----------- >> dailyBatchRunLog.txt
@echo ------------%date% %time%------------>> dailyBatchRunLog.txt 
cd /D F:\Mrig Analytics\Development\mrigAnalytics\data\


python.exe navAllFetcher.py
python.exe Bhavcopy.py

echo ---Backing RB_WAREHOUSE------
db_dump RB_WAREHOUSE
echo ---Backing MRIGWEB------
db_dump MRIGWEB


exit /B 1

:usage
@echo Batch file did not run
@echo(
@echo Usage : datarun.cmd startDate endDate : dates in YYYYMMDD format
@echo(

exit /B 1 
