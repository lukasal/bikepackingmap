import pandas as pd
import numpy as np
import haversine as hs
import gpxpy
from app.elevation_profile import create_binary_elevation_profile
from app.gpx.process_points import process_points

def process_gpx_data(file_storage):

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

    try:
        gpx = gpxpy.parse(file_storage.stream, version="1.0")
    except Exception as e:
        print(f"Error parsing GPX file: {e}")
        return None
    data = []

    if gpx.tracks:
        print("Using tracks")
        for track in gpx.tracks:
            for segment in track.segments:
                data += process_points(segment.points, segment.get_speed)
    elif gpx.routes:
        print("Using routes")
        for route in gpx.routes:
            data += process_points(route.points)
    else:
        print("No tracks or routes found")
        return None

    # if (
    #     hasattr(gpx, "metadata")
    #     and gpx.metadata
    #     and hasattr(gpx.metadata, "time")
    #     and gpx.metadata.time
    # ):
    #     start_time = gpx.metadata.time
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

    # fill the final df
    df["map.polyline"] = [list(zip(gpx_df["Latitude"], gpx_df["Longitude"]))]
    df["start_latlng"] = df["map.polyline"].apply(lambda x: list(x[0]))
    df["end_latlng"] = df["map.polyline"].apply(lambda x: list(x[-1]))
    df["map.distance"] = [list(gpx_df["Distance"].fillna(0).cumsum())]
    metadata["distance"] = df["map.distance"][0][-1]

    df["name"] = file_storage.filename.split("/")[-1].split(".")[0]
    df["type"] = "GPX"
    # time
    try:
        df["start_date"] = gpx_df["Time"].iloc[0]
        df["end_date"] = gpx_df["Time"].iloc[-1]
        df["date"] = gpx_df["Time"].iloc[0].date()
        metadata["elapsed_time"] = (
            gpx_df["Time"].iloc[-1] - gpx_df["Time"].iloc[0]
        ).total_seconds()
    except:
        df["start_date"] = [None]
        df["end_date"] = [None]
        df["date"] = [None]
        metadata["elapsed_time"] = None

    # start/end location
    df["start_location"] = ""
    df["end_location"] = ""

    # elevation
    df["map.elevation"] = [list(gpx_df["Elevation"])]
    if any(element is not None for element in gpx_df["Elevation"]):
        diffs = gpx_df["Elevation"].diff().fillna(0)
        diffs = diffs.apply(lambda x: x if x > 0.2 else 0)
        metadata["total_elevation_gain"] = diffs.sum()

    if all(element is not None for element in gpx_df["Elevation"]):
        try:
            metadata["elevation_profile"] = create_binary_elevation_profile(
                pd.DataFrame(
                    {
                        "map.elevation": df["map.elevation"][0],
                        "map.distance": df["map.distance"][0],
                    }
                ),
                top_highlight=True,
            )

        except:
            metadata["elevation_profile"] = ""

    df["metadata"] = [metadata]

    return df
