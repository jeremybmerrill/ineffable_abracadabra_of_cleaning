import markovify
from collections import Iterable
from random import choice
from os.path import basename
from datetime import datetime
import pickle
from sys import argv
from os.path import basename, join

start = datetime.now()

input_file = argv[1] if len(argv) >= 2 else "../sentences_100k.txt"
input_file_slug = basename(input_file).replace(".txt", '') 
folder = join("models", input_file_slug)

import spacy
nlp = spacy.load('en_core_web_md')
def get_related(word):
  word = nlp(word)[0]
  filtered_words = [w for w in word.vocab if w.is_lower == word.is_lower and w.prob >= -15]
  similarity = sorted(filtered_words, key=lambda w: word.similarity(w), reverse=True)
  return [w.lower_ for w in similarity[1:10]]


def flatten(l):
    for el in l:
        if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el

markov_model = None
with open(join(folder, input_file_slug + "_markov.pickle"), 'rb') as f:
  markov_model = pickle.loads(f.read())
tags_parent_words_model = None
with open(join(folder, input_file_slug + "_fulltag_words.pickle"), 'rb') as f:
  tags_parent_words_model = pickle.loads(f.read())
tags_only_model = None
with open(join(folder, input_file_slug + "_fulltags_only.pickle"), 'rb') as f:
  tags_only_model = pickle.loads(f.read())

print("stuff loaded after {} secs".format((datetime.now() - start).seconds ))

def walk_recursive(a, b):
  child = markov_model.walk((a.replace("_left", '').replace("_right", ''), b.replace("_left", '').replace("_right", '')))
  # print(a,b,child)
  if not child:
    return [b]
  if child[0] == "":
    return [b]
  return [walk_recursive(b, grandchild) for grandchild in child[0].split("|") if "_left" in grandchild] + [b] + [walk_recursive(b, grandchild) for grandchild in child[0].split("|") if "_right" in grandchild]


START = ('<BEGIN>', 'ROOT_VBZ') # TODO is there a better option for randomly choosing a verb of any type, not just VBZ?
def make_sentence_structure():
    sentence = list(walk_recursive(*START))
    return sentence


def word_for(tag, parent_word):
  """Find a word with the given tag whose parent word is..."""
  # TODO: theme the word selection with a vector
  candidates = tags_parent_words_model.get(parent_word + "|" + tag, None)
  # print("finding a word with tag {} whose parent is {}".format(tag, parent_word))
  add = ""
  if not candidates: 
    for word in get_related(parent_word):
      candidates = tags_parent_words_model.get(word + "|" + tag, None)
      if candidates:
        # print("couldn't find one; finding a word related to {} with tag {}".format(word, tag))
        break
  if not candidates:
    # print("couldn't find one; finding a word with tag {}".format(tag))
    candidates = tags_only_model[tag]
    add = "*"
  word = choice(list(flatten([[cand] * cnt for cand, cnt in candidates.items()])))
  # print("found {}\n".format(word))
  return word # + add

def recursively_fill_in_structure(structure, parent_word):
  root_tag = next((token for token in structure if isinstance(token, str)), None)
  # TODO: condition the choice of (LEFTCHILD, PARENT) and (RIGHTCHILD, PARENT) and (LEFTSIBLING, RIGHTSIBLING)
  # TODO: what if we conditioned each word being chosen on its tag, its parent AND on its parent's left sibling?
  # TODO: what if we conditioned each word being chosen on its tag, its parent AND on the number of right-siblings it has? (to fix intransitive words getting objects)
  root_word = word_for(root_tag.replace("_left", '').replace("_right", ''), parent_word)
  return [root_word if isinstance(item, str) else recursively_fill_in_structure(item, root_word) for item in structure]  

def fill_in_structure(structure):
  return [word_for(tag.replace("_left", '').replace("_right", ''), parent_word) for tag in structure]

if __name__ == "__main__":
  for n in range(0, 10):
    struct = make_sentence_structure()
    # print(struct)
    sentence_tokens = list(flatten(recursively_fill_in_structure(struct, START[0])))
    # print(" ".join(sentence_tokens))
    import truecaser
    sentence = truecaser.truecase_tokens(sentence_tokens)
    print(' '.join(sentence).replace(" ,", ',').replace(" .", '.').replace(" 's", "'s").replace(" - ", '-') )
    print(" ")