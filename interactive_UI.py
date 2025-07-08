import matplotlib.pyplot as plt

# anchor başlangıç noktaları
anchors = [
    [6, 7.5],
    [9, -3],
    [15, 7.5]
]

# matplotlib figürünü ayarla
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_aspect('equal')
ax.set_xlim(0, 20)
ax.set_ylim(-10, 10)
ax.grid(True)

# scatter plot (sadece anchor noktaları)
sc = ax.scatter(
    [a[0] for a in anchors],
    [a[1] for a in anchors],
    s=100,
    c=['blue', 'green', 'orange']
)

selected_index = None

def on_press(event):
    global selected_index
    if event.inaxes != ax:
        return

    for i, a in enumerate(anchors):
        distance = ((event.xdata - a[0])**2 + (event.ydata - a[1])**2)**0.5
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
    # seçili anchoru yeni koordinata taşı
    anchors[selected_index][0] = event.xdata
    anchors[selected_index][1] = event.ydata
    sc.set_offsets(anchors)
    fig.canvas.draw_idle()

# eventleri bağla
fig.canvas.mpl_connect("button_press_event", on_press)
fig.canvas.mpl_connect("button_release_event", on_release)
fig.canvas.mpl_connect("motion_notify_event", on_motion)

plt.show()
