import re

# Source: https://stackoverflow.com/questions/33404752/removing-emojis-from-a-string-in-python
EMOJI_STRING = \
u"\U0001F600-\U0001F64F"  # emoticons
u"\U0001F300-\U0001F5FF"  # symbols & pictographs
u"\U0001F680-\U0001F6FF"  # transport & map symbols
u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
u"\U00002500-\U00002BEF"  # chinese char
u"\U00002702-\U000027B0"
u"\U00002702-\U000027B0"
u"\U000024C2-\U0001F251"
u"\U0001f926-\U0001f937"
u"\U00010000-\U0010ffff"
u"\u2640-\u2642"
u"\u2600-\u2B55"
u"\u200d"
u"\u23cf"
u"\u23e9"
u"\u231a"
u"\ufe0f"  # dingbats
u"\u3030"


EMOJI_REGEX = re.compile("[" + EMOJI_STRING + "]+", re.UNICODE)

URLS_REMOVE_REGEX = re.compile(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', re.MULTILINE | re.IGNORECASE)
EMAILS_REMOVE_REGEX = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')


def remove_emojis(data):
    """
    Removes all unicode emojis from the input text
    """
    return re.sub(EMOJI_REGEX, '', data)


# Source:
# https://stackoverflow.com/questions/11331982/how-to-remove-any-url-within-a-string-in-python
def remove_urls(text):
    text = re.sub(URLS_REMOVE_REGEX, '', text)
    return text


def remove_emails(text):
    text = re.sub(EMAILS_REMOVE_REGEX, "", text)
    return text
