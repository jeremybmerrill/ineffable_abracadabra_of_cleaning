from __future__ import print_function
import json

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream, Status, API
import os
import yaml
import adjest_noun_in_the_place
import urllib3
import re

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

  def tweet_at_user(self, interlocutor_sn, noun=None):
    print(interlocutor_sn, noun)
    try:
        insult_text = adjest_noun_in_the_place.generate_insult(noun)
    except Exception as e:
      insult_text = None
      print("failed: {}".format(e))
    if insult_text: 
      if interlocutor_sn[0] != "@":
        interlocutor_sn = "@" + interlocutor_sn
      reply_text = ".{}? {}".format(interlocutor_sn, insult_text)
      if len(reply_text) > 140:
        reply_text.replace(", if you know what I mean", '')
      print('Reply Text: ' + reply_text)
      twitterApi.update_status(status=reply_text)
    else: 
      print("no insult text")


  def on_event(self, event):
    if event.event == "follow" :
      print("followed by " + event.source["screen_name"])
      self.tweet_at_user(event.source["screen_name"])
    if event.event == "favorite" :
      print("faved by " + event.source["screen_name"])
      self.tweet_at_user(event.source["screen_name"])
    else:
      print("event", event)

  def on_data(self, json_data):
    data = json.loads(json_data.strip())
    try: 
      if 'delete' in data:
          delete = data['delete']['status']
          if self.on_delete(delete['id'], delete['user_id']) is False:
              return False
      elif 'event' in data:
          status = Status.parse(twitterApi, data)
          if self.on_event(status) is False:
              return False
      elif 'direct_message' in data:
          status = Status.parse(twitterApi, data)
          if self.on_direct_message(status) is False:
              return False
      elif 'friends' in data:
          if self.on_friends(data['friends']) is False:
              return False
      elif 'limit' in data:
          if self.on_limit(data['limit']['track']) is False:
              return False
      elif 'disconnect' in data:
          if self.on_disconnect(data['disconnect']) is False:
              return False
      elif 'warning' in data:
          if self.on_warning(data['warning']) is False:
              return False
      else:
        tweet = data
        retweeted = tweet.get('retweeted')
        reply = tweet.get('in_reply_to_status_id')
        from_self = tweet.get('user',{}).get('screen_name','') == username

        print("how do I tell if htis was retweeted or not?")
        print(tweet)

        if not retweeted and not reply and not from_self:
          original_tweet_id = tweet.get('id_str')
          interlocutor_sn = tweet.get('user',{}).get('screen_name')
          original_tweet_text = tweet.get('text')
          original_tweet_url = "https://twitter.com/{}/status/{}".format(tweet.get('user').get('screen_name'), original_tweet_id)
          print('Tweet ID: ' + original_tweet_id)
          print('From: ' + interlocutor_sn)
          print('Tweet Text: ' + original_tweet_text)

          # parse out something in quotes as the noun to try to use.
          matches = re.search(r"\"([A-Za-z ]+)\"", original_tweet_text)
          if (matches):
            self.tweet_at_user(interlocutor_sn, matches[1])
            print('Target Noun: ' + matches[1])
          else:
            self.tweet_at_user(interlocutor_sn)
    except Exception as e: 
      print("error")
      print(data)
      raise e

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
    except AttributeError:
      pass