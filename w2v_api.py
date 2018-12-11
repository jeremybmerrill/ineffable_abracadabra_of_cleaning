from flask import Flask, Response
import json
from datetime import datetime
import gensim
from  gensim.models import Word2Vec, Phrases
import sys
import os
from collections import OrderedDict

w2v_api = Flask(__name__)
w2v_api.config['PROPAGATE_EXCEPTIONS'] = True

cached_synonyms = {}
start = datetime.now()
print("start loading w2v " + str(start))
# w2v_model = Word2Vec.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)  # C binary format
# w2v_model = Word2Vec.load("en_1000_no_stem/en.model") # MemoryError :-(
try:
  model_filepath = sys.argv[1]
  if model_filepath in ["-d", "--daemonize"]:
    raise IndexError
except IndexError:
  try:
    with open("most_recent_model_filename.txt", "r") as f:
      model_filepath = f.read().strip()
  except IOError: 
    print("using default model")
    current_dir = os.path.dirname(__file__)
    model_filepath = os.path.join(current_dir, 'model_sentences_raw_words_trigrams_min_count_50_size_200_downsampling_0.001.bin')
w2v_model = Word2Vec.load(model_filepath) #, encoding='latin1')  # C binary format
print("using model from " + model_filepath)

bigrams_model_name =   'bigrams_model_nyt_sentences_5.5M_15_10000000.bin'
trigrams_model_name = "trigrams_model_nyt_sentences_5.5M_10_10000000.bin"
ngrams_models = {
  "bigrams": bigrams_model_name,
  "trigrams": trigrams_model_name
}
which_ngrams_model = "trigrams"

if which_ngrams_model:
  ngrams_model = Phrases.load(ngrams_models[which_ngrams_model])


print("finish loading w2v" +  str(datetime.now()))
print("loading w2v took  " + str((datetime.now() - start).seconds) + " seconds")

@w2v_api.route("/")
def hello():
    return json.dumps({"loaded": True})

@w2v_api.route("/similarize/<word>")
def similarize(word):
  try:
    try: 
      similar_words = cached_synonyms[word]
    except KeyError:
      similar_words = w2v_model.wv.most_similar(positive=[word], negative=[], topn=5)
      cached_synonyms[word] = similar_words
  except KeyError: #word not in vocabulary
    similar_words = []

  return Response(json.dumps({'word': word, 'similar_words': similar_words}), mimetype='application/json')

@w2v_api.route("/phrases/<sentence>")
def group_ngrams(sentence):
  split_sentence = sentence.split(",")
  return Response(json.dumps({'grouped': ngrams_model[split_sentence] if which_ngrams_model else split_sentence, 'input': split_sentence}), mimetype='application/json')


@w2v_api.route("/themed/<word>/<theme>")
def themed(word, theme):
  try:
    similar_words = w2v_model.wv.most_similar(positive=[(word, 1)] + [(theme, 1)], negative=[], topn=50)
  except KeyError: #word not in vocabulary
    similar_words = []
  return Response(json.dumps({'word': word, 'similar_words': similar_words}), mimetype='application/json')

@w2v_api.route("/analogy_cosmul/<word>/<isto>/<as_>")
def analogy_cosmul(word, isto, as_):
  try:
    similar_words = w2v_model.wv.most_similar_cosmul(positive=[as_, isto], negative=[word], topn=5)
    print("%s : %s :: %s : %s" % (word, isto, as_, similar_words[0][0]))
  except KeyError: #word not in vocabulary
    similar_words = []
  return Response(json.dumps(OrderedDict([
     ('analogy', "{} is to {} as {} is to __________".format(word.upper(), isto.upper(), as_.upper())),
     ('similar_words', similar_words)
    ])
  ), mimetype='application/json')

@w2v_api.route("/analogy/<word>/<isto>/<as_>")
def analogy(word, isto, as_):
  try:
    similar_words = w2v_model.wv.most_similar(positive=[as_, isto], negative=[word], topn=5)
    print("%s : %s :: %s : %s" % (word, isto, as_, similar_words[0][0]))
  except KeyError: #word not in vocabulary
    similar_words = []
  return Response(json.dumps(OrderedDict([
     ('analogy', "{} is to {} as {} is to __________".format(word.upper(), isto.upper(), as_.upper())),
     ('similar_words', similar_words)
    ])
  ), mimetype='application/json')
# new_jersey isto bruce_springsteen as long_island isto
# bruce_springsteen - new_jersey + long_island
# 
# >>> trained_model.most_similar_cosmul(positive=['baghdad', 'england'], negative=['london'])
# london : england :: baghdad : ________
# word   : isto    :: as_ : _______
# most_similar_cosmul(positive=['baghdad', 'england'], negative=['london'])

if __name__ == "__main__":
    w2v_api.run()