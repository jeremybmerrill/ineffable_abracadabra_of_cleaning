# Ineffable Wizardry of (Cleaning / Structure

This project aims to generate more coherent ebooks-style sentences by modeling structures (i.e. parse trees), then filling in the words for each node in the parse tree with a word that has received the same tag as that node (potentially conditioned on other things too!)

`python sentences_to_tree.py corpus.txt` generates a variety of text files for model training from a file called `corpus.txt`, which must be a newline-separated file of sentences; the eventual model and its intermediate files are stored in `models/` at a subpath matching the basename of the corpus file, in this case, `models/corpus/`. `python make_models.py corpus.txt` generates the eventual models. `python markov.py corpus.txt` generates some sentences from those models.

If your input text is not a newline-separated file of sentences, `python text_to_clean_sentences.py corpus.txt` creates `corpus_sentences.txt` with all the sentences on their own lines, in a format appropriate for the input to `sentences_to_tree.py`. 

Current model: 
Only generates the parse trees from short-ish sentences, to avoid run-ons that are usually incoherent. `grep -E "^.{15,140}$" corpus_100k.txt > corpus.txt`


## TODO:
problem:
  intransitive nouns getting direct objects
  subject-verb agreement ("he wield")
  (weird relationships between verbs and prepostion
  "to one's" as a whole PP (without something to be belonged there...)
solution?:
  by conditioning the _word_ choice maybe on the sibling tag as well as the parent tag? 
  (if the parent is a verb, check if the subject ever appears as the child of the verb?)
  condition the choice of (LEFTCHILD, PARENT) and (RIGHTCHILD, PARENT) and (LEFTSIBLING, RIGHTSIBLING)
  what if we conditioned each word being chosen on its tag, its parent AND on its parent's left sibling?
  what if we conditioned each word being chosen on its tag, its parent AND on the number of right-siblings its parent has
bad sentences:
  "each is the open open discussion, said year ' daniele." <-- shouldn't do that with apostrophes.
  when they was to laugh, buck evans estimated plays : of the san vegas for partner.
  in *a miles* on foot of being a suit resiliency after an dinner to go mr he is little.
  we was both announcer and the big coach at state.


theme word choices with spacy's sense2vec
  (if I have a sentence theme ALREADY and a target theme, can calculate vector distance between the themes, apply that to the source word)

Hallmark: what do i get from using the short-sentence structure model and a tag to themed words word-filler-inner?
(So far, I'm using sentences_short/markov.pickle and the rest all from hallmark. That's not working great because there are fulltags called for that don't exist in the hallmark dataset.)