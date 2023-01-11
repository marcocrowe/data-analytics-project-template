#!/usr/bin/env python
# coding: utf-8

# ## Download Twitter Data

# <!--
# import data_analytics.github as github
# print(github.create_jupyter_notebook_header("markcrowe-com", "data-analytics-project-template", "notebooks/notebook-1-02-dc-twitter-api.ipynb", "master")
# -->
# <table style="margin: auto;"><tr><td><a href="https://mybinder.org/v2/gh/markcrowe-com/data-analytics-project-template/master?filepath=notebooks/notebook-1-02-dc-twitter-api.ipynb" target="_parent"><img src="https://mybinder.org/badge_logo.svg" alt="Open In Binder"/></a></td><td>online editors</td><td><a href="https://colab.research.google.com/github/markcrowe-com/data-analytics-project-template/blob/master/notebooks/notebook-1-02-dc-twitter-api.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a></td></tr></table>

# > "It took exhaustive research, sifting through teraquads of data, separating fact from rumor, but eventually I arrived at the truth." - Captain Kathryn Janeway, 2376

# ### Setup

# Import required third party Python libraries, import supporting functions and sets up data source file paths.

# Local
#%pip install -r notebook-1-02-dc-twitter-api/requirements.txt
# Remote option
#%pip install -r https://raw.githubusercontent.com/markcrowe-com/data-analytics-project-template/notebook-1-02-dc-twitter-api/requirements.txt
#Options: --quiet --user


from configparser import ConfigParser
from IPython.display import clear_output
from pandas import DataFrame
import tweepy


# #### Function

MAX_COUNT: int = 200  # 200 is the maximum allowed count
EXTENDED_MODE: str = "extended"  # to keep full_text

def download_user_tweets(o_auth_handler: tweepy.OAuthHandler,
                         screen_name: str,
                         include_re_tweets: bool = False,
                         tweet_count: int = MAX_COUNT,
                         tweet_mode: str = EXTENDED_MODE,
                         tweepy_api_wait_on_rate_limit: bool = True,
                         print_status_updates: bool = True):
    if tweet_count > MAX_COUNT:
        tweet_count = MAX_COUNT

    tweepy_api: tweepy.API = tweepy.API(
        o_auth_handler, wait_on_rate_limit=tweepy_api_wait_on_rate_limit)

    tweets_list: list[tweepy.models.Status] = []
    oldest_id = None
    while True:
        tweets_result_set = tweepy_api.user_timeline(screen_name=screen_name,
                                                     count=tweet_count,
                                                     include_rts=include_re_tweets,
                                                     max_id=oldest_id,
                                                     tweet_mode=tweet_mode)
        if len(tweets_result_set) == 0:
            break
        oldest_id:int = tweets_result_set[-1].id - 1
        tweets_list.extend(tweets_result_set)
        if print_status_updates:
            clear_output(wait=True)
            print(f'Number of tweets downloaded so far {len(tweets_list)}')
    return tweets_list


# ### Twitter config

# <https://python-twitter.readthedocs.io/en/latest/getting_started.html>  
# 
# 
# You need to have a developer account: <https://developer.twitter.com/en/portal/petition/essential/basic-info>
# 
# And apply for elevated access.
# <https://developer.twitter.com/en/portal/products/elevated>

# See [twitter-config.ini.sample](twitter-config.ini.sample) for the ini file format.

config_filepath: str = "twitter-config.ini"
config_parser: ConfigParser = ConfigParser()
config_parser.read(config_filepath)

access_token: str = config_parser["Twitter"]["AccessToken"]
access_token_secret: str = config_parser["Twitter"]["AccessTokenSecret"]
consumer_key: str = config_parser["Twitter"]["ApiKey"]
consumer_secret: str = config_parser["Twitter"]["ApiKeySecret"]


o_auth_handler: tweepy.OAuthHandler = tweepy.OAuthHandler(consumer_key, consumer_secret)
o_auth_handler.set_access_token(access_token, access_token_secret)


# ### Download Irish Farming's Tweets
# 
# Dept of Agriculture, Food and the Marine:  <a href="https://twitter.com/agriculture_ie" target="_new">@agriculture_ie</a>

screen_name: str = "agriculture_ie"  #Dept of Agriculture, Food and the Marine
user_tweets: list[tweepy.models.Status] = download_user_tweets(o_auth_handler, screen_name, True)


# Print 3 Top Tweets

tweet_status: tweepy.models.Status
for tweet_status in user_tweets[:3]:
    print(f"Id: {tweet_status.id}, Timestamp:{tweet_status.created_at}")
    print(tweet_status.full_text.rstrip())
    print()


# ### Extract fields of interest from Tweets

selected_tweet_fields_list: list[list[any]] = [[
    tweet.id_str,
    tweet.user.screen_name, 
    tweet.created_at,
    tweet.favorite_count, 
    tweet.retweet_count,
    tweet.full_text.encode("utf-8").decode("utf-8")
] for _, tweet in enumerate(user_tweets)]


# ### Save Asset

tweet_column_names: list[str] = [
    "id",
    "screen_name",
    "created_at",
    "favorite_count",
    "retweet_count",
    "text"
]
dataframe: DataFrame = DataFrame(selected_tweet_fields_list, columns=tweet_column_names)
dataframe.to_csv('./../assets/twitter-agriculture-ie.csv', index=False)
dataframe.head(3)


# Author &copy; 2022 <a href="https://github.com/markcrowe-com" target="_parent">Mark Crowe</a>. All rights reserved.
