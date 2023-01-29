import logging
from collections import defaultdict
from aipolit.utils.text import read_tsv
from aipolit.ttdata.loader import load_tt_tsv_file
from aipolit.preprocessors.tweet_cleaners import remove_users_from_beg


class PolitTweetsData:
    """
    This class manages tweets from politics.
    """

    TT_USER_NAME_NONE = 'brak'

    def __init__(self):
        self.tt_user_name_to_metadata = dict()
        self.tweets_data = list()

    def load_data(self, input_tweets_fp, input_users_fp):
        user_data = read_tsv(input_users_fp)
        self._parse_user_data(user_data)
        tweets_data = load_tt_tsv_file(input_tweets_fp)
        self._parse_tweets_data(tweets_data)
        logging.info(
            "PolitTweetsData: loaded %i tweets for %i politicians",
            len(tweets_data),
            len(self.tt_user_name_to_metadata))

    def _parse_user_data(self, user_data):
        for entry in user_data:
            tt_user_name = entry['tt_user_name']
            if not tt_user_name:
                continue
            if tt_user_name == self.TT_USER_NAME_NONE:
                continue
            club = entry['club']
            party = entry['party']
            self.tt_user_name_to_metadata[tt_user_name] = {
                'club': club,
                'party': party,
            }

    def _parse_tweets_data(self, raw_tweets_data):
        for entry in raw_tweets_data:
            if entry['username'] in self.tt_user_name_to_metadata:

                raw_text = entry['text']
                text = remove_users_from_beg(raw_text)
                entry['text'] = text
                entry['raw_text'] = raw_text
                self.tweets_data.append(entry)
