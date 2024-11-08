#!/usr/bin/env python3

import argparse
import logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(asctime)s\t%(message)s')


from aipolit.ttdata.polit_tweets_data import PolitTweetsData
from aipolit.ttdata.polit_tweets_filter import PolitTweetsFilter


def parse_arguments():
    """parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Reads political tweets and info about authors to fiter only those tweets which meets given criteria'
    )

    parser.add_argument(
        '--input-tweets', '-it',
        required=True,
        help='Input TSV file to take tweets')

    parser.add_argument(
        '--input-users', '-iu',
        required=True,
        help='Input TSV file to take user data')

    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Filepath to output TSV file')

    parser.add_argument(
        '--limit', '-l',
        type=int,
        help='Limit number of tweets to given number')

    parser.add_argument(
        '--min-char-length', '-mcl',
        type=int,
        help='Minimum number of chars for the tweet')

    parser.add_argument(
        '--fixed-club', '-fc',
        help='Take only tweets from this club')

    args = parser.parse_args()

    return args


def main():
    args = parse_arguments()

    data = PolitTweetsData()
    data.load_data(args.input_tweets, args.input_users)
    ttfilter = PolitTweetsFilter(data)

    ttfilter.min_char_length = args.min_char_length
    ttfilter.fixed_club = args.fixed_club

    ttfilter.dump_to_file(args.output)


main()
