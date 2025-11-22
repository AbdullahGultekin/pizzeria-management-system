@echo off
if "%1"=="hidden" goto :hidden
start "" /min "%~f0" hidden
exit
:hidden
cd /d "C:\Users\abdul\Cursor projects\pizzeria-management-system"
pythonw app.py
exit

