import polyline
import pandas as pd
from tqdm import tqdm
import requests
import re
from flask import session
from ..elevation_profile import create_elevation_profile
import matplotlib.pyplot as plt
import base64
import os
from datetime import timedelta


# define function to get elevation data
def get_elevation(id):
    base_url = "https://www.strava.com/api/v3/activities/" + str(id) + "/streams"
    access_token = session["access_token"]
    headers = {"Authorization": "Bearer " + access_token}

    payload = {"keys": "altitude", "key_by_type": True}
    r = requests.get(base_url, headers=headers, params=payload).json()

    return r["distance"]["data"], r["altitude"]["data"]


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


def preprocess(activities):
    # drop activitites without a gps track
    activities = activities.dropna(
        subset=["map.summary_polyline", "start_date_local", "elapsed_time"],
    )
    activities = activities[activities["map.summary_polyline"] != ""]

    # add decoded summary polylines
    activities["map.polyline"] = activities["map.summary_polyline"].apply(
        polyline.decode
    )
    activities["start_latlng"] = activities["map.polyline"].apply(lambda x: list(x[0]))
    activities["end_latlng"] = activities["map.polyline"].apply(lambda x: list(x[-1]))
    # activities = activities[activities.name.str.contains("tappa") ]

    # get elevation data
    elevation_data = list()
    distance_data = list()
    elevation_profiles = list()
    for idx in tqdm(activities.index):
        activity = activities.loc[idx, :]
        # TODO catch if fails
        try:
            distance, elevation = get_elevation(activity.id)
            fig = create_elevation_profile(
                pd.DataFrame({"map.elevation": elevation, "map.distance": distance}),
                top_color=False,
            )
            png = "elevation_profile_.png"
            fig.savefig(png, dpi=75)
            plt.close()

            # read png file
            elevation_profile = base64.b64encode(open(png, "rb").read()).decode()
            # delete file
            os.remove(png)

        except:
            distance = []
            elevation = []
            elevation_profile = ""

        elevation_data.append(elevation)
        distance_data.append(distance)
        elevation_profiles.append(elevation_profile)

    # add elevation data to dataframe
    activities["map.elevation"] = elevation_data
    activities["map.distance"] = distance_data
    activities["elevation_profile"] = elevation_profiles

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

    # read POIs
    # poi = pd.read_excel("data/data_poi.xlsx")
    # poi['Datum'] = poi.Datum.dt.date
    # poi = poi.groupby(['Datum', 'type']).agg({'reference_dist':lambda x: list(x), 'reference_label':lambda x: list(x)})

    # #add POI information
    # activities = pd.merge(activities,poi, how='left', left_on = ['date', 'type'], right_on = ['Datum', 'type'], )

    # activities['reference_dist'] = activities['reference_dist'].apply(lambda d: d if isinstance(d, list) else [])
    # activities['reference_label'] = activities['reference_label'].apply(lambda d: d if isinstance(d, list) else [])

    # #detect rest days
    activities["restday_previous"] = [
        0 if date in set(pd.to_datetime(activities["date"])) else 1
        for date in pd.to_datetime(activities["date"]) - timedelta(days=1)
    ]
    activities["restday_after"] = [
        0 if date in set(pd.to_datetime(activities["date"])) else 1
        for date in pd.to_datetime(activities["date"]) + timedelta(days=1)
    ]

    # set index
    # activities.set_index('start_date_local', inplace=True)#
    # Apply the function to each row
    activities["metadata"] = activities.apply(
        lambda row: combine_columns(row, information_columns), axis=1
    )

    # Drop the original columns
    # columns_to_drop = [col for col in information_columns if col in activities.columns]
    # activities = activities.drop(columns=columns_to_drop)
    activities = activities.sort_values(by="start_date").reset_index(drop=True)
    activities = activities[
        [
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
    ]
    return activities
