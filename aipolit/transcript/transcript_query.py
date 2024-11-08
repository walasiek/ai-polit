from aipolit.transcript.utils import load_transcripts
from hipisejm.stenparser.transcript import SpeechReaction, SpeechInterruption


AVAILABLE_TO_DUMP = {
    'speech_speaker',
    'utt',   # all utt tags regardless type
    'utt_norm', # only utt without reactions and interruptions
    'utt_reaction', # only reaction
    'utt_interrupt', # only interruptions
    'utt_interrupt_by', # only names of the persons who interrupted
}


class TranscriptQuery:
    """
    This class helps to dump specific parts of the transcripts.
    For example one can use it to dump all speaker names.
    """

    def __init__(self, fixed_transcript_dir=None):
        self.transcripts = load_transcripts(fixed_dir=fixed_transcript_dir)
        self.cache = {}
        self._clear_cache()

    def query(self, what_to_dump, to_filehandle=None, to_list=None):
        # workaround for argparse :)
        if isinstance(what_to_dump, list):
            what_to_dump = {k for k in what_to_dump}
        elif isinstance(what_to_dump, str):
            what_to_dump = {what_to_dump}

        assert isinstance(what_to_dump, set), "what_to_dump should be set!"

        self._clear_cache()
        self.cache['out_file'] = to_filehandle
        self.cache['out_list'] = to_list

        for dump_type in what_to_dump:
            assert dump_type in AVAILABLE_TO_DUMP

        matching_transcripts = self.transcripts
        self._dump_matching(matching_transcripts, what_to_dump)

    def count_transcripts(self):
        return len(self.transcripts)

    def _clear_cache(self):
        self.cache = dict()
        self.cache['out_file'] = None
        self.cache['out_list'] = None

    def _dump_matching(self, matching_transcripts, what_to_dump):
        for transcript in matching_transcripts:
            for session_speech in transcript.session_content:

                if 'speech_speaker' in what_to_dump:
                    self._put_to_dump(session_speech.speaker)

                for speech_content in session_speech.content:
                    if isinstance(speech_content, str):
                        if 'utt' in what_to_dump or 'utt_norm' in what_to_dump:
                            self._put_to_dump(speech_content)
                    else:
                        if isinstance(speech_content, SpeechReaction):
                            if 'utt' in what_to_dump or 'utt_reaction' in what_to_dump:
                                self._put_to_dump(speech_content.reaction_text)
                        elif isinstance(speech_content, SpeechInterruption):
                            if 'utt_interrupt_by' in what_to_dump:
                                self._put_to_dump(speech_content.interrupted_by_speaker)
                            if 'utt' in what_to_dump or 'utt_interrupt' in what_to_dump:
                                self._put_to_dump(speech_content.text)

    def _put_to_dump(self, txt):
        if self.cache['out_list'] is not None:
            self.cache['out_list'].append(txt)
        elif self.cache['out_file'] is not None:
            self.cache['out_file'].write(txt)
            self.cache['out_file'].write("\n")
        else:
            print(txt)
