import tkinter as tk
import json
from tkinter import filedialog
from espmega.espmega_r3 import ESPMega_standalone, ESPMega_slave, ESPMega
from dataclasses import dataclass
import sys
import json
import sys
from tkinter import messagebox
import tkinter.messagebox as messagebox

@dataclass
class PhysicalLightEntity:
    controller: ESPMega
    pwm_channel: int

global light_server
global light_server_port
global rapid_mode
global light_map_file
global light_grid
global design_mode

light_map_file = ""  # Default light map file

# Load config.json if it exists
try:
    with open("config.json", "r") as file:
        config = json.load(file)
    light_server = config["light_server"]
    light_server_port = config["light_server_port"]
    rapid_mode = config["rapid_mode"]
    light_map_file = config["light_map_file"]
    design_mode = config["design_mode"]
except FileNotFoundError:
    light_server = ""
    light_server_port = 1883
    rapid_mode = False
    light_map_file = ""
    design_mode = False

# Create a tkinter gui window ask for the light server ip and port and whether to enable rapid response mode
root = tk.Tk()
root.title("ELS Pre-Flight")
root.geometry("500x275")
root.resizable(False, False)

def submit_config():
    global light_server
    global light_server_port
    global rapid_mode
    light_server = light_server_entry.get()
    light_server_port = int(light_server_port_entry.get())
    rapid_mode = rapid_mode_var.get()
    design_mode = design_mode_var.get()
    if light_server == "":
        messagebox.showerror("Error", "Please enter the light server ip.")
        return
    if light_server_port == "":
        messagebox.showerror("Error", "Please enter the light server port.")
        return
    if light_map_file == "":
        messagebox.showerror("Error", "Please select a light map file.")
        return
    # Save the config to config.json
    with open("config.json", "w") as file:
        json.dump({"light_server": light_server, "light_server_port": light_server_port, "rapid_mode": rapid_mode, "light_map_file": light_map_file,"design_mode": design_mode}, file)
    root.destroy()

def open_light_map_file_chooser_dialog():
    global light_map_file
    light_map_file = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    light_map_button.config(text=light_map_file)

# Create a small label to explain design mode
design_mode_label = tk.Label(root, text="Design mode allows you to play with the lights without connecting to a controller.\nThis is useful for testing lighting designs.")
design_mode_label.pack()

# Create a design mode toggle
design_mode_var = tk.BooleanVar()
design_mode_toggle = tk.Checkbutton(root, text="Design Mode", variable=design_mode_var)
design_mode_toggle.pack()

# Create a field to enter the light server ip
light_server_label = tk.Label(root, text="Light Server IP")
light_server_label.pack()
light_server_entry = tk.Entry(root)
light_server_entry.pack()

# Create a field to enter the light server port
light_server_port_label = tk.Label(root, text="Light Server Port")
light_server_port_label.pack()
light_server_port_entry = tk.Entry(root)
light_server_port_entry.pack()

# Create a checkbox to enable rapid response mode
rapid_mode_var = tk.BooleanVar()
rapid_mode_toggle = tk.Checkbutton(root, text="Enable Rapid Response Mode", variable=rapid_mode_var)
rapid_mode_toggle.pack()

# Create a text label for the light map file chooser
light_map_label = tk.Label(root, text="Light Map File")
light_map_label.pack()

# Create a button to open a file dialog asking to select the light map file
light_map_button = tk.Button(root, text="Browse..."if light_map_file=="" else light_map_file, command=open_light_map_file_chooser_dialog)
light_map_button.pack(pady=5)

# Create a button to submit the configuration and close the window
submit_button = tk.Button(root, text="Submit", command=submit_config, pady=5)
submit_button.pack(pady=5)

