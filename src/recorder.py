#!/usr/bin/env python3
"""
PyRecorder - Core Recording Engine

High-performance screen recording with thread-safe operation and
dynamic region support for multi-monitor setups.

Features:
- Thread-safe video recording with MSS
- Dynamic region changes during recording
- Frame resizing for consistent video output
- Windows system audio integration
- OpenCV-based video encoding

Author: PyRecorder Team
License: MIT
"""

import cv2
import numpy as np
import mss
import threading
import time
import os
from datetime import datetime

# Audio capture imports - prioritize Windows loopback audio
try:
    from loopback_audio import WindowsAudioLoopback
    LOOPBACK_AUDIO_AVAILABLE = True
except ImportError:
    LOOPBACK_AUDIO_AVAILABLE = False

# Audio recording capability  
AUDIO_AVAILABLE = LOOPBACK_AUDIO_AVAILABLE

class ScreenRecorder:
    def __init__(self):
        self.recording = False
        self.video_writer = None
        self.audio_recorder = None
        self.video_thread = None
        self.output_filename = None
        self.record_region = None
        self.region_lock = threading.Lock()  # Thread-safe region updates
        self.video_writer_lock = threading.Lock()  # Thread-safe video writer updates
        self.current_video_size = None  # Track current video dimensions
        
        # Video settings
        self.fps = 30
        
        # Initialize audio recorder - Windows loopback only
        if LOOPBACK_AUDIO_AVAILABLE:
            self.audio_recorder = WindowsAudioLoopback()
            if self.audio_recorder.is_available():
                self.audio_type = "Windows system audio (loopback)"
                print("Windows system audio loopback available - will capture what you hear!")
            else:
                self.audio_recorder = None
                self.audio_type = "none"
                print("Windows loopback audio not available - enable Stereo Mix in Sound settings")
        else:
            self.audio_recorder = None
            self.audio_type = "none"
            print("No audio recording available - sounddevice not installed")
        
    def start_recording(self, x, y, width, height, filename):
        """
        Start recording the specified region.
        Args:
            x, y: Top-left corner coordinates
            width, height: Recording area dimensions
            filename: Output filename
        Returns:
            bool: True if recording started successfully
        """
        try:
            self.output_filename = filename
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(filename, fourcc, self.fps, (width, height))
            
            if not self.video_writer.isOpened():
                print("Error: Could not open video writer")
                return False
            
            # Store recording parameters and video size
            with self.region_lock:
                self.record_region = {'left': x, 'top': y, 'width': width, 'height': height}
            with self.video_writer_lock:
                self.current_video_size = (width, height)
            self.recording = True
            
            # Start audio recording if available
            if self.audio_recorder:
                audio_started = self.audio_recorder.start_recording(filename)
                if audio_started:
                    print(f"Started {self.audio_type} audio recording")
                else:
                    print(f"Failed to start {self.audio_type} audio recording")
            else:
                print("Recording video only (no audio)")
            
            # Start video recording thread
            self.video_thread = threading.Thread(target=self._record_video)
            self.video_thread.daemon = True
            self.video_thread.start()
            
            print(f"Recording started: {width}x{height} at ({x}, {y})")
            return True
            
        except Exception as e:
            print(f"Error starting recording: {str(e)}")
            self.recording = False
            return False
    
    def stop_recording(self):
        """
        Stop recording and save files.
        Returns:
            str: Final output filename
        """
        try:
            print("Stopping recording...")
            self.recording = False
            
            # Wait for video thread to finish
            if self.video_thread and self.video_thread.is_alive():
                self.video_thread.join(timeout=5)
            
            # Stop audio recording
            audio_file = None
            if self.audio_recorder:
                audio_file = self.audio_recorder.stop_recording()
            
            # Close video writer
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            
            # Combine video and audio if both exist
            if audio_file and os.path.exists(audio_file) and self.output_filename:
                final_filename = self.output_filename.replace('.mp4', '_final.mp4')
                
                # Try to combine using the audio recorder's method
                combine_success = False
                if hasattr(self.audio_recorder, 'combine_with_video'):
                    combine_success = self.audio_recorder.combine_with_video(
                        self.output_filename, audio_file, final_filename
                    )
                
                if combine_success:
                    # Clean up temporary files
                    try:
                        if os.path.exists(self.output_filename):
                            os.remove(self.output_filename)  # Remove video-only file
                        if os.path.exists(audio_file):
                            os.remove(audio_file)  # Remove audio-only file
                    except Exception as e:
                        print(f"Warning: Could not clean up temporary files: {e}")
                    
                    return final_filename
                else:
                    print("Audio combination failed, returning video-only file")
                    return self.output_filename
            else:
                return self.output_filename
                
        except Exception as e:
            print(f"Error stopping recording: {str(e)}")
            return self.output_filename
    
    def update_recording_region(self, x, y, width, height):
        """
        Update the recording region while recording is active.
        New frames will be resized to match the original video dimensions.
        Args:
            x, y: New top-left corner coordinates
            width, height: New recording area dimensions
        Returns:
            bool: True if region was updated successfully
        """
        if not self.recording:
            print("Cannot update region: not currently recording")
            return False
            
        try:
            # Update the region - frames will be resized to fit original video size
            with self.region_lock:
                self.record_region = {'left': x, 'top': y, 'width': width, 'height': height}
            
            print(f"Recording region updated: {width}x{height} at ({x}, {y})")
            with self.video_writer_lock:
                if self.current_video_size:
                    orig_w, orig_h = self.current_video_size
                    print(f"New frames will be resized from {width}x{height} to {orig_w}x{orig_h}")
            
            return True
            
        except Exception as e:
            print(f"Error updating recording region: {str(e)}")
            return False
    
    def get_current_region(self):
        """Get the current recording region"""
        with self.region_lock:
            return self.record_region.copy() if self.record_region else None
    
    def _record_video(self):
        """Record video frames in a separate thread"""
        try:
            with mss.mss() as sct:
                while self.recording:
                    start_time = time.time()
                    
                    # Get current region (thread-safe)
                    with self.region_lock:
                        current_region = self.record_region.copy() if self.record_region else None
                    
                    # Get original video size (thread-safe)
                    with self.video_writer_lock:
                        target_size = self.current_video_size
                    
                    if not current_region or not target_size:
                        time.sleep(0.01)  # Brief pause if no region or size
                        continue
                    
                    # Capture screen region
                    screenshot = sct.grab(current_region)
                    
                    # Convert to numpy array
                    frame = np.array(screenshot)
                    
                    # Convert BGRA to BGR (remove alpha channel)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    
                    # Resize frame to match original video dimensions if needed
                    current_h, current_w = frame.shape[:2]
                    target_w, target_h = target_size
                    
                    if (current_w, current_h) != (target_w, target_h):
                        frame = cv2.resize(frame, (target_w, target_h))
                    
                    # Write frame to video
                    if self.video_writer:
                        self.video_writer.write(frame)
                    
                    # Control frame rate
                    elapsed = time.time() - start_time
                    sleep_time = (1.0 / self.fps) - elapsed
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                        
        except Exception as e:
            print(f"Error in video recording: {str(e)}")
