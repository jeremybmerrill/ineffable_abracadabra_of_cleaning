import similarize

from w2v_api import w2v_api
import threading
from twitter import *
import yaml
from time import sleep
from datetime import datetime

def api_thread():
    w2v_api.run()

#start the API
threads = []
t = threading.Thread(target=api_thread)
t.daemon = True
threads.append(t)
t.start()

#once the API is started, get twitter creds, generate a joke, tweet it, then sleep
with open('twitter_creds.secret', 'r') as f:
  creds = yaml.load(f)
  t = Twitter(auth=OAuth(creds["token"], creds["secret"], creds["consumer_key"], creds["consumer_secret"]))

while True:
  now  = datetime.now()
  print("what time is it? it's %i:%i" % (now.hour, now.minute))
  if (now.hour == 9 or now.hour == 16) and now.minute > 0 and now.minute < 10:
    joke = similarize.do()
    if len(joke) < 140:
      t.statuses.update(status=joke)
  sleep(60 * 10) # check the time every ten minutes
