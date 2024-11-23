import pandas as pd
import pickle
import os
from functools import wraps
from datetime import datetime
from app.preprocess import preprocess
from app.redis_client import redis_client
from app.map_activities2 import map_activities


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
        self.raw = pd.DataFrame(columns=['name', 'start_date'])  # Data for each user
        self.selected_df = pd.DataFrame()  # Selected activities for further processing
        self.preprocessed = pd.DataFrame()
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
    def add_activities(self, activities):
        """
        Add activities to the user's DataFrame.
        :param activities: List of activities as dictionaries or DataFrame
        """
        self.raw = activities

    def get_activities(self):
        """
        Return the DataFrame of all activities for this user.
        """
        return self.raw

    @store_in_redis 
    def select_activities(self, selection_criteria):
        """
        Select activities based on some criteria (e.g., activity names or start_date).
        :param selection_criteria: Criteria for selecting activities (e.g., list of indices, a filter function, etc.)
        """
        # Assuming selection_criteria is a list of indices for simplicity
        self.selected_df = self.raw.loc[self.raw['id'].isin(selection_criteria)]

    @store_in_redis 
    def preprocess_selected(self):
        """
        Preprocess the selected activities for the user.
        For example: clean data, add extra columns, or calculate new features.
        """
        if not self.selected_df.empty:
            # Example: Add a new column 'processed' to mark activities as preprocessed
            self.preprocessed  = preprocess(self.selected_df)
            self.map_activities = map_activities(self.preprocessed)

    @store_in_redis
    def save(self):
        """
        store current class in redis
        """
        pass

    def get_selected_activities(self):
        """
        Return the DataFrame of selected activities for this user.
        """
        return self.selected_df
