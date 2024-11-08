from hipisejm.stenparser.transcript import SessionTranscript
from aipolit.transcript.occurrence_counter import ListOccurrenceCounter

sample_transcript_fp = "resources/test_data/transcripts_sejm/sample_transcript_06_a_ksiazka.xml"
sample_transcript = SessionTranscript()
sample_transcript.load_from_xml(sample_transcript_fp)


def test_simple_occurrence_count():
    searched_tokens = [
        'książka',
        'książki'
    ]
    counter = ListOccurrenceCounter(searched_tokens)
    result = counter.run_count(sample_transcript)
    assert len(result) == 5, "total number of occurrences found"


def test_detailed_occurrence_count():
    searched_tokens = [
        'Na sekretarzy dzisiejszych obrad',
    ]
    counter = ListOccurrenceCounter(searched_tokens)
    result = counter.run_count(sample_transcript)
    assert len(result) == 1, "total number of occurrences found"

    occurrence = result[0]

    assert occurrence.speaker == "Marszałek Szymon Hołownia"
    assert occurrence.sentence == "Na sekretarzy dzisiejszych obrad powołuję posłów Jolantę Niezgodzką, Aleksandrę Karolinę Wiśniewską, Filipa Kaczyńskiego i Łukasza Kmitę."
    assert occurrence.matched_utt_index == 2
    # TODO to może być trudne
    #assert occurrence.sentence_start_index_in_utt == 21
    assert occurrence.sentence_start_match == 0
    assert occurrence.sentence_end_match == len(searched_tokens[0])
    assert occurrence.prev_sentence == "Dzień dobry państwu."


def test_phrases_occurrence_count():
    searched_tokens = [
        'polski rząd',
    ]
    counter = ListOccurrenceCounter(searched_tokens)
    result = counter.run_count(sample_transcript)
    assert len(result) == 3, "total number of occurrences found"


def test_occurrence_correct_prev_sentence_with_double_interruptions():
    searched_tokens = [
        'Ha, ha, ha',
    ]
    counter = ListOccurrenceCounter(searched_tokens)
    result = counter.run_count(sample_transcript)
    assert len(result) == 12, "total number of occurrences found"

    occur_with_double = result[1]
    assert 'Bardzo proszę, panie pośle' in occur_with_double.prev_sentence, "Should correct show prev_sentence when two interruptions appear"
