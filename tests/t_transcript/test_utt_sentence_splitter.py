from hipisejm.stenparser.transcript import SpeechReaction, SpeechInterruption
from aipolit.transcript.utt_sentence_splitter import UttSentenceSplitter


splitter = UttSentenceSplitter()


def test_sample_utt_split_reg():
    tested_utt = 'To jest pkt. 1. To jest pkt.2. A to jest trzecie!'
    actual_result = splitter.split_utt_to_sentences(tested_utt)
    assert actual_result == [
        ('To jest pkt. 1.', 0),
        ('To jest pkt.2.', 16),
        ('A to jest trzecie!', 31)], "test sample utt with reg type"


def test_sample_utt_split_interruption():
    tested_utt = SpeechInterruption('Anna Nowak', 'Hańba! Hańba! Hańba!')
    actual_result = splitter.split_utt_to_sentences(tested_utt)
    assert actual_result == [
        ('Hańba!', 0),
        ('Hańba!', 7),
        ('Hańba!', 14)], "test sample utt with interruption"


def test_sample_utt_split_interruption_no_space():
    tested_utt = SpeechInterruption('Anna Nowak', 'Hańba!Hańba!Hańba!')
    actual_result = splitter.split_utt_to_sentences(tested_utt)
    assert actual_result == [
        ('Hańba!Hańba!Hańba!', 0),], "test sample utt with interruption no space"


def test_sample_utt_split_reaction():
    tested_utt = SpeechReaction('Oklaski. Śmiech na sali.')
    actual_result = splitter.split_utt_to_sentences(tested_utt)
    assert actual_result == [
        ('Oklaski.', 0),
        ('Śmiech na sali.', 9)], "test sample utt with reaction"
