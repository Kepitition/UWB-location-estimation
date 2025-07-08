import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import random

# --- Global state ---
anchors = [[6, 7.5], [9, -3], [5, 7.5]]
distances = [7.0, 5.0, 8.0]
colors = ['blue', 'green', 'red', 'purple', 'orange', 'brown', 'cyan', 'magenta', 'gray', 'olive']
text_labels = []
coord_texts = []
circles = []
anchor_coord_labels = []
distance_entries = []
star = None
selected_index = None

# --- Trilateration ---
def trilateration_3anchors(p1, d1, p2, d2, p3, d3):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    A = 2 * (x2 - x1)
    B = 2 * (y2 - y1)
    C = d1**2 - d2**2 - x1**2 + x2**2 - y1**2 + y2**2
    D = 2 * (x3 - x1)
    E = 2 * (y3 - y1)
    F = d1**2 - d3**2 - x1**2 + x3**2 - y1**2 + y3**2
    denominator = A * E - B * D
    if denominator == 0:
        raise ValueError("Anchors are aligned")
    x = (C * E - B * F) / denominator
    y = (A * F - C * D) / denominator
    return x, y

# --- UI Functions ---
def update_position():
    global star
    if len(anchors) < 3:
        result_label.config(text="Need at least 3 anchors")
        return
    try:
        # Update distances from entry values
        for i, entry in enumerate(distance_entries):
            distances[i] = float(entry.get())

        # pick closest 3 distances
        d_index = sorted(range(len(distances)), key=lambda i: distances[i])[:3]
        p1, d1 = anchors[d_index[0]], distances[d_index[0]]
        p2, d2 = anchors[d_index[1]], distances[d_index[1]]
        p3, d3 = anchors[d_index[2]], distances[d_index[2]]
        pos = trilateration_3anchors(p1, d1, p2, d2, p3, d3)
        if star:
            star.remove()
        star = ax.plot(pos[0], pos[1], 'r*', markersize=12)[0]
        result_label.config(text=f"Estimated Position: ({pos[0]:.2f}, {pos[1]:.2f})")
        fig.canvas.draw_idle()
    except Exception as e:
        result_label.config(text=str(e))


def redraw_anchors():
    global sc
    for t in text_labels: t.remove()
    for c in coord_texts: c.remove()
    for circle in circles: circle.remove()
    text_labels.clear()
    coord_texts.clear()
    circles.clear()
    for lbl in anchor_coord_labels: lbl.destroy()
    anchor_coord_labels.clear()
    for entry in distance_entries: entry.destroy()
    distance_entries.clear()

    for i, (a, d) in enumerate(zip(anchors, distances)):
        color = colors[i % len(colors)]
        lbl = ttk.Label(control_frame, text=f"A{i+1} Pos: ({a[0]:.2f}, {a[1]:.2f})")
        lbl.pack()
        anchor_coord_labels.append(lbl)

        entry = ttk.Entry(control_frame, width=10)
        entry.insert(0, str(d))
        entry.pack()
        entry.bind("<KeyRelease>", lambda e: update_position())
        distance_entries.append(entry)

        text = ax.text(a[0] + 0.3, a[1] + 0.3, f"A{i+1}", color=color, fontsize=9)
        coord = ax.text(a[0] + 0.3, a[1] - 0.7, f"({a[0]:.2f}, {a[1]:.2f})", color=color, fontsize=8)
        circle = patches.Circle(a, radius=d, fill=False, linestyle='--', color=color, alpha=0.4)
        ax.add_patch(circle)
        text_labels.append(text)
        coord_texts.append(coord)
        circles.append(circle)

    sc.remove()
    sc = ax.scatter([a[0] for a in anchors], [a[1] for a in anchors], s=100, c=[colors[i % len(colors)] for i in range(len(anchors))])
    fig.canvas.draw_idle()


def add_anchor():
    if len(anchors) >= 10:
        result_label.config(text="Max 10 anchors allowed")
        return
    x = random.uniform(-10, 10)
    y = random.uniform(-10, 10)
    anchors.append([x, y])
    distances.append(5.0)
    redraw_anchors()


def remove_anchor():
    if len(anchors) <= 3:
        result_label.config(text="Need minimum 3 anchors")
        return
    anchors.pop()
    distances.pop()
    redraw_anchors()


def on_press(event):
    global selected_index
    if event.inaxes != ax:
        return
    for i, a in enumerate(anchors):
        if ((event.xdata - a[0])**2 + (event.ydata - a[1])**2)**0.5 < 0.5:
            selected_index = i
            break


def on_release(event):
    global selected_index
    selected_index = None


def on_motion(event):
    global selected_index
    if selected_index is None or event.inaxes != ax:
        return
    anchors[selected_index][0] = event.xdata
    anchors[selected_index][1] = event.ydata
    redraw_anchors()
    update_position()

# --- Plot Setup ---
root = tk.Tk()
root.title("Anchor Manager GUI")
frame = ttk.Frame(root)
frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
control_frame = ttk.Frame(root)
control_frame.pack(side=tk.RIGHT, fill=tk.Y)

fig, ax = plt.subplots(figsize=(10, 6))
ax.set_aspect('equal')
ax.set_xlim(-20, 20)
ax.set_ylim(-20, 20)
ax.grid(True)
ax.set_title("Anchor Layout")

sc = ax.scatter([a[0] for a in anchors], [a[1] for a in anchors], s=100, c=colors[:len(anchors)])
result_label = ttk.Label(control_frame, text="Estimated Position: (?)")
result_label.pack()
ttk.Button(control_frame, text="Add Anchor", command=add_anchor).pack(pady=2)
ttk.Button(control_frame, text="Remove Anchor", command=remove_anchor).pack(pady=2)
ttk.Button(control_frame, text="Find Position", command=update_position).pack(pady=2)

canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

fig.canvas.mpl_connect("button_press_event", on_press)
fig.canvas.mpl_connect("button_release_event", on_release)
fig.canvas.mpl_connect("motion_notify_event", on_motion)

redraw_anchors()
root.mainloop()
