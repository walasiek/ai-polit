#!/usr/bin/env python3

import argparse
import logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(asctime)s\t%(message)s')


import fileinput
from aipolit.ttgenerators.tweet_generator import TweetGenerator, list_all_generated_models, print_all_available_models
from aipolit.utils.text import read_txt_list


def parse_arguments():
    """parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Generates tweets using given model. If prompts not given as arguments then takes them from STDIN'
    )

    parser.add_argument(
        '--name', '-n',
        choices=list_all_generated_models(),
        help='Model name (unique identifier to distinguish the models)')

    parser.add_argument(
        '--count', '-k',
        type=int,
        default=10,
        help='Number of tweets to be generated from one prompt')

    parser.add_argument(
        '--query-file', '-qf',
        help='If set then generates tweets using prompts from given file (each line is considered to be one prompt)')

    parser.add_argument(
        '--save-filename', '-s',
        help='If set then saves generated prompts to model dir with given filename.')

    parser.add_argument(
        '--with-sentiment', '-ws',
        action='store_true',
        help='If set then computes sentiment mode')

    parser.add_argument(
        '--list',
        action='store_true',
        help='Show all available models and exit')

    args = parser.parse_args()

    return args


def _read_from_stdin(args, gen):
    while True:
        line = input("Prompt> ")
        line = line.rstrip()
        generated = gen.generate_tweets(line, num_return_sequences=args.count)
        for i, g in enumerate(generated):
            print(f"{i + 1}) {g}\n")

        print("\n")


def _process_query_file(args, gen):
    prompts = read_txt_list(args.query_file)
    all_generated = gen.generate_tweets_for_list(
        prompts,
        save_to_filename=args.save_filename,
        with_sentiment=args.with_sentiment,
        num_return_sequences=args.count)

    prev_prompt = None
    for entry in all_generated:
        prompt = entry[1]
        if prev_prompt is None or prev_prompt != prompt:
            print("")
            print(f"Prompt> {prompt}")
            prev_prompt = prompt

        print(entry[2])
        sentiment = entry[3]
        if sentiment is not None:
            print("Sentiment:", sentiment)
        print("")


def main():
    args = parse_arguments()
    if args.list:
        print_all_available_models()
        return

    gen = TweetGenerator(args.name)
    gen.load_generator()

    if args.with_sentiment:
        gen.load_sentiment_model()

    if args.query_file:
        _process_query_file(args, gen)
    else:
        _read_from_stdin(args, gen)


main()
