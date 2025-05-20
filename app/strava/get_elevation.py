from flask import session
import requests


# define function to get elevation data
def get_elevation(id):
    base_url = "https://www.strava.com/api/v3/activities/" + str(id) + "/streams"
    access_token = session["access_token"]
    headers = {"Authorization": "Bearer " + access_token}

    payload = {"keys": "altitude", "key_by_type": True}
    r = requests.get(base_url, headers=headers, params=payload).json()

    return r["distance"]["data"], r["altitude"]["data"]
