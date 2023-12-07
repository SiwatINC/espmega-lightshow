import tkinter as tk

def change_color(event):
    event.widget.config(bg="red")  # Change the background color to red

root = tk.Tk()

# Create a 5x5 grid of elements
for i in range(5):
    for j in range(5):
        element = tk.Frame(root, width=50, height=50, bg="white")
        element.grid(row=i, column=j)
        element.bind("<Button-1>", change_color)  # Bind left mouse click event to change_color function

root.mainloop()
