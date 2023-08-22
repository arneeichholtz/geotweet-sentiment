# Example params:
# --senti_scores_path data/Ida_aug-sept-21/sentiment_scores
# --aff_tweets_path data/Ida_aug-sept-21/affect_tweets
# --output_path data/Ida_aug-sept-21/aggregated_sentiment
# --years '2021'
# --tweet_type 'worldgeo'
# --areas 'north' 'south'

"""
Main script to aggregate the sentiment scores of the tweets and the location of the Twitter users. Sentiment scores for all tweets in the database are stored at
senti_scores_path; the affected tweets are stored at aff_tweets_path; the sentiment scores for users from the affected area is saved to output_path
"""

import argparse
import numpy as np
import pandas as pd
import os
import glob

def standardize(values):
    mean = np.nanmean(values)
    std = np.nanstd(values)
    return [(value - mean)/std for value in values]

def comp_single_file(out_path, area):
    """
    Compile single file with all the means and standardized scores for the hour-files
    """
    score_files = sorted(glob.glob(os.path.join(out_path, "*")))
    means, base_names = [], []
    for file in score_files:
        base_name = os.path.basename(file)
        base_names.append(base_name)
        mean = pd.read_csv(file)["mean"].iloc[0]
        means.append(mean)

    means = {"base_name": base_names, "mean": means, "standardized": standardize(means)}
    df = pd.DataFrame(means)
    df.to_csv(os.path.join(out_path, f"all_means_{area}.csv"))

def align_folders(score_files, aff_tweet_files):
    """
    Align folders if a score file is missing, this tweet file should be skipped - only works if a single score file is missing in single sequence
    """
    iter_score = iter(score_files)
    iter_tweets = iter(aff_tweet_files)
    scores, aff_tweets = [], []

    for score_file, tweet_file in zip(iter_score, iter_tweets):
        hour_score = score_file.split("_")[4]
        hour_tweet = tweet_file.split("_")[4]

        if hour_score != hour_tweet:
            tweet_file = next(iter_tweets)

        scores.append(score_file)
        aff_tweets.append(tweet_file)
    return scores, aff_tweets

def get_date_name(score_file):
    beg_ind = score_file.index("_")
    end_ind = score_file.index(".")
    date_name = score_file[beg_ind + 1: end_ind]
    return date_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--senti_scores_path", default='', type=str, help="Path to sentiment score files")
    parser.add_argument("--aff_tweets_path", default='', type=str, help="Path to affected tweet files")
    parser.add_argument("--output_path", default="", type=str,
                        help="Path to output of aggregated sentiment scores per hour-file")
    parser.add_argument('--years', nargs='*', default=['2021'], type=str,
                        help='Which year(s) are we aggregating scores for')
    parser.add_argument('--tweet_type', default='worldgeo',
                        help='What type of tweets are we analyzing? (worldgeo, onepercent)')
    parser.add_argument("--areas", nargs="*", default="full_country", help="Which areas do we want to aggregate for")
    args = parser.parse_args()

    for year in args.years:
        scores_path = os.path.join(args.senti_scores_path, args.tweet_type, year)
        score_files = sorted([os.path.basename(elem) for elem in glob.glob(os.path.join(scores_path, "*"))])

        for area in args.areas:
            tweets_path = os.path.join(args.aff_tweets_path, args.tweet_type, year, area)
            aff_tweet_files = sorted([os.path.basename(elem) for elem in glob.glob(os.path.join(tweets_path, "tweets", "*"))])
            out_path = os.path.join(args.output_path, args.tweet_type, year, area)

            # Some files might be missing in the sentiment scores, also need to remove these from affected tweets
            score_files, aff_tweet_files = align_folders(score_files, aff_tweet_files)

            for score_file, aff_tweet_file in zip(score_files, aff_tweet_files):
                score_path = os.path.join(scores_path, score_file)
                aff_path = os.path.join(tweets_path, "tweets", aff_tweet_file)

                date_name = get_date_name(score_file)
                print("date name: ", date_name)
                if date_name not in aff_tweet_file:
                    # We must be sure that we combine senti score and affected tweets of the same hour-file
                    print("The file names are different. \nscore file: {} \naffected tweets file: {}"
                          .format(score_file, aff_tweet_file))
                else:
                    senti_df = pd.read_csv(score_path)
                    senti_df = senti_df[senti_df["score"] <= 1]

                    aff_tweets_df = pd.read_csv(aff_path)

                    # Merge affected tweets with sentiment scores to get the score for tweets from the affected area only
                    df = aff_tweets_df.merge(senti_df, left_on="tweet_id", right_on="message_id")
                    df = df[["score"]]

                    mean_score = np.mean(df['score'])
                    mean_df = pd.DataFrame([{"mean": mean_score}])
                    mean_df.to_csv(os.path.join(out_path, "aggr_score_{}.csv".format(date_name)))

            # Compile all the average scores and standardized values into a single .csv file
            comp_single_file(out_path, area)
