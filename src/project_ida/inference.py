import re
import pandas as pd
from tqdm import tqdm

class Inference:
    """
    Inference class to save the location names (states, cities) to look for and their regular expressions (regex)
    Params
        path_to_names: path to excel file containing location names and the corresponding regex
    """
    
    def __init__(self, path_to_names):
        self.names = pd.read_excel(path_to_names)
        self.regex = [re.compile(entry) for entry in self.names['regex']]

    def inference_loc(self, df):
        """
        Geo inference based on the user-profile location
        Params
            df: Dataframe with user ID's and user-profile location
        Returns
            result: result DataFrame with user ID's, profile location and inferred location
        """
        matches = self.find_location(df)
        return matches

    def inference_descrip(self, df):
        """
        (NOT USED NOR IMPLEMENTED)
        Geo inference based on user-profile description
        """
        pass

    def find_location(self, df):
        """
        Find match(es) between user-profile 'location' and excel file of location names.
        Params
            df: DataFrame with user ID's and user-profile location
        Returns
            df_out: DataFrame with user ID, profile location and inferred location
        """
        print("Finding location matches")
        locations = list(df['location']) # The user-profile locations
        outlist = locations.copy()

        for loc_ind, loc in tqdm(enumerate(locations), total=len(locations)):
            results = []

            for regex_ind, regex in enumerate(self.regex):
                if regex.search(loc):
                    results.append(self.names.loc[regex_ind, "Name"])
                    # If a match is found, we can stop searching
                    break

            user_id = df.iloc[loc_ind]["user_id"]
            line = {"user_id": user_id, "location": loc, "inferred loc": results}
            outlist[loc_ind] = line

        df_out = pd.DataFrame(outlist)
        return df_out

    def find_location_row(self, row, not_found="not_found"):
        """
        Find match(es) for a single row (ie, tweet)
        """
        location = row["location"]
        results = []

        for regex_ind, regex in enumerate(self.regex):
            if regex.search(location):
                results.append(self.names.loc[regex_ind, "Name"])
                # If a match is found, stop searching
                break

        if len(results) == 0:
            results = not_found
        line = {"user_id": row["user_id"], "location": location, "inferred loc": results}
        return line

