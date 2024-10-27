from aipolit.sejmvote.globals import AVAILABLE_ELECTIONS_IDS

from aipolit.sejmvote.voting_sejm_general_results import VotingSejmGeneralResults
from aipolit.sejmvote.voting_sejm2023_general_results import VotingSejm2023GeneralResults
from aipolit.sejmvote.voting_prez2020_general_results import VotingPrez2020GeneralResults


def create_voting_general_results(elections_id):
    assert elections_id in AVAILABLE_ELECTIONS_IDS

    if elections_id == 'sejm2019':
        return VotingSejmGeneralResults()
    elif elections_id == 'sejm2023':
        return VotingSejm2023GeneralResults()
    elif elections_id == 'prez2020':
        return VotingPrez2020GeneralResults()

    raise Exception("Unknown elections id: " + str(elections_id))
