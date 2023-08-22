import argparse
import json
import multiprocessing

import pandas as pd
import numpy as np
import torch
import gzip
import os
import glob
import time
import re

from utils.data_read_in import clean_for_content
from utils.emb_sentiment_imputer import create_embeddings

def extract_latest_file(path):
    """
    Returns the latest added file in folder specified by path
    """
    files = glob.glob(os.path.join(path, "*"))
    latest_file = max(files, key=os.path.getctime)
    return latest_file

def extract_latest_ind(args, year):
    """
    Returns the input folder-index for the file most recently added to the output folder
    (ie, index in input folder from where to continue with imputation)
    """
    latest_output_file = extract_latest_file(os.path.join(args.output_path, year))
    basename = os.path.basename(latest_output_file)
    date = extract_date(basename)
    latest_input_file = next((s for s in args.file_names if date in s), None)
    index = args.file_names.index(latest_input_file)
    return index

def extract_date(basename):
    """
    Extract the date from a basename, like so: sentiment_2016-05-06_16_00_02.csv --> 2016-05-06_16_00_02
    """
    date_index = re.search(r"\d", basename).start()
    end_index = basename.index(".")
    return basename[date_index:end_index]

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

    for index, f in enumerate(args.file_names):
        if f.startswith(f"{year}{dash_str}{str(low)}"):
            if low_ind == -1:
                low_ind = index

        if f.startswith(f"{year}{dash_str}{str(high)}"):
            high_ind = index

    return args.file_names[low_ind:(high_ind + 1)]

def gz_to_dataframe(file_path):
    """
    Converts .txt.gz file to pandas DataFrame format. The tweet text, language, message ID and user ID are saved
        @param file_path: path to file containing tweets. Every file contains tweets sent within an hour interval,
        like 2013-08-26_03_00_02.
    """
    print("Converting gzip file to dataframe..")
    with gzip.open(file_path, "r") as f:
        lines = f.readlines()

    tweets = []
    for line in lines:
        try:
            dict_line = json.loads(line) # Convert string to json dict format

            text = dict_line['text']
            lang = dict_line['lang']
            message_id = dict_line['id']
            user_id = dict_line['user']['id']
            tweet = {'text': text, 'lang': lang, 'message_id': message_id, "user_id": user_id}
            tweets.append(tweet)
        except:
            continue

    print("{} entries out of {} were discarded".format(len(lines)-len(tweets), len(lines)))
    df = pd.DataFrame(tweets)
    return df

def impute_sentiment_embed(file_name, year, args):
    """
    Impute sentiment scores based on the sentence embeddings created by BERT. Sentiment score is the predicted
    probability of the tweet belonging to positive class.
    Params
        file_name: file name for which sentiment will be computed. Note, it is a file name and not a full path
        year: year of the tweets
        args: arguments from ArgParser
    """
    file_path = os.path.join(args.data_path, year, file_name)
    df = gz_to_dataframe(file_path)

    print("Cleaning data")

    df['text'] = [clean_for_content(text, lang) for text, lang in zip(df['text'], df['lang'])]
    df = df[df['text'] != ""].reset_index(drop=True)  # some tweets might have empty text fields after clean_for_content

    # args.emb_model = torch.load('models/emb.pkl')
    # args.clf_model = torch.load('models/clf.pkl')

    predictions, scores = [], []

    print("Imputing Sentiment")
    embeddings = create_embeddings(args.emb_model, df, args)

    # predictions += list(args.clf_model.predict(embeddings))
    scores += list(args.clf_model.predict_proba(embeddings)[:, 1])
    del embeddings

    df['score'] = np.round(scores, args.score_digits)
    scores = df[['message_id', 'user_id', 'score']]  # data frame with only the message ID's, tweet ID's and sentiment scores
    return scores

def imputer(file_name, year, args):
    """
    Imputer function to call the impute_sentiment sub-function and write the output to a csv file
    Params
        file_name: file name for which sentiment will be computed. Note, it is a file name and not a full path
        args: arguments from ArgParser
    """
    try:
        senti_scores = impute_sentiment_embed(file_name, year, args)

        out_path = os.path.join(args.output_path, args.tweet_type, year)
        print("Out path: ", out_path)
        senti_scores.to_csv(os.path.join(out_path, "sentiment_{}.csv".format(extract_date(file_name))))
    except:
        print("File {} does not contain tweets".format(file_name))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', default='', help='What filename do you want to impute sentiment for?')
    parser.add_argument('--platform', default='', help='Which social media data are we using (twitter, weibo)?')
    parser.add_argument('--data_path', default='', type=str, help='Path to data folder')
    parser.add_argument('--output_path', default='data/sentiment_scores/', type=str, help='path to output')
    parser.add_argument('--dict_methods', nargs='*', default='liwc emoji hedono', help='Which dict techniques do you '
                                                                                       'want to use?')
    parser.add_argument('--emb_methods', nargs='*', default='bert',
                        help='Which embedding techniques do you want to use?')
    parser.add_argument('--random_seed', default=123, type=int, help='random seed')
    parser.add_argument('--score_digits', default=6, type=int, help='how many digits to the output score')
    parser.add_argument('--years', nargs='*', default=['2013'], type=str, help='For which years do we want to compute sentiment')

    parser.add_argument('--months', nargs='*', default='', type=str, help='For which month(s) do we want to compute sentiment')
    parser.add_argument('--tweet_type', default='worldgeo', help='What type of tweets are we analyzing? (worldgeo, onepercent)')

    # Emb based parameters
    parser.add_argument('--batch_size', default=100, type=int, help='batch size')

    # Dict based parameters
    parser.add_argument('--max_rows', default=2500000, type=int, help='Run by chunks of how many rows')
    parser.add_argument('--nb_cores', default=min(16, multiprocessing.cpu_count()), type=int, help='')

    args = parser.parse_args()

    if 'bert' in args.emb_methods:
        if torch.cuda.is_available():
            args.emb_model = torch.load('models/emb.pkl')
            args.clf_model = torch.load('models/clf.pkl')
        else:
            print("WARNING: Running on CPU")
            args.emb_model = torch.load('models/emb.pkl', map_location=torch.device('cpu'))
            args.emb_model._target_device = torch.device(type='cpu')
            args.clf_model = torch.load('models/clf.pkl', map_location=torch.device('cpu'))
            args.clf_model._target_device = torch.device(type='cpu')

    for year in args.years:
        if args.filename == '':
            path = os.path.join(args.data_path, year)
            args.file_names = sorted([os.path.basename(elem) for elem in glob.glob(os.path.join(path, "*"))])
            # store the name of the file, like 2013-08.txt.gz, and not its full path, for easy reference later
        else:
            args.file_names = [args.filename]

        # Hard-coded year where the imputer was stopped because of Supercloud maintenance
        if year == '2017':
            # Files still to go from this specific year
            latest_index = extract_latest_ind(args, year) + 1
            args.file_names = args.file_names[latest_index:]

        if args.months != '':
            args.file_names = extract_month_files(args, year)

        print(f"Running for year {year}. This year has {len(args.file_names)} files.")

        for i, file_name in enumerate(args.file_names):
            start = time.time()
            print("\nRunning for {}. {} files left.".format(file_name, len(args.file_names) - (i + 1)))
            imputer(file_name, year, args)
            print("Runtime: {} minutes\n\n".format(round((time.time() - start) / 60, 1)))

    print("Done. All sentiment scores computed.")


