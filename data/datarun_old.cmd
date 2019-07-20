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
echo Gold Prices download started
python.exe goldprice.py
echo Gold Prices downloaded
echo Crude Oil Prices download started
python.exe crudeoilprices.py
echo Crude Oil Prices downloaded
echo Exchange Rates download started 
python.exe exchangeratesHistory.py %startdate% %enddate%
echo Exchange Rates downloaded
echo Stock History download started
python.exe stockHistory.py %startdate% %enddate%
echo Stock History downloaded 
echo NSE Index History download started
python.exe nseIndexHistory.py %startdate% %enddate%
echo NSE Index History downloaded
echo Total Return History download started
python.exe totalreturnindicesHistory.py %startdate% %enddate%
echo Total Return History downloaded
echo Option Chain History download started
python.exe optionChainHistory.py
echo Option Chain History downloaded

echo -----Weekly and Monthly data downloads-----
python.exe datarun.py
echo Populating daily returns
python.exe sql_stored_procs.py
rem echo Futures History download started
rem python.exe futuresHistory.py %startdate% %enddate%
rem echo Futures History downloaded
exit /B 1

:usage
@echo Batch file did not run
@echo(
@echo Usage : datarun.cmd startDate endDate : dates in YYYYMMDD format
@echo(

exit /B 1 
