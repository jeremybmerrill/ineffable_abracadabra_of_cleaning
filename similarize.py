import Levenshtein
import re, string, json, sys
from random import random, randint, choice
from titlecase import titlecase
from datetime import datetime
from itertools import groupby
from nltk.stem import *
import requests
import csv
from tokenizer import TreebankWordTokenizer
import yaml

stemming = False
similar_words_source = "api"
chosen_synonyms = {}


api_keys = {}
with open("api-keys.secret") as f:
  api_keys = yaml.load(f)

import re, collections
class NorvigSpellCheck:
  """ via http://norvig.com/spell-correct.html """
  def __init__(self):
    def words(text): return re.findall('[a-z]+', text.lower()) 

    def train(features):
        model = collections.defaultdict(lambda: 1)
        for f in features:
            model[f] += 1
        return model

    self.NWORDS = train(words(file('eng_news_2013_1M/eng_news_2013_1M-words.txt').read()))

  alphabet = 'abcdefghijklmnopqrstuvwxyz'

  def edits1(self, word):
     splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
     deletes    = [a + b[1:] for a, b in splits if b]
     transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
     replaces   = [a + c + b[1:] for a, b in splits for c in self.alphabet if b]
     inserts    = [a + c + b     for a, b in splits for c in self.alphabet]
     return set(deletes + transposes + replaces + inserts)

  def known_edits2(self,word):
      return set(e2 for e1 in self.edits1(word) for e2 in self.edits1(e1) if e2 in self.NWORDS)

  def known(self, words): return set(w for w in words if w in self.NWORDS)

  def correct(self, word):
      candidates = self.known([word]) or self.known(self.edits1(word)) or self.known_edits2(word) or [word]
      return max(candidates, key=self.NWORDS.get)

if stemming:
  from nltk.stem.porter import *
  stemmer = PorterStemmer()
  from difflib import SequenceMatcher
  spell_check = NorvigSpellCheck()

def api_exists():
  try:
    resp = requests.get("http://localhost:5000")
    return resp.json()["loaded"] == True
  except requests.exceptions.ConnectionError:
    return False
def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result



stopwords = ["Harry Potter", "Harry", "Potter", "how", "where"]
with open("stopwords.txt") as f:
  for line in f:
    stopwords.append(line.strip())
non_alpha_chars = re.compile("[\W]+")
cached_synonyms = {}

if not api_exists() and similar_words_source == "local":
  try:
    from gensim.models.word2vec_inner import train_sentence_sg, train_sentence_cbow, FAST_VERSION
  except ImportError:
    print("uninstall scipy, install scipy 0.15.1, then reinstlal gensim (without -U)")

  import gensim
  from  gensim.models import Word2Vec
  start = datetime.now()
  print("start loading w2v " + str(start))
  # w2v_model = Word2Vec.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)  # C binary format
  # w2v_model = Word2Vec.load("en_1000_no_stem/en.model") # MemoryError :-(
  print("finish loading w2v" +  str(datetime.now()))
  print("loading w2v took  " + str((datetime.now() - start).seconds) + " seconds")

def rephrase(sentence, theme=None):
  new_version = []
  # def reducer(memo, char): #TODO: should not split on apostrophes in "can't" or "eatin'" but should for "spiders'"
  #   if (char.isalpha() or char == "'") == (memo[-1][-1].isalpha() or memo[-1][-1] == "'"):
  #     memo[-1] = memo[-1] + char
  #     return memo
  #   else:
  #     return memo + [char]
  # words = reduce( reducer , list(sentence.strip()), [' '])
  words = []
  my_sentence = sentence[0:]
  tokens = TreebankWordTokenizer().tokenize(sentence)
  for token in tokens:
    split_idx = my_sentence.index(token)
    if(len(my_sentence[0:split_idx]) > 0):
      words.append(my_sentence[0:split_idx])
    words.append(my_sentence[split_idx:(split_idx+len(token))])
    my_sentence = my_sentence[(split_idx+len(token)):]
  # words = [word for sublist in [[word, ' '] for word in TreebankWordTokenizer().tokenize(sentence)] for word in sublist ]
  for word in words:
    if word == '':
      continue
    if word in stopwords or not word[0].isalpha():
      new_version.append(word)
    else:
      # TODO: retain punctuation
      prefixes = []
      suffixes = []
      for thing, fix  in [(list(word), prefixes), (list(reversed(word)), suffixes)]:
        for char in thing:
          if non_alpha_chars.match(char):
            fix.append(char)
          else:
            break
      # print(word)
      # removes non-alphabetic chars in the word.
      # I don't recall why this is in here.
      # removing it so "you're" stays "you're" not "youre"
      # word = non_alpha_chars.sub('', word)
      # print(word)
      if stemming:
        word_stem = stemmer.stem(word)
        word_morphology = word_diff(word, word_stem)
        random_weird_changes = word_diff(word_stem, word)
        print("%s = %s + %s (- %s)" % (word, word_stem, word_morphology, random_weird_changes) )

        synonym_stem = get_synonym(word_stem, theme)
        if random_weird_changes:
          print("random_weird_changes: %s" % random_weird_changes)
          reversed_synonym_stem = list(synonym_stem[::-1]) # [::-1] reverses a string because Python is intuitive
          for subtraction in reversed(random_weird_changes):
            if reversed_synonym_stem[0] == subtraction:
              print("removed %s" % reversed_synonym_stem[0])
              reversed_synonym_stem = reversed_synonym_stem[1:]
            else:
              break
          synonym_stem = reversed_synonym_stem[::-1] # [::-1] reverses a string because Python is intuitive

        misspelled_synonym = ''.join(synonym_stem) + "".join(word_morphology)
        synonym = spell_check.correct(misspelled_synonym)
      else:
        synonym = get_synonym(word, theme)
      print("new version" + str(new_version))
      new_version.append(''.join(prefixes) + synonym + ''.join(reversed(suffixes)))
  print("new version" + str(new_version))
  return titlecase(''.join(new_version).strip().replace(" 's", "'s"))

