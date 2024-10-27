from aipolit.sejmvote.globals import AVAILABLE_ELECTIONS_IDS

from aipolit.sejmvote.voting_sejm_candidate_results import VotingSejmCandidateResults
from aipolit.sejmvote.voting_sejm2023_candidate_results import VotingSejm2023CandidateResults
from aipolit.sejmvote.voting_prez2020_candidate_results import VotingPrez2020CandidateResults


def create_voting_candidate_results(elections_id, okreg_no):
    assert elections_id in AVAILABLE_ELECTIONS_IDS

    if elections_id == 'sejm2019':
        return VotingSejmCandidateResults(okreg_no)
    elif elections_id == 'sejm2023':
        return VotingSejm2023CandidateResults(okreg_no)
    elif elections_id == 'prez2020':
        return VotingPrez2020CandidateResults(okreg_no)

    raise Exception("Unknown elections id: " + str(elections_id))
