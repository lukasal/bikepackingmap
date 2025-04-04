import pandas as pd
import pickle
import os
from functools import wraps
from datetime import datetime
from app.activity_manager.postprocess_activities import postprocess
from app.redis_client import redis_client
from app.map.MapSettings import MapSettings
from app.models.activity_model import Activity
from typing import List

# Define the decorator without an outer function
def store_in_redis(method):

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        # Set TTL from environment variable or default to 1800 seconds (30 minutes)
        ttl_seconds = int(os.getenv("SESSION_EXP_TIME", 1800))  # Move here for dynamic value
        # Execute the original method
        result = method(self, *args, **kwargs)
        
        # Serialize the instance and store it in Redis with TTL
        serialized_instance = pickle.dumps(self)
        redis_client.setex(f"session:{self.session_id}", ttl_seconds, serialized_instance)
        
        return result

    return wrapper

class ActivityManager:
    @store_in_redis
    def __init__(self, session_id):
        """
        Initialize the ActivityManager with a user-specific ID.
        Each user gets their own DataFrame to manage activities.
        """
        self.session_id = session_id  # User-specific session ID
        self.activities = []
        self.map_settings = None
        self.map_ids = None

        self.last_activity = datetime.utcnow()

    # Class method to load an instance from Redis
    @classmethod
    def load_from_redis(cls, session_id):
        # Attempt to get serialized data from Redis
        serialized_activity = redis_client.get(f"session:{session_id}")

        # If no data is found, return None
        if serialized_activity is None:
            return None

        # Deserialize the data into a UserActivity instance
        user_activity = pickle.loads(serialized_activity)
        return user_activity
        # Class method to load an instance from Redis

    @store_in_redis    
    def set_last_activity(self):
        self.last_activity = datetime.utcnow()

    @store_in_redis         
    def add_activities(self, activities: List[Activity]):
        """
        Add activities to the user's DataFrame.
        :param activities: List of activities 
        """
        self.activities += activities

    @store_in_redis
    def set_map_ids(self, map_ids):
        self.map_ids = map_ids

    def get_activities_df(self, ids=None):
        """
        Return the DataFrame of all activities for this user.
        """
        if self.activities:
            df = pd.DataFrame([activity.model_dump() for activity in self.activities])
            if ids:
                if not isinstance(ids, list):
                    ids = [ids]
                df = df.set_index("id").loc[ids].reset_index()
        else:
            # Create an empty DataFrame with columns from the Activity model
            df = pd.DataFrame(columns=Activity.get_field_names())

        return df

    
    def get_map_settings(self):
        """
        Return the map settings for this user.
        """
        if self.map_settings is None:
            self.init_map_settings()
        return self.map_settings

    @store_in_redis
    def init_map_settings(self):
        """
        Initialize the map settings for this user.
        """
        self.map_settings = MapSettings(
            self.get_activities_df(self.map_ids), "config/interactive_settings.yml"
        )
    @store_in_redis
    def delete_all_activities(self):
        """
        Delete all activities for this user.
        """
        self.activities = []

    @store_in_redis
    def save(self):
        """
        store current class in redis
        """
        pass

    def send_to_frontend(self):
        """
        Return the activities DataFrame displayed at the frontend.
        """
        # Prepare data to send to the frontend
        data_to_send = self.get_activities_df()[["start_date", "name", "id", "type"]]
        data_to_send["start_date"] = data_to_send["start_date"].apply(
            lambda x: (x.strftime("%Y-%m-%d %H:%M:%S") if x is not None else "")
        )
        return data_to_send.to_dict(
            orient="records"
        )

    @store_in_redis
    def postprocess(self, id_list):
        """
        Postprocess the activities after selection.
        For example: add elevation data, calculate distances, etc.
        """
        # Update activities based on IDs
        for i, activity in enumerate(self.activities):
            if activity.id in id_list:
                self.activities[i] = postprocess(activity)

    def reorder_activities(self, id_list):
        """
        Reorder the activities based on the provided ID list.
        """
        # Extract IDs from activities
        activity_ids = [activity.id for activity in self.activities]

        # Check if id_list and activity_ids contain the same IDs
        if set(id_list) != set(activity_ids):
            raise ValueError(
                "The provided ID list does not match the IDs in the activities."
            )

        self.activities = [
            activity for id in id_list for activity in self.activities if activity.id == id
        ]
