@echo off
echo Starting PyRecorder...

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Run the main Python script
python main.py

pause
