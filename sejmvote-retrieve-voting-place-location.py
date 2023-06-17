#!/usr/bin/env python3

import argparse
import logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s\t%(message)s')

from aipolit.sejmvote.voting_place_locator import VotingPlaceLocator
from aipolit.sejmvote.voting_factory import create_voting_place_data
from aipolit.sejmvote.globals import AVAILABLE_ELECTIONS_IDS


def parse_arguments():
    """parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Tries to load langitude and latitude for voting place'
    )

    parser.add_argument(
        '--okreg', '-o',
        help='Limit query only to data from the given sejm okreg')

    parser.add_argument(
        '--city', '-c',
        help='Limit query only to data from the given city')

    parser.add_argument(
        '--limit', '-l',
        type=int,
        help='Limit number of voting places processed')

    parser.add_argument(
        '--elections-id', '-e',
        choices=AVAILABLE_ELECTIONS_IDS,
        required=True,
        help='Elections IDS to be quiried')

    args = parser.parse_args()

    return args


def process_data(data, obwod_id_to_process, elections_id):
    voting_place_locator = VotingPlaceLocator()

    found_location = 0
    for i, obwod_id in enumerate(obwod_id_to_process):
        logging.info("Query location %s (%i out of %i)", obwod_id, i + 1, len(obwod_id_to_process))
        entry = data.get_voting_place_by_id(obwod_id)
        location_result = voting_place_locator.query(entry)
        if location_result[0] is not None:
            found_location += 1

        data.location_data.add_location_data(obwod_id, location_result[0], location_result[1])

    logging.info("We found %i locations out of %i", found_location, len(obwod_id_to_process))
    data.location_data.save_data()


def create_obwod_ids_to_process(data, args):
    result = []
    for entry in data.voting_place_data:
        if args.city:
            if entry['city'] != args.city:
                continue
        if args.okreg:
            # warning for compatibility with sejm2019, prez2020, etc.!!!
            if entry[data.okreg_key_name] != args.okreg:
                continue

        if args.limit:
            if len(result) >= args.limit:
                break
        # TODO exclude already queried
        obwod_id = entry['obwod_id']
        if obwod_id in data.location_data.obwod_id_to_location_data:
            continue

        result.append(obwod_id)
    logging.info("We have %i obwod to query", len(result))
    return result

def main():
    args = parse_arguments()

    data = create_voting_place_data(args.elections_id)
    obwod_id_to_process = create_obwod_ids_to_process(data, args)
    process_data(data, obwod_id_to_process, args.elections_id)

main()