def open_generate_light_map_template_window():
    light_map_generator_window = tk.Toplevel(root)
    light_map_generator_window.title("Generate Map")
    light_map_generator_window.geometry("250x150")
    light_map_generator_window.resizable(False, False)

    # Create a field to enter the number of rows
    light_map_rows_label = tk.Label(light_map_generator_window, text="Number of Rows")
    light_map_rows_label.pack()
    light_map_rows_entry = tk.Entry(light_map_generator_window)
    light_map_rows_entry.pack()

    # Create a field to enter the number of columns
    light_map_columns_label = tk.Label(light_map_generator_window, text="Number of Columns")
    light_map_columns_label.pack()
    light_map_columns_entry = tk.Entry(light_map_generator_window)
    light_map_columns_entry.pack()

    def submit_light_map_template():
        rows = int(light_map_rows_entry.get())
        columns = int(light_map_columns_entry.get())
        light_map = [[None]*columns]*rows
        # Ask the user where to save the light map template
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        with open(filename, "w") as file:
            json.dump(light_map, file)
        light_map_generator_window.destroy()

    # Create a button to submit the configuration and close the window
    submit_button = tk.Button(light_map_generator_window, text="Submit", command=submit_light_map_template, pady=5)
    submit_button.pack(pady=5)

# Create a button to generate a template light map file with the specified dimensions with all lights disabled
light_map_generate_button = tk.Button(root, text="Generate Light Map Template", command=open_generate_light_map_template_window)
light_map_generate_button.pack(pady=5)

# Fill in the default values
light_server_entry.insert(0, light_server)
light_server_port_entry.insert(0, light_server_port)
rapid_mode_var.set(rapid_mode)
design_mode_var.set(design_mode)

# Start the tkinter main loop
root.mainloop()


print(design_mode)
# Light state constants
LIGHT_DISABLED = -1
LIGHT_OFF = 0
LIGHT_ON = 1
COLOR_ON = "white"
COLOR_OFF = "gray"
COLOR_DISABLED = "gray12"
COLOR_OFF_OFFLINE = "brown4"
COLOR_ON_OFFLINE = "red"

ENABLE_PHYSICAL_SYNCRONIZATION = True

def state_to_color(state: int):
    if state == LIGHT_ON:
        return COLOR_ON
    elif state == LIGHT_OFF:
        return COLOR_OFF
    else:
        return COLOR_DISABLED

def color_to_state(color: str):
    if color == COLOR_ON:
        return LIGHT_ON
    elif color == COLOR_OFF:
        return LIGHT_OFF
    else:
        return LIGHT_DISABLED

