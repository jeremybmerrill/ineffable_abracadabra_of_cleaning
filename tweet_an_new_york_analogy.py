from __future__ import print_function
import json

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
import os
import yaml
import new_york_version_bot
import urllib3

current_dir = os.path.dirname(__file__)
twitter_creds_filename = os.path.join(current_dir, 'twitter_creds.secret')
username = None
twitterApi = None
with open(twitter_creds_filename, 'r') as f:
  creds = yaml.load(f)
  username = creds["username"]
  # twitter = Twitter(auth=OAuth(, creds["secret"], creds["consumer_key"], creds["consumer_secret"]))

  auth = OAuthHandler(creds["consumer_key"], creds["consumer_secret"])
  auth.set_access_token(creds["token"], creds["secret"])
  twitterApi = API(auth)

class ReplyToTweet(StreamListener):
    def on_data(self, data):
        tweet = json.loads(data.strip())
        
        retweeted = tweet.get('retweeted')
        from_self = tweet.get('user',{}).get('screen_name','') == username

        if retweeted is not None and not retweeted and not from_self:

            original_tweet_id = tweet.get('id_str')
            interlocutor_sn = tweet.get('user',{}).get('screen_name')
            original_tweet_text = tweet.get('text')
            original_tweet_url = "https://twitter.com/{}/status/{}".format(tweet.get('user').get('screen_name'), original_tweet_id)

            try:
              tweet_text_to_parse = original_tweet_text.replace("@{}".format(username), '').strip()
              print("parsing: {}".format(tweet_text_to_parse))
              analogy_text = new_york_version_bot.parse_and_analogize(tweet_text_to_parse)
            except Exception as e:
              analogy_text = None
              print("failed: {}".format(e))
            if analogy_text: 

              replyText = analogy_text.lower() + " " + original_tweet_url

              #check if response is over 140 char

              print('Tweet ID: ' + original_tweet_id)
              print('From: ' + interlocutor_sn)
              print('Tweet Text: ' + original_tweet_text)
              print('Reply Text: ' + replyText)

              # If rate limited, the status posts should be queued up and sent on an interval
              # was in_reply_to_status_id=original_tweet_id
              twitterApi.update_status(status=replyText)
            else: 
              print("no analogy text")

    def on_error(self, status):
        print("on error had error")
        print(status)


if __name__ == '__main__':
  while True:
    try:
      streamListener = ReplyToTweet()
      twitterStream = Stream(auth, streamListener)
      twitterStream.userstream(_with='user')
    except urllib3.exceptions.ReadTimeoutError:
      pass