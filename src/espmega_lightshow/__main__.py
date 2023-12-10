import tkinter as tk
from tkinter import ttk
import json
from tkinter import filedialog
from espmega.espmega_r3 import ESPMega_standalone, ESPMega_slave, ESPMega
from dataclasses import dataclass
import sys
import json
import sys
from tkinter import messagebox
import tkinter.messagebox as messagebox
import os
from time import sleep, perf_counter
import time
import statistics
from importlib import util as importlib_util
from espmega_lightshow.scripting import UserScript
import shutil
import traceback
import webbrowser

@dataclass
class PhysicalLightEntity:
    controller: ESPMega
    pwm_channel: int

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
            physical_light.controller.digital_write(
                physical_light.pwm_channel, state)

    def create_physical_light(self, row: int, column: int, controller: ESPMega, pwm_channel: int):
        self.assign_physical_light(
            row, column, PhysicalLightEntity(controller, pwm_channel))

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
                                controller = ESPMega_standalone(
                                    base_topic, light_server, light_server_port)
                                if rapid_mode:
                                    controller.enable_rapid_response_mode()
                            else:
                                controller = None
                            self.controllers[base_topic] = controller
                        self.create_physical_light(
                            row_index, column_index, controller, pwm_id)
                        self.set_light_state(row_index, column_index, False)
                    except Exception as e:
                        messagebox.showerror(
                            "Controller Error", f'The controller at {base_topic} is throwing an error:\n{e}\n\nPlease note that the controller must be connected to the network and running the ESPMega firmware.\n\nYou may continue without this light, but it will not be able to be controlled.')
                        self.assign_physical_light(
                            row_index, column_index, None)

    def read_light_map_from_file(self, filename: str):
        try:
            with open(filename, "r") as file:
                light_map = json.load(file)
            # Check if the light map is valid
            if len(light_map) == 0:
                raise Exception("Light map cannot be empty.")
            if len(light_map[0]) == 0:
                raise Exception("Light map cannot be empty.")
            for row in light_map:
                if len(row) != len(light_map[0]):
                    raise Exception(
                        "All rows in the light map must have the same length.")
                for column in row:
                    if column != None:
                        if "base_topic" not in column:
                            raise Exception(
                                "The base_topic field is missing from a light.")
                        if "pwm_id" not in column:
                            raise Exception(
                                "The pwm_id field is missing from a light.")
                        if type(column["base_topic"]) != str:
                            raise Exception(
                                "The base_topic field must be a string.")
                        if type(column["pwm_id"]) != int:
                            raise Exception(
                                "The pwm_id field must be an integer.")
            self.read_light_map(light_map)
        except FileNotFoundError:
            messagebox.showerror(
                "File Not Found", f"The file {filename} could not be found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            sys.exit(1)

def restart():
    python = sys.executable
    os.execl(python, python, * sys.argv)


global light_server
global light_server_port
global rapid_mode
global light_map_file
global light_grid
global design_mode
global animation_quick_load_slots
global script_quick_load_slots
global configured

animation_quick_load_slots = [None]*5
script_quick_load_slots = [None]*5

light_map_file = ""  # Default light map file

# Get Icon File Path
icon_file = os.path.join(os.path.dirname(__file__), "icon.ico")

# Get Logo File Path
logo_file = os.path.join(os.path.dirname(__file__), "logo.png")

# Load config.json if it exists
try:
    with open("config.json", "r") as file:
        config = json.load(file)
    light_server = config["light_server"]
    light_server_port = config["light_server_port"]
    rapid_mode = config["rapid_mode"]
    light_map_file = config["light_map_file"]
    design_mode = config["design_mode"]
    animation_quick_load_slots = config["animation_quick_load_slots"]
    script_quick_load_slots = config["script_quick_load_slots"]
except FileNotFoundError:
    light_server = ""
    light_server_port = 1883
    rapid_mode = False
    light_map_file = ""
    design_mode = False
except KeyError:
    # Delete the config file if it is corrupted
    os.remove("config.json")
    light_server = ""
    light_server_port = 1883
    rapid_mode = False
    light_map_file = ""
    design_mode = False
    # Inform the user that the config file is corrupted and that it has been deleted
    messagebox.showerror(
        "Error", "The config file is corrupted and has been deleted. Please reconfigure the program.")

# Check quick load slots integrity
if len(animation_quick_load_slots) != 5:
    messagebox.showerror(
        "Error", "The animation quick load slots are corrupted and have been reset.")
    animation_quick_load_slots = [None]*5
if len(script_quick_load_slots) != 5:
    messagebox.showerror(
        "Error", "The script quick load slots are corrupted and have been reset.")
    script_quick_load_slots = [None]*5

# Create a tkinter gui window ask for the light server ip and port and whether to enable rapid response mode
root = tk.Tk()
root.title("ELS Pre-Flight")
root.iconbitmap(icon_file)
root.geometry("600x360")
root.resizable(False, False)

configured = False

def submit_config():
    global light_server
    global light_server_port
    global rapid_mode
    global design_mode
    global configured
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
        json.dump({"light_server": light_server, "light_server_port": light_server_port,
                  "rapid_mode": rapid_mode, "light_map_file": light_map_file, "design_mode": design_mode,
                  "script_quick_load_slots": script_quick_load_slots, "animation_quick_load_slots": animation_quick_load_slots}, file)
    configured = True
    root.destroy()


def open_light_map_file_chooser_dialog():
    global light_map_file
    light_map_file = filedialog.askopenfilename(
        filetypes=[("JSON Files", "*.json")])
    light_map_button.config(text=light_map_file)

# Create a label for the title
title_label = ttk.Label(root, text="ESPMega Lightshow Setup", font=("Arial", 24))
title_label.pack()

# Create a small label to explain design mode
design_mode_label = ttk.Label(
    root, text="Design mode allows you to play with the lights without connecting to a controller.\nThis is useful for testing lighting designs.")
design_mode_label.pack()

# Create a design mode toggle
design_mode_var = tk.BooleanVar()
design_mode_toggle = ttk.Checkbutton(
    root, text="Design Mode", variable=design_mode_var)
design_mode_toggle.pack()

# Create a field to enter the light server ip
light_server_label = ttk.Label(root, text="Light Server IP")
light_server_label.pack()
light_server_entry = ttk.Entry(root)
light_server_entry.pack()

# Create a field to enter the light server port
light_server_port_label = ttk.Label(root, text="Light Server Port")
light_server_port_label.pack()
light_server_port_entry = ttk.Entry(root)
light_server_port_entry.pack()

# Create a small label to explain rapid response mode
rapid_response_label = ttk.Label(
    root, text="Rapid response mode makes the lights respond faster by disabling the acknowledgement from the controller.\nThis is useful if multiple lights are being controlled at once and are on the same controller.")
rapid_response_label.pack()

# Create a checkbox to enable rapid response mode
rapid_mode_var = tk.BooleanVar()
rapid_mode_toggle = ttk.Checkbutton(
    root, text="Rapid Response Mode", variable=rapid_mode_var)
rapid_mode_toggle.pack()

# Create a text label for the light map file chooser
light_map_label = ttk.Label(root, text="Light Map File")
light_map_label.pack()

# Create a button to open a file dialog asking to select the light map file
light_map_button = ttk.Button(root, text="Browse..."if light_map_file ==
                             "" else light_map_file, command=open_light_map_file_chooser_dialog)
light_map_button.pack(pady=5)

# Create a button to submit the configuration and close the window
submit_button = ttk.Button(root, text="Submit", command=submit_config)
submit_button.pack(pady=5)


def open_generate_light_map_template_window():
    light_map_generator_window = tk.Toplevel(root)
    light_map_generator_window.title("Generate Map")
    light_map_generator_window.iconbitmap(icon_file)
    light_map_generator_window.geometry("250x130")
    light_map_generator_window.resizable(False, False)

    # Create a field to enter the number of rows
    light_map_rows_label = ttk.Label(
        light_map_generator_window, text="Number of Rows")
    light_map_rows_label.pack()
    light_map_rows_entry = ttk.Entry(light_map_generator_window)
    light_map_rows_entry.pack()

    # Create a field to enter the number of columns
    light_map_columns_label = ttk.Label(
        light_map_generator_window, text="Number of Columns")
    light_map_columns_label.pack()
    light_map_columns_entry = ttk.Entry(light_map_generator_window)
    light_map_columns_entry.pack()

    def submit_light_map_template():
        rows = int(light_map_rows_entry.get())
        columns = int(light_map_columns_entry.get())
        light_map = [[None]*columns]*rows
        # Ask the user where to save the light map template
        filename = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        with open(filename, "w") as file:
            json.dump(light_map, file)
        light_map_generator_window.destroy()

    # Create a button to submit the configuration and close the window
    submit_button = ttk.Button(light_map_generator_window,
                              text="Generate", command=submit_light_map_template)
    submit_button.pack(pady=5)


# Create a button to generate a template light map file with the specified dimensions with all lights disabled
light_map_generate_button = ttk.Button(
    root, text="Generate Light Map Template", command=open_generate_light_map_template_window)
light_map_generate_button.pack(pady=5)

# Fill in the default values
light_server_entry.insert(0, light_server)
light_server_port_entry.insert(0, light_server_port)
rapid_mode_var.set(rapid_mode)
design_mode_var.set(design_mode)

# Start the tkinter main loop
root.mainloop()

# Exit the program if the user closes the window
if not configured:
    sys.exit(0)

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

MIN_BPM = 20
MAX_BPM = 200


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
    if (light_grid.light_map[row][column] == None):
        return -1
    if (light_grid.get_physical_light(row, column) == None):
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
    if (ENABLE_PHYSICAL_SYNCRONIZATION and light_state != -1):
        light_grid.set_light_state(row, column, state)


def get_tile_state(row: int, column: int):
    element = lightgrid_frame.grid_slaves(row=row, column=column)[0]
    if element.cget("bg") == COLOR_ON or element.cget("bg") == COLOR_ON_OFFLINE:
        return True
    else:
        return False


def change_color(event):
    if not playback_active:
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
    # Don't delete the last frame
    if len(frames) == 1:
        return
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
    filename = filedialog.asksaveasfilename(
        defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if filename:
        with open(filename, "w") as file:
            json.dump(frames, file)


def move_frame_left():
    frame_index = slider.get()
    if frame_index > 0:
        frames[frame_index], frames[frame_index -
                                    1] = frames[frame_index-1], frames[frame_index]
        slider.set(frame_index-1)
        render_frame_at_index(frame_index-1)
    root.update()


def move_frame_right():
    frame_index = slider.get()
    if frame_index < len(frames)-1:
        frames[frame_index], frames[frame_index +
                                    1] = frames[frame_index+1], frames[frame_index]
        slider.set(frame_index+1)
        render_frame_at_index(frame_index+1)
    root.update()


def play_frames():
    global animation_id  # Declare animation_id as a global variable
    global playback_active
    global current_frame
    playback_active = True
    current_frame = slider.get()
    # If the current frame is the last frame and repeat is disabled, don't play
    if current_frame == len(frames)-1 and not repeat_var.get():
        playback_active = False
        return
    playback_status_label.config(text="Status: Playing")
    start_time = perf_counter()
    while current_frame < len(frames):
        if not playback_active:
            break
        render_frame_at_index(current_frame)
        slider.set(current_frame)  # Update the slider position
        speed = speed_scale.get()  # Get the value of the speed scale
        # Calculate the delay between frames in milliseconds based on speed
        delay = int(60000 / speed)
        root.update()
        # Delay between frames (in seconds)
        should_increment = True
        while perf_counter() - start_time < delay/1000:
            if not playback_active:
                break
            if speed_scale.get() != speed:
                should_increment = False
                break
            if slider.get() != current_frame:
                should_increment = False
                break
            root.update()
            root.update_idletasks()
        if should_increment:
            current_frame = slider.get()
            current_frame += 1
        else:
            current_frame = slider.get()
        start_time = perf_counter()
    repeat = repeat_var.get()  # Get the value of the repeat toggle
    if (repeat and playback_active):
        current_frame = 0
        slider.set(current_frame)
        play_frames()
    else:
        playback_status_label.config(text="Status: Stopped")



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
    light_config_window.iconbitmap(icon_file)
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
            physical_light_config = {
                "base_topic": base_topic, "pwm_id": pwm_id}
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

    position_label = tk.Label(
        light_config_window, text=f"Configuring Light at {row}, {column}")
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

    state_label = tk.Label(light_config_window,
                           text=f"This light is currently: {state}")
    state_label.pack()

    light_enable_checkbox = tk.Checkbutton(
        light_config_window, text="Enable", command=checkbox_callback, variable=enable_var)
    light_enable_checkbox.pack()

    base_topic_label = tk.Label(light_config_window, text="Base Topic")
    base_topic_label.pack()
    base_topic_entry = tk.Entry(light_config_window)
    base_topic_entry.pack()

    pwm_id_label = tk.Label(light_config_window, text="PWM ID")
    pwm_id_label.pack()
    pwm_id_entry = tk.Entry(light_config_window)
    pwm_id_entry.pack()

    submit_button = tk.Button(
        light_config_window, text="Submit", command=submit_light_config, pady=5)
    submit_button.pack(pady=5)

    if light_grid.light_map[row][column] != None:
        light_enable_checkbox.select()
        base_topic_entry.insert(
            0, light_grid.light_map[row][column]["base_topic"])
        pwm_id_entry.insert(0, light_grid.light_map[row][column]["pwm_id"])
    else:
        light_enable_checkbox.deselect()
        base_topic_entry.configure(state="disabled")
        pwm_id_entry.configure(state="disabled")

    light_config_window.mainloop()


def render_frame_at_index(frame_index: int):
    frame = frames[frame_index]
    render_frame(frame)

def frame_forward():
    frame_index = slider.get()
    if frame_index < len(frames)-1:
        slider.set(frame_index+1)
        render_frame_at_index(frame_index+1)
    if frame_index == len(frames)-1 and repeat_var.get():
        slider.set(0)
        render_frame_at_index(0)
    root.update()

def frame_backward():
    frame_index = slider.get()
    if frame_index > 0:
        slider.set(frame_index-1)
        render_frame_at_index(frame_index-1)
    if frame_index == 0 and repeat_var.get():
        slider.set(len(frames)-1)
        render_frame_at_index(len(frames)-1)
    root.update()

def reconnect_light_controllers():
    global light_grid
    global design_mode
    old_light_map = light_grid.light_map
    light_grid = LightGrid(design_mode=design_mode)
    light_grid.read_light_map(old_light_map)
    render_frame_at_index(slider.get())
    root.update()


frames = [[[0]*light_grid.columns]*light_grid.rows]

root = tk.Tk()

root.title("ESPMega Light Show")
root.iconbitmap(icon_file)


# Create a label for the title
title_label = ttk.Label(root, text="ESPMega Light Show", font=("Helvetica", 36, "bold"), foreground="gray26")
title_label.pack()

# Create another frame to the bottom
buttom_frame = ttk.Frame(root)
buttom_frame.pack(side="bottom", padx=10)  # Add padding to the right frame

# Create a grid to hold the playback controls
playback_grid = ttk.Frame(buttom_frame)
playback_grid.pack()

playback_status_frame = ttk.Frame(playback_grid)

# Create a text label for the playback controls
playback_label = ttk.Label(
    playback_status_frame, text="Playback Controls", font=("Arial", 10))
playback_label.pack()

# Create a text label to show the current playback status
playback_status_label = ttk.Label(playback_status_frame, text="Status: Stopped")
playback_status_label.pack()

playback_status_frame.pack(side="left")

# Create a separator to seperate the playback controls from the playback status
separator = ttk.Separator(playback_grid, orient="vertical")
separator.pack(side="left", padx=10, fill="y")

# Create a frame to hold the button section of the playback controls
playback_section = ttk.Frame(playback_grid)
playback_section.pack(side="left")

# Create a frame to hold the playback controls
playback_button_frame = ttk.Frame(playback_section)
playback_button_frame.pack()

# Create a button to play the recorded frames
play_button = ttk.Button(playback_button_frame, text="Play", command=play_frames)
play_button.pack(side="left")

# Create a button to pause the animation
pause_button = ttk.Button(playback_button_frame, text="Pause", command=pause_frames)
pause_button.pack(side="left")

# Create a button to stop the animation
stop_button = ttk.Button(playback_button_frame, text="Stop", command=stop_frames)
stop_button.pack(side="left")

# Create a frame to hold the repeat toggle and the scrubing controls
manipulation_frame = ttk.Frame(playback_section)
manipulation_frame.pack()

# Create a button that goes to the previous frame
button_previous_frame = ttk.Button(
    manipulation_frame, text="Previous Frame", command=frame_backward)
button_previous_frame.pack(side="left")

# Create a repeat toggle
repeat_var = tk.BooleanVar()
repeat_toggle = ttk.Checkbutton(
    manipulation_frame, text="Repeat", variable=repeat_var)
repeat_toggle.pack(side="left")

# Create a button that goes to the next frame
button_next_frame = ttk.Button(
    manipulation_frame, text="Next Frame", command=frame_forward)
button_next_frame.pack(side="right")

# Add a separator to seperate the playback controls from bpm controls
separator = ttk.Separator(playback_grid, orient="vertical")
separator.pack(side="left", padx=10, fill="y")

# Create a scale to adjust playback speed
speed_scale = tk.Scale(playback_grid, from_=MIN_BPM, to=MAX_BPM,
                       orient="horizontal", label="BPM", resolution=0.1)
speed_scale.set(120)
speed_scale.pack()

# Create a separator to seperate the slider from the top frame
separator = ttk.Separator(buttom_frame, orient="horizontal")
separator.pack(fill="x", pady=10)

# Create a slider to scrub through recorded frames
slider = tk.Scale(buttom_frame, label="Timeline", from_=0, to=len(
    frames)-1, orient="horizontal", command=scrub_frames,length=root.winfo_width()*0.9)
slider.pack()

help_label = ttk.Label(
    buttom_frame, text="Left click to toggle a light.\nRight click to configure a light.", font=("Arial", 12), justify="center")
help_label.pack()

if (design_mode):
    # Create a text label for the design mode
    design_mode_label = ttk.Label(
        buttom_frame, text="You are currently in design mode.\nIn this mode, physical lights will not be controlled.", font=("Arial", 12, "bold"), foreground="red", justify="center")
    design_mode_label.pack()

# Create a text label for the author
author_label = ttk.Label(
    buttom_frame, text="SIWAT SYSTEM 2023", font=("Arial", 12))
author_label.pack()

# Create another frame to the right
management_frame = ttk.Frame(root)
management_frame.pack(side="right", padx=10)  # Add padding to the right frame

playback_frame = ttk.Frame(management_frame)
playback_frame.pack()

# Create a text label for the record controls
record_label = ttk.Label(playback_frame, text="Record Controls", font=("Arial", 10))
record_label.pack()

# Create a separator to seperate the record controls from the label
separator = ttk.Separator(playback_frame, orient="horizontal")
separator.pack(fill="x")

# Create a button to add a frame to the end of the animation
add_frame_button = tk.Button(
    playback_frame, text="Add Frame", command=add_frame, height=4, width=15, bg="green", fg="white")
add_frame_button.pack(pady=5)

# Create a button to record a frame to the current frame
record_frame_button = tk.Button(
    playback_frame, text="Record Frame", command=record_frame, height=4, width=15, bg="red", fg="white")
record_frame_button.pack(pady=5)

# Create a button to delete the current frame
delete_frame_button = tk.Button(
    playback_frame, text="Delete Frame", command=delete_frame, height=4, width=15, bg="firebrick4", fg="white")
delete_frame_button.pack(pady=5)

# Create a separator to seperate the record controls from the label
separator = ttk.Separator(playback_frame, orient="horizontal")
separator.pack(fill="x")

# Create a text label for the frame manipulation controls
frame_manipulation_label = ttk.Label(playback_frame, text="Move Current Frame", font=("Arial", 10))
frame_manipulation_label.pack()

# Create a frame to hold the frame manipulation buttons (move frame left and move frame right)
frame_manipulation_frame = ttk.Frame(playback_frame)
frame_manipulation_frame.pack()

# Create a button to move the current frame left
move_frame_left_button = tk.Button(
    frame_manipulation_frame, text="Left", command=move_frame_left, height=2, width=8, bg="orange", fg="black")
move_frame_left_button.grid(row=1, column=0, pady=5)

# Create a button to move the current frame right
move_frame_right_button = tk.Button(
    frame_manipulation_frame, text="Right", command=move_frame_right, height=2, width=8, bg="orange", fg="black")
move_frame_right_button.grid(row=1, column=1, pady=5)

# Create a separator to seperate the frame manipulation controls from the utility
separator = ttk.Separator(playback_frame, orient="horizontal")
separator.pack(fill="x")

# Create a text label for the utility
utility_label = ttk.Label(management_frame, text="BPM Counter", font=("Arial", 10))
utility_label.pack()



bpm_samples = []

def bpm_counter_callback():
    global last_press_time, bpm_samples
    current_time = time.time()
    if last_press_time is not None:
        bpm = 60 / (current_time - last_press_time)
        bpm_samples.append(bpm)
        if len(bpm_samples) > 5:
            bpm_samples = bpm_samples[-5:]  # Keep only the last 5 samples
        bpm_average = statistics.mean(bpm_samples)
        if len(bpm_samples) == 1:
            bpm_filtered = bpm_samples
        else:
            bpm_filtered = [b for b in bpm_samples if abs(b - bpm_average) <= 2 * statistics.stdev(bpm_samples)]
        bpm = statistics.mean(bpm_filtered)
        bpm_counter_button.config(text=f"{bpm:.2f} BPM")
        
        # Change button color based on BPM
        if bpm < 100:
            bpm_counter_button.config(bg="blue")
        elif bpm >= 100 and bpm < 150:
            bpm_counter_button.config(bg="green")
        else:
            bpm_counter_button.config(bg="red")
        
    last_press_time = current_time

last_press_time = None

# Create a BPM counter button
bpm_counter_button = tk.Button(
    management_frame, text="Click Me!", command=bpm_counter_callback, height=2, width=15, bg="blue", fg="white")
bpm_counter_button.pack(pady=5)

# Create a button to apply the BPM to the speed scale
bpm_apply_button = tk.Button(
    management_frame, text="Apply BPM", command=lambda: speed_scale.set(bpm_counter_button.cget("text").split(" ")[0]), height=2, width=15, bg="blue", fg="white")
bpm_apply_button.pack(pady=5)

lightgrid_frame = ttk.Frame(root)
lightgrid_frame.pack()


def resize_elements(event):
    width = (root.winfo_width() - management_frame.winfo_width()) // columns*0.9
    height = (root.winfo_height() - buttom_frame.winfo_height() -
              title_label.winfo_height())/rows*0.95
    for i in range(rows):
        for j in range(columns):
            element = lightgrid_frame.grid_slaves(row=i, column=j)[0]
            element.config(width=width, height=height)
    slider.config(length=root.winfo_width()*0.9)
    speed_scale.config(length=(root.winfo_width()-playback_section.winfo_width()-playback_status_frame.winfo_width()-20)*0.8)

for i in range(rows):
    for j in range(columns):
        element = tk.Frame(lightgrid_frame, width=50, height=50,
                           bg="white", highlightthickness=1, highlightbackground="black")
        element.grid(row=i, column=j)
        # Bind left mouse click event to change_color function
        element.bind("<Button-1>", change_color)
        # Bind right mouse click event to change_light_config function
        element.bind("<Button-3>", change_light_config)


def load_animation():
    global frames
    filename = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if filename:
        try:
            with open(filename, "r") as file:
                temp_frames = json.load(file)
                # Check if the animation is empty
                if len(temp_frames) == 0:
                    raise Exception("Animation cannot be empty.")
                # Check if the animation has the same dimensions as the light map
                if len(temp_frames[0]) != len(light_grid.light_map) or len(temp_frames[0][0]) != len(light_grid.light_map[0]):
                    raise Exception(
                        "The animation must have the same dimensions as the light map.")
                # Check the animation for invalid frames
                for frame in temp_frames:
                    for row in frame:
                        for light in row:
                            # Check if the light is a boolean value or an integer value of 0 or 1
                            if type(light) != bool and type(light) != int or(type(light) == int and (light != 0 and light != 1)):
                                raise Exception(
                                    "The animation must only contain boolean values.")
                frames = temp_frames
            slider.config(to=len(frames)-1)  # Update the slider range
            slider.set(0)  # Set the slider value to the first frame
        except FileNotFoundError:
            messagebox.showerror(
                "File Not Found", f"The file {filename} could not be found.")
        except Exception as e:
            messagebox.showerror("Load Error", f"{e}\nAre you sure this is a valid animation file?")

def new_animation():
    global frames
    frames = [[[0]*light_grid.columns]*light_grid.rows]
    slider.config(to=len(frames)-1)  # Update the slider range
    slider.set(0)  # Set the slider value to the first frame
    render_frame_at_index(0)


def run_script(filename: str):
    def import_from_file(module_name, file_path):
        spec = importlib_util.spec_from_file_location(module_name, file_path)
        module = importlib_util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    global playback_active

    if filename:
        try:
            print(filename.split(".")[0])
            CustomUserScript = import_from_file(filename.split(".")[0], filename).CustomUserScript
        except FileNotFoundError:
            messagebox.showerror(
                "File Not Found", f"The file {filename} could not be found.")
        except Exception as e:
            messagebox.showerror("Load Error", f"{e}\nAre you sure this is a valid Python script?")
    # At this point, the class "CustomUserScript" should be defined
    # Check if the class is defined
    if not "CustomUserScript" in locals():
        messagebox.showerror("Script Error", "The script must define a class called CustomUserScript.")
        return

    # Check if the class is a subclass of UserScript
    if not issubclass(CustomUserScript, UserScript):
        messagebox.showerror("Script Error", "The class CustomUserScript must be a subclass of UserScript.")
        return

    # Instantiate the class
    script = CustomUserScript(rows, columns, set_tile_state, get_tile_state)

    # Stop Playback if it is active
    if playback_active:
        playback_active = False
    
    # All controls except the speed scale and the BPM counter button
    add_frame_button.config(state="disabled")
    record_frame_button.config(state="disabled")
    delete_frame_button.config(state="disabled")
    move_frame_left_button.config(state="disabled")
    move_frame_right_button.config(state="disabled")
    button_previous_frame.config(state="disabled")
    button_next_frame.config(state="disabled")
    slider.config(state="disabled")
    play_button.config(state="disabled")
    pause_button.config(state="disabled")
    stop_button.config(state="disabled")
    repeat_toggle.config(state="disabled")
    # Lock Run Script button
    file_menu.entryconfig(4, state="disabled")
    # Lock All Quick Load Menu
    for i in range(5):
        quick_run_menu.entryconfig(i, state="disabled")
        quick_run_menu.entryconfig(i+7, state="disabled")
    playback_status_label.config(text="Status: Scripted")
    
    # Create a new window to display the script controls
    script_controls_window = tk.Toplevel(root)
    script_controls_window.title("Script Runner")
    script_controls_window.iconbitmap(icon_file)
    script_controls_window.geometry("250x130")
    script_controls_window.resizable(False, False)
    
    # Add a label to display the script name
    script_name_label = ttk.Label(script_controls_window, text=f"Script: {filename.split('/')[-1]}")
    script_name_label.pack()

    # Add a label to display the script status
    script_status_label = ttk.Label(script_controls_window, text="Status: Running")
    script_status_label.pack()

    # Add a label to display the current frame number
    script_frame_label = ttk.Label(script_controls_window, text="Frame: 0")
    script_frame_label.pack()

    # Add a label to display the current time
    script_time_label = ttk.Label(script_controls_window, text="Time Elapsed: 0")
    script_time_label.pack()

    def stop_script():
        script.active = False

    # Add a stop button to stop the script
    script_stop_button = ttk.Button(script_controls_window, text="Stop", command=stop_script)
    script_stop_button.pack(pady=5)
    start_time = perf_counter()
    begin_time = perf_counter()
    ignore_execution_flag = False
    while True:
        if not script.active:
            break
        # Check if script window is closed
        if not script_controls_window.winfo_exists():
            script.active = False
            break
        # Calculate delay in seconds from bpm
        delay = 60 / speed_scale.get()
        if perf_counter() - start_time >= delay:
            start_time = perf_counter()
            time_epoch = perf_counter() - begin_time
            # Execute the script using try-except to catch errors
            # This script will be written by the user and might contain errors
            try:
                script.__draw_frame__(time_epoch)
            except Exception as e:
                messagebox.showerror("Script Error", traceback.format_exc())
                # Stop the script
                script.active = False
                # Set the ignore execution flag to true to prevent the program from waiting for the script to stop
                ignore_execution_flag = True
                break
            # Update the frame label
            script_frame_label.config(text=f"Frame: {script.frame_count}")
        # Update the time label
        script_time_label.config(text=f"Time Elapsed: {perf_counter() - begin_time:.2f} seconds")
        root.update()
        root.update_idletasks()
    stop_wait_time = 15000
    stop_time = perf_counter()
    # script.execuiting is meant to be set by the script itself to indicate that it is still running
    while script.executing and not ignore_execution_flag:
        if perf_counter() - stop_time >= stop_wait_time:
            messagebox.showerror("Script Error", "The script is taking too long to stop.\nProgram will now restart to prevent the program from freezing.")
            restart()
        root.update()
        root.update_idletasks()
    playback_active = False
    script_controls_window.destroy()
    # Re-enable all controls
    add_frame_button.config(state="normal")
    record_frame_button.config(state="normal")
    delete_frame_button.config(state="normal")
    move_frame_left_button.config(state="normal")
    move_frame_right_button.config(state="normal")
    button_previous_frame.config(state="normal")
    button_next_frame.config(state="normal")
    slider.config(state="normal")
    play_button.config(state="normal")
    pause_button.config(state="normal")
    stop_button.config(state="normal")
    repeat_toggle.config(state="normal")
    # Unlock Run Script button
    file_menu.entryconfig(4, state="normal")
    # Unlock All Quick Load Menu
    quick_run_menu.entryconfig(0, state="normal")
    for i in range(5):
        quick_run_menu.entryconfig(i, state="normal")
        quick_run_menu.entryconfig(i+7, state="normal")
    playback_status_label.config(text="Status: Stopped")
render_frame_at_index(0)

def generate_template_script():
    # Ask the user where to save the script
    filename = filedialog.asksaveasfilename(
        defaultextension=".py", filetypes=[("Python Files", "*.py")])
    # Copy the template script from the module directory to the specified location
    if filename:
        try:
            shutil.copyfile(os.path.join(os.path.dirname(__file__), "template_script.py"), filename)
        except Exception as e:
            messagebox.showerror("Save Error", f"{e}")

root.bind("<Configure>", resize_elements)

def run_script_prompt():
    filename = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
    run_script(filename)

# Create a menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Create the file menu
file_menu = tk.Menu(menu_bar, tearoff=False)
file_menu.add_command(label="New Animation", command=new_animation)
file_menu.add_command(label="Save Animation", command=save_animation)
file_menu.add_command(label="Load Animation", command=load_animation)
file_menu.add_separator()
file_menu.add_command(label="Run Script", command=run_script_prompt)
file_menu.add_command(label="Generate Template Script", command=generate_template_script)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

# Create the controller menu
controller_menu = tk.Menu(menu_bar, tearoff=False)
controller_menu.add_command(
    label="Reconnect Controllers", command=reconnect_light_controllers)
controller_menu.add_command(
    label="Reconfigure Controllers", command=restart)
controller_menu.add_separator()
controller_menu.add_command(
    label="Generate Light Map", command=open_generate_light_map_template_window)
menu_bar.add_cascade(label="Controllers", menu=controller_menu)

def load_animation_at_slot(slot: int):
    global frames
    filename = animation_quick_load_slots[slot-1]
    if (filename == None):
        save_animation_at_slot(slot)
        return
    if filename:
        try:
            with open(filename, "r") as file:
                temp_frames = json.load(file)
                # Check if the animation is empty
                if len(temp_frames) == 0:
                    raise Exception("Animation cannot be empty.")
                # Check if the animation has the same dimensions as the light map
                if len(temp_frames[0]) != len(light_grid.light_map) or len(temp_frames[0][0]) != len(light_grid.light_map[0]):
                    raise Exception(
                        "The animation must have the same dimensions as the light map.")
                # Check the animation for invalid frames
                for frame in temp_frames:
                    for row in frame:
                        for light in row:
                            # Check if the light is a boolean value or an integer value of 0 or 1
                            if type(light) != bool and type(light) != int or(type(light) == int and (light != 0 and light != 1)):
                                raise Exception(
                                    "The animation must only contain boolean values.")
                frames = temp_frames
            slider.config(to=len(frames)-1)  # Update the slider range
            slider.set(0)  # Set the slider value to the first frame
            # Update quick load menu
            quick_run_menu.entryconfig(slot-1, label=f"Animation Slot {slot}: {filename.split('/')[-1]}")
        except FileNotFoundError:
            messagebox.showerror(
                "File Not Found", f"The file {filename} could not be found.")
        except Exception as e:
            messagebox.showerror("Load Error", f"{e}\nAre you sure this is a valid animation file?")
        render_frame_at_index(0)
        if (instant_playback_var.get()):
            play_frames()

# Put script filenames in the quick load menu
def save_script_at_slot(slot: int):
    global script_quick_load_slots
    # Ask the user where the script is located
    filename = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
    if filename:
        script_quick_load_slots[slot-1] = filename
        quick_run_menu.entryconfig(slot+6, label=f"Script Slot {slot}: {filename.split('/')[-1]}")

# Put animation filenames in the quick load menu
def save_animation_at_slot(slot: int):
    global animation_quick_load_slots
    # Ask the user where the animation is located
    filename = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if filename:
        animation_quick_load_slots[slot-1] = filename
        quick_run_menu.entryconfig(slot-1, label=f"Animation Slot {slot}: {filename.split('/')[-1]}")

# Run the script at the specified slot if it is not empty
def load_script_at_slot(slot: int):
    filename = script_quick_load_slots[slot-1]
    print(filename)
    if (filename == None):
        save_script_at_slot(slot)
        return
    run_script(filename)

def clear_animation_slot(slot: int):
    global animation_quick_load_slots
    animation_quick_load_slots[slot-1] = None
    quick_run_menu.entryconfig(slot-1, label=f"Animation Slot {slot}: Empty")

def clear_script_slot(slot: int):
    global script_quick_load_slots
    script_quick_load_slots[slot-1] = None
    quick_run_menu.entryconfig(slot+6, label=f"Script Slot {slot}: Empty")

instant_playback_var = tk.BooleanVar()

# Create the Quick Run menu
quick_run_menu = tk.Menu(menu_bar, tearoff=False)
quick_run_menu.add_command(label="Animation Slot 1: Empty", command=lambda: load_animation_at_slot(1))
quick_run_menu.add_command(label="Animation Slot 2: Empty", command=lambda: load_animation_at_slot(2))
quick_run_menu.add_command(label="Animation Slot 3: Empty", command=lambda: load_animation_at_slot(3))
quick_run_menu.add_command(label="Animation Slot 4: Empty", command=lambda: load_animation_at_slot(4))
quick_run_menu.add_command(label="Animation Slot 5: Empty", command=lambda: load_animation_at_slot(5))
quick_run_menu.add_checkbutton(label="Instant Playback (Disabled)", variable=instant_playback_var, command=lambda: quick_run_menu.entryconfig(5,label="Instant Playback (Enabled)" if instant_playback_var.get() else "Instant Playback (Disabled)"))
quick_run_menu.add_separator()
quick_run_menu.add_command(label="Script Slot 1: Empty", command=lambda: load_script_at_slot(1))
quick_run_menu.add_command(label="Script Slot 2: Empty", command=lambda: load_script_at_slot(2))
quick_run_menu.add_command(label="Script Slot 3: Empty", command=lambda: load_script_at_slot(3))
quick_run_menu.add_command(label="Script Slot 4: Empty", command=lambda: load_script_at_slot(4))
quick_run_menu.add_command(label="Script Slot 5: Empty", command=lambda: load_script_at_slot(5))
quick_run_menu.add_separator()
# Create a submenu to house the clear menu
clear_menu = tk.Menu(quick_run_menu, tearoff=False)
clear_menu.add_command(label="Animation Slot 1", command=lambda: clear_animation_slot(1))
clear_menu.add_command(label="Animation Slot 2", command=lambda: clear_animation_slot(2))
clear_menu.add_command(label="Animation Slot 3", command=lambda: clear_animation_slot(3))
clear_menu.add_command(label="Animation Slot 4", command=lambda: clear_animation_slot(4))
clear_menu.add_command(label="Animation Slot 5", command=lambda: clear_animation_slot(5))
clear_menu.add_separator()
clear_menu.add_command(label="Script Slot 1", command=lambda: clear_script_slot(1))
clear_menu.add_command(label="Script Slot 2", command=lambda: clear_script_slot(2))
clear_menu.add_command(label="Script Slot 3", command=lambda: clear_script_slot(3))
clear_menu.add_command(label="Script Slot 4", command=lambda: clear_script_slot(4))
clear_menu.add_command(label="Script Slot 5", command=lambda: clear_script_slot(5))
clear_menu.add_separator()
clear_menu.add_command(label="Clear All Animation Slots", command=lambda: [clear_animation_slot(i) for i in range(1, 6)])
clear_menu.add_command(label="Clear All Script Slots", command=lambda: [clear_script_slot(i) for i in range(1, 6)])
clear_menu.add_command(label="Clear All", command=lambda: [clear_animation_slot(i) for i in range(1, 6)] + [clear_script_slot(i) for i in range(1, 6)])
quick_run_menu.add_cascade(label="Clear Slot", menu=clear_menu)
menu_bar.add_cascade(label="Quick Load", menu=quick_run_menu)

# Populate the quick run menu with the filenames in the quick load slots
for i in range(5):
    if animation_quick_load_slots[i] != None:
        quick_run_menu.entryconfig(i, label=f"Animation Slot {i+1}: {animation_quick_load_slots[i].split('/')[-1]}")
    if script_quick_load_slots[i] != None:
        quick_run_menu.entryconfig(i+7, label=f"Script Slot {i+1}: {script_quick_load_slots[i].split('/')[-1]}")

def open_about_popup():
    about_popup = tk.Toplevel(root)
    about_popup.title("About")
    about_popup.iconbitmap(icon_file)
    about_popup.geometry("350x110")
    about_popup.resizable(False, False)

    # Create a label for the title
    title_label = ttk.Label(about_popup, text="ESPMega Light Show", font=("Arial", 24))
    title_label.pack()

    # Create a label for the author
    author_label = ttk.Label(about_popup, text="Made by Siwat Sirichai")
    author_label.pack()

    # Create link to the github repository
    def open_github():
        webbrowser.open("https://github.com/SiwatINC/espmega-lightshow/")
    github_link = ttk.Label(about_popup, text="GitHub Repository", foreground="blue", cursor="hand2")
    github_link.pack()
    github_link.bind("<Button-1>", lambda e: open_github())

    # Create a label for the company name
    company_label = ttk.Label(about_popup, text="SIWAT SYSTEM 2023")
    company_label.pack()

# Create the help menu
help_menu = tk.Menu(menu_bar, tearoff=False)
help_menu.add_command(label="About", command=open_about_popup)
help_menu.add_command(label="Documentation", command=lambda: webbrowser.open("https://github.com/SiwatINC/espmega-lightshow/wiki"))
menu_bar.add_cascade(label="Help", menu=help_menu)


# Set the size of the root window
root.geometry("1000x800")

def handle_spacebar(event):
    # Inclement the current frame by 1 then render the frame
    # unless the current frame is the last frame then loop back to the first frame and render it
    if slider.get() == len(frames)-1:
        slider.set(0)
        render_frame_at_index(0)
    else:
        slider.set(slider.get()+1)
        render_frame_at_index(slider.get())

def handle_up_arrow(event):
    # Increase the bpm by 0.5 if increasing the bpm will not cause the value to exceed 200 if it exceeds 200, set it to 200
    if speed_scale.get() + 0.5 <= 200:
        speed_scale.set(speed_scale.get()+0.5)
    else:
        speed_scale.set(200)

def handle_down_arrow(event):
    # Decrease the bpm by 0.5 if decreasing the bpm will not cause the value to go below 40 if it goes below 40, set it to 40
    if speed_scale.get() - 0.5 >= 40:
        speed_scale.set(speed_scale.get()-0.5)
    else:
        speed_scale.set(40)

def handle_left_arrow(event):
    # Decrement the current frame by 1 then render the frame
    # unless the current frame is the first frame then loop back to the last frame and render it
    if slider.get() == 0:
        slider.set(len(frames)-1)
        render_frame_at_index(len(frames)-1)
    else:
        slider.set(slider.get()-1)
        render_frame_at_index(slider.get())

def handle_right_arrow(event):
    # Increment the current frame by 1 then render the frame
    # unless the current frame is the last frame then loop back to the first frame and render it
    if slider.get() == len(frames)-1:
        slider.set(0)
        render_frame_at_index(0)
    else:
        slider.set(slider.get()+1)
        render_frame_at_index(slider.get())

root.bind("<space>", handle_spacebar)
root.bind("<Up>", handle_up_arrow)
root.bind("<Down>", handle_down_arrow)
root.bind("<Left>", handle_left_arrow)
root.bind("<Right>", handle_right_arrow)


root.mainloop()

# Write Quick Load data to file
with open("config.json", "w") as file:
    json.dump({"light_server": light_server, "light_server_port": light_server_port,
                "rapid_mode": rapid_mode, "light_map_file": light_map_file, "design_mode": design_mode,
                "script_quick_load_slots": script_quick_load_slots, "animation_quick_load_slots": animation_quick_load_slots}, file)

# Take all connected controllers out of rapid response mode
if rapid_mode:
    for controller in light_grid.controllers.values():
        controller.disable_rapid_response_mode()
