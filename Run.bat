@echo off
git pull
start wt powershell -NoExit -Command "cd '%~dp0'; .venv\Scripts\Activate.ps1; python main.py"