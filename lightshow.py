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
    for frame_index, frame in enumerate(frames):
        for i in range(rows):
            for j in range(columns):
                element = lightgrid_frame.grid_slaves(row=i, column=j)[0]
                element.config(bg=frame[i][j])
        root.update()
        slider.set(frame_index)  # Update the slider position
        root.after(500)  # Delay between frames (in milliseconds)

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

# Create another frame to the right
management_frame = tk.Frame(root)
management_frame.pack(side="right", padx=10)  # Add padding to the right frame

# Create a button to play the recorded frames
play_button = tk.Button(management_frame, text="Play Frames", command=play_frames)
play_button.pack()

# Create a button to record a frame
record_button = tk.Button(management_frame, text="Record Frame", command=record_frame)
record_button.pack()

# Create a button to save the animation
save_button = tk.Button(management_frame, text="Save Animation", command=save_animation)
save_button.pack()

# Create a slider to scrub through recorded frames
slider = tk.Scale(management_frame, from_=0, to=len(frames)-1, orient="horizontal", command=scrub_frames)
slider.pack()

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

# Add a button to load the animation
load_button = tk.Button(management_frame, text="Load Animation", command=load_animation)
load_button.pack()

root.mainloop()