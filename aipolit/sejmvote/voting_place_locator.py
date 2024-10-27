from geopy.geocoders import Nominatim
import re
import logging


class VotingPlaceLocator:
    """
    Queries DBs such as OpenStreetMap to find longitude and latitude of the given
    voting place.
    """

    def __init__(self):
        self.cache = dict()
        self.locator = Nominatim(user_agent="aipolit-geocoder")

    def query(self, voting_place):
        """
        Returns tuple (latitude, longitude)
        """
        place_hash = self.get_hash(voting_place)
        if place_hash in self.cache:
            return self.cache[place_hash]

        final_result = self._try_to_query(voting_place)
        if final_result is None:
            logging.info("WARNING! Could not find location for: %s", voting_place['location_fullname'])
            final_result = (None, None)

        self.cache[place_hash] = final_result
        return final_result

    def _try_to_query(self, voting_place):
        query = {
            'street': '',
            'city': voting_place['city'],
            'country': 'Polska',
            'postalcode': voting_place['postal_code'],
        }

        street_candidates = self._create_street_cands(voting_place)
        queried_streets = set()

        for cand_street in street_candidates:
            if cand_street in queried_streets:
                continue
            queried_streets.add(cand_street)
            query['street'] = cand_street
            location = None
            try:
                location = self.locator.geocode(query)
            except Exception as e:
                logging.error("PROBLEM WITH RETRIEVAL OF QUERY: %s\nEXCEPTION: %s", query, e)

            if location is not None:
                return (location.latitude, location.longitude)
        return None

    def _create_street_cands(self, voting_place):
        cands = []
        if voting_place['street_name']:
            cands.append(f"{voting_place['street_number']} {voting_place['street_name']}")
            cands.append(f"{voting_place['street_name']}")

            street_name = voting_place['street_name']
            street_name_replaced = re.sub(r"^\s*(ul|al|os|pl)\.\s*", "", street_name)
            if street_name_replaced != street_name:
                cands.append(f"{voting_place['street_number']} {street_name_replaced}")
                cands.append(f"{street_name_replaced}")
        else:
            cands.append(f"{voting_place['street_number']}")
#            cands.append(f"{voting_place['city']} {voting_place['street_number']}")

        return cands

    @classmethod
    def get_hash(cls, voting_place):
        place_hash = "===".join((voting_place['teryt_gminy'], voting_place['street_name'], voting_place['street_number'], voting_place['city']))
        return place_hash
