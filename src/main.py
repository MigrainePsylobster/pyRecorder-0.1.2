#!/usr/bin/env python3
"""
PyRecorder - Main GUI Application

A powerful screen recording application with advanced multi-monitor support
and Windows system audio capture.

Features:
- Multi-monitor region selection with transparent overlay
- Window-specific recording
- Dynamic region changes during recording
- Windows system audio capture via Stereo Mix
- High-quality MP4 output at 30 FPS

Author: PyRecorder Team
License: MIT
Repository: https://github.com/yourusername/pyrecorder
"""

import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
import os
import sys
from datetime import datetime

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from recorder import ScreenRecorder, AUDIO_AVAILABLE
from region_selector import RegionSelector
from window_selector import WindowSelector

class PyRecorderGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PyRecorder")
        self.root.geometry("400x320")
        self.root.resizable(False, False)
        
        self.recorder = ScreenRecorder()
        self.recording = False
        
        # Theme settings
        self.dark_mode = False
        self.themes = {
            'light': {
                'bg': '#ffffff',
                'fg': '#000000',
                'button_bg': '#f0f0f0',
                'button_fg': '#000000',
                'frame_bg': '#ffffff',
                'record_button_bg': '#4CAF50',
                'stop_button_bg': '#f44336',
                'change_button_bg': '#FF9800'
            },
            'dark': {
                'bg': '#2d2d2d',
                'fg': '#ffffff',
                'button_bg': '#404040',
                'button_fg': '#ffffff',
                'frame_bg': '#3d3d3d',
                'record_button_bg': '#4CAF50',
                'stop_button_bg': '#f44336',
                'change_button_bg': '#FF9800'
            }
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Apply initial theme
        self.apply_theme()
        
        # Title
        self.title_label = tk.Label(self.root, text="PyRecorder", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=10)
        
        # Theme toggle button (top right)
        theme_frame = tk.Frame(self.root)
        theme_frame.pack(fill="x", padx=20)
        
        self.theme_button = tk.Button(theme_frame, text="🌙 Dark Mode", 
                                    command=self.toggle_theme, 
                                    font=("Arial", 8), width=12, height=1)
        self.theme_button.pack(side="right")
        
        # Recording mode selection
        self.mode_frame = tk.LabelFrame(self.root, text="Recording Mode", font=("Arial", 10, "bold"))
        self.mode_frame.pack(pady=10, padx=20, fill="x")
        
        self.mode_var = tk.StringVar(value="region")
        
        self.region_radio = tk.Radiobutton(self.mode_frame, text="Select Region (Draw Rectangle)", 
                                    variable=self.mode_var, value="region", font=("Arial", 10))
        self.region_radio.pack(anchor="w", padx=10, pady=5)
        
        self.window_radio = tk.Radiobutton(self.mode_frame, text="Select Window", 
                                    variable=self.mode_var, value="window", font=("Arial", 10))
        self.window_radio.pack(anchor="w", padx=10, pady=5)
        
        # Control buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=20)
        
        self.record_button = tk.Button(self.button_frame, text="Start Recording", 
                                     command=self.toggle_recording, 
                                     bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                                     width=15, height=2)
        self.record_button.pack(pady=5)
        
        # Change region button (initially hidden)
        self.change_region_button = tk.Button(self.button_frame, text="Change Region", 
                                            command=self.change_recording_region,
                                            bg="#FF9800", fg="white", font=("Arial", 10, "bold"),
                                            width=15, height=1)
        # Don't pack initially - will show during recording
        
        # Status
        self.status_label = tk.Label(self.root, text="Ready to record", 
                                   font=("Arial", 10), fg="green")
        self.status_label.pack(pady=5)
        
        # Recording info
        self.info_label = tk.Label(self.root, text="", font=("Arial", 9), fg="blue")
        self.info_label.pack(pady=5)
        
        # Audio status
        if self.recorder.audio_type == "system/microphone":
            audio_status = "Audio: Available (System/Microphone)"
            audio_color = "green"
        else:
            audio_status = "Audio: Disabled"
            audio_color = "red"
            
        self.audio_status_label = tk.Label(self.root, text=audio_status, 
                                         font=("Arial", 8), fg=audio_color)
        self.audio_status_label.pack(pady=2)
        
        # Apply theme to all widgets after creation
        self.apply_theme()
        
    def apply_theme(self):
        """Apply the current theme to all widgets"""
        theme = self.themes['dark' if self.dark_mode else 'light']
        
        # Apply to root window
        self.root.configure(bg=theme['bg'])
        
        # Update theme button text and colors
        if hasattr(self, 'theme_button'):
            if self.dark_mode:
                self.theme_button.config(text="☀️ Light Mode", bg=theme['button_bg'], fg=theme['button_fg'])
            else:
                self.theme_button.config(text="🌙 Dark Mode", bg=theme['button_bg'], fg=theme['button_fg'])
        
        # Update all widgets if they exist
        widget_updates = [
            ('title_label', {'bg': theme['bg'], 'fg': theme['fg']}),
            ('mode_frame', {'bg': theme['frame_bg'], 'fg': theme['fg']}),
            ('region_radio', {'bg': theme['frame_bg'], 'fg': theme['fg'], 'selectcolor': theme['button_bg']}),
            ('window_radio', {'bg': theme['frame_bg'], 'fg': theme['fg'], 'selectcolor': theme['button_bg']}),
            ('button_frame', {'bg': theme['bg']}),
            ('status_label', {'bg': theme['bg']}),
            ('info_label', {'bg': theme['bg']}),
            ('audio_status_label', {'bg': theme['bg']}),
        ]
        
        for attr_name, config in widget_updates:
            if hasattr(self, attr_name):
                widget = getattr(self, attr_name)
                try:
                    widget.configure(**config)
                except tk.TclError:
                    # Some configurations might not be available for all widgets
                    pass
        
        # Update theme frame
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame) and hasattr(self, 'button_frame') and widget != self.button_frame and hasattr(self, 'mode_frame') and widget != self.mode_frame:
                try:
                    widget.configure(bg=theme['bg'])
                except tk.TclError:
                    pass
        
    def toggle_theme(self):
        """Toggle between light and dark mode"""
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        
    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        try:
            if self.mode_var.get() == "region":
                # Use region selector
                selector = RegionSelector()
                region = selector.select_region()
                
                if region is None:
                    self.status_label.config(text="Recording cancelled", fg="orange")
                    return
                    
                x, y, width, height = region
                
            else:  # window mode
                # Use window selector
                selector = WindowSelector()
                window_info = selector.select_window()
                
                if window_info is None:
                    self.status_label.config(text="No window selected", fg="orange")
                    return
                    
                x, y, width, height = window_info
            
            # Create recordings folder if it doesn't exist
            recordings_dir = "recordings"
            if not os.path.exists(recordings_dir):
                os.makedirs(recordings_dir)
                print(f"Created recordings directory: {recordings_dir}")
            
            # Generate filename with timestamp in recordings folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(recordings_dir, f"recording_{timestamp}.mp4")
            
            # Start recording
            success = self.recorder.start_recording(x, y, width, height, filename)
            
            if success:
                self.recording = True
                theme = self.themes['dark' if self.dark_mode else 'light']
                self.record_button.config(text="Stop Recording", bg=theme['stop_button_bg'])
                self.status_label.config(text="Recording...", fg="red")
                self.info_label.config(text=f"Recording: {width}x{height} at ({x}, {y})")
                
                # Show change region button only for region mode
                if self.mode_var.get() == "region":
                    self.change_region_button.pack(pady=3)
                
                # Disable mode selection during recording
                for widget in self.root.winfo_children():
                    if isinstance(widget, tk.LabelFrame):
                        for child in widget.winfo_children():
                            if isinstance(child, tk.Radiobutton):
                                child.config(state="disabled")
            else:
                self.status_label.config(text="Failed to start recording", fg="red")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start recording: {str(e)}")
            self.status_label.config(text="Error occurred", fg="red")
            
    def stop_recording(self):
        try:
            filename = self.recorder.stop_recording()
            self.recording = False
            theme = self.themes['dark' if self.dark_mode else 'light']
            self.record_button.config(text="Start Recording", bg=theme['record_button_bg'])
            self.status_label.config(text="Recording saved", fg="green")
            
            # Hide change region button
            self.change_region_button.pack_forget()
            
            # Re-enable mode selection
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.LabelFrame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Radiobutton):
                            child.config(state="normal")
            
            # Show just the filename for display (not full path)
            display_name = os.path.basename(filename) if filename else "Unknown"
            self.info_label.config(text=f"Saved: {display_name} (in recordings folder)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop recording: {str(e)}")
    
    def change_recording_region(self):
        """Allow user to change recording region while recording is active"""
        try:
            if not self.recording:
                return
                
            # Use region selector to get new region
            selector = RegionSelector()
            new_region = selector.select_region()
            
            if new_region is None:
                # User cancelled - keep current region
                return
                
            x, y, width, height = new_region
            
            # Update the recorder's region
            success = self.recorder.update_recording_region(x, y, width, height)
            
            if success:
                self.info_label.config(text=f"Recording: {width}x{height} at ({x}, {y}) [UPDATED]")
                self.status_label.config(text="Region updated - still recording...", fg="orange")
                
                # Flash the status back to recording after 2 seconds
                self.root.after(2000, lambda: self.status_label.config(text="Recording...", fg="red"))
            else:
                messagebox.showwarning("Warning", "Failed to update recording region")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to change region: {str(e)}")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PyRecorderGUI()
    app.run()
