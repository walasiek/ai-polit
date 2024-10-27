from hipisejm.stenparser.transcript import SpeechReaction, SpeechInterruption
from aipolit.transcript.utt_sentence_splitter import UttSentenceSplitter


splitter = UttSentenceSplitter()


def test_sample_utt_split_reg():
    tested_utt = 'To jest pkt. 1. To jest pkt.2. A to jest trzecie!'
    actual_result_sentences = splitter.split_utt_to_sentences(tested_utt)
    assert actual_result_sentences == [
        'To jest pkt. 1.',
        'To jest pkt.2.',
        'A to jest trzecie!'], "test sample utt with reg type"

    actual_result_indexes = splitter.estimate_start_index_of_each_sentence_matching(tested_utt, actual_result_sentences)

    assert actual_result_indexes == [
        0, 16, 31], "test sample utt with reg type (sentence index)"

def test_sample_utt_split_reg_single_sentence():
    tested_utt = 'Hola!'
    actual_result_sentences = splitter.split_utt_to_sentences(tested_utt)
    assert actual_result_sentences == [
        'Hola!'], "test sample utt with reg type single sentence"

    actual_result_indexes = splitter.estimate_start_index_of_each_sentence_matching(tested_utt, actual_result_sentences)

    assert actual_result_indexes == [0], "test sample utt with reg type single sentence (sentence index)"


def test_sample_utt_split_reg_empty_sentence():
    tested_utt = ''
    actual_result_sentences = splitter.split_utt_to_sentences(tested_utt)
    assert actual_result_sentences == [], "test sample utt with reg type empty sentence"

    actual_result_indexes = splitter.estimate_start_index_of_each_sentence_matching(tested_utt, actual_result_sentences)

    assert actual_result_indexes == [], "test sample utt with reg type empty sentence (sentence index)"


def test_sample_utt_split_interruption():
    tested_utt = SpeechInterruption('Anna Nowak', 'Hańba! Hańba! Hańba!')
    actual_result_sentences = splitter.split_utt_to_sentences(tested_utt)
    assert actual_result_sentences == [
        'Hańba!',
        'Hańba!',
        'Hańba!'], "test sample utt with interruption"

    actual_result_indexes = splitter.estimate_start_index_of_each_sentence_matching(tested_utt, actual_result_sentences)

    assert actual_result_indexes == [
        0, 7, 14], "test sample utt with interruption (sentence index)"


def test_sample_utt_split_interruption_no_space():
    tested_utt = SpeechInterruption('Anna Nowak', 'Hańba!Hańba!Hańba!')
    actual_result_sentences = splitter.split_utt_to_sentences(tested_utt)
    assert actual_result_sentences == [
        'Hańba!Hańba!Hańba!',], "test sample utt with interruption no space"

    actual_result_indexes = splitter.estimate_start_index_of_each_sentence_matching(tested_utt, actual_result_sentences)

    assert actual_result_indexes == [
        0], "test sample utt with interruption no space (sentence index)"


def test_sample_utt_split_reaction():
    tested_utt = SpeechReaction('Oklaski. Śmiech na sali.')
    actual_result_sentences = splitter.split_utt_to_sentences(tested_utt)
    assert actual_result_sentences == [
        'Oklaski.',
        'Śmiech na sali.'], "test sample utt with reaction"

    actual_result_indexes = splitter.estimate_start_index_of_each_sentence_matching(tested_utt, actual_result_sentences)

    assert actual_result_indexes == [
        0, 9], "test sample utt with reaction (sentence index)"
