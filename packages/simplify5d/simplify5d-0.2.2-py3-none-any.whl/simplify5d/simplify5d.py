import numpy as np

class Simplify5d:

    def get_sq_dist_2d(p1, p2):
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return dx * dx + dy * dy

    def get_sq_dist_3d(p1, p2):
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        dz = p1[2] - p2[2]
        return dx * dx + dy * dy + dz * dz

    def get_sq_seg_dist_2d(p, p1, p2):
        x, y = p1
        dx = p2[0] - x
        dy = p2[1] - y

        if dx != 0 or dy != 0:
            t = ((p[0] - x) * dx + (p[1] - y) * dy) / (dx * dx + dy * dy)
            if t > 1:
                x = p2[0]
                y = p2[1]
            elif t > 0:
                x += dx * t
                y += dy * t

        dx = p[0] - x
        dy = p[1] - y

        return dx * dx + dy * dy

    def get_sq_seg_dist_3d(p, p1, p2):
        x, y, z = p1
        dx = p2[0] - x
        dy = p2[1] - y
        dz = p2[2] - z

        if dx != 0 or dy != 0 or dz != 0:
            t = ((p[0] - x) * dx + (p[1] - y) * dy + (p[2] - z) * dz) / (dx * dx + dy * dy + dz * dz)
            if t > 1:
                x = p2[0]
                y = p2[1]
                z = p2[2]
            elif t > 0:
                x += dx * t
                y += dy * t
                z += dz * t

        dx = p[0] - x
        dy = p[1] - y
        dz = p[2] - z

        return dx * dx + dy * dy + dz * dz

    @staticmethod
    def radial_dist_2d(points, sq_tolerance):
        prev_point = points[0]
        new_points = [prev_point]
        for point in points[1:]:
            if Simplify5d.get_sq_dist_2d(point, prev_point) > sq_tolerance:
                new_points.append(point)
                prev_point = point
        if not np.array_equal(prev_point, points[-1]):
            new_points.append(points[-1])
        return new_points

    @staticmethod
    def radial_dist_3d(points, sq_tolerance):
        prev_point = points[0]
        new_points = [prev_point]
        for point in points[1:]:
            if Simplify5d.get_sq_dist_3d(point, prev_point) > sq_tolerance:
                new_points.append(point)
                prev_point = point
        if not np.array_equal(prev_point, points[-1]):
            new_points.append(points[-1])
        return new_points

    def dp_step_2d(points, first, last, sq_tolerance, simplified):
        max_sq_dist = sq_tolerance
        index = None
        for i in range(first + 1, last):
            sq_dist = Simplify5d.get_sq_seg_dist_2d(points[i], points[first], points[last])
            if sq_dist > max_sq_dist:
                index = i
                max_sq_dist = sq_dist
        if index and max_sq_dist > sq_tolerance:
            if index - first > 1:
                Simplify5d.dp_step_2d(points, first, index, sq_tolerance, simplified)
            simplified.append(points[index])
            if last - index > 1:
                Simplify5d.dp_step_2d(points, index, last, sq_tolerance, simplified)

    def dp_step_3d(points, first, last, sq_tolerance, simplified):
        max_sq_dist = sq_tolerance
        index = None
        for i in range(first + 1, last):
            sq_dist = Simplify5d.get_sq_seg_dist_3d(points[i], points[first], points[last])
            if sq_dist > max_sq_dist:
                index = i
                max_sq_dist = sq_dist
        if index and max_sq_dist > sq_tolerance:
            if index - first > 1:
                Simplify5d.dp_step_3d(points, first, index, sq_tolerance, simplified)
            simplified.append(points[index])
            if last - index > 1:
                Simplify5d.dp_step_3d(points, index, last, sq_tolerance, simplified)

    @staticmethod
    def douglas_peucker_2d(points, sq_tolerance):
        last = len(points) - 1
        simplified = [points[0]]
        Simplify5d.dp_step_2d(points, 0, last, sq_tolerance, simplified)
        simplified.append(points[last])
        return simplified

    @staticmethod
    def douglas_peucker_3d(points, sq_tolerance):
        last = len(points) - 1
        simplified = [points[0]]
        Simplify5d.dp_step_3d(points, 0, last, sq_tolerance, simplified)
        simplified.append(points[last])
        return simplified

    @staticmethod
    def simplify(points, tolerance=1.0, highest_quality=False):
        points = np.asarray(points)
        
        if len(points) <= 2:
            return points
        
        is_2d = points.shape[1] == 2
        is_3d = points.shape[1] == 3
        
        if not (is_2d or is_3d):
            raise ValueError("Points must be 2D or 3D")
        
        sq_tolerance = tolerance * tolerance
        
        if not highest_quality:
            points = Simplify5d.radial_dist_2d(points, sq_tolerance) if is_2d else Simplify5d.radial_dist_3d(points, sq_tolerance)
        
        points = Simplify5d.douglas_peucker_2d(points, sq_tolerance) if is_2d else Simplify5d.douglas_peucker_3d(points, sq_tolerance)
        
        return points

    @staticmethod
    def deinterpolate(points, tolerance=1e-5):
        if len(points) < 2:
            return points
        
        print(f'Cleaning {len(points)} to ', end="")

        # Calculate vectors for each segment
        vectors = np.diff(points, axis=0)

        # Normalise vectors
        normVectors = np.array([npline.norm(v) for v in vectors])

        # Filter out points that create duplicate segments
        filtered_points = [points[0]]
        for i in range(1, len(points)):
            if i == 1 or np.linalg.norm(normVectors[i-1] - normVectors[i-2]) > tolerance:
                filtered_points.append(points[i])

        print(f'{len(filtered_points)} points')

        return np.array(filtered_points)

# Example usage:
if __name__ == "__main__":
        
    points_2d = np.array([[0, 0], [1, 1], [2, 2], [3, 3]])
    points_3d = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2], [3, 3, 3]])

    simplified_2d = Simplify5d.simplify(points_2d, tolerance=1.0, highest_quality=False)
    simplified_3d = Simplify5d.simplify(points_3d, tolerance=1.0, highest_quality=False)

    print("Simplified 2D points:", simplified_2d)
    print("Simplified 3D points:", simplified_3d)
    