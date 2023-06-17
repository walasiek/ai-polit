from aipolit.sejmvote.globals import AVAILABLE_ELECTIONS_IDS

from aipolit.sejmvote.voting_place_data_prez2020 import VotingPlaceDataPrez2020
from aipolit.sejmvote.voting_place_data_sejm2019 import VotingPlaceDataSejm2019
from aipolit.sejmvote.voting_sejm_general_results import VotingSejmGeneralResults
from aipolit.sejmvote.voting_sejm_candidate_results import VotingSejmCandidateResults
from aipolit.sejmvote.voting_prez2020_general_results import VotingPrez2020GeneralResults
from aipolit.sejmvote.voting_prez2020_candidate_results import VotingPrez2020CandidateResults


VOTING_PLACE_DATA_INSTANCE = dict()


def create_voting_place_data(elections_id):
    assert elections_id in AVAILABLE_ELECTIONS_IDS

    if elections_id not in VOTING_PLACE_DATA_INSTANCE:
        if elections_id == 'sejm2019':
            VOTING_PLACE_DATA_INSTANCE[elections_id] = VotingPlaceDataSejm2019()
        elif elections_id == 'prez2020':
            VOTING_PLACE_DATA_INSTANCE[elections_id] = VotingPlaceDataPrez2020()
        else:
            raise Exception("Unknown elections id: " + str(elections_id))

    return VOTING_PLACE_DATA_INSTANCE[elections_id]


def create_voting_general_results(elections_id):
    assert elections_id in AVAILABLE_ELECTIONS_IDS

    if elections_id == 'sejm2019':
        return VotingSejmGeneralResults()
    elif elections_id == 'prez2020':
        return VotingPrez2020GeneralResults()

    raise Exception("Unknown elections id: " + str(elections_id))


def create_voting_candidate_results(elections_id, okreg_no):
    assert elections_id in AVAILABLE_ELECTIONS_IDS

    if elections_id == 'sejm2019':
        return VotingSejmCandidateResults(okreg_no)
    elif elections_id == 'prez2020':
        return VotingPrez2020CandidateResults(okreg_no)

    raise Exception("Unknown elections id: " + str(elections_id))
