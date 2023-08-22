# Example params:
# --data_path /data1/groups/SUL_TWITTER
# --output_path data/Ida_aug-sept-21/affect_tweets
# --aff_cities_path data/Ida_aug-sept-21/affect_area_files (generated by prepare_files)
# --tweet_type 'worldgeo' (worldgeo or onepercent)
# --years '2021'
# --months '8' '9' (starting from 1)
# --country 'United States'
# --areas 'full_country'

"""
Main script to extract the tweets from users in a designated affected area. For instance, if we wish to select all tweets originating from the United States, 
the result is a subsection of the database with only those tweets. The tweet data is retrieved from data_path; the output tweet data is saved to output_path.
aff_cities_path is a folder with files that contain the names of cities in the affected areas.
"""

from tweet_file import TweetFile
from inference import Inference
from unique_users import UniqueUsers

import os
import pandas as pd
import argparse
import glob

def extract_month_files(args, year):
    """
    Returns files only from month(s) specified in args for the year given as parameter
    """
    months = [int(x) for x in args.months]
    low = min(months)
    high = max(months)

    # Append 0's to month-numbers under 10 because they appear so in filenames (e.g. 9 is 09)
    low = f"0{low}" if low < 10 else low
    high = f"0{high}" if high < 10 else high

    low_ind = -1
    # for worldgeo the files are named like so: 2021-01-01_00_00_01.txt.gz
    # for onepercent the files are named like so: 2021_01_01_00_onepercent.txt.gz
    # We thus have two different dashes
    dash_str = "-" if args.tweet_type == "worldgeo" else "_"

    for index, file in enumerate(args.file_names):
        if file.startswith(f"{year}{dash_str}{str(low)}"):
            if low_ind == -1:
                low_ind = index

        if file.startswith(f"{year}{dash_str}{str(high)}"):
            high_ind = index

    return args.file_names[low_ind : (high_ind+1)]

def stats_to_csv(out_path, len_tweets, matches, date_name, locs=0, is_geo=True):
    """
    Writes some statistics to .csv for each hour-file.
    For geo-tagged tweets: number of tweets and number of matches;
    For regular tweets: number of tweets, number of non-empty location entries, and number of matches
    """
    stats_line = {"tweets": len_tweets, "matches": matches}

    if not is_geo:
        stats_line["locations"] = locs

    df = pd.DataFrame([stats_line])
    stats_out_path = os.path.join(out_path, "stats", "stats_{}.csv".format(date_name))
    df.to_csv(stats_out_path)

def extract_state_matches(country_df, states):
    """
    Extract geo-tag references to the states that are fully affected for the area
    """
    state_df = pd.DataFrame([{}])
    for state in states:
        match = country_df.loc[(country_df["type"] == "admin") &
                               (country_df["full_name"] == state)]
        state_df = pd.concat([state_df, match]).reset_index(drop=True)
    return state_df.loc[1:]

def match_tweets_locs(all_matches, tweet_files, out_path):
    """
    ONLY USED FOR REGULAR TWEETS
    Matching the tweets and users in each tweet file to the user ID's and inferred user locations in all_matches
    Params:
        all_matches: DataFrame with all unique users, profile locations and inferred location
        tweet_files: list of TweetFile objects, each TweetFile object is the tweets of one hour-file
    """
    print("Merging tweet files with inferred location")
    for tweet_file in tweet_files:
        tweets_df = tweet_file.get_tweets()
        tweets_df = tweets_df[["tweet_id", "user_id"]]
        df = pd.merge(tweets_df, all_matches, left_on="user_id", right_on="user_id")
        print("Merged: ", df.head().to_string())
        df = df[["tweet_id", "user_id", "location", "inferred loc"]]

        # Tweets to csv
        df.to_csv(os.path.join(out_path, "tweets", "aff_{}.csv".format(tweet_file.get_date_name())))

        # Stats to csv
        matches = len(df)
        print("Location matches for file {}: {}".format(tweet_file.get_date_name(), matches))
        locs = tweet_file.get_len_tweets() # Number of tweets with non-empty location entry, because locs_only=True
        all_tweets = tweet_file.get_len_all_tweets() # Number of tweets (all)
        stats_to_csv(out_path, all_tweets, matches, tweet_file.get_date_name(), locs, is_geo=False)

