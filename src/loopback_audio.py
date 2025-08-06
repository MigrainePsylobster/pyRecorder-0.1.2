import sounddevice as sd
import numpy as np
import wave
import threading
import time
import os
import tempfile

class WindowsAudioLoopback:
    """
    Capture Windows audio output (system sound) using sounddevice
    This captures the actual audio that's being played through your speakers/headset
    """
    
    def __init__(self):
        self.recording = False
        self.audio_data = []
        self.audio_file = None
        self.sample_rate = 44100
        self.channels = 2
        self.stream = None
        
    def list_loopback_devices(self):
        """List available loopback devices - ONLY system audio output capture"""
        try:
            devices = sd.query_devices()
            loopback_devices = []
            
            for i, device in enumerate(devices):
                device_name = device['name'].lower()
                # ONLY look for system audio output loopback devices
                # Exclude microphones, line-in, and other input sources
                if (any(keyword in device_name for keyword in [
                    'stereo mix', 'what u hear', 'wave out mix', 'loopback'
                ]) and device['max_input_channels'] > 0 and
                # Exclude microphone-related devices
                not any(exclude in device_name for exclude in [
                    'microphone', 'mic', 'line in', 'aux', 'input'
                ])):
                    loopback_devices.append((i, device))
                    print(f"Found system output loopback: {device['name']}")
                    
            return loopback_devices
        except Exception as e:
            print(f"Error listing devices: {e}")
            return []
    
    def find_output_device(self):
        """Find ONLY system audio output loopback device (no microphones or line-in)"""
        try:
            devices = sd.query_devices()
            
            # Priority 1: Stereo Mix (pure system audio output)
            for i, device in enumerate(devices):
                if (device['max_input_channels'] > 0 and 
                    'stereo mix' in device['name'].lower() and
                    # Ensure it's not a microphone or line-in
                    not any(exclude in device['name'].lower() for exclude in [
                        'microphone', 'mic', 'line in', 'aux'
                    ])):
                    print(f"Found Stereo Mix (system output): {device['name']}")
                    return i
            
            # Priority 2: "What U Hear" type devices (system output only)
            for i, device in enumerate(devices):
                if (device['max_input_channels'] > 0 and 
                    any(keyword in device['name'].lower() for keyword in [
                        'what u hear', 'wave out mix', 'loopback'
                    ]) and
                    # Exclude any microphone/input devices
                    not any(exclude in device['name'].lower() for exclude in [
                        'microphone', 'mic', 'line in', 'aux', 'input'
                    ])):
                    print(f"Found system output loopback: {device['name']}")
                    return i
            
            print("❌ No system audio output loopback device found")
            print("💡 Enable 'Stereo Mix' in Windows Sound settings to capture system audio")
            return None
            
        except Exception as e:
            print(f"Error finding output device: {e}")
            return None
    
    def is_available(self):
        """Check if loopback recording is available"""
        try:
            device_id = self.find_output_device()
            return device_id is not None
        except:
            return False
    
    def start_recording(self, output_file):
        """Start recording system audio output"""
        if self.recording:
            return False
            
        try:
            # Find loopback device
            device_id = self.find_output_device()
            if device_id is None:
                print("No audio loopback device found")
                return False
            
            device_info = sd.query_devices(device_id)
            print(f"Using audio device: {device_info['name']}")
            
            # Use device's max input channels, but limit to reasonable number
            max_channels = min(device_info['max_input_channels'], 2)  # Stereo max
            if max_channels < 1:
                print(f"Device has no input channels: {max_channels}")
                return False
                
            self.channels = max_channels
            
            # Try to use device's preferred sample rate
            try:
                self.sample_rate = int(device_info['default_samplerate'])
            except:
                self.sample_rate = 44100  # Fallback
            
            print(f"Recording config: {self.channels} channels, {self.sample_rate}Hz")
            
            # Create audio file path
            temp_dir = tempfile.gettempdir()
            base_name = os.path.splitext(os.path.basename(output_file))[0]
            self.audio_file = os.path.join(temp_dir, f"{base_name}_audio.wav")
            
            # Clear previous data
            self.audio_data = []
            self.recording = True
            
            # Start recording stream
            self.stream = sd.InputStream(
                device=device_id,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=self._audio_callback,
                dtype=np.float32
            )
            
            self.stream.start()
            print(f"Started Windows audio loopback recording from: {device_info['name']}")
            return True
            
        except Exception as e:
            print(f"Error starting loopback recording: {e}")
            self.recording = False
            return False
    
    def stop_recording(self):
        """Stop recording and save audio file"""
        if not self.recording:
            return None
            
        self.recording = False
        
        try:
            # Stop and close stream
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            
            # Save audio data to file
            if self.audio_data and self.audio_file:
                self._save_audio_data()
                
                if os.path.exists(self.audio_file) and os.path.getsize(self.audio_file) > 0:
                    print(f"Windows audio output saved: {self.audio_file} ({os.path.getsize(self.audio_file)} bytes)")
                    return self.audio_file
                else:
                    print("Audio file was not created or is empty")
                    return None
            else:
                print("No audio data recorded")
                return None
                
        except Exception as e:
            print(f"Error stopping recording: {e}")
            return None
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback function for audio stream"""
        if status:
            print(f"Audio callback status: {status}")
        
        if self.recording:
            # Convert and store audio data
            self.audio_data.append(indata.copy())
    
    def _save_audio_data(self):
        """Save recorded audio data to WAV file"""
        try:
            if not self.audio_data or not self.audio_file:
                return
                
            # Concatenate all audio chunks
            audio_array = np.concatenate(self.audio_data, axis=0)
            
            # Convert float32 to int16 for WAV format
            audio_int16 = (audio_array * 32767).astype(np.int16)
            
            # Save as WAV file
            with wave.open(str(self.audio_file), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_int16.tobytes())
                
            print(f"Audio data saved: {len(audio_array)} samples")
            
        except Exception as e:
            print(f"Error saving audio data: {e}")
    
    def combine_with_video(self, video_file, audio_file, output_file):
        """Combine video with recorded system audio"""
        try:
            import subprocess
            
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-i', audio_file,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                '-y',
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(output_file):
                print(f"Combined video with system audio: {output_file}")
                return True
            else:
                print(f"Audio combination failed: {result.stderr[:200]}")
                return False
                
        except Exception as e:
            print(f"Error combining audio/video: {e}")
            return False

# Test function
def test_loopback():
    """Test Windows audio loopback"""
    loopback = WindowsAudioLoopback()
    
    print("Testing Windows Audio Loopback...")
    print(f"Available: {loopback.is_available()}")
    
    # List available devices
    devices = loopback.list_loopback_devices()
    print(f"Found {len(devices)} potential loopback devices:")
    for device_id, device in devices:
        print(f"  {device_id}: {device['name']} (channels: {device['max_input_channels']})")
    
    # Test recording
    if loopback.is_available():
        print("\\nStarting 5-second test recording...")
        print("Play some audio now (music, YouTube, etc.)")
        
        if loopback.start_recording("test_loopback.mp4"):
            time.sleep(5)
            audio_file = loopback.stop_recording()
            
            if audio_file:
                print(f"✅ Success! Recorded system audio to: {audio_file}")
            else:
                print("❌ No audio file created")
        else:
            print("❌ Failed to start recording")
    else:
        print("❌ No loopback devices available")

if __name__ == "__main__":
    test_loopback()
