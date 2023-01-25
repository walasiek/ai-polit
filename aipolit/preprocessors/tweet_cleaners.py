"""
Tweet specific cleaning functions.
"""
import re
from aipolit.preprocessors.text_cleaners import EMOJI_STRING

USERNAME_BEGIN_REGEX = re.compile(r"^(@[a-zA-Z0-9_]+ )+")
PRESERVE_USERNAME_AND_HASH_REGEX = re.compile(r"([#@][\w_]+)\b")
PRESERVE_EMOJIS_REGEX = re.compile("([" + EMOJI_STRING + "]+)", re.UNICODE)
ALL_WHITESPACE_REGEX = re.compile(r"\s+")


def remove_users_from_beg(text):
    """
    Removes usernames from tweets which are responses to other tweets.
    In such tweets, they start with all the users to which you respond.
    """
    text = re.sub(USERNAME_BEGIN_REGEX, "", text)
    return text


def preserve_tokens(text, with_tt_usernames_and_hashes, with_emojis):
    """
    Returns text with some entities replaced with keywords.
    Also returns mapping: keyword => original value

    Useful to keep some special tokens untouched.

    Example:
        Here is #hashTag => Here is LEMTOKEN1
    """
    cache = dict()

    def convert_func(matchobj):
        matched_orig = matchobj.group(1)
        match_id = f"LEMTOKEN{len(cache)}"

        cache[match_id] = matched_orig
        return f"{match_id}"

    if with_tt_usernames_and_hashes or with_emojis:
        if with_tt_usernames_and_hashes:
            text = re.sub(PRESERVE_USERNAME_AND_HASH_REGEX, convert_func, text)
        if with_emojis:
            text = re.sub(PRESERVE_EMOJIS_REGEX, convert_func, text)

        text = re.sub(ALL_WHITESPACE_REGEX, " ", text)
        text = re.sub(r"^\s+", "", text)
        text = re.sub(r"\s+$", "", text)

    return text, cache


def restore_tokens(text, cache):
    tokens = re.split(r"(LEMTOKEN\d+)", text)
    result = []
    for tok in tokens:
        result.append(cache.get(tok, tok))
    return "".join(result)
