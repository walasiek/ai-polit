from aipolit.sejmvote.voting_place_data_prez2020 import VotingPlaceDataPrez2020
from aipolit.sejmvote.voting_place_data_sejm2019 import VotingPlaceDataSejm2019
from aipolit.sejmvote.globals import AVAILABLE_ELECTIONS_IDS


INSTANCE = dict()


def create_voting_place_data(elections_id):
    assert elections_id in AVAILABLE_ELECTIONS_IDS

    if elections_id not in INSTANCE:
        if elections_id == 'sejm2019':
            INSTANCE[elections_id] = VotingPlaceDataSejm2019()
        elif elections_id == 'prez2020':
            INSTANCE[elections_id] = VotingPlaceDataPrez2020()
        else:
            raise Exception("Unknown elections id: " + str(elections_id))

    return INSTANCE[elections_id]
