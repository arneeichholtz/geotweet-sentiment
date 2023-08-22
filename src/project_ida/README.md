## Organization of folder

- `main_affected_tweets.py` Main script to extract the tweets from users in a designated affected area. For instance, if we wish to select all tweets originating from the United States, the result is a subset of the database with only those tweets. The tweet data is retrieved from data_path; the output tweet data is saved to output_path.
aff_cities_path is a folder with files that contain the names of cities in the affected areas.

- `main_senti_aggregator.py` 

- `prepare_files.py` 

- `inference.py` 

- `tweet_file.py` 

- `unique_users.py` 

### Example usage of scripts

### Compute sentiment scores:
```
python3 src/main_sentiment_imputer.py --data_path /data1/groups/SUL_TWITTER/worldgeo --output_path data/Ida_aug-sept-21/sentiment_scores --years '2021' --months '8' '9' --tweet_type 'worldgeo'
```

### Train nn:
```
python3 src/setup_emb_clf.py --max_seq_length 64
```


