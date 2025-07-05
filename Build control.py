import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import serial
import serial.tools.list_ports
import threading
import time
import math # Still needed for SemicircleSlider, though it's not used for servo control directly anymore
import re # For regular expressions to parse serial data

# --- Custom Semicircle Slider Widget (Kept as a generic component, though no longer used for servo control in this simplified GUI) ---
# This class is still included for completeness, but its instances are removed from the main app.
class SemicircleSlider(tk.Canvas):
    def __init__(self, parent, min_val=0, max_val=180, default_min=30, default_max=150, **kwargs):
        super().__init__(parent, **kwargs)
        self.min_val = min_val
        self.max_val = max_val
        self.current_min = default_min
        self.current_max = default_max

        # Ensure dimensions are integers for canvas drawing
        self.width = int(self.cget("width"))
        self.height = int(self.cget("height"))
        self.center_x = self.width / 2
        self.center_y = self.height - 10 # Adjust to make space for labels/knobs
        self.radius = min(self.center_x, self.center_y) - 20 # Leave some padding

        self.knob_radius = 10
        self.knob1_id = None
        self.knob2_id = None
        self.active_knob = None

        self.bind("<ButtonPress-1>", self._on_button_press)
        self.bind("<B1-Motion>", self._on_mouse_drag)
        self.bind("<ButtonRelease-1>", self._on_button_release)
        self.bind("<Configure>", self._on_resize) # Handle window resizing

        self.draw_slider()

        # Callbacks for when the values change
        self.value_change_callback = None

    def _on_resize(self, event):
        # Update dimensions on resize
        self.width = self.winfo_width()
        self.height = self.winfo_height()
        self.center_x = self.width / 2
        self.center_y = self.height - 10
        self.radius = min(self.center_x, self.center_y) - 20
        self.draw_slider() # Redraw everything

    def draw_slider(self):
        self.delete("all")

        # Draw the background arc (semicircle)
        # Angles for arc are in degrees, 0 is right, 90 is up, 180 is left
        # We want 0-180 degrees to map to 180-0 degrees on the canvas arc (top left to top right)
        # Tkinter arc start/extent: start=0, extent=180 draws from right to left (0 to 180 on a compass)
        # To map servo 0-180 to this, we need to invert: servo_angle -> 180 - servo_angle
        self.create_arc(self.center_x - self.radius, self.center_y - self.radius,
                        self.center_x + self.radius, self.center_y + self.radius,
                        start=0, extent=180, style="arc", outline="#4CAF50", width=4, tags="arc")

        # Draw current sweep range arc
        # Convert servo angles (0-180) to canvas arc angles (180-0)
        # The start of the arc is 180 - max(self.current_min, self.current_max)
        # The extent is abs(self.current_max - self.current_min)
        start_arc_angle = 180 - max(self.current_min, self.current_max)
        extent_arc_angle = abs(self.current_max - self.current_min)

        self.create_arc(self.center_x - self.radius, self.center_y - self.radius,
                        self.center_x + self.radius, self.center_y + self.radius,
                        start=start_arc_angle, extent=extent_arc_angle, style="arc", outline="#2196F3", width=6, tags="range_arc")


        # Draw knobs
        self._draw_knob(self.current_min, "knob1")
        self._draw_knob(self.current_max, "knob2")

        # Draw center line (optional, for visual reference of 90 degrees)
        self.create_line(self.center_x, self.center_y, self.center_x, self.center_y - self.radius, fill="gray", dash=(2,2))

    def _draw_knob(self, angle, tag):
        # Convert servo angle (0-180) to canvas angle (180-0 for arc drawing)
        canvas_angle = 180 - angle

        # Convert degrees to radians for math.cos and math.sin
        rad_angle = math.radians(canvas_angle)

        # Calculate knob position
        x = self.center_x + self.radius * math.cos(rad_angle)
        y = self.center_y - self.radius * math.sin(rad_angle)

        # Draw the knob circle
        knob_id = self.create_oval(x - self.knob_radius, y - self.knob_radius,
                                   x + self.knob_radius, y + self.knob_radius,
                                   fill="#FF5722", outline="#BF360C", width=2, tags=tag)
        if tag == "knob1":
            self.knob1_id = knob_id
        else:
            self.knob2_id = knob_id

    def _on_button_press(self, event):
        x, y = event.x, event.y
        # Check if knob1 was clicked
        if self.find_withtag("knob1") and self.coords(self.knob1_id) and \
           self.coords(self.knob1_id)[0] <= x <= self.coords(self.knob1_id)[2] and \
           self.coords(self.knob1_id)[1] <= y <= self.coords(self.knob1_id)[3]:
            self.active_knob = "knob1"
        # Check if knob2 was clicked
        elif self.find_withtag("knob2") and self.coords(self.knob2_id) and \
             self.coords(self.knob2_id)[0] <= x <= self.coords(self.knob2_id)[2] and \
             self.coords(self.knob2_id)[1] <= y <= self.coords(self.knob2_id)[3]:
            self.active_knob = "knob2"

    def _on_mouse_drag(self, event):
        if self.active_knob:
            x, y = event.x, event.y

            # Calculate angle from mouse position relative to center
            dx = x - self.center_x
            dy = self.center_y - y # Y-axis inverted for standard math angles

            # Avoid division by zero if mouse is exactly at center
            if dx == 0 and dy == 0:
                return

            # Calculate angle in radians, then convert to degrees
            angle_rad = math.atan2(dy, dx)
            angle_deg = math.degrees(angle_rad)

            # Constrain angle to the semicircle (0 to 180 degrees)
            if angle_deg < 0:
                angle_deg = 0 # Prevent going below 0 (right side)
            elif angle_deg > 180:
                angle_deg = 180 # Prevent going above 180 (left side)

            # Convert canvas angle (180-0) back to servo angle (0-180)
            servo_angle = round(180 - angle_deg)

            # Update the active knob's value
            if self.active_knob == "knob1":
                self.current_min = servo_angle
            else:
                self.current_max = servo_angle

            self.draw_slider() # Redraw the slider with updated knob position
            if self.value_change_callback:
                self.value_change_callback(self.current_min, self.current_max)

    def _on_button_release(self, event):
        self.active_knob = None

    def set_value_change_callback(self, callback):
        self.value_change_callback = callback

    def get_min_max_angles(self):
        return self.current_min, self.current_max

    def set_min_max_angles(self, min_angle, max_angle):
        self.current_min = constrain(min_angle, self.min_val, self.max_val)
        self.current_max = constrain(max_angle, self.min_val, self.max_val)
        self.draw_slider()

