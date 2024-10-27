import re
import emoji


URLS_REMOVE_REGEX = re.compile(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', re.MULTILINE | re.IGNORECASE)
EMAILS_REMOVE_REGEX = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')


def remove_emojis(data):
    """
    Removes all unicode emojis from the input text
    """
    return emoji.replace_emoji(data, replace='')


# Source:
# https://stackoverflow.com/questions/11331982/how-to-remove-any-url-within-a-string-in-python
def remove_urls(text):
    text = re.sub(URLS_REMOVE_REGEX, '', text)
    return text


def remove_emails(text):
    text = re.sub(EMAILS_REMOVE_REGEX, "", text)
    return text


def remove_non_alphanumeric(text):
    text = re.sub(r"[^\w]+", " ", text)

    text = re.sub(r"^\s+", "", text)
    text = re.sub(r"\s+$", "", text)
    text = re.sub(r"\s+", " ", text)
    return text
