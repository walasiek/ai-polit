#!/usr/bin/env python3

import argparse
import logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(asctime)s\t%(message)s')


import re
from aipolit.transcript.person_affiliation import PersonAffiliation, Person


DESCRIPTION="""
Helper script to parse person political affiliation.
It analyzes data from the web.
Additionally it cross-checks with current data we have in resources:
1. Persons occuring in resources, but not occurring in none of new files are printed as warnings
2. Persons occuring in resources as ACTIVE, but in new files as NOT_ACTIVE, are updated with active_to filled as "TODO"
3. Persons with mismatch in club name have their clubs updated accordingly (current/previos club date_to/from are marked as "TODO")

Produces file which after manual rearrangments (check "TODO") can be copied to resources as new (updated) affiliation file.

Data sources:
1. Data for sejm 10th term (download those pages and use as input params)
- active: https://www.sejm.gov.pl/Sejm10.nsf/poslowie.xsp?type=A
- deactivated: https://www.sejm.gov.pl/Sejm10.nsf/poslowie.xsp?type=B

To manually fill correct dates it is useful to check: https://pl.wikipedia.org/wiki/Pos%C5%82owie_na_Sejm_Rzeczypospolitej_Polskiej_X_kadencji
"""


def parse_arguments():
    """parse command line arguments"""
    parser = argparse.ArgumentParser(
        description=DESCRIPTION
    )

    parser.add_argument(
        '--infile-active', '-ia',
        required=True,
        help='Input file with active persons')

    parser.add_argument(
        '--infile-deactivated', '-id',
        help='Input file with persons who are not active anymore')

    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Where to save final .json file after parse (to be reviewed manually)')

    args = parser.parse_args()

    return args


def unify_club_name(club_name):
    fixed_replacements = {
        'niez.': "niezależni",
        "PSL-TD": "PSL",
        "Polska2050-TD": "PL2050",
    }
    if club_name in fixed_replacements:
        return fixed_replacements[club_name]
    return club_name


def split_f_name_and_s_name(surname_and_name):
    f_name = None
    s_name = None
    match = re.match(r"^\s*([^ ]+)\s+(.*)$", surname_and_name)
    if match:
        s_name = match.group(1).strip()
        f_name = match.group(2).strip()

    return f_name, s_name


def read_data_from_active_file(f, output):
    for line in f:
        line = line.rstrip()

        match = re.search(r"div class=\"deputyName\">([^<]+)</div></a><div class=\"deputy-box-details\"><strong>([^<]+)</strong>", line)
        if match:
            surname_and_name = match.group(1)
            club_name = unify_club_name(match.group(2))
            f_name, s_name = split_f_name_and_s_name(surname_and_name)
            if f_name is not None and s_name is not None:
                entry = (f_name, s_name, club_name)
                output.append(entry)
    logging.info("Found %i active MPs after parsing active file!", len(output))


def read_data_from_deactivated_file(f, output):
    for line in f:
        line = line.rstrip()
        match = re.search(r"<div class=\"deputyName\">([^<]+)</div></a><div class=\"deputy-box-details\"><strong>([^<]+)</strong><br>([^<]+)</div></div>", line)
        if match:
            surname_and_name = match.group(1)
            club_name = unify_club_name(match.group(2))
            reason = unify_club_name(match.group(3))
            f_name, s_name = split_f_name_and_s_name(surname_and_name)
            if f_name is not None and s_name is not None:
                entry = (f_name, s_name, club_name, reason)
                output.append(entry)
    logging.info("Found %i NOT active MPs after parsing deactivated file!", len(output))


def create_new_data(data):
    active_list = data['active']
    not_active_list = data['deactivated']

    new_data = []

    for e in active_list:
        new_e = {
            "f_name": e[0],
            "s_name": e[1],
            "current_club_name": e[2],
            "active": True,
        }
        new_data.append(new_e)

    for e in not_active_list:
        new_e = {
            "f_name": e[0],
            "s_name": e[1],
            "current_club_name": e[2],
            "deactivate_reason": e[3],
            "active": False,
        }
        new_data.append(new_e)

    return new_data


def merge_with_old(args, data):
    person_affiliation = PersonAffiliation()
    logging.info("Loaded current PersonAffiliation with active persons %i out of %i in data file.",
                 person_affiliation.count(only_active=True),
                 person_affiliation.count(),
                 )

    new_data = create_new_data(data)

    # add all new to person_affiliation

    names_in_new_data = set()
    for e in new_data:
        old_person = person_affiliation.get_person_by_f_name_and_s_name(e['f_name'], e['s_name'])
        names_in_new_data.add(f"{e['f_name']} {e['s_name']}")

        if old_person is None:
            club_entry = {
                'club_name': e['current_club_name'],
                'from_date': f"{Person.UNK_ENTRY}_NEW_PERSON_START_TERM"
            }

            e['clubs'] = [club_entry]
            if not e['active']:
                e['active_to'] = f"{Person.UNK_ENTRY}_DEACTIVATE_DATE"

            person_affiliation.add_person(Person.from_json_entry(e))
        else:
            # Cases for conflicts:

            # Case 1: inconsistent activity (MP is not active anymore)
            if old_person.check_is_active() != e['active']:
                if not e['active']:
                    old_person.is_active = False
                    old_person.deactivate_reason = e['deactivate_reason']
                    old_person.active_to = f"{Person.UNK_ENTRY}_DEACTIVATE_DATE"
                else:
                    raise ValueError(f"Inconsistent data... It seems person_affiliation who was not active is active in new parsed data! This is impossible... so please check if there is no implementation error: {str(e)}")

            else:
                # Case 2: inconsistent club (change of club), and person still active
                if (old_person.get_club() != e['current_club_name']) and e['active']:
                    old_person.all_clubs[-1]['to_date'] = f"{Person.UNK_ENTRY}_CHANGE_OF_CLUB_DATE"
                    old_person.all_clubs.append({
                        'club_name': e['current_club_name'],
                        'from_date': f"{Person.UNK_ENTRY}_CHANGE_OF_CLUB_DATE"
                    })

    # Check if there is someone in "old" data who does not appear in new data
    for name in person_affiliation.name_to_entry.keys():
        if name not in names_in_new_data:
            logging.info("WARNING: Name %s from old PersonAffiliation data file not found in new parsed data!", name)

    return person_affiliation

def read_data_from_files(args):
    data = dict()
    data['active'] = []

    if args.infile_active:
        with open(args.infile_active, "r") as f:
            read_data_from_active_file(f, data['active'])
    if args.infile_deactivated:
        with open(args.infile_deactivated, "r") as f:
            data['deactivated'] = []
            read_data_from_deactivated_file(f, data['deactivated'])

    person_affiliation = merge_with_old(args, data)
    person_affiliation.dump_to_json_file(args.output)

    logging.info("Saving new data file to: %s\n\n"
                 "Now you should review the file manually and check for all 'TODO' e.g.:\n"
                 "  diff %s %s\n\n"
                 "When you are done please save the file to:\n"
                 "  cp %s %s",
                 args.output,
                 person_affiliation.input_data_filepath, args.output,
                 person_affiliation.input_data_filepath, args.output)


def main():
    args = parse_arguments()

    data = read_data_from_files(args)

    # TODO


main()
