@echo off
echo Starting Backend Server from .venv...
".\.venv\Scripts\python.exe" -m uvicorn main:app --reload
pause
