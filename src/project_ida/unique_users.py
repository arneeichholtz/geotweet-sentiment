import pandas as pd

class UniqueUsers:
    """
    UniqueUsers class to store and update the unique users over many tweet files
    """

    def __init__(self):
        # Initialize the Unique Users object with an empty dataframe
        self.users = pd.DataFrame({"user_id": [], "location": []}, dtype=int)

    def update_users(self, df):
        """
        Update unique users with pandas functions
        """
        new_df = pd.concat([self.users, df])
        self.users = new_df.drop_duplicates(subset=["user_id"]).reset_index(drop=True)
        print(f"Users updated. Unique users: {len(self.users)}")

    def get_users(self):
        return self.users


