import polyline
import pandas as pd
from tqdm import  tqdm 
import requests
import re
from flask import session
from .elevation_profile import create_elevation_profile
import matplotlib.pyplot as plt
import base64
import os

# define function to get elevation data using the open-elevation API
def get_elevation(id):
    base_url = 'https://www.strava.com/api/v3/activities/'+ str(id) + '/streams'
    access_token = session["access_token"]    
    headers = {'Authorization': 'Bearer ' + access_token}

    payload = {
           'keys': 'altitude', 
           'key_by_type': True
           }
    r = requests.get(base_url,     
                 headers=headers, 
                 params=payload).json()
    
    return r['distance']['data'],r['altitude']['data']

def preprocess(activities):
    # add decoded summary polylines
    activities['map.polyline'] = activities['map.summary_polyline'].apply(polyline.decode)

    # activities = activities[activities.name.str.contains("tappa") ]

    # get elevation data
    elevation_data = list()
    distance_data = list()
    elevation_profiles = list()
    for idx in tqdm(activities.index):
        activity = activities.loc[idx, :]
        # TODO catch if fails
        distance, elevation = get_elevation(activity.id)
        elevation_data.append(elevation)
        distance_data.append(distance)
        fig = create_elevation_profile(
            {"map.elevation": elevation, "map.distance": distance}
        )
        png = "elevation_profile_.png"
        fig.savefig(png, dpi=75)
        plt.close()

        # read png file
        elevation_profile = base64.b64encode(open(png, "rb").read()).decode()
        elevation_profiles.append(elevation_profile)
        # delete file
        os.remove(png)
    # add elevation data to dataframe
    activities['map.elevation'] = elevation_data
    activities['map.distance'] = distance_data
    activities["elevation_profile"] = elevation_profiles

    activities['start_location'] =  [(re.findall(r'\: (.+) -', s)+[''])[0] for s in activities['name']]
    activities['end_location'] = [(re.findall(r'\- (.+)$', s)+[''])[0] for s in activities['name']]

    # convert data types
    # activities.loc[:, 'start_date'] = pd.to_datetime(activities['start_date']).dt.date
    activities.loc[:, 'date'] = pd.to_datetime(activities['start_date_local']).dt.date
    activities.loc[:, 'start_date_local'] = pd.to_datetime(activities['start_date_local']).dt.tz_localize(None)
    # convert values
    activities.loc[:, 'distance'] /= 1000 # convert from m to km
    activities.loc[:, 'average_speed'] *= 3.6 # convert from m/s to km/h
    activities.loc[:, 'max_speed'] *= 3.6 # convert from m/s to km/h

    # drop columns
    activities.drop(
        [
            'map.summary_polyline', 
            'resource_state',
            'external_id', 
            'upload_id', 
            'location_city', 
            'location_state', 
            'start_date',
            'has_kudoed', 
            'athlete.resource_state', 
            'utc_offset', 
            'map.resource_state', 
            'athlete.id', 
            'visibility', 
            'heartrate_opt_out', 
            'upload_id_str', 
            'from_accepted_tag', 
            'map.id', 
            'manual', 
            'private', 
            'flagged', 
        ], 
        axis=1, 
        inplace=True
    )

    # read POIs
    # poi = pd.read_excel("data/data_poi.xlsx")
    # poi['Datum'] = poi.Datum.dt.date
    # poi = poi.groupby(['Datum', 'type']).agg({'reference_dist':lambda x: list(x), 'reference_label':lambda x: list(x)})

    # #add POI information
    # activities = pd.merge(activities,poi, how='left', left_on = ['date', 'type'], right_on = ['Datum', 'type'], )

    # activities['reference_dist'] = activities['reference_dist'].apply(lambda d: d if isinstance(d, list) else [])
    # activities['reference_label'] = activities['reference_label'].apply(lambda d: d if isinstance(d, list) else [])

    # #detect rest days
    # activities['restday_previous'] = [0 if date  in set(pd.to_datetime(activities['date'])) else 1 for date in pd.to_datetime(activities['date'])- timedelta(days=1)]
    # activities['restday_after'] = [0 if date  in set(pd.to_datetime(activities['date'])) else 1 for date in pd.to_datetime(activities['date'])+ timedelta(days=1)]

    # set index
    activities.set_index('start_date_local', inplace=True)#

    return activities
