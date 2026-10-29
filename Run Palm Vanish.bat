@echo off
cd /d "%~dp0"
py palm_vanish.py %*
if errorlevel 1 pause