# ugh I want a stemmed model
# alternatively, to reject similar words that have a different morphology

def word_diff(longer_word, shorter_word):
  print("diff %s - %s" % (longer_word, shorter_word))
  if longer_word == shorter_word:
    return []
  # via http://stackoverflow.com/questions/6486450/python-compute-list-difference
  a = list(longer_word)
  b = list(shorter_word)
  squeeze=SequenceMatcher( None, a, b)
  return reduce( lambda p,q: p+q, 
               map( lambda t: squeeze.a[t[1]:t[2]], 
                    filter(lambda x:x[0]!='equal', 
                           squeeze.get_opcodes() ) ) )


def get_similar_words_from_wordnik(word):
  try:
    try: 
      similar_words = cached_synonyms[word]
    except KeyError:
      print("going to the web " + word + " not in " + str(cached_synonyms.keys() ))
      resp = requests.get("http://api.wordnik.com:80/v4/word.json/"+word+"/relatedWords?useCanonical=false&relationshipTypes=&limitPerRelationshipType=100&api_key=" + api_keys["wordnik"]).json()
      similar_words = []
      if len(resp) > 0:
        if "synonym" in [item["relationshipType"] for item in resp]:
          similar_words += [ (synonym, 1) for synonym in [item for item in resp if item["relationshipType"] == "synonym"][0]["words"]] 
        if "hypernym" in [item["relationshipType"] for item in resp]:
          similar_words += [ (synonym, 0.5) for synonym in [item for item in resp if item["relationshipType"] in ("hypernym")][0]["words"]]

      if not len(similar_words):
        similar_words = [(word, 1)]
      cached_synonyms[word] = similar_words
  except KeyError: #word not in vocabulary
    return word
  print("words similar to " + word + " " + str(similar_words)) 
  return similar_words

def get_similar_words_from_api(word):
  try:
    try: 
      return cached_synonyms[word]
    except KeyError: # word not cached
      resp = requests.get("http://localhost:5000/similarize/" + word).json()
      if len(resp["similar_words"]) > 0:
        cached_synonyms[word] = resp["similar_words"]
        return resp["similar_words"]
      else: 
        return [[word, 1]]
  except KeyError: #word not in vocabulary
    return [[word, 1]]



def get_themed_similar_words_from_api(word, theme):
  resp = requests.get("http://localhost:5000/themed/" + word + "/" + theme).json()
  if len(resp["similar_words"]) > 0:
    return resp["similar_words"]
  else: 
    return [[word, 1]]


def get_similar_words_from_local_w2v(word):
  try:
    try: 
      similar_words = cached_synonyms[word]
    except KeyError:
      similar_words = w2v_model.most_similar(positive=[word], negative=[], topn=20)
      cached_synonyms[word] = similar_words
  except KeyError: #word not in vocabulary
    return word
  print("words similar to " + word + " " + str(similar_words)) 
  return similar_words

# TODO: if there's nothing, try the canonical form, then compare, of the returned options, which has a form that has the same morphology (the most matching letters on the end)

