import tkinter as tk
import json
from tkinter import filedialog
from espmega.espmega_r3 import ESPMega_standalone, ESPMega_slave, ESPMega
from dataclasses import dataclass

@dataclass
class PhysicalLightEntity:
    controller: ESPMega
    pwm_channel: int

light_server ="192.168.0.26"
light_server_port = 1883

# Light state constants
LIGHT_DISABLED = -1
LIGHT_OFF = 0
LIGHT_ON = 1
COLOR_ON = "red"
COLOR_OFF = "white"
COLOR_DISABLED = "gray"

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

# Light map data structure example
light_map = [[{"base_topic": "espmega/1","pwm_id":0},{"base_topic": "espmega/1","pwm_id":1},{"base_topic": "espmega/1","pwm_id":2}],
            [{"base_topic": "espmega/2","pwm_id":0},{"base_topic": "espmega/2","pwm_id":1},{"base_topic": "espmega/2","pwm_id":2}]]

class LightGrid:
    def __init__(self, rows: int = 0, columns: int = 0):
        self.rows = rows
        self.columns = columns
        self.lights: list = [None] * rows * columns
    def assign_physical_light(self, row: int, column: int, physical_light: PhysicalLightEntity):
        self.lights[row * self.columns + column] = physical_light
    def get_physical_light(self, row, column):
        return self.lights[row * self.columns + column]
    def set_light_state(self, row: int, column: int, state: bool):
        physical_light = self.get_physical_light(row, column)
        if physical_light:
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
        self.rows = len(light_map)
        self.columns = len(light_map[0])
        self.lights = [None] * self.rows * self.columns
        existing_controllers = {}  # Dictionary to store existing controllers

        for row_index, row in enumerate(light_map):
            for column_index, light in enumerate(row):
                if light is None:
                    self.assign_physical_light(row_index, column_index, None)
                else:
                    base_topic = light["base_topic"]
                    pwm_id = light["pwm_id"]

                    if base_topic in existing_controllers:
                        controller = existing_controllers[base_topic]
                    else:
                        controller = ESPMega_standalone(base_topic, light_server, light_server_port)
                        existing_controllers[base_topic] = controller

                    self.create_physical_light(row_index, column_index, controller, pwm_id)
    def read_light_map_from_file(self, filename: str):
        with open(filename, "r") as file:
            light_map = json.load(file)
        self.read_light_map(light_map)

# Load light map from light_map.json
light_grid = LightGrid()
light_grid.read_light_map_from_file(filename="light_map.json")
rows = light_grid.rows
columns = light_grid.columns

global playback_active
playback_active: bool = False
def change_color(event):
    row = event.widget.grid_info()["row"]
    column = event.widget.grid_info()["column"]
    print(f"Clicked element at row {row}, column {column}")
    if event.widget.cget("bg") != COLOR_DISABLED:
        if event.widget.cget("bg") == COLOR_ON:
            event.widget.config(bg=COLOR_OFF)  # Change the background color to white
        else:
            event.widget.config(bg=COLOR_ON)  # Change the background color to red

def record_frame():
    frame = []
    for i in range(rows):
        row = []
        for j in range(columns):
            element = lightgrid_frame.grid_slaves(row=i, column=j)[0]
            element_color = element.cget("bg")
            element_state = color_to_state(element_color)
            row.append(element_state)
        frame.append(row)
    frames.append(frame)
    slider.config(to=len(frames)-1)  # Update the slider range
    slider.set(len(frames)-1)  # Set the slider value to the last frame
    print("Frame recorded")
    # Update the slider position
    root.update()

def save_animation():
    filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if filename:
        with open(filename, "w") as file:
            json.dump(frames, file)
        print(f"Animation saved to {filename}")

def play_frames():
    global animation_id  # Declare animation_id as a global variable
    global playback_active
    playback_active = True
    for frame_index, frame in enumerate(frames):
        if not playback_active:
            break
        render_frame(frame)
        root.update()
        slider.set(frame_index)  # Update the slider position
        speed = speed_scale.get()  # Get the value of the speed scale
        delay = int(1000 / speed)  # Calculate the delay between frames based on speed
        animation_id = root.after(delay)  # Delay between frames (in milliseconds)
    repeat = repeat_var.get()  # Get the value of the repeat toggle
    if(repeat and playback_active):
        play_frames()

def stop_frames():
    global playback_active
    playback_active = False
    root.after_cancel(animation_id)

def scrub_frames(value):
    frame_index = int(value)
    frame = frames[frame_index]
    render_frame(frame)
    root.update()

def render_frame(frame: list):
    for i in range(rows):
        for j in range(columns):
            element = lightgrid_frame.grid_slaves(row=i, column=j)[0]
            print(light_grid.get_physical_light(i, j))
            if light_grid.get_physical_light(i, j) == None:
                element.config(bg=COLOR_DISABLED)
            element.config(bg=state_to_color(frame[i][j]))

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

# Create a text label for the author
author_label = tk.Label(buttom_frame, text="SIWAT SYSTEM 2023", font=("Arial", 12), fg="gray") 
author_label.pack()

# Create another frame to the right
management_frame = tk.Frame(root)
management_frame.pack(side="right", padx=10)  # Add padding to the right frame

playback_frame = tk.Frame(management_frame)
playback_frame.pack()

# Create a button to play the recorded frames
play_button = tk.Button(playback_frame, text="Play", command=play_frames)
play_button.pack()

# Create a button to stop the animation
stop_button = tk.Button(playback_frame, text="Stop", command=stop_frames)
stop_button.pack()

# Create a button to record a frame
record_button = tk.Button(playback_frame, text="Record", command=record_frame)
record_button.pack()

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

def load_animation():
    global frames
    filename = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if filename:
        with open(filename, "r") as file:
            frames = json.load(file)
        slider.config(to=len(frames)-1)  # Update the slider range
        slider.set(0)  # Set the slider value to the first frame
        print(f"Animation loaded from {filename}")

# Create a button to save the animation
save_button = tk.Button(management_frame, text="Save Animation", command=save_animation)
save_button.pack()

# Add a button to load the animation
load_button = tk.Button(management_frame, text="Load Animation", command=load_animation)
load_button.pack()

render_frame_at_index(0)

root.mainloop()