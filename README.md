The Ineffable Wizardry of Cleaning
==================================

ugh I can't remember the name of that cleaning up book
so let's make all the varieties
using word2vec to find synonyms of the words in the title

and other books too, obviously.

see [@WhatToWriteNext](https://twitter.com/whattowritenext)

Natural Language?
-----------------

This uses word2vec, which is some existence-altering wizardry of its own. Tutorial and explanation below -- along with an interactive word2vec model: [http://radimrehurek.com/2014/02/word2vec-tutorial/](http://radimrehurek.com/2014/02/word2vec-tutorial/)

Some ideas I had and might be inexplicably contained in unreachable code in the source
--------------------------------------------------------------------------------------

## other options to increase fidelity to grammatical structure of input:
 - use an off-the-shelf stemmer and compare the removed portion (leaf?) in the word and synonym for levenshtein distance
 - pre-parse (by hand) into SimpleNLG structures
   then synonymize each word (using an API)
   then use NLG for conjugation
 - what about parsing with NLTK and combining the POS and the word ("Vtrash", "NNtrash"), and then using those as the input to the model? 

## wordnik has an awesome API, might help doing the stem -> conjugated form
http://developer.wordnik.com/docs.html#!/word/getRelatedWords_get_4

TODO: consider shrinking the window size to take advantage of more syntactic similarity:
> Effect of Window Size
> The size of the sliding window has a strong effect on the re-
> sulting vector similarities.  Larger windows tend to produce more topical similarities (i.e.
> \dog", \bark" and \leash" will be grouped together, as well as \walked", \run" and \walk-
> ing"), while smaller windows tend to produce more functional and syntactic similarities (i.e.
> \Poodle", \Pitbull", \Rottweiler", or \walking",\running",\approaching").
from http://u.cs.biu.ac.il/~yogo/nnlp.pdf, p23
"Positional windows" also useful (rather than training on "the", train on "the:-2" if the focus word occurs two words after "the" )

Future work
-----------
Themed book titles
"What if Harry Potter was about artists"

this requires a list of titles ALONG WITH their topics so we can do something like:

 `Harry Potter and the Chamber of Secrets` minus `magic` plus `art` and see what we get.

Corpora
========

I'm using a corpus of sentences from The New York Times that I, unfortunately, can't share. Here are some alternatives that'd probably work fine:

- pretrained Google News model: https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit
- and from the University of Leipzig: [eng_news_2013_3M.tar.gz](http://corpora2.informatik.uni-leipzig.de/download.html)
