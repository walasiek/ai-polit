from aipolit.transcript.transcript_query import TranscriptQuery

sample_transcript_dir = "resources/test_data/transcripts_sejm"
transcript_query = TranscriptQuery(
    fixed_transcript_dir=sample_transcript_dir)


def test_simple_query():
    assert transcript_query.count_transcripts() == 1, "Check if no of transcripts loaded correctly"
