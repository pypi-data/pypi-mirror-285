from typing import Tuple, List
from rpas_utils_lib import KML
import math

def euclidean_distance(m: Tuple[int, int], n: Tuple[int, int]):
        x = (m[0] - n[0]) ** 2
        y = (m[1] - n[1]) ** 2
        d = math.sqrt(x + y)
        return d

def measure_error(projected_points: List[KML], detection_points: List[Tuple[int, int]]):
        distances = []
        for p, d in zip(projected_points, detection_points):
            if p is None or d is None:
                continue
            distance = euclidean_distance(p.pixel_location, d)
            distances.append(distance)
        return sum(distances) / len(distances)

