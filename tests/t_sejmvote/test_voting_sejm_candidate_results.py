from aipolit.sejmvote.voting_sejm_candidate_results import VotingSejmCandidateResults
import pytest


def test_simple_check():
    candidate_results = VotingSejmCandidateResults.get_instance(okreg_no='13')
    assert candidate_results is not None

    assert candidate_results.get_filename() == 'wyniki_gl_na_kand_po_obwodach_sejm_okr_13.csv'

    # some random candidates to check
    assert candidate_results.lista_id_to_candidate_names['ko'][11] == 'Władysław Andrzej DYNA'
    assert candidate_results.lista_id_to_candidate_names['pis'][0] == 'Małgorzata Ewa WASSERMANN'
    assert candidate_results.lista_id_to_candidate_names['psl'][26] == 'Stanisław DZIEDZIC'
    assert candidate_results.lista_id_to_candidate_names['sld'][27] == 'Tomasz Marek LEŚNIAK'
    assert candidate_results.lista_id_to_candidate_names['konfederacja'][22] == 'Janina PĘCZEK'

    # some random values to check
    obwod_id = '120601===1'   # source: https://sejmsenat2019.pkw.gov.pl/sejmsenat2019/pl/wyniki/protokol/sejm/546450
    results_entry = candidate_results.get_results_entry_by_obwod_id(obwod_id)
    assert results_entry['total_votes_lista_psl_cand_0'] == 47
    assert results_entry['total_votes_lista_psl_cand_1'] == 6
    assert results_entry['total_votes_lista_psl_cand_2'] == 15
    assert results_entry['total_votes_lista_pis_cand_27'] == 14
