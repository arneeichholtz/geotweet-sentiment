import gzip
import json
import pandas as pd
import os

class TweetFile:
    """
    TweetFile class to store information for each file containing tweets
    Params
        path_to_data: the path to the tweet data file
        is_geo: bool to set the type of tweet (True is geo-tagged, False is regular) - default False
        locs_only: bool to set whether we only want to store the tweets with non-empty user location
                   this is to save memory because we only consider the tweets where we can infer the location - default True
    """

    def __init__(self, path_to_data, is_geo=False, locs_only=True):
        self.path = path_to_data
        self.lines = self.extract_lines()
        self.len_lines = len(self.lines)

        # Regular tweets
        if not is_geo:
            self.tweets = self.extract_tweets()

            # Override tweets and only store the tweets with non-empty user-profile location
            if locs_only:
                self.len_all_tweets = len(self.tweets) # len_all_tweets refers to all tweets, not just with location
                self.tweets = self.extract_location()

        # Geo-tagged tweets
        else:
            self.tweets = self.extract_geo_tweets()

        self.len_tweets = len(self.tweets)
        self.date_name = self.extract_date_name()

    def extract_lines(self):
        """
        Method to open the .txt.gzip file. 
        Returns
            Lines: a txt file object
        """
        with gzip.open(self.path, "r") as f:
            lines = f.readlines()
        print("Lines in original file: ", len(lines))
        return lines

    def extract_tweets(self):
        """
        Extract the tweets from the data file, storing tweet ID, user ID and location entry (not storing any geo-tag information)
        Returns
            df: DataFrame with tweets
        """
        tweets = []
        for line in self.lines:
            try:
                dict_line = json.loads(line)
                tweet_id = dict_line['id']
                user_id = dict_line['user']['id']
                location = dict_line['user']['location']

                tweet = {"tweet_id": tweet_id, "user_id": user_id, "location": location}
                tweets.append(tweet)
            except:
                continue
        print("Tweets: ", len(tweets))
        df = pd.DataFrame(tweets)
        return df

    def extract_geo_tweets(self):
        """
        Extract geo-tagged tweets from the data file, storing tweet ID, user ID, full name of the tagged location, country of the geo-tag, and geo-tag type
        Returns
            df: DataFrame with geo-tagged tweets
        """
        geo_tweets = []
        for line in self.lines:
            try:
                dict_line = json.loads(line)
                tweet_id = dict_line['id']
                user_id = dict_line['user']['id']

                place_obj = dict_line['place']
                full_name = place_obj['full_name']
                country = place_obj['country']
                type = place_obj['place_type']

                tweet = {"tweet_id": tweet_id, "user_id": user_id, "full_name": full_name, "country": country,
                         "type": type}
                geo_tweets.append(tweet)
            except:
                continue
        print("Geo-tagged tweets: ", len(geo_tweets))
        df = pd.DataFrame(geo_tweets)
        return df

    def extract_date_name(self):
        """
        Get date-name of a file, like 2021-01-01_00_00_01
        """
        base_name = os.path.basename(self.path)
        end_ind = base_name.index(".")
        return base_name[:end_ind]

    def extract_location(self):
        """
        Extract the tweets that have non-empty user-profile location
        Returns
            tweets_loc: tweets DataFrame with non-empty location
        """
        copy_df = self.tweets
        df = copy_df.replace(to_replace="", value=pd.NaT) # Replace empty string values with pd.NaT, those are picked up by dropna()
        tweets_loc = df.dropna(subset=['location'])
        return tweets_loc

    def extract_location_and_descrip(self):
        """
        (NOT USED)
        Extract tweets that have non-empty user-profile location and tweets that have only user-profile description
        Returns
            df_loc: dataframe with tweets that have a non-empty location entry
            df_descrip: dataframe with tweets that have only description entry
        """
        copy_df = self.tweets
        df = copy_df.replace(to_replace="", value=pd.NaT) # Replace empty string values with pd.NaT, those are picked up by dropna()
        df_loc = df.dropna(subset=['location']) # All tweets that have at least location
        df_descrip = df[df.description.notnull() & df.location.isnull()] # All tweets that have only description
        return df_loc, df_descrip

    """
    Get methods for the different attributes
    """
    def get_len_all_tweets(self):
        return self.len_all_tweets

    def get_lines(self):
        return self.lines

    def get_len_tweets(self):
        return self.len_tweets

    def get_tweets(self):
        return self.tweets

    def get_date_name(self):
        return self.date_name
