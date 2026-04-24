@echo off
cd /d %~dp0
echo Starting DBLens backend...
call venv\Scripts\activate.bat
python run.py
