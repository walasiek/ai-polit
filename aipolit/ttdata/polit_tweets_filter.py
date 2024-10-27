import logging
from aipolit.utils.text import save_tsv


class PolitTweetsFilter:
    """
    Processes tweets in PolitTweetsData and creates only tweets which meet given critera.
    Can dump list to TSV file.
    """

    def __init__(self, polit_tweets_data):
        self.polit_tweets_data = polit_tweets_data

        # filters

        # Min character length (excluding sequence of user names in TT responses)
        self.min_char_length = None
        # Take only tweets from given club
        self.fixed_club = None

    def dump_to_file(self, fp):
        header = self.polit_tweets_data.tweets_data[0].keys()
        filtered_data = self.filter_data()
        logging.info("PolitTweetsFilter: after filtering we got %i out of %i tweets", len(filtered_data), len(self.polit_tweets_data.tweets_data))
        save_tsv(fp, filtered_data, header)

    def filter_data(self):
        filtered_data = list()

        for e in self.polit_tweets_data.tweets_data:
            if self.should_be_removed(e):
                continue

            filtered_data.append(e)

        return filtered_data

    def should_be_removed(self, e):
        if self.min_char_length:
            if len(e['text']) < self.min_char_length:
                return True

        if self.fixed_club:
            username = e['username']
            club = self.polit_tweets_data.tt_user_name_to_metadata[username]['club']
            if club != self.fixed_club:
                return True

        return False
