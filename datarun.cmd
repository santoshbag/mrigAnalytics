@echo off

set TODAY=%DATE:~10,4%%DATE:~4,2%%DATE:~7,2%

for /f "usebackq" %%i in (`PowerShell $date ^= Get-Date^; $date ^= $date.AddDays^(-1^)^; $date.ToString^('yyyyMMdd'^)`) do set YESTERDAY=%%i 

set startdate=%1
set enddate=%2
set alldata=%3
set progressbar=%4

if [%1] == [] set startdate=%YESTERDAY%
if [%2] == [] set enddate=%TODAY%
if [%3] == [] set alldata="1"
if [%4] == [] set progressbar="1"

echo Welcome to Mrig Data Run!
echo %alldata%
@echo -------------Mrig Data Run----------- >> dailyBatchRunLog.txt
@echo ------------%date% %time%------------>> dailyBatchRunLog.txt 
#cd /D F:\Mrig Analytics\Development\mrigAnalytics\data\
cmd /c "cd /d C:\anaconda\Scripts & .\activate & cd /d G:\Mrig Analytics\mrigAnalytics\data\ & python .\datarun.py"

#python.exe datarun_linux.py %startdate% %enddate% %alldata% %progressbar%

#echo ---Backing RB_WAREHOUSE------
#db_dump RB_WAREHOUSE
#echo ---Backing MRIGWEB------
#db_dump MRIGWEB


exit /B 1

:usage
@echo Batch file did not run
@echo(
@echo Usage : datarun.cmd startDate endDate : dates in YYYYMMDD format
@echo(

exit /B 1 
