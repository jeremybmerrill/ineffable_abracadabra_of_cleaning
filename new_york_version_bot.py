import json
import sys
import requests
import re
from random import random

class NoAnaloguesException(Exception):
  pass
# "Pizza but for Atlanta"
# "Met but for Chicago"
# "Mets but in Chicago" 
#  TK: 
# "What is Atlanta's version of Pizza?"
# "New York : Pizza :: Atlanta : "
# "I'm moving to Atlanta and like Pizza"

SCALE_FACTOR = 50
matcher = re.compile("(?:what (?:is|are) ?)*(?:a ?)* *([A-Za-z ]+) [a-z]+? [a-z]+? ([A-Za-z ]+)", re.I) # TODO: more of these
SENTENCE_OPTIONS = [ # New York, Pizza, Atlanta, Chili
            "{2}'s version of {1} is {3}",
            "{2}'s answer to {0}'s {1} is {3}",
            "{0} is to {1} as {2} is to {3}",
            "if you like {1} in {0}, you'll love the {3} in {2}!",
            ]
SUFFIX_OPTIONS = ["(Or maybe the {})"]

def pick_one(arr):
  return arr[int(random()* len(arr))]

def pick_similar_word(candidates):
  total_similarness = sum([(similarity ** SCALE_FACTOR) for (synonym, similarity) in candidates])
  original_r = r = random() * total_similarness
  for synonym, similarity in candidates:
    r -= similarity ** SCALE_FACTOR
    if r <= 0:
      return synonym

def parse(tweet):
  matches = re.findall(matcher, tweet) #or re.match()
  print(matches)
  return matches[0]

def analogy(word, isto, as_):
  resp_json = requests.get("http://localhost:5000/analogy/{}/{}/{}".format(word, isto.lower().replace(" ", "_"), as_.lower().replace(" ", "_")))
  resp = resp_json.json()

  analogue = pick_similar_word(resp["similar_words"])
  if not analogue:
    raise NoAnaloguesException("no analogue for {} : {} :: {} : _____".format(word, isto, as_))
  analogue = analogue.replace("_", " ").title()
  while True:
    another_analogue = pick_similar_word(resp["similar_words"]).replace("_", " ").title()
    if another_analogue != analogue:
      break
  sentence = pick_one(SENTENCE_OPTIONS).format(word.replace("_", " ").title(), isto, as_, analogue)
  suffix = pick_one(SUFFIX_OPTIONS).format(another_analogue)
  sentence_plus_suffix = sentence + " " + suffix
  if len(sentence_plus_suffix) < 140 and random() > 0.8:
    return sentence_plus_suffix
  else:
    return sentence

def parse_and_analogize(text):
  parsed = parse(text)
  try:
    return analogy("new_york", parsed[0], parsed[1])
  except NoAnaloguesException:
    if re.match(r"^the ", parsed[0]):
      return analogy("new_york", re.sub(r"^the ", "", parsed[0]) , parsed[1])
    if re.match(r"^a ", parsed[0]):
      return analogy("new_york", re.sub(r"^a ", "", parsed[0]) , parsed[1])
    if " " in parsed[0]:
      return analogy("new_york", parsed[0].split(" ")[0], parsed[1])


if __name__ == "__main__":
  tweet = sys.argv[1]
  if not tweet:
    print("couldn't parse '{}'".format(tweet))
    exit()
  print(parse_and_analogize(tweet))