# Helper function to constrain values (similar to Arduino's constrain)
def constrain(val, min_val, max_val):
    return max(min_val, min(val, max_val))

# --- Custom Toggle Button (for lesion switches) ---
class ToggleButton(ttk.Button):
    # Class-level counter to ensure unique style names
    _instance_count = 0

    def __init__(self, parent, style_obj, text_on="INTACT", text_off="LESION", bg_on="#4CAF50", bg_off="#F44336",
                 fg_on="white", fg_off="white", initial_state=True, command=None, **kwargs):
        kwargs.pop('width', None)
        kwargs.pop('height', None)

        # Generate a unique style name for this instance
        ToggleButton._instance_count += 1
        # Use a base style like 'TButton' for inheritance
        self.unique_style_name = f'LesionToggle{ToggleButton._instance_count}.TButton'
        
        # Configure the style for this unique name, inheriting from 'TButton'
        # This must be done BEFORE calling super().__init__
        style_obj.configure(self.unique_style_name,
                            font=('Inter', 10, 'bold'),
                            padding=(10, 15),
                            borderwidth=2, # Ensure border is consistent
                            relief='raised') # Ensure initial relief is consistent

        # Map the states for this unique style
        # The 'background' and 'foreground' states are mapped here
        style_obj.map(self.unique_style_name,
                      background=[('!disabled', bg_on), ('!disabled', 'pressed', bg_off)],
                      foreground=[('!disabled', fg_on), ('!disabled', 'pressed', fg_off)])

        # Initialize the ttk.Button with the unique style name
        super().__init__(parent, style=self.unique_style_name, **kwargs)
        
        self.text_on = text_on
        self.text_off = text_off
        self.bg_on = bg_on
        self.bg_off = bg_off
        self.fg_on = fg_on
        self.fg_off = fg_off
        self._state = initial_state # True for ON (intact), False for OFF (lesion)
        self._command = command # Store the original command
        self.style_obj = style_obj # Store the style object passed from the app

        self.config(command=self._toggle_state)
        # Call _update_appearance to set the initial text and background based on initial_state
        self._update_appearance()

    def _toggle_state(self):
        self._state = not self._state
        self._update_appearance()
        if self._command:
            self._command(self._state) # Pass the new state (True/False) to the callback

    def _update_appearance(self):
        # Update the button's text based on its internal state
        if self._state:
            self.config(text=self.text_on)
            # When state is ON (INTACT), ensure its background is bg_on
            self.style_obj.map(self.unique_style_name,
                               background=[('!disabled', self.bg_on), ('active', self.bg_on)],
                               foreground=[('!disabled', self.fg_on), ('active', self.fg_on)])
        else:
            self.config(text=self.text_off)
            # When state is OFF (LESION), ensure its background is bg_off
            self.style_obj.map(self.unique_style_name,
                               background=[('!disabled', self.bg_off), ('active', self.bg_off)],
                               foreground=[('!disabled', self.fg_off), ('active', self.fg_off)])


    def get_state(self):
        return self._state

    def set_state(self, state):
        if self._state != state:
            self._state = state
            self._update_appearance()


