# ai-polit
AI for politics. My toys to measure politics using NLP and AI techniques.


Testing
=======

To run all tests type (use -s for debug show of prints ;) ):

    pytest tests

To run specific test put path to the test file:

    pytest tests/t_preprocessors/test_text_cleaners.py

Scripts
=======

References to scripts. We use the following naming convention for scripts:

    {TOPIC_PREFIC}-{COMMAND_NAME}.py

Where TOPIC_PREFIX is one of the topics mentioned later in this document (check section *Topics*).


Topics
======

Each topic refers to specific NLP/AI/Analytic task. It can e.g. analytucs

The following topics are handled in this repository:
- *polittweets* - scripts to analyze political tweets
- *ttgen* - tweet generation algorithms
- *utils* - helper scripts and utilities

Topic: polittweets
==================

TBD

Topic: ttgen
============

TBD

Topic: utils
============

TBD


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
