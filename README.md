The Ineffable Wizardry of Cleaning
==================================

ugh I can't remember the name of that cleaning up book
so let's make all the varieties
using word2vec to find synonyms of the words in it
and probably being recursive so we end up with moar jokez

(here's the pretrained word2vec model: https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit)
see this interactive word2vec model: http://radimrehurek.com/2014/02/word2vec-tutorial/

## other options to increase fidelity to grammatical structure of input:
 - use an off-the-shelf stemmer and compare the removed portion (leaf?) in the word and synonym for levenshtein distance
 - pre-parse (by hand) into SimpleNLG structures
   then synonymize each word (using an API)
   then use NLG for conjugation
 - use a stemmer to train my own word2vec model

TODO: wordnik has a huge API, might help doing the stem -> conjugated form
http://developer.wordnik.com/docs.html#!/word/getRelatedWords_get_4

Corpora
========

en_1000_no_stem: I forget where it's from, but it gives a MemoryError
text8: I also forget where it's from
eng_news_2013_1M.tar.gz: http://corpora2.informatik.uni-leipzig.de/download.html
eng_news_2013_3M.tar.gz: http://corpora2.informatik.uni-leipzig.de/download.html