# --- Main Application Class ---
class IrisControllerApp:
    def __init__(self, master):
        self.master = master
        master.title("Iris Reflex Simulation") # Simplified title
        master.geometry("800x600") # Adjusted smaller window size
        master.resizable(True, True)

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Inter', 11))
        self.style.configure('TButton', font=('Inter', 11, 'bold'), padding=8, borderwidth=2)
        self.style.map('TButton', background=[('active', '!disabled', '#66BB6A'), ('disabled', '#B0B0B0')],
                                 foreground=[('active', '!disabled', 'white'), ('disabled', '#606060')],
                                 bordercolor=[('active', '!disabled', '#4CAF50')])
        self.style.configure('Connect.TButton', background='#2196F3', foreground='white')
        self.style.map('Connect.TButton', background=[('active', '!disabled', '#42A5F5')])
        self.style.configure('Disconnect.TButton', background='#F44336', foreground='white')
        self.style.map('Disconnect.TButton', background=[('active', '!disabled', '#EF5350')])
        self.style.configure('Mode.TRadiobutton', font=('Inter', 12, 'bold'), background='#f0f0f0')
        # Removed the global 'Lesion.TButton' configure/map as it's now handled by each ToggleButton instance


        self.serial_port = None
        self.ser = None
        self.read_thread = None
        self.running = False
        self.arduino_data = {} # Dictionary to store parsed data from Arduino

        # No current_mode StringVar needed as it's fixed to REFLEX
        self.ldr_high_threshold = tk.IntVar(value=400)
        self.ldr_low_threshold = tk.IntVar(value=600)

        # Mapping of lesion pin numbers to their names for GUI and commands
        # These pin numbers MUST match the Arduino sketch's pin definitions
        self.lesion_pins = {
            "Optic Nerve Left": 2, "Optic Nerve Right": 3, # Renamed from Afferent
            "PTN Left": 4, "PTN Right": 5,
            "EWP Left": 6, "EWP Right": 7,
            "CN3 Left": 8, "CN3 Right": 11
        }
        self.lesion_states = {name: tk.BooleanVar(value=True) for name in self.lesion_pins} # True=intact, False=lesion

        self.create_widgets()
        self.update_port_list()

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="15")
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(1, weight=1) # LDR/Lesion row
        main_frame.grid_rowconfigure(2, weight=1) # Console output row

        # --- Top: Port Selection ---
        top_frame = ttk.Frame(main_frame, padding="10")
        top_frame.grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky="ew")
        top_frame.columnconfigure(1, weight=1) # Port combobox

        ttk.Label(top_frame, text="Port:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.port_combobox = ttk.Combobox(top_frame, width=25, state="readonly", font=('Inter', 10))
        self.port_combobox.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.port_combobox.bind("<<ComboboxSelected>>", self.on_port_selected)

        self.refresh_button = ttk.Button(top_frame, text="Refresh", command=self.update_port_list, style='Connect.TButton')
        self.refresh_button.grid(row=0, column=2, padx=5, pady=2)

        self.connect_button = ttk.Button(top_frame, text="Connect", command=self.connect_serial, style='Connect.TButton')
        self.connect_button.grid(row=0, column=3, padx=5, pady=2)

        self.disconnect_button = ttk.Button(top_frame, text="Disconnect", command=self.disconnect_serial, state=tk.DISABLED, style='Disconnect.TButton')
        self.disconnect_button.grid(row=0, column=4, padx=5, pady=2)

        # --- Middle Row: LDR/Thresholds (Left) & Lesion Switches (Right) ---
        # LDR & Threshold Frame
        ldr_frame = ttk.LabelFrame(main_frame, text="Light Sensor (LDR) Control", padding="10")
        ldr_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        ldr_frame.columnconfigure(1, weight=1) # Allow LDR value labels to expand

        ttk.Label(ldr_frame, text="LDR Left:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.ldr_left_label = ttk.Label(ldr_frame, text="---", font=('Inter', 12, 'bold'))
        self.ldr_left_label.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(ldr_frame, text="LDR Right:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.ldr_right_label = ttk.Label(ldr_frame, text="---", font=('Inter', 12, 'bold'))
        self.ldr_right_label.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(ldr_frame, text="Global Light Level:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.global_light_label = ttk.Label(ldr_frame, text="---", font=('Inter', 12, 'bold'))
        self.global_light_label.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        ttk.Separator(ldr_frame, orient="horizontal").grid(row=3, column=0, columnspan=4, sticky="ew", pady=10)

        # LDR Thresholds
        ttk.Label(ldr_frame, text="High Intensity Threshold:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.high_thresh_entry = ttk.Entry(ldr_frame, textvariable=self.ldr_high_threshold, width=10, font=('Inter', 10))
        self.high_thresh_entry.grid(row=4, column=1, padx=5, pady=2, sticky="w")
        ttk.Button(ldr_frame, text="+", width=2, command=lambda: self.adjust_ldr_threshold(self.ldr_high_threshold, 10)).grid(row=4, column=2, padx=1, pady=2)
        ttk.Button(ldr_frame, text="-", width=2, command=lambda: self.adjust_ldr_threshold(self.ldr_high_threshold, -10)).grid(row=4, column=3, padx=1, pady=2)

        ttk.Label(ldr_frame, text="Low Intensity Threshold:").grid(row=5, column=0, padx=5, pady=2, sticky="w")
        self.low_thresh_entry = ttk.Entry(ldr_frame, textvariable=self.ldr_low_threshold, width=10, font=('Inter', 10))
        self.low_thresh_entry.grid(row=5, column=1, padx=5, pady=2, sticky="w")
        ttk.Button(ldr_frame, text="+", width=2, command=lambda: self.adjust_ldr_threshold(self.ldr_low_threshold, 10)).grid(row=5, column=2, padx=1, pady=2)
        ttk.Button(ldr_frame, text="-", width=2, command=lambda: self.adjust_ldr_threshold(self.ldr_low_threshold, -10)).grid(row=5, column=3, padx=1, pady=2)

        self.set_ldr_button = ttk.Button(ldr_frame, text="Apply LDR Thresholds", command=self.send_ldr_thresholds, style='Connect.TButton')
        self.set_ldr_button.grid(row=6, column=0, columnspan=4, pady=10)


        # Lesion Switches Frame
        lesion_frame = ttk.LabelFrame(main_frame, text="Neural Pathway Lesions", padding="10")
        lesion_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        lesion_frame.columnconfigure(0, weight=1)
        lesion_frame.columnconfigure(1, weight=1)

        ttk.Label(lesion_frame, text="Left Eye Pathways", font=('Inter', 11, 'underline')).grid(row=0, column=0, pady=5)
        ttk.Label(lesion_frame, text="Right Eye Pathways", font=('Inter', 11, 'underline')).grid(row=0, column=1, pady=5)

        # Store ToggleButton instances to manage their state
        self.lesion_toggle_buttons = {}
        row_idx = 1
        for name_l, name_r in [("Optic Nerve Left", "Optic Nerve Right"),
                               ("PTN Left", "PTN Right"),
                               ("EWP Left", "EWP Right"),
                               ("CN3 Left", "CN3 Right")]:
            btn_l = ToggleButton(lesion_frame, self.style, text_on=name_l + "\nINTACT", text_off=name_l + "\nLESION",
                                 command=lambda state, n=name_l: self.send_lesion_state(n, state),
                                 initial_state=self.lesion_states[name_l].get())
            btn_l.grid(row=row_idx, column=0, padx=5, pady=5, sticky="ew")
            self.lesion_toggle_buttons[name_l] = btn_l

            btn_r = ToggleButton(lesion_frame, self.style, text_on=name_r + "\nINTACT", text_off=name_r + "\nLESION",
                                 command=lambda state, n=name_r: self.send_lesion_state(n, state),
                                 initial_state=self.lesion_states[name_r].get())
            btn_r.grid(row=row_idx, column=1, padx=5, pady=5, sticky="ew")
            self.lesion_toggle_buttons[name_r] = btn_r
            row_idx += 1

        # Console Output
        console_frame = ttk.LabelFrame(main_frame, text="Arduino Serial Output (Debug)", padding="10")
        console_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        console_frame.grid_rowconfigure(0, weight=1)
        console_frame.grid_columnconfigure(0, weight=1)

        self.console_text = scrolledtext.ScrolledText(console_frame, width=80, height=10, wrap=tk.WORD, font=('Consolas', 9), bg="#1e1e1e", fg="#e0e0e0", insertbackground="white")
        self.console_text.grid(row=0, column=0, sticky="nsew")
        self.console_text.config(state=tk.DISABLED)

        self.update_widget_states()

    def update_port_list(self):
        ports = serial.tools.list_ports.comports()
        port_devices = [port.device for port in ports]
        
        wokwi_option = "Wokwi RFC2217 (localhost:4000)"
        if wokwi_option not in port_devices:
            port_devices.insert(0, wokwi_option)

        self.port_combobox['values'] = port_devices

        if 'COM9' in port_devices:
            self.port_combobox.set('COM9')
            self.serial_port = 'COM9'
        elif wokwi_option in port_devices:
            self.port_combobox.set(wokwi_option)
            self.serial_port = wokwi_option
        elif port_devices:
            self.port_combobox.set(port_devices[0])
            self.serial_port = port_devices[0]
        else:
            self.port_combobox.set("No ports found")
            self.serial_port = None
        self.update_connection_buttons()

    def on_port_selected(self, event):
        self.serial_port = self.port_combobox.get()
        self.update_connection_buttons()

    def update_connection_buttons(self):
        can_connect = bool(self.serial_port and not self.ser)
        self.connect_button.config(state=tk.NORMAL if can_connect else tk.DISABLED)
        self.disconnect_button.config(state=tk.NORMAL if self.ser else tk.DISABLED)
        self.update_widget_states()

    def connect_serial(self):
        if not self.serial_port:
            messagebox.showerror("Connection Error", "Please select a serial port.")
            return
        try:
            if self.serial_port == "Wokwi RFC2217 (localhost:4000)":
                self.ser = serial.serial_for_url('rfc2217://localhost:4000', baudrate=9600)
            else:
                self.ser = serial.Serial(self.serial_port, 9600, timeout=1)
            
            time.sleep(2)
            self.ser.flushInput()
            self.running = True
            self.read_thread = threading.Thread(target=self.read_from_serial, daemon=True)
            self.read_thread.start()
            messagebox.showinfo("Connection Status", f"Connected to {self.serial_port}")
            self.update_connection_buttons()
            self.send_command("SET_MODE:REFLEX")
            self.send_ldr_thresholds()
            for name, var in self.lesion_states.items():
                self.send_lesion_state(name, var.get())

        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not open serial port: {e}")
            self.ser = None
            self.running = False
            self.update_connection_buttons()

    def disconnect_serial(self):
        if self.ser and self.ser.is_open:
            self.running = False
            if self.read_thread and self.read_thread.is_alive():
                self.read_thread.join(timeout=1)
            self.ser.close()
            messagebox.showinfo("Connection Status", "Disconnected from serial port.")
        self.ser = None
        self.update_connection_buttons()

    def read_from_serial(self):
        while self.running and self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8', errors='replace').strip()
                    if line:
                        self.master.after(0, self.update_console, line)
                        if line.startswith("DATA|"):
                            self.master.after(0, self.parse_arduino_data, line)
            except serial.SerialException as e:
                print(f"Serial read error: {e}")
                self.running = False
                self.master.after(0, lambda: messagebox.showerror("Serial Error", f"Serial connection lost: {e}"))
                self.master.after(0, self.disconnect_serial)
                break
            except Exception as e:
                print(f"Unexpected read error: {e}")
                self.running = False
                self.master.after(0, lambda: messagebox.showerror("Error", f"An unexpected error occurred: {e}"))
                self.master.after(0, self.disconnect_serial)
                break
            time.sleep(0.01)

    def update_console(self, text):
        self.console_text.config(state=tk.NORMAL)
        self.console_text.insert(tk.END, text + "\n")
        self.console_text.see(tk.END)
        self.console_text.config(state=tk.DISABLED)

    def parse_arduino_data(self, line):
        if line.startswith("DATA|"):
            parts = line[5:].split('|')
            data = {}
            for part in parts:
                sub_parts = part.split(',')
                for item in sub_parts:
                    if ':' in item:
                        key, value = item.split(':')
                        data[key.strip()] = value.strip()
            self.arduino_data = data
            self.update_gui_from_arduino_data()

    def update_gui_from_arduino_data(self):
        if 'LDR_L' in self.arduino_data:
            self.ldr_left_label.config(text=self.arduino_data['LDR_L'])
        if 'LDR_R' in self.arduino_data:
            self.ldr_right_label.config(text=self.arduino_data['LDR_R'])
        if 'GLL' in self.arduino_data:
            self.global_light_label.config(text=self.arduino_data['GLL'])

    def send_command(self, command):
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(f"{command}\n".encode('utf-8'))
            except serial.SerialException as e:
                messagebox.showerror("Serial Write Error", f"Failed to send command: {e}")
                self.disconnect_serial()
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred while sending command: {e}")
                self.disconnect_serial()

    def on_mode_change(self):
        self.send_command("SET_MODE:REFLEX")
        self.update_widget_states()

    def update_widget_states(self):
        is_connected = bool(self.ser and self.ser.is_open)
        is_reflex_mode = True

        self.high_thresh_entry.config(state=tk.NORMAL if is_connected and is_reflex_mode else tk.DISABLED)
        self.low_thresh_entry.config(state=tk.NORMAL if is_connected and is_reflex_mode else tk.DISABLED)
        self.set_ldr_button.config(state=tk.NORMAL if is_connected and is_reflex_mode else tk.DISABLED)
        
        for name, button_instance in self.lesion_toggle_buttons.items():
            button_instance.config(state=tk.NORMAL if is_connected and is_reflex_mode else tk.DISABLED)

    def adjust_ldr_threshold(self, var, delta):
        current_val = var.get()
        new_val = current_val + delta
        new_val = constrain(new_val, 0, 1023)
        var.set(new_val)

    def send_ldr_thresholds(self):
        if self.ser and self.ser.is_open:
            high = self.ldr_high_threshold.get()
            low = self.ldr_low_threshold.get()
            if high >= low:
                messagebox.showwarning("Threshold Warning", "High Intensity Threshold must be less than Low Intensity Threshold for correct LDR behavior.")
                return
            self.send_command(f"SET_LDR_THRESH:{high},{low}")
        else:
            messagebox.showwarning("Connection Required", "Please connect to Arduino to set LDR Thresholds.")

    def send_lesion_state(self, lesion_name, state):
        if self.ser and self.ser.is_open:
            pin_num = self.lesion_pins[lesion_name]
            pin_state = 1 if state else 0
            self.send_command(f"SET_PIN_STATE:{pin_num},{pin_state}")
        else:
            if lesion_name in self.lesion_toggle_buttons:
                self.lesion_toggle_buttons[lesion_name].set_state(not state)
            messagebox.showwarning("Connection Required", "Please connect to Arduino to change Lesion states.")

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.disconnect_serial()
            self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = IrisControllerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
