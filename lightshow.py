import tkinter as tk
import json
from tkinter import filedialog

def change_color(event):
    row = event.widget.grid_info()["row"]
    column = event.widget.grid_info()["column"]
    print(f"Clicked element at row {row}, column {column}")
    
    if event.widget.cget("bg") == "red":
        event.widget.config(bg="white")  # Change the background color to white
    else:
        event.widget.config(bg="red")  # Change the background color to red

def record_frame():
    frame = []
    for i in range(rows):
        row = []
        for j in range(columns):
            element = lightgrid_frame.grid_slaves(row=i, column=j)[0]
            row.append(element.cget("bg"))
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
    speed = speed_scale.get()  # Get the value of the speed scale
    delay = int(1000 / speed)  # Calculate the delay between frames based on speed
    for frame_index, frame in enumerate(frames):
        for i in range(rows):
            for j in range(columns):
                speed = speed_scale.get()  # Get the value of the speed scale
                delay = int(1000 / speed)  # Calculate the delay between frames based on speed
                element = lightgrid_frame.grid_slaves(row=i, column=j)[0]
                element.config(bg=frame[i][j])
        root.update()
        slider.set(frame_index)  # Update the slider position
        root.after(delay)  # Delay between frames (in milliseconds)

    repeat = repeat_var.get()  # Get the value of the repeat toggle
    if(repeat):
        play_frames()

def scrub_frames(value):
    frame_index = int(value)
    frame = frames[frame_index]
    for i in range(rows):
        for j in range(columns):
            element = lightgrid_frame.grid_slaves(row=i, column=j)[0]
            element.config(bg=frame[i][j])
    root.update()

frames = []

rows = 6
columns = 6

root = tk.Tk()

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

# Create a button to play the recorded frames
play_button = tk.Button(management_frame, text="Play Frames", command=play_frames)
play_button.pack()

# Create a button to record a frame
record_button = tk.Button(management_frame, text="Record Frame", command=record_frame)
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

root.mainloop()