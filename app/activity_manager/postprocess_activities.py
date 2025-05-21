from app.models.activity_model import Activity
from app.strava.get_elevation import get_elevation
from app.map.elevation_profile import create_binary_elevation_profile


def postprocess(activity: Activity) -> Activity:
    if activity.source == "strava":
        # get elevation data from strava API
        try:
            activity.map_distance, activity.map_elevation = get_elevation(activity.id)
            if activity.map_distance is not None:
                activity.map_distance = [
                    point / 1000 for point in activity.map_distance
                ]  # convert from m to km

        except Exception:
            pass

    if activity.map_distance and activity.map_elevation:
        activity.metadata["elevation_profile"] = create_binary_elevation_profile(
            activity.map_distance, activity.map_elevation, top_highlight=True
        )

    activity.ready = True

    # read POIs
    # poi = pd.read_excel("data/data_poi.xlsx")
    # poi['Datum'] = poi.Datum.dt.date
    # poi = poi.groupby(['Datum', 'type']).agg({'reference_dist':lambda x: list(x), 'reference_label':lambda x: list(x)})

    # #add POI information
    # activities = pd.merge(activities,poi, how='left', left_on = ['date', 'type'], right_on = ['Datum', 'type'], )

    # activities['reference_dist'] = activities['reference_dist'].apply(lambda d: d if isinstance(d, list) else [])
    # activities['reference_label'] = activities['reference_label'].apply(lambda d: d if isinstance(d, list) else [])

    # #detect rest days
    # activities.metadata["restday_previous"] = [
    #     0 if date in set(pd.to_datetime(activities["date"])) else 1
    #     for date in pd.to_datetime(activities["date"]) - timedelta(days=1)
    # ]
    # activities["restday_after"] = [
    #     0 if date in set(pd.to_datetime(activities["date"])) else 1
    #     for date in pd.to_datetime(activities["date"]) + timedelta(days=1)
    # ]

    return activity
