import logging
from collections import OrderedDict, defaultdict
from aipolit.utils.text import read_csv
from aipolit.utils.globals import \
     AIPOLIT_SEJM_ELECTION_VOTING_PLACE_RAW_DATA_FP, \
     AIPOLIT_SEJM_ELECTION_VOTING_PLACE_DATA_DIR


class VotingPlaceData:
    """
    Load voting location data.
    """

    INSTANCE = dict()

    def __init__(self):
        self.voting_place_data = []
        self.obwod_id_to_index = dict()
        self.location_data = None
        self.okreg_number_to_powiats = defaultdict(set)
        # workaround to allow use different keys in derived classes
        self.okreg_key_name = 'sejm_okreg_number'

    @classmethod
    def create_id_from_entry(cls, entry):
        return entry['teryt_gminy'] + '===' + entry['obwod_number']

    def get_powiats_for_okreg(self, okreg):
        return list(sorted(self.okreg_number_to_powiats.get(okreg, {})))

    def add_powiat_for_okreg(self, okreg, powiat_name):
        self.okreg_number_to_powiats[okreg].add(powiat_name)

    def get_voting_place_by_id(self, obwod_id):
        index = self.obwod_id_to_index[obwod_id]
        return self.voting_place_data[index]

    def get_obwod_ids_matching_criteria(self, city=None, okreg_number=None, with_location_data=True, min_population=None, powiat_name=None):
        result = []
        for entry in self.voting_place_data:
            if city:
                if entry['city'] != city:
                    continue
            if powiat_name:
                if entry['powiat_name'] != powiat_name:
                    continue
            if okreg_number:
                if entry[self.okreg_key_name] != okreg_number:
                    continue
            if with_location_data:
                if entry['obwod_id'] not in self.location_data.obwod_id_to_location_data:
                    continue

                location_data = self.location_data.obwod_id_to_location_data[entry['obwod_id']]
                skip_this = False
                for k in ['latitude', 'longitude']:
                    if location_data[k] is None:
                        skip_this = True
                if skip_this:
                    continue
            if min_population:
                if min_population > entry['population']:
                    continue

            result.append(entry['obwod_id'])
        return result
