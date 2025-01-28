import pandas as pd
import numpy as np
import haversine as hs
import gpxpy


def process_gpx_data(file_path):

    gpx = gpxpy.parse(open(file_path), version="1.0")
    points = []
    data = []

    # Extract start time
    start_time = None
    # if (
    #     hasattr(gpx, "metadata")
    #     and gpx.metadata
    #     and hasattr(gpx.metadata, "time")
    #     and gpx.metadata.time
    # ):
    #     start_time = gpx.metadata.time

    for track in gpx.tracks:
        for segment in track.segments:
            for point_idx, point in enumerate(segment.points):
                point_data = [point.longitude, point.latitude]

                # Include elevation if present
                if hasattr(point, "elevation") and point.elevation is not None:
                    point_data.append(point.elevation)
                else:
                    point_data.append(None)

                # Include time if present
                if hasattr(point, "time") and point.time is not None:
                    point_data.append(point.time)
                else:
                    point_data.append(None)

                if point_idx == 0:
                    distance = np.nan
                else:
                    distance = hs.haversine(
                        point1=(points[point_idx - 1][1], points[point_idx - 1][0]),
                        point2=(point.latitude, point.longitude),
                        unit=hs.Unit.METERS,
                    )

                point_data.extend(
                    [
                        segment.get_speed(point_idx),
                        distance,
                    ]
                )
                points.append((point.latitude, point.longitude))
                data.append(point_data)

    columns = [
        "Longitude",
        "Latitude",
        "Elevation",
        "Time",
        "Speed",
        "Distance",
    ]

    # Create DataFrame
    gpx_df = pd.DataFrame(data, columns=columns)

    # Additional DataFrame creation and metadata handling
    df = pd.DataFrame(
        columns=[
            "name",
            "id",
            "start_date",
            "end_date",
            "date",
            "type",
            "map.polyline",
            "start_latlng",
            "end_latlng",
            "map.elevation",
            "map.distance",
            "start_location",
            "end_location",
            "metadata",
        ]
    )
    metadata = {}

    df["map.polyline"] = [list(zip(gpx_df["Latitude"], gpx_df["Longitude"]))]
    df["start_latlng"] = df["map.polyline"].apply(lambda x: list(x[0]))
    df["end_latlng"] = df["map.polyline"].apply(lambda x: list(x[-1]))
    df["map.distance"] = [list(gpx_df["Distance"].fillna(0).cumsum())]
    metadata["distance"] = df["map.distance"].apply(lambda x: x[-1])

    df["name"] = file_path.split("/")[-1].split(".")[0]
    df["type"] = "GPX"
    # time
    df["start_date"] = gpx_df["Time"].iloc[0]
    df["end_date"] = gpx_df["Time"].iloc[-1]
    df["date"] = gpx_df["Time"].iloc[0].date()
    metadata["elapsed_time"] = (
        gpx_df["Time"].iloc[-1] - gpx_df["Time"].iloc[0]
    ).total_seconds()

    # elevation
    df["map.elevation"] = [list(gpx_df["Elevation"])]
    diffs = gpx_df["Elevation"].diff().fillna(0)
    diffs = diffs.apply(lambda x: x if x > 0.2 else 0)
    metadata["total_elevation_gain"] = diffs.sum()

    # start/end location
    df["start_location"] = ""
    df["end_location"] = ""

    df["metadata"] = [metadata]

    return df
