import pandas as pd
from datetime import datetime
from app.preprocess import preprocess


class ActivityManager:
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
        
    def set_last_activity(self):
        self.last_activity = datetime.utcnow()
        
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

    def select_activities(self, selection_criteria):
        """
        Select activities based on some criteria (e.g., activity names or start_date).
        :param selection_criteria: Criteria for selecting activities (e.g., list of indices, a filter function, etc.)
        """
        # Assuming selection_criteria is a list of indices for simplicity
        self.selected_df = self.raw.loc[selection_criteria]

    def preprocess_selected(self):
        """
        Preprocess the selected activities for the user.
        For example: clean data, add extra columns, or calculate new features.
        """
        if not self.selected_df.empty:
            # Example: Add a new column 'processed' to mark activities as preprocessed
            self.preprocessed  = preprocess(self.selected_df)


    def get_selected_activities(self):
        """
        Return the DataFrame of selected activities for this user.
        """
        return self.selected_df