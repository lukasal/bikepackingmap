import numpy as np
import haversine as hs
from dateutil import parser
import datetime
import pandas as pd

def process_points(points, get_speed_func=None):
    data = []
    processed_points = []

    for point_idx, point in enumerate(points):
        point_data = [point.longitude, point.latitude]

        # Include elevation if present
        point_data.append(getattr(point, "elevation", None))

        # Include time if present
        point_data.append(getattr(point, "time", None))

        if point_idx == 0:
            distance = np.nan
        else:
            distance = hs.haversine(
                point1=processed_points[point_idx - 1],
                point2=(point.latitude, point.longitude),
                unit=hs.Unit.KILOMETERS,
            )

        speed = get_speed_func(point_idx) if get_speed_func else None

        point_data.extend([speed, distance])
        processed_points.append((point.latitude, point.longitude))
        data.append(point_data)

    return data
