import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.patches as patches


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
        raise ValueError("Anchor points are all in line cannot solve it")

    x = (C * E - B * F) / denominator
    y = (A * F - C * D) / denominator

    return x, y


def draw_depot(ax):
    raf_w, raf_h = 3, 20
    koridor_w = 3
    num_blocks = 8

    total_width = num_blocks * raf_w + (num_blocks - 1) * koridor_w
    start_x = -total_width / 2

    for i in range(num_blocks):
        x = start_x + i * (raf_w + koridor_w)
        # üst raf
        ax.add_patch(plt.Rectangle((x, 3), raf_w, raf_h, color='black', alpha=0.3))
        # orta raf
        ax.add_patch(plt.Rectangle((x, 0), raf_w, raf_h, color='black', alpha=0.3))
        # alt raf
        ax.add_patch(plt.Rectangle((x, -3 - raf_h), raf_w, raf_h, color='black', alpha=0.3))


# anchors
anchors = [
    [6, 7.5],
    [9, -3],
    [5, 7.5]
]

distances = [7, 5, 8]

selected_index = None
star = None
circles = []


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
        print("Ranges not integer")
        return


    for circle, a, d in zip(circles, anchors, current_distances):
        circle.center = a
        circle.radius = d

    try:
        pos = trilateration_3anchors(anchors[0], d1, anchors[1], d2, anchors[2], d3)

        if star:
            star.remove()
        star = ax.plot(pos[0], pos[1], 'r*', markersize=12)[0]
        fig.canvas.draw_idle()
    except Exception as e:
        print(e)


def on_press(event):
    global selected_index
    if event.inaxes != ax:
        return
    for i, a in enumerate(anchors):
        distance = ((event.xdata - a[0]) ** 2 + (event.ydata - a[1]) ** 2) ** 0.5
        if distance < 0.5:
            selected_index = i
            break


def on_release(event):
    global selected_index
    selected_index = None


def on_motion(event):
    global selected_index
    if selected_index is None:
        return
    if event.inaxes != ax:
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

    for i in range(3):
        anchor_coord_labels[i].config(text=f"A{i + 1} Pos: ({anchors[i][0]:.2f}, {anchors[i][1]:.2f})")
    fig.canvas.draw_idle()


# --- Tkinter penceresi
root = tk.Tk()
root.title("Warehouse Anchor Position GUI")

frame = ttk.Frame(root)
frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

control_frame = ttk.Frame(root)
control_frame.pack(side=tk.RIGHT, fill=tk.Y)

ttk.Label(control_frame, text="Range A1:").pack()
entry1 = ttk.Entry(control_frame)
entry1.insert(0, str(distances[0]))
entry1.pack()

ttk.Label(control_frame, text="Range A2:").pack()
entry2 = ttk.Entry(control_frame)
entry2.insert(0, str(distances[1]))
entry2.pack()

ttk.Label(control_frame, text="Range A3:").pack()
entry3 = ttk.Entry(control_frame)
entry3.insert(0, str(distances[2]))
entry3.pack()

anchor_coord_labels = []
for i in range(3):
    lbl = ttk.Label(control_frame, text=f"A{i+1} Pos: ({anchors[i][0]}, {anchors[i][1]})")
    lbl.pack()
    anchor_coord_labels.append(lbl)



ttk.Button(control_frame, text="Find Location", command=update_plot).pack(pady=10)

# --- Matplotlib kısmı
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_aspect('equal')
ax.set_xlim(-20, 20)
ax.set_ylim(-20, 20)
ax.grid(True)
ax.set_title("Warehouse topdown view anchor position management")
ax.set_xlabel("X (meter)")
ax.set_ylabel("Y (meter)")

draw_depot(ax)

labels = ['A1', 'A2', 'A3']
colors = ['blue', 'green', 'red']
text_labels = []
coord_texts = []

for a, label, color in zip(anchors, labels, colors):

    t_label = ax.text(a[0] + 0.3, a[1] + 0.3, label, fontsize=10, color=color)

    t_coord = ax.text(a[0] + 0.3, a[1] - 0.7, f"({a[0]:.2f}, {a[1]:.2f})", fontsize=9, color=color)

    text_labels.append(t_label)
    coord_texts.append(t_coord)

# ilk çizim
sc = ax.scatter(
    [a[0] for a in anchors],
    [a[1] for a in anchors],
    s=100,
    c=['blue', 'green', 'red']
)

current_distances = distances.copy()


for a, d, color in zip(anchors, current_distances, ['blue', 'green', 'red']):
    circle = patches.Circle(a, radius=d, linestyle='--', fill=False, color=color, alpha=0.5, linewidth=2)
    ax.add_patch(circle)
    circles.append(circle)

canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# olay bağlama
fig.canvas.mpl_connect("button_press_event", on_press)
fig.canvas.mpl_connect("button_release_event", on_release)
fig.canvas.mpl_connect("motion_notify_event", on_motion)

root.mainloop()