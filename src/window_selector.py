import tkinter as tk
from tkinter import ttk, messagebox
import pygetwindow as gw

class WindowSelector:
    def __init__(self):
        self.selected_window = None
        
    def select_window(self):
        """
        Opens a dialog to select which window to record.
        Returns (x, y, width, height) or None if cancelled.
        """
        # Get all visible windows
        windows = []
        for window in gw.getAllWindows():
            if window.title and window.visible and window.width > 0 and window.height > 0:
                # Exclude our own windows
                if "PyRecorder" not in window.title and window.title != "":
                    windows.append(window)
        
        if not windows:
            messagebox.showwarning("No Windows", "No suitable windows found to record.")
            return None
            
        # Create selection dialog
        dialog = tk.Toplevel()
        dialog.title("Select Window to Record")
        dialog.geometry("500x400")
        dialog.resizable(True, True)
        dialog.grab_set()  # Make dialog modal
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"500x400+{x}+{y}")
        
        # Instructions
        instruction_label = tk.Label(dialog, text="Select a window to record:", 
                                   font=("Arial", 12, "bold"))
        instruction_label.pack(pady=10)
        
        # Create listbox with scrollbar
        frame = tk.Frame(dialog)
        frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Arial", 10))
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Populate listbox with window information
        window_data = []
        for i, window in enumerate(windows):
            try:
                title = window.title[:50] + "..." if len(window.title) > 50 else window.title
                size_info = f"{window.width}x{window.height}"
                display_text = f"{title} ({size_info})"
                listbox.insert(tk.END, display_text)
                window_data.append(window)
            except Exception:
                continue  # Skip windows that can't be accessed
                
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                self.selected_window = window_data[selection[0]]
                dialog.destroy()
            else:
                messagebox.showwarning("No Selection", "Please select a window.")
                
        def on_cancel():
            self.selected_window = None
            dialog.destroy()
            
        select_button = tk.Button(button_frame, text="Select", command=on_select,
                                bg="#4CAF50", fg="white", font=("Arial", 12),
                                width=10)
        select_button.pack(side=tk.LEFT, padx=10)
        
        cancel_button = tk.Button(button_frame, text="Cancel", command=on_cancel,
                                bg="#f44336", fg="white", font=("Arial", 12),
                                width=10)
        cancel_button.pack(side=tk.LEFT, padx=10)
        
        # Refresh button
        def refresh_windows():
            listbox.delete(0, tk.END)
            window_data.clear()
            
            updated_windows = []
            for window in gw.getAllWindows():
                if window.title and window.visible and window.width > 0 and window.height > 0:
                    if "PyRecorder" not in window.title and window.title != "":
                        updated_windows.append(window)
            
            for window in updated_windows:
                try:
                    title = window.title[:50] + "..." if len(window.title) > 50 else window.title
                    size_info = f"{window.width}x{window.height}"
                    display_text = f"{title} ({size_info})"
                    listbox.insert(tk.END, display_text)
                    window_data.append(window)
                except Exception:
                    continue
                    
        refresh_button = tk.Button(button_frame, text="Refresh", command=refresh_windows,
                                 bg="#2196F3", fg="white", font=("Arial", 12),
                                 width=10)
        refresh_button.pack(side=tk.LEFT, padx=10)
        
        # Double-click to select
        def on_double_click(event):
            on_select()
            
        listbox.bind("<Double-Button-1>", on_double_click)
        
        # Wait for dialog to close
        dialog.wait_window()
        
        if self.selected_window:
            try:
                # Get window position and size
                return (self.selected_window.left, self.selected_window.top, 
                       self.selected_window.width, self.selected_window.height)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to get window information: {str(e)}")
                return None
        
        return None
