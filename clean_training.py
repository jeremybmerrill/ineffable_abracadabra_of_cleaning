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

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
sentences_filename = "my_sentences_5.5M.txt
smaller_sentences_filename = "my_sentences_5.5M.txt"
start = datetime.now()
print("start training w2v " + str(start))

# an iterator, via http://rare-technologies.com/word2vec-tutorial/
class MySentences(object):
  def __init__(self, filename):
    self.filename = filename
    self.alpha_re = re.compile("^[a-zA-Z]+'?[a-zA-Z]*?$") # allow single apostrophes but not double apostrophes: note, this doesn't allow 'ere
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
      yield words

smaller_sentences = MySentences(smaller_sentences_filename) # a memory-friendly iterator



# this bigrams/trigrams bit is the same for both (but that the trigrams take `smaller_sentences` piped thru the bigrams model)
# N.B. -- the bigrams/trigrams finding works fine in 2.1.0 (etc.)
bigrams_threshold  = 15
trigrams_threshold = 10 # new york times is 11.1
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

  we_should_save_the_bigrams = False
  if we_should_save_the_bigrams:
    bigrams_so_far = set()
    with open(bigrams_model_name + ".txt", 'a') as f:
      for phrase, score in bigrams_model.export_phrases(smaller_sentences):
        if phrase not in bigrams_so_far:
          f.write("{}\t{}\n".format(phrase, score))
          bigrams_so_far.add(phrase)

smaller_sentences = MySentences(smaller_sentences_filename) # a memory-friendly iterator

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

  we_should_save_the_trigrams = False
  if we_should_save_the_trigrams:
    trigrams_so_far = set()
    with open(trigrams_model_name + ".txt", 'a') as f:
      for phrase, score in trigrams_model.export_phrases(bigrams_model[smaller_sentences]):
        if phrase not in trigrams_so_far:
          f.write("{}\t{}\n".format(phrase, score))
          trigrams_so_far.add(phrase)




sentences = MySentences(sentences_filename) # a memory-friendly iterator
ngrams_models = {
  "bigrams": lambda x: bigrams_model[x],
  "trigrams": lambda x: trigrams_model[bigrams_model[x]],
}

# my settings :)
ngrams_model = "trigrams"
min_count = 10 # was 10, also 50
size = 200
downsampling = 1e-3 # has variously been 1e-3 and 0
use_skipgrams = False


if True:
  model = gensim.models.Word2Vec(
                                  ngrams_models[ngrams_model](sentences) if ngrams_model else sentences, 
                                  workers=4, 
                                  min_count=min_count, 
                                  size=size, 
                                  sample=downsampling, 
                                  # sg=(1 if use_skipgrams else 0)
                                )

  model.init_sims(replace=True)
  try:
    model_name = "model_%s_%s_%s_min_count_%s_size_%s_downsampling_%s_%s.bin" % (sentences_filename.split("/")[-1].split(".")[0], "stemmed" if stemming else "raw_words", ngrams_model, min_count, size, downsampling, "sg" if use_skipgrams else "cbow")
  except:
    model_name = "model.bin"
  model.save(model_name)

  with open("most_recent_model_filename.txt", "w") as f:
    f.write(model_name)

    print(model.most_similar_cosmul(positive=['woman', 'king'], negative=['man']))

print("finish training w2v" +  str(datetime.now()))
print("training w2v took %i seconds (%i minutes)") % ((datetime.now() - start).seconds, (datetime.now() - start).seconds / 60)
# TODO: test more via https://www.kaggle.com/c/word2vec-nlp-tutorial/details/part-2-word-vectors