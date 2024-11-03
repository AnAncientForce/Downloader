@echo off
git pull
call "%~dp0.venv\Scripts\activate"
python "%~dp0main.py"