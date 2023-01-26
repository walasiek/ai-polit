"""
Tweet specific cleaning functions.
"""
import re
import emoji


USERNAME_BEGIN_REGEX = re.compile(r"^(@[a-zA-Z0-9_]+ )+")
PRESERVE_USERNAME_AND_HASH_REGEX = re.compile(r"([#@][\w_]+)\b")
ALL_WHITESPACE_REGEX = re.compile(r"\s+")


def remove_users_from_beg(text):
    """
    Removes usernames from tweets which are responses to other tweets.
    In such tweets, they start with all the users to which you respond.
    """
    text = re.sub(USERNAME_BEGIN_REGEX, "", text)
    return text


def preserve_tokens(text, with_tt_usernames_and_hashes=True, with_emojis=True):
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

    def convert_emoji_func(chars, data_dict):
        match_id = f"LEMTOKEN{len(cache)}"

        cache[match_id] = chars
        return f"{match_id}"

    if with_tt_usernames_and_hashes or with_emojis:
        if with_tt_usernames_and_hashes:
            text = re.sub(PRESERVE_USERNAME_AND_HASH_REGEX, convert_func, text)
        if with_emojis:
            text = emoji.replace_emoji(text, replace=convert_emoji_func)

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
