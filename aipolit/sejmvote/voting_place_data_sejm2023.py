import logging
from collections import OrderedDict
from aipolit.utils.text import read_csv
from aipolit.utils.globals import \
     AIPOLIT_SEJM2023_ELECTION_VOTING_PLACE_RAW_DATA_FP, \
     AIPOLIT_SEJM2023_ELECTION_VOTING_PLACE_DATA_DIR
from aipolit.sejmvote.voting_place_location_data import VotingPlaceLocationData
from aipolit.sejmvote.voting_place_data import VotingPlaceData


class VotingPlaceDataSejm2023(VotingPlaceData):
    """
    Load voting location data for Sejm Elections in 2023.
    """

    INTEGER_COLUMNS = {
        'population',
        'voters_count',
    }

    # Put '' to ignore the column
    TRANSLATE_RAW_COLUMNS = {
        'TERYT gminy': 'teryt_gminy',
        'Województwo': '',
        'Gmina': 'gmina_name',
        'Powiat': 'powiat_name',
        'Numer': 'obwod_number',
        'Mieszkańcy': 'population',
        'Wyborcy': 'voters_count',
        'Siedziba': 'location_name',
        'Miejscowość': 'city',
        'Ulica': 'street_name',
        'Numer posesji': 'street_number',
        'Numer lokalu': 'street_sub_number',
        'Kod pocztowy': 'postal_code',
        'Poczta': '',
        'Typ obwodu': 'obwod_type',
        'Przystosowany dla niepełnosprawnych': 'ozn_friendly',
        'Typ obszaru': 'location_type',
        'Pełna siedziba': 'location_fullname',
        'Opis granic': 'borders_description',
        'Okręg Sejm': 'sejm2023_okreg_number',
        'Okręg Senat': 'senat2023_okreg_number',
        'Wysłane pakiety wyborcze': '',
        'Liczba wydanych pełnomocnictw do głosowania': '',
    }

    def __init__(self):
        super().__init__()

        # workaround to allow use different keys in derived classes
        self.okreg_key_name = 'sejm2023_okreg_number'

        self._load_from_raw()
        self.location_data = VotingPlaceLocationData(AIPOLIT_SEJM2023_ELECTION_VOTING_PLACE_DATA_DIR)
        self.location_data.load_data()

    def _load_from_raw(self):
        fp = AIPOLIT_SEJM2023_ELECTION_VOTING_PLACE_RAW_DATA_FP
        logging.info("Load raw data from the file: %s", fp)
        raw_data = read_csv(fp, delimiter=';', quotechar='"', fix_utf=True)

        for entry in raw_data:
            parsed_entry = self._parse_entry_keys(entry)
            if parsed_entry:
                obwod_id = self.create_id_from_entry(parsed_entry)
                parsed_entry['obwod_id'] = obwod_id
                self.add_powiat_for_okreg(parsed_entry[self.okreg_key_name], parsed_entry['powiat_name'])
                self.obwod_id_to_index[obwod_id] = len(self.voting_place_data)
                self.voting_place_data.append(parsed_entry)

        logging.info("Loaded %i voting places from raw data file", len(self.voting_place_data))

    def _parse_entry_keys(self, entry):
        """ Returns None if parsing failed """
        parsed_entry = OrderedDict()
        for k, v in entry.items():
            parsed_key = self.TRANSLATE_RAW_COLUMNS.get(k, None)
            if parsed_key is None:
                raise Exception(f"Unknown column name found in file {fp} column {k}")
            if parsed_key == '':
                continue
            if parsed_key in self.INTEGER_COLUMNS:
                try:
                    v = int(v)
                except Exception as e:
                    logging.info("Exception parsing int key [%s / %s] in entry: %s", k, parsed_key, entry)
                    # parsing failed
                    return None
                    continue
                    #raise e

            parsed_entry[parsed_key] = v
        return parsed_entry
