from aipolit.sejmvote.voting_sejm_general_results import VotingSejmGeneralResults
import pytest


def test_simple_check():
    general_results_data = VotingSejmGeneralResults()
    assert general_results_data is not None

    obwod_ids = general_results_data.voting_place_data.get_obwod_ids_matching_criteria(
        city="Kraków",
        sejm_okreg_number='13',
        with_location_data=True,
        min_population=300,
        powiat_name=None)

    assert len(obwod_ids) == 398

    assert '126101===21' in obwod_ids

    results_entry = general_results_data.get_results_entry_by_obwod_id("126101===21")
    assert results_entry is not None

    # source: https://sejmsenat2019.pkw.gov.pl/sejmsenat2019/pl/wyniki/protokol/sejm/547861
    assert results_entry['region_name'] == 'małopolskie'
    assert results_entry['total_possible_voters'] == 1604
    assert results_entry['total_valid_votes'] == 1157
    assert results_entry['total_votes_lista_ko'] == 388
    assert results_entry['total_votes_lista_konfederacja'] == 97
    assert results_entry['total_votes_lista_sld'] == 195
    assert results_entry['total_votes_lista_pis'] == 421
