#!/usr/bin/env python
# coding: utf-8

# ## Download Twitter Data

# <!--
# import data_analytics.github as github
# print(github.create_jupyter_notebook_header("markcrowe-com", "data-analytics-project-template", "notebooks/notebook-1-02-dc-twitter-api.ipynb", "master")
# -->
# <table style="margin: auto;"><tr><td><a href="https://mybinder.org/v2/gh/markcrowe-com/data-analytics-project-template/master?filepath=notebooks/notebook-1-02-dc-twitter-api.ipynb" target="_parent"><img src="https://mybinder.org/badge_logo.svg" alt="Open In Binder"/></a></td><td>online editors</td><td><a href="https://colab.research.google.com/github/markcrowe-com/data-analytics-project-template/blob/master/notebooks/notebook-1-02-dc-twitter-api.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a></td></tr></table>

# ### Setup
# Import required third party Python libraries, import supporting functions and sets up data source file paths.

# Local
#!pip install -r script/requirements.txt
# Remote option
#!pip install -r https://raw.githubusercontent.com/markcrowe-com/data-analytics-project-template/requirements.txt
#Options: --quiet --user


from configparser import ConfigParser
from pandas import DataFrame
import tweepy


# ### Twitter
# #### Irish Farming Accounts
# 
# Dept of Agriculture, Food and the Marine:  <a href="https://twitter.com/agriculture_ie" target="_new">@agriculture_ie</a>  
# Leading the sustainable development of Ireland’s agri-food, forestry and marine sectors.

# See [config.ini.sample](config.ini.sample) for the ini file format.

config_filepath = "config.ini"
config_parser = ConfigParser()
config_parser.read(config_filepath)

access_token = config_parser["Twitter"]["AccessToken"]
access_token_secret = config_parser["Twitter"]["AccessTokenSecret"]
consumer_key = config_parser["Twitter"]["ApiKey"]
consumer_secret = config_parser["Twitter"]["ApiKeySecret"]


# <https://python-twitter.readthedocs.io/en/latest/getting_started.html>  
# 
# 
# You need to have a developer account: <https://developer.twitter.com/en/portal/petition/essential/basic-info>
# 
# And apply for elevated access.
# <https://developer.twitter.com/en/portal/products/elevated>

o_auth_handler = tweepy.OAuthHandler(consumer_key, consumer_secret)
o_auth_handler.set_access_token(access_token, access_token_secret)
tweepy_api = tweepy.API(o_auth_handler, wait_on_rate_limit=True)


#Dept of Agriculture, Food and the Marine
screen_name = "agriculture_ie"


tweets = tweepy_api.user_timeline(
    screen_name=screen_name,
    count=200,  # 200 is the maximum allowed count
    include_rts=False,
    tweet_mode="extended"
)  # Necessary to keep full_text otherwise only the first 140 words are extracted


for tweet in tweets[:3]:
    print("ID: {}".format(tweet.id))
    print(tweet.created_at)
    print(tweet.full_text)
    print("\n")


#extract additional tweets

all_tweets = []
all_tweets.extend(tweets)
oldest_id = tweets[-1].id
while True:
    tweets = tweepy_api.user_timeline(
        screen_name=screen_name,
        count=200,# 200 is the maximum allowed count
        include_rts=False,
        max_id=oldest_id - 1,
        # Necessary to keep full_text
        # otherwise only the first 140 words are extracted
        tweet_mode='extended')
    if len(tweets) == 0:
        break
    oldest_id = tweets[-1].id
    all_tweets.extend(tweets)
    print('N of tweets downloaded till now {}'.format(len(all_tweets)))


tweets_list: list = [[
    tweet.id_str, tweet.user.screen_name, tweet.created_at,
    tweet.favorite_count, tweet.retweet_count,
    tweet.full_text.encode("utf-8").decode("utf-8")
] for idx, tweet in enumerate(all_tweets)]


tweet_columns = [
    "id", "screen_name", "created_at", "favorite_count", "retweet_count",
    "text"
]
dataframe = DataFrame(tweets_list, columns=tweet_columns)
dataframe.to_csv('./../assets/twitter-agriculture-ie.csv', index=False)
dataframe.head(3)

