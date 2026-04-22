import math

def get_convex_hull_shrinking_circle(points):
    """
    Pure Python implementation of the Convex Hull algorithm using 
    Shrinking Circle (Radial Sweep) logic.
    Returns the minimal set of vertex points.
    """
    if len(points) <= 2:
        return points

    # 1. Find the Centroid (Arithmetic Mean)
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    center = (cx, cy)

    # 2. Radial Sweep (Sort by Angle)
    # If multiple points share the same angle, choose the one farthest from the center 
    # (the first one hit by the shrinking circle).
    def get_polar_info(p):
        dx, dy = p[0] - center[0], p[1] - center[1]
        angle = math.atan2(dy, dx)
        dist_sq = dx**2 + dy**2
        return angle, dist_sq, p

    # Sort ascending by angle, and descending by distance to keep the outermost point for each angle
    sorted_points_info = sorted([get_polar_info(p) for p in points], key=lambda x: (x[0], -x[1]))

    # Filter out inner points sharing the same angle
    candidates = []
    last_angle = None
    for angle, dist_sq, p in sorted_points_info:
        if angle != last_angle:
            candidates.append(p)
            last_angle = angle

    # 3. Minimization (Keep Only Vertices)
    # Use cross product to check for convexity (Graham Scan-like check)
    def cross_product(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    hull = []
    for p in candidates:
        # If the new point 'p' makes the turn non-convex, pop the last point
        while len(hull) >= 2 and cross_product(hull[-2], hull[-1], p) <= 0:
            hull.pop()
        hull.append(p)

    # Cleanup potential redundancies at the wrap-around point (360 degrees)
    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(hull) and len(hull) > 2:
            prev = hull[i-1]
            curr = hull[i]
            nxt = hull[(i+1) % len(hull)]
            if cross_product(prev, curr, nxt) <= 0:
                hull.pop(i)
                changed = True
            else:
                i += 1

    return hull

# --- Example Usage ---
if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt

    # Generate test data (Random points)
    np.random.seed(42)
    test_points = np.random.uniform(10, 90, (30, 2)).tolist()
    # Add some explicit edge cases
    test_points.extend([(5, 5), (95, 5), (5, 95), (95, 95)])

    result = get_convex_hull_shrinking_circle(test_points)

    print(f"Input Points: {len(test_points)}")
    print(f"Output (Vertex) Points: {len(result)}")
    print("-" * 20)
    
    # Visualization
    plt.figure(figsize=(8, 8))
    pts = np.array(test_points)
    plt.scatter(pts[:, 0], pts[:, 1], color='gray', alpha=0.5, label='All Points')
    
    hull_pts = np.array(result)
    # Close the hull loop for drawing
    closed_hull = np.vstack([hull_pts, hull_pts[0]])
    
    plt.plot(closed_hull[:, 0], closed_hull[:, 1], 'r-', linewidth=2, label='Minimal Hull')
    plt.scatter(hull_pts[:, 0], hull_pts[:, 1], color='red', s=80, label='Vertices')
    
    plt.title("Minimal Convex Hull Algorithm Test")
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.show()
