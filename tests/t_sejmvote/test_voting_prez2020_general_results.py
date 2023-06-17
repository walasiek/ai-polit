from aipolit.sejmvote.voting_prez2020_general_results import VotingPrez2020GeneralResults
import pytest


def test_simple_check():
    general_results_data = VotingPrez2020GeneralResults()
    assert general_results_data is not None

    obwod_ids = general_results_data.voting_place_data.get_obwod_ids_matching_criteria(
        city=None,
        okreg_number='18',
        with_location_data=False,
        min_population=300,
        powiat_name=None)

    assert len(obwod_ids) == 1207

    assert '126101===21' in obwod_ids
    # source: https://prezydent20200628.pkw.gov.pl/prezydent20200628/pl/wyniki/1/protokol/706025
    results_entry = general_results_data.get_results_entry_by_obwod_id("126101===21")
    assert results_entry is not None

    assert results_entry['region_name'] == 'małopolskie'
    assert results_entry['total_possible_voters'] == 1544
    assert results_entry['total_valid_votes'] == 1142
    assert results_entry['total_votes_lista_1_tura'] == 1142
