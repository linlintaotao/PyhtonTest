# just use for test python run with jenkins

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm

x = np.linspace(0, 3 * np.pi, 100)
y = np.sin(x) * 5
dydx = np.cos(0.5 * (x[:-1] + x[1:]))  # first derivative
print(dydx)
colors = []

# Create a set of line segments so that we can color them individually
# This creates the points as a N x 1 x 2 array so that we can stack points
# together easily to get the segments. The segments array for line collection
# needs to be (numlines) x (points per line) x 2 (for x and y)
points = np.array([x, y]).T.reshape(-1, 1, 2)
print(points)

segments = np.concatenate([points[:-1], points[1:]], axis=1)

print(segments)

for i in range(len(segments)):
    if i % 4 == 0:
        colors.append('r')
    else:
        colors.append('green')
fig, axs = plt.subplots()
# Use a boundary norm instead
lc = LineCollection(segments, colors=colors, linestyles='dotted')
lc.set_linewidth(1.5)
axs.add_collection(lc)
axs.set_xlim(x.min(), x.max())
axs.set_ylim(-5.1, 5.1)
plt.show()
