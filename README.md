# PyRecorder

A powerful, high-quality screen recording application for Windows with advanced multi-monitor support and system audio capture.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

##  Features

###  **Recording Modes**
- **Region Selection**: Lightshot-style area selection with transparent overlay
- **Window Selection**: Record specific application windows
- **Dynamic Region Changes**: Adjust recording area during active recording

###  **Multi-Monitor Support**
- **Automatic adaptation** to any monitor configuration
- **Mixed resolutions** support (4K + 1080p + any combination)
- **Negative coordinates** handling for extended desktop setups
- **Real-time coordinate conversion** across all monitors

###  **High-Quality Audio**
- **Windows system audio capture** (what you hear through speakers/headphones)
- **Loopback audio recording** via Stereo Mix
- **Automatic audio/video synchronization**
- **No microphone interference** - pure system output only

###  **Performance & Quality**
- **30 FPS** smooth recording
- **MP4 format** with optimized compression
- **Real-time video processing** with OpenCV
- **Thread-safe** recording engine
- **Minimal performance impact**

##  Quick Start

### Prerequisites
- **Windows 10/11**
- **Python 3.8+**
- **Stereo Mix enabled** in Windows Sound settings (for audio capture)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/pyrecorder.git
   cd pyrecorder
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Enable Stereo Mix** (for audio capture):
   - Right-click sound icon in system tray
   - Select "Open Sound settings"
   - Go to "Sound Control Panel"
   - In "Recording" tab, right-click and "Show Disabled Devices"
   - Enable "Stereo Mix"

4. **Run the application**:
   ```bash
   python main.py
   ```

### Alternative Setup (Windows)
Run the automated setup script:
```bash
Setup.bat
```

##  Usage

### Basic Recording

1. **Launch the application**: `python main.py`
2. **Choose recording mode**:
   - **Region**: Select custom area on any monitor
   - **Window**: Choose specific application window
3. **Click "Start Recording"**
4. **Select your area/window** using the transparent overlay
5. **Click "Stop Recording"** when finished

### Advanced Features

####  **Dynamic Region Changes**
- While recording, click **"Change Region"** to select a new area
- Recording continues seamlessly with the new region
- Frames automatically resized to maintain video consistency

####  **Multi-Monitor Recording**
- Works automatically with any monitor setup
- Select regions across different monitors
- Handles complex layouts (extended desktop, mixed resolutions)

####  **Audio Configuration**
- Ensure **Stereo Mix** is enabled for system audio capture
- Audio automatically combines with video during recording
- Final output: `filename_final.mp4` with synchronized audio/video

##  Configuration

### Monitor Support
- **Automatic detection** of monitor configuration
- **No manual setup** required
- **Instant adaptation** to monitor changes

### Audio Settings
The application prioritizes **Windows system audio** (Stereo Mix):
- **System output only** - no microphone interference
- **High-quality capture** at 44.1kHz, 16-bit
- **Automatic device detection**

### Video Quality
- **Format**: MP4 (H.264 compatible)
- **Frame Rate**: 30 FPS
- **Resolution**: Native (matches selected region)
- **Compression**: Optimized for quality/size balance

## Dependencies

### Core Libraries
- `opencv-python` - Video processing and encoding
- `mss` - High-performance screen capture
- `numpy` - Array processing
- `Pillow` - Image manipulation
- `sounddevice` - Audio capture interface

### GUI Framework
- `tkinter` - Built-in Python GUI (no additional install)
- `pygetwindow` - Window detection and management

### Audio Processing
- `sounddevice` - Audio recording
- Windows Audio APIs (automatic detection)

## Troubleshooting

### Audio Issues
**Problem**: "No audio file created" message
**Solution**: 
1. Enable Stereo Mix in Windows Sound settings
2. Ensure it's set as default recording device
3. Check Windows audio drivers are up to date

### Multi-Monitor Issues
**Problem**: Region selector only shows on one monitor
**Solution**: 
- The overlay covers all monitors automatically
- If not visible, try pressing `Alt+Tab` to focus the overlay window
- Restart the application if monitor configuration changed

### Performance Issues
**Problem**: Recording is laggy or dropped frames
**Solution**:
1. Close unnecessary applications
2. Record smaller regions for better performance
3. Ensure sufficient disk space in recordings folder

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

##  TODO / Roadmap

- [ ] **Hotkey support** for start/stop recording
- [ ] **Multiple output formats** (AVI, MOV, WebM)
- [ ] **Frame rate options** (15, 30, 60 FPS)
- [ ] **Quality presets** (Low, Medium, High, Ultra)
- [ ] **Recording scheduler** with timer
- [ ] **Webcam overlay** option
- [ ] **Linux/macOS support**

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- **MSS library** for efficient screen capture
- **OpenCV** for video processing
- **Windows Audio Session API** for system audio capture
- **Python community** for excellent libraries and documentation

##  Tips

### For Best Results:
- **Close unnecessary applications** during recording
- **Use SSD storage** for better write performance  
- **Record smaller regions** for higher frame rates
- **Enable Stereo Mix** before first use
- **Test audio** with a short recording first

### Multi-Monitor Setups:
- The application **automatically adapts** to any monitor configuration
- **No setup required** when switching between laptop/desktop/docking station
- **Negative coordinates** are handled automatically
- **Mixed resolutions** (4K + 1080p) work seamlessly


