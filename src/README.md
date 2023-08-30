## Organization of folder

Code partly adapted from Covid sentiment Nature paper, see this repository: https://github.com/Jianghao/Sentiment_COVID-19

- `main_sentiment_imputer.py` computes sentiment scores

- `setup_emb_clf.py` trains neural network on 1.6mln labeled tweets

- `project_ida` folder for location inference for Hurricane Ida Project. (Fully my own work)

- `utils` various helper functions

### Example usage of scripts

### Compute sentiment scores:
```
python3 src/main_sentiment_imputer.py --data_path /data1/groups/SUL_TWITTER/worldgeo --output_path data/Ida_aug-sept-21/sentiment_scores --years '2021' --months '8' '9' --tweet_type 'worldgeo'
```

### Train nn:
```
python3 src/setup_emb_clf.py --max_seq_length 64
```


