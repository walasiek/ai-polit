from aipolit.sejmvote.voting_prez2020_candidate_results import VotingPrez2020CandidateResults
import pytest


def test_simple_check():
    candidate_results = VotingPrez2020CandidateResults.get_instance(okreg_no='18')
    assert candidate_results is not None

    # some random candidates to check
    assert candidate_results.lista_id_to_candidate_names['1_tura'][0] == 'Robert BIEDROŃ'
    assert candidate_results.lista_id_to_candidate_names['1_tura'][1] == 'Krzysztof BOSAK'
    assert candidate_results.lista_id_to_candidate_names['1_tura'][2] == 'Andrzej Sebastian DUDA'
    assert candidate_results.lista_id_to_candidate_names['1_tura'][3] == 'Szymon Franciszek HOŁOWNIA'
    assert candidate_results.lista_id_to_candidate_names['1_tura'][4] == 'Marek JAKUBIAK'
    assert candidate_results.lista_id_to_candidate_names['1_tura'][5] == 'Władysław Marcin KOSINIAK-KAMYSZ'
    assert candidate_results.lista_id_to_candidate_names['1_tura'][6] == 'Mirosław Mariusz PIOTROWSKI'
    assert candidate_results.lista_id_to_candidate_names['1_tura'][7] == 'Paweł Jan TANAJNO'
    assert candidate_results.lista_id_to_candidate_names['1_tura'][8] == 'Rafał Kazimierz TRZASKOWSKI'
    assert candidate_results.lista_id_to_candidate_names['1_tura'][9] == 'Waldemar Włodzimierz WITKOWSKI'
    assert candidate_results.lista_id_to_candidate_names['1_tura'][10] == 'Stanisław Józef ŻÓŁTEK'

    assert candidate_results.get_candidate_name('1_tura', 4) == 'Marek JAKUBIAK'

    # some random values to check
    obwod_id = '120201===5'   # source: https://prezydent20200628.pkw.gov.pl/prezydent20200628/pl/wyniki/1/protokol/704240
    results_entry = candidate_results.get_results_entry_by_obwod_id(obwod_id)
    assert results_entry['total_votes_lista_1_tura_cand_0'] == 14
    assert results_entry['total_votes_lista_1_tura_cand_1'] == 103
    assert results_entry['total_votes_lista_1_tura_cand_2'] == 552
    assert results_entry['total_votes_lista_1_tura_cand_3'] == 85

    assert candidate_results.get_candidate_result(obwod_id, '1_tura', 0) == 14
    assert candidate_results.get_candidate_result(obwod_id, '1_tura', 1) == 103
