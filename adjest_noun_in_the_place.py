from gensim.models import Word2Vec
from random import choice
import json

# model trained with train_in_vain.py
MODEL = Word2Vec.load("model_sentences_tagged_raw_words_trigrams_min_count_10_size_200_downsampling_0.001_cbow.bin")

NOUNS = [
          "flower", "fish", "ball", "cheese",
          "light", "crayon", "bunny", "pizza", 
          "cookie", "lamp", "poem", "avocado",
          "ship", "airplane", "mountain", "bike",
          "coffee", "beer", "wine", "steak",
          "cat", "brisket", "rock", "car"
        ]

# not the Xest Y in the Z bot (use word2vec to find the nearest adjective to a noun, find the nearest container noun from a list of "in the NP" phrases) [pos-tagged NYT corpus is wrong, I think because of hyphenated nouns not getting tagged) 

# file generated with 
# grep -Eo "in_IN the_DT [a-z]+_NNS?" sentences_5.5M_tagged.txt > in_the_NN.txt
# then grouping and counting.
DESTINATIONS = json.load(open("in_the_NN_counts.json", 'r'))

VOWELS = ("a", "e", 'i', 'o', 'u')
CONSONANTS = ("b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", 'q', "r", "s", "t", "v", "w", "x", "y", "z")
PRONS = ("he's", "she's", "they're")
def superlativize(adj):
  ll = adj[-1]
  pl = adj[-2]
  if pl in VOWELS and ll in ("d", "t" ):
    return adj + ll + "est"
  elif(ll == "y"): # spicy, toasty, creamy
    return adj[:-1] + "i" + "est"
  elif(ll == "e"): # nice
    return adj + "st"
  else:
    return adj + "est"

def generate_insult(noun=None):
  #                              tool : shed :: NOUN : ???
  # analogy    MODEL.wv.most_similar_cosmul(positive=["shed", noun], negative=["tool"], topn=5)
  # best       MODEL.most_similar_cosmul([noun + "_nn", "best_jjs"], topn=200)
  if not noun:
    noun = choice(NOUNS)
  adjs = [word for word, sim in MODEL.most_similar_cosmul(positive=["fast_jj", noun + "_nn"], negative=["car_nn"], topn=200) if "jj" in word and word.split("_")[0][-2:] != "ed" and word.split("_")[0][-3:] != "ing" and word not in noun and noun not in word][0:10]
  places = [word.split("_")[0] for word, sim in MODEL.most_similar_cosmul(positive=["library_nn", noun + "_nn"], negative=["book_nn"], topn=200) if word[-2:] == "nn" and DESTINATIONS.get(word.split("_")[0], 0) > 10 and word not in noun and noun not in word][0:10]
  adjs = [(adj.split("_")[0] if 'jjs' in adj else superlativize(adj.split("_")[0])) for adj in adjs if adj not in ["best_jjs", "nice_jj", "nicest_jj"]]
  places = [place for place in places if place not in (noun, "location", "container", "place")]

  return "not{} the {} {} in the {}{}".format(
    choice(["", "", "", "", " exactly"]), 
    choice(adjs), 
    noun, 
    choice(places), 
    choice(["","","","", ", if you know what I mean"])
    )
if __name__ == "__main__":
  for noun in NOUNS: 
    print(choice(PRONS) + " " + generate_insult(noun))
