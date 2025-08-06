import tkinter as tk
from PIL import Image, ImageTk
import mss

class RegionSelector:
    def __init__(self):
        self.root = None
        self.canvas = None
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.selected_region = None
        self.screenshot = None
        
    def select_region(self):
        """
        Opens a transparent overlay across ALL monitors where user can draw a rectangle.
        Returns (x, y, width, height) or None if cancelled.
        """
        # Get total screen dimensions across all monitors
        with mss.mss() as sct:
            # Get the combined monitor (monitor 0 = all monitors)
            total_monitor = sct.monitors[0]
            total_width = total_monitor["width"]
            total_height = total_monitor["height"]
            total_left = total_monitor["left"]  
            total_top = total_monitor["top"]
            
        # Create fullscreen transparent overlay window
        self.root = tk.Toplevel()
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.3)  # Make window semi-transparent
        self.root.configure(bg='gray')  # Light gray background
        
        # Position window to cover all monitors
        self.root.geometry(f"{total_width}x{total_height}+{total_left}+{total_top}")
        self.root.overrideredirect(True)  # Remove window decorations after geometry is set
        
        # Create canvas that covers the entire area
        self.canvas = tk.Canvas(
            self.root, 
            highlightthickness=0, 
            bg='gray',
            width=total_width,
            height=total_height
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Instructions at top center
        instruction_text = "🎯 Click and drag to select recording area • ESC to cancel • ENTER to confirm"
        self.canvas.create_text(
            total_width // 2, 50, 
            text=instruction_text, 
            fill='white', 
            font=('Arial', 16, 'bold'),
            tags="instructions"
        )
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # Bind keyboard events  
        self.root.bind("<Escape>", self.cancel_selection)
        self.root.bind("<Return>", self.confirm_selection)
        
        self.canvas.focus_set()
        self.root.focus_force()
        
        # Wait for user selection
        self.root.wait_window()
        
        return self.selected_region
        
    def on_click(self, event):
        """Start drawing rectangle"""
        self.start_x = event.x
        self.start_y = event.y
        
        # Clear any existing rectangle
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            
        # Clear instructions to reduce clutter during drawing
        self.canvas.delete("instructions")
            
    def on_drag(self, event):
        """Update rectangle while dragging"""
        if self.start_x is not None and self.start_y is not None:
            # Clear previous rectangle
            if self.rect_id:
                self.canvas.delete(self.rect_id)
                
            # Draw new rectangle with bright, visible colors
            self.rect_id = self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y,
                outline='red', width=3, fill='red', stipple='gray25'
            )
            
            # Show dimensions
            width = abs(event.x - self.start_x)
            height = abs(event.y - self.start_y)
            
            # Delete previous dimension text
            self.canvas.delete("dimensions")
            
            # Show current dimensions
            mid_x = (self.start_x + event.x) // 2
            mid_y = (self.start_y + event.y) // 2
            self.canvas.create_text(
                mid_x, mid_y, 
                text=f"{width} × {height}px", 
                fill='white', 
                font=('Arial', 14, 'bold'),
                tags="dimensions"
            )
            
    def on_release(self, event):
        """Finish rectangle selection"""
        if self.start_x is not None and self.start_y is not None:
            # Calculate region coordinates (absolute screen coordinates)
            x1, y1 = self.start_x, self.start_y
            x2, y2 = event.x, event.y
            
            # Ensure positive width and height
            x = min(x1, x2)
            y = min(y1, y2)
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            
            # Minimum size check
            if width < 50 or height < 50:
                self.canvas.delete("error_msg")
                self.canvas.create_text(
                    event.x, event.y + 30, 
                    text="❌ Area too small! (minimum 50×50px)", 
                    fill='yellow', 
                    font=('Arial', 14, 'bold'),
                    tags="error_msg"
                )
                return
            
            # Convert to absolute screen coordinates by adding monitor offsets
            with mss.mss() as sct:
                total_monitor = sct.monitors[0]
                offset_x = total_monitor["left"]  # This will be -1920 for your setup
                offset_y = total_monitor["top"]   # This will be 0 for your setup
                
            # Convert canvas coordinates to absolute screen coordinates
            abs_x = x + offset_x
            abs_y = y + offset_y
            
            self.selected_region = (abs_x, abs_y, width, height)
            
            print(f"🎯 Region selected: Canvas({x}, {y}) → Screen({abs_x}, {abs_y}) {width}×{height}")
            print(f"   Offset applied: ({offset_x}, {offset_y})")
            
            # Show confirmation message
            with mss.mss() as sct:
                total_monitor = sct.monitors[0]
                total_width = total_monitor["width"]
                total_height = total_monitor["height"]
            
            self.canvas.delete("confirm_msg")
            self.canvas.create_text(
                total_width // 2, 
                total_height - 100,
                text="✅ Region selected! Press ENTER to confirm or ESC to cancel", 
                fill='lime', 
                font=('Arial', 16, 'bold'),
                tags="confirm_msg"
            )
            
    def confirm_selection(self, event=None):
        """Confirm the selection and close window"""
        if self.selected_region:
            self.root.destroy()
            
    def cancel_selection(self, event=None):
        """Cancel selection and close window"""
        self.selected_region = None
        self.root.destroy()
