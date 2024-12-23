#!/usr/bin/env python3

import argparse
from argparse import RawTextHelpFormatter
import logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(asctime)s\t%(message)s')


from aipolit.transcript.transcript_query import TranscriptQuery, AVAILABLE_TO_DUMP


def parse_arguments():
    """parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="""Allows to dump specific part of Transcript XMLs to TXT dump for easier data processing.

Useful use cases:


    - Ranking of who interrupts the most:
    ./bin/aipolit-transcript-query.py -w utt_interrupt_by | sort |uniq -c |sort -nr|less

    - Ranking of the most common interruptions
    ./bin/aipolit-transcript-query.py -w utt_interrupt | sort |uniq -c |sort -nr|less

    - Ranking of the most common reactions
    ./bin/aipolit-transcript-query.py -w utt_reaction | sort |uniq -c |sort -nr|less

    - Ranking who speaks the most
    ./bin/aipolit-transcript-query.py -w speech_speaker | sort |uniq -c |sort -nr|less

    - Raw speakers of the given political affiliations
    ./bin/aipolit-transcript-query.py -w speech_speaker -sa KO

    - Utterances only from speakers of multiple political affiliations
    ./bin/aipolit-transcript-query.py -w utt_norm -sa KO PiS
        """,
        formatter_class=RawTextHelpFormatter
    )

    parser.add_argument(
        '--fixed-dir', '-fd',
        help='Fixed directory to load transcripts, overrides defaults (useful for tests)')

    parser.add_argument(
        '--output', '-o',
        help='If defined, then saves dump into given file.')

    parser.add_argument(
        '--what', '-w',
        type=str,
        nargs='+',
        help=f"What should be dumped. Any combination of: [{', '.join(sorted(AVAILABLE_TO_DUMP))}]")

    parser.add_argument(
        '--speaker_affiliation', '-sa',
        type=str,
        nargs="+",
        help='If defined, then processes only speakers with one of given affiliations (separate by space).')

    args = parser.parse_args()

    return args


def run_query(transcript_query, args, filehandle=None):
    transcript_query.query(
        args.what,
        to_filehandle=filehandle,
        restrict_speaker_affiliations=args.speaker_affiliation,
    )


def main():
    args = parse_arguments()

    transcript_query = TranscriptQuery(fixed_transcript_dir=args.fixed_dir)
    logging.info("Loaded %i transcript files to query.", transcript_query.count_transcripts())

    if args.output:
        logging.info("Saving dump to file: %s", args.output)
        with open(args.output, "w") as f:
            run_query(transcript_query, args, f)
    else:
        run_query(transcript_query, args)


main()
