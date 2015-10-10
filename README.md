The Ineffable Wizardry of Cleaning
==================================

ugh I can't remember the name of that cleaning up book
so let's make all the varieties
using word2vec to find synonyms of the words in the title

and other books too, obviously.

Natural Language?
-----------------


This uses word2vec, which is some existence-altering wizardry of its own. Tutorial and explanation below -- along with an interactive word2vec model: [http://radimrehurek.com/2014/02/word2vec-tutorial/](http://radimrehurek.com/2014/02/word2vec-tutorial/)

Some ideas I had and might be inexplicably contained in the source
------------------------------------------------------------------

## other options to increase fidelity to grammatical structure of input:
 - use an off-the-shelf stemmer and compare the removed portion (leaf?) in the word and synonym for levenshtein distance
 - pre-parse (by hand) into SimpleNLG structures
   then synonymize each word (using an API)
   then use NLG for conjugation
 - use a stemmer to train my own word2vec model

## wordnik has an awesome API, might help doing the stem -> conjugated form
http://developer.wordnik.com/docs.html#!/word/getRelatedWords_get_4

Future work
-----------
Themed book titles
"What if Harry Potter was about artists"
find mean of the input word (e.g. "chamber" or "secrets") 

this requires a list of titles ALONG WITH their topics so we can do something like:

 `Harry Potter and the Chamber of Secrets` minus `magic` plus `art` and see what we get.

Corpora
========

I'm using a corpus of sentences from The New York Times that I, unfortunately, can't share. Here are some alternatives that'd probably work fine:

- pretrained Google News model: https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit
- and from the University of Leipzig: [eng_news_2013_3M.tar.gz](http://corpora2.informatik.uni-leipzig.de/download.html)