import matplotlib
matplotlib.use('Agg') # Using Agg backend for headless environments
import matplotlib.pyplot as plt
import numpy as np
import math
from matplotlib.animation import FuncAnimation
from scipy.spatial import ConvexHull

# 1. Data Generation
np.random.seed(42)
points = np.random.uniform(10, 90, (50, 2))
center = np.mean(points, axis=0)

# Calculate the actual Convex Hull to pre-identify target vertices for the animation
real_hull = ConvexHull(points)
hull_indices = real_hull.vertices 

# Prepare data in polar coordinates for radial processing
polar_data = []
for i, p in enumerate(points):
    dx, dy = p[0] - center[0], p[1] - center[1]
    dist = math.sqrt(dx**2 + dy**2)
    angle = math.atan2(dy, dx)
    polar_data.append({'id': i, 'point': p, 'dist': dist, 'angle': angle})

# Start the circle slightly outside the farthest point
max_dist = max(p['dist'] for p in polar_data) + 5

# 2. Visualization Setup
fig, ax = plt.subplots(figsize=(9, 9))
ax.set_aspect('equal')
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)

# Initial scatter plots
ax.scatter(points[:, 0], points[:, 1], color='gray', alpha=0.3, s=20, label='Inner Points')
circle_plot = plt.Circle(center, max_dist, color='blue', fill=False, linewidth=1.5, alpha=0.5, label='Shrinking Circle')
ax.add_patch(circle_plot)

hull_line, = ax.plot([], [], 'r-', linewidth=2.5, label='Minimal Hull Boundary')
captured_scatter = ax.scatter([], [], color='red', s=80, edgecolors='black', zorder=5, label='Vertex Points')

# List to store vertices as they are captured by the circle
captured_pts = []

def init():
    """Initialize animation elements."""
    hull_line.set_data([], [])
    captured_scatter.set_offsets(np.empty((0, 2)))
    return circle_plot, hull_line, captured_scatter

def update(frame):
    """Update function for each animation frame."""
    # Shrinking circle logic: radius decreases over time
    current_radius = max_dist * (1 - frame / 150)
    circle_plot.set_radius(current_radius)
    
    # Capture only target vertices when the circle reaches their distance
    for p_info in polar_data:
        if p_info['id'] in hull_indices:
            if p_info['dist'] >= current_radius and p_info['id'] not in [p['id'] for p in captured_pts]:
                captured_pts.append(p_info)

    if captured_pts:
        # Sort captured points by angle to maintain a continuous boundary line
        sorted_pts = sorted(captured_pts, key=lambda x: x['angle'])
        pts_coords = np.array([p['point'] for p in sorted_pts])
        
        # Close the loop by connecting the last point to the first
        closed_pts = np.vstack([pts_coords, pts_coords[0]])
        hull_line.set_data(closed_pts[:, 0], closed_pts[:, 1])
        captured_scatter.set_offsets(pts_coords)

    return circle_plot, hull_line, captured_scatter

# Create the animation
ani = FuncAnimation(fig, update, frames=150, init_func=init, blit=True, interval=40, repeat=False)

plt.title("Minimal Convex Hull: Shrinking Circle Algorithm")
plt.legend(loc='upper right')
plt.grid(True, linestyle=':', alpha=0.3)

# Define save path for the animation
save_path = '/home/tnc4y/projects/shrinking-circle-hull/assets/minimal_hull.gif'
print(f"Saving animation to {save_path}...")
try:
    ani.save(save_path, writer='pillow', fps=25)
    print("Animation saved successfully.")
except Exception as e:
    print(f"Error saving animation: {e}")
