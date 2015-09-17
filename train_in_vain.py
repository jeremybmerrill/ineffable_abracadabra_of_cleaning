from nltk.stem.porter import *
from nltk.tokenize import word_tokenize
import gensim, logging
from datetime import datetime
import gensim
import cython 

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
sentences_filename = "eng_news_2013_3M/eng_news_2013_3M-sentences.txt"


start = datetime.now()
print("start training w2v " + str(start))

# an iterator, via http://rare-technologies.com/word2vec-tutorial/
class MySentences(object):
  def __init__(self, filename):
    self.filename = filename
    self.stemmer = PorterStemmer()
    # TODO: use http://www.nltk.org/howto/stem.html

  def __iter__(self):
    for line in open(self.filename):
      # TODO find a better way to distinguish sentence-initial caps from proper noun

      # sentences come like this:
      # 80  10:11 p.m., an unwanted person was reported on College Avenue.
      # 81  10:13 a.m., a report of shoplifting was investigated at Maine Smoke Shop on College Avenue.
      # 82  10:14: The proportion of A-levels awarded at least an A grade has fallen for the second year in a row.
      # 141529  But the debt ceiling may end up being the larger inflection point, especially as Obama staked out a hard-lined position against negotiating over that vote.

      sentence = line.decode("UTF8").split("\t", 1)[1]
      words = [word.lower() for word in word_tokenize(sentence) if word.isalpha() ]
      stems = [self.stemmer.stem(word) for word in words]
      if "deathli" in stems:
        print(stems)
      yield stems

sentences = MySentences(sentences_filename) # a memory-friendly iterator
min_count = 10
size = 200
downsampling = 1e-3
model = gensim.models.Word2Vec(sentences, workers=4, min_count=min_count, size=size, sample=downsampling)
model.init_sims(replace=True)
try:
  model_name = "model_%s_stemmed_min_count_%s_size_%s_downsampling_%s.bin" % (sentences_filename.split("/")[-1].split(".")[0], min_count, size, downsampling)
except:
  model_name = "model.bin"
model.save(model_name)

print("finish training w2v" +  str(datetime.now()))
print("training w2v took %i seconds (%i minutes)") % ((datetime.now() - start).seconds, (datetime.now() - start).seconds / 60)
# TODO: test more via https://www.kaggle.com/c/word2vec-nlp-tutorial/details/part-2-word-vectors
