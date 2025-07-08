import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

import sys
import traceback

def show_exception_and_exit(exc_type, exc_value, tb):
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press Enter to close...")
    sys.exit(1)

sys.excepthook = show_exception_and_exit
def trilateration_3anchors(p1, d1, p2, d2, p3, d3):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3

    A = 2 * (x2 - x1)
    B = 2 * (y2 - y1)
    C = d1 ** 2 - d2 ** 2 - x1 ** 2 + x2 ** 2 - y1 ** 2 + y2 ** 2

    D = 2 * (x3 - x1)
    E = 2 * (y3 - y1)
    F = d1 ** 2 - d3 ** 2 - x1 ** 2 + x3 ** 2 - y1 ** 2 + y3 ** 2

    denominator = A * E - B * D
    if denominator == 0:
        raise ValueError("Anchor points are in a line")

    x = (C * E - B * F) / denominator
    y = (A * F - C * D) / denominator
    return x, y


def intersect_two_angles(p1, theta1_deg, p2, theta2_deg):
    x1, y1 = p1
    x2, y2 = p2
    theta1 = math.radians(theta1_deg)
    theta2 = math.radians(theta2_deg)

    m1 = math.tan(theta1)
    m2 = math.tan(theta2)

    if abs(m1 - m2) < 1e-6:
        raise ValueError("Lines are parallel")

    x = ((m1 * x1 - m2 * x2) + (y2 - y1)) / (m1 - m2)
    y = m1 * (x - x1) + y1
    return x, y


def draw_depot(ax):
    raf_w, raf_h = 3, 20
    koridor_w = 3
    num_blocks = 8
    total_width = num_blocks * raf_w + (num_blocks - 1) * koridor_w
    start_x = -total_width / 2
    for i in range(num_blocks):
        x = start_x + i * (raf_w + koridor_w)
        for y_off in [-3 - raf_h, 0, 3]:
            ax.add_patch(plt.Rectangle((x, y_off), raf_w, raf_h, color='black', alpha=0.3))


def update_plot():
    global star
    try:
        d1 = float(entry1.get())
        d2 = float(entry2.get())
        d3 = float(entry3.get())
        current_distances[0] = d1
        current_distances[1] = d2
        current_distances[2] = d3
    except ValueError:
        print("Invalid distances")
        return

    for circle, a, d in zip(circles, anchors, current_distances):
        circle.center = a
        circle.radius = d

    try:
        pos = trilateration_3anchors(anchors[0], d1, anchors[1], d2, anchors[2], d3)
        if star:
            star.remove()
        star = ax.plot(pos[0], pos[1], 'r*', markersize=12)[0]
        result_label.config(text=f"Position: ({pos[0]:.2f}, {pos[1]:.2f})")
        fig.canvas.draw_idle()
    except Exception as e:
        print(e)


def update_plot_with_2angles():
    global star
    try:
        a1 = float(entry_angle1.get())
        a2 = float(entry_angle2.get())
    except ValueError:
        print("Invalid angles")
        return

    try:
        pos = intersect_two_angles(anchors[0], a1, anchors[1], a2)
        if star:
            star.remove()
        star = ax.plot(pos[0], pos[1], 'r*', markersize=12)[0]
        result_label.config(text=f"Position: ({pos[0]:.2f}, {pos[1]:.2f})")
        fig.canvas.draw_idle()
    except Exception as e:
        print(e)


def run_location_finder():
    if mode_var.get() == "3-anchors":
        update_plot()
    else:
        update_plot_with_2angles()


def switch_mode(new_mode):
    mode_var.set(new_mode)
    if new_mode == "3-anchors":
        entry1.pack()
        entry2.pack()
        entry3.pack()
        entry_angle1.pack_forget()
        entry_angle2.pack_forget()
    else:
        entry1.pack_forget()
        entry2.pack_forget()
        entry3.pack_forget()
        entry_angle1.pack()
        entry_angle2.pack()


