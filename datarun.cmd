@echo off

if [%1] == [] goto usage
if [%2] == [] goto usage

echo Welcome to Mrig Data Run!
@echo -------------Mrig Data Run----------- >> dailyBatchRunLog.txt
@echo ------------%date% %time%------------>> dailyBatchRunLog.txt 
cd /D F:\Mrig Analytics\Development\mrigAnalytics\

set startdate=%1
set enddate=%2


rem python.exe test.py %startdate% %enddate%
python.exe navAllFetcher.py
echo Mutual Funds NAV downloaded
python.exe stockHistory.py %startdate% %enddate%
echo Stock History downloaded 
python.exe nseIndexHistory.py %startdate% %enddate%
echo NSE Index History downloaded
python.exe futuresHistory.py %startdate% %enddate%
echo Futures History downloaded
python.exe totalreturnindicesHistory.py %startdate% %enddate%
echo Total Return History downloaded

:usage
@echo Batch file did not run
@echo(
@echo Usage : datarun.cmd startDate endDate : dates in YYYYMMDD format
exit /B 1 
