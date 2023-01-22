"""
Tweet specific cleaning functions.
"""
import re

USERNAME_BEGIN_REGEX = re.compile(r"^(@[a-zA-Z0-9_]+ )+")


def remove_users_from_beg(text):
    """
    Removes usernames from tweets which are responses to other tweets.
    In such tweets, they start with all the users to which you respond.
    """
    text = re.sub(USERNAME_BEGIN_REGEX, "", text)
    return text
