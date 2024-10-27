from aipolit.sejmvote.voting_prez2020_candidate_results import VotingPrez2020CandidateResults


class VotingPrez2020GeneralResults:
    """
    Stores general results (na listy) from the Prez2020 Elections.
    IMPORTANT: This is really a wrapper around VotingPrez2020CandidateResults
    to preserve compatibility with the Sejm2019 elections!
    """
    def __init__(self):
        self.candidate_results_data = VotingPrez2020CandidateResults.get_instance(okreg_no=None)
        self.voting_place_data = self.candidate_results_data.voting_place_data
        self.results_data = self.candidate_results_data.results_data
        self.obwod_id_to_index = self.candidate_results_data.obwod_id_to_index

    def get_results_entry_by_obwod_id(self, obwod_id):
        if obwod_id in self.obwod_id_to_index:
            i = self.obwod_id_to_index[obwod_id]
            return self.results_data[i]
        return None