def affect_tweets_worldgeo(args, tweets_folder_path, out_path, area, full_states):
    """
    Finds tweets originating from Ida-affected area for geo-tagged tweets
    """
    if area != "full_country":
        # Read in Dataframe with affected cities for this area. If one of these cities is referenced in the tag, the
        # tweet originates from the Ida-affected area
        aff_path = os.path.join(args.aff_cities_path, "Ida_files", area+".csv")
        aff_cities = pd.read_csv(aff_path)

    for file in args.file_names:
        print("File: ", file)
        tweets_path = os.path.join(tweets_folder_path, file)

        # Make TweetFile object to store the data for each hour-file
        tweet_file = TweetFile(tweets_path, is_geo=True)
        tweets_df = tweet_file.get_tweets()
        len_tweets = tweet_file.get_len_tweets()  # Number of tweets in original file
        date_name = tweet_file.get_date_name()  # date_name is like 2021-08-01_00_00_00 (no path or extension)

        # Find the tweets tagged with the country as specified in args
        country_df = tweets_df[tweets_df["country"] == args.country]
        country_df = country_df[["tweet_id", "user_id", "type", "full_name"]]

        if area == "full_country":
            # If the area is full_country, all the geo-tags originating from the country should be included, so write this to csv
            country_df.to_csv(os.path.join(out_path, "tweets", "aff_{}.csv".format(date_name)))

            matches = len(country_df)
            print("Matches: ", matches)
            stats_to_csv(matches, len_tweets, out_path, date_name)
        else:
            # If area is not full_country, only the geo-tags originating from the specific sub-area should be included. This is a subset of country_df

            # Extract the tweets that match with affected cities
            city_df = country_df[country_df["type"] == "city"]
            city_df = city_df.merge(aff_cities, left_on="full_name", right_on="city_and_abbrev")

            # Extract the tweets that geo-tag the fully affected state(s) of the area (stored in full_states dictionary)
            state_df = extract_state_matches(country_df, full_states[area])
            df = pd.concat([city_df, state_df]).reset_index(drop=True)
            df = df[["tweet_id", "user_id", "full_name"]]

            # Tweets to csv
            df.to_csv(os.path.join(out_path, "tweets", "aff_{}.csv".format(date_name)))

            matches = len(df)
            print("Matches: ", matches)
            stats_to_csv(matches, len_tweets, out_path, date_name)

def affect_tweets_oneperc(args, tweets_folder_path, out_path, area):
    """
    Finds tweets originating from Ida-affected area for regular tweets, not geo-tagged
    """
    unique_users = UniqueUsers() # Create UniqueUsers object to store the unique users over all files
    tweet_files = [] # List to store the tweet files so we don't have to load them again

    for file in args.file_names:
        print("\nFile: ", file)
        tweets_path = os.path.join(tweets_folder_path, file)

        # Make TweetFile object - not geo-tagged, storing only tweets with non-empty location
        tweet_file = TweetFile(tweets_path, is_geo=False, locs_only=True)
        tweets_df = tweet_file.get_tweets() # Tweets with non-empty profile location

        # To update the unique users we only need the user ID and location, not tweet ID
        unique_users.update_users(tweets_df[["user_id", "location"]])
        tweet_files.append(tweet_file)

    users = unique_users.get_users() # Single file with all unique users for all files

    # Read in affected city names and regex and instantiate Inference object
    aff_path = os.path.join(args.aff_cities_path, "regex_files", "Location_{}.xlsx".format(area))
    inference = Inference(aff_path)

    # Infer the location with the regex for the unique users
    all_matches = inference.inference_loc(users)
    all_matches.to_csv(os.path.join(out_path, "{}_unique_users_loc.csv".format(area)), index=False)
    print("All matches found")

    # Now that we have inferred the location for all users, we have to connect this to the users in each hour-file
    # The result is the inferred location for the users in each hour-file
    match_tweets_locs(all_matches, tweet_files, out_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--data_path', default='', type=str, help='Path to tweets data')
    parser.add_argument('--output_path', default='', type=str,
                        help='Path to output where we store the tweets from affected areas')
    parser.add_argument('--aff_cities_path', default='', type=str, help='Path to .csv file with affected cities')
    parser.add_argument('--years', nargs='*', default=['2021'], type=str,
                        help='Which year(s) are we selecting tweets for')
    parser.add_argument('--months', nargs='*', default='', type=str,
                        help='Which month(s) are we selecting tweets for')
    parser.add_argument('--tweet_type', default='worldgeo',
                        help='What type of tweets are we analyzing? (worldgeo, onepercent)')
    parser.add_argument("--country", default="United States", type=str, help="Country to select affected tweets for")
    parser.add_argument("--areas", nargs="*", default="full_country", type=str,
                        help="What specific areas do we want to find the tweets for")
    parser.add_argument("--sub_files", nargs="*", default="", type=str, help="Sub section of files where we want to find affected tweets for")
    args = parser.parse_args()

    # Fully affected states for the areas  - hard-coded but can be added as argument
    n_states = ["New Jersey, USA"]
    s_states = ["Louisiana, USA", "Mississippi, USA"]

    # Dictionary of fully affected states for each area (north and south). Used for geo-tag references
    full_states = {"north": n_states, "south": s_states}

    for year in args.years:
        tweets_folder_path = os.path.join(args.data_path, args.tweet_type, year)

        if args.sub_files == "":
            args.file_names = sorted([os.path.basename(elem) for elem in glob.glob(os.path.join(tweets_folder_path, "*"))])
            # Store the basename of the file, like 2021-01-01_00_00_01.txt.gz, and not its full path, for easy reference later

            if args.months != '':
                # If specific months are given, not all months of the year should be included
                args.file_names = extract_month_files(args, year)
        else:
            args.file_names = args.sub_files

        print("Extracting tweets from the following files: ", args.file_names)

        # Get tweets from affected areas
        for area in args.areas:
            out_path = os.path.join(args.output_path, args.tweet_type, year, area)
            print("Out path: ", out_path)

            # Regular tweets
            if args.tweet_type == "onepercent":
                affect_tweets_oneperc(args, tweets_folder_path, out_path, area)

            # Geo-tagged tweets
            else:
                affect_tweets_worldgeo(args, tweets_folder_path, out_path, area, full_states)









