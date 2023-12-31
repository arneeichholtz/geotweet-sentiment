### Organization of folder

Code and setup is my own.

- `main_affected_tweets.py`: script to find tweets from users of the affected area (in this case affected by Hurricane Ida).

- `main_senti_aggregator.py`: script to aggregate the sentiment scores with the user location.

- `prepare_files.py`: script to generate the files used for the location inference, selecting cities, counties and making regex.

- `inference.py`: contains wrapper class for location inference.

- `tweet_file.py`: contains class for the data, ie files with tweets. 

- `unique_users.py`: contains class to save unique users over entire database. 

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
