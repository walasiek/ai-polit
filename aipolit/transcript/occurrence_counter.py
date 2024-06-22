import re
from typing import Union, Optional, List
from hipisejm.stenparser.transcript import SessionTranscript, SpeechReaction, SpeechInterruption, SessionSpeech
from hipisejm.stenparser.transcript_utils import get_speaker_for_utt
from aipolit.transcript.utt_sentence_splitter import UttSentenceSplitter


class PhraseOccurrence:
    """
    Represents single occurrence of the phrase/word we are searching for.

    speaker - who was a speaker of the matched sentence
    sentence - matched sentence which contains occurrence
    matched_utt_index - index of utt in speech_ref with matched sentence
    sentence_start_index_in_utt - character index (of utt text) where 'sentence' begins (allows to retrieve text before sentence from utt)
    sentence_start_match - chracter index (in sentence!) where matching begins
    sentence_end_match - chracter index (in sentence!) where matching finishes
    utt_ref - reference to utt object which contains matched text
    speech_ref - reference to speech object which contains matched text (in fact this means that utt_ref is redundant because we already have matched_utt_index, but I leave it due to initial implementation :( )
    prev_sentence - sentence preceeding matching
    """
    def __init__(self,
                 speaker: str,
                 sentence: str,
                 matched_utt_index: int,
                 sentence_start_index_in_utt: int,
                 sentence_start_match: int,
                 sentence_end_match: int,
                 utt_ref: Union[str, SpeechReaction, SpeechInterruption],
                 speech_ref: SessionSpeech,
                 prev_sentence: Optional[str]):
        self.speaker = speaker
        self.sentence = sentence
        self.matched_utt_index = matched_utt_index
        self.sentence_start_index_in_utt = sentence_start_index_in_utt
        self.sentence_start_match = sentence_start_match
        self.sentence_end_match = sentence_end_match
        self.utt_ref = utt_ref
        self.speech_ref = speech_ref
        self.prev_sentence = prev_sentence

    def __str__(self):
        sentence_with_tag = self.sentence[:self.sentence_start_match] + \
          '<b>' + \
          self.sentence[self.sentence_start_match: self.sentence_end_match] + \
          '</b>' + \
          self.sentence_end_match[self.sentence_end_match:]

        full_txt = f"{self.speaker}: {sentence_with_tag}"

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

    def run_count(self, transcript: SessionTranscript) -> List[PhraseOccurrence]:
        """
        Returns list of counted occurrencies.
        Steps:
        1. Split into sentences using sentence-splitter
        2. Regex search for "hańba" occurrencies (and some variants like inflecional forms)

        Returns list consisting of entries (PhraseOccurrence).

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
        for utt_index, utt in enumerate(session_speech.content):
            sentence_splits = self.utt_sentence_splitter.split_utt_to_sentences(utt)
            for sentence_split in sentence_splits:
                sentence = sentence_split[0]
                sentence_start_index_in_utt = sentence_split[1]
                self._check_searched_in_sentence(result, sentence, sentence_start_index_in_utt, utt, utt_index, session_speech)
                if isinstance(utt, str):
                    self.cache['prev_sentence'] = sentence
            self.cache['prev_utt'] = utt
            self.cache['prev_utt_speech'] = session_speech

    def _check_searched_in_sentence(self, result, sentence, sentence_start_index_in_utt, utt, utt_index, session_speech):
        pos = 0
        keep_procesing = True
        while keep_procesing:
            matched = self.searched_regex.search(sentence, pos=pos)
            if matched:
                keep_procesing = True
                pos = matched.start() + 1
                self._new_occurrence(result, sentence, sentence_start_index_in_utt, utt, utt_index, matched.start(), matched.end(), session_speech)
            else:
                keep_procesing = False
        return False

    def _new_occurrence(self, result, sentence, sentence_start_index_in_utt, utt_ref, matched_utt_index, sentence_start_match, sentence_end_match, speech_ref):
        speaker = get_speaker_for_utt(utt_ref, speech_ref)
        prev_sentence = self.cache['prev_sentence']

        occurrence = PhraseOccurrence(
            speaker,
            sentence,
            matched_utt_index,
            sentence_start_index_in_utt,
            sentence_start_match,
            sentence_end_match,
            utt_ref, speech_ref,
            prev_sentence)

        result.append(occurrence)
