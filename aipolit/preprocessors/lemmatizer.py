import spacy
import re
from aipolit.preprocessors.text_cleaners import EMOJI_STRING


PRESERVE_USERNAME_AND_HASH_REGEX = re.compile(r"([#@][\w_]+)\b")
PRESERVE_EMOJIS_REGEX = re.compile("([" + EMOJI_STRING + "]+)", re.UNICODE)
ALL_WHITESPACE_REGEX = re.compile(r"\s+")


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

        prep_text, cache = self.preserve_tokens(text, ignore_tt_usernames_and_hashes, ignore_emojis)

        doc = self.model(prep_text)
        for token in doc:
            # useful for debug
            # print(f"{token.text}|{token.pos_}|{token.dep_}|{token.lemma_}")

            # sometimes spacy returns two forms, hotfix
            orig_text = token.text
            if orig_text not in cache:
                lemma = token.lemma_.split(" ")[0]
                result.append(lemma)
            else:
                result.append(cache[orig_text])

        result_text = " ".join(result)
        return result_text

    def preserve_tokens(self, text, ignore_tt_usernames_and_hashes, ignore_emojis):
        cache = dict()

        def convert_func(matchobj):
            matched_orig = matchobj.group(1)
            match_id = f"LEMTOKEN_{len(cache)}"
            cache[match_id] = matched_orig
            return f" {match_id} "

        if ignore_tt_usernames_and_hashes or ignore_emojis:
            if ignore_tt_usernames_and_hashes:
                text = re.sub(PRESERVE_USERNAME_AND_HASH_REGEX, convert_func, text)
            if ignore_emojis:
                text = re.sub(PRESERVE_EMOJIS_REGEX, convert_func, text)

            text = re.sub(ALL_WHITESPACE_REGEX, " ", text)

        return text, cache
