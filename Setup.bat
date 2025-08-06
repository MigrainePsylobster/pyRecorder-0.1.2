@echo off
echo Setting up Python environment for PyRecorder...

:: Check if virtual environment exists
if exist "venv\" (
    echo Virtual environment already exists, skipping creation...
) else (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment. Make sure Python is installed.
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Check if main requirements are already installed
python -c "import mss, cv2, pygetwindow, numpy, PIL" >nul 2>&1
if errorlevel 1 (
    echo Installing main packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install main requirements.
        pause
        exit /b 1
    )
) else (
    echo Main packages are already installed.
)

:: Try to install audio support
echo.
echo Attempting to install audio support (pyaudio)...
pip install pyaudio >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Could not install pyaudio for audio recording.
    echo The application will work with VIDEO ONLY recording.
    echo.
    echo To add audio support later, try one of these options:
    echo 1. pip install pipwin, then: pipwin install pyaudio
    echo 2. Use Anaconda: conda install pyaudio
    echo 3. Download precompiled wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/
    echo.
) else (
    echo Audio support installed successfully!
)

echo.
echo Setup complete!
echo You can now run the recorder using run.bat
echo Note: If audio didn't install, the app will record video only.
pause
