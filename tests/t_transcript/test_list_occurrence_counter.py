from hipisejm.stenparser.transcript import SessionTranscript
from aipolit.transcript.occurrence_counter import ListOccurrenceCounter

sample_transcript_fp = "resources/test_data/sample_transcript_06_a_ksiazka.xml"
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


def test_phrases_occurrence_count():
    searched_tokens = [
        'polski rząd',
    ]
    counter = ListOccurrenceCounter(searched_tokens)
    result = counter.run_count(sample_transcript)
    assert len(result) == 3, "total number of occurrences found"
