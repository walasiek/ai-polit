import re
from typing import Union, Optional, List
from hipisejm.stenparser.transcript import SessionTranscript, SpeechReaction, SpeechInterruption, SessionSpeech
from aipolit.transcript.utt_sentence_splitter import UttSentenceSplitter

def get_speaker_for_utt(utt, speech):
    """
    Helper method for Transcript processing
    """
    if isinstance(utt, str):
        return speech.speaker
    elif isinstance(utt, SpeechReaction):
        return None
    elif isinstance(utt, SpeechInterruption):
        return utt.interrupted_by_speaker
    else:
        raise ValueError(f"Unknown object utt in SessionSpeech: {utt}")


class PhraseOccurence:
    """
    Represents single occurrence of the phrase/word we are searching for.
    """
    def __init__(self,
                 speaker: str,
                 sentence: str,
                 utt_ref: Union[str, SpeechReaction, SpeechInterruption],
                 speech_ref: SessionSpeech,
                 prev_sentence: Optional[str]):
        self.speaker = speaker
        self.sentence = sentence
        self.utt_ref = utt_ref
        self.speech_ref = speech_ref
        self.prev_sentence = prev_sentence

    def __str__(self):
        full_txt = f"{self.speaker}: {self.sentence}"

        if isinstance(self.utt_ref, SpeechInterruption):
            inter_txt = f" (przerywając wypowiedź <{self.speech_ref.speaker}> o treści: {self.prev_sentence})"
            full_txt = full_txt + inter_txt
        return full_txt


class ListOccurrenceCounter:
    """
    This class counts occurrences of fixed list of phrases / words in the given transcript.
    """
    def __init__(self, searched_tokens: List[str]):
        self.searched_tokens = searched_tokens
        self.utt_sentence_splitter = UttSentenceSplitter()
        self.searched_regex = self._create_searched_regex()
        # cache objects
        self.cache = dict()
        self._init_cache()

    def run_count(self, transcript: SessionTranscript) -> List[PhraseOccurence]:
        """
        Returns list of counted occurrencies.
        Steps:
        1. Split into sentences using sentence-splitter
        2. Regex search for "hańba" occurrencies (and some variants like inflecional forms)

        Returns list consisting of entries (PhraseOccurence).

        Where:
        - speaker (str) - name of the speaker, who used "Hańba"
        - sentence (str) - sentence in which "Hańba" occured
        - utt_ref (str, SessionReaction, Session Interruption) - reference to full utterance object
        - speech_ref (SessionSpeech) - reference to full speech during which Hańba occurred
        - prev_sentence (str) - sentence preceeding occurrence of Hańba (only non-reaction/interruption sentences are counted)
        """
        result = []
        self._init_cache()

        for session_speech in transcript.session_content:
            self._count_in_speech(result, session_speech)

        return result

    def _create_searched_regex(self):
        regex_txt = r"\b(?:" + "|".join(self.searched_tokens) + r")\b"
        return re.compile(regex_txt, flags=re.IGNORECASE)

    def _init_cache(self):
        self.cache['prev_sentence'] = None
        self.cache['prev_utt'] = None
        self.cache['prev_utt_speech'] = None

    def _count_in_speech(self, result, session_speech):
        speech_speaker = session_speech.speaker
        for utt in session_speech.content:
            sentences = self.utt_sentence_splitter.split_utt_to_sentences(utt)
            for sentence in sentences:
                self._check_searched_in_sentence(result, sentence, utt, session_speech)
                if isinstance(utt, str):
                    self.cache['prev_sentence'] = sentence
            self.cache['prev_utt'] = utt
            self.cache['prev_utt_speech'] = session_speech

    def _check_searched_in_sentence(self, result, sentence, utt, session_speech):
        pos = 0
        keep_procesing = True
        while keep_procesing:
            matched = self.searched_regex.search(sentence, pos=pos)
            if matched:
                keep_procesing = True
                pos = matched.start() + 1
                self._new_occurrence(result, sentence, utt, session_speech)
            else:
                keep_procesing = False
        return False

    def _new_occurrence(self, result, sentence, utt_ref, speech_ref):
        speaker = get_speaker_for_utt(utt_ref, speech_ref)
        prev_sentence = self.cache['prev_sentence']
        occurrence = PhraseOccurence(speaker, sentence, utt_ref, speech_ref, prev_sentence)
        result.append(occurrence)
