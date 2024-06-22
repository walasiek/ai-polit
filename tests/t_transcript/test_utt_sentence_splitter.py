from hipisejm.stenparser.transcript import SpeechReaction, SpeechInterruption
from aipolit.transcript.utt_sentence_splitter import UttSentenceSplitter


splitter = UttSentenceSplitter()


def test_sample_utt_split_reg():
    tested_utt = 'To jest pierwsze zdanie. To jest drugie. A to jest trzecie!'
    actual_result = splitter.split_utt_to_sentences(tested_utt)
    assert actual_result == [
        'To jest pierwsze zdanie.',
        'To jest drugie.',
        'A to jest trzecie!'], "test sample utt with reg type"


def test_sample_utt_split_interruption():
    tested_utt = SpeechInterruption('Anna Nowak', 'Hańba! Hańba! Hańba!')
    actual_result = splitter.split_utt_to_sentences(tested_utt)
    assert actual_result == [
        'Hańba!',
        'Hańba!',
        'Hańba!'], "test sample utt with interruption"


def test_sample_utt_split_reaction():
    tested_utt = SpeechReaction('Oklaski. Śmiech na sali.')
    actual_result = splitter.split_utt_to_sentences(tested_utt)
    assert actual_result == [
        'Oklaski.',
        'Śmiech na sali.'], "test sample utt with reaction"
