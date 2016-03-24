#!/usr/bin/python

from nltk.stem.porter import *
from tokenizer import TreebankWordTokenizer
import gensim
import logging
from datetime import datetime
import gensim
import cython 
import re
from os.path import exists

# Dear future Jeremy,
# you are going to want to know that there are >#54908750 sentences
# in the corpus. 

# if you want to play with the phrases models, here's what to c/p into python
# import gensim
# bigrams_model_name = "bigrams_model.bin"
# bigrams_model = gensim.models.Phrases.load(bigrams_model_name)
# trigrams_model_name = "trigrams_model.bin"
# trigrams_model = gensim.models.Phrases.load(trigrams_model_name)
# trigrams_model[bigrams_model[["hillary", "rodham"]]


stemming = False

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
# sentences_filename = "eng_news_2013_3M/eng_news_2013_3M-sentences.txt"
sentences_filename = "nyt/taggerAPI/sentences.txt"
smaller_sentences_filename = "nyt_sentences_5.5M.txt"
start = datetime.now()
print("start training w2v " + str(start))

# import re
# apostrophe_tests = {
#   "'ere" : False,
#   "'geez": False,
#   "can't" : True,
#   "would've" : True,
#   "cheese": True,
#   "eatin'" : True,
#   "''what" : False,
#   "''what''" : False,
#   "that''" : False
# }
# for test in apostrophe_tests.keys():
#   if not bool(alpha_re.match(test)) == apostrophe_tests[test]:
#     print(test)

# an iterator, via http://rare-technologies.com/word2vec-tutorial/
class MySentences(object):
  def __init__(self, filename):
    self.filename = filename
    self.alpha_re = re.compile("^[a-zA-Z]+'?[a-zA-Z]*?$") # allow single apostrophes but not double apostrophes: note, this doesn't allow 'ere
    if stemming: 
      self.stemmer = PorterStemmer()
    self.treebank_word_tokenizer = TreebankWordTokenizer()
    # TODO: use http://www.nltk.org/howto/stem.html

  def __iter__(self):
    for line in open(self.filename):
      # TODO find a better way to distinguish sentence-initial caps from proper noun

      # sentences come like this:
      # 80  10:11 p.m., an unwanted person was reported on College Avenue.
      # 81  10:13 a.m., a report of shoplifting was investigated at Maine Smoke Shop on College Avenue.
      # 82  10:14: The proportion of A-levels awarded at least an A grade has fallen for the second year in a row.
      # 141529  But the debt ceiling may end up being the larger inflection point, especially as Obama staked out a hard-lined position against negotiating over that vote.

      sentence = line.decode("UTF8").split("\t", 1)[-1].replace(".", ' ')
      words = [word.lower() for word in self.treebank_word_tokenizer.tokenize(sentence) if re.match(self.alpha_re, word) ]
      if stemming:
        stems = [self.stemmer.stem(word) for word in words]
        yield stems
      else:
        yield words

smaller_sentences = MySentences(smaller_sentences_filename) # a memory-friendly iterator

bigrams_threshold  = 80
trigrams_threshold = 50
bigrams_max_vocab_size  = 10 * 1000 * 1000
trigrams_max_vocab_size = 10 * 1000 * 1000
try:
  bigrams_model_name = "bigrams_model_%(input_filename)s_%(threshold)i_%(max_vocab_size)i.bin" % {
    'input_filename': '.'.join(smaller_sentences_filename.split("/")[-1].split(".")[:-1]),
    'threshold': bigrams_threshold,
    'max_vocab_size': bigrams_max_vocab_size
  }
except:
  bigrams_model_name = "bigrams_model.bin"
if exists(bigrams_model_name):
  bigrams_model = gensim.models.Phrases.load(bigrams_model_name)
else:
  bigrams_model = gensim.models.Phrases(smaller_sentences, threshold=bigrams_threshold, max_vocab_size=bigrams_max_vocab_size)
  bigrams_model.save(bigrams_model_name)


try:
  trigrams_model_name = "trigrams_model_%(input_filename)s_%(threshold)i_%(max_vocab_size)i.bin" % {
    'input_filename': '.'.join(smaller_sentences_filename.split("/")[-1].split(".")[:-1]),
    'threshold': trigrams_threshold,
    'max_vocab_size': trigrams_max_vocab_size
  }
except:
  trigrams_model_name = "trigrams_model.bin"
if exists(trigrams_model_name):
  trigrams_model = gensim.models.Phrases.load(trigrams_model_name)
else:
  trigrams_model = gensim.models.Phrases(bigrams_model[smaller_sentences], threshold=trigrams_threshold, max_vocab_size=trigrams_max_vocab_size)
  trigrams_model.save(trigrams_model_name)



# sentences_with_phrases = [
# "Officials from Libya's moderate governing coalition were demanding that the United States stop the wealthy nation of Qatar from sending money and arms to militias aligned with Libya's Islamist political bloc.",
# "The Islamists, in turn, were accusing a rival gulf power, the United Arab Emirates, of providing similar patronage to fighters aligned with their political enemies.",
# "The appeal from Mitt Romney and the furious reaction to it captured the essence of the party's schism over Donald J. Trump."
# ]
# alpha_re = re.compile("^[a-zA-Z]+'?[a-zA-Z]*$")
# my_treebank_word_tokenizer = TreebankWordTokenizer()
# tokenized_sentences = []
# for line in sentences_with_phrases:
#   sentence = line.decode("UTF8").split("\t", 1)[-1]
#   words = [word.lower() for word in my_treebank_word_tokenizer.tokenize(sentence) if re.match(alpha_re, word) ]
#   tokenized_sentences.append(words)

# # for sent in tokenized_sentences:
# #   print(bigrams_model[sent])
# # trigram = gensim.models.Phrases(bigrams_model[sentences])
# for sent in tokenized_sentences:
#   print(trigrams_model[sent])
# raise Exception

sentences = MySentences(sentences_filename) # a memory-friendly iterator


ngrams_models = {
  "bigrams": lambda x: bigrams_model[x],
  "trigrams": lambda x: trigrams_model[bigrams_model[x]]
}
ngrams_model = "trigrams"
min_count = 50 # was 10
size = 200
downsampling = 1e-3

if False:
  # model = gensim.models.Word2Vec((ngrams_models.get(ngrams_model, None)[sentences] if ngrams_models.get(ngrams_model, None) else sentences), workers=4, min_count=min_count, size=size, sample=downsampling)
  model = gensim.models.Word2Vec(ngrams_models.get(ngrams_model, lambda x: x)(sentences), workers=4, min_count=min_count, size=size, sample=downsampling)

  model.init_sims(replace=True)
  try:
    model_name = "model_%s_%s_%s_min_count_%s_size_%s_downsampling_%s.bin" % (sentences_filename.split("/")[-1].split(".")[0], "stemmed" if stemming else "raw_words", ngrams_model, min_count, size, downsampling)
  except:
    model_name = "model.bin"
  model.save(model_name)

print("finish training w2v" +  str(datetime.now()))
print("training w2v took %i seconds (%i minutes)") % ((datetime.now() - start).seconds, (datetime.now() - start).seconds / 60)
# TODO: test more via https://www.kaggle.com/c/word2vec-nlp-tutorial/details/part-2-word-vectors
