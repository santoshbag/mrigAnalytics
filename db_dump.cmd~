@echo off

set db=%1

cd /D F:\Mrig Analytics\Data Warehouse\mrig\

set PGPASSWORD=xanto007&& pg_dump -U postgres -d %db% | gzip > %db%.pgsql.gz

