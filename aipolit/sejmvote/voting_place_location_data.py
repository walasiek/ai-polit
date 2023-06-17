import logging
import os
from collections import OrderedDict, Counter
from aipolit.utils.text import read_tsv, NONE_STRING


class VotingPlaceLocationData:
    FILENAME = 'voting_place_location_data.tsv'

    FLOAT_COLUMNS = {
        'latitude',
        'longitude',
    }

    def __init__(self, data_directory):
        self.obwod_id_to_location_data = OrderedDict()
        self.data_directory = data_directory

    def get_data_fp(self):
        fp = os.path.join(
            self.data_directory,
            self.FILENAME)
        return fp

    @classmethod
    def create_empty_entry(cls):
        entry = OrderedDict()
        entry['obwod_id'] = None
        entry['latitude'] = None
        entry['longitude'] = None
        entry['duplicate_count'] = None
        entry['duplicate_index'] = None
        return entry

    def add_location_data(self, obwod_id, latitude, longitude):
        entry = self.create_empty_entry()
        entry['obwod_id'] = obwod_id
        entry['latitude'] = latitude
        entry['longitude'] = longitude

        self.obwod_id_to_location_data[obwod_id] = entry

    def deduplicate_coordinates(self, obwod_id, delta=0.001):
        entry = self.obwod_id_to_location_data[obwod_id]

        latitude = entry['latitude']
        longitude = entry['longitude']

        if entry['duplicate_count'] is None or entry['duplicate_index'] is None:
            raise Exception(f"Implementation error: duplicate_count or duplicate_index are not defined for {obwod_id}. Function reload_duplicate_location_resolver should be run first!")

        duplicate_index = entry['duplicate_index']
        duplicate_count = entry['duplicate_count']

        delta_x = int(duplicate_index / 3)
        delta_y = duplicate_index % 3

        return (latitude + delta_x * delta, longitude + delta_y * delta)

    def reload_duplicate_location_resolver(self):
        """
        Should be loaded to resolve duplicate location for map generation
        Recommended to use after any data manipulation (add, load)
        """
        duplicate_count = Counter()
        for obwod_id, entry in self.obwod_id_to_location_data.items():
            location_hash = (entry['latitude'],  entry['longitude'])
            entry['duplicate_index'] = duplicate_count[location_hash]
            duplicate_count[location_hash] += 1

        for obwod_id, entry in self.obwod_id_to_location_data.items():
            location_hash = (entry['latitude'],  entry['longitude'])
            entry['duplicate_count'] = duplicate_count[location_hash]

    def load_data(self):
        fp = self.get_data_fp()

        if os.path.isfile(fp):
            data = read_tsv(fp)
            for raw_entry in data:
                entry = self.create_empty_entry()
                for k, v in raw_entry.items():
                    if v == NONE_STRING:
                        v = None
                    elif v is None:
                        v = None
                    elif k in self.FLOAT_COLUMNS:
                        v = float(v)
                    entry[k] = v
                self.obwod_id_to_location_data[entry['obwod_id']] = entry

        self.reload_duplicate_location_resolver()
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
