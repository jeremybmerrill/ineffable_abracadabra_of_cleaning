from flask import Flask, Response
import json
from datetime import datetime
import gensim
from  gensim.models import Word2Vec
import sys
app = Flask(__name__)

cached_synonyms = {}
start = datetime.now()
print("start loading w2v " + str(start))
# w2v_model = Word2Vec.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)  # C binary format
# w2v_model = Word2Vec.load("en_1000_no_stem/en.model") # MemoryError :-(
try:
  model_filepath = sys.argv[1]
except KeyError:
  print("couldn't load " +sys.argv[1]+ "; using default model")
  model_filepath = 'model_sentences_raw_words_min_count_20_size_200_downsampling_0.001.bin'
print("using model from " + model_filepath)
w2v_model = Word2Vec.load(model_filepath)  # C binary format

print("finish loading w2v" +  str(datetime.now()))
print("loading w2v took  " + str((datetime.now() - start).seconds) + " seconds")

@app.route("/")
def hello():
    return json.dumps({"loaded": True})

@app.route("/similarize/<word>")
def similarize(word):
  try:
    try: 
      similar_words = cached_synonyms[word]
    except KeyError:
      similar_words = w2v_model.most_similar(positive=[word], negative=[], topn=20)
      cached_synonyms[word] = similar_words
  except KeyError: #word not in vocabulary
    similar_words = []

  return Response(json.dumps({'word': word, 'similar_words': similar_words}), mimetype='application/json')


@app.route("/themed/<word>/<theme>")
def themed(word, theme):
  try:
    similar_words = w2v_model.most_similar(positive=[(word, 1)] + [(theme, 0.75)], negative=[], topn=20)
  except KeyError: #word not in vocabulary
    similar_words = []
  return Response(json.dumps({'word': word, 'similar_words': similar_words}), mimetype='application/json')


if __name__ == "__main__":
    app.run()