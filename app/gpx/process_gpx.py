import pandas as pd
import numpy as np
import haversine as hs
import gpxpy
from app.map.elevation_profile import create_binary_elevation_profile
from app.gpx.process_points import process_points
from app.models.activity_model import Activity
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_gpx_data(file_storage: object) -> Activity:
    activity = {}
    metadata = {}
    data = []

    try:
        gpx = gpxpy.parse(file_storage.stream, version="1.0")
    except Exception as e:
        logger.error(f"Error parsing GPX file: {e}")
        return None

    if gpx.tracks:
        logger.info("Using tracks")
        for track in gpx.tracks:
            for segment in track.segments:
                data += process_points(segment.points, segment.get_speed)
    elif gpx.routes:
        logger.info("Using routes")
        for route in gpx.routes:
            data += process_points(route.points)
    else:
        logger.info("No tracks or routes found")
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

    # location data
    activity["map_polyline"] = list(zip(gpx_df["Latitude"], gpx_df["Longitude"]))
    activity["start_latlng"] = activity["map_polyline"][0]
    activity["end_latlng"] = activity["map_polyline"][-1]
    activity["map_distance"] = list(gpx_df["Distance"].fillna(0).cumsum())
    metadata["distance"] = activity["map_distance"][-1]

    activity["name"] = file_storage.filename.split("/")[-1].split(".")[0]
    activity["type"] = "GPX"

    # time
    activity["start_date"] = (
        gpx_df["Time"].iloc[0] if not gpx_df["Time"].empty else None
    )
    activity["end_date"] = gpx_df["Time"].iloc[-1] if not gpx_df["Time"].empty else None
    activity["date"] = gpx_df["Time"].iloc[0].date() if activity["end_date"] else None
    if not activity["start_date"] is None and not activity["end_date"] is None:
        metadata["elapsed_time"] = (
            activity["end_date"] - activity["start_date"]
        ).total_seconds()

    # start/end location
    # activity["start_location"] = ""
    # activity["end_location"] = ""

    # elevation if available
    if any(element is not None for element in gpx_df["Elevation"]):
        activity["map_elevation"] = list(gpx_df["Elevation"])
        diffs = gpx_df["Elevation"].diff().fillna(0)
        diffs = diffs.apply(lambda x: x if x > 0.2 else 0)
        metadata["total_elevation_gain"] = diffs.sum()

    activity["metadata"] = metadata
    activity["source"] = "GPX"
    activity["type"] = "GPX"
    activity["ready"] = False

    activity = Activity(**activity)
    return activity
