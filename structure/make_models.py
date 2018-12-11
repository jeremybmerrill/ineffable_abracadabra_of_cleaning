import markovify
from os.path import basename, join
from os import makedirs
import pickle
from sys import argv
from datetime import datetime
start = datetime.now()

input_file = argv[1] if len(argv) >= 2 else "../sentences_100k.txt"
input_file_slug = basename(input_file).replace(".txt", '') 
folder = join("models", input_file_slug)

makedirs(folder, exist_ok=True)

markov_model = None
with open(join(folder, input_file_slug + "_trees.txt")) as f:
  text = f.read()
  corpus = [line.split("^") for line in text.split("\n")]
  markov_model = markovify.Chain(corpus, 2)
with open(join(folder, input_file_slug + "_markov.pickle") , 'wb') as f:
  pickle.dump(markov_model, f)

tags_parent_words_model = {}
with open(join(folder, input_file_slug + "_tag_words.txt")) as f:
  text = f.read()
  tag_word_pairs = [line.split("^", 1) for line in text.split("\n") if "^" in line]
  for tag, word in tag_word_pairs:
    if not tags_parent_words_model.get(tag):
      tags_parent_words_model[tag] = {}
    tags_parent_words_model[tag][word] =  tags_parent_words_model[tag].get(word, 0) + 1
with open(join(folder, input_file_slug + "_tag_words.pickle") , 'wb') as f:
  pickle.dump(tags_parent_words_model, f)

tags_only_model = {}
with open(join(folder, input_file_slug + "_tags_only.txt")) as f:
  text = f.read()
  tag_word_pairs = [line.split("^", 1) for line in text.split("\n") if "^" in line]
  for tag, word in tag_word_pairs:
    if not tags_only_model.get(tag):
      tags_only_model[tag] = {}
    tags_only_model[tag][word] =  tags_only_model[tag].get(word, 0) + 1
with open(join(folder, input_file_slug + "_tags_only.pickle") , 'wb') as f:
  pickle.dump(tags_only_model, f)


tags_parent_words_model = {}
with open(join(folder, input_file_slug + "_fulltag_words.txt")) as f:
  text = f.read()
  tag_word_pairs = [line.split("^", 1) for line in text.split("\n") if "^" in line]
  for tag, word in tag_word_pairs:
    if not tags_parent_words_model.get(tag):
      tags_parent_words_model[tag] = {}
    tags_parent_words_model[tag][word] =  tags_parent_words_model[tag].get(word, 0) + 1
with open(join(folder, input_file_slug + "_fulltag_words.pickle") , 'wb') as f:
  pickle.dump(tags_parent_words_model, f)

tags_only_model = {}
with open(join(folder, input_file_slug + "_fulltags_only.txt")) as f:
  text = f.read()
  tag_word_pairs = [line.split("^", 1) for line in text.split("\n") if "^" in line]
  for tag, word in tag_word_pairs:
    if not tags_only_model.get(tag):
      tags_only_model[tag] = {}
    tags_only_model[tag][word] =  tags_only_model[tag].get(word, 0) + 1
with open(join(folder, input_file_slug + "_fulltags_only.pickle") , 'wb') as f:
  pickle.dump(tags_only_model, f)

print("stuff written after {} secs".format((datetime.now() - start).seconds ))
