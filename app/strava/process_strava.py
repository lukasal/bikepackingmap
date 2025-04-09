import polyline
import pandas as pd
from tqdm import tqdm
import requests
import re
from flask import session
from app.map.elevation_profile import create_binary_elevation_profile
import matplotlib.pyplot as plt
import base64
import os
from datetime import timedelta
from app.models.activity_model import Activity
from typing import List


def decode_polyline(x):
    try:
        return polyline.decode(x)
    except Exception:
        return None

information_columns = [
    "distance",
    "moving_time",
    "elapsed_time",
    "total_elevation_gain",
    "achievement_count",
    "kudos_count",
    "comment_count",
    "max_speed",
    "elev_high",
    "elev_low",
    "pr_count",
    "total_photo_count",
    "average_cadence",
    "average_temp",
    "average_watts",
    "weighted_average_watts",
    "max_watts",
    "average_heartrate",
    "max_heartrate",
    "average_speed",
    "max_speed",
    "elevation_profile",
]


def combine_columns(row, columns):
    return {col: row[col] for col in columns if col in row}


def process_strava(activities: pd.DataFrame) -> List[Activity]:
    """
    Preprocess the activities data from Strava API.

    Args:
        activities (pd.DataFrame): DataFrame containing activities data.

    Returns:
        pd.DataFrame: Preprocessed activities data.
    """
    # drop activitites without a gps track
    activities = activities.dropna(
        subset=["map.summary_polyline", "start_date_local", "elapsed_time"],
    )
    activities = activities[activities["map.summary_polyline"] != ""]
    # create warning when activities are dropped

    # add decoded summary polylines
    if activities.empty:
        return []

    activities["map_polyline"] = activities["map.summary_polyline"].apply(decode_polyline)
    activities["start_latlng"] = activities["map_polyline"].apply(lambda x: list(x[0]))
    activities["end_latlng"] = activities["map_polyline"].apply(lambda x: list(x[-1]))

    activities["start_location"] = [
        (re.findall(r"\: (.+) -", s) + [""])[0] for s in activities["name"]
    ]
    activities["end_location"] = [
        (re.findall(r"\- (.+)$", s) + [""])[0] for s in activities["name"]
    ]
    # convert data types
    # activities.loc[:, 'start_date'] = pd.to_datetime(activities['start_date']).dt.date
    activities["date"] = pd.to_datetime(activities["start_date_local"]).dt.date
    activities["start_date"] = pd.to_datetime(
        activities["start_date_local"]
    ).dt.tz_localize(None)
    activities["end_date"] = activities["start_date"] + pd.to_timedelta(
        activities["elapsed_time"], unit="s"
    )
    # convert values
    activities.loc[:, "distance"] /= 1000  # convert from m to km
    activities.loc[:, "average_speed"] *= 3.6  # convert from m/s to km/h
    activities.loc[:, "max_speed"] *= 3.6  # convert from m/s to km/h

    activities["metadata"] = activities.apply(
        lambda row: combine_columns(row, information_columns), axis=1
    )
    activities["id"] = activities["id"].astype(str)
    activities["source"] = "strava"
    activities["ready"] = False

    activities = activities.sort_values(by="start_date").reset_index(drop=True)

    validated_activities = Activity.convert_df(activities)

    return validated_activities