def on_press(event):
    global selected_index
    if event.inaxes != ax:
        return
    for i, a in enumerate(anchors):
        if ((event.xdata - a[0]) ** 2 + (event.ydata - a[1]) ** 2) ** 0.5 < 0.5:
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
    sc.set_offsets(anchors)
    for circle, a in zip(circles, anchors):
        circle.center = a
    for i, a in enumerate(anchors):
        text_labels[i].set_position((a[0] + 0.3, a[1] + 0.3))
        coord_texts[i].set_position((a[0] + 0.3, a[1] - 0.7))
        coord_texts[i].set_text(f"({a[0]:.2f}, {a[1]:.2f})")
        anchor_coord_labels[i].config(text=f"A{i + 1} Pos: ({a[0]:.2f}, {a[1]:.2f})")
    fig.canvas.draw_idle()


# GUI setup
root = tk.Tk()
root.title("Anchor Positioning GUI")

frame = ttk.Frame(root)
frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

control_frame = ttk.Frame(root)
control_frame.pack(side=tk.RIGHT, fill=tk.Y)

mode_var = tk.StringVar(value="3-anchors")

ttk.Button(control_frame, text="3 Anchor Mode", command=lambda: switch_mode("3-anchors")).pack(pady=2)
ttk.Button(control_frame, text="2 Anchor + 2 Angle Mode", command=lambda: switch_mode("2-angles")).pack(pady=2)

ttk.Label(control_frame, text="Range A1:").pack()
entry1 = ttk.Entry(control_frame)
entry1.insert(0, "7")
entry1.pack()

ttk.Label(control_frame, text="Range A2:").pack()
entry2 = ttk.Entry(control_frame)
entry2.insert(0, "5")
entry2.pack()

ttk.Label(control_frame, text="Range A3:").pack()
entry3 = ttk.Entry(control_frame)
entry3.insert(0, "8")
entry3.pack()

ttk.Label(control_frame, text="Angle from A1 (deg):").pack()
entry_angle1 = ttk.Entry(control_frame)
entry_angle1.insert(0, "45")
entry_angle1.pack_forget()

ttk.Label(control_frame, text="Angle from A2 (deg):").pack()
entry_angle2 = ttk.Entry(control_frame)
entry_angle2.insert(0, "135")
entry_angle2.pack_forget()

anchor_coord_labels = []
for i in range(3):
    lbl = ttk.Label(control_frame, text=f"A{i + 1} Pos: (?)")
    lbl.pack()
    anchor_coord_labels.append(lbl)

result_label = ttk.Label(control_frame, text="Position: (?)")
result_label.pack()

ttk.Button(control_frame, text="Find Location", command=run_location_finder).pack(pady=5)

# Plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_aspect('equal')
ax.set_xlim(-20, 20)
ax.set_ylim(-20, 20)
ax.grid(True)
ax.set_title("Anchor Positioning View")
ax.set_xlabel("X")
ax.set_ylabel("Y")

draw_depot(ax)

anchors = [[6, 7.5], [9, -3], [5, 7.5]]
distances = [7, 5, 8]
current_distances = distances.copy()

colors = ['blue', 'green', 'red']
labels = ['A1', 'A2', 'A3']
text_labels = []
coord_texts = []
circles = []
star = None
selected_index = None

for a, label, color in zip(anchors, labels, colors):
    t_label = ax.text(a[0] + 0.3, a[1] + 0.3, label, fontsize=10, color=color)
    t_coord = ax.text(a[0] + 0.3, a[1] - 0.7, f"({a[0]:.2f}, {a[1]:.2f})", fontsize=9, color=color)
    text_labels.append(t_label)
    coord_texts.append(t_coord)

sc = ax.scatter([a[0] for a in anchors], [a[1] for a in anchors], s=100, c=colors)

for a, d, color in zip(anchors, current_distances, colors):
    circle = patches.Circle(a, radius=d, linestyle='--', fill=False, color=color, alpha=0.5)
    ax.add_patch(circle)
    circles.append(circle)

canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

fig.canvas.mpl_connect("button_press_event", on_press)
fig.canvas.mpl_connect("button_release_event", on_release)
fig.canvas.mpl_connect("motion_notify_event", on_motion)

root.mainloop()

# TODO: Make table for error problems (distance errors)
# TODO: Add Anchor adding and deletion button (distance should be calculated with chosen closest 3 anchors)
# TODO: Cover zone eklenebilir
# TODO: Video yapilabilecek materyal topla
# TODO: Make gray part black
# TODO: Uygunluga gore 2 veya 3 anchor kullanma simulatoru yap (en yakin)
# 80x120 euro palet boyutu