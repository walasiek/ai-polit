#!/usr/bin/env python3

import argparse
import logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(asctime)s\t%(message)s')


from aipolit.transcript.transcript_query import TranscriptQuery, AVAILABLE_TO_DUMP


def parse_arguments():
    """parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Checks transcripts and tries to assign affiliations to all speakers occuring.'
    )

    parser.add_argument(
        '--fixed-dir', '-fd',
        help='Fixed directory to load transcripts, overrides defaults (useful for tests)')

    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Saves dump into given TSV file.')

    args = parser.parse_args()

    return args


def run_query(transcript_query, args, filehandle=None):
    transcript_query.assign_speakers_to_affiliations(
        to_filehandle=filehandle
    )


def main():
    args = parse_arguments()

    transcript_query = TranscriptQuery(fixed_transcript_dir=args.fixed_dir)
    logging.info("Loaded %i transcript files to query.", transcript_query.count_transcripts())

    with open(args.output, "w") as f:

        f.write("\t".join(['speaker_name', 'affiliations', 'canon_name']))
        f.write("\n")

        speaker_name_to_entry = transcript_query.assign_speakers_to_affiliations()

        def sort_entries(k_v):
            entry = k_v[1]
            canon = entry['canon_name']
            if canon is None:
                canon = ''
            return (canon, entry['speaker_name'])

        with_aff_count = 0
        with_multi_aff_count = 0
        without_aff_count = 0
        for name, entry in sorted(speaker_name_to_entry.items(), key=sort_entries):
            f.write(name)
            f.write("\t")
            f.write(",".join(sorted(entry['affiliations'])))
            f.write("\t")
            if entry['canon_name'] is None:
                f.write("<UNK>")
            else:
                f.write(entry['canon_name'])
            f.write("\n")

            if len(entry['affiliations']) > 0:
                with_aff_count += 1
                if len(entry['affiliations']) > 1:
                    with_multi_aff_count += 1
            else:
                without_aff_count += 1
        logging.info("All unique speakers found: %i", len(speaker_name_to_entry))
        logging.info("-- without any affiliation (cant assign): %i", without_aff_count)
        logging.info("-- with at least 1 affiliation: %i", with_aff_count)
        logging.info("-- with multiaffiliations: %i", with_multi_aff_count)


main()
