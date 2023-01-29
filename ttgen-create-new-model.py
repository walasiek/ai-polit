#!/usr/bin/env python3

import argparse
import logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(asctime)s\t%(message)s')


from aipolit.ttgenerators.tweet_generator import TweetGenerator, list_all_generated_models, print_all_available_models
from aipolit.utils.text import read_tsv


def parse_arguments():
    """parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Creates new model from given list of tweets (TSV file). Input list must have two columns: tweet_id, text'
    )

    parser.add_argument(
        '--name', '-n',
        help='Model name (unique identifier to distinguish the models)')

    parser.add_argument(
        '--list',
        action='store_true',
        help='Show all available models and exit')

    parser.add_argument(
        '--input', '-i',
        help='Input TSV file to take tweets from')

    parser.add_argument(
        '--limit', '-l',
        type=int,
        help='Limit number of tweets to given number')

    parser.add_argument(
        '--epochs', '-e',
        type=int,
        default=1,
        help='Number of epochs to train.')

    args = parser.parse_args()

    return args


def main():
    args = parse_arguments()
    if args.list:
        print_all_available_models()
        return

    gen = TweetGenerator(args.name)

    if args.input is None:
        logging.info("IMPORTANT: You have not provided the input file. This will create 'empty' baseline model")
        gen.train_new_generator([])
    else:
        data = read_tsv(args.input)
        gen.train_new_generator(data, limit=args.limit, epochs=args.epochs)


main()