class LightGrid:
    def __init__(self, rows: int = 0, columns: int = 0, design_mode: bool = False):
        self.rows = rows
        self.columns = columns
        self.lights: list = [None] * rows * columns
        self.controllers = {}
        self.design_mode = design_mode
    def assign_physical_light(self, row: int, column: int, physical_light: PhysicalLightEntity):
        self.lights[row * self.columns + column] = physical_light
    def get_physical_light(self, row, column):
        return self.lights[row * self.columns + column]
    def set_light_state(self, row: int, column: int, state: bool):
        physical_light = self.get_physical_light(row, column)
        if physical_light and not self.design_mode:
            physical_light.controller.digital_write(physical_light.pwm_channel, state)
    def create_physical_light(self, row: int, column: int, controller: ESPMega, pwm_channel: int):
        self.assign_physical_light(row, column, PhysicalLightEntity(controller, pwm_channel))
    def get_light_state(self, row: int, column: int):
        physical_light = self.get_physical_light(row, column)
        if physical_light:
            return physical_light.controller.get_pwm_state(physical_light.pwm_channel)
        else:
            return None

    def read_light_map(self, light_map: list):
        self.light_map = light_map
        self.rows = len(light_map)
        self.columns = len(light_map[0])
        self.lights = [None] * self.rows * self.columns
        self.controllers = {}  # Dictionary to store existing controllers

        for row_index, row in enumerate(light_map):
            for column_index, light in enumerate(row):
                if light is None:
                    self.assign_physical_light(row_index, column_index, None)
                else:
                    base_topic = light["base_topic"]
                    pwm_id = light["pwm_id"]

                    try:
                        if base_topic in self.controllers:
                            controller = self.controllers[base_topic]
                        else:
                            if not self.design_mode:
                                controller = ESPMega_standalone(base_topic, light_server, light_server_port)
                            else:
                                controller = None
                            if rapid_mode:
                                controller.enable_rapid_response_mode()
                            self.controllers[base_topic] = controller
                        self.create_physical_light(row_index, column_index, controller, pwm_id)
                        self.set_light_state(row_index, column_index, False)
                    except Exception as e:
                        messagebox.showerror("Controller Error", f'The controller at {base_topic} is throwing an error:\n{e}\n\nPlease note that the controller must be connected to the network and running the ESPMega firmware.\n\nYou may continue without this light, but it will not be able to be controlled.')
                        self.assign_physical_light(row_index, column_index, None)
                    

    def read_light_map_from_file(self, filename: str):
        try:
            with open(filename, "r") as file:
                light_map = json.load(file)
            self.read_light_map(light_map)
        except FileNotFoundError:
            messagebox.showerror("File Not Found", f"The file {filename} could not be found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            sys.exit(1)

# Load light map from light_map.json
light_grid = LightGrid(design_mode=design_mode)
light_grid.read_light_map_from_file(filename=light_map_file)
rows = light_grid.rows
columns = light_grid.columns

global playback_active
global current_frame
current_frame = 0
playback_active: bool = False

# -1 if light is disabled, 0 if light is offline, 1 if light is online
def check_light_online(row: int, column: int):
    if(light_grid.light_map[row][column] == None):
        return -1
    if(light_grid.get_physical_light(row, column) == None):
        return 0
    return 1

def set_tile_state(row: int, column: int, state: bool):
    element = lightgrid_frame.grid_slaves(row=row, column=column)[0]
    light_state = check_light_online(row, column)
    if light_state == -1:
        element.config(bg=COLOR_DISABLED)
    elif light_state == 0:
        if state:
            element.config(bg=COLOR_ON_OFFLINE)
        else:
            element.config(bg=COLOR_OFF_OFFLINE)
    else:
        if state:
            element.config(bg=COLOR_ON)
        else:
            element.config(bg=COLOR_OFF)
    if(ENABLE_PHYSICAL_SYNCRONIZATION and light_state != -1):
        light_grid.set_light_state(row, column, state)

def get_tile_state(row: int, column: int):
    element = lightgrid_frame.grid_slaves(row=row, column=column)[0]
    if element.cget("bg") == COLOR_ON or element.cget("bg") == COLOR_ON_OFFLINE:
        return True
    else:
        return False

def change_color(event):
    row = event.widget.grid_info()["row"]
    column = event.widget.grid_info()["column"]
    set_tile_state(row, column, not get_tile_state(row, column))

def add_frame():
    frame = []
    for i in range(rows):
        row = []
        for j in range(columns):
            element_state = get_tile_state(i, j)
            row.append(element_state)
        frame.append(row)
    frames.append(frame)
    slider.config(to=len(frames)-1)  # Update the slider range
    slider.set(len(frames)-1)  # Set the slider value to the last frame
    # Update the slider position
    root.update()

def record_frame():
    frame_index = slider.get()
    frame = []
    for i in range(rows):
        row = []
        for j in range(columns):
            element_state = get_tile_state(i, j)
            row.append(element_state)
        frame.append(row)
    frames[frame_index] = frame
    render_frame_at_index(frame_index)
    # Update the slider position
    root.update()

def delete_frame():
    frame_index = slider.get()
    frames.pop(frame_index)
    slider.config(to=len(frames)-1)  # Update the slider range
    if frame_index > 0:
        slider.set(frame_index-1)
        render_frame_at_index(frame_index-1)
    else:
        slider.set(0)
        render_frame_at_index(0)
    # Update the slider position
    root.update()

def save_animation():
    filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if filename:
        with open(filename, "w") as file:
            json.dump(frames, file)

def move_frame_left():
    frame_index = slider.get()
    if frame_index > 0:
        frames[frame_index], frames[frame_index-1] = frames[frame_index-1], frames[frame_index]
        slider.set(frame_index-1)
        render_frame_at_index(frame_index-1)
    root.update()

def move_frame_right():
    frame_index = slider.get()
    if frame_index < len(frames)-1:
        frames[frame_index], frames[frame_index+1] = frames[frame_index+1], frames[frame_index]
        slider.set(frame_index+1)
        render_frame_at_index(frame_index+1)
    root.update()

def play_frames():
    global animation_id  # Declare animation_id as a global variable
    global playback_active
    global current_frame
    playback_active = True
    current_frame = slider.get()
    while current_frame < len(frames):
        if not playback_active:
            break
        render_frame_at_index(current_frame)
        slider.set(current_frame)  # Update the slider position
        speed = speed_scale.get()  # Get the value of the speed scale
        delay = int(3000 / speed)  # Calculate the delay between frames based on speed
        root.update()
        animation_id = root.after(delay)  # Delay between frames (in milliseconds)
        current_frame = slider.get()
        current_frame += 1
    repeat = repeat_var.get()  # Get the value of the repeat toggle
    if(repeat and playback_active):
        current_frame = 0
        slider.set(current_frame)
        play_frames()

def pause_frames():
    global playback_active
    playback_active = False

def stop_frames():
    global playback_active
    playback_active = False
    slider.set(0)
    render_frame_at_index(0)
    root.after_cancel(animation_id)

def scrub_frames(value):
    frame_index = int(value)
    render_frame_at_index(frame_index)
    root.update()

def render_frame(frame: list):
    for i in range(rows):
        for j in range(columns):
            element = lightgrid_frame.grid_slaves(row=i, column=j)[0]
            set_tile_state(i, j, frame[i][j])
        
def change_light_config(event):
    row = event.widget.grid_info()["row"]
    column = event.widget.grid_info()["column"]
    physical_light = light_grid.get_physical_light(row, column)
    light_config_window = tk.Toplevel(root)
    light_config_window.geometry("250x190")
    light_config_window.title("Light Config")
    light_config_window.resizable(False, False)

    # Define variables for the disable checkbox
    enable_var = tk.BooleanVar()

    def submit_light_config():
        global light_grid
        if enable_var.get():
            base_topic = base_topic_entry.get()
            pwm_id = pwm_id_entry.get()
            if base_topic == "":
                messagebox.showerror("Error", "Please enter a base topic.")
                return
            elif pwm_id == "":
                messagebox.showerror("Error", "Please enter a PWM ID.")
                return
            try:
                pwm_id = int(pwm_id)
            except ValueError:
                messagebox.showerror("Error", "The PWM ID must be an integer.")
                return
            physical_light_config = {"base_topic": base_topic, "pwm_id": pwm_id}
        else:
            physical_light_config = None

        # Update the light map
        modified_light_map = light_grid.light_map
        modified_light_map[row][column] = physical_light_config
        
        # Save the light map to the file
        with open(light_map_file, "w") as file:
            json.dump(light_grid.light_map, file)

        # Reload the light_grid
        light_grid = LightGrid(design_mode=design_mode)
        light_grid.read_light_map(modified_light_map)

        render_frame_at_index(slider.get())
        root.update()
        
        # Close the window
        light_config_window.destroy()

    def checkbox_callback():
        if enable_var.get():
            base_topic_entry.configure(state="normal")
            pwm_id_entry.configure(state="normal")
        else:
            base_topic_entry.configure(state="disabled")
            pwm_id_entry.configure(state="disabled")

    position_label = tk.Label(light_config_window, text=f"Configuring Light at {row+1}, {column+1}")
    position_label.pack()

    state = ""
    if check_light_online(row, column) == -1:
        state = "Disabled"
    elif design_mode:
        state = "Simulated"
    else:
        if check_light_online(row, column) == 0:
            state = "Offline"
        else:
            state = "Online"

    state_label = tk.Label(light_config_window, text=f"This light is currently: {state}")
    state_label.pack()

    light_enable_checkbox = tk.Checkbutton(light_config_window, text="Enable", command=checkbox_callback, variable=enable_var)
    light_enable_checkbox.pack()

    base_topic_label = tk.Label(light_config_window, text="Base Topic")
    base_topic_label.pack()
    base_topic_entry = tk.Entry(light_config_window)
    base_topic_entry.pack()

    pwm_id_label = tk.Label(light_config_window, text="PWM ID")
    pwm_id_label.pack()
    pwm_id_entry = tk.Entry(light_config_window)
    pwm_id_entry.pack()

    submit_button = tk.Button(light_config_window, text="Submit", command=submit_light_config, pady=5)
    submit_button.pack(pady=5)

    if light_grid.light_map[row][column] != None:
        light_enable_checkbox.select()
        base_topic_entry.insert(0, light_grid.light_map[row][column]["base_topic"])
        pwm_id_entry.insert(0, light_grid.light_map[row][column]["pwm_id"])
    else:
        light_enable_checkbox.deselect()
        base_topic_entry.configure(state="disabled")
        pwm_id_entry.configure(state="disabled")

    light_config_window.mainloop()


def render_frame_at_index(frame_index: int):
    frame = frames[frame_index]
    render_frame(frame)
            

frames = [[[0]*light_grid.rows]*light_grid.columns]

root = tk.Tk()

root.title("ESPMega Light Show")


# Create a label for the title
title_label = tk.Label(root, text="ESPMega Light Show", font=("Arial", 24))
title_label.pack()

# Create another frame to the bottom
buttom_frame = tk.Frame(root)
buttom_frame.pack(side="bottom", padx=10)  # Add padding to the right frame

if(design_mode):
    # Create a text label for the design mode
    design_mode_label = tk.Label(buttom_frame, text="You are currently in design mode.\nIn this mode, physical lights will not be controlled.", font=("Arial", 12), fg="red")
    design_mode_label.pack()

# Create a text label for the author
author_label = tk.Label(buttom_frame, text="SIWAT SYSTEM 2023", font=("Arial", 12), fg="gray") 
author_label.pack()

# Create another frame to the right
management_frame = tk.Frame(root)
management_frame.pack(side="right", padx=10)  # Add padding to the right frame

playback_frame = tk.Frame(management_frame)
playback_frame.pack()

# Create a text label for the playback controls
playback_label = tk.Label(playback_frame, text="Playback Controls", font=("Arial", 10))
playback_label.pack()

# Create a button to play the recorded frames
play_button = tk.Button(playback_frame, text="Play", command=play_frames)
play_button.pack()

# Create a button to pause the animation
pause_button = tk.Button(playback_frame, text="Pause", command=pause_frames)
pause_button.pack()

# Create a button to stop the animation
stop_button = tk.Button(playback_frame, text="Stop", command=stop_frames)
stop_button.pack()

# Create a button to delete the current frame
delete_frame_button = tk.Button(playback_frame, text="Delete Frame", command=delete_frame)
delete_frame_button.pack()

# Create a button to move the current frame left
move_frame_left_button = tk.Button(playback_frame, text="Move Frame Left", command=move_frame_left)
move_frame_left_button.pack()

# Create a button to move the current frame right
move_frame_right_button = tk.Button(playback_frame, text="Move Frame Right", command=move_frame_right)
move_frame_right_button.pack()

# Create a button to record a frame
add_frame_button = tk.Button(playback_frame, text="Add Frame", command=add_frame)
add_frame_button.pack()

# Create a button to record a frame to the current frame
record_frame_button = tk.Button(playback_frame, text="Record Frame", command=record_frame)
record_frame_button.pack()

# Create a slider to scrub through recorded frames
slider = tk.Scale(management_frame, label="Frame Scrubber", from_=0, to=len(frames)-1, orient="horizontal", command=scrub_frames)
slider.pack()

# Create a repeat toggle
repeat_var = tk.BooleanVar()
repeat_toggle = tk.Checkbutton(management_frame, text="Repeat", variable=repeat_var)
repeat_toggle.pack()

# Create a scale to adjust playback speed
speed_scale = tk.Scale(management_frame, from_=1, to=10, orient="horizontal", label="Speed", resolution=0.1)
speed_scale.set(5)  # Set the default speed to 5
speed_scale.pack()

lightgrid_frame = tk.Frame(root)
lightgrid_frame.pack()

for i in range(rows):
    for j in range(columns):
        element = tk.Frame(lightgrid_frame, width=50, height=50, bg="white", highlightthickness=1, highlightbackground="black")
        element.grid(row=i, column=j)
        element.bind("<Button-1>", change_color)  # Bind left mouse click event to change_color function
        element.bind("<Button-3>", change_light_config)  # Bind right mouse click event to change_light_config function

def load_animation():
    global frames
    filename = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if filename:
        with open(filename, "r") as file:
            frames = json.load(file)
        slider.config(to=len(frames)-1)  # Update the slider range
        slider.set(0)  # Set the slider value to the first frame

# Create a label for the Save/Load section
save_load_label = tk.Label(management_frame, text="File Management", font=("Arial", 10))
save_load_label.pack()

# Create a button to save the animation
save_button = tk.Button(management_frame, text="Save Animation", command=save_animation)
save_button.pack()

# Add a button to load the animation
load_button = tk.Button(management_frame, text="Load Animation", command=load_animation)
load_button.pack()

render_frame_at_index(0)

root.mainloop()

# Take all connected controllers out of rapid response mode
if rapid_mode:
    for controller in light_grid.controllers.values():
        controller.disable_rapid_response_mode()