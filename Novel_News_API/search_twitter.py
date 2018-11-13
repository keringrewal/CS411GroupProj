from TwitterSearch import *
from private import key_store as ks
import json
import requests

def search_twitter(keywords):
    try:
        tso = TwitterSearchOrder() # create a TwitterSearchOrder object
        tso.set_keywords(keywords) # let's define all words we would like to have a look for
        tso.set_language('en') # we want to see German tweets only
        tso.set_include_entities(False) # and don't give us all those entity information


        info = ks.get_twitter_keys()

        # it's about time to create a TwitterSearch object with our secret tokens
        ts = TwitterSearch(
            consumer_key = info["consumer_key"],
            consumer_secret = info["consumer_secret"],
            access_token = info["access_token"],
            access_token_secret = info["access_secret"]
         )


        tweets = []

        for tweet in ts.search_tweets_iterable(tso):
            if not tweet['text'].startswith('RT') and not tweet['text'].startswith(keywords[0]):
                value = {'id': tweet['id_str'], 'user': tweet['user']['screen_name'], 'text': tweet['text']}
                url = "http://twitter.com/{0}/status/{1}".format(value['user'], value['id'])

                info = [url, value['text'], value['user']]
                tweets.append(info)
            if len(tweets) == 10:
                break

        return tweets



    except TwitterSearchException as e: # take care of all those ugly errors if there are some
        print(e)
