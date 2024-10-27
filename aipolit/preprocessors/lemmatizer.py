import spacy
import re
from aipolit.preprocessors.tweet_cleaners import preserve_tokens, restore_tokens


class PLLemmatizer:
    """
    Converts each token from the input text
    to canonical form (lemma).

    Works only on Polish language.

    Allows to mark some "exceptions" which will not be processed.

    Remark: to use models you will need to first download them using
       python -m spacy download pl_core_news_sm
    (check enter.sh script)
    """

    # models available are: pl_core_news_sm, pl_core_news_md, pl_core_news_lg
    DEFAULT_MODEL = "pl_core_news_sm"

    INSTANCE = None

    def __init__(self):
        self.model = spacy.load(self.DEFAULT_MODEL)

    @classmethod
    def get_instance(cls):
        if cls.INSTANCE is None:
            cls.INSTANCE = PLLemmatizer()
        return cls.INSTANCE

    def process_text(self, text, ignore_tt_usernames_and_hashes=True, ignore_emojis=True):
        """
        Runs lemmatization. Returns text with all tokens transformed into canonical forms.

        Params:
        ignore_tt_usernames_and_hashes - will not process tokens which seems to be TT usernames or hashtags
        ignore_emojis - will ignore emojis (sometimes lemmatizer does some strange things with them due to unicode encoding)
        """
        result = []

        prep_text, cache = preserve_tokens(
            text,
            with_tt_usernames_and_hashes=ignore_tt_usernames_and_hashes,
            with_emojis=ignore_emojis,
            surround_spaces=True)

        doc = self.model(prep_text)
        for token in doc:
            # useful for debug
            # print(f"{token.text}|{token.pos_}|{token.dep_}|{token.lemma_}")

            # sometimes spacy returns two forms, hotfix
            orig_text = token.text
            if not orig_text.startswith('LEMTOKEN'):
                lemma = token.lemma_.split(" ")[0]
                result.append(lemma)
            else:
                result.append(restore_tokens(orig_text, cache))

        result_text = " ".join(result)
        return result_text
