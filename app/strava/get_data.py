import requests

import pandas as pd

# define function to get your strava data
def get_data(access_token, start_date, end_date, per_page=200, page=1):

    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": "Bearer " + access_token}
    params = {
        "before": end_date,
        "after": start_date,
        "per_page": per_page,
        "page": page,
    }

    data = requests.get(activities_url, headers=headers, params=params).json()
    data = pd.json_normalize(data)
    return data
