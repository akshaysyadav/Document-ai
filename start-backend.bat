@echo off
echo Starting KMRL Document-AI Backend...
cd /d "C:\Desktop\KMRL\Document-ai\backend"
set PYTHONPATH=.
C:\Desktop\KMRL\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000