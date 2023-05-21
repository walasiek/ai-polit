import logging
import os
from collections import OrderedDict
from aipolit.utils.text import read_tsv, NONE_STRING
from aipolit.utils.globals import \
     AIPOLIT_SEJM_ELECTION_VOTING_PLACE_DATA_DIR


class VotingPlaceLocationData:
    FILENAME = 'voting_place_location_data.tsv'

    FLOAT_COLUMNS = {
        'latitude',
        'longitude',
    }

    def __init__(self):
        self.obwod_id_to_location_data = OrderedDict()

    @classmethod
    def get_data_fp(cls):
        fp = os.path.join(
            AIPOLIT_SEJM_ELECTION_VOTING_PLACE_DATA_DIR,
            cls.FILENAME)
        return fp

    def add_location_data(self, obwod_id, latitude, longitude):
        entry = OrderedDict()
        entry['obwod_id'] = obwod_id
        entry['latitude'] = latitude
        entry['longitude'] = longitude
        self.obwod_id_to_location_data[obwod_id] = entry

    def load_data(self):
        fp = self.get_data_fp()

        if os.path.isfile(fp):
            data = read_tsv(fp)
            for raw_entry in data:
                entry = OrderedDict()
                for k, v in raw_entry.items():
                    if v == NONE_STRING:
                        v = None
                    elif v is None:
                        v = None
                    elif k in self.FLOAT_COLUMNS:
                        v = float(v)
                    entry[k] = v
                self.obwod_id_to_location_data[entry['obwod_id']] = entry
        logging.info("Loaded %i VotingPlaceLocationData", len(self.obwod_id_to_location_data))

    def save_data(self):
        fp = self.get_data_fp()
        logging.info("Saving %i VotingPlaceLocationData to %s", len(self.obwod_id_to_location_data), fp)
        with open(fp, "w") as f:
            f.write("\t".join(("obwod_id", "latitude", "longitude")))
            f.write("\n")
            for obwod_id, entry in self.obwod_id_to_location_data.items():
                f.write(obwod_id)

                for k in ['latitude', 'longitude',]:
                    val = entry[k]
                    if val is None:
                        val = NONE_STRING
                    f.write("\t")
                    f.write(str(val))
                f.write("\n")
