from aipolit.transcript.utils import load_transcripts


class TranscriptQuery:
    """
    This class helps to dump specific parts of the transcripts.
    For example one can use it to dump all speaker names.
    """

    def __init__(self, fixed_transcript_dir=None):
        self.transcripts = load_transcripts(fixed_dir=fixed_transcript_dir)

    def count_transcripts(self):
        return len(self.transcripts)
