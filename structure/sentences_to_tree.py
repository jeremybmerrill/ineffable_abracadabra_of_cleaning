import spacy
import markovify
from os.path import basename, join
from sys import argv
from os import makedirs


# goal is to parse a corpus to dependency trees, so I can train a model
# (maybe just a markov model) for children and postcedents
nlp = spacy.load('en_core_web_sm') # TODO use en_core_web_lg 

def jbfmtag(token, position=None):
  return token.dep_ + "_" + token.tag_ + ("_" + position if position else "")

def tag_children_line(token, parent="<BEGIN>"):
  children_tagged = [jbfmtag(child, "left") for child in token.lefts] + [jbfmtag(child, "right") for child in token.rights]
  return parent + "^" + jbfmtag(token) + "^" + "|".join(children_tagged)

def recursive_tag_children_line(token, parent="<BEGIN>"):
  return [tag_children_line(token, parent)] + [item for sublist in [recursive_tag_children_line(child, jbfmtag(token)) for child in token.children] for item in sublist]


def pos_parent_line(token, parent="<BEGIN>"):
  return parent + "|" + token.tag_ + "^" + token.text

def recursive_pos_parent_line(token, parent="<BEGIN>"):
  return [pos_parent_line(token, parent)] + [item for sublist in [recursive_pos_parent_line(child, token.text) for child in token.children] for item in sublist]

def tag_parent_line(token, parent="<BEGIN>"):
  return parent + "|" + jbfmtag(token) + "^" + token.text

def recursive_tag_parent_line(token, parent="<BEGIN>"):
  return [tag_parent_line(token, parent)] + [item for sublist in [recursive_tag_parent_line(child, token.text) for child in token.children] for item in sublist]


input_file = argv[1] if len(argv) >= 2 else "../sentences_100k.txt"
input_file_slug = basename(input_file).replace(".txt", '') 
folder = join("models", input_file_slug)
makedirs(folder, exist_ok=True)

with open(join(folder, input_file_slug + "_trees.txt"), 'w') as tree_output: 
  with open(join(folder, input_file_slug + "_tag_words.txt"), 'w') as tag_word_output: 
    with open(join(folder, input_file_slug + "_tags_only.txt"), 'w') as tags_output: 
      with open(join(folder, input_file_slug + "_fulltag_words.txt"), 'w') as fulltag_word_output: 
        with open(join(folder, input_file_slug + "_fulltags_only.txt"), 'w') as fulltags_output: 
          with open(input_file, 'r') as file:
            for line in file:
              line = line.replace("''", '').strip()
              # TODO: copy text cleaning stuff from another bit of this project
              if line == '':
                continue
              doc = nlp(line)

              # TODO: should be trigrams, e.g.
              # <BEGIN>,ROOT_VERB,nsubj_NOUN|aux_VERB|dobj_NOUN|punct_PUNCT|cc_CCONJ|conj_VERB

              root = next((token for token in doc if token.dep_ == "ROOT"), None)
              # print([item for sublist in recursive_tag_children_line(root) for item in sublist])
              for tree_line in recursive_tag_children_line(root):
                tree_output.write(tree_line + "\n" )

              # condition filling the words back in on something other than JUST the part of speech
              #      conditioning on previous word won't work (because we sometimes don't know the previous word)
              #      we can condition on the parent word
              for tree_line in recursive_pos_parent_line(root):
                tag_word_output.write(tree_line + "\n" )
                split = tree_line.split("^")
                tags_output.write(split[0].split("|")[1] + "^" + split[1] + "\n")

              # condition filling the words back in on something other than JUST the part of speech
              #      conditioning on previous word won't work (because we sometimes don't know the previous word)
              #      we can condition on the parent word
              for tree_line in recursive_tag_parent_line(root):
                fulltag_word_output.write(tree_line + "\n" )
                split = tree_line.split("^")
                fulltags_output.write(split[0].split("|")[1] + "^" + split[1] + "\n")
