@echo off


echo Starting Mrig Analytics!
cmd /c "cd /d C:\anaconda\Scripts & .\activate & cd /d G:\Mrig Analytics\mrigAnalytics\mrigweb\ & python .\manage.py runserver"

#python.exe manage.py runserver
