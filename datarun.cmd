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
cd /D F:\Mrig Analytics\Development\mrigAnalytics\


rem python.exe test.py %startdate% %enddate%
echo Mutual Funds NAV download started
python.exe navAllFetcher.py
echo Mutual Funds NAV downloaded
echo Yield Curves download started
python.exe yieldcurve.py
echo Yield Curves downloaded
echo Stock History download started
python.exe stockHistory.py %startdate% %enddate%
echo Stock History downloaded 
echo NSE Index History download started
python.exe nseIndexHistory.py %startdate% %enddate%
echo NSE Index History downloaded
echo Total Return History download started
python.exe totalreturnindicesHistory.py %startdate% %enddate%
echo Total Return History downloaded
echo Futures History download started
python.exe futuresHistory.py %startdate% %enddate%
echo Futures History downloaded
exit /B 1

:usage
@echo Batch file did not run
@echo(
@echo Usage : datarun.cmd startDate endDate : dates in YYYYMMDD format
@echo(

exit /B 1 
