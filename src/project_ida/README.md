### Organization of folder

- `main_affected_tweets.py` 

- `main_senti_aggregator.py` 

- `prepare_files.py` 

- `inference.py` 

- `tweet_file.py` 

- `unique_users.py` 

## Example usage of scripts

### Main affected tweets
onepercent tweets:
```
python3 src/project_ida/main_affected_tweets.py --data_path /data1/groups/SUL_TWITTER --output_path data/Ida_aug-sept-21/affect_tweets --aff_cities_path data/Ida_aug-sept-21/affect_area_files --years '2021' --months '8' '9' --country 'United States' --tweet_type 'onepercent' --areas 'full_country' 'north' 'south' 
```

worldgeo tweets:
```
python3 src/project_ida/main_affected_tweets.py --data_path /data1/groups/SUL_TWITTER --output_path data/Ida_aug-sept-21/affect_tweets --years '2021' --months '8' '9' --country 'United States' --tweet_type 'worldgeo' --areas 'full_country'
```

### Main senti aggregator
```
python3 src/project_ida/main_senti_aggregator.py --senti_scores_path data/Ida_aug-sept-21/sentiment_scores --aff_tweets_path data/Ida_aug-sept-21/affect_tweets --output_path data/Ida_aug-sept-21/aggregated_sentiment --years '2021' --tweet_type 'onepercent' --areas 'north' 'south'
```






### Train nn:
```
python3 src/setup_emb_clf.py --max_seq_length 64
```


