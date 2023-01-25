# ai-polit
AI for politics. My toys to measure politics using NLP and AI techniques.


Testing
=======

To run all tests type (use -s for debug show of prints ;) ):

    pytest tests

To run specific test put path to the test file:

    pytest tests/t_preprocessors/test_text_cleaners.py

Notebooks
=========

References to notebooks. In most cases notebooks are draft pieces of code.
Some of them might be published.

001_characteristic_words_for_tt_descriptions (unpublished)
----------------------------------------------------------

First experiment on MP's account description and algorithm to find characteristic words.
Two approaches:

1. Random Forest + feature weights
2. LIME explanation (also on Random Forest)

A playground for more challanging tasks ;)


002_experiment_with_tweet_identification_for_sejm_parties (unpublished)
-----------------------------------------------------------------------

Very similar to previous notebook, but the classification task is different - this time we collected
tweets for all MPs from the given year, and try to identify who wrote the tweet.

Then the classifier is used to identify characteristic words.
