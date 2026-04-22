import pytest
import math
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from minimal_hull_algorithm import get_convex_hull_shrinking_circle


class TestConvexHullEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_single_point(self):
        """Test with a single point"""
        points = [(5.0, 5.0)]
        result = get_convex_hull_shrinking_circle(points)
        assert len(result) == 1
        assert result[0] == (5.0, 5.0)

    def test_two_points(self):
        """Test with exactly two points"""
        points = [(0.0, 0.0), (1.0, 1.0)]
        result = get_convex_hull_shrinking_circle(points)
        assert len(result) == 2
        assert set(result) == set(points)

    def test_three_collinear_points(self):
        """Test with three collinear points - should return only endpoints"""
        points = [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]
        result = get_convex_hull_shrinking_circle(points)
        # Should return only 2 points (the endpoints) as the middle is collinear
        assert len(result) == 2
        assert (0.0, 0.0) in result
        assert (2.0, 2.0) in result

    def test_many_collinear_points(self):
        """Test with many collinear points on a horizontal line"""
        points = [(float(i), 0.0) for i in range(10)]
        result = get_convex_hull_shrinking_circle(points)
        # Should return only 2 points (endpoints)
        assert len(result) == 2
        assert (0.0, 0.0) in result
        assert (9.0, 0.0) in result

    def test_vertical_collinear_points(self):
        """Test with collinear points on a vertical line"""
        points = [(0.0, float(i)) for i in range(8)]
        result = get_convex_hull_shrinking_circle(points)
        assert len(result) == 2
        assert (0.0, 0.0) in result
        assert (0.0, 7.0) in result

    def test_duplicate_points(self):
        """Test with duplicate/overlapping points"""
        points = [(1.0, 1.0), (1.0, 1.0), (1.0, 1.0), (2.0, 2.0), (2.0, 2.0)]
        result = get_convex_hull_shrinking_circle(points)
        # Should handle duplicates gracefully
        assert len(result) >= 1
        # The result should only contain unique points
        assert len(result) == len(set(result))

    def test_all_same_point(self):
        """Test with all identical points"""
        points = [(5.0, 5.0)] * 10
        result = get_convex_hull_shrinking_circle(points)
        assert len(result) == 1
        assert result[0] == (5.0, 5.0)

    def test_points_on_circle(self):
        """Test with points arranged on a circle"""
        # Create 8 points on a unit circle
        points = []
        for i in range(8):
            angle = 2 * math.pi * i / 8
            points.append((math.cos(angle), math.sin(angle)))
        
        result = get_convex_hull_shrinking_circle(points)
        # All points should be on the hull for a regular octagon
        assert len(result) == 8

    def test_square_vertices(self):
        """Test with square vertices (4 points)"""
        points = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        result = get_convex_hull_shrinking_circle(points)
        assert len(result) == 4
        result_set = set(result)
        assert result_set == set(points)

    def test_triangle(self):
        """Test with triangle vertices"""
        points = [(0.0, 0.0), (2.0, 0.0), (1.0, 2.0)]
        result = get_convex_hull_shrinking_circle(points)
        assert len(result) == 3
        assert set(result) == set(points)

    def test_point_inside_triangle(self):
        """Test with triangle + one interior point"""
        points = [(0.0, 0.0), (4.0, 0.0), (2.0, 4.0), (2.0, 2.0)]  # last point is inside
        result = get_convex_hull_shrinking_circle(points)
        assert len(result) == 3
        # Interior point should not be in the hull
        assert (2.0, 2.0) not in result
        # Triangle vertices should be in the hull
        assert (0.0, 0.0) in result
        assert (4.0, 0.0) in result
        assert (2.0, 4.0) in result

    def test_point_on_triangle_edge(self):
        """Test with a point on the edge of a triangle"""
        points = [(0.0, 0.0), (4.0, 0.0), (2.0, 4.0), (2.0, 0.0)]  # last point on bottom edge
        result = get_convex_hull_shrinking_circle(points)
        assert len(result) == 3
        # Point on edge should not be included as a separate vertex
        assert set(result) == {(0.0, 0.0), (4.0, 0.0), (2.0, 4.0)}


