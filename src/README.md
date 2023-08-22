## Organization of folder

-`main_sentiment_imputer.py` computes sentiment scores

-`setup_emb_clf.py` trains neural network on 1.6mln labeled tweets

-`project_ida` folder for location inference for Hurricane Ida Project

-`utils` various helper functions

### Example usage of scripts

### Compute sentiment scores:
```
python3 src/sentiment_imputer_AE.py --data_path /data1/groups/SUL_TWITTER/worldgeo --output_path data/Ida_aug-sept-21/sentiment_scores --years '2021' --months '8' '9' --tweet_type 'worldgeo'
```


