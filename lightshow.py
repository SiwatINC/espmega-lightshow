import tkinter as tk

def change_color(event):
    row = event.widget.grid_info()["row"]
    column = event.widget.grid_info()["column"]
    print(f"Clicked element at row {row}, column {column}")
    
    if event.widget.cget("bg") == "red":
        event.widget.config(bg="white")  # Change the background color to white
    else:
        event.widget.config(bg="red")  # Change the background color to red

rows = 6
columns = 6

root = tk.Tk()

# Create a label for the title
title_label = tk.Label(root, text="ESPMega Light Show", font=("Arial", 24))
title_label.pack()

# Create another frame to the right
management_frame = tk.Frame(root)
management_frame.pack(side="right")

# Create a textbox for IP address
ip_label = tk.Label(management_frame, text="IP Address:")
ip_label.pack()

ip_entry = tk.Entry(management_frame)
ip_entry.pack()



lightgrid_frame = tk.Frame(root)
lightgrid_frame.pack()

# Create a grid of elements
for i in range(rows):
    for j in range(columns):
        element = tk.Frame(lightgrid_frame, width=50, height=50, bg="white", highlightthickness=1, highlightbackground="black")
        element.grid(row=i, column=j)
        element.bind("<Button-1>", change_color)  # Bind left mouse click event to change_color function
        
root.mainloop()