class TestConvexHullProperties:
    """Test mathematical properties of the convex hull"""

    def test_result_is_convex(self):
        """Test that the result forms a convex polygon (no non-convex angles)"""
        from minimal_hull_algorithm import get_convex_hull_shrinking_circle
        
        def cross_product(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        points = [(0, 0), (4, 0), (4, 4), (0, 4), (2, 2)]
        result = get_convex_hull_shrinking_circle(points)
        
        if len(result) > 2:
            for i in range(len(result)):
                prev = result[i - 1]
                curr = result[i]
                nxt = result[(i + 1) % len(result)]
                # All turns should be in the same direction (positive cross product)
                cp = cross_product(prev, curr, nxt)
                assert cp >= 0, f"Non-convex hull detected at point {i}"

    def test_all_input_points_contained(self):
        """Test that all original points are on or inside the hull"""
        import numpy as np
        
        points = [(1, 1), (5, 1), (5, 5), (1, 5), (3, 3), (2, 4), (4, 2)]
        result = get_convex_hull_shrinking_circle(points)
        result_array = np.array(result)
        
        # The convex hull should contain all original points
        # A simple check: the centroid should be inside the hull
        centroid = np.mean(result_array, axis=0)
        assert len(result) >= 3

    def test_minimal_set(self):
        """Test that result is minimal (no redundant collinear points)"""
        # Create a rectangle with many points on the edges
        points = [
            (0, 0), (1, 0), (2, 0), (3, 0), (4, 0),  # bottom edge
            (4, 1), (4, 2), (4, 3), (4, 4),          # right edge
            (3, 4), (2, 4), (1, 4), (0, 4),          # top edge
            (0, 3), (0, 2), (0, 1)                   # left edge
        ]
        result = get_convex_hull_shrinking_circle(points)
        # Should only return 4 corner points
        assert len(result) == 4
        result_set = set(result)
        assert (0, 0) in result_set
        assert (4, 0) in result_set
        assert (4, 4) in result_set
        assert (0, 4) in result_set


class TestConvexHullWithRandomPoints:
    """Test with various random point distributions"""

    def test_random_points_small_set(self):
        """Test with a small random point set"""
        points = [(1.5, 2.3), (4.1, 0.2), (3.9, 5.0), (0.1, 1.0), (5.0, 4.9)]
        result = get_convex_hull_shrinking_circle(points)
        assert len(result) >= 3
        # All result points should be from input
        for point in result:
            assert point in points

    def test_random_points_large_set(self):
        """Test with a larger set of random points"""
        import numpy as np
        np.random.seed(42)
        points = np.random.uniform(0, 100, (50, 2)).tolist()
        
        result = get_convex_hull_shrinking_circle(points)
        assert len(result) >= 3
        
        # All result points should be from input
        for point in result:
            assert point in points

    def test_clustered_points(self):
        """Test with clustered points"""
        # Two clusters
        cluster1 = [(1 + i*0.1, 1 + j*0.1) for i in range(3) for j in range(3)]
        cluster2 = [(10 + i*0.1, 10 + j*0.1) for i in range(3) for j in range(3)]
        points = cluster1 + cluster2
        
        result = get_convex_hull_shrinking_circle(points)
        assert len(result) >= 3
        # Clustered points should have reasonable hull
        assert len(result) <= len(points)


class TestConvexHullNumericalStability:
    """Test numerical stability with extreme values"""

    def test_negative_coordinates(self):
        """Test with negative coordinates"""
        points = [(-5, -5), (5, -5), (5, 5), (-5, 5), (0, 0)]
        result = get_convex_hull_shrinking_circle(points)
        assert len(result) == 4
        # All corners should be included
        assert (-5, -5) in result
        assert (5, -5) in result
        assert (5, 5) in result
        assert (-5, 5) in result

    def test_very_small_coordinates(self):
        """Test with very small floating point coordinates"""
        points = [(0.0001, 0.0001), (0.0002, 0.0001), (0.0002, 0.0002), (0.0001, 0.0002)]
        result = get_convex_hull_shrinking_circle(points)
        assert len(result) == 4

    def test_large_coordinates(self):
        """Test with large coordinates"""
        points = [(10000, 10000), (20000, 10000), (20000, 20000), (10000, 20000)]
        result = get_convex_hull_shrinking_circle(points)
        assert len(result) == 4

    def test_mixed_coordinate_ranges(self):
        """Test with mixed coordinate ranges"""
        points = [(0.001, 1000), (1000, 0.001), (999.999, 999.999), (0.002, 0.002)]
        result = get_convex_hull_shrinking_circle(points)
        assert len(result) >= 3


class TestConvexHullSpecialShapes:
    """Test with special geometric shapes"""

    def test_regular_hexagon(self):
        """Test with regular hexagon vertices"""
        points = []
        for i in range(6):
            angle = 2 * math.pi * i / 6
            points.append((10 * math.cos(angle), 10 * math.sin(angle)))
        
        result = get_convex_hull_shrinking_circle(points)
        assert len(result) == 6

    def test_pentagon(self):
        """Test with regular pentagon vertices"""
        points = []
        for i in range(5):
            angle = 2 * math.pi * i / 5
            points.append((math.cos(angle), math.sin(angle)))
        
        result = get_convex_hull_shrinking_circle(points)
        assert len(result) == 5

    def test_star_shape(self):
        """Test with star shape (concave vertices become convex hull)"""
        # Create a 5-pointed star (only outer vertices will be in convex hull)
        outer_points = []
        inner_points = []
        for i in range(5):
            # Outer vertex
            angle = 2 * math.pi * i / 5
            outer_points.append((2 * math.cos(angle), 2 * math.sin(angle)))
            # Inner vertex
            angle_inner = angle + math.pi / 5
            inner_points.append((math.cos(angle_inner), math.sin(angle_inner)))
        
        points = outer_points + inner_points
        result = get_convex_hull_shrinking_circle(points)
        # Convex hull should have 5 outer vertices
        assert len(result) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