# words should have one synonym for the whole jokes, so "How to talk so kids will listen and listen so kids will talk" maintains its symmetry. (that goes into chosen_synonyms)
def get_synonym(word, theme=None):
  try: 
    print("checking for " + word + " in chosen_synonyms")
    return chosen_synonyms[word]
  except KeyError:
    print("couldn't find " + word)
    if similar_words_source == "api":
      if theme is not None:
        similar_words = get_themed_similar_words_from_api(word, theme)
      else:
        similar_words = get_similar_words_from_api(word)
    elif similar_words_source == "wordnik":
      if theme is not None:
        raise "not implemented"
      similar_words = get_similar_words_from_wordnik(word)
    elif similar_words_source == "local":
      if theme is not None:
        raise "not implemented"
      similar_words = get_similar_words_from_local_w2v(word)
    
    print(similar_words)
    synonyms = [(synonym, similarity) for (synonym, similarity) in similar_words if any([l.isupper() for l in list(synonym)]) == any([l.isupper() for l in list(word)]) and unicode(word).lower() not in unicode(synonym).lower() and Levenshtein.distance(unicode(word), unicode(synonym[0:max(len(synonym), len(word))])) > 3]
    # weight by similarity, pick randomly
    total_similarness = sum([(similarity ** 2 if '_' not in synonym else (similarity ** 2) / 4) for (synonym, similarity) in synonyms])
    r = random() * total_similarness
    for synonym, similarity in synonyms:
      r -= similarity ** 2
      if r <= 0:
        chosen_synonyms[word] = synonym.replace("_", " ")
        return chosen_synonyms[word]
    chosen_synonyms[word] = similar_words[0][0].replace("_", " ") # this is reachable only if the only synonym is the same as the word
    return chosen_synonyms[word]

def get_titles_from_nyt_api():
  resp = requests.get("http://api.nytimes.com/svc/books/v2/lists/overview.json?api-key=" + api_keys["nyt"]).json()
  # [u'Combined Print and E-Book Fiction', u'Combined Print and E-Book Nonfiction', u'Hardcover Fiction', u'Hardcover Nonfiction', u'Trade Fiction Paperback', u'Mass Market Paperback', u'Paperback Nonfiction', u'E-Book Fiction', u'E-Book Nonfiction', u'Advice How-To and Miscellaneous', u'Picture Books', u'Childrens Middle Grade Hardcover', u'Childrens Middle Grade Paperback', u'Childrens Middle Grade E-Book', u'Young Adult Hardcover', u'Young Adult Paperback', u'Young Adult E-Book', u'Series Books', u'Hardcover Graphic Books', u'Paperback Graphic Books', u'Manga', u'Animals', u'Business Books', u'Crime and Punishment', u'Culture', u'Education', u'Family', u'Fashion Manners and Customs', u'Humor', u'Hardcover Political Books', u'Relationships', u'Science', u'Travel']
  eligible_books = [item for sublist in [[merge_dicts(book,  {"list_name": l["list_name"]}) for book in l["books"] if book["title"].count(" ") > 3 and "vol." not in book["title"].lower()] for l in resp["results"]["lists"] if l["list_name"] not in ["Games and Activities"] ] for item in sublist]
  return [(book["title"], book["author"]) for book in eligible_books]

def get_titles_from_wikipedia_csv():
  titles = []
  with open('bestselling books.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      # "Book","Author(s)","Original language","First published","Approximate sales"
      if row["Book"].count(" ") > 3:
        titles.append((row["Book"], row["Author(s)"]))
  return titles


def get_titles_from_book_titles_dot_text():
  titles = []
  with open("book_titles.txt") as f:
    for line in enumerate(f):
      titles.append(line)
  return [(title, "?") for title in titles]

def get_candidate_titles():
  if len(sys.argv) > 2:
    return (sys.argv[1], sys.argv[2])
  elif False:
    return get_titles_from_book_titles_dot_text()
  elif False:
    return get_titles_from_nyt_api()
  elif False:
    return get_titles_from_wikipedia_csv()
  elif True:
    return get_titles_from_wikipedia_csv() + get_titles_from_nyt_api()

def do():
  if False: #make one joke per choice
    jokes = []
    for i, line in get_candidate_titles():
      for n in xrange(0, 10):
        joke = rephrase(line)
        if joke == '':
          continue
        jokes.append(joke)
        print(joke)
    for joke in jokes:
      print(joke)
    return jokes
  elif True: # pick a book title from the NYT bestsellers API and make a joke title from it
    book = choice(get_candidate_titles())
    joke_title = rephrase(book[0].lower())
    print(book)
    return "What %s should write next: \n\n%s" % (book[1], joke_title)
  elif False: #rephrase it with a random theme (but the themes don't actually work)
    book = choice(get_candidate_titles())
    theme = choice(["art", "music", "pop", "history", "politics", "sex", "fashion", "food", "travel" ])
    joke_title = rephrase(book[0].lower(), theme)
    print(book)
    return "What if %s was about %s: \n\n%s" % (book[0], theme, joke_title)


if __name__ == "__main__":
  print do()